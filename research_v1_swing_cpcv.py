"""Purged CPCV robustness diagnostic for Short H5 and Swing H10.

This module is deliberately separate from the production and anchored
walk-forward paths.  CPCV folds may train on observations later than a test
block, so their results are a model-stability diagnostic only; they are never
deployment simulation, sealed holdout evidence, or promotion evidence.

Frozen comparison contract:
- H5 is the unchanged Short reference; H10 is the only Swing challenger.
- identical PIT/CA-safe panel, feature family, cost model and admission policy
- six contiguous date groups, two test groups per combination
- each of the four remaining groups serves once as independent residual calibration
- training observations purged around both test and calibration label windows
- original Top3 freeze, post-rank normal-market veto, no backfill
"""
from __future__ import annotations

import argparse
import itertools
import json
from pathlib import Path

import numpy as np
import pandas as pd

from research_v1_context import CONTEXT_FEATURES, add_context
from research_v1_distributional_netev import (
    _apply_distribution,
    _fixed_record_map,
    _pipe,
)
from research_v1_fixed_horizon_label import add_fixed_horizon_target
from research_v1_selected_calibration import (
    _evaluate_with_runner,
    _selected_residual_quantiles,
)
from research_v1_supervised_cache import load_or_build
from research_v1_swing_challenger import _comparison_view
from run_research_v1 import load_panel

ALLOWED_HORIZONS = (5, 10)
CPCV_GROUPS = 6
CPCV_TEST_GROUPS = 2
MIN_TRAIN_DAYS = 504
CAL_DAYS = 126
TOP_K = 3


def _blocked_by_label_overlap(
    candidate_positions: set[int],
    protected_positions: set[int],
    horizon: int,
) -> set[int]:
    """Conservatively purge positions whose outcome windows can overlap."""
    if not candidate_positions or not protected_positions:
        return set()
    blocked = set()
    for pos in candidate_positions:
        if any(abs(pos - other) <= horizon for other in protected_positions):
            blocked.add(pos)
    return blocked


def cpcv_assignments(
    dates,
    *,
    horizon: int,
    n_groups: int = CPCV_GROUPS,
    n_test_groups: int = CPCV_TEST_GROUPS,
    cal_days: int = CAL_DAYS,
):
    """Create deterministic, group-disjoint CPCV train/cal/test assignments."""
    if horizon not in ALLOWED_HORIZONS:
        raise ValueError(f"horizon must be one of {ALLOWED_HORIZONS}")
    ordered = [pd.Timestamp(x) for x in sorted(set(dates))]
    if len(ordered) < n_groups:
        raise ValueError("not enough dates for CPCV groups")
    groups = [list(map(int, x)) for x in np.array_split(np.arange(len(ordered)), n_groups)]
    assignments = []
    all_positions = set(range(len(ordered)))
    split_id = 0
    for test_group_ids in itertools.combinations(range(n_groups), n_test_groups):
        remaining = [g for g in range(n_groups) if g not in test_group_ids]
        test_positions = set().union(*(set(groups[g]) for g in test_group_ids))
        for cal_group_id in remaining:
            cal_group_positions = groups[cal_group_id]
            cal_positions = set(cal_group_positions[-min(cal_days, len(cal_group_positions)):])
            excluded_groups = set(test_group_ids) | {cal_group_id}
            train_positions = set().union(
                *(set(groups[g]) for g in range(n_groups) if g not in excluded_groups)
            )
            protected = test_positions | cal_positions
            train_positions -= _blocked_by_label_overlap(train_positions, protected, horizon)
            train_positions &= all_positions - test_positions - set(cal_group_positions)
            assignments.append({
                "split_id": int(split_id),
                "test_group_ids": list(map(int, test_group_ids)),
                "cal_group_id": int(cal_group_id),
                "train_dates": [ordered[i] for i in sorted(train_positions)],
                "cal_dates": [ordered[i] for i in sorted(cal_positions)],
                "test_dates": [ordered[i] for i in sorted(test_positions)],
                "purge_days": int(horizon),
            })
            split_id += 1
    return assignments


def cpcv_prediction_splits(
    z: pd.DataFrame,
    *,
    horizon: int,
    features: list[str],
    top_k: int = TOP_K,
):
    dates = sorted(pd.Timestamp(x) for x in z["decision_date"].drop_duplicates())
    outputs = []
    for assignment in cpcv_assignments(dates, horizon=horizon):
        train_dates = assignment["train_dates"]
        cal_dates = assignment["cal_dates"]
        test_dates = assignment["test_dates"]
        if len(train_dates) < MIN_TRAIN_DAYS or len(cal_dates) < CAL_DAYS:
            continue
        train = z[z["decision_date"].isin(train_dates)].copy()
        cal = z[z["decision_date"].isin(cal_dates)].copy()
        test = z[z["decision_date"].isin(test_dates)].copy()
        train = train[train["fh_label_available"].fillna(False).astype(bool)].copy()
        cal = cal[cal["fh_label_available"].fillna(False).astype(bool)].copy()
        if train.empty or cal.empty or test.empty:
            continue
        model = _pipe(features)
        model.fit(train[features], train["fh_net_return"].astype(float))
        cal["pred_mean"] = model.predict(cal[features])
        test["pred_mean"] = model.predict(test[features])
        quantiles = _selected_residual_quantiles(cal, top_k=top_k)
        if not quantiles:
            continue
        pred = _apply_distribution(test, quantiles)
        pred["model"] = "ridge_selected_top3_residual_q25_cpcv_diagnostic"
        pred["cpcv_split_id"] = assignment["split_id"]
        meta = {
            **{k: v for k, v in assignment.items() if not k.endswith("_dates")},
            "train_start": str(train_dates[0].date()),
            "train_end": str(train_dates[-1].date()),
            "cal_start": str(cal_dates[0].date()),
            "cal_end": str(cal_dates[-1].date()),
            "test_start": str(test_dates[0].date()),
            "test_end": str(test_dates[-1].date()),
            "train_days": int(len(train_dates)),
            "cal_days": int(len(cal_dates)),
            "test_days": int(len(test_dates)),
            "selection_conditioned_residual_quantiles": quantiles,
        }
        outputs.append((pred, meta))
    return outputs


def _distribution(rows: list[dict], key: str) -> dict:
    values = np.asarray([float(r[key]) for r in rows], dtype=float)
    if len(values) == 0:
        return {"n": 0, "min": 0.0, "p25": 0.0, "median": 0.0, "p75": 0.0, "max": 0.0}
    return {
        "n": int(len(values)),
        "min": float(np.min(values)),
        "p25": float(np.quantile(values, 0.25)),
        "median": float(np.median(values)),
        "p75": float(np.quantile(values, 0.75)),
        "max": float(np.max(values)),
    }


def aggregate_cpcv_views(views: list[dict]) -> dict:
    keys = [
        "precision_at_selected",
        "fixed_participation_cost_proxy_mean_net_return",
        "profit_factor",
        "mdd",
        "es95",
        "es99",
        "date_cluster_lcb95",
    ]
    out = {key: _distribution(views, key) for key in keys}
    out["splits_evaluated"] = int(len(views))
    out["fraction_positive_net_ev"] = float(np.mean([
        v["fixed_participation_cost_proxy_mean_net_return"] > 0.0 for v in views
    ])) if views else 0.0
    out["fraction_pf_gt_1"] = float(np.mean([
        v["profit_factor"] > 1.0 for v in views
    ])) if views else 0.0
    out["fraction_positive_cluster_lcb"] = float(np.mean([
        v["date_cluster_lcb95"] > 0.0 for v in views
    ])) if views else 0.0
    return out


def run_cpcv(raw, supervised_cache: Path, horizon: int):
    frame, legacy_map, label_diag, cache_meta = load_or_build(
        raw,
        supervised_cache,
        horizon=horizon,
        target_return=0.04,
        stop_return=-0.025,
        participation=0.0005,
        commission_round_trip_bps=3.0,
    )
    frame = frame[frame["adv20_rank"] >= 0.20].copy().reset_index(drop=True)
    z = add_fixed_horizon_target(raw, add_context(frame), legacy_map, horizon)
    fixed_map = _fixed_record_map(z, horizon)
    split_predictions = cpcv_prediction_splits(
        z, horizon=horizon, features=CONTEXT_FEATURES, top_k=TOP_K
    )
    split_reports = []
    views = []
    for pred, meta in split_predictions:
        result, _, _ = _evaluate_with_runner(
            z,
            fixed_map,
            raw,
            name=f"{'short_h5' if horizon == 5 else 'swing_h10'}_cpcv_split_{meta['split_id']}",
            features=CONTEXT_FEATURES,
            runner=lambda _z, _pred=pred, _meta=meta, **_kw: (_pred, [_meta]),
            train_days=MIN_TRAIN_DAYS,
            cal_days=CAL_DAYS,
            test_days=0,
            horizon=horizon,
            top_k=TOP_K,
        )
        view = _comparison_view(result)
        views.append(view)
        split_reports.append({"split": meta, "comparison_view": view})
    aggregate = aggregate_cpcv_views(views)
    return {
        "evaluation_stage": "PURGED_CPCV_ROBUSTNESS_DIAGNOSTIC_NOT_DEPLOYMENT_NOT_HOLDOUT",
        "strategy": "SHORT_REFERENCE" if horizon == 5 else "SWING_CHALLENGER",
        "horizon_sessions": int(horizon),
        "short_strategy_modified": False,
        "protocol": {
            "groups": CPCV_GROUPS,
            "test_groups_per_combination": CPCV_TEST_GROUPS,
            "test_combinations": 15,
            "calibration_assignments_per_test_combination": 4,
            "expected_assignments": 60,
            "purge_equals_horizon": True,
            "calibration_group_disjoint": True,
            "selection_conditioned_q25": True,
            "same_pit_features_and_cost_model": True,
            "traditional_cpcv_can_use_future_training_relative_to_test": True,
            "deployment_or_promotion_evidence": False,
            "sealed_holdout_burned": False,
        },
        "supervised_cache": cache_meta,
        "label_diagnostics": label_diag,
        "aggregate": aggregate,
        "splits": split_reports,
        "verdict": "CPCV_STABILITY_DIAGNOSTIC_ONLY_NO_PROMOTION_VERDICT",
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cache", default="research_data/marcap_kospi_pit_long")
    ap.add_argument("--supervised-cache", required=True)
    ap.add_argument("--result-dir", required=True)
    ap.add_argument("--horizon", type=int, required=True, choices=ALLOWED_HORIZONS)
    args = ap.parse_args()
    raw = load_panel(Path(args.cache))
    report = run_cpcv(raw, Path(args.supervised_cache), args.horizon)
    out = Path(args.result_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out / "summary.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2, default=str),
        encoding="utf-8",
    )
    print("SWING_CPCV=" + json.dumps(report, ensure_ascii=False, default=str), flush=True)


if __name__ == "__main__":
    main()

