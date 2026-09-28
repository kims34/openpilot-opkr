"""Bound the impact of daily-OHLC target/stop ordering ambiguity.

The primary policy remains conservative stop-first.  This diagnostic trains the
current market-context logistic model only on the primary stop-first labels, then
replays the *same purged prediction scores and decision-time ranks* against two
outcome maps:

1. stop-first (primary executable-conservative bound)
2. target-first (optimistic upper-bound sensitivity)

Because model scores are held fixed, the delta isolates barrier-order ambiguity
rather than letting optimistic labels also alter model training.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from research_v1_context import add_context
from research_v1_holdaware import evaluate_topk_only
from research_v1_pit_labels import make_pit_supervised
from research_v1_pit_run import _grade
from research_v1_pit_run_purged import _walk_forward_pit
from run_research_v1 import load_panel


def _row(name: str, candidate: dict) -> dict:
    ex = candidate.get("executable_set", {})
    port = candidate.get("portfolio", {})
    return {
        "name": name,
        "trades": int(ex.get("trades") or 0),
        "mean_gross_return": float(ex.get("mean_gross_return") or 0.0),
        "mean_cost_return": float(ex.get("mean_cost_return") or 0.0),
        "mean_net_return": float(ex.get("mean_net_return") or 0.0),
        "profit_factor": float(ex.get("profit_factor") or 0.0),
        "cluster_low": float(ex.get("cluster_bootstrap_95_low") or 0.0),
        "cluster_high": float(ex.get("cluster_bootstrap_95_high") or 0.0),
        "total_return": float(port.get("total_return") or 0.0),
        "max_drawdown": float(port.get("max_drawdown") or 0.0),
        **_grade(candidate),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cache", default="research_data/marcap_kospi_pit")
    ap.add_argument("--result-dir", default="research_results/marcap_pit_ambiguity")
    ap.add_argument("--horizon", type=int, default=5)
    ap.add_argument("--top-k", type=int, default=3)
    ap.add_argument("--target", type=float, default=0.04)
    ap.add_argument("--stop", type=float, default=-0.025)
    ap.add_argument("--participation", type=float, default=0.0005)
    ap.add_argument("--train-days", type=int, default=200)
    ap.add_argument("--test-days", type=int, default=40)
    args = ap.parse_args()

    raw = load_panel(Path(args.cache))

    primary_frame, primary_map, primary_diag = make_pit_supervised(
        raw,
        horizon=args.horizon,
        target_return=args.target,
        stop_return=args.stop,
        participation=args.participation,
        ambiguity_resolution_policy="stop_first",
    )
    optimistic_frame, optimistic_map, optimistic_diag = make_pit_supervised(
        raw,
        horizon=args.horizon,
        target_return=args.target,
        stop_return=args.stop,
        participation=args.participation,
        ambiguity_resolution_policy="target_first",
    )

    primary_keys = primary_frame[["decision_date", "symbol"]].reset_index(drop=True)
    optimistic_keys = optimistic_frame[["decision_date", "symbol"]].reset_index(drop=True)
    if not primary_keys.equals(optimistic_keys):
        raise RuntimeError("ambiguity sensitivity changed the decision universe")

    frame = primary_frame[primary_frame["adv20_rank"] >= 0.20].copy().reset_index(drop=True)
    context = add_context(frame)
    pred = _walk_forward_pit(
        context,
        "logistic_context",
        args.train_days,
        args.test_days,
        context=True,
        purge_days=args.horizon,
    )

    primary_result, primary_selected, _ = evaluate_topk_only(
        pred, primary_map, raw, args.horizon, args.top_k
    )
    optimistic_result, optimistic_selected, _ = evaluate_topk_only(
        pred, optimistic_map, raw, args.horizon, args.top_k
    )

    primary = _row("stop_first_primary", primary_result)
    optimistic = _row("target_first_optimistic_same_scores", optimistic_result)

    sel_cols = ["decision_date", "symbol"]
    same_selection = (
        primary_selected[sel_cols].reset_index(drop=True).equals(
            optimistic_selected[sel_cols].reset_index(drop=True)
        )
        if not primary_selected.empty and not optimistic_selected.empty
        else primary_selected.empty == optimistic_selected.empty
    )
    if not same_selection:
        raise RuntimeError("first-hit sensitivity unexpectedly changed selected candidates")

    delta = {
        "mean_net_return": optimistic["mean_net_return"] - primary["mean_net_return"],
        "profit_factor": optimistic["profit_factor"] - primary["profit_factor"],
        "cluster_low": optimistic["cluster_low"] - primary["cluster_low"],
        "total_return": optimistic["total_return"] - primary["total_return"],
        "max_drawdown": optimistic["max_drawdown"] - primary["max_drawdown"],
    }

    report = {
        "evaluation_stage": "PIT_PRELIMINARY_AMBIGUITY_BOUND_PURGED",
        "purge_days": int(args.horizon),
        "scores_and_ranks_held_fixed": True,
        "selected_candidates_identical": same_selection,
        "primary_diagnostics": primary_diag,
        "optimistic_diagnostics": optimistic_diag,
        "primary": primary,
        "optimistic_upper_bound": optimistic,
        "delta_optimistic_minus_primary": delta,
        "interpretation_rule": (
            "target-first is not an executable assumption. If the optimistic upper bound still fails, "
            "intraday first-hit ordering alone cannot rescue this candidate. If it materially changes the result, "
            "intraday/tick first-hit history becomes a high-priority data dependency."
        ),
    }

    out = Path(args.result_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out / "summary.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    pd.DataFrame([primary, optimistic]).to_csv(out / "comparison.csv", index=False)
    print("AMBIGUITY_BOUND=" + json.dumps(report, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
