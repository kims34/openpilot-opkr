"""Fail-closed validator for Railway KRX worker provisioning readiness evidence."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

PATH = Path("INDEXALERT_KRX_WORKER_PROVISIONING_READINESS_EVIDENCE.json")

class KRXWorkerProvisioningEvidenceError(ValueError):
    pass

def _require(cond: bool, msg: str) -> None:
    if not cond:
        raise KRXWorkerProvisioningEvidenceError(msg)

def validate_provisioning_evidence(data: Mapping[str, Any]) -> dict[str, Any]:
    _require(isinstance(data, Mapping), "evidence must be an object")
    _require(data.get("schema_version") == "1", "schema_version drift")
    _require(
        data.get("evidence_class") == "RAILWAY_READ_ONLY_PROVISIONING_GAP_AUDIT",
        "unexpected evidence_class",
    )
    _require(data.get("railway_project") == "IndexAlert", "Railway project drift")
    _require(data.get("railway_environment") == "production", "Railway environment drift")
    _require(
        data.get("required_worker_service_name") == "indexalert-krx-historical-worker",
        "worker service name drift",
    )
    _require(data.get("dedicated_worker_service_present") is False, "worker service presence must remain false for this snapshot")

    runtime_volume = data.get("existing_public_runtime_volume") or {}
    _require(runtime_volume.get("service_name") == "indexalert-runtime", "runtime volume service drift")
    _require(runtime_volume.get("mount_path") == "/data", "runtime volume mount drift")
    _require(runtime_volume.get("reuse_for_historical_worker_forbidden") is True, "runtime volume reuse guard lost")

    _require(data.get("dedicated_worker_volume_present") is False, "dedicated worker volume presence must remain false for this snapshot")
    required_volume = data.get("required_worker_volume") or {}
    _require(required_volume.get("mount_path") == "/data", "worker mount path drift")
    _require(
        required_volume.get("raw_root") == "/data/indexalert/krx-historical-v3",
        "worker raw root drift",
    )
    _require(required_volume.get("sharing_with_public_runtime_forbidden") is True, "volume sharing guard lost")

    required_vars = data.get("required_worker_variables") or {}
    _require(set(required_vars.get("secret_names") or []) == {"KRX_ID","KRX_PW","KRX_AUTH_KEY"}, "worker secret-name set drift")
    nonsecret = required_vars.get("nonsecret_exact") or {}
    _require(nonsecret.get("KRX_PRIVATE_RAW_DIR") == "/data/indexalert/krx-historical-v3", "KRX_PRIVATE_RAW_DIR drift")
    _require(nonsecret.get("INDEXALERT_KRX_HIST_WORKER_ROLE") == "DEDICATED_ONE_SHOT", "worker role drift")
    _require(required_vars.get("bulk_consent_env") == "KRX_HISTORICAL_ACQUISITION_CONSENT", "bulk consent env drift")
    _require(required_vars.get("bulk_consent_must_be_absent_initially") is True, "initial bulk-consent absence guard lost")

    deploy = data.get("required_deploy_shape") or {}
    _require(deploy.get("repository") == "kims34/openpilot-opkr", "repo drift")
    _require(deploy.get("branch") == "index-alert-research-v1", "branch drift")
    _require(deploy.get("dockerfile") == "Dockerfile.krx-historical-worker", "Dockerfile drift")
    _require(deploy.get("default_command") == "python research_v1_krx_historical_worker_entrypoint.py", "default command drift")
    _require(deploy.get("public_domain_forbidden") is True, "public-domain guard lost")
    _require(deploy.get("cron_forbidden") is True, "cron guard lost")
    _require(deploy.get("restart_policy") == "NEVER", "restart policy drift")

    blockers=set(data.get("current_blockers") or [])
    expected_blockers={
        "DEDICATED_WORKER_SERVICE_NOT_CREATED",
        "DEDICATED_PRIVATE_VOLUME_NOT_CREATED_OR_ATTACHED",
        "WORKER_ONLY_KRX_SECRETS_NOT_CONFIGURED",
        "SERVICE_AND_VOLUME_CREATION_NOT_EXPLICITLY_AUTHORIZED",
    }
    _require(blockers == expected_blockers, "provisioning blocker set drift")

    authority=data.get("authority") or {}
    for key in (
        "service_creation_authorized",
        "volume_creation_or_attachment_authorized",
        "worker_secret_configuration_authorized",
        "bulk_network_execution_authorized_by_user",
        "expected_scope_network_execution_authorized_by_user",
        "sealed_holdout_authorized",
        "live_trading_authorized",
    ):
        _require(authority.get(key) is False, f"{key} illegally true")

    return {
        "valid": True,
        "worker_service_present": False,
        "dedicated_worker_volume_present": False,
        "runtime_volume_reuse_allowed": False,
        "service_creation_authorized": False,
        "volume_creation_or_attachment_authorized": False,
        "bulk_network_execution_authorized_by_user": False,
        "sealed_holdout_authorized": False,
        "live_trading_authorized": False,
    }

def validate_file(path: Path = PATH) -> dict[str, Any]:
    return validate_provisioning_evidence(json.loads(path.read_text(encoding="utf-8")))

if __name__ == "__main__":
    print(json.dumps(validate_file(), ensure_ascii=False, indent=2))
