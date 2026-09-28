"""Hold-aware, no-forced-backfill comparison for IndexAlert Research v1.

Each day only the model's original top-K names are eligible. If an eligible name
is already held, that slot remains empty; lower ranks are not promoted unless a
separate admission threshold policy explicitly authorizes them elsewhere.
"""
from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path

import pandas as pd

from research_v1_core import date_cluster_bootstrap_mean, summarize
from research_v1_ml import make_supervised, stateful_select_records, walk_forward_predictions
from research_v1_portfolio import simulate_portfolio, summary_dict
from run_research_v1 import load_panel


def evaluate_topk_only(pred, record_map, raw, horizon: int, top_k: int):
    limited = (
        pred.sort_values(["decision_date", "score"], ascending=[True, False])
        .groupby("decision_date", group_keys=False)
        .head(top_k)
        .copy()
    )
    recs, selected, diag = stateful_select_records(limited, record_map, top_k=top_k, threshold=None)
    metrics = summarize(recs)
    point, lo, hi = date_cluster_bootstrap_mean(recs) if recs else (0.0, 0.0, 0.0)
    eval_start = pd.Timestamp(pred["decision_date"].min()).date()
    eval_end = max(
        pd.Timestamp(pred["decision_date"].max()).date(),
        max((r.exit_day for r in recs), default=eval_start),
    )
    path, port = simulate_portfolio(
        raw, recs, horizon=horizon, initial_equity=1.0,
        daily_cohort_fraction=1.0 / horizon, suppress_duplicate_symbols=False,
        evaluation_start=eval_start, evaluation_end=eval_end,
    )
    return {
        "executable_set": {
            **asdict(metrics),
            "cluster_bootstrap_mean_net_return": point,
            "cluster_bootstrap_95_low": lo,
            "cluster_bootstrap_95_high": hi,
        },
        **diag,
        "portfolio": summary_dict(port),
        "selected_executable_rows": int(len(recs)),
        "test_dates": int(pred["decision_date"].nunique()),
        "trade_days": int(selected["decision_date"].nunique()) if not selected.empty else 0,
        "trade_day_coverage": float(selected["decision_date"].nunique() / pred["decision_date"].nunique()) if not selected.empty else 0.0,
        "policy": "original_top_k_only__held_names_leave_empty_slots",
    }, selected, path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cache", default="research_data/public_smoke_daily")
    ap.add_argument("--result-dir", default="research_results/public_smoke_holdaware")
    ap.add_argument("--horizon", type=int, default=5)
    ap.add_argument("--top-k", type=int, default=3)
    ap.add_argument("--target", type=float, default=0.04)
    ap.add_argument("--stop", type=float, default=-0.025)
    ap.add_argument("--participation", type=float, default=0.0005)
    ap.add_argument("--train-days", type=int, default=200)
    ap.add_argument("--test-days", type=int, default=40)
    args = ap.parse_args()

    raw = load_panel(Path(args.cache))
    pit = bool(raw.get("point_in_time_universe", pd.Series([False])).fillna(False).astype(bool).all())
    frame, record_map, diag = make_supervised(
        raw, horizon=args.horizon, target_return=args.target, stop_return=args.stop,
        participation=args.participation,
    )
    out_dir = Path(args.result_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    report = {
        "result_class": "JUDGE" if pit else "SMOKE_NONPIT",
        "judge_eligible": pit,
        "diagnostics": diag,
        "models": {},
    }
    for kind in ["logistic_l2", "logistic_elasticnet"]:
        pred = walk_forward_predictions(frame, kind, args.train_days, args.test_days)
        result, selected, path = evaluate_topk_only(pred, record_map, raw, args.horizon, args.top_k)
        report["models"][kind] = result
        selected.to_csv(out_dir / f"{kind}_selected.csv", index=False)
        path.to_csv(out_dir / f"{kind}_portfolio.csv", index=False)
    if not pit:
        report["warning"] = "Non-PIT smoke result only; policy comparison, not profitability evidence."
    (out_dir / "summary.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
