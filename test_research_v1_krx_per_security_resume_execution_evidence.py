import pytest

from research_v1_krx_per_security_execution_evidence import (
    CHECKPOINT_COUNT,
    EXPECTED_TASK_COUNT,
    EXPECTED_TASK_SET_SHA256,
    INTERRUPTION_EVIDENCE_ID,
    REMAINING_COUNT,
    KRXPerSecurityExecutionEvidenceError,
    build_execution_evidence,
    validate_evidence,
)


def _summary():
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


def _resume_evidence():
    return build_execution_evidence(
        public_phase_summary=_summary(),
        private_batch_metadata_sha256="a" * 64,
        completed_task_count=EXPECTED_TASK_COUNT,
        resumed_task_count=CHECKPOINT_COUNT,
        network_request_attempt_count=REMAINING_COUNT,
        deployment_id="resume-deployment",
        source_revision="resume-revision",
        interruption_evidence_id=INTERRUPTION_EVIDENCE_ID,
        post_run_boundary=_boundary(),
    )


def test_resumed_execution_evidence_binds_exact_checkpoint_and_remaining_scope():
    evidence = _resume_evidence()
    assert evidence["execution"]["execution_path"] == "RESUMED_AFTER_INTERRUPTION"
    assert evidence["execution"]["interruption_evidence_id"] == INTERRUPTION_EVIDENCE_ID
    out = validate_evidence(evidence)
    assert out["valid"] is True
    assert out["resumed_task_count"] == CHECKPOINT_COUNT
    assert out["network_request_attempt_count"] == REMAINING_COUNT


def test_resumed_evidence_rejects_wrong_interruption_binding():
    with pytest.raises(
        KRXPerSecurityExecutionEvidenceError,
        match="interruption evidence binding drift",
    ):
        build_execution_evidence(
            public_phase_summary=_summary(),
            private_batch_metadata_sha256="a" * 64,
            completed_task_count=EXPECTED_TASK_COUNT,
            resumed_task_count=CHECKPOINT_COUNT,
            network_request_attempt_count=REMAINING_COUNT,
            deployment_id="resume-deployment",
            source_revision="resume-revision",
            interruption_evidence_id="wrong",
            post_run_boundary=_boundary(),
        )


def test_resumed_evidence_rejects_checkpoint_or_network_count_drift():
    with pytest.raises(
        KRXPerSecurityExecutionEvidenceError,
        match="resume checkpoint accounting drift",
    ):
        build_execution_evidence(
            public_phase_summary=_summary(),
            private_batch_metadata_sha256="a" * 64,
            completed_task_count=EXPECTED_TASK_COUNT,
            resumed_task_count=CHECKPOINT_COUNT - 1,
            network_request_attempt_count=REMAINING_COUNT + 1,
            deployment_id="resume-deployment",
            source_revision="resume-revision",
            interruption_evidence_id=INTERRUPTION_EVIDENCE_ID,
            post_run_boundary=_boundary(),
        )

    with pytest.raises(
        KRXPerSecurityExecutionEvidenceError,
        match="resume network accounting drift",
    ):
        build_execution_evidence(
            public_phase_summary=_summary(),
            private_batch_metadata_sha256="a" * 64,
            completed_task_count=EXPECTED_TASK_COUNT,
            resumed_task_count=CHECKPOINT_COUNT + 1,
            network_request_attempt_count=REMAINING_COUNT - 1,
            deployment_id="resume-deployment",
            source_revision="resume-revision",
            interruption_evidence_id=INTERRUPTION_EVIDENCE_ID,
            post_run_boundary=_boundary(),
        )


def test_resumed_evidence_requires_resume_consent_relock():
    boundary = _boundary()
    boundary["resume_consent_disabled_again"] = False
    with pytest.raises(
        KRXPerSecurityExecutionEvidenceError,
        match="resume_consent_disabled_again guard lost",
    ):
        build_execution_evidence(
            public_phase_summary=_summary(),
            private_batch_metadata_sha256="a" * 64,
            completed_task_count=EXPECTED_TASK_COUNT,
            resumed_task_count=CHECKPOINT_COUNT,
            network_request_attempt_count=REMAINING_COUNT,
            deployment_id="resume-deployment",
            source_revision="resume-revision",
            interruption_evidence_id=INTERRUPTION_EVIDENCE_ID,
            post_run_boundary=boundary,
        )


def test_validator_rejects_resumed_path_drift():
    evidence = _resume_evidence()
    evidence["execution"]["interruption_evidence_id"] = "wrong"
    with pytest.raises(
        KRXPerSecurityExecutionEvidenceError,
        match="interruption evidence binding drift",
    ):
        validate_evidence(evidence)

    evidence = _resume_evidence()
    evidence["execution"]["resumed_task_count"] -= 1
    evidence["execution"]["network_request_attempt_count"] += 1
    with pytest.raises(
        KRXPerSecurityExecutionEvidenceError,
        match="resume checkpoint accounting drift",
    ):
        validate_evidence(evidence)
