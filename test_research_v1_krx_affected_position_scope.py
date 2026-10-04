import pandas as pd
import pytest

from research_v1_krx_affected_position_scope import KRXAffectedPositionScopeError, build_affected_position_scope, public_affected_scope_summary
from research_v1_krx_affected_position_adapter import normalized_status_frames_to_events

FP = "a" * 64

def _positions():
    return pd.DataFrame([
        {"position_id":"p1","symbol":"111111","entry_day":"2026-01-02","exit_day":"2026-01-08","affected_qty":10,"entry_cost_basis_total":1000},
        {"position_id":"p2","symbol":"222222","entry_day":"2026-01-02","exit_day":"2026-01-03","affected_qty":5,"entry_cost_basis_total":500},
    ])

def _events():
    return pd.DataFrame([
        {"symbol":"111111","event_type":"HALT","event_start":"2026-01-05","event_end":"2026-01-06","available_at":"2026-01-05T18:00:00+09:00"},
        {"symbol":"222222","event_type":"DELISTING","event_start":"2026-01-10","event_end":"2026-01-10","available_at":"2026-01-09T18:00:00+09:00"},
    ])

def test_only_intersecting_position_becomes_expected_economics_scope():
    out=build_affected_position_scope(positions=_positions(),status_events=_events(),source_contract_fingerprint=FP)
    assert list(out["position_id"])==["p1"]
    assert list(out["event_type"])==["HALT"]
    summary=public_affected_scope_summary(out)
    assert summary["distinct_affected_positions"]==1
    assert summary["security_identifiers_emitted"] is False
    assert summary["sealed_holdout_authorized"] is False

def test_no_intersection_produces_empty_scope_not_fabricated_economics():
    out=build_affected_position_scope(positions=_positions(),status_events=_events().iloc[[1]].copy(),source_contract_fingerprint=FP)
    assert out.empty

def test_naive_event_availability_fails_closed():
    events=_events(); events.loc[0,"available_at"]="2026-01-05 18:00:00"
    with pytest.raises(KRXAffectedPositionScopeError,match="timezone-aware"):
        build_affected_position_scope(positions=_positions(),status_events=events,source_contract_fingerprint=FP)

@pytest.mark.parametrize("field,bad", [("affected_qty",float("nan")),("affected_qty",float("inf")),("entry_cost_basis_total",float("nan")),("entry_cost_basis_total",float("inf"))])
def test_nonfinite_position_economics_fail_closed(field,bad):
    p=_positions(); p.loc[0,field]=bad
    with pytest.raises(KRXAffectedPositionScopeError,match="finite and positive"):
        build_affected_position_scope(positions=p,status_events=_events(),source_contract_fingerprint=FP)

def test_open_ended_halt_requires_attested_resume():
    halts=pd.DataFrame([{"symbol":"111111","halt_date":"2026-01-05","resume_date":pd.NaT,"available_at":"2026-01-05T18:00:00+09:00"}])
    empty_cleanup=pd.DataFrame(columns=["symbol","cleanup_start","cleanup_end","available_at"])
    empty_delist=pd.DataFrame(columns=["symbol","delisting_date","available_at"])
    with pytest.raises(ValueError,match="open-ended HALT"):
        normalized_status_frames_to_events(halts=halts,cleanup=empty_cleanup,delistings=empty_delist)
