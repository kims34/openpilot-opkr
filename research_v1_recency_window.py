"""Recency-window challenger for the strongest stable label direction.

Compares the existing expanding training history with one prespecified rolling
window of 200 decision sessions. Both use the fixed-horizon positive-net label,
the same market-context features, five-session purge, and unchanged executable
barrier outcome policy. No window search is performed.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from research_v1_context import CONTEXT_FEATURES, add_context
from research_v1_fixed_horizon_label import add_fixed_horizon_target, purged_predict as expanding_predict
from research_v1_holdaware import evaluate_topk_only
from research_v1_supervised_cache import load_or_build
from run_research_v1 import load_panel


def _pipe():
    prep = ColumnTransformer([
        ("num", Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]), CONTEXT_FEATURES)
    ], remainder="drop")
    model = LogisticRegression(C=1.0, penalty="l2", solver="liblinear", max_iter=2000, random_state=20260928)
    return Pipeline([("prep", prep), ("model", model)])


def rolling_predict(frame: pd.DataFrame, train_days=200, test_days=40, purge_days=5):
    dates = sorted(pd.Timestamp(x) for x in frame["decision_date"].drop_duplicates())
    out = []
    start = train_days + purge_days
    while start < len(dates):
        test_block = dates[start:start + test_days]
        if not test_block:
            break
        train_end = start - purge_days
        train_start = max(0, train_end - train_days)
        train_dates = dates[train_start:train_end]
        train = frame[frame["decision_date"].isin(train_dates)].copy()
        train = train[train["fh_positive_net"].notna()].copy()
        test = frame[frame["decision_date"].isin(test_block)].copy()
        if train.empty or test.empty:
            start += test_days
            continue
        y = train["fh_positive_net"].astype(int)
        if y.nunique() < 2:
            start += test_days
            continue
        model = _pipe()
        model.fit(train[CONTEXT_FEATURES], y)
        test["score"] = model.predict_proba(test[CONTEXT_FEATURES])[:, 1]
        test["model"] = "logistic_fixed_horizon_rolling200"
        test["train_window_start"] = train_dates[0]
        test["train_window_end"] = train_dates[-1]
        out.append(test[[
            "decision_date", "symbol", "label_positive_net", "net_return",
            "label_available", "entry_fillable", "ambiguous_same_bar",
            "post_entry_missing_future", "score", "model",
            "train_window_start", "train_window_end",
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
        "expected_shortfall_95": float(ex.get("trade_expected_shortfall_95") or 0.0),
        "cluster_low": float(ex.get("cluster_bootstrap_95_low") or 0.0),
        "cluster_high": float(ex.get("cluster_bootstrap_95_high") or 0.0),
        "total_return": float(port.get("total_return") or 0.0),
        "max_drawdown": float(port.get("max_drawdown") or 0.0),
    }


def yearly(selected: pd.DataFrame):
    if selected.empty:
        return []
    x = selected.copy()
    x["year"] = pd.to_datetime(x["decision_date"]).dt.year
    rows = []
    for y, g in x.groupby("year"):
        rows.append({
            "year": int(y),
            "trades": int(len(g)),
            "mean_realized_net_return": float(g["net_return"].mean()),
        })
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cache", default="research_data/marcap_kospi_pit")
    ap.add_argument("--supervised-cache", default="research_data/pit_supervised_v1")
    ap.add_argument("--result-dir", default="research_results/marcap_pit_recency")
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

    exp_pred = expanding_predict(
        z, target_col="fh_positive_net", kind="logistic",
        train_days=args.train_days, test_days=args.test_days, purge_days=args.horizon,
    )
    exp_result, exp_sel, _ = evaluate_topk_only(exp_pred, record_map, raw, args.horizon, args.top_k)

    roll_pred = rolling_predict(z, args.train_days, args.test_days, args.horizon)
    roll_result, roll_sel, _ = evaluate_topk_only(roll_pred, record_map, raw, args.horizon, args.top_k)

    e = view(exp_result)
    r = view(roll_result)
    report = {
        "evaluation_stage": "PIT_PRELIMINARY_PURGED_RECENCY_WINDOW_CHALLENGER",
        "label": "next_open_to_Dplus5_positive_cost_adjusted_return",
        "features": "market_context",
        "purge_days": args.horizon,
        "window_search": False,
        "rolling_window_sessions": args.train_days,
        "execution_outcome_policy_unchanged": True,
        "supervised_cache": meta,
        "label_diagnostics": diag,
        "expanding": e,
        "rolling_200": r,
        "delta_rolling_minus_expanding": {k: r[k] - e[k] for k in r if k in e and isinstance(r[k], (int, float))},
        "expanding_yearly_selected": yearly(exp_sel),
        "rolling_yearly_selected": yearly(roll_sel),
        "interpretation": (
            "Prefer rolling training only if it improves post-cost OOS economics and recent-year stability without materially worsening tail risk. "
            "This is a single prespecified recency test, not window optimization."
        ),
    }
    out = Path(args.result_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out / "summary.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    exp_sel.to_csv(out / "expanding_selected.csv", index=False)
    roll_sel.to_csv(out / "rolling200_selected.csv", index=False)
    print("RECENCY_WINDOW=" + json.dumps(report, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
