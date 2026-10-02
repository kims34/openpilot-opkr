import copy

import pytest

from research_v1_krx_status_economics_preparation_evidence import (
    KRXStatusEconomicsPreparationEvidenceError,
    PER_SECURITY_EXPECTED_TASK_COUNT,
    PER_SECURITY_EXPECTED_TASK_SET_SHA256,
    build_preparation_evidence,
    validate_evidence,
)


def _predecessor():
    return {
        "phase": "PER_SECURITY_HISTORY",
        "status": "COMPLETE",
        "expected_task_count": PER_SECURITY_EXPECTED_TASK_COUNT,
        "completed_task_count": PER_SECURITY_EXPECTED_TASK_COUNT,
        "failed_task_count": 0,
        "task_set_fingerprint_sha256": PER_SECURITY_EXPECTED_TASK_SET_SHA256,
        "phase_complete": True,
    }


def _prepare():
    return {
        "mode": "PREPARE_STATUS_ECONOMICS",
        "task_count": 3,
        "delisted_episode_count": 5,
        "cleanup_price_task_count": 3,
        "delisted_without_cleanup_interval_count": 2,
        "task_set_fingerprint_sha256": "a" * 64,
        "private_task_manifest_metadata_sha256": "b" * 64,
        "private_task_manifest_relpath": "task_manifests/status-economics-v3.json",
        "phase_status": "PENDING",
        "phase_complete": False,
        "network_request_attempted": False,
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


def test_build_and_validate_network_free_status_economics_preparation():
    evidence = build_preparation_evidence(
        predecessor_summary=_predecessor(),
        preparation_result=_prepare(),
    )
    out = validate_evidence(evidence)
    assert out["valid"] is True
    assert out["task_count"] == 3
    assert out["network_request_attempted"] is False
    assert out["status_economics_execution_authorized"] is False
    assert out["exact_status_economics_ready"] is False
    assert out["sealed_holdout_authorized"] is False
    assert out["live_trading_authorized"] is False


def test_preparation_evidence_rejects_incomplete_predecessor():
    predecessor = _predecessor()
    predecessor["completed_task_count"] -= 1
    predecessor["phase_complete"] = False
    predecessor["status"] = "IN_PROGRESS"
    with pytest.raises(KRXStatusEconomicsPreparationEvidenceError, match="not COMPLETE"):
        build_preparation_evidence(
            predecessor_summary=predecessor,
            preparation_result=_prepare(),
        )


def test_preparation_evidence_rejects_predecessor_failure_or_scope_drift():
    predecessor = _predecessor()
    predecessor["failed_task_count"] = 1
    with pytest.raises(KRXStatusEconomicsPreparationEvidenceError, match="has failures"):
        build_preparation_evidence(
            predecessor_summary=predecessor,
            preparation_result=_prepare(),
        )

    predecessor = _predecessor()
    predecessor["task_set_fingerprint_sha256"] = "0" * 64
    with pytest.raises(KRXStatusEconomicsPreparationEvidenceError, match="fingerprint drift"):
        build_preparation_evidence(
            predecessor_summary=predecessor,
            preparation_result=_prepare(),
        )


def test_preparation_evidence_rejects_network_or_exact_economics_claim():
    prep = _prepare()
    prep["network_request_attempted"] = True
    with pytest.raises(KRXStatusEconomicsPreparationEvidenceError, match="attempted network"):
        build_preparation_evidence(
            predecessor_summary=_predecessor(),
            preparation_result=prep,
        )

    prep = _prepare()
    prep["exact_status_economics_ready"] = True
    with pytest.raises(KRXStatusEconomicsPreparationEvidenceError, match="illegally claimed ready"):
        build_preparation_evidence(
            predecessor_summary=_predecessor(),
            preparation_result=prep,
        )


def test_preparation_evidence_never_grants_execution_or_later_authority():
    evidence = build_preparation_evidence(
        predecessor_summary=_predecessor(),
        preparation_result=_prepare(),
    )
    evidence["authority"]["status_economics_execution_authorized"] = True
    with pytest.raises(KRXStatusEconomicsPreparationEvidenceError, match="illegally true"):
        validate_evidence(evidence)

    evidence = build_preparation_evidence(
        predecessor_summary=_predecessor(),
        preparation_result=_prepare(),
    )
    evidence["authority"]["sealed_holdout_authorized"] = True
    with pytest.raises(KRXStatusEconomicsPreparationEvidenceError, match="illegally true"):
        validate_evidence(evidence)


def test_preparation_evidence_rejects_task_count_mismatch():
    prep = _prepare()
    prep["cleanup_price_task_count"] = 2
    with pytest.raises(KRXStatusEconomicsPreparationEvidenceError, match="task count drift"):
        build_preparation_evidence(
            predecessor_summary=_predecessor(),
            preparation_result=prep,
        )
