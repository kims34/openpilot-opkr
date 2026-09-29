"""Pre-rank normal-market universe challenger for IndexAlert Research v1.

Purpose: distinguish a true universe-definition correction from a post-rank risk
veto.  The eligibility rule is fixed by KRX market structure, not fitted to
returns: from 2015-06-15 onward, decision-day KRX base-price-adjusted return must
remain inside the normal +/-30% price-limit envelope (plus 50bp tolerance).
Missing critical state evidence fails closed.

Protocol is intentionally narrow:
- one existing feature family only: CONTEXT_ONLY;
- same expanding 504-session train, 126-session calibration, 126-session test;
- same five-session purge, q25 lower-bound admission, costs and Top3 policy;
- no hyperparameter/threshold/window search;
- pre-rank scope is applied before context aggregation, training, calibration
  and ranking;
- this is developmental robustness evidence, never a sealed holdout.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from research_v1_context import add_context
from research_v1_distributional_long_history import CONTEXT_ONLY, evaluate_candidate
from research_v1_distributional_netev import _fixed_record_map
from research_v1_fixed_horizon_label import add_fixed_horizon_target
from research_v1_market_eligibility import tag_normal_market_eligibility
from research_v1_supervised_cache import load_or_build
from run_research_v1 import load_panel


def _build_z(raw, frame, legacy_map, horizon):
    context = add_context(frame)
    z = add_fixed_horizon_target(raw, context, legacy_map, horizon)
    return z, _fixed_record_map(z, horizon)


def _compact(candidate):
    m = candidate.get("metrics", {})
    p = candidate.get("portfolio", {})
    e = candidate.get("extreme_day_dependency", {}).get("remove_best_days", {})
    return {
        "selected_records": int(candidate.get("selected_records", 0)),
        "trade_day_coverage": float(candidate.get("trade_day_coverage", 0.0)),
        "mean_net_return": float(m.get("mean_net_return", 0.0)),
        "profit_factor": float(m.get("profit_factor", 0.0)),
        "cluster_bootstrap_95_low": float(m.get("cluster_bootstrap_95_low", 0.0)),
        "cluster_bootstrap_95_high": float(m.get("cluster_bootstrap_95_high", 0.0)),
        "total_return": float(p.get("total_return", 0.0)),
        "max_drawdown": float(p.get("max_drawdown", 0.0)),
        "remove_best_1_mean_net": float(e.get("1", {}).get("metrics", {}).get("mean_net_return", 0.0)),
        "remove_best_3_mean_net": float(e.get("3", {}).get("metrics", {}).get("mean_net_return", 0.0)),
        "remove_best_5_mean_net": float(e.get("5", {}).get("metrics", {}).get("mean_net_return", 0.0)),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cache", default="research_data/marcap_kospi_pit_long")
    ap.add_argument("--supervised-cache", default="research_data/pit_supervised_long_v3_ca_fp")
    ap.add_argument("--result-dir", default="research_results/marcap_pit_normal_market_scope")
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

    # Reference population: current full KOSPI-security research scope.
    ref_z, ref_map = _build_z(raw, frame, legacy_map, args.horizon)
    reference, _, _ = evaluate_candidate(
        ref_z,
        ref_map,
        raw,
        name="context_only_full_scope_reference",
        features=CONTEXT_ONLY,
        train_days=args.train_days,
        cal_days=args.cal_days,
        test_days=args.test_days,
        horizon=args.horizon,
        top_k=args.top_k,
    )

    # Challenger population: market eligibility is determined at decision time
    # before context, model fitting/calibration and rank generation.
    tagged = tag_normal_market_eligibility(frame)
    normal_frame = tagged[tagged["normal_market_eligible"].astype(bool)].copy().reset_index(drop=True)
    normal_z, normal_map = _build_z(raw, normal_frame, legacy_map, args.horizon)
    challenger, challenger_selected, _ = evaluate_candidate(
        normal_z,
        normal_map,
        raw,
        name="context_only_pre_rank_normal_market_scope",
        features=CONTEXT_ONLY,
        train_days=args.train_days,
        cal_days=args.cal_days,
        test_days=args.test_days,
        horizon=args.horizon,
        top_k=args.top_k,
    )

    ref_post_rank = reference.get("market_eligibility_overlay", {})
    report = {
        "evaluation_stage": "DEVELOPMENTAL_PRE_RANK_NORMAL_MARKET_SCOPE_CHALLENGER_NOT_HOLDOUT",
        "history_start": str(raw["decision_date"].min().date()),
        "history_end": str(raw["decision_date"].max().date()),
        "protocol": {
            "market_scope_rule": "abs_decision_day_KRX_base_return_le_30.5pct_and_not_missing",
            "scope_application": "before_context_training_calibration_ranking",
            "feature_family": "CONTEXT_ONLY_FIXED",
            "train_days": args.train_days,
            "cal_days": args.cal_days,
            "test_days": args.test_days,
            "purge_days": args.horizon,
            "top_k": args.top_k,
            "hyperparameter_search": False,
            "threshold_search": False,
            "promotion_allowed": False,
        },
        "rows_after_liquidity_reference": int(len(frame)),
        "rows_after_pre_rank_normal_market_scope": int(len(normal_frame)),
        "rows_vetoed_pre_rank": int(len(frame) - len(normal_frame)),
        "veto_rate": float((len(frame) - len(normal_frame)) / len(frame)) if len(frame) else 0.0,
        "supervised_cache": cache_meta,
        "label_diagnostics": label_diag,
        "full_scope_reference": reference,
        "post_rank_gate_reference": ref_post_rank,
        "pre_rank_normal_market_challenger": challenger,
        "compact_comparison": {
            "full_scope": _compact(reference),
            "post_rank_gate": _compact(ref_post_rank),
            "pre_rank_scope": _compact(challenger),
        },
        "guardrail": (
            "This universe correction was motivated by verified non-standard trading states. "
            "It may support a data-policy decision but cannot establish investable edge without "
            "official security-status/common-stock identity and later sealed holdout/Shadow evidence."
        ),
    }

    out = Path(args.result_dir)
    out.mkdir(parents=True, exist_ok=True)
    # Fold metadata contains pandas.Timestamp values from the PIT walk-forward.
    # Serialisation must not make an otherwise completed research run fail.
    encoded = json.dumps(report, ensure_ascii=False, indent=2, default=str)
    (out / "summary.json").write_text(encoded, encoding="utf-8")
    challenger_selected.to_csv(out / "pre_rank_normal_market_selected.csv", index=False)
    print("NORMAL_MARKET_SCOPE=" + json.dumps(report, ensure_ascii=False, default=str), flush=True)


if __name__ == "__main__":
    main()
