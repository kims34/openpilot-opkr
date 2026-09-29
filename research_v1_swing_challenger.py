"""Preregistered Swing Challenger for IndexAlert research.

This module does NOT modify the existing 5-session Short research policy.
It evaluates the separately named H10 swing challenger through an independent CI job.

Frozen policy for each horizon:
- corporate-action-safe PIT features/labels/MTM
- date-aware statutory tax + commission + spread/impact cost
- expanding 504-session training history
- independent 126-session calibration block
- independent 126-session OOS test blocks
- purge/embargo exactly equal to the evaluated holding horizon
- selection-conditioned q25/q50/q75 residual calibration
- conservative NetEV lower bound > 0
- freeze original decision-time Top3
- post-rank normal-market fail-closed veto
- vetoed/held/unfillable names leave empty slots
- no rank-4+ backfill

The primary Swing Challenger uses all_context features. context_only is retained as a
prespecified diagnostic only. This is developmental evidence, never a sealed holdout
or production-promotion test.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from research_v1_context import CONTEXT_FEATURES, add_context
from research_v1_distributional_long_history import CONTEXT_ONLY, evaluate_candidate
from research_v1_distributional_netev import _fixed_record_map
from research_v1_fixed_horizon_label import add_fixed_horizon_target
from research_v1_selected_calibration import _evaluate_with_runner, selected_calibration_walk_forward
from research_v1_supervised_cache import load_or_build
from run_research_v1 import load_panel

ALLOWED_SWING_HORIZONS = (10,)
TRAIN_DAYS = 504
CAL_DAYS = 126
TEST_DAYS = 126
TOP_K = 3


def _safe(d: dict, *path, default=None):
    cur = d
    for key in path:
        if not isinstance(cur, dict) or key not in cur:
            return default
        cur = cur[key]
    return cur


def _robustness_flags(candidate: dict) -> dict:
    gate = candidate.get("market_eligibility_overlay", {})
    metrics = gate.get("metrics", {})
    best5 = _safe(
        gate, "extreme_day_dependency", "remove_best_days", "5", "metrics",
        default={},
    ) or {}
    cost2 = _safe(gate, "cost_stress", "2.0", default={}) or {}

    # Frozen Master-Spec contract: best-5 removal must preserve positive mean,
    # PF>1 and positive date-cluster LCB. 2x-cost must preserve positive mean
    # and PF>1. These are conjunctions, not point-estimate-only checks.
    best5_robust = bool(
        float(best5.get("mean_net_return", 0.0)) > 0.0
        and float(best5.get("profit_factor", 0.0)) > 1.0
        and float(best5.get("cluster_bootstrap_95_low", 0.0)) > 0.0
    )
    cost2_robust = bool(
        float(cost2.get("mean_net_return", 0.0)) > 0.0
        and float(cost2.get("profit_factor", 0.0)) > 1.0
    )
    flags = {
        "positive_mean_net": float(metrics.get("mean_net_return", 0.0)) > 0.0,
        "profit_factor_gt_1": float(metrics.get("profit_factor", 0.0)) > 1.0,
        "positive_date_cluster_lcb": float(metrics.get("cluster_bootstrap_95_low", 0.0)) > 0.0,
        "positive_after_remove_best_5_days": best5_robust,
        "positive_at_2x_cost": cost2_robust,
    }
    flags["all_developmental_robustness_checks_pass"] = all(flags.values())
    return flags


def _comparison_view(candidate: dict) -> dict:
    """Expose the frozen Short-vs-Swing comparison fields without retuning.

    Master-Spec dominance uses *daily portfolio* ES95/ES99, not trade-level ES.
    Keep both families explicit; the legacy ``es95``/``es99`` comparison keys
    now intentionally point to the daily portfolio tail-risk metrics.
    """
    gate = candidate.get("market_eligibility_overlay", {})
    metrics = gate.get("metrics", {})
    portfolio = gate.get("portfolio", {})
    trade_es95 = float(metrics.get("trade_expected_shortfall_95", 0.0))
    trade_es99 = float(metrics.get("trade_expected_shortfall_99", 0.0))
    daily_es95 = float(portfolio.get("daily_expected_shortfall_95", 0.0))
    daily_es99 = float(portfolio.get("daily_expected_shortfall_99", 0.0))
    return {
        "selected_records": int(gate.get("selected_records", 0)),
        "trade_days": int(gate.get("trade_days", 0)),
        "trade_day_coverage": float(gate.get("trade_day_coverage", 0.0)),
        "precision_at_selected": float(metrics.get("precision_at_selected", 0.0)),
        "fixed_participation_cost_proxy_mean_net_return": float(
            metrics.get("mean_net_return", 0.0)
        ),
        "profit_factor": float(metrics.get("profit_factor", 0.0)),
        "mdd": float(portfolio.get("max_drawdown", 0.0)),
        "es95": daily_es95,
        "es99": daily_es99,
        "daily_portfolio_es95": daily_es95,
        "daily_portfolio_es99": daily_es99,
        "trade_es95": trade_es95,
        "trade_es99": trade_es99,
        "date_cluster_lcb95": float(metrics.get("cluster_bootstrap_95_low", 0.0)),
        "cost_model": {
            "participation_of_adv": 0.0005,
            "commission_round_trip_bps": 3.0,
            "date_aware_statutory_tax": True,
            "spread_impact_allowance": True,
            "capacity_curve_available": False,
        },
    }


def run_horizon(
    *,
    raw,
    supervised_cache: Path,
    horizon: int,
    top_k: int = TOP_K,
    train_days: int = TRAIN_DAYS,
    cal_days: int = CAL_DAYS,
    test_days: int = TEST_DAYS,
):
    if horizon not in ALLOWED_SWING_HORIZONS:
        raise ValueError(f"Swing horizon must be one of {ALLOWED_SWING_HORIZONS}; got {horizon}")
    if top_k != TOP_K:
        raise ValueError("Swing Challenger TopK is preregistered at 3 and must not be tuned")

    frame, legacy_map, label_diag, cache_meta = load_or_build(
        raw,
        supervised_cache,
        horizon=horizon,
        target_return=0.04,
        stop_return=-0.025,
        participation=0.0005,
        commission_round_trip_bps=3.0,
    )
    frame = frame[frame["adv20_rank"] >= 0.20].copy().reset_index(drop=True)
    context = add_context(frame)
    z = add_fixed_horizon_target(raw, context, legacy_map, horizon)
    fixed_map = _fixed_record_map(z, horizon)

    marginal_reference, _, marginal_gate_selected = evaluate_candidate(
        z,
        fixed_map,
        raw,
        name=f"swing_h{horizon}_all_context_marginal_q25_reference",
        features=CONTEXT_FEATURES,
        train_days=train_days,
        cal_days=cal_days,
        test_days=test_days,
        horizon=horizon,
        top_k=top_k,
    )

    primary, primary_selected, primary_gate_selected = _evaluate_with_runner(
        z,
        fixed_map,
        raw,
        name=f"swing_h{horizon}_all_context_selection_conditioned_q25",
        features=CONTEXT_FEATURES,
        runner=lambda zz, **kw: selected_calibration_walk_forward(
            zz, top_k=top_k, **kw
        ),
        train_days=train_days,
        cal_days=cal_days,
        test_days=test_days,
        horizon=horizon,
        top_k=top_k,
    )

    context_diag, context_selected, context_gate_selected = _evaluate_with_runner(
        z,
        fixed_map,
        raw,
        name=f"swing_h{horizon}_context_only_selection_conditioned_q25_diagnostic",
        features=CONTEXT_ONLY,
        runner=lambda zz, **kw: selected_calibration_walk_forward(
            zz, top_k=top_k, **kw
        ),
        train_days=train_days,
        cal_days=cal_days,
        test_days=test_days,
        horizon=horizon,
        top_k=top_k,
    )

    flags = _robustness_flags(primary)
    verdict = (
        "SWING_DEVELOPMENTAL_ROBUSTNESS_CHECKS_PASS_NOT_PROMOTED"
        if flags["all_developmental_robustness_checks_pass"]
        else "SWING_NO_ROBUST_EDGE_YET"
    )
    report = {
        "evaluation_stage": "SWING_CHALLENGER_LONG_HISTORY_CA_SAFE_NOT_SEALED_HOLDOUT",
        "strategy_family": "Swing Challenger",
        "short_strategy_modified": False,
        "horizon_sessions": int(horizon),
        "horizon_label": "~2_trading_weeks",
        "history_start": str(raw["decision_date"].min().date()),
        "history_end": str(raw["decision_date"].max().date()),
        "protocol": {
            "train_days_initial": int(train_days),
            "cal_days": int(cal_days),
            "test_days": int(test_days),
            "purge_days": int(horizon),
            "purge_equals_horizon": True,
            "liquidity_floor": "adv20_rank_ge_0.20",
            "primary_features": "all_context",
            "calibration": "calibration_daily_top3_by_pred_mean__q25_q50_q75",
            "admission": "netev_low_gt_0__freeze_original_top3__blocked_slot_stays_empty",
            "market_eligibility_overlay": "post_rank_abs_KRX_base_return_gt_30.5pct_veto__no_backfill",
            "top_k": int(top_k),
            "rank4plus_backfill": False,
            "hyperparameter_search": False,
            "horizon_search": False,
            "promotion_allowed": False,
        },
        "supervised_cache": cache_meta,
        "label_diagnostics": label_diag,
        "marginal_reference": marginal_reference,
        "primary_selection_conditioned": primary,
        "context_only_diagnostic": context_diag,
        "walk_forward_comparison_view": _comparison_view(primary),
        "robustness_flags": flags,
        "promotion_blockers": [
            "purged_cpcv_not_yet_run",
            "capacity_curve_not_available",
            "intraday_fill_partial_fill_and_markout_not_available",
            "sealed_holdout_not_run",
            "prospective_shadow_not_run",
        ],
        "verdict": verdict,
        "guardrail": (
            "H10 is a preregistered independent challenger. A better historical point estimate "
            "does not select a production winner. Any surviving candidate still requires fresh sealed "
            "evidence and prospective Shadow before promotion."
        ),
    }
    selections = {
        "marginal_normal_market": marginal_gate_selected,
        "primary_raw": primary_selected,
        "primary_normal_market": primary_gate_selected,
        "context_only_raw": context_selected,
        "context_only_normal_market": context_gate_selected,
    }
    return report, selections


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cache", default="research_data/marcap_kospi_pit_long")
    ap.add_argument("--supervised-cache", required=True)
    ap.add_argument("--result-dir", required=True)
    ap.add_argument("--horizon", type=int, required=True, choices=ALLOWED_SWING_HORIZONS)
    ap.add_argument("--top-k", type=int, default=TOP_K)
    ap.add_argument("--train-days", type=int, default=TRAIN_DAYS)
    ap.add_argument("--cal-days", type=int, default=CAL_DAYS)
    ap.add_argument("--test-days", type=int, default=TEST_DAYS)
    args = ap.parse_args()

    if args.train_days != TRAIN_DAYS or args.cal_days != CAL_DAYS or args.test_days != TEST_DAYS:
        raise ValueError("Swing train/cal/test windows are preregistered and cannot be tuned in this runner")

    raw = load_panel(Path(args.cache))
    report, selections = run_horizon(
        raw=raw,
        supervised_cache=Path(args.supervised_cache),
        horizon=args.horizon,
        top_k=args.top_k,
        train_days=args.train_days,
        cal_days=args.cal_days,
        test_days=args.test_days,
    )

    out = Path(args.result_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out / "summary.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2, default=str),
        encoding="utf-8",
    )
    for name, selected in selections.items():
        selected.to_csv(out / f"{name}_selected.csv", index=False)
    print("SWING_CHALLENGER=" + json.dumps(report, ensure_ascii=False, default=str), flush=True)


if __name__ == "__main__":
    main()

