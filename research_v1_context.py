"""Simple market-context challenger for IndexAlert Research v1.

Adds only contemporaneously-known cross-sectional market state derived from the
same decision-date panel: median returns, breadth, dispersion and stock residual
returns. No model-complexity increase and no hyperparameter search.
"""
from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from research_v1_core import date_cluster_bootstrap_mean, summarize
from research_v1_ml import FEATURES, make_supervised, stateful_select_records
from research_v1_portfolio import simulate_portfolio, summary_dict
from run_research_v1 import load_panel

CONTEXT_FEATURES = FEATURES + [
    "market_ret1_median", "market_ret5_median", "market_ret20_median",
    "breadth1", "breadth5", "dispersion20",
    "resid_ret1", "resid_ret5", "resid_ret20",
]


def add_context(frame: pd.DataFrame) -> pd.DataFrame:
    x = frame.copy()
    g = x.groupby("decision_date")
    x["market_ret1_median"] = g["ret1"].transform("median")
    x["market_ret5_median"] = g["ret5"].transform("median")
    x["market_ret20_median"] = g["ret20"].transform("median")
    x["breadth1"] = g["ret1"].transform(lambda s: float((s > 0).mean()))
    x["breadth5"] = g["ret5"].transform(lambda s: float((s > 0).mean()))
    x["dispersion20"] = g["ret20"].transform(lambda s: float(s.std(ddof=0)))
    x["resid_ret1"] = x["ret1"] - x["market_ret1_median"]
    x["resid_ret5"] = x["ret5"] - x["market_ret5_median"]
    x["resid_ret20"] = x["ret20"] - x["market_ret20_median"]
    return x


def _pipe(kind: str):
    prep = ColumnTransformer([
        ("num", Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]), CONTEXT_FEATURES)
    ], remainder="drop")
    if kind == "logistic_context":
        model = LogisticRegression(C=1.0, penalty="l2", solver="liblinear", max_iter=2000, random_state=20260928)
    elif kind == "ridge_context":
        model = Ridge(alpha=1.0)
    else:
        raise ValueError(kind)
    return Pipeline([("prep", prep), ("model", model)])


def predict_walk_forward(frame: pd.DataFrame, kind: str, train_days=200, test_days=40):
    dates = sorted(pd.Timestamp(x) for x in frame["decision_date"].drop_duplicates())
    out = []
    start = train_days
    while start < len(dates):
        test_block = dates[start:start + test_days]
        if not test_block:
            break
        train_block = dates[:start]
        train = frame[frame["decision_date"].isin(train_block)]
        test = frame[frame["decision_date"].isin(test_block)].copy()
        if train.empty or test.empty:
            start += test_days
            continue
        pipe = _pipe(kind)
        if kind == "logistic_context":
            if train["label_positive_net"].nunique() < 2:
                start += test_days
                continue
            pipe.fit(train[CONTEXT_FEATURES], train["label_positive_net"])
            test["score"] = pipe.predict_proba(test[CONTEXT_FEATURES])[:, 1]
        else:
            pipe.fit(train[CONTEXT_FEATURES], train["net_return"])
            test["score"] = pipe.predict(test[CONTEXT_FEATURES])
        test["model"] = kind
        out.append(test[["decision_date", "symbol", "label_positive_net", "net_return", "ambiguous_same_bar", "score", "model"]])
        start += test_days
    if not out:
        return pd.DataFrame()
    return pd.concat(out, ignore_index=True).sort_values(["decision_date", "score"], ascending=[True, False])


def evaluate(pred, record_map, raw, horizon, top_k, threshold=None, original_topk_only=True):
    if pred.empty:
        return {}, pd.DataFrame(), pd.DataFrame()
    use = pred
    if original_topk_only:
        use = (
            pred.sort_values(["decision_date", "score"], ascending=[True, False])
            .groupby("decision_date", group_keys=False)
            .head(top_k)
            .copy()
        )
    recs, selected, diag = stateful_select_records(use, record_map, top_k=top_k, threshold=threshold)
    m = summarize(recs)
    point, lo, hi = date_cluster_bootstrap_mean(recs) if recs else (0.0, 0.0, 0.0)
    eval_start = pd.Timestamp(pred["decision_date"].min()).date()
    eval_end = max(pd.Timestamp(pred["decision_date"].max()).date(), max((r.exit_day for r in recs), default=eval_start))
    path, port = simulate_portfolio(
        raw, recs, horizon=horizon, initial_equity=1.0,
        daily_cohort_fraction=1.0 / horizon, suppress_duplicate_symbols=False,
        evaluation_start=eval_start, evaluation_end=eval_end,
    )
    return {
        "executable_set": {
            **asdict(m),
            "cluster_bootstrap_mean_net_return": point,
            "cluster_bootstrap_95_low": lo,
            "cluster_bootstrap_95_high": hi,
        },
        **diag,
        "portfolio": summary_dict(port),
        "test_dates": int(pred["decision_date"].nunique()),
        "trade_days": int(selected["decision_date"].nunique()) if not selected.empty else 0,
        "trade_day_coverage": float(selected["decision_date"].nunique() / pred["decision_date"].nunique()) if not selected.empty else 0.0,
    }, selected, path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cache", default="research_data/public_smoke_daily")
    ap.add_argument("--result-dir", default="research_results/public_smoke_context")
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
    base, record_map, diag = make_supervised(raw, horizon=args.horizon, target_return=args.target, stop_return=args.stop, participation=args.participation)
    frame = add_context(base)
    out = Path(args.result_dir)
    out.mkdir(parents=True, exist_ok=True)

    report = {
        "result_class": "JUDGE" if pit else "SMOKE_NONPIT",
        "judge_eligible": pit,
        "feature_policy": "simple_market_context_no_hyperparameter_search",
        "features": CONTEXT_FEATURES,
        "diagnostics": diag,
        "models": {},
    }

    log_pred = predict_walk_forward(frame, "logistic_context", args.train_days, args.test_days)
    r, sel, path = evaluate(log_pred, record_map, raw, args.horizon, args.top_k, threshold=None, original_topk_only=True)
    r["objective"] = "probability_positive_net_return"
    r["admission_rule"] = "original_top3_only__held_names_leave_empty_slots"
    report["models"]["logistic_context_top3_only"] = r
    sel.to_csv(out / "logistic_context_selected.csv", index=False)
    path.to_csv(out / "logistic_context_portfolio.csv", index=False)

    ridge_pred = predict_walk_forward(frame, "ridge_context", args.train_days, args.test_days)
    r, sel, path = evaluate(ridge_pred, record_map, raw, args.horizon, args.top_k, threshold=0.0, original_topk_only=False)
    r["objective"] = "direct_cost_adjusted_net_return"
    r["admission_rule"] = "predicted_net_return_gt_0__0_to_3"
    report["models"]["ridge_context_positive_only"] = r
    sel.to_csv(out / "ridge_context_selected.csv", index=False)
    path.to_csv(out / "ridge_context_portfolio.csv", index=False)

    if not pit:
        report["warning"] = "Non-PIT smoke result only; context feature diagnostic, not profitability evidence."
    (out / "summary.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
