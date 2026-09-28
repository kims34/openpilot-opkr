"""Calibration-selected abstention policy for IndexAlert Research v1.

This keeps the model simple and tests whether a NO-TRADE gate can rescue
cost-adjusted economics. Thresholds are chosen only on a calibration window,
then frozen for the subsequent test block. With the public smoke universe the
result remains strictly non-PIT and cannot be promoted.
"""
from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path

import numpy as np
import pandas as pd

from research_v1_core import date_cluster_bootstrap_mean, summarize
from research_v1_ml import FEATURES, _pipeline, make_supervised, stateful_select_records
from research_v1_portfolio import simulate_portfolio, summary_dict
from run_research_v1 import load_panel


def _choose_threshold(cal: pd.DataFrame, record_map: dict, top_k: int, min_trades: int = 30):
    if cal.empty:
        return None, {"reason": "empty_calibration"}
    coverages = [0.05, 0.10, 0.20, 0.30, 0.40]
    candidates = []
    probs = cal["prob"].to_numpy(dtype=float)
    for cov in coverages:
        threshold = float(np.quantile(probs, 1.0 - cov))
        recs, _, state_diag = stateful_select_records(
            cal, record_map, top_k=top_k, threshold=threshold, active_until={}
        )
        if len(recs) < min_trades:
            continue
        m = summarize(recs)
        point, lo, hi = date_cluster_bootstrap_mean(recs, samples=1000, seed=20260928)
        candidates.append({
            "coverage_target": cov,
            "threshold": threshold,
            "executable_trades": len(recs),
            **state_diag,
            "mean_net_return": m.mean_net_return,
            "bootstrap_point": point,
            "bootstrap_low": lo,
            "bootstrap_high": hi,
        })
    # Fail closed: admission is allowed only when the calibration-window lower
    # confidence bound is above zero. Otherwise the engine chooses NO TRADE.
    valid = [x for x in candidates if x["bootstrap_low"] > 0]
    if not valid:
        return None, {"reason": "no_positive_lower_bound_policy", "candidates": candidates}
    best = max(valid, key=lambda x: (x["bootstrap_low"], x["mean_net_return"]))
    return float(best["threshold"]), {"reason": "selected_on_calibration_lower_bound", "selected": best, "candidates": candidates}


def run_selective(
    frame: pd.DataFrame,
    record_map: dict,
    raw_panel: pd.DataFrame,
    train_days: int = 160,
    calibration_days: int = 40,
    test_days: int = 40,
    top_k: int = 3,
    horizon: int = 5,
):
    dates = sorted(pd.Timestamp(x) for x in frame["decision_date"].drop_duplicates())
    test_records = []
    all_test_rows = []
    fold_log = []
    live_state = {}
    start = train_days + calibration_days
    while start < len(dates):
        train_block = dates[: start - calibration_days]
        cal_block = dates[start - calibration_days: start]
        test_block = dates[start: start + test_days]
        if not test_block:
            break
        train = frame[frame["decision_date"].isin(train_block)]
        cal = frame[frame["decision_date"].isin(cal_block)].copy()
        test = frame[frame["decision_date"].isin(test_block)].copy()
        if train.empty or cal.empty or test.empty or train["label_positive_net"].nunique() < 2:
            start += test_days
            continue
        model = _pipeline("logistic_l2")
        model.fit(train[FEATURES], train["label_positive_net"])
        cal["prob"] = model.predict_proba(cal[FEATURES])[:, 1]
        test["prob"] = model.predict_proba(test[FEATURES])[:, 1]
        threshold, threshold_info = _choose_threshold(cal, record_map, top_k)
        if threshold is None:
            selected = []
            selected_rows = pd.DataFrame()
            state_diag = {"active_position_candidates_blocked": 0, "backfill_selections": 0}
        else:
            selected, selected_rows, state_diag = stateful_select_records(
                test, record_map, top_k=top_k, threshold=threshold, active_until=live_state
            )
        test_records.extend(selected)
        test["threshold"] = threshold if threshold is not None else np.nan
        test["trade_allowed"] = bool(threshold is not None)
        all_test_rows.append(test[[
            "decision_date", "symbol", "label_positive_net", "net_return",
            "ambiguous_same_bar", "prob", "threshold", "trade_allowed",
        ]])
        fold_log.append({
            "train_end": str(train_block[-1].date()),
            "cal_start": str(cal_block[0].date()),
            "cal_end": str(cal_block[-1].date()),
            "test_start": str(test_block[0].date()),
            "test_end": str(test_block[-1].date()),
            "threshold": threshold,
            "test_executable_selected": len(selected),
            **state_diag,
            "test_selected_ambiguous": int(selected_rows.get("ambiguous_same_bar", pd.Series(dtype=bool)).fillna(False).astype(bool).sum()) if not selected_rows.empty else 0,
            "threshold_selection": threshold_info,
        })
        start += test_days

    pred = pd.concat(all_test_rows, ignore_index=True) if all_test_rows else pd.DataFrame()
    metrics = summarize(test_records)
    point, lo, hi = date_cluster_bootstrap_mean(test_records) if test_records else (0.0, 0.0, 0.0)

    if pred.empty:
        eval_start = eval_end = None
    else:
        eval_start = pd.Timestamp(pred["decision_date"].min()).date()
        eval_end = max(
            pd.Timestamp(pred["decision_date"].max()).date(),
            max((r.exit_day for r in test_records), default=eval_start),
        )
    path, portfolio = simulate_portfolio(
        raw_panel, test_records, horizon=horizon, initial_equity=1.0,
        daily_cohort_fraction=1.0 / horizon, suppress_duplicate_symbols=False,
        evaluation_start=eval_start, evaluation_end=eval_end,
    )
    test_dates = int(pred["decision_date"].nunique()) if not pred.empty else 0
    trade_days = len({r.decision_day for r in test_records})
    return {
        "executable_set": {
            **asdict(metrics),
            "cluster_bootstrap_mean_net_return": point,
            "cluster_bootstrap_95_low": lo,
            "cluster_bootstrap_95_high": hi,
        },
        "portfolio": summary_dict(portfolio),
        "test_dates": test_dates,
        "trade_days": trade_days,
        "trade_day_coverage": float(trade_days / test_dates) if test_dates else 0.0,
        "avg_executable_trades_per_test_day": float(len(test_records) / test_dates) if test_dates else 0.0,
        "folds": fold_log,
    }, pred, pd.DataFrame([asdict(r) for r in test_records]), path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cache", default="research_data/public_smoke_daily")
    ap.add_argument("--result-dir", default="research_results/public_smoke_selective")
    ap.add_argument("--horizon", type=int, default=5)
    ap.add_argument("--top-k", type=int, default=3)
    ap.add_argument("--target", type=float, default=0.04)
    ap.add_argument("--stop", type=float, default=-0.025)
    ap.add_argument("--participation", type=float, default=0.0005)
    args = ap.parse_args()

    raw = load_panel(Path(args.cache))
    pit = bool(raw.get("point_in_time_universe", pd.Series([False])).fillna(False).astype(bool).all())
    frame, record_map, diag = make_supervised(
        raw, horizon=args.horizon, target_return=args.target, stop_return=args.stop,
        participation=args.participation,
    )
    result, pred, trades, path = run_selective(
        frame, record_map, raw, train_days=160, calibration_days=40,
        test_days=40, top_k=args.top_k, horizon=args.horizon,
    )
    report = {
        "result_class": "JUDGE" if pit else "SMOKE_NONPIT",
        "judge_eligible": pit,
        "policy": "logistic_l2_plus_calibration_selected_abstention",
        "selection_rule": (
            "For each fold, choose among fixed probability-coverage candidates on the prior "
            "40-day calibration block; require positive date-cluster bootstrap lower bound, "
            "else NO TRADE. Candidate admission is stateful and backfills blocked active names."
        ),
        "diagnostics": diag,
        "result": result,
    }
    if not pit:
        report["warning"] = "Non-PIT smoke result only. No production or profitability claim allowed."
    out = Path(args.result_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out / "summary.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    pred.to_csv(out / "predictions.csv", index=False)
    trades.to_csv(out / "executable_trades.csv", index=False)
    path.to_csv(out / "portfolio.csv", index=False)
    print(json.dumps(report, ensure_ascii=False, indent=2), flush=True)


if __name__ == "__main__":
    main()
