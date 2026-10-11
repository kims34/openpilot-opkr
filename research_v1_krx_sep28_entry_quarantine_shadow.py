"""Research-only prospective new-entry quarantine for KRX 2026-09-28 anomalies.

This is NOT a KRX normalization bypass, historical backtest correction, trading
rule amendment, source-status admission, or an order path. It consumes a
privately provided common-stock observation panel and *already frozen* Top3.
No provider network requests, saved securities, model fitting, price imputation,
portfolio valuation or historical P&L. The existing all-universe FAIL_CLOSED
source gate remains authoritative.

Caller-provided panel identities, raw SHA strings and available-at timestamps
are NOT independently authenticated by this module. A result is an exploratory
veto feasibility diagnostic only, never authorization for remaining entries.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
import math
import re
from typing import Any, Mapping, Sequence

SOURCE_SESSION = "2026-09-28"
EXPECTED_COMMON = 803
EXPECTED_NONPOSITIVE = 27
HEX_SHA256 = re.compile(r"[0-9a-f]{64}\Z")
SYMBOL = re.compile(r"[A-Z0-9]{6}\Z")
NONNEG_INTEGER = re.compile(r"(?:0|[1-9][0-9]*)(?:,[0-9]{3})*\Z")
NONNEG_DECIMAL = re.compile(r"(?:0|[1-9][0-9]*)(?:,[0-9]{3})*(?:\.[0-9]+)?\Z")


class EntryQuarantineError(ValueError):
    """Never include provider records or sensitive identifiers in errors."""


@dataclass(frozen=True)
class ShadowQuarantineResult:
    # PRIVATE in-process candidate decision identities, never print/persist them.
    private_slot_decisions: tuple[tuple[int, str, str], ...] = field(repr=False)
    # Safe to publish: aggregates and independent-authority vetoes only.
    summary: dict[str, Any]


def _timestamp(value: object) -> datetime:
    if type(value) is not str:
        raise EntryQuarantineError("AWARE_TIMESTAMP_REQUIRED")
    try:
        ts = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        raise EntryQuarantineError("AWARE_TIMESTAMP_REQUIRED") from None
    if ts.tzinfo is None or ts.utcoffset() is None:
        raise EntryQuarantineError("AWARE_TIMESTAMP_REQUIRED")
    return ts


def _symbol(value: object) -> str:
    if type(value) is not str or not SYMBOL.fullmatch(value):
        raise EntryQuarantineError("CANONICAL_SYMBOL_REQUIRED")
    return value


def _number(value: object, *, integer: bool = False) -> Decimal:
    if type(value) not in (int, str, Decimal):
        raise EntryQuarantineError("PRICE_OR_ACTIVITY_INVALID")
    if type(value) is str:
        pattern = NONNEG_INTEGER if integer else NONNEG_DECIMAL
        if not pattern.fullmatch(value):
            raise EntryQuarantineError("PRICE_OR_ACTIVITY_INVALID")
        value = value.replace(",", "")
    try:
        n = Decimal(value)
    except (ValueError, InvalidOperation):
        raise EntryQuarantineError("PRICE_OR_ACTIVITY_INVALID") from None
    if not n.is_finite() or n < 0 or (integer and n != n.to_integral_value()):
        raise EntryQuarantineError("PRICE_OR_ACTIVITY_INVALID")
    return n


def _source_scope(source_rows: Sequence[Mapping[str, Any]], session: str) -> tuple[set[str], set[str]]:
    if type(source_rows) not in (tuple, list) or len(source_rows) != EXPECTED_COMMON:
        raise EntryQuarantineError("UNVERIFIED_COMMON_STOCK_SCOPE")
    seen: set[str] = set()
    excluded: set[str] = set()
    for row in source_rows:
        if not isinstance(row, Mapping):
            raise EntryQuarantineError("SOURCE_ROW_INVALID")
        if row.get("source_session") != session:
            raise EntryQuarantineError("SOURCE_ROW_SESSION_MISMATCH")
        symbol = _symbol(row.get("symbol"))
        if symbol in seen:
            raise EntryQuarantineError("DUPLICATE_SOURCE_SYMBOL")
        seen.add(symbol)
        o, h, l, c = (
            _number(row.get(col)) for col in ("open", "high", "low", "close")
        )
        vol, val = _number(row.get("volume"), integer=True), _number(row.get("value"), integer=True)
        if min(o, h, l, c) <= 0:
            # The specifically observed 2026-09-28 failure shape: no
            # recorded activity, positive close, no opening/high/low prices.
            # Do not silently "repair" or infer an official HALT event.
            if not (o == 0 and h == 0 and l == 0 and c > 0 and vol == 0 and val == 0):
                raise EntryQuarantineError("SOURCE_ANOMALY_SHAPE_CHANGED")
            excluded.add(symbol)
        elif not (l <= o <= h and l <= c <= h):
            raise EntryQuarantineError("SOURCE_POSITIVE_PRICE_INVALID")
    if len(excluded) != EXPECTED_NONPOSITIVE:
        raise EntryQuarantineError("SOURCE_ANOMALY_COUNT_CHANGED")
    return seen, excluded


def _original_top3(original_top3: Sequence[Mapping[str, Any]]) -> tuple[tuple[str, float, bool], ...]:
    if type(original_top3) not in (tuple, list) or len(original_top3) > 3:
        raise EntryQuarantineError("ORIGINAL_TOP3_SCOPE_INVALID")
    out = []
    seen: set[str] = set()
    for slot in original_top3:
        if not isinstance(slot, Mapping):
            raise EntryQuarantineError("ORIGINAL_TOP3_SCOPE_INVALID")
        symbol = _symbol(slot.get("symbol"))
        score = slot.get("score")
        market_eligible = slot.get("normal_market_eligible")
        if symbol in seen or type(score) not in (int, float) or not math.isfinite(score) or score <= 0:
            raise EntryQuarantineError("ORIGINAL_TOP3_SCOPE_INVALID")
        if type(market_eligible) is not bool:
            raise EntryQuarantineError("ORIGINAL_MARKET_VETO_MISSING")
        seen.add(symbol)
        out.append((symbol, float(score), market_eligible))
    if out != sorted(out, key=lambda item: (-item[1], item[0])):
        raise EntryQuarantineError("ORIGINAL_TOP3_ORDER_CHANGED")
    return tuple(out)


def evaluate_new_entry_quarantine_shadow(
    *,
    source_session: str,
    source_observed_at: str,
    decision_at: str,
    source_raw_sha256_claim: str,
    common_stock_observations: Sequence[Mapping[str, Any]],
    original_top3: Sequence[Mapping[str, Any]],
    held_positions: Sequence[Mapping[str, Any]],
) -> ShadowQuarantineResult:
    """Demonstrate an additive veto; never authorize trades or source admission.

    Rows are private and must come from pre-existing KRX reads. The caller's
    SHA256 is a label, not independently validated provenance. The earlier
    observation cannot be applied before it was actually retrieved.
    """
    if source_session != SOURCE_SESSION:
        raise EntryQuarantineError("SOURCE_SESSION_OUTSIDE_PINNED_DIAGNOSTIC")
    if type(source_raw_sha256_claim) is not str or not HEX_SHA256.fullmatch(source_raw_sha256_claim):
        raise EntryQuarantineError("SOURCE_SHA256_CLAIM_INVALID")
    observed, decision = _timestamp(source_observed_at), _timestamp(decision_at)
    if observed > decision:
        raise EntryQuarantineError("FUTURE_OBSERVATION_LEAKAGE")
    try:
        source_day = date.fromisoformat(source_session)
    except ValueError:
        raise EntryQuarantineError("SOURCE_SESSION_INVALID") from None
    if observed.date() < source_day or decision.date() < source_day:
        raise EntryQuarantineError("SOURCE_CHRONOLOGY_INVALID")
    universe, excluded = _source_scope(common_stock_observations, source_session)
    frozen = _original_top3(original_top3)
    if type(held_positions) not in (list, tuple):
        raise EntryQuarantineError("HELD_POSITION_SCOPE_MISSING")
    pos_ids: set[str] = set()
    held_syms: list[str] = []
    for p in held_positions:
        if not isinstance(p, Mapping) or type(p.get("position_id")) is not str:
            raise EntryQuarantineError("HELD_POSITION_SCOPE_INVALID")
        pid = p["position_id"]
        if not pid or pid in pos_ids:
            raise EntryQuarantineError("HELD_POSITION_SCOPE_INVALID")
        sym = _symbol(p.get("symbol"))
        pos_ids.add(pid)
        held_syms.append(sym)

    slot_decisions: list[tuple[int, str, str]] = []
    kept = rejected = existing_veto = unknown = 0
    for slot_id, (sym, _score, eligible) in enumerate(frozen, 1):
        if not eligible:
            disposition = "EXISTING_MARKET_VETO"
            existing_veto += 1
        elif sym not in universe:
            disposition = "UNKNOWN_SOURCE_SCOPE_VETO"
            unknown += 1
        elif sym in excluded:
            disposition = "NEW_ENTRY_QUARANTINE_VETO"
            rejected += 1
        else:
            disposition = "STRUCTURALLY_RETAINED_NOT_AUTHORIZED"
            kept += 1
        slot_decisions.append((slot_id, sym, disposition))
    summary = {
        "classification": "KRX_SEP28_RESEARCH_ONLY_NEW_ENTRY_VETO_FEASIBILITY",
        "source_session": source_session,
        "observed_nonpositive_count": EXPECTED_NONPOSITIVE,
        "observed_common_stock_count": EXPECTED_COMMON,
        "observed_remaining_source_rows": EXPECTED_COMMON - EXPECTED_NONPOSITIVE,
        "original_top3_slots": len(frozen),
        "shadow_structurally_retained_slots": kept,
        "shadow_anomalous_new_entry_veto_slots": rejected,
        "pre_existing_market_veto_slots": existing_veto,
        "unknown_source_veto_slots": unknown,
        "no_trade_observation": kept == 0,
        "rank4plus_backfill": False,
        "held_positions_untouched": True,
        "held_positions_observed_count": len(held_syms),
        "held_positions_overlapping_quarantine_count": sum(sym in excluded for sym in held_syms),
        "held_positions_exact_economics_verified": False,
        "source_original_bytes_independently_verified_here": False,
        "full_source_admission_verified": False,
        "official_halt_status_verified": False,
        "historical_pit_backtest_authorized": False,
        "prospective_alpha_admission_authorized": False,
        "independent_holdout_authorized": False,
        "champion_change_authorized": False,
        "net_ev_certified": False,
        "real_orders_authorized": False,
        "funds_movement_authorized": False,
        "permission_change_authorized": False,
        "ordering": "DISABLED",
        "canonical_krx_source_fail_closed_preserved": True,
    }
    return ShadowQuarantineResult(tuple(slot_decisions), summary)
