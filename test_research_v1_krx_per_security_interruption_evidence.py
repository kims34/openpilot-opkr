import copy, json
from pathlib import Path
import pytest
from research_v1_krx_per_security_interruption_evidence import KRXPerSecurityInterruptionEvidenceError,validate_evidence,validate_file
PATH=Path("INDEXALERT_KRX_PER_SECURITY_HISTORY_INTERRUPTION_EVIDENCE.json")

def _d(): return json.loads(PATH.read_text(encoding="utf-8"))

def test_committed_interruption_evidence():
    out=validate_file()
    assert out=={"valid":True,"completed_task_count":11750,"remaining_task_count":2546,"failed_task_count":0,"resume_authorized":False}

def test_rejects_checkpoint_or_fingerprint_drift():
    d=_d(); d["checkpoint_probe"]["completed_task_count"]=11749
    with pytest.raises(KRXPerSecurityInterruptionEvidenceError,match="checkpoint count drift"): validate_evidence(d)
    d=_d(); d["checkpoint_probe"]["task_set_fingerprint_sha256"]="0"*64
    with pytest.raises(KRXPerSecurityInterruptionEvidenceError,match="probe fingerprint drift"): validate_evidence(d)

def test_rejects_network_or_authority_escalation():
    d=_d(); d["checkpoint_probe"]["network_request_attempted"]=True
    with pytest.raises(KRXPerSecurityInterruptionEvidenceError,match="attempted network"): validate_evidence(d)
    d=_d(); d["boundary"]["resume_authorized"]=True
    with pytest.raises(KRXPerSecurityInterruptionEvidenceError,match="illegally true"): validate_evidence(d)
    d=_d(); d["boundary"]["sealed_holdout_authorized"]=True
    with pytest.raises(KRXPerSecurityInterruptionEvidenceError,match="illegally true"): validate_evidence(d)


def test_rejects_resume_consent_contract_drift():
    d=_d(); d["boundary"]["resume_consent_env"]="WRONG"
    with pytest.raises(KRXPerSecurityInterruptionEvidenceError,match="resume consent env drift"): validate_evidence(d)
    d=_d(); d["boundary"]["resume_consent_sentinel"]="WRONG"
    with pytest.raises(KRXPerSecurityInterruptionEvidenceError,match="resume consent sentinel drift"): validate_evidence(d)
