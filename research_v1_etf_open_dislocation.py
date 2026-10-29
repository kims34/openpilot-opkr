"""IndexAlert ETF Open: deterministic OFFLINE KRX opening quote anomaly triage.

This is not a broker client, trade simulator, or production market-data parser.
It uses caller-supplied *synthetic* quote/reference snapshots only and cannot
authorize orders, infer executed fills, certify NAV fair value or earn profits.
The real feed adapter, legal market calendar, valuation provenance and
independent replay datasets are deliberately outside this research prototype.
No imports for network, secrets, financial accounts or brokerage SDKs.
"""
from __future__ import annotations

from collections import Counter
from datetime import datetime, timedelta, timezone
from hashlib import sha256
import json
import re

KST = timezone(timedelta(hours=9))
SCHEMA = "indexalert-etf-open-offline-v1"
INPUT_FIELDS = frozenset({
    "symbol", "venue", "observed_at_ms", "quote_at_ms", "bid_krw",
    "ask_krw", "bid_visible_qty", "ask_visible_qty", "nav_krw",
    "nav_at_ms", "fx_at_ms", "us_futures_at_ms", "valuation_at_ms",
    "fair_lower_krw", "fair_upper_krw",
})
INT_FIELDS = INPUT_FIELDS - {"symbol", "venue"}
SESSION_OPEN = (9, 0)
SESSION_CUTOFF = (9, 5)
MAX_EVENT_LAG_MS = 1500
MAX_REFERENCE_LAG_MS = 2000
MAX_FAIR_RANGE_BPS = 80
# Synthetic research thresholds ONLY; not optimized, calibrated, or production.
ILLUSTRATIVE_MIN_EDGE_BPS = 80
ILLUSTRATIVE_COST_BUFFER_BPS = 30
ILLUSTRATIVE_SELECTION_BUFFER_BPS = 30
MAX_REPLAY_EVENTS = 10000

class OfflineETFInputError(ValueError):
    """Only fixed, non-sensitive errors; never include raw quote/source data."""


def _integer(value: object) -> bool:
    return type(value) is int


def _prohibited_state() -> dict:
    return {
        "source_data_pit_admitted": False,
        "official_krx_session_verified": False,
        "issuer_and_etf_listing_pit_verified": False,
        "independent_fair_value_model_validated": False,
        "us_futures_and_fx_source_pit_verified": False,
        "exchange_tick_size_verified": False,
        "orderbook_depth_and_queue_verified": False,
        "actual_entry_fill_verified": False,
        "actual_exit_fill_verified": False,
        "net_after_tax_profit_verified": False,
        "market_data_network_access_authorized": False,
        "broker_login_authorized": False,
        "backtest_performance_run_authorized": False,
        "live_orders_authorized": False,
        "independent_holdout_authorized": False,
        "champion_change_authorized": False,
        "funds_movement_authorized": False,
        "ordering": "DISABLED",
    }


def _validate(snapshot: object) -> dict:
    if type(snapshot) is not dict or set(snapshot) != INPUT_FIELDS:
        raise OfflineETFInputError("OFFLINE_SNAPSHOT_FIELD_SCOPE_INVALID")
    if type(snapshot["symbol"]) is not str or not re.fullmatch(
        r"[0-9]{6}", snapshot["symbol"]
    ):
        raise OfflineETFInputError("ETF_SYMBOL_INVALID")
    if snapshot["venue"] != "KRX" or type(snapshot["venue"]) is not str:
        raise OfflineETFInputError("EXCHANGE_SCOPE_INVALID")
    for key in INT_FIELDS:
        if not _integer(snapshot[key]) or snapshot[key] < 0:
            raise OfflineETFInputError("QUOTE_NUMERIC_FIELD_INVALID")
    if any(snapshot[x] == 0 for x in (
        "bid_krw", "ask_krw", "bid_visible_qty", "ask_visible_qty",
        "nav_krw", "fair_lower_krw", "fair_upper_krw", "observed_at_ms",
    )):
        raise OfflineETFInputError("ZERO_OR_MISSING_QUOTE_FIELD")
    if snapshot["bid_krw"] >= snapshot["ask_krw"]:
        raise OfflineETFInputError("LOCKED_OR_CROSSED_BOOK_NOT_EXECUTABLE")
    if snapshot["fair_lower_krw"] > snapshot["fair_upper_krw"]:
        raise OfflineETFInputError("INVERTED_FAIR_VALUE_INTERVAL")
    return snapshot


def inspect_snapshot(snapshot: object) -> dict:
    """Assess discount to the LOWER fair-value bound, never trade or infer fills.

    All timing is based on local capture/observed_at_ms, not quote/exchange
    origin time; the former must be at or after each data source timestamp.
    Independent point-in-time provenance is never inferred from caller input.
    """
    s = _validate(snapshot)
    observed = s["observed_at_ms"]
    try:
        at = datetime.fromtimestamp(observed / 1000, KST)
    except (OverflowError, ValueError, OSError):
        raise OfflineETFInputError("OBSERVATION_TIME_INVALID") from None
    local_clock = (at.hour, at.minute)
    base = {"schema": SCHEMA, "status": "OFFLINE_REJECT",
            "reason": "INSUFFICIENT_EVIDENCE", "candidate": False,
            "gross_lower_bound_discount_bps": 0,
            "model_policy": "ILLUSTRATIVE_UNCALIBRATED",
            **_prohibited_state()}
    if at.weekday() >= 5 or not (
        SESSION_OPEN <= local_clock < SESSION_CUTOFF
    ):
        return {**base, "reason": "NOT_0900_TO_0905_KRX_WEEKDAY"}
    for key in ("quote_at_ms", "nav_at_ms", "fx_at_ms",
                "us_futures_at_ms", "valuation_at_ms"):
        age = observed - s[key]
        if age < 0:
            return {**base, "reason": "FUTURE_DATED_REFERENCE_LOOKAHEAD"}
        allowed = MAX_EVENT_LAG_MS if key == "quote_at_ms" else MAX_REFERENCE_LAG_MS
        if age > allowed:
            return {**base, "reason": "REFERENCE_OR_BOOK_STALE"}
    # The valuation cannot incorporate a reference observed after it was made.
    # This is a necessary chronology check, not source authentication.
    if any(s[key] > s["valuation_at_ms"] for key in (
        "nav_at_ms", "fx_at_ms", "us_futures_at_ms"
    )):
        return {**base, "reason": "VALUATION_PRECEDES_REQUIRED_REFERENCE"}
    # Compare exact integer products: flooring bps would admit >80 bps.
    if ((s["fair_upper_krw"] - s["fair_lower_krw"]) * 10000
            > MAX_FAIR_RANGE_BPS * s["fair_lower_krw"]):
        return {**base, "reason": "FAIR_VALUE_UNCERTAINTY_TOO_WIDE"}
    # Not a PnL estimate. No queue position, order/cancel latency, slippage,
    # executable fill, FX future-vs-spot reconciliation, or taxation is known.
    discount_bps = (
        (s["fair_lower_krw"] - s["ask_krw"]) * 10000
        // s["fair_lower_krw"]
    )
    threshold = (ILLUSTRATIVE_MIN_EDGE_BPS + ILLUSTRATIVE_COST_BUFFER_BPS
                 + ILLUSTRATIVE_SELECTION_BUFFER_BPS)
    if discount_bps < threshold:
        return {**base, "reason": "NO_CONSERVATIVE_CANDIDATE",
                "gross_lower_bound_discount_bps": discount_bps}
    return {
        **base,
        "status": "OFFLINE_WATCH_ONLY_NO_ORDER",
        "reason": "SYNTHETIC_DISCOUNT_CANDIDATE_NOT_A_FILL",
        "candidate": True,
        "gross_lower_bound_discount_bps": discount_bps,
    }


def replay_offline(snapshots: object) -> dict:
    """Aggregate ONLY counts from captured/synthetic snapshots; no PnL or IDs.

    Deliberately refuses unsorted/duplicated receipt instants and remains
    an offline diagnostic. Same symbol may have multiple snapshots, but no
    assumed executions or position state exists.
    """
    if (type(snapshots) is not list or not 1 <= len(snapshots) <=
            MAX_REPLAY_EVENTS):
        raise OfflineETFInputError("REPLAY_SIZE_INVALID")
    prev = -1
    status = Counter()
    for s in snapshots:
        normalized = _validate(s)
        stamp = normalized["observed_at_ms"]
        if stamp <= prev:
            raise OfflineETFInputError("REPLAY_NONMONOTONE_OBSERVATION")
        prev = stamp
        r = inspect_snapshot(normalized)
        status[r["reason"]] += 1
    return {
        "schema": SCHEMA,
        "purpose": "OFFLINE_WATCH_ONLY_REPLAY_COUNTS_NOT_PERFORMANCE",
        "snapshots_observed": len(snapshots),
        "synthetic_discount_candidates": status[
            "SYNTHETIC_DISCOUNT_CANDIDATE_NOT_A_FILL"],
        "rejected_or_non_signal_snapshots": len(snapshots) - status[
            "SYNTHETIC_DISCOUNT_CANDIDATE_NOT_A_FILL"],
        # Prevent accidental inference of fill rate or profitable trade count.
        "orders_submitted": 0,
        "positions_opened": 0,
        "fills_verified": 0,
        "net_profit_calculated": False,
        **_prohibited_state(),
    }


if __name__ == "__main__":
    # Dry-run is intentionally independent of market/broker/network and does
    # not read a configured private data mount, account, or any other file.
    print(json.dumps({
        "schema": SCHEMA, "status": "OFFLINE_RESEARCH_ONLY_NO_DATA",
        "snapshots_observed": 0, **_prohibited_state()
    }, sort_keys=True))

