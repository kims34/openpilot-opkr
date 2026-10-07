"""Shared data eligibility and universe policy for IndexAlert Research v1."""
from __future__ import annotations

import pandas as pd


def _all_true(panel: pd.DataFrame, col: str, default: bool = False) -> bool:
    if col not in panel.columns or panel.empty:
        return default
    s = panel[col].fillna(False).astype(bool)
    return bool(s.all())


def dataset_status(panel: pd.DataFrame) -> dict:
    """Return research eligibility without confusing PIT with final Judge quality.

    A historical daily membership universe can be point-in-time while still
    lacking a validated common-stock identity layer. Such data are substantially
    stronger than a fixed current basket but remain PIT_PRELIMINARY.
    """
    pit = _all_true(panel, "point_in_time_universe", False)
    common_validated = _all_true(panel, "common_stock_identity_validated", False)
    judge_eligible = pit and common_validated
    if judge_eligible:
        result_class = "JUDGE"
    elif pit:
        result_class = "PIT_PRELIMINARY"
    else:
        result_class = "SMOKE_NONPIT"
    return {
        "point_in_time_universe": pit,
        "common_stock_identity_validated": common_validated,
        "judge_eligible": judge_eligible,
        "result_class": result_class,
        "survivorship_bias_possible": not pit,
    }


def add_liquidity_eligibility(panel: pd.DataFrame, quantile: float = 0.20) -> pd.DataFrame:
    """Apply the same date-local ADV gate to baselines and ML research.

    The cut is computed only from same-date, already-known trailing ADV values.
    New/insufficient-history rows are not eligible until their ADV is observable.
    """
    if not 0 <= quantile < 1:
        raise ValueError("quantile must be in [0, 1)")
    x = panel.copy()
    if "adv20" not in x.columns:
        raise ValueError("adv20 required before liquidity eligibility")
    cuts = x.groupby("decision_date")["adv20"].transform(lambda s: s.quantile(quantile))
    x["liquidity_cut_adv20"] = cuts
    x["liquid_eligible"] = x["adv20"].notna() & cuts.notna() & (x["adv20"] >= cuts)
    return x


def filter_liquid_eligible(panel: pd.DataFrame) -> pd.DataFrame:
    if "liquid_eligible" not in panel.columns:
        raise ValueError("liquid_eligible missing; call add_liquidity_eligibility first")
    return panel[panel["liquid_eligible"].fillna(False).astype(bool)].copy()
