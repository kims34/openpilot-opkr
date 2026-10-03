import json
from pathlib import Path

import pytest

from research_v1_krx_per_security_consent import (
    KRXPerSecurityConsentError,
    validate_contract,
)

PATH = Path("INDEXALERT_KRX_PER_SECURITY_HISTORY_CONSENT_CONTRACT.json")
RESUME = "I_AUTHORIZE_INDEXALERT_KRX_PER_SECURITY_HISTORY_RESUME_v1"
TASK_SHA = "fb5b883c6fe0e9c15e88aea9bdf874ddd7a11ae8a009c2ddf91c4e4249a8ba38"


def _data():
    return json.loads(PATH.read_text(encoding="utf-8"))


def _resume_in_progress():
    data = _data()
    data["status"] = "RESUME_USER_AUTHORIZED_EXECUTION_IN_PROGRESS"
    data["interruption"]["resume_authorized"] = True
    data["authority"]["per_security_history_execution_authorized"] = True
    data["resume_authorization"] = {
        "exact_user_approval_phrase": RESUME,
        "authorized": True,
        "consumed": False,
        "one_shot": True,
        "reusable": False,
        "same_frozen_scope_only": True,
        "received_date_kst": "2026-10-03",
        "consumed_for_deployment_id": "resume-deployment",
        "source_revision": "resume-revision",
    }
    data["resume_execution"] = {
        "deployment_id": "resume-deployment",
        "source_revision": "resume-revision",
        "start_command": "python research_v1_krx_historical_worker_entrypoint.py --execute-per-security-history",
        "task_count": 14296,
        "task_set_fingerprint_sha256": TASK_SHA,
        "checkpoint_count_at_start": 11750,
        "remaining_task_count_at_start": 2546,
        "interruption_evidence_id": "INDEXALERT-KRX-PER-SECURITY-HISTORY-INTERRUPTION-2026-10-03-v1",
        "resume_consent_env": "KRX_PER_SECURITY_HISTORY_RESUME_CONSENT",
        "resume_consent_sentinel": RESUME,
        "execution_status": "IN_PROGRESS",
        "later_stage_auto_authorization": False,
        "status_economics_authorized": False,
        "expected_scope_network_execution_authorized": False,
        "feature_performance_testing_authorized": False,
        "sealed_holdout_authorized": False,
        "genuine_live_authorized": False,
        "live_trading_authorized": False,
    }
    return data


def _resume_complete():
    data = _resume_in_progress()
    data["status"] = "EXECUTION_COMPLETE_AUTHORITY_CONSUMED"
    data["authority"]["per_security_history_execution_authorized"] = False
    data["resume_authorization"]["authorized"] = False
    data["resume_authorization"]["consumed"] = True
    data["resume_execution"]["execution_status"] = "COMPLETE"
    data["completion"] = {
        "evidence_id": "INDEXALERT-KRX-PER-SECURITY-HISTORY-EXEC-2026-10-03-v1",
        "completed_task_count": 14296,
        "failed_task_count": 0,
        "resumed_task_count": 11750,
        "network_request_attempt_count": 2546,
        "phase_status": "COMPLETE",
        "phase_complete": True,
        "task_set_fingerprint_sha256": TASK_SHA,
        "interruption_evidence_id": "INDEXALERT-KRX-PER-SECURITY-HISTORY-INTERRUPTION-2026-10-03-v1",
        "bulk_execution_consent_disabled_again": True,
        "per_security_consent_disabled_again": True,
        "resume_consent_disabled_again": True,
        "start_command_restored_to_preflight_only": True,
        "preflight_network_request_attempted_false": True,
        "status_economics_authorized": False,
        "expected_scope_network_execution_authorized": False,
        "feature_performance_testing_authorized": False,
        "sealed_holdout_authorized": False,
        "genuine_live_authorized": False,
        "live_trading_authorized": False,
    }
    return data


def test_current_interruption_remains_unauthorized():
    out = validate_contract(_data())
    assert out["valid"] is True
    assert out["authorized"] is False
    assert out["interrupted"] is True
    assert out["resuming"] is False
    assert out["authority_consumed"] is True


def test_resume_in_progress_requires_new_bound_authority():
    out = validate_contract(_resume_in_progress())
    assert out["valid"] is True
    assert out["authorized"] is True
    assert out["resuming"] is True
    assert out["completed"] is False
    assert out["authority_consumed"] is False

    data = _resume_in_progress()
    data["resume_authorization"]["exact_user_approval_phrase"] = "WRONG"
    with pytest.raises(KRXPerSecurityConsentError, match="resume approval phrase drift"):
        validate_contract(data)

    data = _resume_in_progress()
    data["resume_execution"]["deployment_id"] = "different"
    with pytest.raises(KRXPerSecurityConsentError, match="resume execution deployment drift"):
        validate_contract(data)


def test_resume_in_progress_cannot_change_frozen_scope():
    data = _resume_in_progress()
    data["resume_execution"]["task_count"] = 14295
    with pytest.raises(KRXPerSecurityConsentError, match="resume task count drift"):
        validate_contract(data)

    data = _resume_in_progress()
    data["resume_execution"]["task_set_fingerprint_sha256"] = "0" * 64
    with pytest.raises(KRXPerSecurityConsentError, match="resume task-set fingerprint drift"):
        validate_contract(data)

    data = _resume_in_progress()
    data["resume_execution"]["checkpoint_count_at_start"] = 11749
    with pytest.raises(KRXPerSecurityConsentError, match="resume checkpoint count drift"):
        validate_contract(data)


def test_resume_completion_consumes_authority_and_requires_exact_accounting():
    out = validate_contract(_resume_complete())
    assert out["valid"] is True
    assert out["authorized"] is False
    assert out["completed"] is True
    assert out["authority_consumed"] is True

    data = _resume_complete()
    data["resume_authorization"]["consumed"] = False
    with pytest.raises(KRXPerSecurityConsentError, match="not consumed"):
        validate_contract(data)

    data = _resume_complete()
    data["completion"]["resumed_task_count"] = 11749
    with pytest.raises(KRXPerSecurityConsentError, match="resumed task count drift"):
        validate_contract(data)

    data = _resume_complete()
    data["completion"]["network_request_attempt_count"] = 2545
    with pytest.raises(KRXPerSecurityConsentError, match="network request count drift"):
        validate_contract(data)


def test_resume_completion_relocks_all_three_consents_and_later_stages():
    data = _resume_complete()
    data["completion"]["resume_consent_disabled_again"] = False
    with pytest.raises(KRXPerSecurityConsentError, match="resume consent guard lost"):
        validate_contract(data)

    data = _resume_complete()
    data["completion"]["sealed_holdout_authorized"] = True
    with pytest.raises(KRXPerSecurityConsentError, match="illegally true"):
        validate_contract(data)
