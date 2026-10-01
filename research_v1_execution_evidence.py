"""Fail-closed schema and diagnostics for IndexAlert execution evidence.

Execution evidence is tiered so Shadow decisions cannot be mislabeled as broker
fills:
- SHADOW records decisions/intents only and are not accepted by this fill schema.
- PAPER records actual responses from a supported paper/simulation broker.
  They are operational evidence, not live-market fill evidence.
- LIVE records actual real-account broker executions and is the only source that
  can contribute to empirical live fill/slippage/partial-fill evidence.

This module does not simulate fills. Missing fills, partial fills, latency and
markouts are outcomes to preserve, not records to drop. Backtest/synthetic
fills and Shadow would-be fills are rejected.

Important terminology boundary:
- structurally valid LIVE rows only prove that real-account observations exist
  in the expected schema;
- they do NOT establish sample sufficiency, capacity, tail behavior or closure
  of the empirical execution blocker.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass

import numpy as np
import pandas as pd


SHADOW_DECISION_SOURCE = "PROSPECTIVE_SHADOW_DECISION_LOG"
PAPER_EXECUTION_SOURCE = "PROSPECTIVE_PAPER_EXECUTION_LOG"
LIVE_EXECUTION_SOURCE = "PROSPECTIVE_LIVE_EXECUTION_LOG"
ACCEPTED_EXECUTION_SOURCES = frozenset({PAPER_EXECUTION_SOURCE, LIVE_EXECUTION_SOURCE})

# Backward-compatible import alias only. New code must use LIVE_EXECUTION_SOURCE
# explicitly; the former Shadow-labelled value was conceptually incorrect for
# empirical broker-fill evidence.
EMPIRICAL_EXECUTION_SOURCE = LIVE_EXECUTION_SOURCE


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
    paper_observations: int
    live_observations: int
    live_filled_observations: int
    live_no_fill_observations: int
    live_partial_fill_observations: int
    live_full_fill_observations: int
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
    accepted_execution_sources_only: bool
    contains_paper_execution_evidence: bool
    contains_live_execution_evidence: bool
    live_execution_source_only: bool
    complete_markout_for_fills: bool
    structural_execution_evidence_ready: bool
    live_structural_execution_evidence_present: bool
    # Deprecated compatibility field. It is deliberately never raised merely
    # because one or more LIVE rows are structurally valid.
    live_empirical_execution_evidence_ready: bool
    empirical_execution_sufficiency_assessed: bool
    empirical_execution_blocker_closed: bool


def _ts(series: pd.Series) -> pd.Series:
    return pd.to_datetime(series, errors="coerce", utc=True)


def _finite_median(series: pd.Series) -> float | None:
    x = pd.to_numeric(series, errors="coerce").replace([np.inf, -np.inf], np.nan).dropna()
    return None if x.empty else float(x.median())


def validate_execution_observations(table: pd.DataFrame) -> pd.DataFrame:
    """Validate broker execution rows and derive non-model diagnostics.

    Zero-fill rows are valid and must remain in the evidence set. Filled rows
    require timestamps, price and markouts. BUY is the only currently supported
    side because IndexAlert's frozen research policy is long-only Top3.

    Shadow decisions are intentionally rejected here because SHADOW submits no
    broker order. Paper and live observations remain distinguishable in `source`.
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

    sources = x["source"].astype(str).str.strip()
    if sources.eq(SHADOW_DECISION_SOURCE).any():
        raise ExecutionEvidenceError(
            "Shadow decisions cannot carry broker fill evidence; use a separate Shadow decision/intention log"
        )
    bad_sources = sorted(set(sources) - set(ACCEPTED_EXECUTION_SOURCES))
    if bad_sources:
        raise ExecutionEvidenceError(
            "execution source must be PAPER or LIVE broker evidence; "
            f"unsupported sources: {bad_sources}"
        )
    x["source"] = sources

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

    # No-fill observations must not fabricate execution timestamps/prices or markouts.
    no_fill_fields = [
        "first_fill_at", "final_fill_at", "avg_fill_price",
        "markout_5m_price", "markout_30m_price", "markout_close_price",
    ]
    if x.loc[no_fill, no_fill_fields].notna().any().any():
        raise ExecutionEvidenceError("zero-fill rows must not contain fill timestamps/prices/markouts")

    x["fill_ratio"] = x["filled_qty"] / x["requested_qty"]
    x["partial_fill"] = (x["fill_ratio"] > 0) & (x["fill_ratio"] < 1)
    x["full_fill"] = x["fill_ratio"].eq(1.0)
    x["no_fill"] = x["fill_ratio"].eq(0.0)
    x["execution_tier"] = np.where(
        x["source"].eq(LIVE_EXECUTION_SOURCE), "LIVE", "PAPER"
    )
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
        x[f"markout_{label}_bps"] = np.where(
            filled,
            (x[col] / x["avg_fill_price"] - 1.0) * 10000.0,
            np.nan,
        )
    return x


def audit_execution_evidence(table: pd.DataFrame) -> dict:
    x = validate_execution_observations(table)
    filled = x["filled_qty"] > 0
    live = x["source"].eq(LIVE_EXECUTION_SOURCE)
    paper = x["source"].eq(PAPER_EXECUTION_SOURCE)
    live_filled = live & filled

    complete_markout = bool(
        x.loc[filled, ["markout_5m_price", "markout_30m_price", "markout_close_price"]]
        .notna().all().all()
    ) if filled.any() else False
    live_complete_markout = bool(
        x.loc[live_filled, ["markout_5m_price", "markout_30m_price", "markout_close_price"]]
        .notna().all().all()
    ) if live_filled.any() else False
    live_structural = bool(live_filled.any() and live_complete_markout)

    audit = ExecutionAudit(
        observations=int(len(x)),
        paper_observations=int(paper.sum()),
        live_observations=int(live.sum()),
        live_filled_observations=int((live & filled).sum()),
        live_no_fill_observations=int((live & x["no_fill"]).sum()),
        live_partial_fill_observations=int((live & x["partial_fill"]).sum()),
        live_full_fill_observations=int((live & x["full_fill"]).sum()),
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
        accepted_execution_sources_only=bool(x["source"].isin(ACCEPTED_EXECUTION_SOURCES).all()),
        contains_paper_execution_evidence=bool(paper.any()),
        contains_live_execution_evidence=bool(live.any()),
        live_execution_source_only=bool(live.all()),
        complete_markout_for_fills=complete_markout,
        structural_execution_evidence_ready=bool(filled.any() and complete_markout),
        live_structural_execution_evidence_present=live_structural,
        # One or more structurally valid LIVE rows are not sufficient to close
        # the empirical execution blocker. Keep the legacy-looking field false
        # until a separately frozen sufficiency protocol exists and passes.
        live_empirical_execution_evidence_ready=False,
        empirical_execution_sufficiency_assessed=False,
        empirical_execution_blocker_closed=False,
    )
    out = asdict(audit)
    out["promotion_ready"] = False
    out["promotion_note"] = (
        "Paper observations validate broker/execution plumbing only. Structurally valid LIVE observations may contribute to empirical evidence, "
        "but this audit does not invent a sample-sufficiency threshold. live_empirical_execution_evidence_ready and empirical_execution_blocker_closed therefore remain false until a separately frozen, preregistered sufficiency protocol exists and passes. "
        "Capacity, tails, sealed holdout and prospective confirmation remain separate requirements."
    )
    return out
