"""Fail-closed schema and diagnostics for empirical IndexAlert execution evidence.

This module does not simulate fills. It validates *observed* Shadow/live-style
execution records so backtest assumptions cannot be mislabeled as empirical
execution evidence.

It is intentionally separate from alpha/model selection. Missing fills, partial
fills, latency and markouts are outcomes to preserve, not records to drop.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass

import numpy as np
import pandas as pd


EMPIRICAL_EXECUTION_SOURCE = "PROSPECTIVE_SHADOW_EXECUTION_LOG"


class ExecutionEvidenceError(ValueError):
    pass


REQUIRED_COLUMNS = {
    "decision_date",
    "symbol",
    "side",
    "recommendation_at",
    "order_submitted_at",
    "requested_qty",
    "filled_qty",
    "first_fill_at",
    "final_fill_at",
    "avg_fill_price",
    "reference_open",
    "markout_5m_price",
    "markout_30m_price",
    "markout_close_price",
    "source",
    "ingested_at",
}


@dataclass(frozen=True)
class ExecutionAudit:
    observations: int
    filled_observations: int
    no_fill_observations: int
    partial_fill_observations: int
    full_fill_observations: int
    mean_fill_ratio: float
    median_submit_latency_ms: float | None
    median_time_to_first_fill_ms: float | None
    median_buy_slippage_vs_open_bps: float | None
    median_markout_5m_bps: float | None
    median_markout_30m_bps: float | None
    median_markout_close_bps: float | None
    empirical_source_only: bool
    complete_markout_for_fills: bool
    structural_execution_evidence_ready: bool


def _ts(series: pd.Series) -> pd.Series:
    return pd.to_datetime(series, errors="coerce", utc=True)


def _finite_median(series: pd.Series) -> float | None:
    x = pd.to_numeric(series, errors="coerce").replace([np.inf, -np.inf], np.nan).dropna()
    return None if x.empty else float(x.median())


def validate_execution_observations(table: pd.DataFrame) -> pd.DataFrame:
    """Validate empirical execution rows and derive non-model diagnostics.

    Zero-fill rows are valid and must remain in the evidence set. Filled rows
    require timestamps, price and markouts. BUY is the only currently supported
    side because IndexAlert's frozen research policy is long-only Top3.
    """
    if table is None:
        raise ExecutionEvidenceError("execution evidence table is None")
    missing = sorted(REQUIRED_COLUMNS - set(table.columns))
    if missing:
        raise ExecutionEvidenceError(f"execution evidence missing required columns: {missing}")
    if table.empty:
        raise ExecutionEvidenceError("execution evidence table is empty")

    x = table.copy()
    x["decision_date"] = pd.to_datetime(x["decision_date"], errors="coerce").dt.normalize()
    x["symbol"] = x["symbol"].astype(str).str.strip().str.upper().str.replace(r"\.0$", "", regex=True)
    x["symbol"] = x["symbol"].map(lambda s: s.zfill(6) if s.isdigit() else s)
    x["side"] = x["side"].astype(str).str.upper().str.strip()
    if not x["side"].eq("BUY").all():
        raise ExecutionEvidenceError("current frozen execution schema supports BUY only")
    if x["decision_date"].isna().any() or x["symbol"].eq("").any():
        raise ExecutionEvidenceError("invalid decision_date or symbol")

    for c in ["recommendation_at", "order_submitted_at", "first_fill_at", "final_fill_at", "ingested_at"]:
        x[c] = _ts(x[c])
    if x[["recommendation_at", "order_submitted_at", "ingested_at"]].isna().any().any():
        raise ExecutionEvidenceError("recommendation/order/ingested timestamps are mandatory")
    if (x["order_submitted_at"] < x["recommendation_at"]).any():
        raise ExecutionEvidenceError("order_submitted_at cannot precede recommendation_at")
    if (x["ingested_at"] < x["recommendation_at"]).any():
        raise ExecutionEvidenceError("ingested_at cannot precede recommendation_at")

    for c in [
        "requested_qty", "filled_qty", "avg_fill_price", "reference_open",
        "markout_5m_price", "markout_30m_price", "markout_close_price",
    ]:
        x[c] = pd.to_numeric(x[c], errors="coerce")

    if x["requested_qty"].isna().any() or (x["requested_qty"] <= 0).any():
        raise ExecutionEvidenceError("requested_qty must be positive")
    if x["filled_qty"].isna().any() or (x["filled_qty"] < 0).any():
        raise ExecutionEvidenceError("filled_qty must be non-negative")
    if (x["filled_qty"] > x["requested_qty"]).any():
        raise ExecutionEvidenceError("filled_qty cannot exceed requested_qty")
    if x["reference_open"].isna().any() or (x["reference_open"] <= 0).any():
        raise ExecutionEvidenceError("reference_open must be positive")

    filled = x["filled_qty"] > 0
    no_fill = ~filled
    required_filled_numeric = [
        "avg_fill_price", "markout_5m_price", "markout_30m_price", "markout_close_price"
    ]
    if x.loc[filled, required_filled_numeric].isna().any().any():
        raise ExecutionEvidenceError("filled rows require fill price and all markout prices")
    if (x.loc[filled, required_filled_numeric] <= 0).any().any():
        raise ExecutionEvidenceError("filled-row fill/markout prices must be positive")
    if x.loc[filled, ["first_fill_at", "final_fill_at"]].isna().any().any():
        raise ExecutionEvidenceError("filled rows require first_fill_at and final_fill_at")
    if (x.loc[filled, "first_fill_at"] < x.loc[filled, "order_submitted_at"]).any():
        raise ExecutionEvidenceError("first fill cannot precede order submission")
    if (x.loc[filled, "final_fill_at"] < x.loc[filled, "first_fill_at"]).any():
        raise ExecutionEvidenceError("final fill cannot precede first fill")

    # No-fill observations must not fabricate execution timestamps/prices.
    if x.loc[no_fill, ["first_fill_at", "final_fill_at", "avg_fill_price"]].notna().any().any():
        raise ExecutionEvidenceError("zero-fill rows must not contain fill timestamps/prices")

    if not x["source"].astype(str).eq(EMPIRICAL_EXECUTION_SOURCE).all():
        raise ExecutionEvidenceError(
            f"source must be exactly {EMPIRICAL_EXECUTION_SOURCE}; simulated/backtest fills are not empirical evidence"
        )

    x["fill_ratio"] = x["filled_qty"] / x["requested_qty"]
    x["partial_fill"] = (x["fill_ratio"] > 0) & (x["fill_ratio"] < 1)
    x["full_fill"] = x["fill_ratio"].eq(1.0)
    x["no_fill"] = x["fill_ratio"].eq(0.0)
    x["submit_latency_ms"] = (
        x["order_submitted_at"] - x["recommendation_at"]
    ).dt.total_seconds() * 1000.0
    x["time_to_first_fill_ms"] = np.where(
        filled,
        (x["first_fill_at"] - x["order_submitted_at"]).dt.total_seconds() * 1000.0,
        np.nan,
    )
    x["buy_slippage_vs_open_bps"] = np.where(
        filled,
        (x["avg_fill_price"] / x["reference_open"] - 1.0) * 10000.0,
        np.nan,
    )
    for label, col in [
        ("5m", "markout_5m_price"),
        ("30m", "markout_30m_price"),
        ("close", "markout_close_price"),
    ]:
        # Positive markout means price moved in the BUY direction after fill.
        x[f"markout_{label}_bps"] = np.where(
            filled,
            (x[col] / x["avg_fill_price"] - 1.0) * 10000.0,
            np.nan,
        )
    return x


def audit_execution_evidence(table: pd.DataFrame) -> dict:
    x = validate_execution_observations(table)
    filled = x["filled_qty"] > 0
    complete_markout = bool(
        x.loc[filled, ["markout_5m_price", "markout_30m_price", "markout_close_price"]]
        .notna().all().all()
    ) if filled.any() else False
    audit = ExecutionAudit(
        observations=int(len(x)),
        filled_observations=int(filled.sum()),
        no_fill_observations=int(x["no_fill"].sum()),
        partial_fill_observations=int(x["partial_fill"].sum()),
        full_fill_observations=int(x["full_fill"].sum()),
        mean_fill_ratio=float(x["fill_ratio"].mean()),
        median_submit_latency_ms=_finite_median(x["submit_latency_ms"]),
        median_time_to_first_fill_ms=_finite_median(x["time_to_first_fill_ms"]),
        median_buy_slippage_vs_open_bps=_finite_median(x["buy_slippage_vs_open_bps"]),
        median_markout_5m_bps=_finite_median(x["markout_5m_bps"]),
        median_markout_30m_bps=_finite_median(x["markout_30m_bps"]),
        median_markout_close_bps=_finite_median(x["markout_close_bps"]),
        empirical_source_only=bool(x["source"].eq(EMPIRICAL_EXECUTION_SOURCE).all()),
        complete_markout_for_fills=complete_markout,
        # Structural only. No sample-size or performance threshold is invented here.
        structural_execution_evidence_ready=bool(filled.any() and complete_markout),
    )
    out = asdict(audit)
    out["promotion_ready"] = False
    out["promotion_note"] = (
        "structural schema validation is not a promotion gate; sample sufficiency, capacity, tails, "
        "sealed holdout and prospective confirmation remain separate requirements"
    )
    return out
