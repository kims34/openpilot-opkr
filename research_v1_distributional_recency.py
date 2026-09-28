"""Recency challenger for Distributional NetEV v0.

Compares the current expanding training history with one prespecified rolling
window equal to the original 160-session training length. Calibration remains a
separate 40-session block with five-session purge on both sides. No window search.

For MTM diagnostics only, a selected position with no executable close on an
intermediate session is carried at its last valid mark until trading resumes.
Realized entry/exit economics are not changed.
"""
from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path

import pandas as pd

from research_v1_context import CONTEXT_FEATURES, add_context
from research_v1_core import date_cluster_bootstrap_mean, summarize
from research_v1_distributional_netev import (
    _apply_distribution,
    _calibration_quantiles,
    _fixed_record_map,
    _pipe,
    distributional_walk_forward,
    freeze_original_topk,
)
from research_v1_fixed_horizon_label import add_fixed_horizon_target
from research_v1_ml import stateful_select_records
from research_v1_portfolio import simulate_portfolio, summary_dict
from research_v1_supervised_cache import load_or_build
from run_research_v1 import load_panel


def rolling_distributional_walk_forward(
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
        train_start = max(0, train_end - train_days)
        if train_end <= train_start:
            start += test_days
            continue
        train_dates = dates[train_start:train_end]
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
        quantiles = _calibration_quantiles(cal)
        if not quantiles:
            start += test_days
            continue
        test = _apply_distribution(test, quantiles)
        test["model"] = "ridge_context_distributional_netev_rolling160"
        preds.append(test)
        folds.append({
            "test_start": str(test_dates[0].date()),
            "test_end": str(test_dates[-1].date()),
            "train_start": str(train_dates[0].date()),
            "train_end": str(train_dates[-1].date()),
            "cal_start": str(cal_dates[0].date()),
            "cal_end": str(cal_dates[-1].date()),
            "train_sessions": int(len(train_dates)),
            "purge_days": int(purge_days),
        })
        start += test_days
    if not preds:
        return pd.DataFrame(), folds
    return pd.concat(preds, ignore_index=True).sort_values(
        ["decision_date", "score"], ascending=[True, False]
    ), folds


def _portfolio_with_halt_mark_carry(raw, records, pred, horizon):
    if pred.empty:
        return {}
    p = raw[["decision_date", "symbol", "close"]].copy()
    p["decision_date"] = pd.to_datetime(p["decision_date"])
    sessions = sorted(pd.Timestamp(x).date() for x in p["decision_date"].unique())
    close_map = {
        (pd.Timestamp(r.decision_date).date(), str(r.symbol)): float(r.close)
        for r in p.itertuples(index=False)
    }
    additions = []
    for rec in records:
        last_mark = float(rec.entry_price)
        for day in sessions:
            if day < rec.entry_day:
                continue
            if day >= rec.exit_day:
                break
            key = (day, rec.symbol)
            if key in close_map:
                last_mark = close_map[key]
            else:
                additions.append({
                    "decision_date": pd.Timestamp(day),
                    "symbol": rec.symbol,
                    "close": last_mark,
                })
    if additions:
        p = pd.concat([p, pd.DataFrame(additions)], ignore_index=True)
        p = p.drop_duplicates(["decision_date", "symbol"], keep="first")

    eval_start = pd.Timestamp(pred["decision_date"].min()).date()
    eval_end = max(
        pd.Timestamp(pred["decision_date"].max()).date(),
        max((r.exit_day for r in records), default=eval_start),
    )
    _, port = simulate_portfolio(
        p,
        records,
        horizon=horizon,
        initial_equity=1.0,
        daily_cohort_fraction=1.0 / horizon,
        suppress_duplicate_symbols=False,
        evaluation_start=eval_start,
        evaluation_end=eval_end,
    )
    result = summary_dict(port)
    result["halt_mark_carry_forward_rows"] = int(len(additions))
    result["halt_mark_policy"] = "last_valid_mark_for_intermediate_MTM_only"
    return result


def _evaluate(pred, fixed_map, raw, horizon, top_k):
    eligible = pred[pred["netev_low"] > 0].copy()
    frozen_topk = freeze_original_topk(eligible, top_k)
    records, selected, diag = stateful_select_records(
        frozen_topk, fixed_map, top_k=top_k, threshold=0.0
    )
    metrics = summarize(records)
    point, lo, hi = date_cluster_bootstrap_mean(records) if records else (0.0, 0.0, 0.0)
    test_dates = int(pred["decision_date"].nunique())
    trade_days = int(selected["decision_date"].nunique()) if not selected.empty else 0
    yearly = []
    if not selected.empty:
        x = selected.copy()
        x["year"] = pd.to_datetime(x["decision_date"]).dt.year
        for y, g in x.groupby("year"):
            yearly.append({
                "year": int(y),
                "trades": int(len(g)),
                "mean_fh_net_return": float(g["fh_net_return"].mean()),
                "median_fh_net_return": float(g["fh_net_return"].median()),
                "positive_rate": float((g["fh_net_return"] > 0).mean()),
            })
    return {
        "eligible_rows": int(len(eligible)),
        "frozen_topk_rows": int(len(frozen_topk)),
        "trades": int(len(records)),
        "trade_days": trade_days,
        "test_dates": test_dates,
        "trade_day_coverage": float(trade_days / test_dates) if test_dates else 0.0,
        "metrics": {
            **asdict(metrics),
            "cluster_bootstrap_mean_net_return": point,
            "cluster_bootstrap_95_low": lo,
            "cluster_bootstrap_95_high": hi,
        },
        "portfolio": _portfolio_with_halt_mark_carry(raw, records, pred, horizon),
        "selection_diagnostics": diag,
        "selection_policy": "netev_low_gt_0__freeze_original_topk__blocked_slot_stays_empty",
        "yearly": yearly,
    }, selected


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cache", default="research_data/marcap_kospi_pit")
    ap.add_argument("--supervised-cache", default="research_data/pit_supervised_v1")
    ap.add_argument("--result-dir", default="research_results/marcap_pit_distributional_recency")
    ap.add_argument("--horizon", type=int, default=5)
    ap.add_argument("--top-k", type=int, default=3)
    ap.add_argument("--train-days", type=int, default=160)
    ap.add_argument("--cal-days", type=int, default=40)
    ap.add_argument("--test-days", type=int, default=40)
    args = ap.parse_args()

    raw = load_panel(Path(args.cache))
    frame, legacy_map, diag, meta = load_or_build(
        raw, Path(args.supervised_cache),
        horizon=args.horizon, target_return=0.04, stop_return=-0.025,
        participation=0.0005, commission_round_trip_bps=3.0,
    )
    frame = frame[frame["adv20_rank"] >= 0.20].copy().reset_index(drop=True)
    context = add_context(frame)
    z = add_fixed_horizon_target(raw, context, legacy_map, args.horizon)
    fixed_map = _fixed_record_map(z, args.horizon)

    exp_pred, exp_folds = distributional_walk_forward(
        z, train_days=args.train_days, cal_days=args.cal_days,
        test_days=args.test_days, purge_days=args.horizon,
    )
    roll_pred, roll_folds = rolling_distributional_walk_forward(
        z, train_days=args.train_days, cal_days=args.cal_days,
        test_days=args.test_days, purge_days=args.horizon,
    )
    exp, exp_sel = _evaluate(exp_pred, fixed_map, raw, args.horizon, args.top_k)
    roll, roll_sel = _evaluate(roll_pred, fixed_map, raw, args.horizon, args.top_k)

    em = exp["metrics"]
    rm = roll["metrics"]
    ep = exp["portfolio"]
    rp = roll["portfolio"]
    delta = {
        "mean_net_return": float(rm.get("mean_net_return", 0.0) - em.get("mean_net_return", 0.0)),
        "profit_factor": float(rm.get("profit_factor", 0.0) - em.get("profit_factor", 0.0)),
        "cluster_low": float(rm.get("cluster_bootstrap_95_low", 0.0) - em.get("cluster_bootstrap_95_low", 0.0)),
        "max_drawdown": float(rp.get("max_drawdown", 0.0) - ep.get("max_drawdown", 0.0)),
        "trade_day_coverage": float(roll["trade_day_coverage"] - exp["trade_day_coverage"]),
    }
    improvement = (
        delta["mean_net_return"] > 0
        and delta["profit_factor"] > 0
        and delta["cluster_low"] >= 0
        and delta["max_drawdown"] >= -0.02
    )
    report = {
        "evaluation_stage": "PIT_PRELIMINARY_DISTRIBUTIONAL_NETEV_RECENCY_CHALLENGER",
        "master_spec_alignment": "drift_recency_after_distributional_netev",
        "window_search": False,
        "rolling_train_sessions": args.train_days,
        "purge_days": args.horizon,
        "cal_days": args.cal_days,
        "portfolio_mark_policy": "last_valid_mark_during_intermediate_halt_MTM_only",
        "selection_policy": "netev_low_gt_0__freeze_original_top3__blocked_slot_stays_empty",
        "supervised_cache": meta,
        "legacy_label_diagnostics": diag,
        "expanding": exp,
        "rolling_160": roll,
        "delta_rolling_minus_expanding": delta,
        "expanding_folds": exp_folds,
        "rolling_folds": roll_folds,
        "decision": "KEEP_ROLLING_AS_CHALLENGER" if improvement else "KEEP_EXPANDING_REFERENCE",
        "interpretation": (
            "One prespecified rolling window only. No train-window optimization is allowed from this result."
        ),
    }
    out = Path(args.result_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out / "summary.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    exp_sel.to_csv(out / "expanding_selected.csv", index=False)
    roll_sel.to_csv(out / "rolling160_selected.csv", index=False)
    print("DISTRIBUTIONAL_RECENCY=" + json.dumps(report, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
