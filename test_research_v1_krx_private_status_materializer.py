import json

import pandas as pd

import research_v1_krx_private_status_materializer as m


def test_materializer_reads_only_completed_halt_raw(monkeypatch):
    state={"status":"COMPLETE","phase_complete":True,"completed":{
        "tid":{"raw_object_sha256":"a"*64,"raw_bytes_size":3,"retrieved_at":"2026-01-08T00:00:00+09:00"}
    }}
    manifest={"tasks":[{
        "task_id":"tid",
        "request_spec":{"kind":"trading_halt","params":{"isuCd2":"123456"}}
    }]}
    def fake_json(root, relpath, git_worktree=None):
        return {"value": state if "batch_state" in relpath else manifest}
    monkeypatch.setattr(m,"read_private_json",fake_json)
    monkeypatch.setattr(m,"read_raw_object",lambda *a,**k:b"raw")
    monkeypatch.setattr(m,"parse_data_marketplace_raw",lambda method,raw:pd.DataFrame([{
        "거래정지일":"20260105","거래재개일":"20260107"
    }]))
    out=m.materialize_private_status_events("/private")
    assert len(out)==1
    assert out.iloc[0]["symbol"]=="123456"
    assert out.iloc[0]["event_type"]=="HALT"
    assert out.iloc[0]["event_start"]==pd.Timestamp("2026-01-05")
    assert out.iloc[0]["event_end"]==pd.Timestamp("2026-01-06")
    assert out.iloc[0]["available_at"] == pd.Timestamp("2026-01-08T00:00:00+09:00")


def test_materializer_rejects_incomplete_phase(monkeypatch):
    monkeypatch.setattr(m,"read_private_json",lambda *a,**k:{"value":{
        "status":"IN_PROGRESS","phase_complete":False
    }})
    try:
        m.materialize_private_status_events("/private")
    except m.KRXPrivateStatusMaterializerError as exc:
        assert "not complete" in str(exc)
    else:
        raise AssertionError("expected fail-closed error")
