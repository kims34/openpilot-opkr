import hashlib
import json
import pandas as pd
import pytest
import research_v1_krx_private_status_materializer as m

def _sha(value):
    return hashlib.sha256(json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(",",":"),default=str).encode()).hexdigest()

def _fixture(monkeypatch, *, resume="20260107"):
    spec={"kind":"trading_halt","params":{"isuCd":"KR7000000000","isuCd2":"123456","strtDd":"20260101","endDd":"20260131"}}
    resolved={"kind":"trading_halt","source_family":"KRX_SECURITY_STATUS","dataset_identifier":"MDCSTAT21301","access_route":"DATA_MARKETPLACE_AUTHENTICATED_WEB_SESSION","bld":"dbms/MDC/STAT/issue/MDCSTAT21301","method":"csv","menu_id":"MDC0202","params":spec["params"],"pinned_client_commit":"pinned"}
    req={"bld":resolved["bld"],"method":resolved["method"],"menu_id":resolved["menu_id"],"params":resolved["params"],"pinned_client_commit":"pinned"}
    req_sha=_sha(req)
    receipt={"receipt_version":"2026-10-01.v2","source_family":"KRX_SECURITY_STATUS","intended_use_scope":"historical_research_only","access_route":resolved["access_route"],"dataset_identifier":"MDCSTAT21301","authorization_evidence_reference":"test","authorization_evidence_fingerprint_sha256":"b"*64,"client_revision":"test","retrieved_at":"2026-01-08T00:00:00+09:00","request_metadata_sha256":req_sha,"response_schema_sha256":"c"*64,"response_payload_sha256":"a"*64,"response_rows":1,"response_columns":["거래정지일","거래재개일"],"public_contract_evidence_version":"test","public_contract_evidence_fingerprint_sha256":"d"*64,"alpha_or_final_judge_promotion_authorized":False,"sealed_holdout_authorized":False,"live_trading_authorized":False}
    body={k:receipt[k] for k in m.verify_receipt_fingerprint.__globals__["RECEIPT_BODY_FIELDS"]}
    receipt["receipt_fingerprint_sha256"]=_sha(body)
    state={"status":"COMPLETE","phase_complete":True,"completed":{"tid":{"raw_object_sha256":"a"*64,"raw_bytes_size":3,"request_metadata_sha256":req_sha}}}
    manifest={"tasks":[{"task_id":"tid","source_family":"KRX_SECURITY_STATUS","request_spec":spec}]}
    cp={"state":"COMPLETE","raw_object_sha256":"a"*64,"receipt_relpath":"receipts/test.json","receipt_fingerprint_sha256":receipt["receipt_fingerprint_sha256"]}
    def fake_json(root,relpath,git_worktree=None):
        if relpath=="batch_state/PER_SECURITY_HISTORY.json": return {"value":state}
        if relpath=="task_manifests/per-security-history-v3.json": return {"value":manifest}
        if relpath.startswith("checkpoints/"): return {"value":cp}
        if relpath=="receipts/test.json": return {"value":receipt}
        raise AssertionError(relpath)
    monkeypatch.setattr(m,"read_private_json",fake_json)
    monkeypatch.setattr(m,"read_raw_object",lambda *a,**k:b"raw")
    monkeypatch.setattr(m,"validate_request_spec",lambda x:resolved)
    monkeypatch.setattr(m,"parse_data_marketplace_raw",lambda method,raw:pd.DataFrame([{"거래정지일":"20260105","거래재개일":resume}]))
    return state

def test_materializer_uses_checkpoint_receipt_provenance(monkeypatch):
    _fixture(monkeypatch)
    out=m.materialize_private_status_events("/private")
    assert len(out)==1
    assert out.iloc[0]["symbol"]=="123456"
    assert out.iloc[0]["event_start"]==pd.Timestamp("2026-01-05")
    assert out.iloc[0]["event_end"]==pd.Timestamp("2026-01-06")
    assert out.iloc[0]["available_at"]==pd.Timestamp("2026-01-08T00:00:00+09:00")

def test_materializer_rejects_open_ended_halt(monkeypatch):
    _fixture(monkeypatch,resume=None)
    with pytest.raises(m.KRXPrivateStatusMaterializerError,match="open-ended HALT"):
        m.materialize_private_status_events("/private")

def test_materializer_rejects_incomplete_phase(monkeypatch):
    monkeypatch.setattr(m,"read_private_json",lambda *a,**k:{"value":{"status":"IN_PROGRESS","phase_complete":False}})
    with pytest.raises(m.KRXPrivateStatusMaterializerError,match="not complete"):
        m.materialize_private_status_events("/private")
