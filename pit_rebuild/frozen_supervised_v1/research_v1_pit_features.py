"""Corporate-action-safe PIT feature construction for KOSPI research.

Execution prices remain raw KRX OHLC.  Return features use KRX's reported daily
fluctuation rate versus the applicable base price (`krx_change_return`). KRX
adjusts that base price for corporate actions such as splits/consolidations and
rights/bonus issues, preventing mechanical price-level changes from being
mistaken for momentum or volatility.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from research_v1_data_policy import add_liquidity_eligibility


def _rolling_compound(series: pd.Series, window: int) -> pd.Series:
    return series.rolling(window, min_periods=window).apply(
        lambda a: float(np.prod(1.0 + a) - 1.0), raw=True
    )


def add_pit_features(panel: pd.DataFrame) -> pd.DataFrame:
    if "krx_change_return" not in panel.columns:
        raise RuntimeError(
            "PIT KOSPI research requires krx_change_return from KRX FLUC_RT; "
            "raw close pct_change is not corporate-action safe"
        )
    x = panel.copy().sort_values(["symbol", "decision_date"]).reset_index(drop=True)
    x["krx_change_return"] = pd.to_numeric(x["krx_change_return"], errors="coerce")
    x["raw_close_ret1"] = x.groupby("symbol", sort=False)["close"].pct_change(1)
    x["corporate_action_return_gap"] = x["raw_close_ret1"] - x["krx_change_return"]

    x["ret1"] = x["krx_change_return"]
    g = x.groupby("symbol", sort=False, group_keys=False)
    x["ret5"] = g["ret1"].transform(lambda s: _rolling_compound(s, 5))
    x["ret20"] = g["ret1"].transform(lambda s: _rolling_compound(s, 20))
    x["vol20"] = g["ret1"].transform(
        lambda s: s.rolling(20, min_periods=20).std(ddof=0)
    )
    x["adv20"] = g["value"].transform(
        lambda s: s.rolling(20, min_periods=20).median()
    )
    x["feature_return_source"] = "KRX_FLUC_RT_BASE_PRICE_ADJUSTED"
    return add_liquidity_eligibility(x, 0.20)


def build_lookup(panel: pd.DataFrame):
    dates = sorted(panel["decision_date"].drop_duplicates())
    date_to_pos = {pd.Timestamp(d): i for i, d in enumerate(dates)}
    by_symbol = {
        s: g.set_index("decision_date").sort_index()
        for s, g in panel.groupby("symbol")
    }
    return dates, date_to_pos, by_symbol


def corporate_action_gap_diagnostics(feature_panel: pd.DataFrame) -> dict:
    if "corporate_action_return_gap" not in feature_panel.columns:
        return {}
    gap = pd.to_numeric(feature_panel["corporate_action_return_gap"], errors="coerce").dropna().abs()
    if gap.empty:
        return {"rows": 0}
    return {
        "rows": int(len(gap)),
        "abs_gap_gt_1pct": int((gap > 0.01).sum()),
        "abs_gap_gt_5pct": int((gap > 0.05).sum()),
        "abs_gap_gt_10pct": int((gap > 0.10).sum()),
        "max_abs_gap": float(gap.max()),
        "p999_abs_gap": float(gap.quantile(0.999)),
        "interpretation": "Large raw-close minus KRX-base-return gaps are corporate-action/discontinuity diagnostics, not automatic filters.",
    }
