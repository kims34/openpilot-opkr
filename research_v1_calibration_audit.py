"""Calibration reliability audit for CA-safe Distributional NetEV.

This is diagnostic only. It does not tune thresholds or promote a model.
It tests whether the current residual-q25/q50/q75 construction is calibrated
marginally and after the actual strict-Top3 selection policy.

Important semantics:
- netev_low is a predictive residual q25 estimate, NOT a confidence bound on
  expected return and NOT a finite-sample conformal guarantee.
- Under stable calibration, P(actual >= netev_low) should be about 75%
  marginally. Selection can break that coverage.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from research_v1_context import CONTEXT_FEATURES, add_context
from research_v1_distributional_long_history import CONTEXT_ONLY
from research_v1_distributional_netev import (
    _fixed_record_map,
    distributional_walk_forward,
    freeze_original_topk,
)
from research_v1_fixed_horizon_label import add_fixed_horizon_target
from research_v1_ml import stateful_select_records
from research_v1_supervised_cache import load_or_build
from run_research_v1 import load_panel


def _profit_factor(x: pd.Series) -> float:
    v = pd.to_numeric(x, errors="coerce").dropna().to_numpy(dtype=float)
    if len(v) == 0:
        return 0.0
    gains = float(v[v > 0].sum())
    losses = float(-v[v < 0].sum())
    if losses > 0:
        return gains / losses
    return float("inf") if gains > 0 else 0.0


def _summary(g: pd.DataFrame) -> dict:
    if g.empty:
        return {"n": 0}
    actual = pd.to_numeric(g["fh_net_return"], errors="coerce")
    low = pd.to_numeric(g["netev_low"], errors="coerce")
    high = pd.to_numeric(g["netev_high"], errors="coerce")
    valid = actual.notna() & low.notna() & high.notna()
    actual, low, high = actual[valid], low[valid], high[valid]
    if len(actual) == 0:
        return {"n": 0}
    shortfall = actual - low
    return {
        "n": int(len(actual)),
        "actual_ge_low_coverage": float((actual >= low).mean()),
        "inside_q25_q75_coverage": float(((actual >= low) & (actual <= high)).mean()),
        "mean_actual_net_return": float(actual.mean()),
        "median_actual_net_return": float(actual.median()),
        "positive_rate": float((actual > 0).mean()),
        "profit_factor": float(_profit_factor(actual)),
        "actual_q01": float(actual.quantile(0.01)),
        "actual_q05": float(actual.quantile(0.05)),
        "actual_q25": float(actual.quantile(0.25)),
        "mean_netev_low": float(low.mean()),
        "median_netev_low": float(low.median()),
        "mean_actual_minus_low": float(shortfall.mean()),
        "q05_actual_minus_low": float(shortfall.quantile(0.05)),
        "worst_actual_minus_low": float(shortfall.min()),
    }


def _group_table(df: pd.DataFrame, column: str) -> dict:
    if df.empty or column not in df.columns:
        return {}
    out = {}
    for key, g in df.groupby(column, dropna=False):
        out[str(key)] = _summary(g)
    return out


def _score_deciles(realised: pd.DataFrame) -> pd.Series:
    # Rank-based deciles avoid duplicate-edge failures from qcut and are purely
    # diagnostic; they do not become a trading threshold.
    pct = realised["netev_low"].rank(method="average", pct=True)
    d = np.ceil(pct * 10).clip(1, 10).astype("Int64")
    return d.astype(str)


def _attach_selected(realised: pd.DataFrame, selected: pd.DataFrame) -> pd.DataFrame:
    out = realised.copy()
    if selected.empty:
        out["selected_stateful"] = False
        return out
    keys = set(
        zip(
            pd.to_datetime(selected["decision_date"]).dt.date,
            selected["symbol"].astype(str),
        )
    )
    out["selected_stateful"] = [
        (pd.Timestamp(d).date(), str(s)) in keys
        for d, s in zip(out["decision_date"], out["symbol"])
    ]
    return out


def audit_model(
    z: pd.DataFrame,
    fixed_map: dict,
    *,
    name: str,
    features: list[str],
    train_days: int,
    cal_days: int,
    test_days: int,
    horizon: int,
    top_k: int,
):
    pred, folds = distributional_walk_forward(
        z,
        train_days=train_days,
        cal_days=cal_days,
        test_days=test_days,
        purge_days=horizon,
        features=features,
    )
    if pred.empty:
        return {"name": name, "error": "no_predictions"}, pred, pd.DataFrame()

    realised = pred[pred["fh_label_available"].fillna(False).astype(bool)].copy()
    realised["decision_date"] = pd.to_datetime(realised["decision_date"])
    realised["year"] = realised["decision_date"].dt.year
    realised["score_decile"] = _score_deciles(realised)
    realised["fold_id"] = (
        realised["train_end"].astype(str)
        + "__"
        + realised["cal_end"].astype(str)
    )
    realised["eligible"] = realised["netev_low"] > 0

    eligible = realised[realised["eligible"]].copy()
    frozen = freeze_original_topk(eligible, top_k)
    frozen_keys = set(
        zip(pd.to_datetime(frozen["decision_date"]).dt.date, frozen["symbol"].astype(str))
    )
    realised["frozen_topk"] = [
        (d.date(), str(s)) in frozen_keys
        for d, s in zip(realised["decision_date"], realised["symbol"])
    ]

    records, selected, selection_diag = stateful_select_records(
        frozen, fixed_map, top_k=top_k, threshold=0.0,
    )
    realised = _attach_selected(realised, selected)

    selected_rows = realised[realised["selected_stateful"]].copy()
    frozen_rows = realised[realised["frozen_topk"]].copy()

    report = {
        "name": name,
        "semantics": {
            "netev_low": "predicted_mean_plus_calibration_residual_q25",
            "nominal_marginal_actual_ge_low": 0.75,
            "nominal_q25_q75_interval_coverage": 0.50,
            "confidence_bound_on_mean": False,
            "finite_sample_conformal_guarantee": False,
        },
        "prediction_rows": int(len(pred)),
        "realised_rows": int(len(realised)),
        "eligible_rows": int(realised["eligible"].sum()),
        "frozen_topk_rows": int(realised["frozen_topk"].sum()),
        "selected_rows": int(realised["selected_stateful"].sum()),
        "selection_diagnostics": selection_diag,
        "marginal_all_realised": _summary(realised),
        "eligible_netev_low_gt_0": _summary(eligible),
        "frozen_original_topk": _summary(frozen_rows),
        "stateful_selected": _summary(selected_rows),
        "selected_by_year": _group_table(selected_rows, "year"),
        "selected_by_vol_bucket": _group_table(selected_rows, "vol_bucket"),
        "selected_by_score_decile": _group_table(selected_rows, "score_decile"),
        "selected_by_fold": _group_table(selected_rows, "fold_id"),
        "all_by_year": _group_table(realised, "year"),
        "all_by_vol_bucket": _group_table(realised, "vol_bucket"),
        "all_by_score_decile": _group_table(realised, "score_decile"),
        "folds": folds,
    }
    sc = report["stateful_selected"]
    report["selection_conditional_calibration_pass"] = bool(
        sc.get("n", 0) >= 50
        and sc.get("actual_ge_low_coverage", 0.0) >= 0.70
        and sc.get("mean_actual_net_return", 0.0) > 0.0
        and sc.get("profit_factor", 0.0) > 1.0
    )
    return report, pred, selected


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cache", default="research_data/marcap_kospi_pit_long")
    ap.add_argument("--supervised-cache", default="research_data/pit_supervised_long_v2_ca")
    ap.add_argument("--result-dir", default="research_results/marcap_pit_calibration_audit")
    ap.add_argument("--horizon", type=int, default=5)
    ap.add_argument("--top-k", type=int, default=3)
    ap.add_argument("--train-days", type=int, default=504)
    ap.add_argument("--cal-days", type=int, default=126)
    ap.add_argument("--test-days", type=int, default=126)
    args = ap.parse_args()

    raw = load_panel(Path(args.cache))
    frame, legacy_map, label_diag, cache_meta = load_or_build(
        raw,
        Path(args.supervised_cache),
        horizon=args.horizon,
        target_return=0.04,
        stop_return=-0.025,
        participation=0.0005,
        commission_round_trip_bps=3.0,
    )
    frame = frame[frame["adv20_rank"] >= 0.20].copy().reset_index(drop=True)
    context = add_context(frame)
    z = add_fixed_horizon_target(raw, context, legacy_map, args.horizon)
    fixed_map = _fixed_record_map(z, args.horizon)

    models = {}
    outputs = {}
    for name, features in {
        "all_context_reference": CONTEXT_FEATURES,
        "context_only_challenger": CONTEXT_ONLY,
    }.items():
        report, pred, selected = audit_model(
            z,
            fixed_map,
            name=name,
            features=features,
            train_days=args.train_days,
            cal_days=args.cal_days,
            test_days=args.test_days,
            horizon=args.horizon,
            top_k=args.top_k,
        )
        models[name] = report
        outputs[name] = (pred, selected)

    final = {
        "evaluation_stage": "LONG_HISTORY_CA_SAFE_CALIBRATION_AUDIT_DIAGNOSTIC_ONLY",
        "history_start": str(raw["decision_date"].min().date()),
        "history_end": str(raw["decision_date"].max().date()),
        "protocol": {
            "train_days_initial": args.train_days,
            "cal_days": args.cal_days,
            "test_days": args.test_days,
            "purge_days": args.horizon,
            "top_k": args.top_k,
            "liquidity_floor": "adv20_rank_ge_0.20",
            "threshold_tuning_from_audit": False,
        },
        "supervised_cache": cache_meta,
        "label_diagnostics": label_diag,
        "models": models,
        "interpretation_guardrail": (
            "A q25 residual forecast is a predictive quantile proxy, not a confidence lower bound on expected NetEV. "
            "Do not tune admission thresholds from this audit; diagnose calibration drift and selection effects first."
        ),
    }
    final["verdict"] = (
        "CURRENT_CALIBRATION_NOT_RELIABLE_FOR_ADMISSION"
        if not all(m.get("selection_conditional_calibration_pass", False) for m in models.values())
        else "SELECTION_CONDITIONAL_CALIBRATION_PRELIMINARILY_ACCEPTABLE"
    )

    out = Path(args.result_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out / "summary.json").write_text(json.dumps(final, ensure_ascii=False, indent=2), encoding="utf-8")
    for name, (pred, selected) in outputs.items():
        pred.to_parquet(out / f"{name}_predictions.parquet", index=False)
        selected.to_csv(out / f"{name}_selected.csv", index=False)
    print("CALIBRATION_AUDIT=" + json.dumps(final, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
