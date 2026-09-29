"""Efficient exit-policy comparison on only frozen admission candidates.

The statistical model is run first.  Only the predeclared lower-bound-positive
frozen Top3 keys are then re-evaluated on corporate-action-safe economic OHLC.
This is exactly equivalent for the compared cohort/policy replay while avoiding
millions of irrelevant barrier reconstructions in long-history research.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from research_v1_context import add_context
from research_v1_distributional_netev import (
    _fixed_record_map,
    distributional_walk_forward,
    freeze_original_topk,
)
from research_v1_exit_policy_compare import (
    FEATURE_FAMILIES,
    _key_set,
    _paired_differences,
    _policy_summary,
    _records_for_keys,
    build_ca_safe_barrier_record_map,
)
from research_v1_fixed_horizon_label import add_fixed_horizon_target
from research_v1_ml import stateful_select_records
from research_v1_supervised_cache import load_or_build
from run_research_v1 import load_panel


def _frame_keys(df: pd.DataFrame) -> set:
    if df.empty:
        return set()
    return {
        (pd.Timestamp(r.decision_date).date(), str(r.symbol))
        for r in df.itertuples(index=False)
    }


def _evaluate_precomputed(
    *, raw, pred, folds, frozen, fixed_map, raw_barrier_map, ca_barrier_map,
    top_k: int, horizon: int,
):
    fixed_state_records, fixed_selected, fixed_sel_diag = stateful_select_records(
        frozen, fixed_map, top_k=top_k, threshold=0.0,
    )
    raw_state_records, raw_selected, raw_sel_diag = stateful_select_records(
        frozen, raw_barrier_map, top_k=top_k, threshold=0.0,
    )
    ca_state_records, ca_selected, ca_sel_diag = stateful_select_records(
        frozen, ca_barrier_map, top_k=top_k, threshold=0.0,
    )

    fixed_keys = _key_set(fixed_selected, fixed_map)
    paired_keys = fixed_keys & set(raw_barrier_map) & set(ca_barrier_map)
    fixed_paired = _records_for_keys(fixed_selected, fixed_map, paired_keys)
    raw_paired = _records_for_keys(fixed_selected, raw_barrier_map, paired_keys)
    ca_paired = _records_for_keys(fixed_selected, ca_barrier_map, paired_keys)
    paired_diff = _paired_differences(fixed_selected, raw_barrier_map, ca_barrier_map, paired_keys)

    raw_ca_changed = 0
    raw_ca_gt_1pct = 0
    if not paired_diff.empty:
        raw_ca_changed = int((paired_diff["raw_barrier_outcome"] != paired_diff["ca_barrier_outcome"]).sum())
        raw_ca_gt_1pct = int((paired_diff["ca_minus_raw_net"].abs() > 0.01).sum())

    return {
        "folds": folds,
        "test_dates": int(pred["decision_date"].nunique()),
        "eligible_rows": int((pred["netev_low"] > 0).sum()),
        "frozen_topk_rows": int(len(frozen)),
        "paired": {
            "common_keys": int(len(paired_keys)),
            "forced_d5_ca_safe": _policy_summary(raw, fixed_paired, pred, horizon, True),
            "raw_gap_aware_barrier_diagnostic": _policy_summary(raw, raw_paired, pred, horizon, False),
            "ca_safe_gap_aware_barrier": _policy_summary(raw, ca_paired, pred, horizon, True),
            "raw_vs_ca_barrier": {
                "outcome_changed_count": raw_ca_changed,
                "abs_net_difference_gt_1pct_count": raw_ca_gt_1pct,
            },
        },
        "policy_consistent_stateful": {
            "forced_d5_ca_safe": {
                "selection": fixed_sel_diag,
                "selected_records": int(len(fixed_state_records)),
                "trade_days": int(fixed_selected["decision_date"].nunique()) if not fixed_selected.empty else 0,
                **_policy_summary(raw, fixed_state_records, pred, horizon, True),
            },
            "raw_gap_aware_barrier_diagnostic": {
                "selection": raw_sel_diag,
                "selected_records": int(len(raw_state_records)),
                "trade_days": int(raw_selected["decision_date"].nunique()) if not raw_selected.empty else 0,
                **_policy_summary(raw, raw_state_records, pred, horizon, False),
            },
            "ca_safe_gap_aware_barrier": {
                "selection": ca_sel_diag,
                "selected_records": int(len(ca_state_records)),
                "trade_days": int(ca_selected["decision_date"].nunique()) if not ca_selected.empty else 0,
                **_policy_summary(raw, ca_state_records, pred, horizon, True),
            },
        },
        "selected_frames": {
            "fixed": fixed_selected,
            "raw": raw_selected,
            "ca": ca_selected,
            "paired_diff": paired_diff,
        },
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cache", required=True)
    ap.add_argument("--supervised-cache", required=True)
    ap.add_argument("--result-dir", required=True)
    ap.add_argument("--horizon", type=int, default=5)
    ap.add_argument("--top-k", type=int, default=3)
    ap.add_argument("--target", type=float, default=0.04)
    ap.add_argument("--stop", type=float, default=-0.025)
    ap.add_argument("--participation", type=float, default=0.0005)
    ap.add_argument("--train-days", type=int, default=160)
    ap.add_argument("--cal-days", type=int, default=40)
    ap.add_argument("--test-days", type=int, default=40)
    args = ap.parse_args()

    raw = load_panel(Path(args.cache))
    frame, raw_barrier_map, label_diag, cache_meta = load_or_build(
        raw,
        Path(args.supervised_cache),
        horizon=args.horizon,
        target_return=args.target,
        stop_return=args.stop,
        participation=args.participation,
        commission_round_trip_bps=3.0,
    )
    frame = frame[frame["adv20_rank"] >= 0.20].copy().reset_index(drop=True)
    z = add_fixed_horizon_target(raw, add_context(frame), raw_barrier_map, args.horizon)
    fixed_map = _fixed_record_map(z, args.horizon)

    prepared = {}
    needed_keys = set()
    for name, features in FEATURE_FAMILIES.items():
        pred, folds = distributional_walk_forward(
            z,
            train_days=args.train_days,
            cal_days=args.cal_days,
            test_days=args.test_days,
            purge_days=args.horizon,
            features=features,
        )
        if pred.empty:
            raise RuntimeError(f"distributional walk-forward produced no predictions for {name}")
        eligible = pred[pred["netev_low"] > 0].copy()
        frozen = freeze_original_topk(eligible, args.top_k)
        prepared[name] = (pred, folds, frozen)
        needed_keys |= _frame_keys(frozen)

    raw_barrier_subset = {
        key: raw_barrier_map[key]
        for key in needed_keys
        if key in raw_barrier_map
    }
    ca_barrier_map, ca_diag = build_ca_safe_barrier_record_map(
        raw,
        raw_barrier_subset,
        horizon=args.horizon,
        target_return=args.target,
        stop_return=args.stop,
        ambiguity_policy="stop_first",
    )

    out_dir = Path(args.result_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    report = {
        "evaluation_stage": "PIT_PRELIMINARY_EXIT_POLICY_ISOLATION_CA_SAFE_SELECTED_ONLY",
        "forecast_target": "corporate_action_safe_next_open_to_Dplus5_close_cost_adjusted_net_return",
        "admission_rule": "netev_low_gt_0__freeze_original_top3__blocked_slot_stays_empty",
        "exit_policies": {
            "A": "forced_Dplus5_on_KRX_FLUC_RT_economic_index",
            "B": "legacy_raw_OHLC_gap_aware_4pct_target_minus2p5pct_stop_DIAGNOSTIC_ONLY",
            "C": "KRX_FLUC_RT_economic_OHLC_gap_aware_4pct_target_minus2p5pct_stop",
        },
        "predeclared_parameters": {
            "target_return": args.target,
            "stop_return": args.stop,
            "horizon": args.horizon,
            "top_k": args.top_k,
            "train_days": args.train_days,
            "cal_days": args.cal_days,
            "test_days": args.test_days,
        },
        "no_parameter_search": True,
        "barrier_build_scope": {
            "frozen_candidate_keys": int(len(needed_keys)),
            "raw_barrier_keys_available": int(len(raw_barrier_subset)),
            "ca_safe_barrier_keys_built": int(len(ca_barrier_map)),
            "equivalence_note": "Only frozen candidates can enter these policy replays; non-candidate barrier records are irrelevant.",
        },
        "supervised_cache": cache_meta,
        "legacy_label_diagnostics": label_diag,
        "ca_safe_barrier_diagnostics": ca_diag,
        "models": {},
    }

    for name, (pred, folds, frozen) in prepared.items():
        result = _evaluate_precomputed(
            raw=raw,
            pred=pred,
            folds=folds,
            frozen=frozen,
            fixed_map=fixed_map,
            raw_barrier_map=raw_barrier_map,
            ca_barrier_map=ca_barrier_map,
            top_k=args.top_k,
            horizon=args.horizon,
        )
        frames = result.pop("selected_frames")
        report["models"][name] = result
        for key, df in frames.items():
            if isinstance(df, pd.DataFrame):
                df.to_csv(out_dir / f"{name}_{key}.csv", index=False)

    report["interpretation_contract"] = {
        "forced_d5": "forecast/opportunity label; not automatically accepted as final execution policy",
        "raw_barrier": "diagnostic only because raw price levels can be discontinuous across corporate actions",
        "ca_safe_barrier": "candidate realistic evaluator; adoption still requires long OOS robustness",
        "paired": "isolates exit-policy effect on identical selected keys",
        "policy_consistent_stateful": "shows full replay effect when earlier exits change future symbol availability",
        "judge_eligible": False,
        "judge_blockers": [
            "exact common-stock identity not yet fully validated",
            "exact halt/delisting economics not yet fully validated",
            "exit-policy comparator is preliminary research, not a sealed Judge",
        ],
    }
    (out_dir / "summary.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print("EXIT_POLICY_COMPARE_FAST=" + json.dumps(report, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
