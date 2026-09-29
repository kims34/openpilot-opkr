"""Recent-regime gate waterfall for the selection-conditioned NetEV challenger.

Diagnostic only. It does not tune thresholds, quantiles, Top-K, features, train
windows, calibration windows, or execution rules. The goal is to explain why
the strongest long-history developmental candidate produces no recent trades.

For each recent OOS window, the waterfall freezes the original decision-time
Top3 by conservative score first, then measures:
  raw predicted mean > 0
  uncertainty/calibration penalty (pred_mean -> netev_low)
  conservative lower NetEV > 0
  normal-market eligibility
  executable fixed-horizon record availability
  stateful final admissions

Blocked slots remain empty. Rank 4+ is never promoted.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from research_v1_context import CONTEXT_FEATURES, add_context
from research_v1_distributional_netev import _fixed_record_map
from research_v1_fixed_horizon_label import add_fixed_horizon_target
from research_v1_market_eligibility import veto_frozen_topk_nonstandard_market
from research_v1_ml import stateful_select_records
from research_v1_selected_calibration import selected_calibration_walk_forward
from research_v1_supervised_cache import load_or_build
from run_research_v1 import load_panel


def _q(s: pd.Series) -> dict:
    x = pd.to_numeric(s, errors="coerce").dropna()
    if x.empty:
        return {"n": 0}
    return {
        "n": int(len(x)),
        "min": float(x.min()),
        "p10": float(x.quantile(0.10)),
        "p25": float(x.quantile(0.25)),
        "median": float(x.quantile(0.50)),
        "p75": float(x.quantile(0.75)),
        "p90": float(x.quantile(0.90)),
        "max": float(x.max()),
        "mean": float(x.mean()),
    }


def _freeze_all_topk(pred: pd.DataFrame, top_k: int) -> pd.DataFrame:
    if pred.empty:
        return pred.copy()
    return (
        pred.sort_values(["decision_date", "netev_low"], ascending=[True, False])
        .groupby("decision_date", group_keys=False)
        .head(int(top_k))
        .copy()
    )


def _window_report(
    pred: pd.DataFrame,
    fixed_map: dict,
    *,
    name: str,
    start: pd.Timestamp | None,
    top_k: int,
) -> dict:
    x = pred.copy()
    if start is not None:
        x = x[pd.to_datetime(x["decision_date"]) >= start].copy()
    if x.empty:
        return {"name": name, "prediction_rows": 0, "test_dates": 0, "final_admissions": 0}

    x["decision_date"] = pd.to_datetime(x["decision_date"])
    x["calibration_penalty"] = x["netev_low"].astype(float) - x["pred_mean"].astype(float)
    frozen = _freeze_all_topk(x, top_k)
    raw_positive = frozen[frozen["pred_mean"] > 0].copy()
    uncertainty_blocked = frozen[(frozen["pred_mean"] > 0) & (frozen["netev_low"] <= 0)].copy()
    lower_positive = frozen[frozen["netev_low"] > 0].copy()

    normal, vetoed, market_diag = veto_frozen_topk_nonstandard_market(lower_positive)

    executable_mask = [
        (pd.Timestamp(d).date(), str(s)) in fixed_map
        for d, s in zip(normal["decision_date"], normal["symbol"])
    ]
    executable = normal.loc[executable_mask].copy() if len(normal) else normal.copy()
    unavailable = normal.loc[[not z for z in executable_mask]].copy() if len(normal) else normal.copy()

    records, selected, selection_diag = stateful_select_records(
        normal, fixed_map, top_k=top_k, threshold=0.0
    )

    dates = int(x["decision_date"].nunique())
    rows_per_stage = {
        "original_topk_rows": int(len(frozen)),
        "raw_pred_mean_positive_rows": int(len(raw_positive)),
        "uncertainty_blocked_rows_pred_mean_pos_but_netev_low_nonpos": int(len(uncertainty_blocked)),
        "conservative_lower_positive_rows": int(len(lower_positive)),
        "market_status_veto_rows": int(len(vetoed)),
        "post_market_gate_rows": int(len(normal)),
        "missing_executable_record_rows": int(len(unavailable)),
        "executable_candidate_rows": int(len(executable)),
        "final_admissions": int(len(records)),
    }
    days_per_stage = {
        "dates_with_raw_pred_mean_positive_topk": int(raw_positive["decision_date"].nunique()) if len(raw_positive) else 0,
        "dates_with_conservative_lower_positive": int(lower_positive["decision_date"].nunique()) if len(lower_positive) else 0,
        "dates_after_market_gate": int(normal["decision_date"].nunique()) if len(normal) else 0,
        "trade_days": int(selected["decision_date"].nunique()) if len(selected) else 0,
    }

    # Attribution is descriptive, not a tuned decision rule.
    raw_pos = rows_per_stage["raw_pred_mean_positive_rows"]
    lower_pos = rows_per_stage["conservative_lower_positive_rows"]
    post_market = rows_per_stage["post_market_gate_rows"]
    final_n = rows_per_stage["final_admissions"]
    if raw_pos == 0:
        dominant = "RAW_ALPHA_NONPOSITIVE_IN_ORIGINAL_TOP3"
    elif lower_pos == 0:
        dominant = "UNCERTAINTY_CALIBRATION_PENALTY_BLOCKS_ALL_RAW_POSITIVE_CANDIDATES"
    elif post_market == 0:
        dominant = "MARKET_STATUS_FAIL_CLOSED_BLOCKS_ALL_CONSERVATIVE_CANDIDATES"
    elif final_n == 0:
        dominant = "EXECUTION_OR_STATEFUL_ADMISSION_BLOCKS_REMAINING_CANDIDATES"
    else:
        dominant = "ADMISSIONS_EXIST"

    return {
        "name": name,
        "start": str(start.date()) if start is not None else None,
        "end": str(x["decision_date"].max().date()),
        "prediction_rows": int(len(x)),
        "test_dates": dates,
        "rows_per_stage": rows_per_stage,
        "days_per_stage": days_per_stage,
        "trade_day_coverage": float(days_per_stage["trade_days"] / dates) if dates else 0.0,
        "dominant_blocker": dominant,
        "distributions": {
            "all_pred_mean": _q(x["pred_mean"]),
            "all_calibration_penalty_netev_low_minus_pred_mean": _q(x["calibration_penalty"]),
            "all_netev_low": _q(x["netev_low"]),
            "original_topk_pred_mean": _q(frozen["pred_mean"]),
            "original_topk_calibration_penalty": _q(frozen["calibration_penalty"]),
            "original_topk_netev_low": _q(frozen["netev_low"]),
        },
        "market_eligibility_diagnostics": market_diag,
        "selection_diagnostics": selection_diag,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cache", default="research_data/marcap_kospi_pit_long")
    ap.add_argument("--supervised-cache", default="research_data/pit_supervised_long_v3_ca_fp")
    ap.add_argument("--result-dir", default="research_results/marcap_pit_recent_gate_diagnostic")
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

    pred, folds = selected_calibration_walk_forward(
        z,
        train_days=args.train_days,
        cal_days=args.cal_days,
        test_days=args.test_days,
        purge_days=args.horizon,
        features=CONTEXT_FEATURES,
        top_k=args.top_k,
    )
    if pred.empty:
        raise RuntimeError("selection-conditioned walk-forward produced no predictions")

    decision_dates = sorted(pd.Timestamp(d) for d in pred["decision_date"].drop_duplicates())
    latest_504_start = decision_dates[max(0, len(decision_dates) - 504)] if decision_dates else None

    windows = {
        "all_oos": None,
        "2022_plus": pd.Timestamp("2022-01-01"),
        "2024_plus": pd.Timestamp("2024-01-01"),
        "latest_504_oos_sessions": latest_504_start,
    }
    reports = {
        name: _window_report(pred, fixed_map, name=name, start=start, top_k=args.top_k)
        for name, start in windows.items()
    }

    yearly = {}
    for year in sorted(pd.to_datetime(pred["decision_date"]).dt.year.unique()):
        yearly[str(int(year))] = _window_report(
            pred[pd.to_datetime(pred["decision_date"]).dt.year == year],
            fixed_map,
            name=str(int(year)),
            start=None,
            top_k=args.top_k,
        )

    report = {
        "evaluation_stage": "DIAGNOSTIC_ONLY_RECENT_GATE_WATERFALL_NO_TUNING",
        "policy_frozen": {
            "model": "all_context_selection_conditioned_q25",
            "top_k": args.top_k,
            "admission": "original_top3_by_netev_low__netev_low_gt_0__normal_market_veto__no_backfill",
            "threshold_changed": False,
            "quantile_changed": False,
            "features_changed": False,
            "promotion_allowed": False,
        },
        "cache_meta": cache_meta,
        "label_diagnostics": label_diag,
        "fold_count": int(len(folds)),
        "windows": reports,
        "yearly": yearly,
        "interpretation_rule": {
            "raw_alpha": "pred_mean <= 0 at original Top3 means the mean model itself sees no positive edge",
            "uncertainty": "pred_mean > 0 but netev_low <= 0 means calibration uncertainty removes the apparent edge; do not loosen q25 just to trade",
            "market_status": "netev_low > 0 but normal-market veto removes it means status/security lineage is the blocker",
            "execution": "post-market candidates with no final admission indicate executable-record or stateful holding constraints",
        },
    }

    out = Path(args.result_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out / "summary.json").write_text(json.dumps(report, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    pred.to_parquet(out / "predictions.parquet", index=False)
    print("RECENT_GATE_DIAGNOSTIC=" + json.dumps(report, ensure_ascii=False, default=str), flush=True)


if __name__ == "__main__":
    main()
