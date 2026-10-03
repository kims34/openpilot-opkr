import copy, json
from pathlib import Path
import pytest
from research_v1_krx_per_security_consent import KRXPerSecurityConsentError, validate_contract, validate_file

PATH=Path("INDEXALERT_KRX_PER_SECURITY_HISTORY_CONSENT_CONTRACT.json")

def _data():
    return json.loads(PATH.read_text(encoding="utf-8"))

def _active_data():
    data=_data()
    data["status"]="USER_AUTHORIZED_EXECUTION_IN_PROGRESS"
    data["user_authorization"]["authorized"]=True
    data["user_authorization"].pop("consumed",None)
    data["execution"]["execution_status"]="IN_PROGRESS"
    data["authority"]["per_security_history_execution_authorized"]=True
    data.pop("interruption",None)
    return data

def _completed_data():
    data=_data()
    data["status"]="EXECUTION_COMPLETE_AUTHORITY_CONSUMED"
    data["interruption"]["resume_authorized"]=True
    data["authority"]["per_security_history_execution_authorized"]=False
    data["resume_authorization"]={
        "exact_user_approval_phrase":"I_AUTHORIZE_INDEXALERT_KRX_PER_SECURITY_HISTORY_RESUME_v1",
        "received_date_kst":"2099-01-01",
        "one_shot":True,
        "reusable":False,
        "same_frozen_scope_only":True,
        "consumed_for_deployment_id":"fresh-resume-deployment",
        "source_revision":"fixed-resume-revision",
        "authorized":False,
        "consumed":True,
    }
    data["resume_execution"]={
        "deployment_id":"fresh-resume-deployment",
        "source_revision":"fixed-resume-revision",
        "start_command":"python research_v1_krx_historical_worker_entrypoint.py --execute-per-security-history",
        "task_count":14296,
        "task_set_fingerprint_sha256":"fb5b883c6fe0e9c15e88aea9bdf874ddd7a11ae8a009c2ddf91c4e4249a8ba38",
        "checkpoint_count_at_start":11750,
        "remaining_task_count_at_start":2546,
        "interruption_evidence_id":"INDEXALERT-KRX-PER-SECURITY-HISTORY-INTERRUPTION-2026-10-03-v1",
        "resume_consent_env":"KRX_PER_SECURITY_HISTORY_RESUME_CONSENT",
        "resume_consent_sentinel":"I_AUTHORIZE_INDEXALERT_KRX_PER_SECURITY_HISTORY_RESUME_v1",
        "execution_status":"COMPLETE",
        "later_stage_auto_authorization":False,
        "status_economics_authorized":False,
        "expected_scope_network_execution_authorized":False,
        "feature_performance_testing_authorized":False,
        "sealed_holdout_authorized":False,
        "genuine_live_authorized":False,
        "live_trading_authorized":False,
    }
    data["completion"]={
        "evidence_id":"INDEXALERT-KRX-PER-SECURITY-HISTORY-EXEC-2026-10-03-v1",
        "completed_task_count":14296,"failed_task_count":0,"phase_status":"COMPLETE","phase_complete":True,
        "task_set_fingerprint_sha256":"fb5b883c6fe0e9c15e88aea9bdf874ddd7a11ae8a009c2ddf91c4e4249a8ba38",
        "resumed_task_count":11750,"network_request_attempt_count":2546,
        "interruption_evidence_id":"INDEXALERT-KRX-PER-SECURITY-HISTORY-INTERRUPTION-2026-10-03-v1",
        "bulk_execution_consent_disabled_again":True,"per_security_consent_disabled_again":True,
        "resume_consent_disabled_again":True,
        "start_command_restored_to_preflight_only":True,"preflight_network_request_attempted_false":True,
        "status_economics_authorized":False,"expected_scope_network_execution_authorized":False,
        "feature_performance_testing_authorized":False,"sealed_holdout_authorized":False,
        "genuine_live_authorized":False,"live_trading_authorized":False,
    }
    return data

def test_committed_per_security_state_is_interrupted_and_consumed():
    out=validate_file()
    assert out["valid"] is True
    assert out["task_count"]==14296
    assert out["authorized"] is False
    assert out["completed"] is False
    assert out["interrupted"] is True
    assert out["authority_consumed"] is True

def test_interrupted_state_requires_relock_and_new_authorization():
    data=_data()
    data["interruption"]["per_security_consent_disabled_again"]=False
    with pytest.raises(KRXPerSecurityConsentError,match="guard lost"):
        validate_contract(data)
    data=_data()
    data["interruption"]["resume_authorized"]=True
    with pytest.raises(KRXPerSecurityConsentError,match="illegally authorized"):
        validate_contract(data)
    data=_data()
    data["interruption"]["resume_requires_new_user_authorization"]=False
    with pytest.raises(KRXPerSecurityConsentError,match="guard lost"):
        validate_contract(data)

def test_interrupted_state_binds_verified_checkpoint():
    out=validate_file()
    assert out["interrupted"] is True
    data=_data()
    data["interruption"]["checkpoint_count_observed"]=11749
    with pytest.raises(KRXPerSecurityConsentError,match="checkpoint count drift"):
        validate_contract(data)
    data=_data()
    data["interruption"]["remaining_task_count"]=2545
    with pytest.raises(KRXPerSecurityConsentError,match="remaining task count drift"):
        validate_contract(data)
    data=_data()
    data["interruption"]["checkpoint_probe_network_request_attempted"]=True
    with pytest.raises(KRXPerSecurityConsentError,match="attempted network"):
        validate_contract(data)

def test_active_state_still_validates_original_exact_binding():
    out=validate_contract(_active_data())
    assert out["authorized"] is True and out["interrupted"] is False
    data=_active_data(); data["execution"]["task_count"]=14295
    with pytest.raises(KRXPerSecurityConsentError,match="execution task count drift"):
        validate_contract(data)

def test_scope_and_later_authority_drift_are_rejected():
    data=_data(); data["prepared_task_set"]["task_count"]=14297
    with pytest.raises(KRXPerSecurityConsentError,match="prepared task count drift"):
        validate_contract(data)
    data=_data(); data["authority"]["status_economics_execution_authorized"]=True
    with pytest.raises(KRXPerSecurityConsentError,match="illegally true"):
        validate_contract(data)

def test_completed_state_remains_fail_closed():
    out=validate_contract(_completed_data())
    assert out["completed"] is True and out["authority_consumed"] is True
    data=_completed_data(); data["completion"]["completed_task_count"]=14295
    with pytest.raises(KRXPerSecurityConsentError,match="completion task count drift"):
        validate_contract(data)
    data=_completed_data(); data["completion"]["sealed_holdout_authorized"]=True
    with pytest.raises(KRXPerSecurityConsentError,match="illegally true"):
        validate_contract(data)
