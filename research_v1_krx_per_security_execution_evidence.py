"""Public-safe builder/validator for completed KRX PER_SECURITY_HISTORY evidence.

This module is offline-only. It never reads raw KRX rows or performs network
access. Evidence can be built only from a public-safe COMPLETE phase summary
plus hashes/counts produced by the frozen worker after the run.
"""
from __future__ import annotations

import re
from typing import Any, Mapping

EXPECTED_TASK_COUNT = 14296
EXPECTED_TASK_SET_SHA256 = "fb5b883c6fe0e9c15e88aea9bdf874ddd7a11ae8a009c2ddf91c4e4249a8ba38"
EXPECTED_DEPLOYMENT_ID = "bc79d1b5-5fb8-46c7-8067-682e61947014"
EXPECTED_SOURCE_REVISION = "9009c48a00394063c813d29219507ee2190ce09e"
INTERRUPTION_EVIDENCE_ID = "INDEXALERT-KRX-PER-SECURITY-HISTORY-INTERRUPTION-2026-10-03-v1"
CHECKPOINT_COUNT = 11750
REMAINING_COUNT = 2546
PRIVATE_BATCH_RELPATH = "batches/per-security-history-v3.json"
EVIDENCE_ID = "INDEXALERT-KRX-PER-SECURITY-HISTORY-EXEC-2026-10-03-v1"
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


class KRXPerSecurityExecutionEvidenceError(ValueError):
    pass


def _require(cond: bool, msg: str) -> None:
    if not cond:
        raise KRXPerSecurityExecutionEvidenceError(msg)


def _sha(value: Any, field: str) -> str:
    text = str(value or "").strip().lower()
    _require(bool(SHA256_RE.fullmatch(text)), f"{field} must be SHA-256")
    return text


def _require_complete_summary(summary: Mapping[str, Any]) -> None:
    _require(summary.get("phase") == "PER_SECURITY_HISTORY", "phase drift")
    _require(summary.get("status") == "COMPLETE", "phase is not COMPLETE")
    _require(summary.get("phase_complete") is True, "phase_complete must be true")
    _require(
        int(summary.get("expected_task_count", -1)) == EXPECTED_TASK_COUNT,
        "expected task count drift",
    )
    _require(
        int(summary.get("completed_task_count", -1)) == EXPECTED_TASK_COUNT,
        "completed task count is not exact",
    )
    _require(int(summary.get("failed_task_count", -1)) == 0, "failed tasks present")
    _require(
        _sha(summary.get("task_set_fingerprint_sha256"), "task_set_fingerprint_sha256")
        == EXPECTED_TASK_SET_SHA256,
        "task-set fingerprint drift",
    )
    for key in (
        "security_identifiers_emitted",
        "raw_rows_emitted",
        "source_gate_c_closed",
        "source_gate_d_closed",
        "source_gate_e_closed",
        "feature_performance_testing_authorized",
        "sealed_holdout_authorized",
        "live_trading_authorized",
    ):
        _require(summary.get(key) is False, f"{key} illegally true")


def build_execution_evidence(
    *,
    public_phase_summary: Mapping[str, Any],
    private_batch_metadata_sha256: str,
    completed_task_count: int,
    resumed_task_count: int,
    network_request_attempt_count: int,
    deployment_id: str = EXPECTED_DEPLOYMENT_ID,
    source_revision: str = EXPECTED_SOURCE_REVISION,
    interruption_evidence_id: str | None = None,
    post_run_boundary: Mapping[str, Any],
) -> dict[str, Any]:
    """Build metadata-only evidence only after exact frozen completion."""
    _require_complete_summary(public_phase_summary)
    _require(bool(str(deployment_id or "").strip()), "deployment_id required")
    _require(bool(str(source_revision or "").strip()), "source_revision required")
    _require(int(completed_task_count) == EXPECTED_TASK_COUNT, "execution completion count drift")

    resumed = int(resumed_task_count)
    network = int(network_request_attempt_count)
    _require(resumed >= 0, "negative resumed task count")
    _require(network >= 0, "negative network request count")

    resumed_after_interruption = (
        deployment_id != EXPECTED_DEPLOYMENT_ID
        or source_revision != EXPECTED_SOURCE_REVISION
        or interruption_evidence_id is not None
    )
    if resumed_after_interruption:
        _require(
            interruption_evidence_id == INTERRUPTION_EVIDENCE_ID,
            "interruption evidence binding drift",
        )
        _require(resumed == CHECKPOINT_COUNT, "resume checkpoint accounting drift")
        _require(network == REMAINING_COUNT, "resume network accounting drift")
        _require(
            post_run_boundary.get("resume_consent_disabled_again") is True,
            "resume_consent_disabled_again guard lost",
        )
    _require(
        resumed + network == EXPECTED_TASK_COUNT,
        "network/resume accounting does not equal frozen task count",
    )
    if resumed_after_interruption:
        pass
    else:
        _require(deployment_id == EXPECTED_DEPLOYMENT_ID, "deployment drift")
        _require(source_revision == EXPECTED_SOURCE_REVISION, "source revision drift")

    batch_sha = _sha(private_batch_metadata_sha256, "private_batch_metadata_sha256")

    for key in (
        "bulk_execution_consent_disabled_again",
        "per_security_consent_disabled_again",
        "start_command_restored_to_preflight_only",
        "preflight_network_request_attempted_false",
    ):
        _require(post_run_boundary.get(key) is True, f"{key} guard lost")
    for key in (
        "status_economics_authorized",
        "expected_scope_network_execution_authorized",
        "feature_performance_testing_authorized",
        "sealed_holdout_authorized",
        "genuine_live_authorized",
        "live_trading_authorized",
    ):
        _require(post_run_boundary.get(key) is False, f"{key} illegally true")

    return {
        "schema_version": "1",
        "evidence_id": EVIDENCE_ID,
        "stage": "PER_SECURITY_HISTORY",
        "status": "COMPLETE_METADATA_ONLY",
        "execution": {
            "railway_service": "indexalert-krx-historical-worker",
            "deployment_id": deployment_id,
            "source_revision": source_revision,
            "dockerfile": "Dockerfile.krx-historical-worker",
            "mode": "EXECUTE_PER_SECURITY_HISTORY",
            "execution_path": (
                "RESUMED_AFTER_INTERRUPTION"
                if resumed_after_interruption
                else "ORIGINAL_SINGLE_RUN"
            ),
            "interruption_evidence_id": (
                INTERRUPTION_EVIDENCE_ID if resumed_after_interruption else None
            ),
            "task_count": EXPECTED_TASK_COUNT,
            "completed_task_count": EXPECTED_TASK_COUNT,
            "resumed_task_count": resumed,
            "network_request_attempt_count": network,
            "phase_status": "COMPLETE",
            "phase_complete": True,
        },
        "integrity": {
            "task_set_fingerprint_sha256": EXPECTED_TASK_SET_SHA256,
            "private_batch_metadata_sha256": batch_sha,
            "private_batch_relpath": PRIVATE_BATCH_RELPATH,
            "raw_rows_emitted": False,
            "security_identifiers_emitted": False,
        },
        "post_run_boundary": dict(post_run_boundary),
    }


def validate_evidence(data: Mapping[str, Any]) -> dict[str, Any]:
    _require(isinstance(data, Mapping), "evidence must be an object")
    _require(data.get("schema_version") == "1", "schema_version drift")
    _require(data.get("evidence_id") == EVIDENCE_ID, "evidence_id drift")
    _require(data.get("stage") == "PER_SECURITY_HISTORY", "stage drift")
    _require(data.get("status") == "COMPLETE_METADATA_ONLY", "status drift")

    execution = data.get("execution") or {}
    _require(execution.get("railway_service") == "indexalert-krx-historical-worker", "worker drift")
    deployment_id = str(execution.get("deployment_id") or "").strip()
    source_revision = str(execution.get("source_revision") or "").strip()
    _require(bool(deployment_id), "deployment_id required")
    _require(bool(source_revision), "source_revision required")
    _require(execution.get("dockerfile") == "Dockerfile.krx-historical-worker", "Dockerfile drift")
    _require(execution.get("mode") == "EXECUTE_PER_SECURITY_HISTORY", "mode drift")
    execution_path = execution.get("execution_path", "ORIGINAL_SINGLE_RUN")
    _require(
        execution_path in {"ORIGINAL_SINGLE_RUN", "RESUMED_AFTER_INTERRUPTION"},
        "execution path drift",
    )
    if execution_path == "ORIGINAL_SINGLE_RUN":
        _require(deployment_id == EXPECTED_DEPLOYMENT_ID, "deployment drift")
        _require(source_revision == EXPECTED_SOURCE_REVISION, "source revision drift")
        _require(execution.get("interruption_evidence_id") in (None, ""), "unexpected interruption binding")
    else:
        _require(
            execution.get("interruption_evidence_id") == INTERRUPTION_EVIDENCE_ID,
            "interruption evidence binding drift",
        )
    _require(int(execution.get("task_count", -1)) == EXPECTED_TASK_COUNT, "task count drift")
    _require(
        int(execution.get("completed_task_count", -1)) == EXPECTED_TASK_COUNT,
        "completed task count drift",
    )
    resumed = int(execution.get("resumed_task_count", -1))
    network = int(execution.get("network_request_attempt_count", -1))
    _require(resumed >= 0 and network >= 0, "negative execution count")
    if execution_path == "RESUMED_AFTER_INTERRUPTION":
        _require(resumed == CHECKPOINT_COUNT, "resume checkpoint accounting drift")
        _require(network == REMAINING_COUNT, "resume network accounting drift")
    _require(resumed + network == EXPECTED_TASK_COUNT, "network/resume accounting drift")
    _require(execution.get("phase_status") == "COMPLETE", "phase status drift")
    _require(execution.get("phase_complete") is True, "phase_complete lost")

    integrity = data.get("integrity") or {}
    _require(
        _sha(integrity.get("task_set_fingerprint_sha256"), "task_set_fingerprint_sha256")
        == EXPECTED_TASK_SET_SHA256,
        "task-set fingerprint drift",
    )
    _sha(integrity.get("private_batch_metadata_sha256"), "private_batch_metadata_sha256")
    _require(integrity.get("private_batch_relpath") == PRIVATE_BATCH_RELPATH, "private batch relpath drift")
    _require(integrity.get("raw_rows_emitted") is False, "raw rows illegally emitted")
    _require(integrity.get("security_identifiers_emitted") is False, "identifiers illegally emitted")

    boundary = data.get("post_run_boundary") or {}
    for key in (
        "bulk_execution_consent_disabled_again",
        "per_security_consent_disabled_again",
        "start_command_restored_to_preflight_only",
        "preflight_network_request_attempted_false",
    ):
        _require(boundary.get(key) is True, f"{key} guard lost")
    for key in (
        "status_economics_authorized",
        "expected_scope_network_execution_authorized",
        "feature_performance_testing_authorized",
        "sealed_holdout_authorized",
        "genuine_live_authorized",
        "live_trading_authorized",
    ):
        _require(boundary.get(key) is False, f"{key} illegally true")

    if execution_path == "RESUMED_AFTER_INTERRUPTION":
        _require(
            boundary.get("resume_consent_disabled_again") is True,
            "resume_consent_disabled_again guard lost",
        )

    return {
        "valid": True,
        "stage": "PER_SECURITY_HISTORY",
        "task_count": EXPECTED_TASK_COUNT,
        "completed_task_count": EXPECTED_TASK_COUNT,
        "resumed_task_count": resumed,
        "network_request_attempt_count": network,
        "phase_complete": True,
        "status_economics_authorized": False,
        "sealed_holdout_authorized": False,
        "live_trading_authorized": False,
    }
