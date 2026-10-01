"""Cross-source integrity audit for official KRX status-event evidence.

This module checks whether already-normalized official halt, cleanup-trading,
delisting and delisted-price evidence can coexist without temporal/source
contradictions. It deliberately does NOT invent fillability, execution prices,
recovery values or delisting PnL.

Structural consistency is necessary Final-Judge infrastructure, not promotion
or holdout authority.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Iterable

import pandas as pd

from research_v1_krx_cleanup_status import KRX_CLEANUP_SOURCE
from research_v1_krx_official_status import (
    KRX_DELIST_PRICE_SOURCE,
    KRX_DELIST_SOURCE,
    KRX_HALT_SOURCE,
)


class KRXStatusEventIntegrityError(ValueError):
    """Raised when official status evidence is malformed or contradictory."""


@dataclass(frozen=True)
class StatusEventIntegrityAudit:
    halt_rows: int
    cleanup_rows: int
    delisting_rows: int
    delisted_price_rows: int
    orphan_delisted_price_symbols: int
    post_delisting_price_rows: int
    cleanup_actual_delist_order_violations: int
    cleanup_without_actual_delisting_symbols: int
    planned_vs_actual_delisting_mismatch_symbols: int
    availability_lineage_complete: bool
    source_labels_valid: bool
    structurally_consistent: bool
    exact_delisting_economics_ready: bool
    judge_security_status_ready: bool
    sealed_holdout_authorized: bool


def _require_columns(df: pd.DataFrame, columns: Iterable[str], label: str) -> None:
    missing = [c for c in columns if c not in df.columns]
    if missing:
        raise KRXStatusEventIntegrityError(f"{label} missing required columns: {missing}")


def _aware(value, field: str) -> pd.Timestamp:
    try:
        ts = pd.Timestamp(value)
    except Exception as exc:
        raise KRXStatusEventIntegrityError(
            f"{field} contains unparseable timestamp: {value!r}"
        ) from exc
    if pd.isna(ts) or ts.tzinfo is None or ts.utcoffset() is None:
        raise KRXStatusEventIntegrityError(
            f"{field} must be non-missing and timezone-aware"
        )
    return ts


def _symbol(value) -> str:
    text = str(value).strip().upper()
    return text.zfill(6) if text.isdigit() else text


def _source_ok(df: pd.DataFrame, expected: str) -> bool:
    return bool(df.empty or set(df["source"].astype(str)) == {expected})


def _validate_frame_lineage(df: pd.DataFrame, label: str) -> None:
    if "available_at" not in df.columns:
        raise KRXStatusEventIntegrityError(f"{label} missing available_at lineage")
    for value in df["available_at"]:
        _aware(value, f"{label}.available_at")


def audit_status_event_integrity(
    *,
    halts: pd.DataFrame,
    cleanup: pd.DataFrame,
    delistings: pd.DataFrame,
    delisted_prices: pd.DataFrame,
) -> dict:
    """Audit cross-source temporal consistency without creating economics.

    Hard contradictions fail closed:
    - delisted-price row for a symbol absent from actual delisting evidence;
    - regular-session delisted-price row on/after the actual delisting date;
    - actual delisting date on/before cleanup-trading end for the same symbol.

    Planned-vs-actual delisting date differences are counted, not rejected:
    plans can change and must be reconciled to actual MDCSTAT238 evidence.
    Cleanup rows without an actual-delisting row are also counted as incomplete
    evidence rather than converted into a realized delisting event.
    """
    frames = {
        "halts": halts,
        "cleanup": cleanup,
        "delistings": delistings,
        "delisted_prices": delisted_prices,
    }
    if any(df is None for df in frames.values()):
        missing = [name for name, df in frames.items() if df is None]
        raise KRXStatusEventIntegrityError(
            f"all official status frames are required; missing={missing}"
        )

    _require_columns(halts, ["symbol", "halt_date", "resume_date", "source", "available_at"], "halts")
    _require_columns(
        cleanup,
        [
            "symbol",
            "cleanup_start",
            "cleanup_end",
            "planned_delisting_date",
            "source",
            "available_at",
        ],
        "cleanup",
    )
    _require_columns(
        delistings,
        ["symbol", "delisting_date", "source", "available_at"],
        "delistings",
    )
    _require_columns(
        delisted_prices,
        ["date", "symbol", "open", "high", "low", "close", "source", "available_at"],
        "delisted_prices",
    )

    for label, frame in frames.items():
        _validate_frame_lineage(frame, label)

    source_labels_valid = bool(
        _source_ok(halts, KRX_HALT_SOURCE)
        and _source_ok(cleanup, KRX_CLEANUP_SOURCE)
        and _source_ok(delistings, KRX_DELIST_SOURCE)
        and _source_ok(delisted_prices, KRX_DELIST_PRICE_SOURCE)
    )
    if not source_labels_valid:
        raise KRXStatusEventIntegrityError(
            "official status frame contains an unexpected source label"
        )

    actual_by_symbol: dict[str, pd.Timestamp] = {}
    for row in delistings[["symbol", "delisting_date"]].itertuples(index=False):
        symbol = _symbol(row.symbol)
        d = pd.Timestamp(row.delisting_date).normalize()
        previous = actual_by_symbol.get(symbol)
        actual_by_symbol[symbol] = d if previous is None else min(previous, d)

    price_symbols = {_symbol(x) for x in delisted_prices["symbol"]}
    orphan_price_symbols = sorted(price_symbols.difference(actual_by_symbol))

    post_delisting_rows = 0
    for row in delisted_prices[["date", "symbol"]].itertuples(index=False):
        symbol = _symbol(row.symbol)
        actual = actual_by_symbol.get(symbol)
        if actual is None:
            continue
        if pd.Timestamp(row.date).normalize() >= actual:
            post_delisting_rows += 1

    cleanup_order_violations = 0
    cleanup_without_actual: set[str] = set()
    planned_mismatch: set[str] = set()
    for row in cleanup[
        ["symbol", "cleanup_end", "planned_delisting_date"]
    ].itertuples(index=False):
        symbol = _symbol(row.symbol)
        actual = actual_by_symbol.get(symbol)
        if actual is None:
            cleanup_without_actual.add(symbol)
            continue
        cleanup_end = pd.Timestamp(row.cleanup_end).normalize()
        planned = pd.Timestamp(row.planned_delisting_date).normalize()
        if actual <= cleanup_end:
            cleanup_order_violations += 1
        if actual != planned:
            planned_mismatch.add(symbol)

    contradictions = (
        len(orphan_price_symbols)
        + post_delisting_rows
        + cleanup_order_violations
    )
    if orphan_price_symbols:
        raise KRXStatusEventIntegrityError(
            "delisted-price evidence contains symbols absent from actual delisting evidence: "
            f"{orphan_price_symbols[:10]}"
        )
    if post_delisting_rows:
        raise KRXStatusEventIntegrityError(
            "delisted-price evidence contains regular-session price rows on/after actual delisting date"
        )
    if cleanup_order_violations:
        raise KRXStatusEventIntegrityError(
            "actual delisting date must be after cleanup-trading end for matched events"
        )

    audit = StatusEventIntegrityAudit(
        halt_rows=int(len(halts)),
        cleanup_rows=int(len(cleanup)),
        delisting_rows=int(len(delistings)),
        delisted_price_rows=int(len(delisted_prices)),
        orphan_delisted_price_symbols=0,
        post_delisting_price_rows=0,
        cleanup_actual_delist_order_violations=0,
        cleanup_without_actual_delisting_symbols=int(len(cleanup_without_actual)),
        planned_vs_actual_delisting_mismatch_symbols=int(len(planned_mismatch)),
        availability_lineage_complete=True,
        source_labels_valid=True,
        structurally_consistent=(contradictions == 0),
        # Deliberately false. Structural consistency cannot infer fills, queue
        # access, recovery value, executable price or exact economic outcome.
        exact_delisting_economics_ready=False,
        judge_security_status_ready=False,
        sealed_holdout_authorized=False,
    )
    out = asdict(audit)
    out["cleanup_without_actual_delisting_sample"] = sorted(cleanup_without_actual)[:10]
    out["planned_vs_actual_delisting_mismatch_sample"] = sorted(planned_mismatch)[:10]
    out["guardrail"] = (
        "Structural status-event consistency does not imply executable fills, "
        "delisting recovery value, exact NetReturn, Final-Judge readiness or holdout authority."
    )
    return out
