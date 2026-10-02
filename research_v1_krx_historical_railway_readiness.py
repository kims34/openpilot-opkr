"""Fail-closed validator for Railway historical-worker readiness evidence."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

PATH = Path("INDEXALERT_KRX_HISTORICAL_RAILWAY_READINESS_EVIDENCE.json")

GAP_AUDIT = "RAILWAY_READ_ONLY_INFRASTRUCTURE_GAP_AUDIT"
PREFLIGHT_EVIDENCE = "RAILWAY_PREFLIGHT_PROVISIONING_EVIDENCE"


class KRXHistoricalRailwayReadinessError(ValueError):
    pass


def _require(cond: bool, msg: str) -> None:
    if not cond:
        raise KRXHistoricalRailwayReadinessError(msg)


def _validate_required_worker(data: Mapping[str, Any]) -> Mapping[str, Any]:
    req = data.get("required_worker") or {}
    _require(req.get("service_name") == "indexalert-krx-historical-worker", "worker service drift")
    _require(req.get("branch") == "index-alert-research-v1", "branch drift")
    _require(req.get("dockerfile") == "Dockerfile.krx-historical-worker", "Dockerfile drift")
    _require(req.get("dedicated_volume_mount") == "/data", "volume mount drift")
    _require(req.get("private_raw_root") == "/data/indexalert/krx-historical-v3", "raw root drift")
    _require(req.get("public_domain_forbidden") is True, "public-domain guard lost")
    _require(req.get("cron_forbidden") is True, "cron guard lost")
    _require(req.get("restart_policy") == "NEVER", "restart-policy drift")
    _require(
        set(req.get("required_secret_names") or []) == {"KRX_ID", "KRX_PW", "KRX_AUTH_KEY"},
        "worker secret-name set drift",
    )
    nonsecret = req.get("required_nonsecret_variables") or {}
    _require(
        nonsecret.get("KRX_PRIVATE_RAW_DIR") == "/data/indexalert/krx-historical-v3",
        "KRX_PRIVATE_RAW_DIR drift",
    )
    _require(
        nonsecret.get("INDEXALERT_KRX_HIST_WORKER_ROLE") == "DEDICATED_ONE_SHOT",
        "worker role drift",
    )
    _require(
        req.get("bulk_consent_env") == "KRX_HISTORICAL_ACQUISITION_CONSENT",
        "bulk consent env drift",
    )
    _require(
        req.get("bulk_consent_must_be_absent_initially") is True,
        "initial bulk-consent guard lost",
    )
    return req


def _validate_shared_fail_closed_guards(data: Mapping[str, Any]) -> Mapping[str, Any]:
    _require(
        data.get("production_runtime_volume_reuse_allowed") is False,
        "production volume reuse illegally allowed",
    )
    _require(
        data.get("infrastructure_ready_for_bulk_execution") is False,
        "bulk execution readiness cannot be granted by Railway preflight evidence",
    )

    auth = data.get("authority") or {}
    for key in (
        "worker_secret_configuration_authorized",
        "bulk_network_execution_authorized_by_user",
        "expected_scope_network_execution_authorized_by_user",
        "feature_performance_testing_authorized",
        "sealed_holdout_authorized",
        "live_trading_authorized",
    ):
        _require(auth.get(key) is False, f"{key} illegally true")
    return auth


def _validate_runtime_observation(data: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    services = {str(x.get("name")): x for x in (data.get("observed_services") or [])}
    _require("indexalert-runtime" in services, "runtime observation missing")
    runtime = services["indexalert-runtime"]
    _require(runtime.get("has_volume") is True, "runtime volume observation drift")
    _require(runtime.get("volume_mount") == "/data", "runtime volume mount drift")
    _require(runtime.get("must_not_be_reused") is True, "runtime-volume isolation guard lost")
    return services


def _validate_gap_audit(data: Mapping[str, Any], auth: Mapping[str, Any]) -> dict[str, Any]:
    _require(data.get("worker_service_exists") is False, "worker service cannot be claimed present")
    _require(data.get("dedicated_worker_volume_exists") is False, "worker volume cannot be claimed present")
    _require(data.get("worker_only_secrets_configured") is False, "worker secrets cannot be claimed configured")
    _require(data.get("preflight_infrastructure_ready") in (None, False), "preflight readiness cannot be claimed")

    for key in ("service_creation_authorized", "volume_creation_or_attachment_authorized"):
        _require(auth.get(key) is False, f"{key} illegally true")

    return {
        "valid": True,
        "evidence_stage": "GAP_AUDIT",
        "worker_service_exists": False,
        "dedicated_worker_volume_exists": False,
        "worker_only_secrets_configured": False,
        "preflight_infrastructure_ready": False,
        "infrastructure_ready_for_bulk_execution": False,
        "service_creation_authorized": False,
        "volume_creation_or_attachment_authorized": False,
        "worker_secret_configuration_authorized": False,
        "bulk_network_execution_authorized_by_user": False,
        "expected_scope_network_execution_authorized_by_user": False,
        "sealed_holdout_authorized": False,
        "live_trading_authorized": False,
    }


def _validate_preflight_evidence(
    data: Mapping[str, Any],
    auth: Mapping[str, Any],
    services: Mapping[str, Mapping[str, Any]],
) -> dict[str, Any]:
    _require(data.get("worker_service_exists") is True, "preflight evidence requires worker service")
    _require(data.get("dedicated_worker_volume_exists") is True, "preflight evidence requires dedicated worker volume")
    _require(data.get("preflight_infrastructure_ready") is True, "preflight infrastructure readiness missing")
    _require(auth.get("service_creation_authorized") is True, "service_creation_authorized drift")
    _require(auth.get("volume_creation_or_attachment_authorized") is True, "volume_creation_or_attachment_authorized drift")

    worker = services.get("indexalert-krx-historical-worker")
    _require(worker is not None, "worker observation missing")
    _require(worker.get("has_volume") is True, "worker volume evidence drift")
    _require(worker.get("volume_mount") == "/data", "worker volume mount drift")
    _require(worker.get("public_domain") is False, "worker public domain illegally present")
    _require(worker.get("cron") is False, "worker cron illegally present")
    _require(worker.get("restart_policy") == "NEVER", "worker restart policy drift")
    _require(worker.get("dockerfile") == "Dockerfile.krx-historical-worker", "worker Dockerfile drift")
    _require(
        worker.get("start_command") == "python research_v1_krx_historical_worker_entrypoint.py",
        "worker start command drift",
    )
    _require(worker.get("corrected_preflight_deployment_status") == "SUCCESS", "worker preflight deployment not successful")

    preflight = data.get("runtime_preflight") or {}
    _require(preflight.get("mode") == "PREFLIGHT_ONLY", "runtime preflight mode drift")
    _require(preflight.get("explicit_execution_consent_present") is False, "bulk execution consent illegally present")
    _require(preflight.get("network_request_attempted") is False, "KRX network request illegally attempted")
    _require(
        preflight.get("historical_acquisition_network_execution_authorized") is False,
        "historical acquisition execution illegally authorized",
    )
    for key in (
        "feature_performance_testing_authorized",
        "sealed_holdout_authorized",
        "live_trading_authorized",
    ):
        _require(preflight.get(key) is False, f"runtime preflight {key} illegally true")

    secrets_configured = data.get("worker_only_secrets_configured")
    _require(isinstance(secrets_configured, bool), "worker secret readiness must be boolean")
    credential_flags = (
        preflight.get("krx_id_present"),
        preflight.get("krx_pw_present"),
        preflight.get("krx_openapi_auth_key_present"),
    )
    if secrets_configured:
        _require(all(x is True for x in credential_flags), "worker secret presence evidence incomplete")
    elif any(x is not None for x in credential_flags):
        _require(all(x is False for x in credential_flags), "worker secret presence contradicts snapshot")

    return {
        "valid": True,
        "evidence_stage": "PREFLIGHT_PROVISIONED",
        "worker_service_exists": True,
        "dedicated_worker_volume_exists": True,
        "worker_only_secrets_configured": secrets_configured,
        "preflight_infrastructure_ready": True,
        "infrastructure_ready_for_bulk_execution": False,
        "service_creation_authorized": True,
        "volume_creation_or_attachment_authorized": True,
        "worker_secret_configuration_authorized": False,
        "bulk_network_execution_authorized_by_user": False,
        "expected_scope_network_execution_authorized_by_user": False,
        "sealed_holdout_authorized": False,
        "live_trading_authorized": False,
    }


def validate_readiness(data: Mapping[str, Any]) -> dict[str, Any]:
    _require(isinstance(data, Mapping), "evidence must be an object")
    _require(data.get("schema_version") == "1", "schema_version drift")
    evidence_class = data.get("evidence_class")
    _require(evidence_class in {GAP_AUDIT, PREFLIGHT_EVIDENCE}, "evidence_class drift")

    _validate_required_worker(data)
    services = _validate_runtime_observation(data)
    auth = _validate_shared_fail_closed_guards(data)

    if evidence_class == GAP_AUDIT:
        return _validate_gap_audit(data, auth)
    return _validate_preflight_evidence(data, auth, services)


def validate_file(path: Path = PATH) -> dict[str, Any]:
    return validate_readiness(json.loads(path.read_text(encoding="utf-8")))


if __name__ == "__main__":
    print(json.dumps(validate_file(), ensure_ascii=False, indent=2))
