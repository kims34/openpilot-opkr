import json
from pathlib import Path

import pytest

from research_v1_krx_per_security_consent import (
    KRXPerSecurityConsentError,
    validate_contract,
    validate_file,
)

PATH = Path("INDEXALERT_KRX_PER_SECURITY_HISTORY_CONSENT_CONTRACT.json")


def _data():
    return json.loads(PATH.read_text(encoding="utf-8"))


def test_committed_per_security_consent_is_authorized_in_progress():
    out = validate_file()
    assert out["valid"] is True
    assert out["task_count"] == 14296
    assert out["authorized"] is True
    assert out["one_shot"] is True
    assert out["later_stage_auto_authorization"] is False


def test_per_security_consent_rejects_authorization_loss_or_reuse():
    data = _data()
    data["user_authorization"]["authorized"] = False
    with pytest.raises(KRXPerSecurityConsentError, match="authorized execution record lost"):
        validate_contract(data)

    data = _data()
    data["user_authorization"]["earlier_stage_authorization_reusable"] = True
    with pytest.raises(KRXPerSecurityConsentError, match="reuse illegally enabled"):
        validate_contract(data)


def test_per_security_consent_rejects_task_scope_drift():
    data = _data()
    data["prepared_task_set"]["task_count"] = 14297
    with pytest.raises(KRXPerSecurityConsentError, match="prepared task count drift"):
        validate_contract(data)

    data = _data()
    data["prepared_task_set"]["private_task_manifest_metadata_sha256"] = "0" * 64
    with pytest.raises(KRXPerSecurityConsentError, match="private manifest hash drift"):
        validate_contract(data)


def test_per_security_consent_cannot_authorize_later_stages():
    data = _data()
    data["authority"]["status_economics_execution_authorized"] = True
    with pytest.raises(KRXPerSecurityConsentError, match="illegally true"):
        validate_contract(data)

    data = _data()
    data["post_run_lock"]["later_stage_auto_authorization"] = True
    with pytest.raises(KRXPerSecurityConsentError, match="auto authority"):
        validate_contract(data)


def test_active_per_security_execution_is_exactly_bound():
    data = _data()
    execution = data["execution"]
    assert execution["deployment_id"] == "bc79d1b5-5fb8-46c7-8067-682e61947014"
    assert execution["task_count"] == 14296
    assert execution["execution_status"] == "IN_PROGRESS"
    assert execution["later_stage_auto_authorization"] is False

    data = _data()
    data["execution"]["task_count"] = 14295
    with pytest.raises(KRXPerSecurityConsentError, match="execution task count drift"):
        validate_contract(data)

    data = _data()
    data["execution"]["status_economics_authorized"] = True
    with pytest.raises(KRXPerSecurityConsentError, match="illegally true"):
        validate_contract(data)


def _completed_data():
    data = _data()
    data["status"] = "EXECUTION_COMPLETE_AUTHORITY_CONSUMED"
    data["user_authorization"]["authorized"] = False
    data["user_authorization"]["consumed"] = True
    data["execution"]["execution_status"] = "COMPLETE"
    data["authority"]["per_security_history_execution_authorized"] = False
    data["completion"] = {
        "evidence_id": "INDEXALERT-KRX-PER-SECURITY-HISTORY-EXEC-2026-10-03-v1",
        "completed_task_count": 14296,
        "failed_task_count": 0,
        "phase_status": "COMPLETE",
        "phase_complete": True,
        "task_set_fingerprint_sha256": "fb5b883c6fe0e9c15e88aea9bdf874ddd7a11ae8a009c2ddf91c4e4249a8ba38",
        "bulk_execution_consent_disabled_again": True,
        "per_security_consent_disabled_again": True,
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


def test_completed_per_security_state_requires_consumed_authority_and_relock():
    out = validate_contract(_completed_data())
    assert out["valid"] is True
    assert out["authorized"] is False
    assert out["completed"] is True
    assert out["authority_consumed"] is True

    data = _completed_data()
    data["user_authorization"]["consumed"] = False
    with pytest.raises(KRXPerSecurityConsentError, match="not marked consumed"):
        validate_contract(data)

    data = _completed_data()
    data["completion"]["preflight_network_request_attempted_false"] = False
    with pytest.raises(KRXPerSecurityConsentError, match="guard lost"):
        validate_contract(data)


def test_completed_per_security_state_rejects_incomplete_or_later_authority():
    data = _completed_data()
    data["completion"]["completed_task_count"] = 14295
    with pytest.raises(KRXPerSecurityConsentError, match="completion task count drift"):
        validate_contract(data)

    data = _completed_data()
    data["completion"]["status_economics_authorized"] = True
    with pytest.raises(KRXPerSecurityConsentError, match="illegally true"):
        validate_contract(data)


def test_in_progress_state_rejects_premature_completion_record():
    data = _data()
    data["completion"] = {"phase_status": "COMPLETE"}
    with pytest.raises(KRXPerSecurityConsentError, match="prematurely present"):
        validate_contract(data)
