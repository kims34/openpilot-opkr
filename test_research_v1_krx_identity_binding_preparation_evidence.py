import json
from pathlib import Path

import pytest

from research_v1_krx_identity_binding_preparation_evidence import (
    KRXIdentityBindingPreparationEvidenceError,
    validate_evidence,
    validate_file,
)

PATH = Path("INDEXALERT_KRX_IDENTITY_BINDING_PREPARATION_EVIDENCE.json")


def _data():
    return json.loads(PATH.read_text(encoding="utf-8"))


def test_committed_binding_preparation_is_network_free_and_pending():
    out = validate_file()
    assert out["valid"] is True
    assert out["stage"] == "IDENTITY_STANDARD_CODE_BINDING"
    assert out["task_count"] == 145
    assert out["phase_status"] == "PENDING"
    assert out["network_request_attempted"] is False
    assert out["stage_specific_user_authorization_received"] is False
    assert out["sealed_holdout_authorized"] is False
    assert out["live_trading_authorized"] is False


def test_binding_preparation_rejects_count_or_network_drift():
    data = _data()
    data["preparation"]["task_count"] = 144
    with pytest.raises(KRXIdentityBindingPreparationEvidenceError, match="task count drift"):
        validate_evidence(data)

    data = _data()
    data["preparation"]["network_request_attempted"] = True
    with pytest.raises(KRXIdentityBindingPreparationEvidenceError, match="network request illegally attempted"):
        validate_evidence(data)


def test_binding_preparation_cannot_self_authorize():
    for key in (
        "stage_specific_user_authorization_received",
        "prior_identity_seed_authorization_reusable",
        "expected_scope_network_execution_authorized",
        "per_security_history_execution_authorized",
        "status_economics_execution_authorized",
        "feature_performance_testing_authorized",
        "sealed_holdout_authorized",
        "live_trading_authorized",
    ):
        data = _data()
        data["authority"][key] = True
        with pytest.raises(KRXIdentityBindingPreparationEvidenceError, match="illegally true"):
            validate_evidence(data)


def test_binding_preparation_requires_post_prepare_lock():
    data = _data()
    data["post_prepare_lock"]["start_command_restored_to_preflight_only"] = False
    with pytest.raises(KRXIdentityBindingPreparationEvidenceError, match="not restored"):
        validate_evidence(data)
