import json
from pathlib import Path
import pytest

from research_v1_krx_status_economics_consent import (
    KRXStatusEconomicsConsentError,
    validate_contract,
    validate_file,
)

PATH = Path("INDEXALERT_KRX_STATUS_ECONOMICS_CONSENT_CONTRACT.json")


def _data():
    return json.loads(PATH.read_text(encoding="utf-8"))


def test_committed_status_economics_consent_shell_is_not_execution_ready():
    out = validate_file()
    assert out["valid"] is True
    assert out["preparation_complete"] is False
    assert out["execution_scope_frozen"] is False
    assert out["authorized"] is False
    assert out["prior_stage_authorization_reusable"] is False
    assert out["sealed_holdout_authorized"] is False
    assert out["live_trading_authorized"] is False


def test_shell_rejects_premature_preparation_or_scope_freeze():
    data = _data()
    data["preparation_gate"]["preparation_complete"] = True
    with pytest.raises(KRXStatusEconomicsConsentError, match="prematurely complete"):
        validate_contract(data)

    data = _data()
    data["preparation_gate"]["prepared_task_count"] = 1
    with pytest.raises(KRXStatusEconomicsConsentError, match="prematurely frozen"):
        validate_contract(data)


def test_shell_rejects_prior_stage_approval_reuse_or_preauthorization():
    data = _data()
    data["user_authorization"]["prior_stage_authorization_reusable"] = True
    with pytest.raises(KRXStatusEconomicsConsentError, match="reuse enabled"):
        validate_contract(data)

    data = _data()
    data["user_authorization"]["authorized"] = True
    with pytest.raises(KRXStatusEconomicsConsentError, match="pre-authorized"):
        validate_contract(data)


def test_shell_rejects_later_stage_authority_escalation():
    for key in (
        "status_economics_execution_authorized",
        "expected_scope_network_execution_authorized",
        "exact_status_economics_claim_allowed",
        "feature_performance_testing_authorized",
        "sealed_holdout_authorized",
        "shadow_s1_authorized",
        "genuine_live_authorized",
        "live_trading_authorized",
    ):
        data = _data()
        data["authority"][key] = True
        with pytest.raises(KRXStatusEconomicsConsentError, match="illegally true"):
            validate_contract(data)
