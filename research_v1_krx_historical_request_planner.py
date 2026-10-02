"""Deterministic offline request planner for KRX full-history acquisition."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import pandas as pd


HALT_WINDOWS=(
    ("2015-06-15","2017-06-13"),
    ("2017-06-14","2019-06-13"),
    ("2019-06-14","2021-06-12"),
    ("2021-06-13","2023-06-12"),
    ("2023-06-13","2025-06-11"),
    ("2025-06-12","2026-10-01"),
)
PLAN_START=pd.Timestamp("2015-06-15")
PLAN_END=pd.Timestamp("2026-10-01")


class KRXHistoricalRequestPlanError(ValueError):
    pass


def _intersect(a0: pd.Timestamp,a1: pd.Timestamp,b0: pd.Timestamp,b1: pd.Timestamp):
    s=max(a0,b0)
    e=min(a1,b1)
    return None if e<s else (s,e)


def yearly_windows(start: pd.Timestamp,end: pd.Timestamp) -> list[tuple[pd.Timestamp,pd.Timestamp]]:
    if end<start:
        raise KRXHistoricalRequestPlanError("end precedes start")
    out=[]
    y=start.year
    while y<=end.year:
        s=max(start,pd.Timestamp(f"{y}-01-01"))
        e=min(end,pd.Timestamp(f"{y}-12-31"))
        if s<=e:
            out.append((s,e))
        y+=1
    return out


def halt_windows(start: pd.Timestamp,end: pd.Timestamp) -> list[tuple[pd.Timestamp,pd.Timestamp]]:
    out=[]
    for s,e in HALT_WINDOWS:
        hit=_intersect(start,end,pd.Timestamp(s),pd.Timestamp(e))
        if hit is not None:
            if (hit[1]-hit[0]).days+1 > 730:
                raise KRXHistoricalRequestPlanError("halt chunk exceeds 730 days")
            out.append(hit)
    return out


def build_private_request_plan(episodes: pd.DataFrame) -> pd.DataFrame:
    """Return private request rows; callers must never expose identifiers in public logs."""
    required={"episode_key","standard_code","short_code","listing_date","source_new_listing","coverage_start","coverage_end"}
    missing=required-set(episodes.columns)
    if missing:
        raise KRXHistoricalRequestPlanError(f"episodes missing columns: {sorted(missing)}")
    if episodes.empty:
        raise KRXHistoricalRequestPlanError("episodes empty")

    rows=[]
    for ep in episodes.itertuples(index=False):
        start=pd.Timestamp(ep.coverage_start)
        end=pd.Timestamp(ep.coverage_end)
        if start<PLAN_START or end>PLAN_END or end<start:
            raise KRXHistoricalRequestPlanError("episode coverage outside frozen plan")
        code=str(ep.short_code)
        standard=str(ep.standard_code).strip().upper()
        key=str(ep.episode_key)
        if len(code)!=6 or not code.isdigit():
            raise KRXHistoricalRequestPlanError("invalid short code")
        if len(standard)!=12 or not standard.isalnum():
            raise KRXHistoricalRequestPlanError("invalid or unresolved standard code")

        for s,e in halt_windows(start,end):
            rows.append({
                "source_family":"KRX_SECURITY_STATUS",
                "dataset":"trading_halt",
                "bld":"dbms/MDC/STAT/issue/MDCSTAT21301",
                "episode_key":key,
                "standard_code":standard,
                "short_code":code,
                "isuCd":standard,
                "isuCd2":code,
                "start":s,
                "end":e,
            })
        for s,e in yearly_windows(start,end):
            rows.append({
                "source_family":"KRX_INVESTOR_FLOW",
                "dataset":"investor_flow_daily",
                "bld":"dbms/MDC/STAT/standard/MDCSTAT02303",
                "episode_key":key,
                "standard_code":standard,
                "short_code":code,
                "isuCd":standard,
                "isuCd2":"",
                "start":s,
                "end":e,
            })
    out=pd.DataFrame(rows)
    if out.empty:
        raise KRXHistoricalRequestPlanError("no per-security requests generated")
    return out.sort_values(["source_family","dataset","episode_key","start"]).reset_index(drop=True)


def metadata_only_summary(episodes: pd.DataFrame, requests: pd.DataFrame) -> dict:
    """Safe public summary: counts only, no security identifiers."""
    by_dataset=requests.groupby("dataset").size().astype(int).to_dict()
    listing_dates = pd.to_datetime(
        episodes.loc[episodes["source_new_listing"].astype(bool), "listing_date"],
        errors="coerce",
    ).dropna().dt.normalize().nunique()
    fixed_identity = 26
    fixed_cleanup = 12
    return {
        "episode_count":int(len(episodes)),
        "request_count":int(len(requests)),
        "request_count_by_dataset":{str(k):int(v) for k,v in sorted(by_dataset.items())},
        "fixed_identity_seed_requests":fixed_identity,
        "dynamic_listing_date_master_requests":int(listing_dates),
        "fixed_cleanup_year_requests":fixed_cleanup,
        "total_planned_before_delisted_price":int(len(requests)+fixed_identity+fixed_cleanup+listing_dates),
        "identifiers_emitted":False,
        "plan_start":PLAN_START.date().isoformat(),
        "plan_end":PLAN_END.date().isoformat(),
    }
