"""Fast repeatable evaluation of the current best simple PIT candidate.

This is intentionally narrower than the full tournament.  It builds PIT labels
once, trains only the purged market-context logistic model, replays the original
top-3 without backfill, and evaluates cost sensitivity on the exact same selected
trades.  It is for rapid iteration after data/policy fixes; full tournament
results remain the promotion authority.
"""
from __future__ import annotations

import argparse
import json
from dataclasses import asdict, replace
from pathlib import Path

import pandas as pd

from research_v1_context import add_context
from research_v1_core import date_cluster_bootstrap_mean, summarize
from research_v1_holdaware import evaluate_topk_only
from research_v1_pit_labels import kospi_statutory_sell_tax_bps, make_pit_supervised
from research_v1_pit_run_purged import _walk_forward_pit
from research_v1_portfolio import simulate_portfolio, summary_dict
from run_research_v1 import load_panel

PRIMARY_COMMISSION_BPS = 3.0


def _selected_records(selected: pd.DataFrame, record_map: dict):
    out = []
    for row in selected.itertuples(index=False):
        key = (pd.Timestamp(row.decision_date).date(), str(row.symbol))
        base = record_map.get(key)
        if base is None:
            continue
        out.append(replace(base, score=float(row.score)))
    return out


def _adjust_explicit_cost(records, *, commission_bps: float | None = None, zero_all: bool = False):
    adjusted = []
    for rec in records:
        if zero_all:
            primary_explicit = kospi_statutory_sell_tax_bps(rec.entry_day) + PRIMARY_COMMISSION_BPS
            delta = -primary_explicit / 10000.0
        else:
            c = PRIMARY_COMMISSION_BPS if commission_bps is None else float(commission_bps)
            delta = (c - PRIMARY_COMMISSION_BPS) / 10000.0
        new_cost = max(0.0, float(rec.cost_return) + delta)
        adjusted.append(replace(rec, cost_return=new_cost, net_return=float(rec.gross_return) - new_cost))
    return adjusted


def _scenario(raw, pred, records, horizon: int, name: str, *, commission_bps=None, zero_all=False):
    recs = _adjust_explicit_cost(records, commission_bps=commission_bps, zero_all=zero_all)
    m = summarize(recs)
    point, lo, hi = date_cluster_bootstrap_mean(recs) if recs else (0.0, 0.0, 0.0)
    if pred.empty:
        port = None
    else:
        eval_start = pd.Timestamp(pred["decision_date"].min()).date()
        eval_end = max(pd.Timestamp(pred["decision_date"].max()).date(), max((r.exit_day for r in recs), default=eval_start))
        _, p = simulate_portfolio(
            raw, recs, horizon=horizon, initial_equity=1.0,
            daily_cohort_fraction=1.0 / horizon, suppress_duplicate_symbols=False,
            evaluation_start=eval_start, evaluation_end=eval_end,
        )
        port = summary_dict(p)
    return {
        "scenario": name,
        "commission_round_trip_bps": commission_bps,
        "zero_statutory_tax_and_commission": bool(zero_all),
        **asdict(m),
        "cluster_bootstrap_mean_net_return": point,
        "cluster_bootstrap_95_low": lo,
        "cluster_bootstrap_95_high": hi,
        "portfolio": port,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cache", default="research_data/marcap_kospi_pit")
    ap.add_argument("--result-dir", default="research_results/marcap_pit_fast")
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
        commission_round_trip_bps=PRIMARY_COMMISSION_BPS,
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
    candidate, selected, _ = evaluate_topk_only(pred, record_map, raw, args.horizon, args.top_k)
    records = _selected_records(selected, record_map)

    scenarios = [
        _scenario(raw, pred, records, args.horizon, "historical_tax_plus_0bp_commission", commission_bps=0.0),
        _scenario(raw, pred, records, args.horizon, "historical_tax_plus_3bp_commission_primary", commission_bps=3.0),
        _scenario(raw, pred, records, args.horizon, "historical_tax_plus_6bp_commission", commission_bps=6.0),
        _scenario(raw, pred, records, args.horizon, "zero_tax_zero_commission_upper_bound", zero_all=True),
    ]
    primary = scenarios[1]
    zero_upper = scenarios[-1]
    if primary["mean_net_return"] > 0 and primary["profit_factor"] > 1 and primary["cluster_bootstrap_95_low"] > 0:
        verdict = "PRELIMINARY_EDGE_PRESENT"
    elif zero_upper["mean_net_return"] <= 0:
        verdict = "NO_GROSS_EDGE_EVEN_WITH_ZERO_EXPLICIT_COST"
    else:
        verdict = "SIGNAL_NOT_ROBUST_AFTER_REALISTIC_COST"

    report = {
        "evaluation_stage": "PIT_PRELIMINARY_PURGED_FAST",
        "promotion_authority": False,
        "purpose": "rapid diagnostic of current best simple candidate after data/policy fixes",
        "purge_days": args.horizon,
        "model": "logistic_context_top3_only",
        "admission_rule": "original_top3_only__held_or_unfillable_names_leave_empty_slots",
        "label_diagnostics": label_diag,
        "prediction_rows": int(len(pred)),
        "selected_rows": int(len(selected)),
        "selected_records": int(len(records)),
        "candidate_primary": candidate,
        "cost_scenarios": scenarios,
        "verdict": verdict,
    }

    out = Path(args.result_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out / "summary.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    selected.to_csv(out / "selected.csv", index=False)
    pd.DataFrame([{k: v for k, v in s.items() if k != "portfolio"} for s in scenarios]).to_csv(out / "cost_scenarios.csv", index=False)
    print("FAST_PURGED=" + json.dumps(report, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
