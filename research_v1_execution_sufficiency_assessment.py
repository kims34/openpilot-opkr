"""Independent evaluator for the frozen IndexAlert LIVE execution-sufficiency protocol.

This evaluator consumes genuine broker execution observations only. Synthetic or
unit-test fixtures may test the code path but can never become project evidence.
A passing result closes only the empirical execution blocker; it never authorizes
sealed holdout use, model promotion, broker stage advancement or live trading.
"""
from __future__ import annotations

from math import ceil, sqrt
from pathlib import Path
import json
from typing import Any, Mapping

import numpy as np
import pandas as pd

from research_v1_execution_evidence import (
    LIVE_EXECUTION_SOURCE,
    validate_execution_observations,
)
from research_v1_execution_sufficiency_protocol import (
    ExecutionSufficiencyProtocolError,
    validate_execution_sufficiency_protocol,
)


PROJECT_PROTOCOL_JSON = "INDEXALERT_EXECUTION_SUFFICIENCY_PROTOCOL.json"
PROJECT_PROTOCOL_DOCUMENT = "INDEXALERT_EXECUTION_SUFFICIENCY_PROTOCOL.md"

EXTRA_REQUIRED_COLUMNS = {
    "observation_id",
    "decision_policy_id",
    "execution_policy_id",
    "recommendation_expires_at",
    "order_outcome_at",
    "order_expiry_at",
    "reference_adv20_krw",
    "capacity_reference_available_at",
    "entry_slippage_budget_bps",
    "cost_budget_at",
    "modeled_fees_tax_bps",
    "actual_fees_tax_bps",
    "unknown_order_outcome",
    "reconciliation_resolved",
    "risk_limit_breach",
}


class ExecutionSufficiencyAssessmentError(ValueError):
    pass


def _ts(series: pd.Series) -> pd.Series:
    return pd.to_datetime(series, errors="coerce", utc=True)


def _bool_series(series: pd.Series, field: str) -> pd.Series:
    if not series.map(lambda v: isinstance(v, (bool, np.bool_))).all():
        raise ExecutionSufficiencyAssessmentError(f"{field} must contain booleans only")
    return series.astype(bool)


def _cluster_ci(
    frame: pd.DataFrame,
    column: str,
    *,
    samples: int = 3000,
    seed: int = 20261001,
) -> tuple[float, float, float]:
    z = frame[["decision_date", column]].copy()
    z[column] = pd.to_numeric(z[column], errors="coerce")
    z = z.replace([np.inf, -np.inf], np.nan).dropna()
    if z.empty:
        return float("nan"), float("nan"), float("nan")
    daily = z.groupby("decision_date", sort=True)[column].mean().to_numpy(dtype=float)
    point = float(np.mean(daily))
    if len(daily) == 1:
        return point, point, point
    rng = np.random.default_rng(seed)
    draws = np.empty(samples, dtype=float)
    for i in range(samples):
        idx = rng.integers(0, len(daily), size=len(daily))
        draws[i] = float(np.mean(daily[idx]))
    lo, hi = np.quantile(draws, [0.025, 0.975])
    return point, float(lo), float(hi)


def _wilson(successes: int, n: int, z: float = 1.959963984540054) -> tuple[float, float, float]:
    if n <= 0:
        return float("nan"), float("nan"), float("nan")
    p = successes / n
    denom = 1.0 + z * z / n
    center = (p + z * z / (2.0 * n)) / denom
    half = z * sqrt((p * (1.0 - p) + z * z / (4.0 * n)) / n) / denom
    return float(p), float(max(0.0, center - half)), float(min(1.0, center + half))


def _lower_tail_es(series: pd.Series, alpha: float) -> float | None:
    x = pd.to_numeric(series, errors="coerce").replace([np.inf, -np.inf], np.nan).dropna().to_numpy(dtype=float)
    if len(x) == 0:
        return None
    x = np.sort(x)
    k = max(1, int(ceil((1.0 - alpha) * len(x))))
    return float(np.mean(x[:k]))


def _quantile(series: pd.Series, q: float) -> float | None:
    x = pd.to_numeric(series, errors="coerce").replace([np.inf, -np.inf], np.nan).dropna()
    return None if x.empty else float(x.quantile(q))


def load_frozen_project_protocol(base_dir: str | Path = ".") -> tuple[dict[str, Any], str]:
    root = Path(base_dir)
    raw = (root / PROJECT_PROTOCOL_JSON).read_text(encoding="utf-8")
    document = (root / PROJECT_PROTOCOL_DOCUMENT).read_text(encoding="utf-8")
    payload = json.loads(raw)
    validate_execution_sufficiency_protocol(payload, protocol_document_text=document)
    return payload, document


def prepare_live_execution_sufficiency_evidence(
    table: pd.DataFrame,
    protocol: Mapping[str, Any],
) -> pd.DataFrame:
    missing = sorted(EXTRA_REQUIRED_COLUMNS - set(table.columns))
    if missing:
        raise ExecutionSufficiencyAssessmentError(
            f"execution sufficiency evidence missing required columns: {missing}"
        )

    x = validate_execution_observations(table)
    if not x["source"].eq(LIVE_EXECUTION_SOURCE).all():
        raise ExecutionSufficiencyAssessmentError(
            "execution sufficiency assessment accepts genuine LIVE source rows only"
        )

    x["observation_id"] = table["observation_id"].astype(str).str.strip().to_numpy()
    if x["observation_id"].eq("").any() or x["observation_id"].duplicated().any():
        raise ExecutionSufficiencyAssessmentError("observation_id must be non-empty and unique")

    for field in ["decision_policy_id", "execution_policy_id"]:
        x[field] = table[field].astype(str).str.strip().to_numpy()
        if x[field].eq("").any():
            raise ExecutionSufficiencyAssessmentError(f"{field} must be non-empty")
        expected = str(protocol[field]).strip()
        if not x[field].eq(expected).all():
            raise ExecutionSufficiencyAssessmentError(
                f"mixed or unexpected {field}; expected frozen value {expected}"
            )

    for field in [
        "recommendation_expires_at",
        "order_outcome_at",
        "order_expiry_at",
        "capacity_reference_available_at",
        "cost_budget_at",
    ]:
        x[field] = _ts(table[field])
        if x[field].isna().any():
            raise ExecutionSufficiencyAssessmentError(f"{field} must be timezone-aware/parseable")

    if (x["recommendation_expires_at"] <= x["recommendation_at"]).any():
        raise ExecutionSufficiencyAssessmentError("recommendation_expires_at must follow recommendation_at")
    if (x["order_expiry_at"] <= x["order_submitted_at"]).any():
        raise ExecutionSufficiencyAssessmentError("order_expiry_at must follow order_submitted_at")
    if (x["order_outcome_at"] < x["order_submitted_at"]).any():
        raise ExecutionSufficiencyAssessmentError("order_outcome_at cannot precede order submission")
    if (x["capacity_reference_available_at"] > x["recommendation_at"]).any():
        raise ExecutionSufficiencyAssessmentError("capacity ADV20 must be PIT-available by recommendation time")
    if (x["cost_budget_at"] > x["recommendation_at"]).any():
        raise ExecutionSufficiencyAssessmentError("entry cost budget must be frozen by recommendation time")

    for field in [
        "reference_adv20_krw",
        "entry_slippage_budget_bps",
        "modeled_fees_tax_bps",
        "actual_fees_tax_bps",
    ]:
        x[field] = pd.to_numeric(table[field], errors="coerce").to_numpy()
        if x[field].isna().any() or np.isinf(x[field]).any():
            raise ExecutionSufficiencyAssessmentError(f"{field} must be finite numeric")
    if (x["reference_adv20_krw"] <= 0).any():
        raise ExecutionSufficiencyAssessmentError("reference_adv20_krw must be positive")
    if (x["entry_slippage_budget_bps"] <= 0).any():
        raise ExecutionSufficiencyAssessmentError("entry_slippage_budget_bps must be positive")
    if (x[["modeled_fees_tax_bps", "actual_fees_tax_bps"]] < 0).any().any():
        raise ExecutionSufficiencyAssessmentError("fee/tax bps cannot be negative")

    x["unknown_order_outcome"] = _bool_series(table["unknown_order_outcome"], "unknown_order_outcome").to_numpy()
    x["reconciliation_resolved"] = _bool_series(table["reconciliation_resolved"], "reconciliation_resolved").to_numpy()
    x["risk_limit_breach"] = _bool_series(table["risk_limit_breach"], "risk_limit_breach").to_numpy()

    no_fill = x["filled_qty"].eq(0)
    if (x.loc[no_fill, "actual_fees_tax_bps"] != 0).any():
        raise ExecutionSufficiencyAssessmentError("no-fill observations must have zero actual fees/tax")

    x["requested_notional_krw"] = x["requested_qty"] * x["reference_open"]
    x["participation_rate"] = x["requested_notional_krw"] / x["reference_adv20_krw"]
    x["capacity_breach"] = x["participation_rate"] > float(protocol["maximum_participation_rate"])
    x["near_capacity"] = x["participation_rate"] >= (
        float(protocol["maximum_participation_rate"]) * float(protocol["near_capacity_floor_fraction"])
    )
    x["expired_submission"] = x["order_submitted_at"] > x["recommendation_expires_at"]
    filled = x["filled_qty"] > 0
    x["late_fill_after_order_expiry"] = False
    x.loc[filled, "late_fill_after_order_expiry"] = (
        x.loc[filled, "first_fill_at"] > x.loc[filled, "order_expiry_at"]
    )

    ttl_ms = (x["recommendation_expires_at"] - x["recommendation_at"]).dt.total_seconds() * 1000.0
    expiry_ms = (x["order_expiry_at"] - x["order_submitted_at"]).dt.total_seconds() * 1000.0
    x["submit_latency_ttl_fraction"] = x["submit_latency_ms"] / ttl_ms
    x["first_fill_latency_expiry_fraction"] = np.where(
        filled, x["time_to_first_fill_ms"] / expiry_ms, np.nan
    )
    x["excess_slippage_bps"] = np.where(
        filled,
        x["buy_slippage_vs_open_bps"] - x["entry_slippage_budget_bps"],
        np.nan,
    )
    x["positive_slippage_budget_ratio"] = np.where(
        filled,
        np.maximum(x["buy_slippage_vs_open_bps"], 0.0) / x["entry_slippage_budget_bps"],
        np.nan,
    )
    x["fee_tax_excess_bps"] = np.where(
        filled,
        x["actual_fees_tax_bps"] - x["modeled_fees_tax_bps"],
        np.nan,
    )
    x["markout_5m_plus_budget_bps"] = np.where(
        filled,
        x["markout_5m_bps"] + x["entry_slippage_budget_bps"],
        np.nan,
    )
    return x


def assess_execution_sufficiency(
    table: pd.DataFrame,
    protocol: Mapping[str, Any],
    *,
    protocol_document_text: str | None = None,
) -> dict[str, Any]:
    if str(protocol.get("schema_version")) != "2":
        raise ExecutionSufficiencyAssessmentError("empirical assessment requires schema_version 2")
    if protocol_document_text is None:
        raise ExecutionSufficiencyAssessmentError(
            "exact frozen protocol document text is required for SHA-256 binding"
        )

    x = prepare_live_execution_sufficiency_evidence(table, protocol)
    first_live = x["recommendation_at"].min().to_pydatetime()
    try:
        validated = validate_execution_sufficiency_protocol(
            protocol,
            first_live_recommendation_at=first_live,
            protocol_document_text=protocol_document_text,
        )
    except ExecutionSufficiencyProtocolError as exc:
        raise ExecutionSufficiencyAssessmentError(str(exc)) from exc
    p = validated["protocol"]

    live_n = int(len(x))
    dates_n = int(x["decision_date"].nunique())
    filled = x["filled_qty"] > 0
    no_fill = x["no_fill"]
    partial = x["partial_fill"]
    filled_n = int(filled.sum())
    no_fill_n = int(no_fill.sum())
    partial_n = int(partial.sum())
    near = x["near_capacity"]
    near_n = int(near.sum())

    fill_point, fill_lcb, fill_ucb = _cluster_ci(x, "fill_ratio")
    no_fill_rate, no_fill_lcb, no_fill_ucb = _wilson(no_fill_n, live_n)
    partial_rate, partial_lcb, partial_ucb = _wilson(partial_n, live_n)

    filled_x = x.loc[filled].copy()
    slip_point, slip_lcb, slip_ucb = _cluster_ci(filled_x, "excess_slippage_bps")
    fee_point, fee_lcb, fee_ucb = _cluster_ci(filled_x, "fee_tax_excess_bps")
    mark5_point, mark5_lcb, mark5_ucb = _cluster_ci(filled_x, "markout_5m_plus_budget_bps")
    near_fill_point, near_fill_lcb, near_fill_ucb = _cluster_ci(x.loc[near], "fill_ratio")
    near_filled = near & filled
    near_slip_point, near_slip_lcb, near_slip_ucb = _cluster_ci(x.loc[near_filled], "excess_slippage_bps")

    slip_ratio_p95 = _quantile(filled_x["positive_slippage_budget_ratio"], 0.95)
    slip_ratio_p99 = _quantile(filled_x["positive_slippage_budget_ratio"], 0.99)
    submit_frac_p95 = _quantile(x["submit_latency_ttl_fraction"], 0.95)
    fill_expiry_frac_p95 = _quantile(filled_x["first_fill_latency_expiry_fraction"], 0.95)

    gates = {
        "minimum_live_observations": live_n >= int(p["minimum_live_observations"]),
        "minimum_distinct_decision_dates": dates_n >= int(p["minimum_distinct_decision_dates"]),
        "minimum_filled_observations": filled_n >= int(p["minimum_filled_observations"]),
        "minimum_no_fill_observations": no_fill_n >= int(p["minimum_no_fill_observations"]),
        "minimum_partial_fill_observations": partial_n >= int(p["minimum_partial_fill_observations"]),
        "minimum_near_capacity_observations": near_n >= int(p["minimum_near_capacity_observations"]),
        "mean_fill_ratio_lcb95": fill_lcb >= float(p["minimum_mean_fill_ratio_lcb95"]),
        "no_fill_rate_ucb95": no_fill_ucb <= float(p["maximum_no_fill_rate_ucb95"]),
        "partial_fill_rate_ucb95": partial_ucb <= float(p["maximum_partial_fill_rate_ucb95"]),
        "mean_excess_slippage_ucb95": slip_ucb <= float(p["maximum_mean_excess_slippage_bps_ucb95"]),
        "slippage_budget_ratio_p95": slip_ratio_p95 is not None and slip_ratio_p95 <= float(p["maximum_slippage_budget_ratio_p95"]),
        "slippage_budget_ratio_p99": slip_ratio_p99 is not None and slip_ratio_p99 <= float(p["maximum_slippage_budget_ratio_p99"]),
        "fee_tax_excess_ucb95": fee_ucb <= float(p["maximum_fee_tax_excess_bps_ucb95"]),
        "submit_latency_ttl_fraction_p95": submit_frac_p95 is not None and submit_frac_p95 <= float(p["maximum_submit_latency_ttl_fraction_p95"]),
        "first_fill_latency_expiry_fraction_p95": fill_expiry_frac_p95 is not None and fill_expiry_frac_p95 <= float(p["maximum_first_fill_latency_expiry_fraction_p95"]),
        "markout_5m_plus_budget_lcb95": mark5_lcb >= float(p["minimum_5m_markout_plus_budget_lcb95_bps"]),
        "near_capacity_mean_fill_ratio_lcb95": near_fill_lcb >= float(p["minimum_near_capacity_mean_fill_ratio_lcb95"]),
        "near_capacity_mean_excess_slippage_ucb95": near_slip_ucb <= float(p["maximum_near_capacity_mean_excess_slippage_bps_ucb95"]),
        "zero_expired_submissions": int(x["expired_submission"].sum()) == 0,
        "zero_late_fills_after_order_expiry": int(x["late_fill_after_order_expiry"].sum()) == 0,
        "zero_capacity_breaches": int(x["capacity_breach"].sum()) == 0,
        "zero_unknown_outcomes": int(x["unknown_order_outcome"].sum()) == 0,
        "zero_reconciliation_failures": int((~x["reconciliation_resolved"]).sum()) == 0,
        "zero_risk_limit_breaches": int(x["risk_limit_breach"].sum()) == 0,
        "complete_markouts": bool(filled_x[["markout_5m_bps", "markout_30m_bps", "markout_close_bps"]].notna().all().all()),
    }
    passed = bool(all(gates.values()))

    def markout_summary(label: str) -> dict[str, Any]:
        col = f"markout_{label}_bps"
        point, lo, hi = _cluster_ci(filled_x, col)
        return {
            "mean_bps": point,
            "cluster_95_low_bps": lo,
            "cluster_95_high_bps": hi,
            "adverse_es95_bps": _lower_tail_es(filled_x[col], 0.95),
            "adverse_es99_bps": _lower_tail_es(filled_x[col], 0.99),
        }

    return {
        "protocol_id": p["protocol_id"],
        "protocol_fingerprint_sha256": validated["protocol_fingerprint_sha256"],
        "protocol_document_sha256_verified": validated["protocol_document_sha256_verified"],
        "first_live_recommendation_at": validated["first_live_recommendation_at"],
        "preregistered_before_first_live_observation": validated["preregistered_before_first_live_observation"],
        "counts": {
            "live_observations": live_n,
            "distinct_decision_dates": dates_n,
            "filled_observations": filled_n,
            "no_fill_observations": no_fill_n,
            "partial_fill_observations": partial_n,
            "near_capacity_observations": near_n,
        },
        "fill": {
            "mean_fill_ratio": fill_point,
            "cluster_95_low": fill_lcb,
            "cluster_95_high": fill_ucb,
            "no_fill_rate": no_fill_rate,
            "no_fill_wilson_95_low": no_fill_lcb,
            "no_fill_wilson_95_high": no_fill_ucb,
            "partial_fill_rate": partial_rate,
            "partial_fill_wilson_95_low": partial_lcb,
            "partial_fill_wilson_95_high": partial_ucb,
        },
        "slippage": {
            "mean_excess_slippage_bps": slip_point,
            "cluster_95_low_bps": slip_lcb,
            "cluster_95_high_bps": slip_ucb,
            "positive_slippage_budget_ratio_p95": slip_ratio_p95,
            "positive_slippage_budget_ratio_p99": slip_ratio_p99,
        },
        "fee_tax": {
            "mean_excess_bps": fee_point,
            "cluster_95_low_bps": fee_lcb,
            "cluster_95_high_bps": fee_ucb,
        },
        "latency": {
            "submit_latency_ttl_fraction_p95": submit_frac_p95,
            "first_fill_latency_expiry_fraction_p95": fill_expiry_frac_p95,
        },
        "capacity": {
            "maximum_observed_participation_rate": float(x["participation_rate"].max()),
            "near_capacity_observations": near_n,
            "near_capacity_mean_fill_ratio": near_fill_point,
            "near_capacity_fill_cluster_95_low": near_fill_lcb,
            "near_capacity_fill_cluster_95_high": near_fill_ucb,
            "near_capacity_mean_excess_slippage_bps": near_slip_point,
            "near_capacity_excess_slippage_cluster_95_low_bps": near_slip_lcb,
            "near_capacity_excess_slippage_cluster_95_high_bps": near_slip_ucb,
        },
        "markouts": {
            "5m": markout_summary("5m"),
            "30m": markout_summary("30m"),
            "close": markout_summary("close"),
            "five_minute_plus_budget_mean_bps": mark5_point,
            "five_minute_plus_budget_cluster_95_low_bps": mark5_lcb,
            "five_minute_plus_budget_cluster_95_high_bps": mark5_ucb,
        },
        "integrity": {
            "expired_submissions": int(x["expired_submission"].sum()),
            "late_fills_after_order_expiry": int(x["late_fill_after_order_expiry"].sum()),
            "capacity_breaches": int(x["capacity_breach"].sum()),
            "unknown_outcomes": int(x["unknown_order_outcome"].sum()),
            "reconciliation_failures": int((~x["reconciliation_resolved"]).sum()),
            "risk_limit_breaches": int(x["risk_limit_breach"].sum()),
        },
        "gates": gates,
        "failed_gates": [name for name, ok in gates.items() if not ok],
        "empirical_execution_sufficiency_assessed": True,
        "live_empirical_execution_evidence_ready": passed,
        "empirical_execution_blocker_closed": passed,
        "promotion_ready": False,
        "sealed_holdout_authorized": False,
        "live_trading_authorized": False,
        "guardrail": (
            "Passing this evaluator closes only the empirical execution blocker. "
            "KRX/status/PIT/statistical/holdout/prospective confirmation and explicit live-mode gates remain independent."
        ),
    }
