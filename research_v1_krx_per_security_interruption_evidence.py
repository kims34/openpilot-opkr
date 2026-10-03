"""Validator for public-safe PER_SECURITY_HISTORY interruption evidence."""
from __future__ import annotations
import json, re
from pathlib import Path
from typing import Any, Mapping

PATH=Path("INDEXALERT_KRX_PER_SECURITY_HISTORY_INTERRUPTION_EVIDENCE.json")
SHA=re.compile(r"^[0-9a-f]{64}$")
class KRXPerSecurityInterruptionEvidenceError(ValueError): pass
def _r(c,m):
    if not c: raise KRXPerSecurityInterruptionEvidenceError(m)

def validate_evidence(d:Mapping[str,Any])->dict[str,Any]:
    _r(isinstance(d,Mapping),"evidence must be object")
    _r(d.get("schema_version")=="1","schema drift")
    _r(d.get("evidence_id")=="INDEXALERT-KRX-PER-SECURITY-HISTORY-INTERRUPTION-2026-10-03-v1","evidence id drift")
    _r(d.get("stage")=="PER_SECURITY_HISTORY","stage drift")
    _r(d.get("status")=="INTERRUPTED_CHECKPOINT_VERIFIED_AUTHORITY_CONSUMED","status drift")
    x=d.get("original_execution") or {}
    _r(x.get("deployment_id")=="bc79d1b5-5fb8-46c7-8067-682e61947014","deployment drift")
    _r(x.get("source_revision")=="9009c48a00394063c813d29219507ee2190ce09e","source revision drift")
    _r(x.get("crashed_at_utc")=="2026-10-03T00:45:16Z","crash time drift")
    _r(x.get("error_class")=="KRXHistoricalRequestExecutorError","error class drift")
    _r(x.get("reason_code")=="ALPHANUMERIC_SHORT_CODE_VALIDATOR_MISMATCH","reason drift")
    _r(x.get("raw_security_identifier_emitted") is False,"identifier leak")
    s=d.get("frozen_scope") or {}
    _r(int(s.get("expected_task_count",-1))==14296,"expected count drift")
    _r(SHA.fullmatch(str(s.get("task_set_fingerprint_sha256") or "")) is not None,"fingerprint invalid")
    _r(s.get("task_set_fingerprint_sha256")=="fb5b883c6fe0e9c15e88aea9bdf874ddd7a11ae8a009c2ddf91c4e4249a8ba38","fingerprint drift")
    _r(s.get("private_task_manifest_metadata_sha256")=="0d98f45168cedeecc013e95c71abe661ca1fac9df0403ba477d2f5653572c116","manifest hash drift")
    p=d.get("checkpoint_probe") or {}
    _r(p.get("deployment_id")=="92439b24-644a-4d3d-a888-9e0ba568bfac","probe deployment drift")
    _r(p.get("source_revision")=="d156f0dc6056924a798679bd9e93e1f2eb0241fc","probe source drift")
    _r(p.get("mode")=="STATUS_PER_SECURITY_HISTORY","probe mode drift")
    _r(p.get("status")=="IN_PROGRESS","probe status drift")
    _r(int(p.get("completed_task_count",-1))==11750,"checkpoint count drift")
    _r(int(p.get("remaining_task_count",-1))==2546,"remaining count drift")
    _r(int(p.get("failed_task_count",-1))==0,"failed count drift")
    _r(p.get("phase_complete") is False,"phase_complete drift")
    _r(p.get("task_set_fingerprint_sha256")==s.get("task_set_fingerprint_sha256"),"probe fingerprint drift")
    _r(p.get("network_request_attempted") is False,"probe attempted network")
    _r(p.get("security_identifiers_emitted") is False,"probe identifiers emitted")
    _r(p.get("raw_rows_emitted") is False,"probe raw rows emitted")
    b=d.get("boundary") or {}
    for k in ("original_user_authority_consumed","bulk_execution_consent_disabled_again","per_security_consent_disabled_again","configured_start_command_restored_to_preflight_only","restart_policy_never","resume_requires_new_user_authorization"):
        _r(b.get(k) is True,f"{k} guard lost")
    for k in ("resume_authorized","status_economics_authorized","expected_scope_network_execution_authorized","feature_performance_testing_authorized","sealed_holdout_authorized","genuine_live_authorized","live_trading_authorized"):
        _r(b.get(k) is False,f"{k} illegally true")
    _r(b.get("resume_consent_env")=="KRX_PER_SECURITY_HISTORY_RESUME_CONSENT","resume consent env drift")
    _r(b.get("resume_consent_sentinel")=="I_AUTHORIZE_INDEXALERT_KRX_PER_SECURITY_HISTORY_RESUME_v1","resume consent sentinel drift")
    _r(int(p["completed_task_count"])+int(p["remaining_task_count"])==int(s["expected_task_count"]),"checkpoint accounting drift")
    return {"valid":True,"completed_task_count":11750,"remaining_task_count":2546,"failed_task_count":0,"resume_authorized":False}

def validate_file(path:Path=PATH):
    return validate_evidence(json.loads(path.read_text(encoding="utf-8")))
if __name__=="__main__":
    print(json.dumps(validate_file(),ensure_ascii=False,indent=2))
