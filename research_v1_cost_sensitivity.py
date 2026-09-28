"""Cost sensitivity for the purged PIT market-context candidate.

The model is trained once with historical KOSPI statutory sell taxes plus the
primary 3bp round-trip commission allowance.  Its scores, ranks, selected names,
entry/exit prices, and barrier outcomes are then held fixed while only explicit
cost assumptions are shifted.  This isolates cost drag from signal quality.

The zero-tax-zero-commission case is an intentionally unrealistic upper bound:
if the same selected trades remain unattractive there, legal fee assumptions
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
from research_v1_pit_labels import kospi_statutory_sell_tax_bps, make_pit_supervised
from research_v1_pit_run_purged import _walk_forward_pit
from research_v1_portfolio import simulate_portfolio, summary_dict
from run_research_v1 import load_panel

PRIMARY_COMMISSION_ROUND_TRIP_BPS = 3.0


def _adjust_cost(records, *, commission_bps: float | None = None, remove_all_tax_and_commission: bool = False):
    if remove_all_tax_and_commission and commission_bps is not None:
        raise ValueError("choose commission sensitivity or zero-all-explicit-cost bound, not both")
    out = []
    for rec in records:
        if remove_all_tax_and_commission:
            explicit_primary = kospi_statutory_sell_tax_bps(rec.entry_day) + PRIMARY_COMMISSION_ROUND_TRIP_BPS
            delta = -explicit_primary / 10000.0
        else:
            commission = PRIMARY_COMMISSION_ROUND_TRIP_BPS if commission_bps is None else float(commission_bps)
            delta = (commission - PRIMARY_COMMISSION_ROUND_TRIP_BPS) / 10000.0
        new_cost = max(0.0, float(rec.cost_return) + delta)
        out.append(replace(
            rec,
            cost_return=new_cost,
            net_return=float(rec.gross_return) - new_cost,
        ))
    return out


def _summarize_scenario(raw, records, pred, horizon, *, name: str, commission_bps=None, zero_all=False):
    adjusted = _adjust_cost(
        records,
        commission_bps=commission_bps,
        remove_all_tax_and_commission=zero_all,
    )
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
        "scenario": name,
        "commission_round_trip_bps": None if commission_bps is None else float(commission_bps),
        "statutory_tax_removed": bool(zero_all),
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
        commission_round_trip_bps=PRIMARY_COMMISSION_ROUND_TRIP_BPS,
        participation=args.participation,
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
        _summarize_scenario(
            raw, primary_records, pred, args.horizon,
            name="historical_tax_plus_0bp_commission", commission_bps=0.0,
        ),
        _summarize_scenario(
            raw, primary_records, pred, args.horizon,
            name="historical_tax_plus_3bp_commission_primary", commission_bps=3.0,
        ),
        _summarize_scenario(
            raw, primary_records, pred, args.horizon,
            name="historical_tax_plus_6bp_commission", commission_bps=6.0,
        ),
        _summarize_scenario(
            raw, primary_records, pred, args.horizon,
            name="zero_statutory_tax_and_zero_commission_upper_bound", zero_all=True,
        ),
    ]
    primary = next(x for x in scenarios if x["scenario"].endswith("primary"))
    # Varying round-trip commission by 1bp changes every selected trade's net
    # return by exactly 1bp. This is only a commission breakeven diagnostic;
    # statutory taxes, spread and impact remain intact.
    commission_breakeven = PRIMARY_COMMISSION_ROUND_TRIP_BPS + float(primary["mean_net_return"]) * 10000.0

    report = {
        "evaluation_stage": "PIT_PRELIMINARY_PURGED_COST_SENSITIVITY",
        "scores_ranks_and_trade_paths_held_fixed": True,
        "primary_commission_round_trip_bps": PRIMARY_COMMISSION_ROUND_TRIP_BPS,
        "historical_statutory_tax_schedule_bps": {
            "2021-2022": 23.0,
            "2023": 20.0,
            "2024": 18.0,
            "2025": 15.0,
            "2026": 20.0,
        },
        "primary_cost_structure": "historical statutory sell tax + 3bp round-trip commission + 8bp round-trip spread allowance + volatility/participation impact",
        "label_diagnostics": label_diag,
        "selection_diagnostics": select_diag,
        "selected_executable_rows": int(len(primary_records)),
        "selected_trade_days": int(selected["decision_date"].nunique()) if not selected.empty else 0,
        "scenarios": scenarios,
        "commission_bps_breakeven_for_mean_net_only": float(commission_breakeven),
        "interpretation": (
            "If the zero-tax-zero-commission upper bound remains negative, explicit legal/broker costs cannot rescue the fixed selection; "
            "spread/impact and gross signal quality dominate. A negative commission breakeven likewise means reducing broker commission to zero is insufficient."
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
