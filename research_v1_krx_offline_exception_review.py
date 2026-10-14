"""Offline-only KRX exceptional session / nonpositive OHLC reconciliation gate.

All inputs are independently gathered *claims*, not authenticated PIT facts.
This module never fetches providers, accepts account keys, uses Holdout, or
authorizes backtests/trading. Do not pass issuer names or raw price data.
"""
from __future__ import annotations

from datetime import date
import re

HEX64 = re.compile(r"[0-9a-f]{64}\Z")
DATE = re.compile(r"20(?:17|18|19|20|21|22)-\d{2}-\d{2}\Z")
MARKET = frozenset(("OPEN", "CLOSED"))
STOCK = frozenset(("SUSPENDED", "DELISTED", "LISTED", "UNKNOWN"))
MAX_DAYS = 1565
MAX_ROWS = 100000


class EvidenceNotAdmitted(ValueError):
    """Invalid or conflicting source claims; do not treat as trading data."""


def _sha(value: object) -> None:
    if type(value) is not str or not HEX64.fullmatch(value):
        raise EvidenceNotAdmitted("missing or malformed fixed source SHA256")


def _day(value: object) -> str:
    if type(value) is not str or not DATE.fullmatch(value):
        raise EvidenceNotAdmitted("invalid fixed historical day")
    try:
        parsed = date.fromisoformat(value)
    except ValueError as exc:
        raise EvidenceNotAdmitted("invalid calendar date") from exc
    if parsed.weekday() >= 5:
        raise EvidenceNotAdmitted("weekend cannot be a captured weekday exception")
    return value


def _records(items: object, *, kind: str, maximum: int) -> dict:
    if type(items) is not list or len(items) > maximum:
        raise EvidenceNotAdmitted("unbounded " + kind + " input")
    result = {}
    for row in items:
        if type(row) is not dict:
            raise EvidenceNotAdmitted("malformed " + kind + " record")
        day = _day(row.get("date"))
        if kind == "raw_day":
            if set(row) != {"date", "pair_sha256", "daily_row_count"}:
                raise EvidenceNotAdmitted("unsupported raw day fields")
            _sha(row["pair_sha256"])
            if type(row["daily_row_count"]) is not int or not 0 <= row["daily_row_count"] <= MAX_ROWS:
                raise EvidenceNotAdmitted("invalid daily row count")
            key = day
        elif kind == "calendar":
            if set(row) != {"date", "session", "evidence_sha256", "source_kind"}:
                raise EvidenceNotAdmitted("unsupported session source fields")
            if row["source_kind"] != "INDEPENDENT_OFFICIAL_SESSION_CLAIM":
                raise EvidenceNotAdmitted("market status needs independent source")
            _sha(row["evidence_sha256"])
            if type(row["session"]) is not str or row["session"] not in MARKET:
                raise EvidenceNotAdmitted("official market session unknown")
            key = day
        elif kind == "anomaly":
            if set(row) != {"date", "security_token_sha256", "row_sha256", "nonpositive_ohlc"}:
                raise EvidenceNotAdmitted("unsupported price anomaly fields")
            _sha(row["security_token_sha256"])
            _sha(row["row_sha256"])
            if row["nonpositive_ohlc"] is not True:
                raise EvidenceNotAdmitted("only quarantined nonpositive OHLC input allowed")
            key = (day, row["security_token_sha256"])
        elif kind == "security_status":
            if set(row) != {"date", "security_token_sha256", "state", "evidence_sha256", "source_kind"}:
                raise EvidenceNotAdmitted("unsupported stock status fields")
            _sha(row["security_token_sha256"])
            _sha(row["evidence_sha256"])
            if row["source_kind"] != "INDEPENDENT_OFFICIAL_SECURITY_DAY_CLAIM":
                raise EvidenceNotAdmitted("independent daily security evidence required")
            if type(row["state"]) is not str or row["state"] not in STOCK:
                raise EvidenceNotAdmitted("invalid historical security state")
            key = (day, row["security_token_sha256"])
        else:
            raise EvidenceNotAdmitted("unknown source category")
        if key in result:
            raise EvidenceNotAdmitted("duplicated dated evidence")
        result[key] = row
    return result


def review_exceptions(exception_dates: list[str], private_raw_days: list[dict],
                      independent_calendar: list[dict],
                      price_anomalies: list[dict],
                      independent_security_days: list[dict]) -> dict:
    """Cross-check claimed source receipts, never promote to official PIT.

    An empty official-evidence list is valid and reports the unresolved work.
    Every unknown/halt/delist case is quarantined regardless of status claims.
    Current provider snapshots cannot substitute original availability evidence.
    """
    if type(exception_dates) is not list or not 0 < len(exception_dates) <= MAX_DAYS:
        raise EvidenceNotAdmitted("explicit bounded exception-date scope required")
    dates = [_day(x) for x in exception_dates]
    if dates != sorted(set(dates)):
        raise EvidenceNotAdmitted("duplicate or unsorted exception days")
    raw = _records(private_raw_days, kind="raw_day", maximum=MAX_DAYS)
    cal = _records(independent_calendar, kind="calendar", maximum=MAX_DAYS)
    bad = _records(price_anomalies, kind="anomaly", maximum=MAX_ROWS)
    states = _records(independent_security_days, kind="security_status", maximum=MAX_ROWS)
    scope = set(dates)
    if set(raw) != scope or not set(cal).issubset(scope):
        raise EvidenceNotAdmitted("raw source day or calendar scope mismatch")
    if not set(states).issubset(set(bad)):
        raise EvidenceNotAdmitted("unmatched security state claim")
    for d, row in cal.items():
        n = raw[d]["daily_row_count"]
        if row["session"] == "CLOSED" and n > 0:
            raise EvidenceNotAdmitted("trading rows conflict with claimed closed session")
        if row["session"] == "OPEN" and n == 0:
            raise EvidenceNotAdmitted("source gap conflicts with claimed open session")
    # Date-scoped stock statuses cannot make nonpositive OHLC executable.
    # A LISTED stock may still halt: verify separately, never mark TRADABLE.
    return {
        "schema": "indexalert-krx-offline-exception-review-v1",
        "source_status": "SOURCE_ONLY_RETROSPECTIVE_CLAIMS_NOT_PIT",
        "exception_weekdays_checked": len(dates),
        "raw_source_day_hash_shape_checked": len(raw),
        "calendar_claimed_open": sum(x["session"] == "OPEN" for x in cal.values()),
        "calendar_claimed_closed": sum(x["session"] == "CLOSED" for x in cal.values()),
        "calendar_unresolved": len(dates) - len(cal),
        "nonpositive_ohlc_rows_quarantined": len(bad),
        "stock_states_corroborated_retrospectively": len(states),
        "stock_states_unresolved": len(bad) - len(states),
        "calendar_original_publication_pit_verified": False,
        "individual_tradability_verified": False,
        "historical_corporate_actions_verified": False,
        "full_universe_source_admitted": False,
        "m20_performance_run_authorized": False,
        "holdout_access_authorized": False,
        "champion_change_authorized": False,
        "live_orders_authorized": False,
        "funds_movement_authorized": False,
        "permissions_change_authorized": False,
        "raw_security_data_emitted": False,
        "official_network_requests_made": False,
        "storage_mutated": False,
        "ordering": "DISABLED",
    }
