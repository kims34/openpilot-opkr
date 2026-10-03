"""Fail-closed public-safe execution evidence for STATUS_ECONOMICS.

Offline-only. This module never performs KRX network access and never turns
cleanup-price context into a claim about realized fills/recovery economics.
Evidence is buildable only when a previously frozen prepared scope, an exact
COMPLETE execution summary, and post-run relock all agree.
"""
from __future__ import annotations

import re
from typing import Any, Mapping

EVIDENCE_ID = "INDEXALERT-KRX-STATUS-ECONOMICS-EXEC-v1"
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


class KRXStatusEconomicsExecutionEvidenceError(ValueError):
    pass


def _require(cond: bool, msg: str) -> None:
    if not cond:
        raise KRXStatusEconomicsExecutionEvidenceError(msg)


def _sha(value: Any, field: str) -> str:
    text = str(value or "").strip().lower()
    _require(bool(SHA256_RE.fullmatch(text)), f"{field} must be SHA-256")
    return text


def _prepared_scope(scope: Mapping[str, Any]) -> dict[str, Any]:
    _require(isinstance(scope, Mapping), "prepared scope must be an object")
    task_count = int(scope.get("prepared_task_count", -1))
    _require(task_count > 0, "prepared task count must be positive")
    task_sha = _sha(
        scope.get("prepared_task_set_fingerprint_sha256"),
        "prepared_task_set_fingerprint_sha256",
    )
    manifest_sha = _sha(
        scope.get("prepared_private_manifest_metadata_sha256"),
        "prepared_private_manifest_metadata_sha256",
    )
    _require(
        scope.get("prepared_private_manifest_relpath")
        == "task_manifests/status-economics-v3.json",
        "prepared manifest relpath drift",
    )
    _require(scope.get("preparation_complete") is True, "preparation is not complete")
    _require(scope.get("execution_scope_frozen") is True, "execution scope is not frozen")
    _require(
        scope.get("preparation_evidence_id")
        == "INDEXALERT-KRX-STATUS-ECONOMICS-PREP-v1",
        "preparation evidence binding drift",
    )
    _require(
        scope.get("predecessor_completion_evidence_id")
        == "INDEXALERT-KRX-PER-SECURITY-HISTORY-EXEC-2026-10-03-v1",
        "predecessor completion evidence drift",
    )
    _require(
        scope.get("network_request_attempted_during_prepare") is False,
        "preparation attempted network",
    )
    return {
        "task_count": task_count,
        "task_sha": task_sha,
        "manifest_sha": manifest_sha,
    }


def build_execution_evidence(
    *,
    prepared_scope: Mapping[str, Any],
    execution_result: Mapping[str, Any],
    deployment_id: str,
    source_revision: str,
    post_run_boundary: Mapping[str, Any],
) -> dict[str, Any]:
    frozen = _prepared_scope(prepared_scope)

    _require(bool(str(deployment_id or "").strip()), "deployment_id required")
    _require(bool(str(source_revision or "").strip()), "source_revision required")

    _require(
        execution_result.get("mode") == "EXECUTE_STATUS_ECONOMICS",
        "execution mode drift",
    )
    _require(
        int(execution_result.get("task_count", -1)) == frozen["task_count"],
        "execution task count drift",
    )
    _require(
        int(execution_result.get("completed_task_count", -1)) == frozen["task_count"],
        "execution completion count drift",
    )
    _require(
        int(execution_result.get("phase_completed_task_count", -1))
        == frozen["task_count"],
        "phase completion count drift",
    )
    _require(execution_result.get("phase_status") == "COMPLETE", "phase status drift")
    _require(execution_result.get("phase_complete") is True, "phase_complete lost")
    _require(
        _sha(
            execution_result.get("task_set_fingerprint_sha256"),
            "task_set_fingerprint_sha256",
        )
        == frozen["task_sha"],
        "execution task-set fingerprint drift",
    )
    batch_sha = _sha(
        execution_result.get("private_batch_metadata_sha256"),
        "private_batch_metadata_sha256",
    )
    _require(
        execution_result.get("private_batch_relpath")
        == "batches/status-economics-v3.json",
        "private batch relpath drift",
    )

    resumed = int(execution_result.get("resumed_task_count", -1))
    network = int(execution_result.get("network_request_attempt_count", -1))
    _require(resumed >= 0 and network >= 0, "negative execution count")
    _require(
        resumed + network == frozen["task_count"],
        "network/resume accounting drift",
    )

    for key in (
        "security_identifiers_emitted",
        "raw_rows_emitted",
        "exact_status_economics_ready",
        "source_gate_c_closed",
        "source_gate_d_closed",
        "source_gate_e_closed",
        "feature_performance_testing_authorized",
        "sealed_holdout_authorized",
        "live_trading_authorized",
    ):
        _require(execution_result.get(key) is False, f"{key} illegally true")

    for key in (
        "bulk_execution_consent_disabled_again",
        "status_economics_consent_disabled_again",
        "start_command_restored_to_preflight_only",
        "preflight_network_request_attempted_false",
    ):
        _require(post_run_boundary.get(key) is True, f"{key} guard lost")
    for key in (
        "expected_scope_network_execution_authorized",
        "feature_performance_testing_authorized",
        "sealed_holdout_authorized",
        "shadow_s1_authorized",
        "genuine_live_authorized",
        "live_trading_authorized",
    ):
        _require(post_run_boundary.get(key) is False, f"{key} illegally true")

    return {
        "schema_version": "1",
        "evidence_id": EVIDENCE_ID,
        "stage": "STATUS_ECONOMICS",
        "status": "COMPLETE_METADATA_ONLY_CONTEXT_NOT_REALIZED_ECONOMICS",
        "prepared_scope": {
            "task_count": frozen["task_count"],
            "task_set_fingerprint_sha256": frozen["task_sha"],
            "private_manifest_metadata_sha256": frozen["manifest_sha"],
            "private_manifest_relpath": "task_manifests/status-economics-v3.json",
            "preparation_evidence_id": "INDEXALERT-KRX-STATUS-ECONOMICS-PREP-v1",
            "predecessor_completion_evidence_id":
                "INDEXALERT-KRX-PER-SECURITY-HISTORY-EXEC-2026-10-03-v1",
        },
        "execution": {
            "deployment_id": str(deployment_id),
            "source_revision": str(source_revision),
            "mode": "EXECUTE_STATUS_ECONOMICS",
            "task_count": frozen["task_count"],
            "completed_task_count": frozen["task_count"],
            "resumed_task_count": resumed,
            "network_request_attempt_count": network,
            "phase_status": "COMPLETE",
            "phase_complete": True,
        },
        "integrity": {
            "task_set_fingerprint_sha256": frozen["task_sha"],
            "private_batch_metadata_sha256": batch_sha,
            "private_batch_relpath": "batches/status-economics-v3.json",
            "raw_rows_emitted": False,
            "security_identifiers_emitted": False,
        },
        "claims": {
            "cleanup_price_context_complete": True,
            "exact_status_economics_ready": False,
            "realized_fill_economics_proven": False,
            "realized_recovery_cashflows_proven": False,
            "source_gate_c_closed": False,
            "source_gate_d_closed": False,
            "source_gate_e_closed": False,
        },
        "post_run_boundary": dict(post_run_boundary),
    }


def validate_evidence(data: Mapping[str, Any]) -> dict[str, Any]:
    _require(isinstance(data, Mapping), "evidence must be an object")
    _require(data.get("schema_version") == "1", "schema_version drift")
    _require(data.get("evidence_id") == EVIDENCE_ID, "evidence_id drift")
    _require(data.get("stage") == "STATUS_ECONOMICS", "stage drift")
    _require(
        data.get("status")
        == "COMPLETE_METADATA_ONLY_CONTEXT_NOT_REALIZED_ECONOMICS",
        "status drift",
    )

    scope = data.get("prepared_scope") or {}
    task_count = int(scope.get("task_count", -1))
    _require(task_count > 0, "prepared task count must be positive")
    task_sha = _sha(
        scope.get("task_set_fingerprint_sha256"),
        "task_set_fingerprint_sha256",
    )
    _sha(
        scope.get("private_manifest_metadata_sha256"),
        "private_manifest_metadata_sha256",
    )
    _require(
        scope.get("private_manifest_relpath")
        == "task_manifests/status-economics-v3.json",
        "prepared manifest relpath drift",
    )
    _require(
        scope.get("preparation_evidence_id")
        == "INDEXALERT-KRX-STATUS-ECONOMICS-PREP-v1",
        "preparation evidence binding drift",
    )
    _require(
        scope.get("predecessor_completion_evidence_id")
        == "INDEXALERT-KRX-PER-SECURITY-HISTORY-EXEC-2026-10-03-v1",
        "predecessor completion evidence drift",
    )

    execution = data.get("execution") or {}
    _require(bool(str(execution.get("deployment_id") or "").strip()), "deployment_id required")
    _require(bool(str(execution.get("source_revision") or "").strip()), "source_revision required")
    _require(execution.get("mode") == "EXECUTE_STATUS_ECONOMICS", "mode drift")
    _require(int(execution.get("task_count", -1)) == task_count, "task count drift")
    _require(
        int(execution.get("completed_task_count", -1)) == task_count,
        "completed task count drift",
    )
    resumed = int(execution.get("resumed_task_count", -1))
    network = int(execution.get("network_request_attempt_count", -1))
    _require(resumed >= 0 and network >= 0, "negative execution count")
    _require(resumed + network == task_count, "network/resume accounting drift")
    _require(execution.get("phase_status") == "COMPLETE", "phase status drift")
    _require(execution.get("phase_complete") is True, "phase_complete lost")

    integrity = data.get("integrity") or {}
    _require(
        _sha(
            integrity.get("task_set_fingerprint_sha256"),
            "integrity task_set_fingerprint_sha256",
        )
        == task_sha,
        "integrity task-set fingerprint drift",
    )
    _sha(
        integrity.get("private_batch_metadata_sha256"),
        "private_batch_metadata_sha256",
    )
    _require(
        integrity.get("private_batch_relpath") == "batches/status-economics-v3.json",
        "private batch relpath drift",
    )
    _require(integrity.get("raw_rows_emitted") is False, "raw rows emitted")
    _require(
        integrity.get("security_identifiers_emitted") is False,
        "security identifiers emitted",
    )

    claims = data.get("claims") or {}
    _require(claims.get("cleanup_price_context_complete") is True, "context completion lost")
    for key in (
        "exact_status_economics_ready",
        "realized_fill_economics_proven",
        "realized_recovery_cashflows_proven",
        "source_gate_c_closed",
        "source_gate_d_closed",
        "source_gate_e_closed",
    ):
        _require(claims.get(key) is False, f"claim {key} illegally true")

    boundary = data.get("post_run_boundary") or {}
    for key in (
        "bulk_execution_consent_disabled_again",
        "status_economics_consent_disabled_again",
        "start_command_restored_to_preflight_only",
        "preflight_network_request_attempted_false",
    ):
        _require(boundary.get(key) is True, f"{key} guard lost")
    for key in (
        "expected_scope_network_execution_authorized",
        "feature_performance_testing_authorized",
        "sealed_holdout_authorized",
        "shadow_s1_authorized",
        "genuine_live_authorized",
        "live_trading_authorized",
    ):
        _require(boundary.get(key) is False, f"{key} illegally true")

    return {
        "valid": True,
        "stage": "STATUS_ECONOMICS",
        "task_count": task_count,
        "phase_complete": True,
        "exact_status_economics_ready": False,
        "realized_fill_economics_proven": False,
        "sealed_holdout_authorized": False,
        "live_trading_authorized": False,
    }
