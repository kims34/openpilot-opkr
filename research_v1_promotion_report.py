"""Build a no-tuning promotion audit from selected-calibration artifacts.

This report intentionally does not change model predictions, calibration,
ranking, thresholds or selected trades. It only audits whether the current
best developmental candidate has evidence suitable for further promotion.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from run_research_v1 import load_panel


def _metrics(df: pd.DataFrame, seed: int = 1729, boot: int = 2000) -> dict:
    if df.empty:
        return {
            "trades": 0,
            "mean_net_return": 0.0,
            "win_rate": 0.0,
            "profit_factor": 0.0,
            "trade_expected_shortfall_95": 0.0,
            "trade_expected_shortfall_99": 0.0,
            "cluster_bootstrap_mean_net_return": 0.0,
            "cluster_bootstrap_95_low": 0.0,
            "cluster_bootstrap_95_high": 0.0,
        }
    x = pd.to_numeric(df["fh_net_return"], errors="coerce").dropna().to_numpy(float)
    gains = float(x[x > 0].sum())
    losses = float(-x[x < 0].sum())
    pf = gains / losses if losses > 0 else (float("inf") if gains > 0 else 0.0)
    k95 = max(1, int(np.ceil(len(x) * 0.05)))
    k99 = max(1, int(np.ceil(len(x) * 0.01)))
    ordered = np.sort(x)
    es95 = float(ordered[:k95].mean())
    es99 = float(ordered[:k99].mean())

    daily = (
        df.assign(_net=pd.to_numeric(df["fh_net_return"], errors="coerce"))
        .dropna(subset=["_net"])
        .groupby("decision_date")["_net"]
        .mean()
        .to_numpy(float)
    )
    if len(daily):
        rng = np.random.default_rng(seed)
        samples = np.empty(int(boot), dtype=float)
        for i in range(int(boot)):
            samples[i] = rng.choice(daily, size=len(daily), replace=True).mean()
        lo, hi = np.quantile(samples, [0.025, 0.975])
        cluster_mean = float(daily.mean())
    else:
        lo = hi = cluster_mean = 0.0

    return {
        "trades": int(len(x)),
        "mean_net_return": float(x.mean()),
        "win_rate": float((x > 0).mean()),
        "profit_factor": float(pf),
        "trade_expected_shortfall_95": es95,
        "trade_expected_shortfall_99": es99,
        "cluster_bootstrap_mean_net_return": cluster_mean,
        "cluster_bootstrap_95_low": float(lo),
        "cluster_bootstrap_95_high": float(hi),
    }


def _remove_best_days(df: pd.DataFrame, n: int) -> pd.DataFrame:
    if df.empty or n <= 0:
        return df.copy()
    daily = (
        df.assign(_net=pd.to_numeric(df["fh_net_return"], errors="coerce"))
        .groupby("decision_date")["_net"].mean()
        .sort_values(ascending=False)
    )
    removed = set(daily.head(int(n)).index.astype(str))
    return df[~df["decision_date"].astype(str).isin(removed)].copy()


def _stress_2x(df: pd.DataFrame) -> dict:
    if df.empty:
        return {"mean_net_return": 0.0, "profit_factor": 0.0, "win_rate": 0.0}
    gross = pd.to_numeric(df["fh_gross_return"], errors="coerce").to_numpy(float)
    cost = pd.to_numeric(df["fh_cost"], errors="coerce").to_numpy(float)
    net = gross - 2.0 * cost
    gains = float(net[net > 0].sum())
    losses = float(-net[net < 0].sum())
    return {
        "mean_net_return": float(net.mean()),
        "profit_factor": float(gains / losses) if losses > 0 else (float("inf") if gains > 0 else 0.0),
        "win_rate": float((net > 0).mean()),
    }


def _frozen_evidence_flags_and_blockers(
    overall: dict,
    after5: dict,
    recent_metrics: dict,
    stress2: dict,
    *,
    recent_records: int,
) -> tuple[dict, list[str]]:
    """Apply the frozen Master-Spec promotion evidence conjunctions."""
    overall_robust = bool(
        overall.get("mean_net_return", 0.0) > 0
        and overall.get("profit_factor", 0.0) > 1
        and overall.get("cluster_bootstrap_95_low", 0.0) > 0
    )
    jackpot_independent = bool(
        after5.get("mean_net_return", 0.0) > 0
        and after5.get("profit_factor", 0.0) > 1
        and after5.get("cluster_bootstrap_95_low", 0.0) > 0
    )
    recent_robust = bool(
        recent_records > 0
        and recent_metrics.get("mean_net_return", 0.0) > 0
        and recent_metrics.get("profit_factor", 0.0) > 1
        and recent_metrics.get("cluster_bootstrap_95_low", 0.0) > 0
    )
    cost2_ok = bool(
        stress2.get("mean_net_return", 0.0) > 0
        and stress2.get("profit_factor", 0.0) > 1
    )

    blockers = []
    if not overall_robust:
        blockers.append("OVERALL_CLUSTER_LCB_NOT_POSITIVE")
    if not jackpot_independent:
        blockers.append("BEST_5_DECISION_DAY_ROBUSTNESS_FAILS_MEAN_PF_OR_CLUSTER_LCB")
    if recent_records == 0:
        blockers.append("NO_ADMISSIONS_IN_LATEST_504_TEST_SESSIONS")
    elif not recent_robust:
        blockers.append("RECENT_504_SESSION_EDGE_NOT_ROBUST")
    if not cost2_ok:
        blockers.append("FAILS_2X_COST_STRESS")

    return {
        "overall_robust": overall_robust,
        "jackpot_independent_after_best5_days": jackpot_independent,
        "recent_504_session_robust": recent_robust,
        "cost_2x_survives": cost2_ok,
    }, blockers


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--result-dir", default="research_results/marcap_pit_selected_calibration")
    ap.add_argument("--pit-cache", default="research_data/marcap_kospi_pit_long")
    ap.add_argument("--candidate", default="all_context_selection_conditioned_normal_market_selected.csv")
    ap.add_argument("--recent-sessions", type=int, default=504)
    args = ap.parse_args()

    out = Path(args.result_dir)
    summary = json.loads((out / "summary.json").read_text(encoding="utf-8"))
    selected = pd.read_csv(out / args.candidate)
    selected["decision_date"] = pd.to_datetime(selected["decision_date"]).dt.strftime("%Y-%m-%d")

    raw = load_panel(Path(args.pit_cache))
    sessions = sorted(pd.Timestamp(x) for x in raw["decision_date"].drop_duplicates())
    # Restrict current-evidence window to sessions actually covered by test folds.
    folds = summary["results"]["all_context"]["selection_conditioned"].get("folds", [])
    if folds:
        first_test = pd.Timestamp(folds[0]["test_start"])
        last_test = pd.Timestamp(folds[-1]["test_end"])
        sessions = [d for d in sessions if first_test <= d <= last_test]
    recent = sessions[-int(args.recent_sessions):] if sessions else []
    recent_start = recent[0].strftime("%Y-%m-%d") if recent else None
    recent_end = recent[-1].strftime("%Y-%m-%d") if recent else None
    recent_df = selected[selected["decision_date"] >= recent_start].copy() if recent_start else selected.iloc[0:0].copy()

    overall = _metrics(selected)
    remove = {}
    for n in (1, 3, 5):
        kept = _remove_best_days(selected, n)
        remove[str(n)] = {"remaining_records": int(len(kept)), "metrics": _metrics(kept)}
    recent_metrics = _metrics(recent_df)
    stress2 = _stress_2x(selected)
    after5 = remove["5"]["metrics"]
    evidence_flags, blockers = _frozen_evidence_flags_and_blockers(
        overall,
        after5,
        recent_metrics,
        stress2,
        recent_records=int(len(recent_df)),
    )

    portfolio = (
        summary["results"]["all_context"]["selection_conditioned"]
        .get("market_eligibility_overlay", {})
        .get("portfolio", {})
    )
    report = {
        "evaluation_stage": "DEVELOPMENTAL_PROMOTION_EVIDENCE_AUDIT_NOT_HOLDOUT",
        "candidate": "all_context_selection_conditioned_q25__normal_market_fail_closed__strict_top3_no_backfill",
        "changes_model_or_thresholds": False,
        "overall": overall,
        "remove_best_decision_days": remove,
        "recent_504_test_sessions": {
            "start": recent_start,
            "end": recent_end,
            "sessions": int(len(recent)),
            "records": int(len(recent_df)),
            "metrics": recent_metrics,
        },
        "cost_2x": stress2,
        "portfolio_snapshot": portfolio,
        "evidence_flags": evidence_flags,
        "blockers": blockers,
        "classification": "DEVELOPMENTAL_NOT_CURRENTLY_PROMOTABLE" if blockers else "DEVELOPMENTAL_CURRENT_EDGE_CANDIDATE",
        "production_promotion_allowed": False,
        "reason": "Development evidence only; sealed holdout and prospective Shadow are still mandatory even if all flags later pass.",
    }
    (out / "promotion_audit.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2, default=str), encoding="utf-8"
    )
    print("PROMOTION_AUDIT=" + json.dumps(report, ensure_ascii=False, default=str), flush=True)


if __name__ == "__main__":
    main()
