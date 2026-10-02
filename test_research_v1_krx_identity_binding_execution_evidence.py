import json
from pathlib import Path

import pytest

from research_v1_krx_identity_binding_execution_evidence import (
    KRXIdentityBindingExecutionEvidenceError,
    validate_evidence,
    validate_file,
)

PATH = Path("INDEXALERT_KRX_IDENTITY_BINDING_EXECUTION_EVIDENCE.json")


def _data():
    return json.loads(PATH.read_text(encoding="utf-8"))


def test_committed_binding_execution_is_exactly_145_and_complete():
    out = validate_file()
    assert out["valid"] is True
    assert out["stage"] == "IDENTITY_STANDARD_CODE_BINDING"
    assert out["task_count"] == 145
    assert out["completed_task_count"] == 145
    assert out["network_request_attempt_count"] == 145
    assert out["phase_complete"] is True
    assert out["per_security_history_authorized"] is False
    assert out["sealed_holdout_authorized"] is False
    assert out["live_trading_authorized"] is False


def test_binding_execution_rejects_partial_or_extra_execution():
    data = _data()
    data["execution"]["completed_task_count"] = 144
    with pytest.raises(KRXIdentityBindingExecutionEvidenceError, match="completed_task_count"):
        validate_evidence(data)

    data = _data()
    data["execution"]["network_request_attempt_count"] = 146
    with pytest.raises(KRXIdentityBindingExecutionEvidenceError, match="network_request_attempt_count"):
        validate_evidence(data)


def test_binding_execution_rejects_task_set_or_public_leak_drift():
    data = _data()
    data["integrity"]["task_set_fingerprint_sha256"] = "0" * 64
    with pytest.raises(KRXIdentityBindingExecutionEvidenceError, match="task-set fingerprint drift"):
        validate_evidence(data)

    data = _data()
    data["integrity"]["raw_rows_emitted"] = True
    with pytest.raises(KRXIdentityBindingExecutionEvidenceError, match="raw rows"):
        validate_evidence(data)


def test_binding_execution_cannot_authorize_later_stages():
    for key in (
        "per_security_history_authorized",
        "status_economics_authorized",
        "expected_scope_network_execution_authorized",
        "feature_performance_testing_authorized",
        "sealed_holdout_authorized",
        "genuine_live_authorized",
        "live_trading_authorized",
    ):
        data = _data()
        data["post_run_boundary"][key] = True
        with pytest.raises(KRXIdentityBindingExecutionEvidenceError, match="illegally true"):
            validate_evidence(data)


def test_binding_execution_requires_post_run_lock():
    data = _data()
    data["post_run_boundary"]["identity_binding_consent_disabled_again"] = False
    with pytest.raises(KRXIdentityBindingExecutionEvidenceError, match="guard lost"):
        validate_evidence(data)
