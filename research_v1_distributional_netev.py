"""Distributional executable NetEV v0 for IndexAlert Master Spec.

Primary target/evaluation is no longer the legacy fixed target/stop barrier.
For the current daily-data stage, executable-return proxy is:

    decision at prior close -> next executable regular-session open -> D+5 close
    minus date-aware statutory tax, commission, spread and impact allowance.

A simple Ridge predicts mean fixed-horizon Net Return. A purged calibration block
then estimates residual quantiles conditional on contemporaneous volatility
terciles. The conservative lower NetEV is predicted_mean + calibrated q25
residual. Only lower NetEV > 0 is admitted, up to three names per day.

This is deliberately simple and preliminary: no hyperparameter search, no
intraday fill ratio/delay model, and no claim of final conformal coverage.
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
from sklearn.linear_model import Ridge
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from research_v1_context import CONTEXT_FEATURES, add_context
from research_v1_core import DecisionRecord, date_cluster_bootstrap_mean, summarize
from research_v1_fixed_horizon_label import add_fixed_horizon_target
from research_v1_ml import stateful_select_records
from research_v1_portfolio import simulate_portfolio, summary_dict
from research_v1_supervised_cache import load_or_build
from run_research_v1 import load_panel

VOL_BUCKETS = [0.0, 1.0 / 3.0, 2.0 / 3.0, 1.0000001]
Q_LOW = 0.25
Q_MED = 0.50
Q_HIGH = 0.75


def _pipe() -> Pipeline:
    prep = ColumnTransformer([
        ("num", Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]), CONTEXT_FEATURES)
    ], remainder="drop")
    return Pipeline([("prep", prep), ("reg", Ridge(alpha=1.0))])


def _bucket(vol_rank: pd.Series) -> pd.Series:
    return pd.cut(
        vol_rank.astype(float),
        bins=VOL_BUCKETS,
        labels=["low", "mid", "high"],
        include_lowest=True,
        right=False,
    ).astype(str)


def _fixed_record_map(z: pd.DataFrame, horizon: int) -> dict:
    records = {}
    valid = z[z["fh_label_available"].fillna(False).astype(bool)].copy()
    for r in valid.itertuples(index=False):
        if pd.isna(r.fh_entry_open) or pd.isna(r.fh_exit_close) or pd.isna(r.fh_cost):
            continue
        rec = DecisionRecord(
            decision_day=pd.Timestamp(r.decision_date).date(),
            entry_day=pd.Timestamp(r.entry_date).date(),
            symbol=str(r.symbol),
            score=0.0,
            entry_price=float(r.fh_entry_open),
            horizon=int(horizon),
            target_return=0.0,
            stop_return=0.0,
            cost_return=float(r.fh_cost),
            outcome="TIME",
            gross_return=float(r.fh_gross_return),
            net_return=float(r.fh_net_return),
            exit_day=pd.Timestamp(r.exit_date).date(),
            exit_price=float(r.fh_exit_close),
        )
        records[(rec.decision_day, rec.symbol)] = rec
    return records


def _calibration_quantiles(cal: pd.DataFrame) -> dict:
    c = cal[cal["fh_label_available"].fillna(False).astype(bool)].copy()
    c = c[c["pred_mean"].notna() & c["fh_net_return"].notna()].copy()
    if c.empty:
        return {}
    c["residual"] = c["fh_net_return"].astype(float) - c["pred_mean"].astype(float)
    c["vol_bucket"] = _bucket(c["vol20_rank"])
    global_q = {
        "low": float(c["residual"].quantile(Q_LOW)),
        "med": float(c["residual"].quantile(Q_MED)),
        "high": float(c["residual"].quantile(Q_HIGH)),
        "n": int(len(c)),
    }
    out = {"__global__": global_q}
    for name, g in c.groupby("vol_bucket"):
        if len(g) < 50:
            out[str(name)] = {**global_q, "fallback_global": True, "bucket_n": int(len(g))}
        else:
            out[str(name)] = {
                "low": float(g["residual"].quantile(Q_LOW)),
                "med": float(g["residual"].quantile(Q_MED)),
                "high": float(g["residual"].quantile(Q_HIGH)),
                "n": int(len(g)),
                "fallback_global": False,
            }
    return out


def _apply_distribution(test: pd.DataFrame, quantiles: dict) -> pd.DataFrame:
    x = test.copy()
    x["vol_bucket"] = _bucket(x["vol20_rank"])
    global_q = quantiles.get("__global__", {"low": 0.0, "med": 0.0, "high": 0.0})

    def q_for(bucket: str, key: str) -> float:
        return float(quantiles.get(str(bucket), global_q).get(key, global_q.get(key, 0.0)))

    x["netev_low"] = x["pred_mean"] + [q_for(b, "low") for b in x["vol_bucket"]]
    x["netev_median"] = x["pred_mean"] + [q_for(b, "med") for b in x["vol_bucket"]]
    x["netev_high"] = x["pred_mean"] + [q_for(b, "high") for b in x["vol_bucket"]]
    x["score"] = x["netev_low"]
    return x


def distributional_walk_forward(
    z: pd.DataFrame,
    *,
    train_days: int = 160,
    cal_days: int = 40,
    test_days: int = 40,
    purge_days: int = 5,
):
    dates = sorted(pd.Timestamp(x) for x in z["decision_date"].drop_duplicates())
    start = train_days + cal_days + 2 * purge_days
    preds = []
    folds = []
    while start < len(dates):
        test_dates = dates[start:start + test_days]
        if not test_dates:
            break
        cal_end = start - purge_days
        cal_start = cal_end - cal_days
        train_end = cal_start - purge_days
        if train_end <= 0:
            start += test_days
            continue
        train_dates = dates[:train_end]
        cal_dates = dates[cal_start:cal_end]

        train = z[z["decision_date"].isin(train_dates)].copy()
        cal = z[z["decision_date"].isin(cal_dates)].copy()
        test = z[z["decision_date"].isin(test_dates)].copy()
        train = train[train["fh_label_available"].fillna(False).astype(bool)].copy()
        if train.empty or cal.empty or test.empty:
            start += test_days
            continue

        model = _pipe()
        model.fit(train[CONTEXT_FEATURES], train["fh_net_return"].astype(float))
        cal["pred_mean"] = model.predict(cal[CONTEXT_FEATURES])
        test["pred_mean"] = model.predict(test[CONTEXT_FEATURES])
        q = _calibration_quantiles(cal)
        if not q:
            start += test_days
            continue
        test = _apply_distribution(test, q)
        test["model"] = "ridge_context_distributional_netev_v0"
        test["train_end"] = train_dates[-1]
        test["cal_start"] = cal_dates[0]
        test["cal_end"] = cal_dates[-1]
        preds.append(test)
        folds.append({
            "test_start": str(test_dates[0].date()),
            "test_end": str(test_dates[-1].date()),
            "train_end": str(train_dates[-1].date()),
            "cal_start": str(cal_dates[0].date()),
            "cal_end": str(cal_dates[-1].date()),
            "purge_days": int(purge_days),
            "residual_quantiles": q,
        })
        start += test_days
    if not preds:
        return pd.DataFrame(), folds
    return pd.concat(preds, ignore_index=True).sort_values(
        ["decision_date", "score"], ascending=[True, False]
    ), folds


def _portfolio(raw, records, pred, horizon):
    if pred.empty:
        return {}
    start = pd.Timestamp(pred["decision_date"].min()).date()
    end = max(
        pd.Timestamp(pred["decision_date"].max()).date(),
        max((r.exit_day for r in records), default=start),
    )
    _, p = simulate_portfolio(
        raw,
        records,
        horizon=horizon,
        initial_equity=1.0,
        daily_cohort_fraction=1.0 / horizon,
        suppress_duplicate_symbols=False,
        evaluation_start=start,
        evaluation_end=end,
    )
    return summary_dict(p)


def _metric(records):
    s = summarize(records)
    point, lo, hi = date_cluster_bootstrap_mean(records) if records else (0.0, 0.0, 0.0)
    return {
        **asdict(s),
        "cluster_bootstrap_mean_net_return": point,
        "cluster_bootstrap_95_low": lo,
        "cluster_bootstrap_95_high": hi,
    }


def freeze_original_topk(eligible: pd.DataFrame, top_k: int) -> pd.DataFrame:
    """Freeze decision-time ranks before portfolio-state/executability checks."""
    if eligible.empty:
        return eligible.copy()
    return (
        eligible.sort_values(["decision_date", "score"], ascending=[True, False])
        .groupby("decision_date", group_keys=False)
        .head(top_k)
        .copy()
    )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cache", default="research_data/marcap_kospi_pit")
    ap.add_argument("--supervised-cache", default="research_data/pit_supervised_v1")
    ap.add_argument("--result-dir", default="research_results/marcap_pit_distributional")
    ap.add_argument("--horizon", type=int, default=5)
    ap.add_argument("--top-k", type=int, default=3)
    ap.add_argument("--target", type=float, default=0.04)
    ap.add_argument("--stop", type=float, default=-0.025)
    ap.add_argument("--participation", type=float, default=0.0005)
    ap.add_argument("--train-days", type=int, default=160)
    ap.add_argument("--cal-days", type=int, default=40)
    ap.add_argument("--test-days", type=int, default=40)
    args = ap.parse_args()

    raw = load_panel(Path(args.cache))
    frame, legacy_record_map, label_diag, meta = load_or_build(
        raw,
        Path(args.supervised_cache),
        horizon=args.horizon,
        target_return=args.target,
        stop_return=args.stop,
        participation=args.participation,
        commission_round_trip_bps=3.0,
    )
    frame = frame[frame["adv20_rank"] >= 0.20].copy().reset_index(drop=True)
    context = add_context(frame)
    z = add_fixed_horizon_target(raw, context, legacy_record_map, args.horizon)
    fixed_map = _fixed_record_map(z, args.horizon)

    pred, folds = distributional_walk_forward(
        z,
        train_days=args.train_days,
        cal_days=args.cal_days,
        test_days=args.test_days,
        purge_days=args.horizon,
    )
    if pred.empty:
        raise RuntimeError("distributional walk-forward produced no predictions")

    eligible = pred[pred["netev_low"] > 0].copy()
    # Freeze the decision-time ranking before applying stateful executability.
    # A blocked/held name leaves an empty slot; ranks > top_k must never be
    # promoted retroactively, otherwise realised portfolio state changes the
    # candidate set and overstates the executable OOS edge.
    frozen_topk = freeze_original_topk(eligible, args.top_k)
    records, selected, select_diag = stateful_select_records(
        frozen_topk,
        fixed_map,
        top_k=args.top_k,
        threshold=0.0,
    )

    realised = pred[pred["fh_label_available"].fillna(False).astype(bool)].copy()
    interval_mask = (
        (realised["fh_net_return"] >= realised["netev_low"])
        & (realised["fh_net_return"] <= realised["netev_high"])
    )
    lower_coverage = float((realised["fh_net_return"] >= realised["netev_low"]).mean()) if len(realised) else 0.0
    central_coverage = float(interval_mask.mean()) if len(realised) else 0.0

    if not selected.empty:
        selected_dates = pd.to_datetime(selected["decision_date"]).dt.date
        selected_keys = set(zip(selected_dates, selected["symbol"].astype(str)))
    else:
        selected_keys = set()
    realised["admitted"] = [
        (pd.Timestamp(d).date(), str(s)) in selected_keys
        for d, s in zip(realised["decision_date"], realised["symbol"])
    ]
    rejected = realised[~realised["admitted"]]

    test_dates = int(pred["decision_date"].nunique())
    trade_days = int(selected["decision_date"].nunique()) if not selected.empty else 0
    report = {
        "evaluation_stage": "PIT_PRELIMINARY_DISTRIBUTIONAL_EXECUTABLE_NETEV_V0",
        "master_spec_alignment": {
            "primary_target": "next_executable_open_to_Dplus5_close_cost_adjusted_net_return",
            "legacy_barrier_is_primary": False,
            "distribution": "Ridge mean + purged calibration residual q25/q50/q75 conditional on vol20 tercile",
            "admission": "netev_lower_bound_gt_0__freeze_original_top3__blocked_slot_stays_empty",
            "final_conformal_guarantee_claimed": False,
        },
        "purge_days": args.horizon,
        "train_days_initial": args.train_days,
        "cal_days": args.cal_days,
        "test_days": args.test_days,
        "features": CONTEXT_FEATURES,
        "supervised_cache": meta,
        "legacy_label_diagnostics": label_diag,
        "prediction_rows": int(len(pred)),
        "realised_test_rows": int(len(realised)),
        "eligible_lower_bound_positive_rows": int(len(eligible)),
        "selected_records": int(len(records)),
        "test_dates": test_dates,
        "trade_days": trade_days,
        "trade_day_coverage": float(trade_days / test_dates) if test_dates else 0.0,
        "selection_diagnostics": select_diag,
        "selected_executable": _metric(records),
        "portfolio": _portfolio(raw, records, pred, args.horizon),
        "distribution_diagnostics": {
            "target_lower_quantile": Q_LOW,
            "target_central_interval": [Q_LOW, Q_HIGH],
            "empirical_actual_ge_lower": lower_coverage,
            "empirical_actual_inside_q25_q75": central_coverage,
            "mean_predicted_interval_width": float((realised["netev_high"] - realised["netev_low"]).mean()) if len(realised) else 0.0,
        },
        "counterfactual_observable": {
            "admitted_mean_fh_net_return": float(realised.loc[realised["admitted"], "fh_net_return"].mean()) if realised["admitted"].any() else None,
            "rejected_mean_fh_net_return": float(rejected["fh_net_return"].mean()) if len(rejected) else None,
            "rejected_positive_rate": float((rejected["fh_net_return"] > 0).mean()) if len(rejected) else None,
        },
        "folds": folds,
        "blockers": [
            "daily_open_proxy_not_intraday_fill_ratio_time_price",
            "common_stock_identity_not_yet_officially_validated",
            "exact_halt_delisting_economics_not_yet_joined",
            "2024_2026_only_preliminary_history",
        ],
    }

    ex = report["selected_executable"]
    if (
        float(ex.get("mean_net_return", 0.0)) > 0
        and float(ex.get("profit_factor", 0.0)) > 1.0
        and float(ex.get("cluster_bootstrap_95_low", 0.0)) > 0
    ):
        report["verdict"] = "PRELIMINARY_POSITIVE_DISTRIBUTIONAL_EDGE"
    elif len(records) == 0:
        report["verdict"] = "ABSTAINED_ALL_TRADES__NO_CONSERVATIVE_EDGE"
    else:
        report["verdict"] = "NO_ROBUST_DISTRIBUTIONAL_EDGE_YET"

    out = Path(args.result_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out / "summary.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    pred.to_parquet(out / "predictions.parquet", index=False)
    selected.to_csv(out / "selected.csv", index=False)
    print("DISTRIBUTIONAL_NETEV=" + json.dumps(report, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
