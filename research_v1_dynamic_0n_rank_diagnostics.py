"""Outcome-independent rank attribution for Dynamic 0-N diagnostic reports.

All candidates are ranked at decision time from predicted net EV and symbol,
before considering future label availability.  Observed outcomes are used ONLY
for after-the-fact performance summaries within the already fixed rank bands.
This module never selects trades, changes the Frozen model, or opens a holdout.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

BANDS = {
    "r1_3": (1, 3),
    "r4_5": (4, 5),
    "r6_10": (6, 10),
    "r11_plus": (11, 10**9),
}


def rank_diagnostics(pred: pd.DataFrame) -> dict:
    required = ("decision_date", "symbol", "netev_low",
                "fh_label_available", "fh_net_return")
    if not isinstance(pred, pd.DataFrame) or any(c not in pred.columns for c in required):
        raise ValueError("RANK_DIAGNOSTIC_REQUIRED_COLUMNS_MISSING")
    if pred.empty:
        return {
            **{name: {"rows": 0, "ranked_rows": 0, "missing_outcome_rows": 0,
                     "mean_net_return": None, "profit_factor": None,
                     "positive_rate": None, "mean_netev_low": None}
               for name in BANDS},
            "positive_candidate_count_by_day": {
                "days_with_any": 0, "mean": 0.0, "p50": 0.0,
                "p90": 0.0, "max": 0, "days_gt3": 0,
                "days_gt5": 0, "days_gt10": 0,
            },
            "ranking_uses_future_labels": False,
        }
    x = pred.copy()
    if x[["decision_date", "symbol"]].isna().any().any() or x.duplicated(
        subset=["decision_date", "symbol"]).any():
        raise ValueError("RANK_DIAGNOSTIC_AMBIGUOUS_DECISION_ID")
    # Stable, decision-time tie-break; NEVER remove an unknown outcome before
    # assigning a rank or counting positive NetEV candidates.
    x["netev_low"] = pd.to_numeric(x["netev_low"], errors="coerce")
    x = x.sort_values(
        ["decision_date", "netev_low", "symbol"],
        ascending=[True, False, True],
        kind="mergesort", na_position="last",
    )
    x["rank_all"] = x.groupby("decision_date").cumcount() + 1
    observed_return = pd.to_numeric(x["fh_net_return"], errors="coerce")
    x["observed_return"] = observed_return.where(np.isfinite(observed_return))
    x["outcome_known"] = x["fh_label_available"].fillna(False).astype(bool) & x["observed_return"].notna()

    out = {}
    for name, (lo, hi) in BANDS.items():
        group = x[(x["rank_all"] >= lo) & (x["rank_all"] <= hi)]
        returns = group.loc[group["outcome_known"], "observed_return"].to_numpy(dtype=float)
        gains = float(returns[returns > 0].sum()) if len(returns) else 0.0
        losses = float(-returns[returns < 0].sum()) if len(returns) else 0.0
        scores = group["netev_low"].replace([np.inf, -np.inf], np.nan).dropna()
        out[name] = {
            "ranked_rows": int(len(group)),
            "missing_outcome_rows": int(len(group) - len(returns)),
            "rows": int(len(returns)),
            "mean_net_return": float(returns.mean()) if len(returns) else None,
            "profit_factor": float(gains / losses) if losses > 0 else None,
            "positive_rate": float((returns > 0).mean()) if len(returns) else None,
            "mean_netev_low": float(scores.mean()) if len(scores) else None,
        }
    positive = x[x["netev_low"] > 0]
    counts = positive.groupby("decision_date").size()
    out["positive_candidate_count_by_day"] = {
        "days_with_any": int(len(counts)),
        "mean": float(counts.mean()) if len(counts) else 0.0,
        "p50": float(counts.quantile(.5)) if len(counts) else 0.0,
        "p90": float(counts.quantile(.9)) if len(counts) else 0.0,
        "max": int(counts.max()) if len(counts) else 0,
        "days_gt3": int((counts > 3).sum()) if len(counts) else 0,
        "days_gt5": int((counts > 5).sum()) if len(counts) else 0,
        "days_gt10": int((counts > 10).sum()) if len(counts) else 0,
    }
    out["ranking_uses_future_labels"] = False
    return out
