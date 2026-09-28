"""Cross-sectional fixed-horizon rank label challenger.

Uses the same next-open -> D+5 cost-adjusted return proxy as the fixed-horizon
label experiment, converts it to same-date percentile rank, and trains a simple
Ridge to predict relative rank.  Final trades are still evaluated by the unchanged
executable target/stop/time outcome map.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import Ridge
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from research_v1_context import CONTEXT_FEATURES, add_context
from research_v1_fixed_horizon_label import add_fixed_horizon_target
from research_v1_holdaware import evaluate_topk_only
from research_v1_pit_run_purged import _walk_forward_pit
from research_v1_supervised_cache import load_or_build
from run_research_v1 import load_panel


def _pipe():
    prep = ColumnTransformer([
        ("num", Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]), CONTEXT_FEATURES)
    ], remainder="drop")
    return Pipeline([("prep", prep), ("model", Ridge(alpha=1.0))])


def purged_rank_predict(frame, train_days=200, test_days=40, purge_days=5):
    dates = sorted(pd.Timestamp(x) for x in frame["decision_date"].drop_duplicates())
    out = []
    start = train_days + purge_days
    while start < len(dates):
        test_block = dates[start:start + test_days]
        if not test_block:
            break
        train_end = start - purge_days
        train_dates = dates[:train_end]
        train = frame[frame["decision_date"].isin(train_dates)].copy()
        train = train[train["fh_rank"].notna()].copy()
        test = frame[frame["decision_date"].isin(test_block)].copy()
        if train.empty or test.empty:
            start += test_days
            continue
        model = _pipe()
        model.fit(train[CONTEXT_FEATURES], train["fh_rank"].astype(float))
        test["score"] = model.predict(test[CONTEXT_FEATURES])
        test["model"] = "ridge_cross_sectional_forward_rank"
        out.append(test[[
            "decision_date", "symbol", "label_positive_net", "net_return",
            "label_available", "entry_fillable", "ambiguous_same_bar",
            "post_entry_missing_future", "score", "model",
        ]])
        start += test_days
    if not out:
        return pd.DataFrame()
    return pd.concat(out, ignore_index=True).sort_values(["decision_date", "score"], ascending=[True, False])


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
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cache", default="research_data/marcap_kospi_pit")
    ap.add_argument("--supervised-cache", default="research_data/pit_supervised_v1")
    ap.add_argument("--result-dir", default="research_results/marcap_pit_cross_sectional")
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
    z = add_fixed_horizon_target(raw, context, record_map, args.horizon)
    z["fh_rank"] = z.groupby("decision_date")["fh_net_return"].rank(pct=True)
    z.loc[~z["fh_label_available"].fillna(False), "fh_rank"] = pd.NA

    baseline_pred = _walk_forward_pit(
        context, "logistic_context", args.train_days, args.test_days,
        context=True, purge_days=args.horizon,
    )
    baseline_result, _, _ = evaluate_topk_only(baseline_pred, record_map, raw, args.horizon, args.top_k)

    rank_pred = purged_rank_predict(z, args.train_days, args.test_days, args.horizon)
    rank_result, selected, _ = evaluate_topk_only(rank_pred, record_map, raw, args.horizon, args.top_k)

    b = view(baseline_result)
    r = view(rank_result)
    report = {
        "evaluation_stage": "PIT_PRELIMINARY_PURGED_CROSS_SECTIONAL_LABEL_CHALLENGER",
        "purge_days": args.horizon,
        "hyperparameter_search": False,
        "learning_target": "same_date_percentile_rank_of_next_open_to_Dplus5_cost_adjusted_return",
        "execution_outcome_policy_unchanged": True,
        "supervised_cache": meta,
        "label_diagnostics": diag,
        "barrier_label_baseline": b,
        "cross_sectional_rank_ridge": r,
        "delta_rank_minus_barrier": {k: r[k] - b[k] for k in r if k in b and isinstance(r[k], (int, float))},
        "training_rank_rows": int(z["fh_rank"].notna().sum()),
        "selected_rows": int(len(selected)),
        "interpretation": (
            "Keep this label family only if relative-rank learning improves executable OOS economics, not merely rank fit."
        ),
    }
    out = Path(args.result_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out / "summary.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    selected.to_csv(out / "selected.csv", index=False)
    print("CROSS_SECTIONAL_LABEL=" + json.dumps(report, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
