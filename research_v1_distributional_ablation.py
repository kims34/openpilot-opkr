"""Purged PIT feature-family ablation for Distributional NetEV.

This is a diagnostic decomposition, not a hyperparameter search. Every family
uses the same expanding walk-forward, purge, calibration, lower-bound admission,
strict decision-time Top3 freeze and no-backfill execution policy.
"""
from pathlib import Path
import json

from research_v1_context import CONTEXT_FEATURES, add_context
from research_v1_distributional_netev import (
    _calendar_splits,
    _cost_stress,
    _fixed_record_map,
    _metric,
    distributional_walk_forward,
    freeze_original_topk,
)
from research_v1_fixed_horizon_label import add_fixed_horizon_target
from research_v1_ml import FEATURES, stateful_select_records
from research_v1_supervised_cache import load_or_build
from run_research_v1 import load_panel

MARKET = [
    "market_ret1_median", "market_ret5_median", "market_ret20_median",
    "breadth1", "breadth5", "dispersion20",
]
RESID = ["resid_ret1", "resid_ret5", "resid_ret20"]

FAMILIES = {
    "all_context": CONTEXT_FEATURES,
    "base_only": FEATURES,
    "drop_market": [x for x in CONTEXT_FEATURES if x not in MARKET],
    "drop_residual": [x for x in CONTEXT_FEATURES if x not in RESID],
    "context_only": MARKET + RESID,
    "market_only": MARKET,
    "residual_only": RESID,
}


def _rank_diagnostics(pred):
    if pred.empty:
        return {"days": 0, "median_unique_scores_per_day": 0.0, "fraction_days_single_unique_score": 0.0}
    unique_per_day = pred.groupby("decision_date")["score"].nunique(dropna=True)
    return {
        "days": int(len(unique_per_day)),
        "median_unique_scores_per_day": float(unique_per_day.median()),
        "fraction_days_single_unique_score": float((unique_per_day <= 1).mean()),
    }


def _extreme_day_dependency(records):
    if not records:
        return {"baseline": _metric([]), "remove_best_days": {}}
    by_day = {}
    for rec in records:
        by_day.setdefault(rec.decision_day, []).append(rec)
    ranked_days = sorted(
        by_day,
        key=lambda d: sum(r.net_return for r in by_day[d]) / len(by_day[d]),
        reverse=True,
    )
    out = {"baseline": _metric(records), "remove_best_days": {}}
    for n in (1, 3, 5):
        removed = set(ranked_days[:n])
        kept = [r for r in records if r.decision_day not in removed]
        out["remove_best_days"][str(n)] = {
            "removed_dates": [str(d) for d in ranked_days[:n]],
            "remaining_records": int(len(kept)),
            "metrics": _metric(kept),
        }
    return out


def main():
    raw = load_panel(Path("research_data/marcap_kospi_pit"))
    frame, legacy_map, diag, meta = load_or_build(
        raw,
        Path("research_data/pit_supervised_v2_ca"),
        horizon=5,
        target_return=0.04,
        stop_return=-0.025,
        participation=0.0005,
        commission_round_trip_bps=3.0,
    )
    frame = frame[frame["adv20_rank"] >= 0.20].copy().reset_index(drop=True)
    z = add_fixed_horizon_target(raw, add_context(frame), legacy_map, 5)
    fixed = _fixed_record_map(z, 5)
    out_dir = Path("research_results/marcap_pit_distributional_ablation")
    out_dir.mkdir(parents=True, exist_ok=True)
    out = {
        "evaluation_stage": "PIT_PRELIMINARY_CA_SAFE_FEATURE_FAMILY_ABLATION",
        "feature_return_policy": "KRX_FLUC_RT_BASE_PRICE_ADJUSTED_FOR_CORPORATE_ACTIONS",
        "fixed_horizon_return_policy": "KRX_FLUC_RT_ECONOMIC_INDEX_FROM_ENTRY_OPEN_TO_EXIT_CLOSE",
        "policy": "predeclared_feature_family_ablation_same_purged_walkforward_no_oos_threshold_tuning",
        "selection_policy": "netev_low_gt_0__freeze_original_top3__blocked_slot_stays_empty",
        "supervised_cache": meta,
        "label_diagnostics": diag,
        "models": {},
    }
    for name, features in FAMILIES.items():
        pred, _ = distributional_walk_forward(
            z, train_days=160, cal_days=40, test_days=40, purge_days=5, features=features,
        )
        eligible = pred[pred["netev_low"] > 0].copy()
        frozen = freeze_original_topk(eligible, 3)
        records, selected, selection_diag = stateful_select_records(
            frozen, fixed, top_k=3, threshold=0.0
        )
        out["models"][name] = {
            "features": features,
            "selected_records": int(len(records)),
            "trade_days": int(selected["decision_date"].nunique()) if not selected.empty else 0,
            "selection_diagnostics": selection_diag,
            "rank_diagnostics": _rank_diagnostics(pred),
            "metrics": _metric(records),
            "cost_stress": _cost_stress(records),
            "calendar_year_splits": _calendar_splits(records),
            "extreme_day_dependency": _extreme_day_dependency(records),
        }
        selected.to_csv(out_dir / f"{name}_selected.csv", index=False)
    out["diagnostic_note"] = (
        "Calibration always conditions residual quantiles on vol20_rank terciles. "
        "Market-only therefore remains under a fixed stock-specific volatility-calibration layer. "
        "Extreme-day tests remove entire decision days."
    )
    (out_dir / "summary.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print("DISTRIBUTIONAL_ABLATION=" + json.dumps(out, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
