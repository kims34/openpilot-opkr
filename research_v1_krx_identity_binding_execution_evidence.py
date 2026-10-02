"""Fail-closed validator for completed KRX identity-binding execution evidence."""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Mapping

PATH = Path("INDEXALERT_KRX_IDENTITY_BINDING_EXECUTION_EVIDENCE.json")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


class KRXIdentityBindingExecutionEvidenceError(ValueError):
    pass


def _require(cond: bool, msg: str) -> None:
    if not cond:
        raise KRXIdentityBindingExecutionEvidenceError(msg)


def _sha(value: Any, field: str) -> str:
    text = str(value or "").strip().lower()
    _require(bool(SHA256_RE.fullmatch(text)), f"{field} must be SHA-256")
    return text


def validate_evidence(data: Mapping[str, Any]) -> dict[str, Any]:
    _require(isinstance(data, Mapping), "evidence must be an object")
    _require(data.get("schema_version") == "1", "schema_version drift")
    _require(
        data.get("evidence_id")
        == "INDEXALERT-KRX-IDENTITY-BINDING-EXEC-2026-10-03-v1",
        "evidence_id drift",
    )
    _require(data.get("stage") == "IDENTITY_STANDARD_CODE_BINDING", "stage drift")
    _require(data.get("status") == "COMPLETE_METADATA_ONLY", "status drift")

    execution = data.get("execution") or {}
    _require(
        execution.get("railway_service") == "indexalert-krx-historical-worker",
        "Railway worker drift",
    )
    _require(
        execution.get("source_revision")
        == "6c152d8f29354d843b16c35be27a86a8a8058908",
        "source revision drift",
    )
    _require(
        execution.get("dockerfile") == "Dockerfile.krx-historical-worker",
        "Dockerfile drift",
    )
    _require(
        execution.get("mode") == "EXECUTE_IDENTITY_STANDARD_CODE_BINDING",
        "mode drift",
    )
    _require(int(execution.get("task_count", -1)) == 145, "task_count must be 145")
    _require(
        int(execution.get("completed_task_count", -1)) == 145,
        "completed_task_count must be 145",
    )
    _require(int(execution.get("resumed_task_count", -1)) == 0, "unexpected resumed tasks")
    _require(
        int(execution.get("network_request_attempt_count", -1)) == 145,
        "network_request_attempt_count must be 145",
    )
    _require(execution.get("phase_status") == "COMPLETE", "phase status is not COMPLETE")
    _require(execution.get("phase_complete") is True, "phase_complete must be true")

    integrity = data.get("integrity") or {}
    _require(
        _sha(integrity.get("task_set_fingerprint_sha256"), "task_set_fingerprint_sha256")
        == "b3e9c845d74b0b479af0fd95d9015de92697fbd82b7bf07f9765378dfafd11d9",
        "task-set fingerprint drift",
    )
    _sha(integrity.get("private_batch_metadata_sha256"), "private_batch_metadata_sha256")
    _require(
        integrity.get("private_batch_relpath")
        == "batches/identity-standard-code-binding-v3.json",
        "private batch relpath drift",
    )
    _require(integrity.get("raw_rows_emitted") is False, "raw rows illegally emitted")
    _require(
        integrity.get("security_identifiers_emitted") is False,
        "security identifiers illegally emitted",
    )

    boundary = data.get("post_run_boundary") or {}
    for key in (
        "bulk_execution_consent_disabled_again",
        "identity_binding_consent_disabled_again",
        "start_command_restored_to_preflight_only",
    ):
        _require(boundary.get(key) is True, f"{key} guard lost")
    for key in (
        "per_security_history_authorized",
        "status_economics_authorized",
        "expected_scope_network_execution_authorized",
        "feature_performance_testing_authorized",
        "sealed_holdout_authorized",
        "genuine_live_authorized",
        "live_trading_authorized",
    ):
        _require(boundary.get(key) is False, f"{key} illegally true")

    return {
        "valid": True,
        "stage": "IDENTITY_STANDARD_CODE_BINDING",
        "task_count": 145,
        "completed_task_count": 145,
        "network_request_attempt_count": 145,
        "phase_complete": True,
        "per_security_history_authorized": False,
        "sealed_holdout_authorized": False,
        "live_trading_authorized": False,
    }


def validate_file(path: Path = PATH) -> dict[str, Any]:
    return validate_evidence(json.loads(path.read_text(encoding="utf-8")))


if __name__ == "__main__":
    print(json.dumps(validate_file(), ensure_ascii=False, indent=2))
