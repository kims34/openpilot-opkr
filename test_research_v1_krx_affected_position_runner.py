import pandas as pd

from research_v1_krx_affected_position_runner import run


def test_runner_emits_only_aggregate_scope(tmp_path):
    positions = pd.DataFrame([{
        "position_id":"private-p1","symbol":"111111","entry_day":"2026-01-05",
        "exit_day":"2026-01-07","affected_qty":1.0,"entry_cost_basis_total":100.0,
    }])
    events = pd.DataFrame([{
        "symbol":"111111","event_type":"HALT","event_start":"2026-01-06",
        "event_end":"2026-01-06","available_at":"2026-01-06T18:00:00+09:00",
    }])
    pp=tmp_path/"positions.csv"; sp=tmp_path/"events.csv"
    positions.to_csv(pp,index=False); events.to_csv(sp,index=False)
    out=run(positions_path=str(pp),status_events_path=str(sp),source_contract_fingerprint="a"*64)
    assert out["affected_position_event_count"] == 1
    assert out["distinct_affected_positions"] == 1
    assert out["network_request_attempted"] is False
    assert out["raw_rows_emitted"] is False
    assert out["position_identifiers_emitted"] is False
    assert out["security_identifiers_emitted"] is False
    assert "111111" not in str(out)
    assert "private-p1" not in str(out)
