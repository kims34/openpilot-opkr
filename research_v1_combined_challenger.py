"""Combined prespecified challenger after two independent partial improvements.

Combines:
1) the PIT-safe daily path features that improved gross edge, and
2) the fixed-horizon positive-net learning target that improved stability.

Execution/evaluation remains the unchanged target/stop/time economic outcome map.
No hyperparameter search is introduced.
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

from research_v1_context import add_context
from research_v1_fixed_horizon_label import add_fixed_horizon_target
from research_v1_holdaware import evaluate_topk_only
from research_v1_path_context import PATH_CONTEXT_FEATURES, add_path_features
from research_v1_pit_run_purged import _walk_forward_pit
from research_v1_supervised_cache import load_or_build
from run_research_v1 import load_panel


def _pipe():
    prep = ColumnTransformer([
        ("num", Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]), PATH_CONTEXT_FEATURES)
    ], remainder="drop")
    model = LogisticRegression(C=1.0, penalty="l2", solver="liblinear", max_iter=2000, random_state=20260928)
    return Pipeline([("prep", prep), ("model", model)])


def purged_predict(frame, train_days=200, test_days=40, purge_days=5):
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
        model.fit(train[PATH_CONTEXT_FEATURES], y)
        test["score"] = model.predict_proba(test[PATH_CONTEXT_FEATURES])[:, 1]
        test["model"] = "logistic_path_plus_fixed_horizon"
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
        "expected_shortfall_95": float(ex.get("trade_expected_shortfall_95") or 0.0),
        "cluster_low": float(ex.get("cluster_bootstrap_95_low") or 0.0),
        "cluster_high": float(ex.get("cluster_bootstrap_95_high") or 0.0),
        "total_return": float(port.get("total_return") or 0.0),
        "max_drawdown": float(port.get("max_drawdown") or 0.0),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cache", default="research_data/marcap_kospi_pit")
    ap.add_argument("--supervised-cache", default="research_data/pit_supervised_v1")
    ap.add_argument("--result-dir", default="research_results/marcap_pit_combined")
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
    enriched = add_path_features(raw, context)
    z = add_fixed_horizon_target(raw, enriched, record_map, args.horizon)

    base_pred = _walk_forward_pit(
        context, "logistic_context", args.train_days, args.test_days,
        context=True, purge_days=args.horizon,
    )
    base_result, _, _ = evaluate_topk_only(base_pred, record_map, raw, args.horizon, args.top_k)

    combined_pred = purged_predict(z, args.train_days, args.test_days, args.horizon)
    combined_result, selected, _ = evaluate_topk_only(combined_pred, record_map, raw, args.horizon, args.top_k)

    b = view(base_result)
    c = view(combined_result)
    report = {
        "evaluation_stage": "PIT_PRELIMINARY_PURGED_COMBINED_CHALLENGER",
        "purge_days": args.horizon,
        "hyperparameter_search": False,
        "learning_target": "next_open_to_Dplus5_positive_cost_adjusted_return",
        "features": "market_context_plus_PIT_safe_daily_path",
        "execution_outcome_policy_unchanged": True,
        "supervised_cache": meta,
        "label_diagnostics": diag,
        "barrier_context_baseline": b,
        "combined_path_fixed_horizon": c,
        "delta_combined_minus_baseline": {k: c[k] - b[k] for k in c if k in b and isinstance(c[k], (int, float))},
        "selected_rows": int(len(selected)),
        "selected_ambiguous_rows": int(selected.get("ambiguous_same_bar", pd.Series(dtype=bool)).fillna(False).astype(bool).sum()) if not selected.empty else 0,
        "selected_post_entry_missing_rows": int(selected.get("post_entry_missing_future", pd.Series(dtype=bool)).fillna(False).astype(bool).sum()) if not selected.empty else 0,
        "interpretation": (
            "This combination is retained only if it improves OOS net economics and robustness over the barrier-context baseline. "
            "No execution assumption is relaxed."
        ),
    }
    out = Path(args.result_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out / "summary.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    selected.to_csv(out / "selected.csv", index=False)
    print("COMBINED_CHALLENGER=" + json.dumps(report, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
