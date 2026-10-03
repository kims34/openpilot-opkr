import pytest

from research_v1_krx_status_economics_execution_evidence import (
    KRXStatusEconomicsExecutionEvidenceError,
    build_execution_evidence,
    validate_evidence,
)


def _scope():
    return {
        "prepared_task_count": 5,
        "prepared_task_set_fingerprint_sha256": "a" * 64,
        "prepared_private_manifest_metadata_sha256": "b" * 64,
        "prepared_private_manifest_relpath": "task_manifests/status-economics-v3.json",
        "preparation_complete": True,
        "execution_scope_frozen": True,
        "preparation_evidence_id": "INDEXALERT-KRX-STATUS-ECONOMICS-PREP-v1",
        "predecessor_completion_evidence_id":
            "INDEXALERT-KRX-PER-SECURITY-HISTORY-EXEC-2026-10-03-v1",
        "network_request_attempted_during_prepare": False,
    }


def _execution():
    return {
        "mode": "EXECUTE_STATUS_ECONOMICS",
        "task_count": 5,
        "completed_task_count": 5,
        "resumed_task_count": 1,
        "network_request_attempt_count": 4,
        "task_set_fingerprint_sha256": "a" * 64,
        "private_batch_metadata_sha256": "c" * 64,
        "private_batch_relpath": "batches/status-economics-v3.json",
        "phase_status": "COMPLETE",
        "phase_complete": True,
        "phase_completed_task_count": 5,
        "security_identifiers_emitted": False,
        "raw_rows_emitted": False,
        "exact_status_economics_ready": False,
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
        "status_economics_consent_disabled_again": True,
        "start_command_restored_to_preflight_only": True,
        "preflight_network_request_attempted_false": True,
        "expected_scope_network_execution_authorized": False,
        "feature_performance_testing_authorized": False,
        "sealed_holdout_authorized": False,
        "shadow_s1_authorized": False,
        "genuine_live_authorized": False,
        "live_trading_authorized": False,
    }


def _evidence():
    return build_execution_evidence(
        prepared_scope=_scope(),
        execution_result=_execution(),
        deployment_id="future-deployment",
        source_revision="future-revision",
        post_run_boundary=_boundary(),
    )


def test_status_economics_execution_evidence_is_metadata_only_context():
    out = validate_evidence(_evidence())
    assert out["valid"] is True
    assert out["task_count"] == 5
    assert out["phase_complete"] is True
    assert out["exact_status_economics_ready"] is False
    assert out["realized_fill_economics_proven"] is False
    assert out["sealed_holdout_authorized"] is False
    assert out["live_trading_authorized"] is False


def test_evidence_requires_exact_prepared_scope_and_complete_execution():
    scope = _scope()
    scope["preparation_complete"] = False
    with pytest.raises(KRXStatusEconomicsExecutionEvidenceError, match="not complete"):
        build_execution_evidence(
            prepared_scope=scope,
            execution_result=_execution(),
            deployment_id="d",
            source_revision="r",
            post_run_boundary=_boundary(),
        )

    execution = _execution()
    execution["completed_task_count"] = 4
    with pytest.raises(KRXStatusEconomicsExecutionEvidenceError, match="completion count drift"):
        build_execution_evidence(
            prepared_scope=_scope(),
            execution_result=execution,
            deployment_id="d",
            source_revision="r",
            post_run_boundary=_boundary(),
        )


def test_evidence_requires_network_resume_accounting_and_fingerprint():
    execution = _execution()
    execution["network_request_attempt_count"] = 3
    with pytest.raises(KRXStatusEconomicsExecutionEvidenceError, match="accounting drift"):
        build_execution_evidence(
            prepared_scope=_scope(),
            execution_result=execution,
            deployment_id="d",
            source_revision="r",
            post_run_boundary=_boundary(),
        )

    execution = _execution()
    execution["task_set_fingerprint_sha256"] = "0" * 64
    with pytest.raises(KRXStatusEconomicsExecutionEvidenceError, match="fingerprint drift"):
        build_execution_evidence(
            prepared_scope=_scope(),
            execution_result=execution,
            deployment_id="d",
            source_revision="r",
            post_run_boundary=_boundary(),
        )


def test_evidence_never_upgrades_context_to_realized_economics_or_later_authority():
    evidence = _evidence()
    evidence["claims"]["exact_status_economics_ready"] = True
    with pytest.raises(KRXStatusEconomicsExecutionEvidenceError, match="illegally true"):
        validate_evidence(evidence)

    evidence = _evidence()
    evidence["claims"]["realized_fill_economics_proven"] = True
    with pytest.raises(KRXStatusEconomicsExecutionEvidenceError, match="illegally true"):
        validate_evidence(evidence)

    evidence = _evidence()
    evidence["post_run_boundary"]["sealed_holdout_authorized"] = True
    with pytest.raises(KRXStatusEconomicsExecutionEvidenceError, match="illegally true"):
        validate_evidence(evidence)


def test_evidence_requires_post_run_relock():
    boundary = _boundary()
    boundary["status_economics_consent_disabled_again"] = False
    with pytest.raises(KRXStatusEconomicsExecutionEvidenceError, match="guard lost"):
        build_execution_evidence(
            prepared_scope=_scope(),
            execution_result=_execution(),
            deployment_id="d",
            source_revision="r",
            post_run_boundary=boundary,
        )
