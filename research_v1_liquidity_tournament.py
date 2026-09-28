"""Prespecified liquidity-universe sensitivity for the purged context model.

Tests three coarse gates (top 80%, top 50%, top 20% by same-date trailing ADV20)
without threshold tuning.  The purpose is to determine whether the current lack
of edge is concentrated in less liquid names and whether lower execution cost
comes with better or worse gross signal quality.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from research_v1_context import add_context
from research_v1_holdaware import evaluate_topk_only
from research_v1_pit_run_purged import _walk_forward_pit
from research_v1_supervised_cache import load_or_build
from run_research_v1 import load_panel

GATES = [0.20, 0.50, 0.80]


def view(result):
    ex = result.get("executable_set", {})
    port = result.get("portfolio", {})
    return {
        "trades": int(ex.get("trades") or 0),
        "mean_gross_return": float(ex.get("mean_gross_return") or 0.0),
        "mean_cost_return": float(ex.get("mean_cost_return") or 0.0),
        "mean_net_return": float(ex.get("mean_net_return") or 0.0),
        "profit_factor": float(ex.get("profit_factor") or 0.0),
        "cluster_low": float(ex.get("cluster_bootstrap_95_low") or 0.0),
        "cluster_high": float(ex.get("cluster_bootstrap_95_high") or 0.0),
        "total_return": float(port.get("total_return") or 0.0),
        "max_drawdown": float(port.get("max_drawdown") or 0.0),
        "average_gross_exposure": float(port.get("average_gross_exposure") or 0.0),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cache", default="research_data/marcap_kospi_pit")
    ap.add_argument("--supervised-cache", default="research_data/pit_supervised_v1")
    ap.add_argument("--result-dir", default="research_results/marcap_pit_liquidity")
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

    rows = []
    for gate in GATES:
        f = frame[frame["adv20_rank"] >= gate].copy().reset_index(drop=True)
        context = add_context(f)
        pred = _walk_forward_pit(
            context, "logistic_context", args.train_days, args.test_days,
            context=True, purge_days=args.horizon,
        )
        result, selected, _ = evaluate_topk_only(pred, record_map, raw, args.horizon, args.top_k)
        row = {
            "adv20_rank_min": gate,
            "universe_fraction_approx": 1.0 - gate,
            "decision_rows": int(len(f)),
            "decision_dates": int(f["decision_date"].nunique()),
            "selected_rows": int(len(selected)),
            **view(result),
        }
        rows.append(row)

    baseline = next(x for x in rows if x["adv20_rank_min"] == 0.20)
    report = {
        "evaluation_stage": "PIT_PRELIMINARY_PURGED_LIQUIDITY_GATE_TOURNAMENT",
        "gates_prespecified": GATES,
        "hyperparameter_search": False,
        "supervised_cache": meta,
        "label_diagnostics": diag,
        "results": rows,
        "delta_vs_top80_universe": [
            {
                "adv20_rank_min": r["adv20_rank_min"],
                "mean_gross_return": r["mean_gross_return"] - baseline["mean_gross_return"],
                "mean_cost_return": r["mean_cost_return"] - baseline["mean_cost_return"],
                "mean_net_return": r["mean_net_return"] - baseline["mean_net_return"],
                "profit_factor": r["profit_factor"] - baseline["profit_factor"],
                "max_drawdown": r["max_drawdown"] - baseline["max_drawdown"],
            }
            for r in rows
        ],
        "interpretation": (
            "This is a universe sensitivity, not a choose-the-best threshold search. "
            "A stricter gate is useful only if improvement is economically material and later persists in fresh OOS data."
        ),
    }
    out = Path(args.result_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out / "summary.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print("LIQUIDITY_TOURNAMENT=" + json.dumps(report, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
