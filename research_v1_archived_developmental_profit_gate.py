"""Immutable developmental profitability adjudication of existing H5/0-N artifacts.

This checks archived, previously executed historical model results without
rerunning or optimizing their historical data, reading a consumed holdout,
changing Frozen/Champion, or fetching external finance sources.
Archived source runs: Dynamic 0-N 37471348547, Rank-Aware 37473983749.
Any developmental PASS is prohibited; this audit evaluates only whether
the saved diagnostics even meet the required robustness minimums.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

ARCHIVED_RUN_DYNAMIC = 37471348547
ARCHIVED_RUN_RANKAWARE = 37473983749
ARCHIVED_DYNAMIC_EXPERIMENT = "EXP-2026-10-06-DYNAMIC-0N-01"
ARCHIVED_RANKAWARE_EXPERIMENT = "EXP-2026-10-06-DYNAMIC-0N-RANKAWARE-01"
ARCHIVED_DYNAMIC_STAGE = "DEVELOPMENTAL_PREREGISTERED_DIAGNOSTIC_NOT_HOLDOUT_NOT_PROMOTION"
ARCHIVED_RANKAWARE_STAGE = "DEVELOPMENTAL_PREREGISTERED_RANK_AWARE_DIAGNOSTIC_NOT_HOLDOUT"
POLICIES = (
    "A_frozen_dynamic_0_3_champion_reference",
    "B_fixed_0_5_diagnostic",
    "C_fixed_0_10_diagnostic",
    "D_economic_gate_dynamic_0_N_challenger",
)
REFERENCE_CAPITAL_KRW = 100_000
HORIZON = 5


class DevelopmentalEvidenceError(ValueError):
    """Only fixed codes, never provider/raw archive contents."""


def _obj(value: object) -> dict:
    if type(value) is not dict:
        raise DevelopmentalEvidenceError("DEVELOPMENTAL_REPORT_SHAPE_INVALID")
    return value


def _get(d: object, *path: str) -> object:
    obj = d
    for k in path:
        obj = _obj(obj)
        if k not in obj:
            raise DevelopmentalEvidenceError("DEVELOPMENTAL_REQUIRED_METRIC_MISSING")
        obj = obj[k]
    return obj


def _num(value: object) -> float:
    if type(value) not in (float, int) or not math.isfinite(value):
        raise DevelopmentalEvidenceError("DEVELOPMENTAL_METRIC_NOT_FINITE")
    return float(value)


def _count(value: object) -> int:
    if type(value) is not int or value < 0:
        raise DevelopmentalEvidenceError("DEVELOPMENTAL_COUNT_INVALID")
    return value


def _one_candidate(name: str, p: dict) -> dict:
    metrics = _obj(_get(p, "metrics"))
    portfolio = _obj(_get(p, "portfolio"))
    doubled = _obj(_get(p, "cost_stress", "2.0"))
    best_five = _obj(_get(p, "extreme_day_dependency", "remove_best_days", "5", "metrics"))
    net = _num(_get(metrics, "mean_net_return"))
    pf = _num(_get(metrics, "profit_factor"))
    lower = _num(_get(metrics, "cluster_bootstrap_95_low"))
    doubled_net = _num(_get(doubled, "mean_net_return"))
    doubled_pf = _num(_get(doubled, "profit_factor"))
    best5_net = _num(_get(best_five, "mean_net_return"))
    best5_pf = _num(_get(best_five, "profit_factor"))
    best5_lower = _num(_get(best_five, "cluster_bootstrap_95_low"))
    cagr = _num(_get(portfolio, "cagr_252"))
    mdd = _num(_get(portfolio, "max_drawdown"))
    es95 = _num(_get(portfolio, "daily_expected_shortfall_95"))
    es99 = _num(_get(portfolio, "daily_expected_shortfall_99"))
    trades = _count(_get(metrics, "trades"))
    sessions = _count(_get(portfolio, "sessions"))
    max_positions = _count(_get(portfolio, "max_concurrent_positions"))

    checks = {
        "positive_mean_net": net > 0,
        "profit_factor_gt_one": pf > 1,
        "positive_date_cluster_lcb95": lower > 0,
        "two_x_cost_positive_mean": doubled_net > 0,
        "two_x_cost_profit_factor_gt_one": doubled_pf > 1,
        "remove_best_five_positive_mean": best5_net > 0,
        "remove_best_five_profit_factor_gt_one": best5_pf > 1,
        "remove_best_five_positive_lcb95": best5_lower > 0,
    }
    max_n = None
    if name == "D_economic_gate_dynamic_0_N_challenger":
        max_n = _count(_get(p, "selected_n_by_trade_day", "max"))
    elif name == "E_rankaware_dynamic_0_N_challenger":
        # Same evidence from the original rank-aware execution; no algorithm
        # modifications, only archived observations.
        max_n = _count(_get(p, "selected_n", "max"))

    # These are extreme all-positions-equal illustrations, NOT modeled fills.
    per_name_if_max_n = (
        round(REFERENCE_CAPITAL_KRW / HORIZON / max_n, 2)
        if max_n and max_n > 0 else None
    )
    return {
        "candidate": name,
        "trade_count": trades,
        "test_sessions": sessions,
        "mean_net_return_pct": round(100 * net, 5),
        "profit_factor": round(pf, 5),
        "date_cluster_lcb95_pct": round(100 * lower, 5),
        "twice_cost_mean_net_return_pct": round(100 * doubled_net, 5),
        "after_best_five_days_removed_mean_net_pct": round(100 * best5_net, 5),
        "after_best_five_days_removed_pf": round(best5_pf, 5),
        "after_best_five_days_removed_lcb95_pct": round(100 * best5_lower, 5),
        "portfolio_cagr_pct": round(100 * cagr, 5),
        "portfolio_mdd_pct": round(100 * mdd, 5),
        "daily_portfolio_es95_pct": round(100 * es95, 5),
        "daily_portfolio_es99_pct": round(100 * es99, 5),
        "max_concurrent_positions": max_positions,
        "max_admitted_names_same_decision_day": max_n,
        "hypothetical_equal_cohort_krw_per_name_at_max_n": per_name_if_max_n,
        "observed_developmental_robustness_checks": checks,
        "all_observed_robustness_checks_pass": all(checks.values()),
        "official_historical_status_verified": False,
        "verified_krw_round_lot_capacity": False,
        "cross_strategy_same_day_portfolio_delta_lcb_verified": False,
        "independent_holdout_verified": False,
        "promotion_authorized": False,
        "real_orders_authorized": False,
    }


def adjudicate_archived_developmental_results(dynamic: dict, rankaware: dict) -> dict:
    if _get(dynamic, "experiment") != ARCHIVED_DYNAMIC_EXPERIMENT or _get(
        dynamic, "stage"
    ) != ARCHIVED_DYNAMIC_STAGE:
        raise DevelopmentalEvidenceError("UNPINNED_DYNAMIC_EXPERIMENT")
    if _get(rankaware, "experiment") != ARCHIVED_RANKAWARE_EXPERIMENT or _get(
        rankaware, "stage"
    ) != ARCHIVED_RANKAWARE_STAGE:
        raise DevelopmentalEvidenceError("UNPINNED_RANKAWARE_EXPERIMENT")
    fixed = _obj(_get(dynamic, "frozen"))
    if any(
        _get(fixed, key) != value
        for key, value in (
            ("horizon", 5), ("train_days", 504), ("cal_days", 126),
            ("test_days", 126), ("purge_days", 5),
            ("sealed_holdout_touched", False),
        )
    ):
        raise DevelopmentalEvidenceError("FROZEN_H5_DIAGNOSTIC_PROTOCOL_DRIFT")
    if set(_obj(_get(dynamic, "policies"))) != set(POLICIES):
        raise DevelopmentalEvidenceError("ARCHIVED_H5_POLICY_SET_CHANGED")
    if _get(rankaware, "protocol", "sealed_holdout_touched") is not False:
        raise DevelopmentalEvidenceError("RANKAWARE_HOLDOUT_INTEGRITY_INVALID")
    seen = []
    for policy in POLICIES:
        row = _one_candidate(policy, _obj(_get(dynamic, "policies", policy)))
        seen.append(row)
    rank_p = _obj(_get(rankaware, "result"))
    rank_p["selected_n"] = _get(rankaware, "selected_n")
    seen.append(_one_candidate("E_rankaware_dynamic_0_N_challenger", rank_p))

    # A candidate is NOT an edge if it only makes money on a small set of days.
    # No A/B dominance or tiny-live threshold is silently inferred here.
    return {
        "purpose": "FROZEN_H5_DYNAMIC_0N_ARCHIVED_DEVELOPMENTAL_PROFITABILITY_GATE",
        "status": "NO_PROMOTABLE_ECONOMIC_EDGE_FROM_ARCHIVED_EVIDENCE",
        "source_runs": [ARCHIVED_RUN_DYNAMIC, ARCHIVED_RUN_RANKAWARE],
        "developmental_replays_performed": 0,
        "new_market_or_broker_data_downloaded": False,
        "independent_holdout_read": False,
        "reference_capital_krw": REFERENCE_CAPITAL_KRW,
        "cohort_allocation_fraction": f"1/{HORIZON}",
        "candidates_checked": len(seen),
        "candidates_passing_all_observed_robustness": sum(
            r["all_observed_robustness_checks_pass"] for r in seen
        ),
        "candidates": seen,
        "m20_performance_run_authorized": False,
        "independent_holdout_authorized": False,
        "champion_change_authorized": False,
        "real_orders_authorized": False,
        "funds_movement_authorized": False,
        "permissions_change_authorized": False,
        "ordering": "DISABLED",
    }


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--dynamic-summary", type=Path, required=True)
    p.add_argument("--rankaware-summary", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    a = p.parse_args()
    try:
        # 1 MiB cap, strict type checking and rejecting missing receipts.
        def load(path: Path) -> dict:
            if path.stat().st_size > 1_048_576:
                raise DevelopmentalEvidenceError("ARCHIVE_REPORT_OVERSIZED")
            return _obj(json.loads(path.read_text(encoding="utf-8"),
                                   parse_constant=lambda _: None))
        outcome = adjudicate_archived_developmental_results(
            load(a.dynamic_summary), load(a.rankaware_summary)
        )
    except (DevelopmentalEvidenceError, OSError, ValueError, TypeError, UnicodeError):
        raise SystemExit("DEVELOPMENTAL_PROFITABILITY_EVIDENCE_FAIL_CLOSED") from None
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(outcome, sort_keys=True, indent=2), encoding="utf-8")
    print("INDEXALERT_ARCHIVED_NET_PROFITABILITY=" + json.dumps(outcome, sort_keys=True))


if __name__ == "__main__":
    main()
