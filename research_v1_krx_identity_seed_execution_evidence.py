"""Fail-closed validator for real KRX historical IDENTITY_SEED execution evidence."""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Mapping

PATH = Path("INDEXALERT_KRX_HISTORICAL_IDENTITY_SEED_EXECUTION_EVIDENCE.json")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


class KRXIdentitySeedExecutionEvidenceError(ValueError):
    pass


def _require(cond: bool, msg: str) -> None:
    if not cond:
        raise KRXIdentitySeedExecutionEvidenceError(msg)


def _sha(value: Any, field: str) -> str:
    text = str(value or "").strip().lower()
    _require(bool(SHA256_RE.fullmatch(text)), f"{field} must be SHA-256")
    return text


def validate_evidence(data: Mapping[str, Any]) -> dict[str, Any]:
    _require(isinstance(data, Mapping), "evidence must be an object")
    _require(data.get("schema_version") == "1", "schema_version drift")
    _require(
        data.get("evidence_id") == "INDEXALERT-KRX-HIST-IDENTITY-SEED-2026-10-02-v1",
        "evidence_id drift",
    )
    _require(data.get("plan_id") == "INDEXALERT-KRX-HIST-ACQ-v3", "plan_id drift")
    _require(
        data.get("execution_contract_id") == "INDEXALERT-KRX-HIST-EXEC-v3",
        "execution_contract_id drift",
    )

    execution = data.get("execution") or {}
    _require(
        execution.get("railway_service") == "indexalert-krx-historical-worker",
        "Railway worker drift",
    )
    _require(
        execution.get("source_revision") == "6343f01b493404d59736e06eb6968e9820d0e595",
        "source revision drift",
    )
    _require(
        execution.get("dockerfile") == "Dockerfile.krx-historical-worker",
        "Dockerfile drift",
    )
    _require(execution.get("mode") == "EXECUTE_IDENTITY_SEED", "mode drift")
    _require(int(execution.get("task_count", -1)) == 27, "task_count must be 27")
    _require(
        int(execution.get("completed_task_count", -1)) == 27,
        "completed_task_count must be 27",
    )
    _require(int(execution.get("resumed_task_count", -1)) == 0, "unexpected resumed tasks")
    _require(
        int(execution.get("network_request_attempt_count", -1)) == 27,
        "network_request_attempt_count must be 27",
    )
    _require(execution.get("phase_status") == "COMPLETE", "phase status is not COMPLETE")
    _require(execution.get("phase_complete") is True, "phase_complete must be true")

    integrity = data.get("integrity") or {}
    _sha(integrity.get("task_set_fingerprint_sha256"), "task_set_fingerprint_sha256")
    _sha(integrity.get("private_batch_metadata_sha256"), "private_batch_metadata_sha256")
    _require(
        integrity.get("private_batch_relpath") == "batches/identity-seed-v3.json",
        "private batch relpath drift",
    )
    _require(integrity.get("raw_rows_emitted") is False, "raw rows illegally emitted")

    boundary = data.get("post_run_boundary") or {}
    _require(
        boundary.get("execution_consent_disabled_again") is True,
        "post-run execution consent was not disabled",
    )
    _require(
        boundary.get("start_command_restored_to_preflight_only") is True,
        "post-run preflight start command was not restored",
    )
    for key in (
        "identity_standard_code_binding_authorized",
        "expected_scope_network_execution_authorized",
        "per_security_history_execution_authorized",
        "status_economics_execution_authorized",
        "feature_performance_testing_authorized",
        "source_gate_c_closed",
        "source_gate_d_closed",
        "source_gate_e_closed",
        "sealed_holdout_authorized",
        "live_trading_authorized",
    ):
        _require(boundary.get(key) is False, f"{key} illegally true")

    safety = data.get("safety_correction") or {}
    _require(
        int(safety.get("krx_network_requests_from_mismatched_attempts", -1)) == 0,
        "mismatched deployment attempted KRX requests",
    )
    _require(
        safety.get("research_branch_railway_json_pinned_to_worker_dockerfile") is True,
        "research branch worker Dockerfile pin missing",
    )

    return {
        "valid": True,
        "mode": "EXECUTE_IDENTITY_SEED",
        "task_count": 27,
        "completed_task_count": 27,
        "network_request_attempt_count": 27,
        "phase_complete": True,
        "source_gate_c_closed": False,
        "source_gate_d_closed": False,
        "source_gate_e_closed": False,
        "sealed_holdout_authorized": False,
        "live_trading_authorized": False,
    }


def validate_file(path: Path = PATH) -> dict[str, Any]:
    return validate_evidence(json.loads(path.read_text(encoding="utf-8")))


if __name__ == "__main__":
    print(json.dumps(validate_file(), ensure_ascii=False, indent=2))
