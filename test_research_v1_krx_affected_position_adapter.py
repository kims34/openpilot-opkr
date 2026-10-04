from datetime import date

import pandas as pd

from research_v1_core import DecisionRecord
from research_v1_krx_affected_position_adapter import (
    decision_records_to_position_intervals,
    normalized_status_frames_to_events,
)
from research_v1_krx_affected_position_scope import build_affected_position_scope


def _record(symbol="111111"):
    return DecisionRecord(
        decision_day=date(2026,1,2), entry_day=date(2026,1,5), symbol=symbol,
        score=1.0, entry_price=100.0, horizon=3, target_return=.03,
        stop_return=-.02, cost_return=.001, outcome="TIME",
        gross_return=.01, net_return=.009, exit_day=date(2026,1,7), exit_price=101.0,
    )


def test_decision_record_and_halt_join_end_to_end_offline():
    positions = decision_records_to_position_intervals([_record()])
    halts = pd.DataFrame([{
        "symbol":"111111","halt_date":"2026-01-06","resume_date":"2026-01-07",
        "available_at":"2026-01-06T18:00:00+09:00",
    }])
    empty_cleanup = pd.DataFrame(columns=["symbol","cleanup_start","cleanup_end","available_at"])
    empty_delist = pd.DataFrame(columns=["symbol","delisting_date","available_at"])
    events = normalized_status_frames_to_events(
        halts=halts, cleanup=empty_cleanup, delistings=empty_delist
    )
    out = build_affected_position_scope(
        positions=positions, status_events=events, source_contract_fingerprint="a"*64
    )
    assert len(out) == 1
    assert out.iloc[0]["event_type"] == "HALT"


def test_unaffected_record_stays_out_of_exact_economics_scope():
    positions = decision_records_to_position_intervals([_record("222222")])
    halts = pd.DataFrame([{
        "symbol":"111111","halt_date":"2026-01-06","resume_date":"2026-01-07",
        "available_at":"2026-01-06T18:00:00+09:00",
    }])
    events = normalized_status_frames_to_events(
        halts=halts,
        cleanup=pd.DataFrame(columns=["symbol","cleanup_start","cleanup_end","available_at"]),
        delistings=pd.DataFrame(columns=["symbol","delisting_date","available_at"]),
    )
    out = build_affected_position_scope(
        positions=positions, status_events=events, source_contract_fingerprint="a"*64
    )
    assert out.empty
