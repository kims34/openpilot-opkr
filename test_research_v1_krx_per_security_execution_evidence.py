import copy

import pytest

from research_v1_krx_per_security_execution_evidence import (
    EXPECTED_TASK_COUNT,
    EXPECTED_TASK_SET_SHA256,
    KRXPerSecurityExecutionEvidenceError,
    build_execution_evidence,
    validate_evidence,
)


def _complete_summary():
    return {
        "phase": "PER_SECURITY_HISTORY",
        "status": "COMPLETE",
        "expected_task_count": EXPECTED_TASK_COUNT,
        "completed_task_count": EXPECTED_TASK_COUNT,
        "failed_task_count": 0,
        "task_set_fingerprint_sha256": EXPECTED_TASK_SET_SHA256,
        "phase_complete": True,
        "security_identifiers_emitted": False,
        "raw_rows_emitted": False,
        "source_gate_c_closed": False,
        "source_gate_d_closed": False,
        "source_gate_e_closed": False,
        "feature_performance_testing_authorized": False,
        "sealed_holdout_authorized": False,
        "live_trading_authorized": False,
    }


def _boundary():
    return {
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


def _evidence():
    return build_execution_evidence(
        public_phase_summary=_complete_summary(),
        private_batch_metadata_sha256="a" * 64,
        completed_task_count=EXPECTED_TASK_COUNT,
        resumed_task_count=0,
        network_request_attempt_count=EXPECTED_TASK_COUNT,
        post_run_boundary=_boundary(),
    )


def test_execution_evidence_builds_only_after_exact_complete_state():
    out = validate_evidence(_evidence())
    assert out["valid"] is True
    assert out["task_count"] == EXPECTED_TASK_COUNT
    assert out["completed_task_count"] == EXPECTED_TASK_COUNT
    assert out["phase_complete"] is True
    assert out["status_economics_authorized"] is False
    assert out["sealed_holdout_authorized"] is False
    assert out["live_trading_authorized"] is False


def test_execution_evidence_rejects_incomplete_or_failed_phase():
    summary = _complete_summary()
    summary["completed_task_count"] = EXPECTED_TASK_COUNT - 1
    summary["phase_complete"] = False
    summary["status"] = "IN_PROGRESS"
    with pytest.raises(KRXPerSecurityExecutionEvidenceError, match="not COMPLETE"):
        build_execution_evidence(
            public_phase_summary=summary,
            private_batch_metadata_sha256="a" * 64,
            completed_task_count=EXPECTED_TASK_COUNT - 1,
            resumed_task_count=0,
            network_request_attempt_count=EXPECTED_TASK_COUNT - 1,
            post_run_boundary=_boundary(),
        )

    summary = _complete_summary()
    summary["failed_task_count"] = 1
    with pytest.raises(KRXPerSecurityExecutionEvidenceError, match="failed tasks"):
        build_execution_evidence(
            public_phase_summary=summary,
            private_batch_metadata_sha256="a" * 64,
            completed_task_count=EXPECTED_TASK_COUNT,
            resumed_task_count=0,
            network_request_attempt_count=EXPECTED_TASK_COUNT,
            post_run_boundary=_boundary(),
        )


def test_execution_evidence_requires_exact_frozen_fingerprint():
    summary = _complete_summary()
    summary["task_set_fingerprint_sha256"] = "0" * 64
    with pytest.raises(KRXPerSecurityExecutionEvidenceError, match="task-set fingerprint drift"):
        build_execution_evidence(
            public_phase_summary=summary,
            private_batch_metadata_sha256="a" * 64,
            completed_task_count=EXPECTED_TASK_COUNT,
            resumed_task_count=0,
            network_request_attempt_count=EXPECTED_TASK_COUNT,
            post_run_boundary=_boundary(),
        )


def test_execution_evidence_requires_network_plus_resume_accounting():
    with pytest.raises(KRXPerSecurityExecutionEvidenceError, match="network/resume accounting"):
        build_execution_evidence(
            public_phase_summary=_complete_summary(),
            private_batch_metadata_sha256="a" * 64,
            completed_task_count=EXPECTED_TASK_COUNT,
            resumed_task_count=10,
            network_request_attempt_count=EXPECTED_TASK_COUNT,
            post_run_boundary=_boundary(),
        )


def test_execution_evidence_requires_post_run_relock():
    boundary = _boundary()
    boundary["per_security_consent_disabled_again"] = False
    with pytest.raises(KRXPerSecurityExecutionEvidenceError, match="guard lost"):
        build_execution_evidence(
            public_phase_summary=_complete_summary(),
            private_batch_metadata_sha256="a" * 64,
            completed_task_count=EXPECTED_TASK_COUNT,
            resumed_task_count=0,
            network_request_attempt_count=EXPECTED_TASK_COUNT,
            post_run_boundary=boundary,
        )


def test_execution_evidence_cannot_authorize_later_stages():
    evidence = _evidence()
    evidence["post_run_boundary"]["status_economics_authorized"] = True
    with pytest.raises(KRXPerSecurityExecutionEvidenceError, match="illegally true"):
        validate_evidence(evidence)

    evidence = _evidence()
    evidence["post_run_boundary"]["sealed_holdout_authorized"] = True
    with pytest.raises(KRXPerSecurityExecutionEvidenceError, match="illegally true"):
        validate_evidence(evidence)


def test_validator_rejects_execution_scope_or_deployment_drift():
    evidence = _evidence()
    evidence["execution"]["task_count"] = EXPECTED_TASK_COUNT + 1
    with pytest.raises(KRXPerSecurityExecutionEvidenceError, match="task count drift"):
        validate_evidence(evidence)

    evidence = _evidence()
    evidence["execution"]["deployment_id"] = "different"
    with pytest.raises(KRXPerSecurityExecutionEvidenceError, match="deployment drift"):
        validate_evidence(evidence)
