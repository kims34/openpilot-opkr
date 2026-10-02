import json
from pathlib import Path

import pytest

from research_v1_krx_identity_binding_consent import (
    KRXIdentityBindingConsentError,
    validate_contract,
    validate_file,
)

PATH = Path("INDEXALERT_KRX_IDENTITY_BINDING_CONSENT_CONTRACT.json")


def _data():
    return json.loads(PATH.read_text(encoding="utf-8"))


def test_committed_binding_contract_is_frozen_and_not_authorized():
    out = validate_file()
    assert out["valid"] is True
    assert out["stage"] == "IDENTITY_STANDARD_CODE_BINDING"
    assert out["authorized"] is False
    assert out["one_shot"] is True
    assert out["prior_seed_authorization_reusable"] is False
    assert out["dual_consent_required"] is True
    assert out["sealed_holdout_authorized"] is False
    assert out["live_trading_authorized"] is False


def test_prior_seed_authorization_cannot_be_reused():
    data = _data()
    data["user_authorization"]["prior_identity_seed_authorization_reusable"] = True
    with pytest.raises(KRXIdentityBindingConsentError, match="reuse illegally allowed"):
        validate_contract(data)


def test_binding_contract_requires_dual_consent():
    data = _data()
    data["runtime_gate"]["both_consents_required"] = False
    with pytest.raises(KRXIdentityBindingConsentError, match="dual-consent guard lost"):
        validate_contract(data)


def test_binding_cannot_be_pre_authorized():
    data = _data()
    data["user_authorization"]["authorized"] = True
    with pytest.raises(KRXIdentityBindingConsentError, match="pre-authorized"):
        validate_contract(data)


def test_binding_contract_cannot_authorize_later_stages():
    for key in (
        "expected_scope_network_execution_authorized",
        "per_security_history_execution_authorized",
        "status_economics_execution_authorized",
        "feature_performance_testing_authorized",
        "sealed_holdout_authorized",
        "shadow_s1_authorized",
        "live_trading_authorized",
    ):
        data = _data()
        data["authority"][key] = True
        with pytest.raises(KRXIdentityBindingConsentError, match="illegally true"):
            validate_contract(data)


def test_post_run_lock_must_remain_fail_closed():
    data = _data()
    data["post_run_lock"]["disable_stage_consent_again"] = False
    with pytest.raises(KRXIdentityBindingConsentError, match="guard lost"):
        validate_contract(data)

    data = _data()
    data["post_run_lock"]["later_stage_auto_authorization"] = True
    with pytest.raises(KRXIdentityBindingConsentError, match="auto authorization illegally enabled"):
        validate_contract(data)
