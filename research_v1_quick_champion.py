"""Fast PIT diagnostic for the current simple champion candidate only.

Purpose: produce a leakage-controlled read on the current best simple structure
without waiting for the full model tournament.  This is diagnostic only; it does
not bypass final Judge blockers.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from research_v1_context import add_context
from research_v1_data_policy import dataset_status
from research_v1_holdaware import evaluate_topk_only
from research_v1_pit_labels import make_pit_supervised
from research_v1_pit_run_purged import _grade, _walk_forward_pit
from run_research_v1 import load_panel


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cache", default="research_data/marcap_kospi_pit")
    ap.add_argument("--result-dir", default="research_results/marcap_pit_quick")
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
        raise RuntimeError("quick champion diagnostic requires PIT membership")

    frame, record_map, diag = make_pit_supervised(
        raw,
        horizon=args.horizon,
        target_return=args.target,
        stop_return=args.stop,
        participation=args.participation,
    )
    before = len(frame)
    frame = frame[frame["adv20_rank"] >= 0.20].copy().reset_index(drop=True)
    context = add_context(frame)
    pred = _walk_forward_pit(
        context,
        "logistic_context",
        args.train_days,
        args.test_days,
        context=True,
        purge_days=args.horizon,
    )
    result, selected, _ = evaluate_topk_only(
        pred,
        record_map,
        raw,
        args.horizon,
        args.top_k,
    )
    result["objective"] = "probability_positive_net_return_plus_simple_market_context"
    result["admission_rule"] = "PURGED_original_top3_fixed_at_decision__no_fill_empty_slot"
    result["purge_days"] = int(args.horizon)

    ex = result.get("executable_set", {})
    port = result.get("portfolio", {})
    report = {
        "evaluation_stage": "PIT_PRELIMINARY_PURGED_QUICK_CHAMPION",
        "judge_eligible": False,
        "data_status": status,
        "horizon": int(args.horizon),
        "purge_days": int(args.horizon),
        "raw_rows": int(len(raw)),
        "raw_symbols": int(raw["symbol"].nunique()),
        "decision_rows_before_liquidity_gate": int(before),
        "decision_rows_after_liquidity_gate": int(len(frame)),
        "decision_dates": int(frame["decision_date"].nunique()),
        "label_diagnostics": diag,
        "candidate": {
            "trades": int(ex.get("trades") or 0),
            "mean_gross_return": float(ex.get("mean_gross_return") or 0.0),
            "mean_cost_return": float(ex.get("mean_cost_return") or 0.0),
            "mean_net_return": float(ex.get("mean_net_return") or 0.0),
            "win_rate": float(ex.get("win_rate") or 0.0),
            "profit_factor": float(ex.get("profit_factor") or 0.0),
            "expected_shortfall_95": float(ex.get("trade_expected_shortfall_95") or 0.0),
            "cluster_bootstrap_95_low": float(ex.get("cluster_bootstrap_95_low") or 0.0),
            "cluster_bootstrap_95_high": float(ex.get("cluster_bootstrap_95_high") or 0.0),
            "total_return": float(port.get("total_return") or 0.0),
            "cagr_252": float(port.get("cagr_252") or 0.0),
            "max_drawdown": float(port.get("max_drawdown") or 0.0),
            "average_cash_weight": float(port.get("average_cash_weight") or 0.0),
            "average_gross_exposure": float(port.get("average_gross_exposure") or 0.0),
            "trade_day_coverage": float(result.get("trade_day_coverage") or 0.0),
            "selected_rows": int(len(selected)),
            **_grade(result),
        },
        "final_judge_blockers": [
            "common_stock_identity_not_validated",
            "post_entry_missing_bar_economics_not_exact",
            "daily_OHLC_same_bar_first_hit_not_exact",
        ],
        "interpretation": (
            "This quick result may reject the candidate early if economically poor. "
            "It cannot promote the model to live use because final Judge blockers remain."
        ),
    }

    out = Path(args.result_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out / "summary.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    selected.to_csv(out / "selected.csv", index=False)
    print("QUICK_CHAMPION=" + json.dumps(report, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
