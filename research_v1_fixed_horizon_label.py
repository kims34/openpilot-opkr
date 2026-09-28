"""Fixed-horizon label challenger for IndexAlert PIT research.

The live/execution outcome map is unchanged: selected names are still evaluated
with the existing executable target/stop/time policy.  Only the learning target
changes.  Instead of learning whether +4% beats -2.5% first, this challenger
learns next-open -> D+5 close cost-adjusted return (classification and Ridge).
This isolates label choice from execution-policy choice.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from research_v1_context import CONTEXT_FEATURES, add_context
from research_v1_holdaware import evaluate_topk_only
from research_v1_pit_run import _evaluate_positive_net
from research_v1_pit_run_purged import _walk_forward_pit
from research_v1_supervised_cache import load_or_build
from run_research_v1 import load_panel


def add_fixed_horizon_target(raw: pd.DataFrame, frame: pd.DataFrame, record_map: dict, horizon: int) -> pd.DataFrame:
    dates = sorted(pd.Timestamp(x) for x in raw["decision_date"].drop_duplicates())
    pairs = []
    for i, d in enumerate(dates):
        if i + horizon >= len(dates) or i + 1 >= len(dates):
            continue
        pairs.append({"decision_date": d, "entry_date": dates[i + 1], "exit_date": dates[i + horizon]})
    pair_df = pd.DataFrame(pairs)
    z = frame.merge(pair_df, on="decision_date", how="left", validate="many_to_one")

    entry = raw[["decision_date", "symbol", "open"]].rename(columns={"decision_date": "entry_date", "open": "fh_entry_open"})
    exit_ = raw[["decision_date", "symbol", "close"]].rename(columns={"decision_date": "exit_date", "close": "fh_exit_close"})
    z = z.merge(entry, on=["entry_date", "symbol"], how="left", validate="many_to_one")
    z = z.merge(exit_, on=["exit_date", "symbol"], how="left", validate="many_to_one")

    cost_rows = [
        {"decision_date": pd.Timestamp(day), "symbol": str(symbol), "fh_cost": float(rec.cost_return)}
        for (day, symbol), rec in record_map.items()
    ]
    cost_df = pd.DataFrame(cost_rows)
    z = z.merge(cost_df, on=["decision_date", "symbol"], how="left", validate="one_to_one")
    z["fh_gross_return"] = z["fh_exit_close"] / z["fh_entry_open"] - 1.0
    z["fh_net_return"] = z["fh_gross_return"] - z["fh_cost"]
    z["fh_label_available"] = z[["fh_entry_open", "fh_exit_close", "fh_cost"]].notna().all(axis=1)
    z["fh_positive_net"] = np.where(z["fh_label_available"], (z["fh_net_return"] > 0).astype(int), np.nan)
    return z


def _pipe(kind: str):
    prep = ColumnTransformer([
        ("num", Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]), CONTEXT_FEATURES)
    ], remainder="drop")
    if kind == "logistic":
        model = LogisticRegression(C=1.0, penalty="l2", solver="liblinear", max_iter=2000, random_state=20260928)
    elif kind == "ridge":
        model = Ridge(alpha=1.0)
    else:
        raise ValueError(kind)
    return Pipeline([("prep", prep), ("model", model)])


def purged_predict(frame: pd.DataFrame, *, target_col: str, kind: str, train_days=200, test_days=40, purge_days=5):
    dates = sorted(pd.Timestamp(x) for x in frame["decision_date"].drop_duplicates())
    out = []
    start = train_days + purge_days
    while start < len(dates):
        test_block = dates[start:start + test_days]
        if not test_block:
            break
        train_end = start - purge_days
        train_block = dates[:train_end]
        train = frame[frame["decision_date"].isin(train_block)].copy()
        train = train[train[target_col].notna()].copy()
        test = frame[frame["decision_date"].isin(test_block)].copy()
        if train.empty or test.empty:
            start += test_days
            continue
        pipe = _pipe(kind)
        if kind == "logistic":
            y = train[target_col].astype(int)
            if y.nunique() < 2:
                start += test_days
                continue
            pipe.fit(train[CONTEXT_FEATURES], y)
            test["score"] = pipe.predict_proba(test[CONTEXT_FEATURES])[:, 1]
            model_name = "logistic_fixed_horizon_positive"
        else:
            pipe.fit(train[CONTEXT_FEATURES], train[target_col].astype(float))
            test["score"] = pipe.predict(test[CONTEXT_FEATURES])
            model_name = "ridge_fixed_horizon_net"
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


def view(result: dict) -> dict:
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
    ap.add_argument("--result-dir", default="research_results/marcap_pit_fixed_horizon")
    ap.add_argument("--horizon", type=int, default=5)
    ap.add_argument("--top-k", type=int, default=3)
    ap.add_argument("--target", type=float, default=0.04)
    ap.add_argument("--stop", type=float, default=-0.025)
    ap.add_argument("--participation", type=float, default=0.0005)
    ap.add_argument("--train-days", type=int, default=200)
    ap.add_argument("--test-days", type=int, default=40)
    args = ap.parse_args()

    raw = load_panel(Path(args.cache))
    frame, record_map, diag, cache_meta = load_or_build(
        raw, Path(args.supervised_cache),
        horizon=args.horizon, target_return=args.target, stop_return=args.stop,
        participation=args.participation, commission_round_trip_bps=3.0,
    )
    frame = frame[frame["adv20_rank"] >= 0.20].copy().reset_index(drop=True)
    context = add_context(frame)
    z = add_fixed_horizon_target(raw, context, record_map, args.horizon)

    baseline_pred = _walk_forward_pit(
        context, "logistic_context", args.train_days, args.test_days,
        context=True, purge_days=args.horizon,
    )
    baseline_result, _, _ = evaluate_topk_only(baseline_pred, record_map, raw, args.horizon, args.top_k)

    cls_pred = purged_predict(
        z, target_col="fh_positive_net", kind="logistic",
        train_days=args.train_days, test_days=args.test_days, purge_days=args.horizon,
    )
    cls_result, cls_selected, _ = evaluate_topk_only(cls_pred, record_map, raw, args.horizon, args.top_k)

    reg_pred = purged_predict(
        z, target_col="fh_net_return", kind="ridge",
        train_days=args.train_days, test_days=args.test_days, purge_days=args.horizon,
    )
    reg_result, reg_selected = _evaluate_positive_net(raw, reg_pred, record_map, args.horizon, args.top_k)

    base = view(baseline_result)
    cls = view(cls_result)
    reg = view(reg_result)
    report = {
        "evaluation_stage": "PIT_PRELIMINARY_PURGED_FIXED_HORIZON_LABEL_CHALLENGER",
        "purge_days": args.horizon,
        "execution_outcome_policy_unchanged": True,
        "learning_target": "next_open_to_Dplus5_close_cost_adjusted_return",
        "hyperparameter_search": False,
        "supervised_cache": cache_meta,
        "barrier_label_baseline": base,
        "fixed_horizon_logistic": cls,
        "fixed_horizon_ridge_positive_only": reg,
        "delta_logistic_vs_barrier": {k: cls[k] - base[k] for k in cls if k in base and isinstance(cls[k], (int, float))},
        "delta_ridge_vs_barrier": {k: reg[k] - base[k] for k in reg if k in base and isinstance(reg[k], (int, float))},
        "fixed_horizon_training_rows": int(z["fh_label_available"].fillna(False).sum()),
        "fixed_horizon_missing_rows": int((~z["fh_label_available"].fillna(False)).sum()),
        "classification_selected_rows": int(len(cls_selected)),
        "regression_selected_rows": int(len(reg_selected)),
        "label_diagnostics": diag,
        "interpretation": (
            "Adopt a fixed-horizon learning target only if it improves executable barrier-policy OOS economics. "
            "The execution policy itself has not been relaxed."
        ),
    }
    out = Path(args.result_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out / "summary.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    cls_selected.to_csv(out / "logistic_selected.csv", index=False)
    reg_selected.to_csv(out / "ridge_selected.csv", index=False)
    print("FIXED_HORIZON_LABEL=" + json.dumps(report, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
