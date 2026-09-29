"""Promotion-evidence audit for IndexAlert Research v1.

This module does not tune a model. It summarizes whether a developmental
candidate has evidence that would justify *continued promotion research*.
Actual production promotion remains impossible until a sealed holdout and
prospective Shadow are passed.

The audit deliberately checks dimensions that an attractive average can hide:
- date-cluster lower confidence bound,
- dependence on a handful of best decision days,
- current/recent evidence over the latest 504 test sessions,
- cost-stress survival,
- tail loss and drawdown.
"""
from __future__ import annotations

from dataclasses import asdict
from typing import Iterable

import pandas as pd

from research_v1_distributional_netev import _metric


def _records_on_or_after(records: Iterable, cutoff) -> list:
    return [r for r in records if pd.Timestamp(r.decision_day) >= pd.Timestamp(cutoff)]


def _remove_best_decision_days(records: list, n: int) -> list:
    if not records or n <= 0:
        return list(records)
    by_day = {}
    for rec in records:
        by_day.setdefault(rec.decision_day, []).append(rec)
    ranked = sorted(
        by_day,
        key=lambda d: sum(r.net_return for r in by_day[d]) / len(by_day[d]),
        reverse=True,
    )
    remove = set(ranked[:n])
    return [r for r in records if r.decision_day not in remove]


def promotion_evidence_audit(
    records: list,
    pred: pd.DataFrame,
    *,
    recent_test_sessions: int = 504,
    cost_stress: dict | None = None,
    portfolio: dict | None = None,
) -> dict:
    """Return non-tuning evidence diagnostics for a candidate policy."""
    overall = _metric(records)

    dates = sorted(pd.Timestamp(x) for x in pred["decision_date"].drop_duplicates())
    recent_dates = dates[-int(recent_test_sessions):] if dates else []
    recent_start = recent_dates[0] if recent_dates else None
    recent_records = _records_on_or_after(records, recent_start) if recent_start is not None else []
    recent = _metric(recent_records)

    remove_best = {}
    for n in (1, 3, 5):
        kept = _remove_best_decision_days(records, n)
        remove_best[str(n)] = {
            "remaining_records": int(len(kept)),
            "metrics": _metric(kept),
        }

    robust_overall = bool(
        overall.get("mean_net_return", 0.0) > 0
        and overall.get("profit_factor", 0.0) > 1.0
        and overall.get("cluster_bootstrap_95_low", 0.0) > 0
    )
    five = remove_best["5"]["metrics"]
    # Frozen Short/Swing promotion contract: removing the five best decision
    # days must preserve positive mean, PF>1 *and* a positive date-cluster LCB.
    # Mean/PF alone can still be driven by a thin set of dependent dates.
    jackpot_independent = bool(
        five.get("mean_net_return", 0.0) > 0
        and five.get("profit_factor", 0.0) > 1.0
        and five.get("cluster_bootstrap_95_low", 0.0) > 0
    )
    recent_robust = bool(
        len(recent_records) > 0
        and recent.get("mean_net_return", 0.0) > 0
        and recent.get("profit_factor", 0.0) > 1.0
        and recent.get("cluster_bootstrap_95_low", 0.0) > 0
    )

    stress2 = (cost_stress or {}).get("2.0", {})
    cost_2x_survives = bool(
        stress2
        and stress2.get("mean_net_return", 0.0) > 0
        and stress2.get("profit_factor", 0.0) > 1.0
    )

    blockers = []
    if not robust_overall:
        blockers.append("OVERALL_CLUSTER_LCB_NOT_POSITIVE")
    if not jackpot_independent:
        blockers.append("BEST_5_DECISION_DAY_ROBUSTNESS_FAILS_MEAN_PF_OR_CLUSTER_LCB")
    if len(recent_records) == 0:
        blockers.append("NO_ADMISSIONS_IN_LATEST_504_TEST_SESSIONS")
    elif not recent_robust:
        blockers.append("RECENT_504_SESSION_EDGE_NOT_ROBUST")
    if stress2 and not cost_2x_survives:
        blockers.append("FAILS_2X_COST_STRESS")

    return {
        "purpose": "promotion_evidence_only_not_model_tuning",
        "production_promotion_allowed": False,
        "overall": overall,
        "remove_best_decision_days": remove_best,
        "recent_504_test_sessions": {
            "requested_sessions": int(recent_test_sessions),
            "actual_sessions": int(len(recent_dates)),
            "start": str(recent_dates[0].date()) if recent_dates else None,
            "end": str(recent_dates[-1].date()) if recent_dates else None,
            "records": int(len(recent_records)),
            "metrics": recent,
        },
        "cost_2x_survives": cost_2x_survives,
        "portfolio_snapshot": dict(portfolio or {}),
        "evidence_flags": {
            "overall_robust": robust_overall,
            "jackpot_independent_after_best5_days": jackpot_independent,
            "recent_504_session_robust": recent_robust,
        },
        "blockers": blockers,
        "classification": (
            "DEVELOPMENTAL_CURRENT_EDGE_CANDIDATE"
            if not blockers
            else "DEVELOPMENTAL_NOT_CURRENTLY_PROMOTABLE"
        ),
    }
