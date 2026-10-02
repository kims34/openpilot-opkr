import pandas as pd
import pytest

from research_v1_krx_historical_request_planner import (
    KRXHistoricalRequestPlanError,
    build_private_request_plan,
    halt_windows,
    metadata_only_summary,
    yearly_windows,
)


def _episodes():
    return pd.DataFrame([
        {
            "episode_key":"KOSPI|005930|1975-06-11",
            "short_code":"005930",
            "coverage_start":pd.Timestamp("2015-06-15"),
            "coverage_end":pd.Timestamp("2026-10-01"),
        },
        {
            "episode_key":"KOSPI|123456|2020-01-02",
            "short_code":"123456",
            "coverage_start":pd.Timestamp("2020-01-02"),
            "coverage_end":pd.Timestamp("2022-12-30"),
        },
    ])


def test_full_period_chunks_are_six_halt_and_twelve_yearly():
    assert len(halt_windows(pd.Timestamp("2015-06-15"),pd.Timestamp("2026-10-01"))) == 6
    assert len(yearly_windows(pd.Timestamp("2015-06-15"),pd.Timestamp("2026-10-01"))) == 12


def test_episode_intersection_reduces_requests():
    req=build_private_request_plan(_episodes())
    first=req[req["episode_key"].eq("KOSPI|005930|1975-06-11")]
    second=req[req["episode_key"].eq("KOSPI|123456|2020-01-02")]
    assert len(first[first["dataset"].eq("trading_halt")]) == 6
    assert len(first[first["dataset"].eq("investor_flow_daily")]) == 12
    assert len(second[second["dataset"].eq("trading_halt")]) == 2
    assert len(second[second["dataset"].eq("investor_flow_daily")]) == 3


def test_public_summary_contains_counts_not_identifiers():
    eps=_episodes()
    req=build_private_request_plan(eps)
    s=metadata_only_summary(eps,req)
    assert s["episode_count"] == 2
    assert s["request_count"] == 23
    assert s["total_planned_before_delisted_price"] == 38
    assert s["identifiers_emitted"] is False
    raw=str(s)
    assert "005930" not in raw
    assert "123456" not in raw


def test_invalid_episode_fails_closed():
    eps=_episodes()
    eps.loc[0,"coverage_end"]=pd.Timestamp("2027-01-01")
    with pytest.raises(KRXHistoricalRequestPlanError,match="outside frozen plan"):
        build_private_request_plan(eps)
