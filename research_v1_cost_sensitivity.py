"""Cost sensitivity for the purged PIT market-context candidate.

The model is trained once with the primary 23bp tax+commission assumption.  Its
scores, ranks, selected names, entry/exit prices, and barrier outcomes are then
held fixed while only `tax_commission_bps` is shifted.  This isolates cost drag
from signal quality.

The 0bp case is an intentionally unrealistic upper bound: if the same selected
trades remain unattractive even with zero tax+commission, legal fee assumptions
cannot explain the lack of edge.
"""
from __future__ import annotations

import argparse
import json
from dataclasses import asdict, replace
from pathlib import Path

import pandas as pd

from research_v1_context import add_context
from research_v1_core import date_cluster_bootstrap_mean, summarize
from research_v1_ml import stateful_select_records
from research_v1_pit_labels import make_pit_supervised
from research_v1_pit_run_purged import _walk_forward_pit
from research_v1_portfolio import simulate_portfolio, summary_dict
from run_research_v1 import load_panel

PRIMARY_TAX_COMMISSION_BPS = 23.0


def _adjust_cost(records, tax_commission_bps: float):
    delta = (float(tax_commission_bps) - PRIMARY_TAX_COMMISSION_BPS) / 10000.0
    out = []
    for rec in records:
        new_cost = float(rec.cost_return) + delta
        out.append(replace(
            rec,
            cost_return=new_cost,
            net_return=float(rec.gross_return) - new_cost,
        ))
    return out


def _summarize_scenario(raw, records, pred, horizon, bps):
    adjusted = _adjust_cost(records, bps)
    m = summarize(adjusted)
    point, lo, hi = date_cluster_bootstrap_mean(adjusted) if adjusted else (0.0, 0.0, 0.0)
    eval_start = pd.Timestamp(pred["decision_date"].min()).date()
    eval_end = max(
        pd.Timestamp(pred["decision_date"].max()).date(),
        max((r.exit_day for r in adjusted), default=eval_start),
    )
    _, port = simulate_portfolio(
        raw,
        adjusted,
        horizon=horizon,
        initial_equity=1.0,
        daily_cohort_fraction=1.0 / horizon,
        suppress_duplicate_symbols=False,
        evaluation_start=eval_start,
        evaluation_end=eval_end,
    )
    return {
        "tax_commission_bps": float(bps),
        **asdict(m),
        "cluster_bootstrap_mean_net_return": point,
        "cluster_bootstrap_95_low": lo,
        "cluster_bootstrap_95_high": hi,
        "portfolio": summary_dict(port),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cache", default="research_data/marcap_kospi_pit")
    ap.add_argument("--result-dir", default="research_results/marcap_pit_cost_sensitivity")
    ap.add_argument("--horizon", type=int, default=5)
    ap.add_argument("--top-k", type=int, default=3)
    ap.add_argument("--target", type=float, default=0.04)
    ap.add_argument("--stop", type=float, default=-0.025)
    ap.add_argument("--participation", type=float, default=0.0005)
    ap.add_argument("--train-days", type=int, default=200)
    ap.add_argument("--test-days", type=int, default=40)
    args = ap.parse_args()

    raw = load_panel(Path(args.cache))
    frame, record_map, label_diag = make_pit_supervised(
        raw,
        horizon=args.horizon,
        target_return=args.target,
        stop_return=args.stop,
        participation=args.participation,
        # primary make_pit_supervised default is 23bp tax+commission
    )
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

    limited = (
        pred.sort_values(["decision_date", "score"], ascending=[True, False])
        .groupby("decision_date", group_keys=False)
        .head(args.top_k)
        .copy()
    )
    primary_records, selected, select_diag = stateful_select_records(
        limited,
        record_map,
        top_k=args.top_k,
        threshold=None,
    )

    scenarios = [
        _summarize_scenario(raw, primary_records, pred, args.horizon, bps)
        for bps in [0.0, 20.0, 23.0, 26.0]
    ]
    primary = next(x for x in scenarios if x["tax_commission_bps"] == PRIMARY_TAX_COMMISSION_BPS)
    breakeven = PRIMARY_TAX_COMMISSION_BPS + float(primary["mean_net_return"]) * 10000.0

    report = {
        "evaluation_stage": "PIT_PRELIMINARY_PURGED_COST_SENSITIVITY",
        "scores_ranks_and_trade_paths_held_fixed": True,
        "primary_tax_commission_bps": PRIMARY_TAX_COMMISSION_BPS,
        "primary_cost_structure": "23bp tax+commission + 8bp round-trip quoted half-spread allowance + volatility/participation impact",
        "legal_context_2026_kospi": {
            "securities_transaction_tax_bps_sell_side": 5.0,
            "rural_special_tax_bps_sell_side": 15.0,
            "combined_statutory_sell_tax_bps": 20.0,
            "note": "Broker commission is account-specific; the primary 23bp combines statutory tax with a small commission allowance.",
        },
        "label_diagnostics": label_diag,
        "selection_diagnostics": select_diag,
        "selected_executable_rows": int(len(primary_records)),
        "selected_trade_days": int(selected["decision_date"].nunique()) if not selected.empty else 0,
        "scenarios": scenarios,
        "tax_commission_bps_breakeven_for_mean_net_only": float(breakeven),
        "interpretation": (
            "A negative breakeven tax+commission bps means the fixed selected trades would still have negative mean net return "
            "even if tax+commission were zero; spread/impact plus gross signal quality then dominate the failure. "
            "The 0bp scenario is an upper-bound diagnostic, not a realistic trading assumption."
        ),
    }

    out = Path(args.result_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out / "summary.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    pd.DataFrame([
        {k: v for k, v in s.items() if k != "portfolio"}
        | {f"portfolio_{k}": v for k, v in s["portfolio"].items()}
        for s in scenarios
    ]).to_csv(out / "comparison.csv", index=False)
    print("COST_SENSITIVITY=" + json.dumps(report, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
