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


def _ready():
    data = _data()
    data["status"] = "USER_AUTHORIZED_RESUME_READY"
    data["user_authorization"]["authorized"] = True
    data["user_authorization"]["consumed"] = False
    data["user_authorization"]["received_date_kst"] = "2099-01-01"
    data["code_fix"]["source_revision"] = "fixed-revision"
    data["runtime_gate"]["source_revision"] = "fixed-revision"
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
