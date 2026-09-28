"""Fixed-horizon learning target for IndexAlert PIT research.

Core distributional research learns executable next-open -> D+5 cost-adjusted
return.  Raw OHLC remains execution evidence, but fixed-horizon economic return
uses a corporate-action-safe price index built from KRX's reported daily
fluctuation rate versus the applicable adjusted base price.

For a position entered at the regular-session open:
  entry economic price = adjusted close index on entry day * raw open/raw close
  exit economic price  = adjusted close index on the exit day
This preserves within-day open->close movement while removing mechanical
close-to-close price jumps from splits/consolidations/rights-base adjustments.
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


def build_economic_mark_panel(raw: pd.DataFrame) -> pd.DataFrame:
    """Return raw rows plus a per-symbol corporate-action-safe close index.

    The level is arbitrary within each symbol; only within-symbol ratios are used.
    """
    if "krx_change_return" not in raw.columns:
        raise RuntimeError("krx_change_return required for corporate-action-safe fixed-horizon labels")
    x = raw.copy().sort_values(["symbol", "decision_date"]).reset_index(drop=True)
    x["krx_change_return"] = pd.to_numeric(x["krx_change_return"], errors="coerce")
    gross_factor = 1.0 + x["krx_change_return"]
    gross_factor = gross_factor.where(gross_factor > 0)
    x["economic_close"] = gross_factor.groupby(x["symbol"], sort=False).cumprod()
    x["economic_open"] = x["economic_close"] * (x["open"] / x["close"])
    return x


def economic_mark_panel_for_portfolio(raw: pd.DataFrame) -> pd.DataFrame:
    x = build_economic_mark_panel(raw)
    out = x.copy()
    out["close"] = out["economic_close"]
    return out


def add_fixed_horizon_target(raw: pd.DataFrame, frame: pd.DataFrame, record_map: dict, horizon: int) -> pd.DataFrame:
    econ = build_economic_mark_panel(raw)
    dates = sorted(pd.Timestamp(x) for x in raw["decision_date"].drop_duplicates())
    pairs = []
    for i, d in enumerate(dates):
        if i + horizon >= len(dates) or i + 1 >= len(dates):
            continue
        pairs.append({"decision_date": d, "entry_date": dates[i + 1], "exit_date": dates[i + horizon]})
    pair_df = pd.DataFrame(pairs)
    z = frame.merge(pair_df, on="decision_date", how="left", validate="many_to_one")

    entry = econ[["decision_date", "symbol", "open", "economic_open"]].rename(columns={
        "decision_date": "entry_date",
        "open": "fh_entry_open",
        "economic_open": "fh_entry_economic_price",
    })
    exit_ = econ[["decision_date", "symbol", "close", "economic_close"]].rename(columns={
        "decision_date": "exit_date",
        "close": "fh_exit_close",
        "economic_close": "fh_exit_economic_price",
    })
    z = z.merge(entry, on=["entry_date", "symbol"], how="left", validate="many_to_one")
    z = z.merge(exit_, on=["exit_date", "symbol"], how="left", validate="many_to_one")

    cost_rows = [
        {"decision_date": pd.Timestamp(day), "symbol": str(symbol), "fh_cost": float(rec.cost_return)}
        for (day, symbol), rec in record_map.items()
    ]
    cost_df = pd.DataFrame(cost_rows)
    z = z.merge(cost_df, on=["decision_date", "symbol"], how="left", validate="one_to_one")

    z["fh_raw_price_ratio_return"] = z["fh_exit_close"] / z["fh_entry_open"] - 1.0
    z["fh_gross_return"] = z["fh_exit_economic_price"] / z["fh_entry_economic_price"] - 1.0
    z["fh_net_return"] = z["fh_gross_return"] - z["fh_cost"]
    z["fh_label_available"] = z[[
        "fh_entry_economic_price", "fh_exit_economic_price", "fh_cost"
    ]].notna().all(axis=1)
    z["fh_positive_net"] = np.where(
        z["fh_label_available"], (z["fh_net_return"] > 0).astype(int), np.nan
    )
    z["fh_corporate_action_gap"] = z["fh_raw_price_ratio_return"] - z["fh_gross_return"]
    z["fh_return_policy"] = "KRX_FLUC_RT_ECONOMIC_INDEX_FROM_ENTRY_OPEN_TO_EXIT_CLOSE"
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
    ap.add_argument("--supervised-cache", default="research_data/pit_supervised_v2_ca")
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
    gap = pd.to_numeric(z["fh_corporate_action_gap"], errors="coerce").dropna().abs()
    report = {
        "evaluation_stage": "PIT_PRELIMINARY_PURGED_FIXED_HORIZON_LABEL_CHALLENGER",
        "purge_days": args.horizon,
        "learning_target": "corporate_action_safe_next_open_to_Dplus5_close_cost_adjusted_return",
        "fixed_horizon_return_policy": "KRX_FLUC_RT_ECONOMIC_INDEX_FROM_ENTRY_OPEN_TO_EXIT_CLOSE",
        "hyperparameter_search": False,
        "supervised_cache": cache_meta,
        "barrier_label_baseline": base,
        "fixed_horizon_logistic": cls,
        "fixed_horizon_ridge_positive_only": reg,
        "delta_logistic_vs_barrier": {k: cls[k] - base[k] for k in cls if k in base and isinstance(cls[k], (int, float))},
        "delta_ridge_vs_barrier": {k: reg[k] - base[k] for k in reg if k in base and isinstance(reg[k], (int, float))},
        "fixed_horizon_training_rows": int(z["fh_label_available"].fillna(False).sum()),
        "fixed_horizon_missing_rows": int((~z["fh_label_available"].fillna(False)).sum()),
        "fh_raw_vs_economic_gap": {
            "abs_gt_1pct": int((gap > 0.01).sum()),
            "abs_gt_5pct": int((gap > 0.05).sum()),
            "abs_gt_10pct": int((gap > 0.10).sum()),
            "max_abs_gap": float(gap.max()) if len(gap) else 0.0,
        },
        "classification_selected_rows": int(len(cls_selected)),
        "regression_selected_rows": int(len(reg_selected)),
        "label_diagnostics": diag,
    }
    out = Path(args.result_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out / "summary.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    cls_selected.to_csv(out / "logistic_selected.csv", index=False)
    reg_selected.to_csv(out / "ridge_selected.csv", index=False)
    print("FIXED_HORIZON_LABEL=" + json.dumps(report, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
