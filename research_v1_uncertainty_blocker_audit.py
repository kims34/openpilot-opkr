"""Audit whether the recent q25 uncertainty veto is protective or over-conservative.

Diagnostic only. This script keeps the selection-conditioned model, features,
windows, q25 target, Top3 rule and costs frozen. It observes the historical
fixed-horizon outcomes of:
  * original Top3 by conservative NetEV score,
  * original Top3 with pred_mean > 0,
  * the subset blocked only because pred_mean > 0 but netev_low <= 0,
  * conservative lower-bound-positive names before market-status veto.

No result from this audit changes the admission threshold. Its purpose is to
decide whether a conditional q25 estimator is worth testing as a challenger.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from research_v1_context import CONTEXT_FEATURES, add_context
from research_v1_fixed_horizon_label import add_fixed_horizon_target
from research_v1_selected_calibration import selected_calibration_walk_forward
from research_v1_supervised_cache import load_or_build
from run_research_v1 import load_panel


def _freeze_topk(pred: pd.DataFrame, top_k: int) -> pd.DataFrame:
    if pred.empty:
        return pred.copy()
    return (
        pred.sort_values(["decision_date", "netev_low"], ascending=[True, False])
        .groupby("decision_date", group_keys=False)
        .head(int(top_k))
        .copy()
    )


def _cluster_ci(frame: pd.DataFrame, n_boot: int = 3000, seed: int = 1729) -> dict:
    x = frame.dropna(subset=["fh_net_return"]).copy()
    if x.empty:
        return {"point": None, "low": None, "high": None, "date_clusters": 0}
    x["decision_date"] = pd.to_datetime(x["decision_date"]).dt.date
    by_day = x.groupby("decision_date")["fh_net_return"].apply(lambda s: s.to_numpy(dtype=float))
    days = list(by_day.index)
    arrays = [by_day.loc[d] for d in days]
    point = float(np.concatenate(arrays).mean())
    rng = np.random.default_rng(seed)
    vals = np.empty(n_boot, dtype=float)
    n = len(arrays)
    for i in range(n_boot):
        idx = rng.integers(0, n, size=n)
        vals[i] = float(np.concatenate([arrays[j] for j in idx]).mean())
    return {
        "point": point,
        "low": float(np.quantile(vals, 0.025)),
        "high": float(np.quantile(vals, 0.975)),
        "date_clusters": int(n),
    }


def _basic(frame: pd.DataFrame) -> dict:
    x = pd.to_numeric(frame.get("fh_net_return", pd.Series(dtype=float)), errors="coerce").dropna().to_numpy(dtype=float)
    if len(x) == 0:
        return {
            "rows": int(len(frame)), "realised_rows": 0, "mean_net_return": None,
            "median_net_return": None, "positive_rate": None, "profit_factor": None,
            "expected_shortfall_5pct": None, "cluster_bootstrap_95": _cluster_ci(frame),
        }
    gains = float(x[x > 0].sum())
    losses = float(-x[x < 0].sum())
    k = max(1, int(np.ceil(0.05 * len(x))))
    es = float(np.sort(x)[:k].mean())
    return {
        "rows": int(len(frame)),
        "realised_rows": int(len(x)),
        "mean_net_return": float(x.mean()),
        "median_net_return": float(np.median(x)),
        "positive_rate": float((x > 0).mean()),
        "profit_factor": float(gains / losses) if losses > 0 else (float("inf") if gains > 0 else 0.0),
        "expected_shortfall_5pct": es,
        "cluster_bootstrap_95": _cluster_ci(frame),
    }


def _extreme_day_robustness(frame: pd.DataFrame) -> dict:
    x = frame.dropna(subset=["fh_net_return"]).copy()
    if x.empty:
        return {}
    x["decision_date"] = pd.to_datetime(x["decision_date"]).dt.date
    day_mean = x.groupby("decision_date")["fh_net_return"].mean().sort_values(ascending=False)
    out = {}
    for n_remove in (1, 3, 5):
        drop_days = set(day_mean.head(min(n_remove, len(day_mean))).index)
        kept = x[~x["decision_date"].isin(drop_days)].copy()
        out[f"remove_best_{n_remove}_days"] = {
            "removed_days": [str(d) for d in list(day_mean.head(min(n_remove, len(day_mean))).index)],
            **_basic(kept),
        }
    return out


def _stage_report(frame: pd.DataFrame) -> dict:
    return {**_basic(frame), "extreme_day_robustness": _extreme_day_robustness(frame)}


def _window(pred: pd.DataFrame, start: pd.Timestamp | None, top_k: int) -> dict:
    x = pred.copy()
    x["decision_date"] = pd.to_datetime(x["decision_date"])
    if start is not None:
        x = x[x["decision_date"] >= start].copy()
    frozen = _freeze_topk(x, top_k)
    raw_pos = frozen[frozen["pred_mean"] > 0].copy()
    uncertainty_blocked = frozen[(frozen["pred_mean"] > 0) & (frozen["netev_low"] <= 0)].copy()
    lower_pos = frozen[frozen["netev_low"] > 0].copy()
    return {
        "start": str(start.date()) if start is not None else None,
        "end": str(x["decision_date"].max().date()) if len(x) else None,
        "test_dates": int(x["decision_date"].nunique()),
        "original_top3": _stage_report(frozen),
        "raw_pred_mean_positive_top3": _stage_report(raw_pos),
        "uncertainty_blocked_raw_positive_top3": _stage_report(uncertainty_blocked),
        "conservative_lower_positive_top3": _stage_report(lower_pos),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cache", default="research_data/marcap_kospi_pit_long")
    ap.add_argument("--supervised-cache", default="research_data/pit_supervised_long_v3_ca_fp")
    ap.add_argument("--result-dir", default="research_results/marcap_pit_uncertainty_blocker_audit")
    ap.add_argument("--horizon", type=int, default=5)
    ap.add_argument("--top-k", type=int, default=3)
    ap.add_argument("--train-days", type=int, default=504)
    ap.add_argument("--cal-days", type=int, default=126)
    ap.add_argument("--test-days", type=int, default=126)
    args = ap.parse_args()

    raw = load_panel(Path(args.cache))
    frame, legacy_map, diag, meta = load_or_build(
        raw, Path(args.supervised_cache),
        horizon=args.horizon, target_return=0.04, stop_return=-0.025,
        participation=0.0005, commission_round_trip_bps=3.0,
    )
    frame = frame[frame["adv20_rank"] >= 0.20].copy().reset_index(drop=True)
    z = add_fixed_horizon_target(raw, add_context(frame), legacy_map, args.horizon)
    pred, folds = selected_calibration_walk_forward(
        z, train_days=args.train_days, cal_days=args.cal_days,
        test_days=args.test_days, purge_days=args.horizon,
        features=CONTEXT_FEATURES, top_k=args.top_k,
    )
    if pred.empty:
        raise RuntimeError("selection-conditioned walk-forward produced no predictions")

    dates = sorted(pd.Timestamp(d) for d in pred["decision_date"].drop_duplicates())
    latest_504 = dates[max(0, len(dates) - 504)] if dates else None
    windows = {
        "all_oos": None,
        "2022_plus": pd.Timestamp("2022-01-01"),
        "2024_plus": pd.Timestamp("2024-01-01"),
        "latest_504_oos_sessions": latest_504,
    }
    report = {
        "evaluation_stage": "DIAGNOSTIC_ONLY_UNCERTAINTY_BLOCKER_REALIZED_OUTCOMES_NO_TUNING",
        "policy_frozen": {
            "model": "all_context_selection_conditioned_q25",
            "top_k": args.top_k,
            "q25_changed": False,
            "threshold_changed": False,
            "features_changed": False,
            "promotion_allowed": False,
        },
        "cache_meta": meta,
        "label_diagnostics": diag,
        "fold_count": int(len(folds)),
        "windows": {k: _window(pred, v, args.top_k) for k, v in windows.items()},
        "decision_rule_for_next_research": {
            "if_blocked_subset_mean_and_pf_are_weak": "KEEP_ABSTENTION; do not weaken q25; seek orthogonal information",
            "if_blocked_subset_mean_and_pf_are_positive_but_tail_is_wide": "TEST_CONDITIONAL_Q25_MODEL at the same 25th-percentile target; do not change admission threshold",
            "if_positive_only_depends_on_best_days": "REJECT apparent edge as jackpot-dependent",
        },
    }
    out = Path(args.result_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out / "summary.json").write_text(json.dumps(report, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    print("UNCERTAINTY_BLOCKER_AUDIT=" + json.dumps(report, ensure_ascii=False, default=str), flush=True)


if __name__ == "__main__":
    main()
