"""Outcome-independent label-boundary enforcement; not trial admission.

Preserves the existing v2 training length and purge. Synthetic tests only do
not authorise evaluation of a consumed window or admit a successor protocol.
"""
from __future__ import annotations
import pandas as pd

def training_rows(obs, calendar, cutoff, horizon, train_days, purge_days):
    if horizon < 1 or train_days < 1 or purge_days < horizon:
        raise ValueError("invalid frozen horizon/training/purge parameters")
    c = calendar[["day_idx", "date"]].drop_duplicates().sort_values("day_idx").copy()
    c["date"] = pd.to_datetime(c["date"])
    if c.empty or c.day_idx.tolist() != list(range(len(c))):
        raise ValueError("session calendar must be contiguous from zero")
    if c.date.duplicated().any() or not c.date.is_monotonic_increasing:
        raise ValueError("session dates must be strictly increasing")
    observed = c[c.date <= pd.Timestamp(cutoff)]
    if observed.empty:
        raise ValueError("cutoff precedes calendar")
    # first future session index minus the originally frozen purge gap.
    end = int(observed.day_idx.max()) + 1 - purge_days
    start = max(0, end - train_days)
    date_by_idx = c.set_index("day_idx").date
    selected = obs[(obs.decision_idx >= start) & (obs.decision_idx < end)].copy()
    expected_dates = selected.decision_idx.map(date_by_idx)
    if expected_dates.isna().any() or not pd.to_datetime(selected.date).equals(expected_dates):
        raise ValueError("decision date/index binding mismatch")
    outcome_dates = selected.decision_idx.add(horizon).map(date_by_idx)
    if outcome_dates.isna().any() or (outcome_dates > pd.Timestamp(cutoff)).any():
        raise ValueError("training label reaches beyond cutoff")
    return selected
