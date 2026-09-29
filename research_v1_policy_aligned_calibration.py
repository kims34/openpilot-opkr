"""Preregistered policy-aligned calibration population challenger.

EXP-2026-09-29-POLICY-CAL-01.
Developmental diagnostic only; this cannot promote a model.

Only change versus the existing selection-conditioned residual calibration:
1. freeze each calibration day's Top-K by pred_mean exactly as before;
2. apply the same decision-time normal-market fail-closed veto to those frozen
   calibration rows;
3. blocked calibration slots stay empty; rank K+1 is never backfilled;
4. estimate the same q25/q50/q75 residual quantiles from the remaining rows.

The mean model, feature family, q levels, Top-K, train/cal/test windows, purge,
costs, test-time veto and admission netev_low > 0 are unchanged.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from research_v1_context import CONTEXT_FEATURES, add_context
from research_v1_distributional_netev import (
    Q_HIGH,
    Q_LOW,
    Q_MED,
    _apply_distribution,
    _bucket,
    _fixed_record_map,
    _pipe,
)
from research_v1_fixed_horizon_label import add_fixed_horizon_target
from research_v1_market_eligibility import veto_frozen_topk_nonstandard_market
from research_v1_selected_calibration import (
    _cluster_bootstrap_q25_diagnostic,
    _evaluate_with_runner,
    selected_calibration_walk_forward,
)
from research_v1_supervised_cache import load_or_build
from run_research_v1 import load_panel


def _policy_aligned_residual_quantiles(cal: pd.DataFrame, top_k: int = 3) -> tuple[dict, dict]:
    """Residual quantiles from frozen calibration Top-K after the policy veto."""
    c = cal[cal["fh_label_available"].fillna(False).astype(bool)].copy()
    c = c[c["pred_mean"].notna() & c["fh_net_return"].notna()].copy()
    if c.empty:
        return {}, {"error": "empty_calibration"}

    frozen = (
        c.sort_values(["decision_date", "pred_mean"], ascending=[True, False])
        .groupby("decision_date", group_keys=False)
        .head(int(top_k))
        .copy()
    )
    # This is exactly the same PIT decision-time market-state veto used at test
    # time.  Crucially, the rank is frozen before vetoing; there is no backfill.
    eligible, vetoed, gate_diag = veto_frozen_topk_nonstandard_market(frozen)
    ranked = eligible.copy()
    if ranked.empty:
        return {}, {**gate_diag, "error": "all_frozen_calibration_rows_vetoed"}

    ranked["residual"] = (
        ranked["fh_net_return"].astype(float) - ranked["pred_mean"].astype(float)
    )
    ranked["vol_bucket"] = _bucket(ranked["vol20_rank"])

    global_q = {
        "low": float(ranked["residual"].quantile(Q_LOW)),
        "med": float(ranked["residual"].quantile(Q_MED)),
        "high": float(ranked["residual"].quantile(Q_HIGH)),
        "n": int(len(ranked)),
        "source": "calibration_daily_top3_by_pred_mean_then_same_normal_market_veto_no_backfill",
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
                "source": "calibration_daily_top3_by_pred_mean_then_same_normal_market_veto_no_backfill",
                "q25_uncertainty": _cluster_bootstrap_q25_diagnostic(g),
            }
    diag = {
        **gate_diag,
        "frozen_rows": int(len(frozen)),
        "policy_eligible_rows": int(len(ranked)),
        "vetoed_rows": int(len(vetoed)),
        "quantile_levels": [Q_LOW, Q_MED, Q_HIGH],
        "backfill_allowed": False,
    }
    return out, diag


def policy_aligned_calibration_walk_forward(
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
        q, cal_policy_diag = _policy_aligned_residual_quantiles(cal, top_k=top_k)
        if not q:
            start += test_days
            continue
        test = _apply_distribution(test, q)
        test["model"] = "ridge_policy_aligned_selected_top3_residual_q25_v0"
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
            "policy_aligned_residual_quantiles": q,
            "calibration_policy_diagnostics": cal_policy_diag,
        })
        start += test_days

    if not preds:
        return pd.DataFrame(), folds
    return pd.concat(preds, ignore_index=True).sort_values(
        ["decision_date", "score"], ascending=[True, False]
    ), folds


def _compact(result: dict) -> dict:
    gate = result.get("market_eligibility_overlay", {})
    keys = [
        "trade_count", "trade_days", "mean_net_return", "profit_factor",
        "cluster_bootstrap_95", "expected_shortfall_95", "expected_shortfall_99",
        "portfolio", "cost_stress", "extreme_day_robustness",
    ]
    return {k: gate.get(k) for k in keys if k in gate}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cache", default="research_data/marcap_kospi_pit_long")
    ap.add_argument("--supervised-cache", default="research_data/pit_supervised_long_v3_ca_fp")
    ap.add_argument("--result-dir", default="research_results/marcap_pit_policy_aligned_calibration")
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

    reference, _, reference_gate_selected = _evaluate_with_runner(
        z, fixed_map, raw,
        name="all_context_selection_conditioned_q25_reference",
        features=CONTEXT_FEATURES,
        runner=lambda zz, **kw: selected_calibration_walk_forward(
            zz, top_k=args.top_k, **kw
        ),
        train_days=args.train_days,
        cal_days=args.cal_days,
        test_days=args.test_days,
        horizon=args.horizon,
        top_k=args.top_k,
    )
    challenger, _, challenger_gate_selected = _evaluate_with_runner(
        z, fixed_map, raw,
        name="all_context_policy_aligned_selection_conditioned_q25",
        features=CONTEXT_FEATURES,
        runner=lambda zz, **kw: policy_aligned_calibration_walk_forward(
            zz, top_k=args.top_k, **kw
        ),
        train_days=args.train_days,
        cal_days=args.cal_days,
        test_days=args.test_days,
        horizon=args.horizon,
        top_k=args.top_k,
    )

    report = {
        "experiment": "EXP-2026-09-29-POLICY-CAL-01",
        "evaluation_stage": "DEVELOPMENTAL_PREREGISTERED_POLICY_ALIGNMENT_NOT_HOLDOUT",
        "history_start": str(raw["decision_date"].min().date()),
        "history_end": str(raw["decision_date"].max().date()),
        "protocol": {
            "only_change": "apply_same_normal_market_veto_after_calibration_top3_freeze_before_residual_quantiles",
            "quantile_levels_changed": False,
            "q_levels": [Q_LOW, Q_MED, Q_HIGH],
            "top_k": args.top_k,
            "train_days": args.train_days,
            "cal_days": args.cal_days,
            "test_days": args.test_days,
            "purge_days": args.horizon,
            "admission": "netev_low_gt_0",
            "backfill_allowed": False,
            "hyperparameter_search": False,
            "promotion_allowed": False,
        },
        "supervised_cache": cache_meta,
        "label_diagnostics": label_diag,
        "reference": reference,
        "challenger": challenger,
        "compact_reference": _compact(reference),
        "compact_challenger": _compact(challenger),
        "preregistered_gate": (
            "Keep only if calibration population alignment does not deteriorate coverage, "
            "economic robustness, tail risk, or current-evidence behavior. Any improvement is "
            "development evidence only."
        ),
    }

    out = Path(args.result_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out / "summary.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2, default=str), encoding="utf-8"
    )
    reference_gate_selected.to_csv(out / "reference_normal_market_selected.csv", index=False)
    challenger_gate_selected.to_csv(out / "challenger_normal_market_selected.csv", index=False)
    print("POLICY_ALIGNED_CALIBRATION=" + json.dumps(report, ensure_ascii=False, default=str), flush=True)


if __name__ == "__main__":
    main()
