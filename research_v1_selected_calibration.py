"""Selection-conditioned residual calibration challenger.

Developmental challenger only; no promotion can come from this test.
The mean model and q25/q50/q75 targets are unchanged. The only calibration
change is that residual quantiles are estimated from calibration rows that
would have occupied the original top-3 ranks by predicted mean on each
calibration day. This tests winner's-curse / post-selection shift without using
test outcomes or a label-informed test threshold.

Evaluation follows the same strict policy as the long-history reference:
original Top-3 is frozen first; the normal-market eligibility veto is then
applied; blocked slots stay empty and rank 4/5 are never promoted.

No quantile level, Top-K, threshold, train/cal/test window or feature family is
searched in this experiment.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from research_v1_context import CONTEXT_FEATURES, add_context
from research_v1_distributional_long_history import (
    CONTEXT_ONLY,
    _evaluate_selected,
    evaluate_candidate,
)
from research_v1_distributional_netev import (
    Q_HIGH,
    Q_LOW,
    Q_MED,
    _apply_distribution,
    _bucket,
    _fixed_record_map,
    _pipe,
    freeze_original_topk,
)
from research_v1_fixed_horizon_label import add_fixed_horizon_target
from research_v1_market_eligibility import veto_frozen_topk_nonstandard_market
from research_v1_ml import stateful_select_records
from research_v1_supervised_cache import load_or_build
from run_research_v1 import load_panel


def _cluster_bootstrap_q25_diagnostic(frame: pd.DataFrame, *, reps: int = 400) -> dict:
    """Date-cluster bootstrap uncertainty for calibration q25; diagnostic only."""
    if frame.empty:
        return {"rows": 0, "days": 0, "q25": None, "bootstrap_p05": None, "bootstrap_p95": None}
    work = frame[["decision_date", "residual"]].dropna().copy()
    days = list(work["decision_date"].drop_duplicates())
    if not days:
        return {"rows": 0, "days": 0, "q25": None, "bootstrap_p05": None, "bootstrap_p95": None}
    by_day = {d: work.loc[work["decision_date"] == d, "residual"].to_numpy(dtype=float) for d in days}
    rng = np.random.default_rng(20260930)
    qs = []
    for _ in range(int(reps)):
        sampled = rng.choice(days, size=len(days), replace=True)
        vals = np.concatenate([by_day[d] for d in sampled])
        qs.append(float(np.quantile(vals, Q_LOW)))
    return {
        "rows": int(len(work)),
        "days": int(len(days)),
        "q25": float(work["residual"].quantile(Q_LOW)),
        "bootstrap_p05": float(np.quantile(qs, 0.05)),
        "bootstrap_p95": float(np.quantile(qs, 0.95)),
        "bootstrap_width_90": float(np.quantile(qs, 0.95) - np.quantile(qs, 0.05)),
        "reps": int(reps),
        "cluster": "decision_date",
        "diagnostic_only": True,
    }


def _selected_residual_quantiles(cal: pd.DataFrame, top_k: int = 3) -> dict:
    """Estimate residual quantiles on calibration-only predicted-mean Top-K.

    The ranking variable is model prediction only. We deliberately do not use a
    calibration residual-derived lower bound to decide which calibration rows
    enter this estimator, because doing so would make selection depend on the
    same outcomes used to estimate the quantile.
    """
    c = cal[cal["fh_label_available"].fillna(False).astype(bool)].copy()
    c = c[c["pred_mean"].notna() & c["fh_net_return"].notna()].copy()
    if c.empty:
        return {}
    ranked = (
        c.sort_values(["decision_date", "pred_mean"], ascending=[True, False])
        .groupby("decision_date", group_keys=False)
        .head(int(top_k))
        .copy()
    )
    ranked["residual"] = (
        ranked["fh_net_return"].astype(float) - ranked["pred_mean"].astype(float)
    )
    ranked["vol_bucket"] = _bucket(ranked["vol20_rank"])
    global_q = {
        "low": float(ranked["residual"].quantile(Q_LOW)),
        "med": float(ranked["residual"].quantile(Q_MED)),
        "high": float(ranked["residual"].quantile(Q_HIGH)),
        "n": int(len(ranked)),
        "source": "calibration_daily_top3_by_pred_mean",
        "q25_uncertainty": _cluster_bootstrap_q25_diagnostic(ranked),
    }
    out = {"__global__": global_q}
    for name, g in ranked.groupby("vol_bucket"):
        if len(g) < 30:
            out[str(name)] = {
                **global_q,
                "fallback_global": True,
                "bucket_n": int(len(g)),
            }
        else:
            out[str(name)] = {
                "low": float(g["residual"].quantile(Q_LOW)),
                "med": float(g["residual"].quantile(Q_MED)),
                "high": float(g["residual"].quantile(Q_HIGH)),
                "n": int(len(g)),
                "fallback_global": False,
                "source": "calibration_daily_top3_by_pred_mean",
                "q25_uncertainty": _cluster_bootstrap_q25_diagnostic(g),
            }
    return out


def selected_calibration_walk_forward(
    z: pd.DataFrame,
    *,
    train_days: int,
    cal_days: int,
    test_days: int,
    purge_days: int,
    features: list[str],
    top_k: int = 3,
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

        model = _pipe(features)
        model.fit(train[features], train["fh_net_return"].astype(float))
        cal["pred_mean"] = model.predict(cal[features])
        test["pred_mean"] = model.predict(test[features])
        q = _selected_residual_quantiles(cal, top_k=top_k)
        if not q:
            start += test_days
            continue
        test = _apply_distribution(test, q)
        test["model"] = "ridge_selected_top3_residual_q25_v0"
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
            "features": list(features),
            "selection_conditioned_residual_quantiles": q,
        })
        start += test_days
    if not preds:
        return pd.DataFrame(), folds
    return pd.concat(preds, ignore_index=True).sort_values(
        ["decision_date", "score"], ascending=[True, False]
    ), folds


def _evaluate_with_runner(
    z, fixed_map, raw, *, name, features, runner, train_days, cal_days,
    test_days, horizon, top_k,
):
    pred, folds = runner(
        z,
        train_days=train_days,
        cal_days=cal_days,
        test_days=test_days,
        purge_days=horizon,
        features=features,
    )
    if pred.empty:
        empty = {
            "name": name,
            "features": features,
            "error": "no_predictions",
            "folds": folds,
        }
        return empty, pd.DataFrame(), pd.DataFrame()

    eligible = pred[pred["netev_low"] > 0].copy()
    frozen = freeze_original_topk(eligible, top_k)

    records, selected, diag = stateful_select_records(
        frozen, fixed_map, top_k=top_k, threshold=0.0
    )
    reference = _evaluate_selected(raw, pred, records, selected, diag, horizon)

    normal_frozen, vetoed_frozen, gate_diag = veto_frozen_topk_nonstandard_market(frozen)
    gate_records, gate_selected, gate_diag_selection = stateful_select_records(
        normal_frozen, fixed_map, top_k=top_k, threshold=0.0
    )
    gate_result = _evaluate_selected(
        raw, pred, gate_records, gate_selected, gate_diag_selection, horizon
    )
    gate_result["market_eligibility_diagnostics"] = gate_diag
    gate_result["vetoed_frozen_rows"] = int(len(vetoed_frozen))

    result = {
        "name": name,
        "features": features,
        "prediction_rows": int(len(pred)),
        "eligible_lower_bound_positive_rows": int(len(eligible)),
        "frozen_topk_rows": int(len(frozen)),
        **reference,
        "market_eligibility_overlay": gate_result,
        "folds": folds,
    }
    return result, selected, gate_selected


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cache", default="research_data/marcap_kospi_pit_long")
    ap.add_argument("--supervised-cache", default="research_data/pit_supervised_long_v3_ca_fp")
    ap.add_argument("--result-dir", default="research_results/marcap_pit_selected_calibration")
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

    results = {}
    selections = {}
    for family, features in {
        "all_context": CONTEXT_FEATURES,
        "context_only": CONTEXT_ONLY,
    }.items():
        baseline, _, baseline_gate_selected = evaluate_candidate(
            z, fixed_map, raw,
            name=f"{family}_marginal_q25_reference",
            features=features,
            train_days=args.train_days,
            cal_days=args.cal_days,
            test_days=args.test_days,
            horizon=args.horizon,
            top_k=args.top_k,
        )
        challenger, selected, gate_selected = _evaluate_with_runner(
            z, fixed_map, raw,
            name=f"{family}_selection_conditioned_q25",
            features=features,
            runner=lambda zz, **kw: selected_calibration_walk_forward(
                zz, top_k=args.top_k, **kw
            ),
            train_days=args.train_days,
            cal_days=args.cal_days,
            test_days=args.test_days,
            horizon=args.horizon,
            top_k=args.top_k,
        )
        results[family] = {
            "marginal_reference": baseline,
            "selection_conditioned": challenger,
        }
        selections[family] = selected
        selections[f"{family}_selection_conditioned_normal_market"] = gate_selected
        selections[f"{family}_marginal_normal_market"] = baseline_gate_selected

    report = {
        "evaluation_stage": "DEVELOPMENTAL_SELECTION_CONDITIONED_CALIBRATION_CHALLENGER_NOT_HOLDOUT",
        "history_start": str(raw["decision_date"].min().date()),
        "history_end": str(raw["decision_date"].max().date()),
        "protocol": {
            "quantile_levels_changed": False,
            "q_low": Q_LOW,
            "calibration_selection": "daily_top3_by_pred_mean_on_calibration_only",
            "calibration_test_outcome_leakage": False,
            "test_admission": "netev_low_gt_0__freeze_original_top3__no_backfill",
            "market_eligibility_overlay": (
                "post_rank_hard_veto_if_abs_decision_day_KRX_base_return_gt_30.5pct__no_backfill"
            ),
            "hyperparameter_search": False,
            "promotion_allowed": False,
        },
        "supervised_cache": cache_meta,
        "label_diagnostics": label_diag,
        "results": results,
        "guardrail": (
            "This is a development test motivated by diagnosed post-selection calibration failure. "
            "Any improvement must later survive a sealed holdout and prospective Shadow."
        ),
    }
    out = Path(args.result_dir)
    out.mkdir(parents=True, exist_ok=True)
    encoded = json.dumps(report, ensure_ascii=False, indent=2, default=str)
    (out / "summary.json").write_text(encoded, encoding="utf-8")
    for family, selected in selections.items():
        selected.to_csv(out / f"{family}_selected.csv", index=False)
    print("SELECTED_CALIBRATION=" + json.dumps(report, ensure_ascii=False, default=str), flush=True)


if __name__ == "__main__":
    main()