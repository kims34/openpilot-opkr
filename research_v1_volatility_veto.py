"""Volatility risk-veto sensitivity for the current purged context model.

The predictive model is trained exactly once on the existing universe.  At
admission time only, prespecified high-volatility caps are applied before taking
up to three names.  This isolates a risk veto from alpha-model retraining.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from research_v1_context import add_context
from research_v1_holdaware import evaluate_topk_only
from research_v1_pit_run_purged import _walk_forward_pit
from research_v1_supervised_cache import load_or_build
from run_research_v1 import load_panel

VOL_CAPS = [1.0, 0.90, 0.80]


def view(result):
    ex = result.get("executable_set", {})
    port = result.get("portfolio", {})
    return {
        "trades": int(ex.get("trades") or 0),
        "mean_gross_return": float(ex.get("mean_gross_return") or 0.0),
        "mean_cost_return": float(ex.get("mean_cost_return") or 0.0),
        "mean_net_return": float(ex.get("mean_net_return") or 0.0),
        "profit_factor": float(ex.get("profit_factor") or 0.0),
        "expected_shortfall_95": float(ex.get("trade_expected_shortfall_95") or 0.0),
        "cluster_low": float(ex.get("cluster_bootstrap_95_low") or 0.0),
        "cluster_high": float(ex.get("cluster_bootstrap_95_high") or 0.0),
        "total_return": float(port.get("total_return") or 0.0),
        "max_drawdown": float(port.get("max_drawdown") or 0.0),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cache", default="research_data/marcap_kospi_pit")
    ap.add_argument("--supervised-cache", default="research_data/pit_supervised_v1")
    ap.add_argument("--result-dir", default="research_results/marcap_pit_vol_veto")
    ap.add_argument("--horizon", type=int, default=5)
    ap.add_argument("--top-k", type=int, default=3)
    ap.add_argument("--target", type=float, default=0.04)
    ap.add_argument("--stop", type=float, default=-0.025)
    ap.add_argument("--participation", type=float, default=0.0005)
    ap.add_argument("--train-days", type=int, default=200)
    ap.add_argument("--test-days", type=int, default=40)
    args = ap.parse_args()

    raw = load_panel(Path(args.cache))
    frame, record_map, diag, meta = load_or_build(
        raw, Path(args.supervised_cache),
        horizon=args.horizon, target_return=args.target, stop_return=args.stop,
        participation=args.participation, commission_round_trip_bps=3.0,
    )
    frame = frame[frame["adv20_rank"] >= 0.20].copy().reset_index(drop=True)
    context = add_context(frame)
    pred = _walk_forward_pit(
        context, "logistic_context", args.train_days, args.test_days,
        context=True, purge_days=args.horizon,
    )
    risk = frame[["decision_date", "symbol", "vol20_rank"]].copy()
    pred = pred.merge(risk, on=["decision_date", "symbol"], how="left", validate="one_to_one")

    results = []
    for cap in VOL_CAPS:
        eligible = pred[pred["vol20_rank"] <= cap].copy()
        result, selected, _ = evaluate_topk_only(eligible, record_map, raw, args.horizon, args.top_k)
        results.append({
            "max_vol20_rank_allowed": cap,
            "prediction_rows_after_veto": int(len(eligible)),
            "selected_rows": int(len(selected)),
            **view(result),
        })

    baseline = results[0]
    report = {
        "evaluation_stage": "PIT_PRELIMINARY_PURGED_VOLATILITY_RISK_VETO",
        "model_scores_held_fixed": True,
        "veto_caps_prespecified": VOL_CAPS,
        "hyperparameter_search": False,
        "supervised_cache": meta,
        "label_diagnostics": diag,
        "results": results,
        "delta_vs_no_vol_veto": [
            {
                "max_vol20_rank_allowed": r["max_vol20_rank_allowed"],
                "mean_net_return": r["mean_net_return"] - baseline["mean_net_return"],
                "profit_factor": r["profit_factor"] - baseline["profit_factor"],
                "expected_shortfall_95": r["expected_shortfall_95"] - baseline["expected_shortfall_95"],
                "max_drawdown": r["max_drawdown"] - baseline["max_drawdown"],
            }
            for r in results
        ],
        "interpretation": (
            "A volatility cap is useful only if tail risk improves without merely trading too little or destroying net utility. "
            "This is a risk-overlay diagnostic, not a tuned alpha threshold."
        ),
    }
    out = Path(args.result_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out / "summary.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print("VOLATILITY_VETO=" + json.dumps(report, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
