import json
from pathlib import Path

import pytest

from research_v1_krx_per_security_resume_consent import (
    KRXPerSecurityResumeConsentError,
    validate_contract,
    validate_file,
)

PATH = Path("INDEXALERT_KRX_PER_SECURITY_HISTORY_RESUME_CONSENT_CONTRACT.json")


def _data():
    return json.loads(PATH.read_text(encoding="utf-8"))


def _verified_waiting():
    data = _data()
    data["status"] = "FIX_VERIFIED_WAITING_FOR_EXPLICIT_USER_AUTHORIZATION"
    data["code_fix"]["source_revision"] = "fixed-revision"
    data["code_fix"]["official_krx_ci_passed"] = True
    data["runtime_gate"]["source_revision"] = "fixed-revision"
    data["runtime_gate"]["preflight_verified"] = True
    data["runtime_gate"]["preflight_deployment_id"] = "preflight-deployment"
    data["runtime_gate"]["preflight_source_revision"] = "fixed-revision"
    data["runtime_gate"]["preflight_network_request_attempted"] = False
    data["runtime_gate"]["preflight_dockerfile"] = "Dockerfile.krx-historical-worker"
    return data


def _ready():
    data = _verified_waiting()
    data["status"] = "USER_AUTHORIZED_RESUME_READY"
    data["user_authorization"]["authorized"] = True
    data["user_authorization"]["consumed"] = False
    data["user_authorization"]["received_date_kst"] = "2099-01-01"
    data["runtime_gate"]["deployment_id"] = "fresh-deployment"
    data["authority"]["resume_network_execution_authorized"] = True
    return data


def test_committed_resume_contract_is_waiting_and_unauthorized():
    out = validate_file()
    assert out["valid"] is True
    assert out["status"] == "WAITING_FOR_EXPLICIT_USER_AUTHORIZATION"
    assert out["checkpoint_completed_task_count"] == 11750
    assert out["remaining_task_count"] == 2546
    assert out["authorized"] is False
    assert out["completed"] is False


def test_verified_fix_can_be_bound_before_user_authorization():
    out = validate_contract(_verified_waiting())
    assert out["valid"] is True
    assert out["status"] == "FIX_VERIFIED_WAITING_FOR_EXPLICIT_USER_AUTHORIZATION"
    assert out["authorized"] is False

    data = _verified_waiting()
    data["runtime_gate"]["preflight_network_request_attempted"] = True
    with pytest.raises(KRXPerSecurityResumeConsentError, match="attempted network"):
        validate_contract(data)

    data = _verified_waiting()
    data["code_fix"]["official_krx_ci_passed"] = False
    with pytest.raises(KRXPerSecurityResumeConsentError, match="CI proof missing"):
        validate_contract(data)

    data = _verified_waiting()
    data["runtime_gate"]["preflight_source_revision"] = "other"
    with pytest.raises(KRXPerSecurityResumeConsentError, match="preflight source drift"):
        validate_contract(data)


def test_resume_ready_requires_new_bound_source_and_fresh_deployment():
    out = validate_contract(_ready())
    assert out["authorized"] is True

    data = _ready()
    data["runtime_gate"]["deployment_id"] = "bc79d1b5-5fb8-46c7-8067-682e61947014"
    with pytest.raises(KRXPerSecurityResumeConsentError, match="cannot be reused"):
        validate_contract(data)

    data = _ready()
    data["code_fix"]["source_revision"] = "other"
    with pytest.raises(KRXPerSecurityResumeConsentError, match="source binding drift"):
        validate_contract(data)


def test_old_or_missing_authority_cannot_resume():
    data = _ready()
    data["user_authorization"]["authorized"] = False
    with pytest.raises(KRXPerSecurityResumeConsentError, match="authorization record lost"):
        validate_contract(data)

    data = _data()
    data["authority"]["resume_network_execution_authorized"] = True
    with pytest.raises(KRXPerSecurityResumeConsentError, match="illegally true"):
        validate_contract(data)


def test_resume_contract_preserves_frozen_checkpoint_and_later_stage_boundaries():
    data = _ready()
    data["frozen_scope"]["checkpoint_completed_task_count"] = 11749
    with pytest.raises(KRXPerSecurityResumeConsentError, match="checkpoint count drift"):
        validate_contract(data)

    data = _ready()
    data["authority"]["sealed_holdout_authorized"] = True
    with pytest.raises(KRXPerSecurityResumeConsentError, match="illegally true"):
        validate_contract(data)


def test_waiting_state_rejects_premature_fix_or_preflight_binding():
    data = _data()
    data["code_fix"]["source_revision"] = "premature"
    with pytest.raises(KRXPerSecurityResumeConsentError, match="prematurely bound"):
        validate_contract(data)

    data = _data()
    data["runtime_gate"]["preflight_verified"] = True
    with pytest.raises(KRXPerSecurityResumeConsentError, match="prematurely verified"):
        validate_contract(data)
