import pandas as pd
import pytest

from research_v1_krx_affected_position_scope import (
    KRXAffectedPositionScopeError,
    build_affected_position_scope,
    public_affected_scope_summary,
)

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
    out = build_affected_position_scope(
        positions=_positions(), status_events=_events(), source_contract_fingerprint=FP
    )
    assert list(out["position_id"]) == ["p1"]
    assert list(out["event_type"]) == ["HALT"]
    summary = public_affected_scope_summary(out)
    assert summary["distinct_affected_positions"] == 1
    assert summary["security_identifiers_emitted"] is False
    assert summary["sealed_holdout_authorized"] is False


def test_no_intersection_produces_empty_scope_not_fabricated_economics():
    events = _events().iloc[[1]].copy()
    out = build_affected_position_scope(
        positions=_positions(), status_events=events, source_contract_fingerprint=FP
    )
    assert out.empty


def test_naive_event_availability_fails_closed():
    events = _events()
    events.loc[0, "available_at"] = "2026-01-05 18:00:00"
    with pytest.raises(KRXAffectedPositionScopeError, match="timezone-aware"):
        build_affected_position_scope(
            positions=_positions(), status_events=events, source_contract_fingerprint=FP
        )
