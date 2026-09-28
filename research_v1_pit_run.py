"""PIT-preliminary KOSPI tournament on a historical daily membership panel.

Fair-comparison rules:
- same trailing ADV20 bottom-20% exclusion for every model;
- original top-3 only for rankers; held names leave empty slots;
- direct-net-return regression may admit 0..3 only when predicted net > 0;
- same-bar target/stop uses conservative stop-first;
- post-entry missing bars are retained as conservative stop-like outcomes instead
  of deleting the security with future information;
- final Judge remains blocked until common-stock identity and exact delisting /
  halt economics are independently validated.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from research_v1_data_policy import dataset_status
from research_v1_holdaware import evaluate_topk_only
from research_v1_context import add_context, evaluate as evaluate_context, predict_walk_forward
from research_v1_ml import (
    evaluate_regression_model,
    stateful_select_records,
    walk_forward_predictions,
    walk_forward_regression_predictions,
)
from research_v1_pit_labels import make_pit_supervised
from research_v1_selective import run_selective
from research_v1_portfolio import simulate_portfolio, summary_dict
from research_v1_core import date_cluster_bootstrap_mean, summarize
from run_research_v1 import load_panel


def _metric_block(records):
    m = summarize(records)
    point, lo, hi = date_cluster_bootstrap_mean(records) if records else (0.0, 0.0, 0.0)
    return {
        **m.__dict__,
        "cluster_bootstrap_mean_net_return": point,
        "cluster_bootstrap_95_low": lo,
        "cluster_bootstrap_95_high": hi,
    }


def _portfolio(raw, records, horizon, all_dates):
    if all_dates:
        eval_start = pd.Timestamp(min(all_dates)).date()
        eval_end = max(
            pd.Timestamp(max(all_dates)).date(),
            max((r.exit_day for r in records), default=pd.Timestamp(max(all_dates)).date()),
        )
    else:
        eval_start = eval_end = None
    _, port = simulate_portfolio(
        raw, records, horizon=horizon, initial_equity=1.0,
        daily_cohort_fraction=1.0 / horizon, suppress_duplicate_symbols=False,
        evaluation_start=eval_start, evaluation_end=eval_end,
    )
    return summary_dict(port)


def _baseline_from_labeled_frame(
    raw: pd.DataFrame, frame: pd.DataFrame, record_map: dict,
    strategy: str, top_k: int, horizon: int,
):
    scored = frame.copy()
    if strategy == "momentum5":
        scored["score"] = scored["ret5"]
    elif strategy == "momentum20":
        scored["score"] = scored["ret20"]
    elif strategy == "momentum20_liquidity":
        scored["score"] = 0.8 * scored["ret20_rank"] + 0.2 * scored["adv20_rank"]
    else:
        raise ValueError(strategy)

    limited = (
        scored.sort_values(["decision_date", "score"], ascending=[True, False])
        .groupby("decision_date", group_keys=False)
        .head(top_k)
        .copy()
    )
    executed, selected, diag = stateful_select_records(
        limited, record_map, top_k=top_k, threshold=None, active_until={}
    )
    # Signal set before active-position suppression, using only the original top-K.
    signals = []
    for row in limited.itertuples(index=False):
        key = (pd.Timestamp(row.decision_date).date(), str(row.symbol))
        base = record_map.get(key)
        if base is not None:
            signals.append(base.__class__(**{**base.__dict__, "score": float(row.score)}))
    return {
        "signal_set": _metric_block(signals),
        "executable_set": _metric_block(executed),
        "portfolio": _portfolio(raw, executed, horizon, list(scored["decision_date"].unique())),
        **diag,
        "selection_policy": "original_top3_only__held_names_leave_empty_slots",
        "test_dates": int(scored["decision_date"].nunique()),
        "trade_days": int(selected["decision_date"].nunique()) if not selected.empty else 0,
        "trade_day_coverage": float(selected["decision_date"].nunique() / scored["decision_date"].nunique()) if not selected.empty else 0.0,
    }


def _grade(candidate: dict) -> dict:
    ex = candidate.get("executable_set", {})
    p = candidate.get("portfolio", {})
    trades = int(ex.get("trades") or 0)
    net = float(ex.get("mean_net_return") or 0.0)
    pf = float(ex.get("profit_factor") or 0.0)
    lo = float(ex.get("cluster_bootstrap_95_low") or 0.0)
    mdd = float(p.get("max_drawdown") or 0.0)
    issues = []
    if trades == 0:
        return {"grade": "NO_TRADE_FAIL_CLOSED", "issues": ["No trades admitted."]}
    if net <= 0:
        issues.append("mean_net_return_not_positive")
    if pf <= 1.0:
        issues.append("profit_factor_not_above_1")
    if lo <= 0:
        issues.append("date_cluster_95pct_lower_bound_not_positive")
    if mdd <= -0.10:
        issues.append("max_drawdown_worse_than_10pct")
    if not issues:
        return {"grade": "PIT_PRELIMINARY_PROMISING", "issues": []}
    if net > 0 and pf > 1:
        return {"grade": "PIT_PRELIMINARY_INSUFFICIENT_CONFIDENCE", "issues": issues}
    return {"grade": "PIT_PRELIMINARY_NOT_SUITABLE_YET", "issues": issues}


def _compact(report: dict) -> dict:
    return {
        "evaluation_stage": report.get("evaluation_stage"),
        "data_start": report.get("data_start"),
        "data_end": report.get("data_end"),
        "raw_rows": report.get("raw_rows"),
        "raw_symbols": report.get("raw_symbols"),
        "supervised_rows": report.get("supervised_rows_after_liquidity_gate"),
        "supervised_dates": report.get("supervised_dates"),
        "diagnostics": report.get("diagnostics"),
        "overall": report.get("overall_preliminary_assessment"),
        "ranking": report.get("conservative_ranking"),
        "blockers": report.get("final_judge_blockers"),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cache", default="research_data/marcap_kospi_pit")
    ap.add_argument("--result-dir", default="research_results/marcap_pit")
    ap.add_argument("--horizon", type=int, default=5)
    ap.add_argument("--top-k", type=int, default=3)
    ap.add_argument("--target", type=float, default=0.04)
    ap.add_argument("--stop", type=float, default=-0.025)
    ap.add_argument("--participation", type=float, default=0.0005)
    ap.add_argument("--train-days", type=int, default=200)
    ap.add_argument("--test-days", type=int, default=40)
    args = ap.parse_args()

    raw = load_panel(Path(args.cache))
    status = dataset_status(raw)
    if not status["point_in_time_universe"]:
        raise RuntimeError("PIT runner requires point_in_time_universe=True")

    frame, record_map, diag = make_pit_supervised(
        raw, horizon=args.horizon, target_return=args.target,
        stop_return=args.stop, participation=args.participation,
    )
    pre_filter_rows = len(frame)
    # Same date-local trailing ADV eligibility as the baseline research policy.
    frame = frame[frame["adv20_rank"] >= 0.20].copy().reset_index(drop=True)

    report = {
        "judge_version": "KR-KOSPI-JUDGE-v1.0",
        **status,
        "evaluation_stage": "PIT_PRELIMINARY",
        "final_judge_blockers": [
            "common_stock_identity_not_validated" if not status["common_stock_identity_validated"] else None,
            "post_entry_missing_bar_uses_preliminary_planned_stop_not_exact_delisting_halt_value",
            "entry_no_fill_rows_are_not_yet_retained_in_prediction_ranking",
            "daily_OHLC_same_bar_barrier_order_uses_conservative_stop_first",
        ],
        "data_start": str(raw["decision_date"].min().date()),
        "data_end": str(raw["decision_date"].max().date()),
        "raw_rows": int(len(raw)),
        "raw_symbols": int(raw["symbol"].nunique()),
        "supervised_rows_before_liquidity_gate": int(pre_filter_rows),
        "supervised_rows_after_liquidity_gate": int(len(frame)),
        "supervised_dates": int(frame["decision_date"].nunique()),
        "liquidity_policy": "trailing_ADV20_same_date_bottom_20pct_excluded_for_all_models",
        "diagnostics": diag,
        "candidates": {},
    }
    report["final_judge_blockers"] = [x for x in report["final_judge_blockers"] if x]

    for strategy in ["momentum5", "momentum20", "momentum20_liquidity"]:
        report["candidates"][f"baseline_{strategy}"] = _baseline_from_labeled_frame(
            raw, frame, record_map, strategy, args.top_k, args.horizon
        )

    log_pred = walk_forward_predictions(frame, "logistic_l2", args.train_days, args.test_days)
    log_result, _, _ = evaluate_topk_only(log_pred, record_map, raw, args.horizon, args.top_k)
    log_result["objective"] = "probability_positive_net_return"
    log_result["admission_rule"] = "original_top3_only__held_names_leave_empty_slots"
    report["candidates"]["logistic_l2_top3_only"] = log_result

    ridge_pred = walk_forward_regression_predictions(frame, args.train_days, args.test_days)
    ridge_result, _, _ = evaluate_regression_model(
        ridge_pred, record_map, raw, args.horizon, args.top_k, positive_only=True
    )
    ridge_result["admission_rule"] = "predicted_net_return_gt_0__0_to_3"
    report["candidates"]["ridge_net_positive_only"] = ridge_result

    context_frame = add_context(frame)
    context_log = predict_walk_forward(context_frame, "logistic_context", args.train_days, args.test_days)
    result, _, _ = evaluate_context(
        context_log, record_map, raw, args.horizon, args.top_k,
        threshold=None, original_topk_only=True,
    )
    result["objective"] = "probability_positive_net_return_plus_simple_market_context"
    result["admission_rule"] = "original_top3_only__held_names_leave_empty_slots"
    report["candidates"]["logistic_context_top3_only"] = result

    context_ridge = predict_walk_forward(context_frame, "ridge_context", args.train_days, args.test_days)
    result, _, _ = evaluate_context(
        context_ridge, record_map, raw, args.horizon, args.top_k,
        threshold=0.0, original_topk_only=False,
    )
    result["objective"] = "direct_net_return_plus_simple_market_context"
    result["admission_rule"] = "predicted_net_return_gt_0__0_to_3"
    report["candidates"]["ridge_context_positive_only"] = result

    selective, _, _, _ = run_selective(
        frame, record_map, raw,
        train_days=max(100, args.train_days - 40), calibration_days=40,
        test_days=args.test_days, top_k=args.top_k, horizon=args.horizon,
    )
    report["candidates"]["logistic_calibrated_abstention"] = selective

    grades = {name: _grade(candidate) for name, candidate in report["candidates"].items()}
    report["grades"] = grades

    ranked = []
    for name, c in report["candidates"].items():
        ex = c.get("executable_set", {})
        port = c.get("portfolio", {})
        ranked.append({
            "name": name,
            "trades": int(ex.get("trades") or 0),
            "mean_net_return": float(ex.get("mean_net_return") or 0.0),
            "profit_factor": float(ex.get("profit_factor") or 0.0),
            "cluster_low": float(ex.get("cluster_bootstrap_95_low") or 0.0),
            "cluster_high": float(ex.get("cluster_bootstrap_95_high") or 0.0),
            "total_return": float(port.get("total_return") or 0.0),
            "max_drawdown": float(port.get("max_drawdown") or 0.0),
            **grades[name],
        })
    ranked.sort(key=lambda x: (x["cluster_low"], x["mean_net_return"], x["profit_factor"]), reverse=True)
    report["conservative_ranking"] = ranked
    report["overall_preliminary_assessment"] = (
        "AT_LEAST_ONE_PRELIMINARY_PROMISING_CANDIDATE"
        if any(x["grade"] == "PIT_PRELIMINARY_PROMISING" for x in ranked)
        else "NO_ROBUST_SHORT_TERM_EDGE_YET"
    )
    report["warning"] = (
        "PIT membership materially improves validity versus the fixed-basket smoke test. "
        "Post-entry data gaps are no longer future-filtered, but final Judge promotion still requires "
        "common-stock identity and exact delisting/halt economics."
    )

    out = Path(args.result_dir)
    out.mkdir(parents=True, exist_ok=True)
    compact = _compact(report)
    (out / "summary.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    (out / "compact.json").write_text(json.dumps(compact, ensure_ascii=False, indent=2), encoding="utf-8")
    pd.DataFrame(ranked).to_csv(out / "candidate_comparison.csv", index=False)
    print("PIT_COMPACT=" + json.dumps(compact, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
