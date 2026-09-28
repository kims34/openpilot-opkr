"""PIT-safe daily path-context challenger.

Adds only information fully known at the decision close and directly relevant to
a next-session-open entry: overnight gap into the current session, current
intraday return, high-low range, close location in the daily range, and current
trading-value surprise versus the prior 20 sessions.  No hyperparameter search.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from research_v1_context import CONTEXT_FEATURES, add_context
from research_v1_holdaware import evaluate_topk_only
from research_v1_pit_labels import make_pit_supervised
from research_v1_pit_run_purged import _walk_forward_pit
from run_research_v1 import load_panel

PATH_FEATURES = [
    "gap1",
    "intraday_ret1",
    "range1",
    "close_location1",
    "value_surprise20_log",
    "gap1_rank",
    "intraday_ret1_rank",
    "range1_rank",
    "value_surprise20_rank",
]
PATH_CONTEXT_FEATURES = CONTEXT_FEATURES + PATH_FEATURES


def add_path_features(raw: pd.DataFrame, supervised: pd.DataFrame) -> pd.DataFrame:
    x = raw.copy().sort_values(["symbol", "decision_date"]).reset_index(drop=True)
    g = x.groupby("symbol", sort=False)
    x["prev_close"] = g["close"].shift(1)
    x["prior_value20"] = g["value"].transform(lambda s: s.shift(1).rolling(20, min_periods=20).median())
    x["gap1"] = x["open"] / x["prev_close"] - 1.0
    x["intraday_ret1"] = x["close"] / x["open"] - 1.0
    x["range1"] = x["high"] / x["low"] - 1.0
    denom = (x["high"] - x["low"]).astype(float)
    x["close_location1"] = np.where(denom > 0, (x["close"] - x["low"]) / denom, 0.5)
    ratio = (x["value"].astype(float) + 1.0) / (x["prior_value20"].astype(float) + 1.0)
    x["value_surprise20_log"] = np.log(ratio.clip(lower=1e-8))

    for col in ["gap1", "intraday_ret1", "range1", "value_surprise20_log"]:
        x[f"{col.replace('value_surprise20_log','value_surprise20')}_rank"] = x.groupby("decision_date")[col].rank(pct=True)

    keep = ["decision_date", "symbol"] + PATH_FEATURES
    z = supervised.merge(x[keep], on=["decision_date", "symbol"], how="left", validate="one_to_one")
    return z


def _pipe(features):
    prep = ColumnTransformer([
        ("num", Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]), features)
    ], remainder="drop")
    model = LogisticRegression(C=1.0, penalty="l2", solver="liblinear", max_iter=2000, random_state=20260928)
    return Pipeline([("prep", prep), ("model", model)])


def purged_predict(frame: pd.DataFrame, features, train_days=200, test_days=40, purge_days=5, model_name="path_context"):
    dates = sorted(pd.Timestamp(x) for x in frame["decision_date"].drop_duplicates())
    out = []
    start = train_days + purge_days
    while start < len(dates):
        test_block = dates[start:start + test_days]
        if not test_block:
            break
        train_end = start - purge_days
        train_block = dates[:train_end]
        train = frame[frame["decision_date"].isin(train_block)]
        train = train[train["label_available"].fillna(False).astype(bool)].copy()
        test = frame[frame["decision_date"].isin(test_block)].copy()
        if train.empty or test.empty or train["label_positive_net"].nunique() < 2:
            start += test_days
            continue
        pipe = _pipe(features)
        pipe.fit(train[features], train["label_positive_net"].astype(int))
        test["score"] = pipe.predict_proba(test[features])[:, 1]
        test["model"] = model_name
        out.append(test[[
            "decision_date", "symbol", "label_positive_net", "net_return",
            "label_available", "entry_fillable", "ambiguous_same_bar",
            "post_entry_missing_future", "score", "model",
        ]])
        start += test_days
    if not out:
        return pd.DataFrame()
    return pd.concat(out, ignore_index=True).sort_values(["decision_date", "score"], ascending=[True, False])


def metric_view(result: dict) -> dict:
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
    ap.add_argument("--result-dir", default="research_results/marcap_pit_path_context")
    ap.add_argument("--horizon", type=int, default=5)
    ap.add_argument("--top-k", type=int, default=3)
    ap.add_argument("--target", type=float, default=0.04)
    ap.add_argument("--stop", type=float, default=-0.025)
    ap.add_argument("--participation", type=float, default=0.0005)
    ap.add_argument("--train-days", type=int, default=200)
    ap.add_argument("--test-days", type=int, default=40)
    args = ap.parse_args()

    raw = load_panel(Path(args.cache))
    frame, record_map, diag = make_pit_supervised(
        raw,
        horizon=args.horizon,
        target_return=args.target,
        stop_return=args.stop,
        participation=args.participation,
    )
    frame = frame[frame["adv20_rank"] >= 0.20].copy().reset_index(drop=True)
    base_context = add_context(frame)
    enriched = add_path_features(raw, base_context)

    base_pred = _walk_forward_pit(
        base_context, "logistic_context", args.train_days, args.test_days,
        context=True, purge_days=args.horizon,
    )
    base_result, _, _ = evaluate_topk_only(base_pred, record_map, raw, args.horizon, args.top_k)

    path_pred = purged_predict(
        enriched, PATH_CONTEXT_FEATURES,
        train_days=args.train_days, test_days=args.test_days,
        purge_days=args.horizon, model_name="logistic_path_context",
    )
    path_result, selected, _ = evaluate_topk_only(path_pred, record_map, raw, args.horizon, args.top_k)

    b = metric_view(base_result)
    p = metric_view(path_result)
    delta = {k: p[k] - b[k] for k in p if isinstance(p[k], (int, float)) and k in b}
    report = {
        "evaluation_stage": "PIT_PRELIMINARY_PURGED_PATH_CONTEXT_CHALLENGER",
        "purge_days": args.horizon,
        "hyperparameter_search": False,
        "path_features": PATH_FEATURES,
        "label_diagnostics": diag,
        "baseline_logistic_context": b,
        "path_context": p,
        "delta_path_minus_baseline": delta,
        "selected_rows": int(len(selected)),
        "interpretation": (
            "Adopt path features only if cost-adjusted OOS metrics improve materially without worsening tail risk. "
            "This is a single prespecified challenger, not a feature search."
        ),
    }
    out = Path(args.result_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out / "summary.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    selected.to_csv(out / "selected.csv", index=False)
    print("PATH_CONTEXT=" + json.dumps(report, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
