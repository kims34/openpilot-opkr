"""Fail-closed validator for network-free KRX identity-binding preparation evidence."""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Mapping

PATH = Path("INDEXALERT_KRX_IDENTITY_BINDING_PREPARATION_EVIDENCE.json")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


class KRXIdentityBindingPreparationEvidenceError(ValueError):
    pass


def _require(cond: bool, msg: str) -> None:
    if not cond:
        raise KRXIdentityBindingPreparationEvidenceError(msg)


def _sha(value: Any, field: str) -> str:
    text = str(value or "").strip().lower()
    _require(bool(SHA256_RE.fullmatch(text)), f"{field} must be SHA-256")
    return text


def validate_evidence(data: Mapping[str, Any]) -> dict[str, Any]:
    _require(isinstance(data, Mapping), "evidence must be an object")
    _require(data.get("schema_version") == "1", "schema_version drift")
    _require(
        data.get("evidence_id")
        == "INDEXALERT-KRX-IDENTITY-BINDING-PREP-2026-10-02-v1",
        "evidence_id drift",
    )
    _require(data.get("stage") == "IDENTITY_STANDARD_CODE_BINDING", "stage drift")
    _require(
        data.get("status") == "PREPARED_NETWORK_EXECUTION_NOT_AUTHORIZED",
        "status drift",
    )

    railway = data.get("railway") or {}
    _require(
        railway.get("service_name") == "indexalert-krx-historical-worker",
        "worker service drift",
    )
    _require(
        railway.get("source_revision")
        == "ab09e9a0aabf5bcaba53372b6f48b34796715e5d",
        "source revision drift",
    )
    _require(
        railway.get("dockerfile") == "Dockerfile.krx-historical-worker",
        "Dockerfile drift",
    )
    _require(
        railway.get("mode") == "PREPARE_IDENTITY_STANDARD_CODE_BINDING",
        "prepare mode drift",
    )

    prep = data.get("preparation") or {}
    _require(int(prep.get("task_count", -1)) == 145, "binding task count drift")
    _require(
        prep.get("task_count_by_kind") == {"security_master": 145},
        "binding task-kind count drift",
    )
    _sha(prep.get("task_set_fingerprint_sha256"), "task_set_fingerprint_sha256")
    _sha(
        prep.get("private_task_manifest_metadata_sha256"),
        "private_task_manifest_metadata_sha256",
    )
    _require(
        prep.get("private_task_manifest_relpath")
        == "task_manifests/identity-standard-code-binding-v1.json",
        "private manifest relpath drift",
    )
    _require(prep.get("phase_status") == "PENDING", "binding phase must remain PENDING")
    _require(prep.get("phase_complete") is False, "binding phase cannot be complete at prepare")
    _require(
        prep.get("network_request_attempted") is False,
        "network request illegally attempted during prepare",
    )
    _require(
        prep.get("security_identifiers_emitted") is False,
        "security identifiers illegally emitted",
    )
    _require(prep.get("raw_rows_emitted") is False, "raw rows illegally emitted")

    auth = data.get("authority") or {}
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
        _require(auth.get(key) is False, f"{key} illegally true")

    lock = data.get("post_prepare_lock") or {}
    _require(
        lock.get("start_command_restored_to_preflight_only") is True,
        "preflight-only start command was not restored",
    )
    _require(
        lock.get("bulk_execution_sentinel_active") is False,
        "bulk execution sentinel must remain inactive",
    )
    _require(
        lock.get("binding_stage_sentinel_active") is False,
        "binding stage sentinel must remain inactive",
    )

    return {
        "valid": True,
        "stage": "IDENTITY_STANDARD_CODE_BINDING",
        "task_count": 145,
        "phase_status": "PENDING",
        "network_request_attempted": False,
        "stage_specific_user_authorization_received": False,
        "sealed_holdout_authorized": False,
        "live_trading_authorized": False,
    }


def validate_file(path: Path = PATH) -> dict[str, Any]:
    return validate_evidence(json.loads(path.read_text(encoding="utf-8")))


if __name__ == "__main__":
    print(json.dumps(validate_file(), ensure_ascii=False, indent=2))
