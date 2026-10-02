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
