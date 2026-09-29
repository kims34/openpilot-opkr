"""PIT-safe market eligibility diagnostics for IndexAlert Research v1.

This module is a market-structure gate, not a predictive feature or a return
threshold tuned on outcomes.

For KOSPI/KOSDAQ from 2015-06-15 onward the normal daily price limit is +/-30%.
A decision-day KRX base-price-adjusted return materially outside that envelope
therefore indicates a non-standard trading state (for example cleanup trading,
a listing/relisting special regime, or a data/status issue).  Such securities
are fail-closed for the normal short-horizon engine.

Important:
- the decision-day return is known at decision time;
- the gate is applied only after original Top-K is frozen in the diagnostic
  overlay, so vetoed slots stay empty and no 4th/5th-ranked name is promoted;
- this does not replace an official KRX security-status / security-master join.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import date

import pandas as pd

PRICE_LIMIT_30_START = pd.Timestamp("2015-06-15")
NORMAL_DAILY_LIMIT = 0.30
# KRX percentage/tick rounding can sit fractionally around the theoretical
# limit.  50 bps is deliberately a tolerance, not a tuned model threshold.
PRICE_LIMIT_TOLERANCE = 0.005
EXCEPTIONAL_THRESHOLD = NORMAL_DAILY_LIMIT + PRICE_LIMIT_TOLERANCE


@dataclass(frozen=True)
class MarketEligibilityDiagnostics:
    policy: str
    rows_before: int
    rows_after: int
    vetoed_rows: int
    vetoed_dates: int
    vetoed_symbols: int
    threshold_abs_return: float
    backfill_allowed: bool
    official_status_validated: bool


def tag_normal_market_eligibility(frame: pd.DataFrame) -> pd.DataFrame:
    """Attach a decision-time normal-market eligibility flag.

    Required columns are `decision_date` and the CA-safe one-day return `ret1`.
    The function intentionally fails on pre-2015-06-15 rows because the 30%
    rule was not yet in force and a different historical rule would be needed.
    """
    required = {"decision_date", "ret1"}
    missing = required.difference(frame.columns)
    if missing:
        raise ValueError(f"market eligibility requires {sorted(missing)}")

    x = frame.copy()
    d = pd.to_datetime(x["decision_date"], errors="coerce")
    if d.isna().any():
        raise ValueError("decision_date contains unparseable values")
    if len(x) and d.min() < PRICE_LIMIT_30_START:
        raise ValueError(
            "normal-market +/-30% gate is only defined from 2015-06-15 onward"
        )

    ret = pd.to_numeric(x["ret1"], errors="coerce")
    # Missing critical market-state evidence fails closed.
    missing_ret = ret.isna()
    outside_normal_limit = ret.abs() > EXCEPTIONAL_THRESHOLD
    x["market_state_return_missing"] = missing_ret
    x["outside_normal_price_limit_envelope"] = outside_normal_limit.fillna(False)
    x["normal_market_eligible"] = ~(missing_ret | outside_normal_limit.fillna(False))
    x["market_eligibility_reason"] = "NORMAL_PRICE_LIMIT_STATE"
    x.loc[missing_ret, "market_eligibility_reason"] = "MISSING_DECISION_RETURN"
    x.loc[outside_normal_limit.fillna(False), "market_eligibility_reason"] = (
        "OUTSIDE_NORMAL_30PCT_PRICE_LIMIT_ENVELOPE"
    )
    x["market_eligibility_policy"] = (
        "PIT_FAIL_CLOSED__ABS_KRX_BASE_RETURN_LE_30PCT_PLUS_50BP_TOLERANCE"
    )
    return x


def veto_frozen_topk_nonstandard_market(frozen_topk: pd.DataFrame):
    """Veto non-standard names after Top-K is frozen; never backfill slots."""
    tagged = tag_normal_market_eligibility(frozen_topk)
    kept = tagged[tagged["normal_market_eligible"].astype(bool)].copy()
    vetoed = tagged[~tagged["normal_market_eligible"].astype(bool)].copy()
    diag = MarketEligibilityDiagnostics(
        policy="POST_RANK_HARD_VETO__BLOCKED_SLOT_STAYS_EMPTY",
        rows_before=int(len(tagged)),
        rows_after=int(len(kept)),
        vetoed_rows=int(len(vetoed)),
        vetoed_dates=int(vetoed["decision_date"].nunique()) if len(vetoed) else 0,
        vetoed_symbols=int(vetoed["symbol"].nunique()) if "symbol" in vetoed.columns and len(vetoed) else 0,
        threshold_abs_return=float(EXCEPTIONAL_THRESHOLD),
        backfill_allowed=False,
        official_status_validated=False,
    )
    return kept, vetoed, asdict(diag)
