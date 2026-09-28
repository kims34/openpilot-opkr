"""Long-history corporate-action-safe robustness for Distributional NetEV.

This is NOT a sealed holdout. The architecture was informed by later-period
research, so 2015-2026 is used only as a historical robustness/falsification test.
No threshold/window/hyperparameter search is allowed.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from research_v1_context import CONTEXT_FEATURES, add_context
from research_v1_distributional_netev import (
    _calendar_splits,
    _cost_stress,
    _fixed_record_map,
    _metric,
    _portfolio,
    distributional_walk_forward,
    freeze_original_topk,
)
from research_v1_fixed_horizon_label import add_fixed_horizon_target
from research_v1_ml import stateful_select_records
from research_v1_supervised_cache import load_or_build
from run_research_v1 import load_panel

MARKET = [
    "market_ret1_median", "market_ret5_median", "market_ret20_median",
    "breadth1", "breadth5", "dispersion20",
]
RESID = ["resid_ret1", "resid_ret5", "resid_ret20"]
CONTEXT_ONLY = MARKET + RESID


def _extreme_day_dependency(records):
    if not records:
        return {"baseline": _metric([]), "remove_best_days": {}}
    by_day = {}
    for rec in records:
        by_day.setdefault(rec.decision_day, []).append(rec)
    ranked = sorted(
        by_day,
        key=lambda d: sum(r.net_return for r in by_day[d]) / len(by_day[d]),
        reverse=True,
    )
    out = {"baseline": _metric(records), "remove_best_days": {}}
    for n in (1, 3, 5, 10):
        removed = set(ranked[:n])
        kept = [r for r in records if r.decision_day not in removed]
        out["remove_best_days"][str(n)] = {
            "removed_dates": [str(d) for d in ranked[:n]],
            "remaining_records": int(len(kept)),
            "metrics": _metric(kept),
        }
    return out


def evaluate_candidate(z, fixed_map, raw, *, name, features, train_days, cal_days, test_days, horizon, top_k):
    pred, folds = distributional_walk_forward(
        z,
        train_days=train_days,
        cal_days=cal_days,
        test_days=test_days,
        purge_days=horizon,
        features=features,
    )
    if pred.empty:
        return {"name": name, "features": features, "error": "no_predictions"}, pred

    eligible = pred[pred["netev_low"] > 0].copy()
    frozen = freeze_original_topk(eligible, top_k)
    records, selected, selection_diag = stateful_select_records(
        frozen, fixed_map, top_k=top_k, threshold=0.0,
    )
    test_dates = int(pred["decision_date"].nunique())
    trade_days = int(selected["decision_date"].nunique()) if not selected.empty else 0
    result = {
        "name": name,
        "features": features,
        "prediction_rows": int(len(pred)),
        "eligible_lower_bound_positive_rows": int(len(eligible)),
        "frozen_topk_rows": int(len(frozen)),
        "selected_records": int(len(records)),
        "test_dates": test_dates,
        "trade_days": trade_days,
        "trade_day_coverage": float(trade_days / test_dates) if test_dates else 0.0,
        "selection_diagnostics": selection_diag,
        "metrics": _metric(records),
        "cost_stress": _cost_stress(records),
        "calendar_year_splits": _calendar_splits(records),
        "extreme_day_dependency": _extreme_day_dependency(records),
        "portfolio": _portfolio(raw, records, pred, horizon),
        "folds": folds,
    }
    result["preliminary_pass"] = bool(
        result["metrics"].get("mean_net_return", 0.0) > 0
        and result["metrics"].get("profit_factor", 0.0) > 1.0
        and result["metrics"].get("cluster_bootstrap_95_low", 0.0) > 0
    )
    return result, selected


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cache", default="research_data/marcap_kospi_pit_long")
    ap.add_argument("--supervised-cache", default="research_data/pit_supervised_long_v2_ca")
    ap.add_argument("--result-dir", default="research_results/marcap_pit_distributional_long")
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
    selections = {}
    for name, features in {
        "all_context_reference": CONTEXT_FEATURES,
        "context_only_challenger": CONTEXT_ONLY,
    }.items():
        result, selected = evaluate_candidate(
            z, fixed_map, raw,
            name=name,
            features=features,
            train_days=args.train_days,
            cal_days=args.cal_days,
            test_days=args.test_days,
            horizon=args.horizon,
            top_k=args.top_k,
        )
        models[name] = result
        selections[name] = selected

    ref = models["all_context_reference"].get("metrics", {})
    ctx = models["context_only_challenger"].get("metrics", {})
    comparison = {
        "mean_net_return_delta_context_minus_reference": float(ctx.get("mean_net_return", 0.0) - ref.get("mean_net_return", 0.0)),
        "profit_factor_delta_context_minus_reference": float(ctx.get("profit_factor", 0.0) - ref.get("profit_factor", 0.0)),
        "cluster_low_delta_context_minus_reference": float(ctx.get("cluster_bootstrap_95_low", 0.0) - ref.get("cluster_bootstrap_95_low", 0.0)),
    }

    report = {
        "evaluation_stage": "LONG_HISTORY_CA_SAFE_ROBUSTNESS_NOT_SEALED_HOLDOUT",
        "history_start": str(raw["decision_date"].min().date()),
        "history_end": str(raw["decision_date"].max().date()),
        "feature_return_policy": "KRX_FLUC_RT_BASE_PRICE_ADJUSTED_FOR_CORPORATE_ACTIONS",
        "fixed_horizon_return_policy": "KRX_FLUC_RT_ECONOMIC_INDEX_FROM_ENTRY_OPEN_TO_EXIT_CLOSE",
        "protocol": {
            "train_days_initial": args.train_days,
            "cal_days": args.cal_days,
            "test_days": args.test_days,
            "purge_days": args.horizon,
            "liquidity_floor": "adv20_rank_ge_0.20",
            "admission": "netev_low_gt_0__freeze_original_top3__blocked_slot_stays_empty",
            "hyperparameter_search": False,
            "holdout_claim": False,
        },
        "supervised_cache": cache_meta,
        "label_diagnostics": label_diag,
        "models": models,
        "comparison": comparison,
        "promotion_allowed_from_this_test": False,
        "reason": (
            "Long-history evidence can reject fragile candidates or support continued research, "
            "but cannot replace a sealed holdout and prospective Shadow because model choices were informed by prior results."
        ),
    }
    report["verdict"] = (
        "ROBUSTNESS_SUPPORTS_CONTINUED_RESEARCH"
        if models["context_only_challenger"].get("preliminary_pass", False)
        else "LONG_HISTORY_DOES_NOT_YET_ESTABLISH_ROBUST_EDGE"
    )

    out = Path(args.result_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out / "summary.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    for name, selected in selections.items():
        if hasattr(selected, "to_csv"):
            selected.to_csv(out / f"{name}_selected.csv", index=False)
    print("DISTRIBUTIONAL_LONG_HISTORY=" + json.dumps(report, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
