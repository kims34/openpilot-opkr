"""Fail-closed validator for dedicated KRX historical worker deployment."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping


CONTRACT_PATH = Path("INDEXALERT_KRX_HISTORICAL_WORKER_DEPLOYMENT_CONTRACT.json")
DOCKERFILE_PATH = Path("Dockerfile.krx-historical-worker")
REQUIREMENTS_PATH = Path("requirements-krx-historical-worker.txt")


class KRXHistoricalWorkerDeploymentError(ValueError):
    pass


def _require(cond: bool, msg: str) -> None:
    if not cond:
        raise KRXHistoricalWorkerDeploymentError(msg)


def validate_deployment_contract(data: Mapping[str, Any]) -> dict[str, Any]:
    _require(isinstance(data, Mapping), "deployment contract must be an object")
    _require(data.get("schema_version") == "1", "schema_version drift")
    _require(
        data.get("deployment_contract_id")
        == "INDEXALERT-KRX-HIST-WORKER-DEPLOY-v1",
        "deployment_contract_id drift",
    )
    _require(
        data.get("historical_acquisition_plan_id")
        == "INDEXALERT-KRX-HIST-ACQ-v3",
        "plan binding drift",
    )
    _require(
        data.get("historical_execution_contract_id")
        == "INDEXALERT-KRX-HIST-EXEC-v3",
        "execution contract binding drift",
    )
    _require(data.get("repository") == "kims34/openpilot-opkr", "repository drift")
    _require(data.get("branch") == "index-alert-research-v1", "branch drift")
    _require(
        data.get("service_name") == "indexalert-krx-historical-worker",
        "service name drift",
    )
    _require(
        data.get("dockerfile_path") == "Dockerfile.krx-historical-worker",
        "Dockerfile path drift",
    )
    _require(
        data.get("deployment_mode") == "PREFLIGHT_ONLY_BY_DEFAULT",
        "default deployment mode drift",
    )
    _require(data.get("public_domain_forbidden") is True, "public domain prohibition lost")
    _require(data.get("cron_forbidden") is True, "cron prohibition lost")
    _require(data.get("restart_policy") == "NEVER", "restart policy drift")

    volume = data.get("required_volume") or {}
    _require(volume.get("dedicated_persistent_volume") is True, "dedicated volume requirement lost")
    _require(volume.get("mount_path") == "/data", "volume mount path drift")
    _require(
        volume.get("raw_root") == "/data/indexalert/krx-historical-v3",
        "raw root drift",
    )
    _require(
        volume.get("must_be_visible_in_railway_service_config_before_execution")
        is True,
        "Railway volume attestation requirement lost",
    )
    _require(
        volume.get("sharing_with_public_runtime_forbidden") is True,
        "public runtime volume-sharing prohibition lost",
    )

    variables = data.get("required_variables") or {}
    _require(
        set(variables)
        == {
            "KRX_ID",
            "KRX_PW",
            "KRX_AUTH_KEY",
            "KRX_PRIVATE_RAW_DIR",
            "INDEXALERT_KRX_HIST_WORKER_ROLE",
        },
        "required variable set drift",
    )
    for key in ("KRX_ID", "KRX_PW", "KRX_AUTH_KEY"):
        _require(variables[key].get("secret") is True, f"{key} secret boundary lost")
    _require(
        variables["KRX_PRIVATE_RAW_DIR"].get("exact_value")
        == "/data/indexalert/krx-historical-v3",
        "KRX_PRIVATE_RAW_DIR drift",
    )
    _require(
        variables["INDEXALERT_KRX_HIST_WORKER_ROLE"].get("exact_value")
        == "DEDICATED_ONE_SHOT",
        "worker role drift",
    )

    attestation = data.get("railway_runtime_attestation") or {}
    _require(
        attestation.get("RAILWAY_SERVICE_NAME_expected")
        == "indexalert-krx-historical-worker",
        "Railway service attestation drift",
    )
    _require(
        set(attestation.get("forbidden_service_names") or [])
        == {"indexalert-runtime", "indexalert-backend", "indexalert-push"},
        "forbidden Railway services drift",
    )

    consent = data.get("execution_consent") or {}
    _require(
        consent.get("env_name") == "KRX_HISTORICAL_ACQUISITION_CONSENT",
        "bulk consent env drift",
    )
    _require(
        consent.get("exact_value") == "I_AUTHORIZE_INDEXALERT_KRX_HIST_ACQ_v3",
        "bulk consent sentinel drift",
    )
    _require(
        consent.get("must_be_absent_during_initial_preflight_deployment") is True,
        "initial consent absence requirement lost",
    )
    _require(
        consent.get("may_be_set_only_after_explicit_user_bulk_execution_approval")
        is True,
        "explicit user bulk approval requirement lost",
    )

    start = data.get("start_contract") or {}
    _require(
        start.get("default_command")
        == "python research_v1_krx_historical_worker_entrypoint.py",
        "default command drift",
    )
    _require(
        start.get("default_network_request_attempted") is False,
        "default network state drift",
    )
    _require(
        start.get("execute_identity_seed_command")
        == "python research_v1_krx_historical_worker_entrypoint.py --execute-identity-seed",
        "execute command drift",
    )
    _require(
        start.get("execute_command_forbidden_until_user_bulk_approval") is True,
        "execute-command approval guard lost",
    )
    _require(
        start.get("execute_identity_standard_code_binding_command")
        == "python research_v1_krx_historical_worker_entrypoint.py --execute-identity-standard-code-binding",
        "identity-binding execute command drift",
    )
    _require(
        start.get(
            "execute_identity_standard_code_binding_forbidden_until_user_bulk_approval"
        )
        is True,
        "identity-binding approval guard lost",
    )
    _require(
        start.get("prepare_per_security_history_command")
        == "python research_v1_krx_historical_worker_entrypoint.py --prepare-per-security-history",
        "per-security preparation command drift",
    )
    _require(
        start.get("prepare_per_security_history_network_request_attempted") is False,
        "per-security preparation must remain network-free",
    )
    _require(
        start.get("prepare_per_security_history_bulk_consent_required") is False,
        "network-free preparation must not require bulk consent",
    )
    _require(
        start.get("prepare_per_security_history_requires_completed_identity_binding")
        is True,
        "per-security preparation predecessor guard lost",
    )
    _require(
        start.get("prepare_per_security_history_requires_dedicated_worker_private_volume")
        is True,
        "per-security preparation private-worker guard lost",
    )
    _require(
        start.get("execute_per_security_history_command")
        == "python research_v1_krx_historical_worker_entrypoint.py --execute-per-security-history",
        "per-security execute command drift",
    )
    _require(
        start.get("execute_per_security_history_forbidden_until_user_bulk_approval")
        is True,
        "per-security bulk-approval guard lost",
    )
    _require(
        start.get("execute_per_security_history_requires_prepared_private_manifest")
        is True,
        "per-security prepared-manifest guard lost",
    )
    _require(
        start.get("execute_per_security_history_requires_completed_identity_binding")
        is True,
        "per-security predecessor guard lost",
    )
    _require(
        start.get("prepare_status_economics_command")
        == "python research_v1_krx_historical_worker_entrypoint.py --prepare-status-economics",
        "status-economics preparation command drift",
    )
    _require(
        start.get("prepare_status_economics_network_request_attempted") is False,
        "status-economics preparation must remain network-free",
    )
    _require(
        start.get("prepare_status_economics_bulk_consent_required") is False,
        "network-free status-economics preparation must not require bulk consent",
    )
    _require(
        start.get("prepare_status_economics_requires_completed_per_security_history")
        is True,
        "status-economics predecessor guard lost",
    )
    _require(
        start.get("prepare_status_economics_exact_realized_economics_claim_allowed")
        is False,
        "KRX price context must never claim exact realized economics",
    )
    _require(
        start.get("execute_status_economics_command")
        == "python research_v1_krx_historical_worker_entrypoint.py --execute-status-economics",
        "status-economics execute command drift",
    )
    _require(
        start.get("execute_status_economics_forbidden_until_user_bulk_approval")
        is True,
        "status-economics bulk-approval guard lost",
    )
    _require(
        start.get("execute_status_economics_requires_prepared_private_manifest")
        is True,
        "status-economics prepared-manifest guard lost",
    )
    _require(
        start.get("execute_status_economics_requires_completed_per_security_history")
        is True,
        "status-economics predecessor guard lost",
    )
    _require(
        start.get("execute_status_economics_exact_realized_economics_claim_allowed")
        is False,
        "status-economics execution must not claim exact realized economics",
    )

    authority = data.get("authority") or {}
    for key in (
        "service_creation_authorized",
        "volume_creation_or_attachment_authorized",
        "bulk_network_execution_authorized_by_user",
        "feature_performance_testing_authorized",
        "sealed_holdout_authorized",
        "live_trading_authorized",
    ):
        _require(authority.get(key) is False, f"{key} illegally true")

    return {
        "valid": True,
        "deployment_contract_id": data["deployment_contract_id"],
        "preflight_only_by_default": True,
        "dedicated_volume_required": True,
        "service_creation_authorized": False,
        "volume_creation_or_attachment_authorized": False,
        "bulk_network_execution_authorized_by_user": False,
        "sealed_holdout_authorized": False,
        "live_trading_authorized": False,
    }


def validate_worker_requirements(text: str) -> dict[str, Any]:
    lines = [line.strip() for line in str(text).splitlines() if line.strip()]
    rendered = "\n".join(lines)
    pinned = (
        "krx-data-api @ https://github.com/beaten-by-the-market/krx-data-api/"
        "archive/e6ebac9b71482db127348d8a08ebc6743aa3b50e.zip"
    )
    _require(pinned in rendered, "pinned KRX client missing from requirements")
    krx_lines = [line for line in lines if line.startswith("krx-data-api ")]
    _require(
        len(krx_lines) == 1,
        "requirements must contain exactly one krx-data-api pin",
    )
    return {
        "valid": True,
        "pinned_client": True,
        "pinned_client_commit": "e6ebac9b71482db127348d8a08ebc6743aa3b50e",
    }


def validate_worker_dockerfile(text: str) -> dict[str, Any]:
    lines = [line.strip() for line in str(text).splitlines() if line.strip()]
    rendered = "\n".join(lines)
    _require(
        "COPY requirements-krx-historical-worker.txt ./" in rendered,
        "worker requirements file must be copied into image",
    )
    _require(
        "pip install -r requirements-krx-historical-worker.txt" in rendered,
        "worker requirements file must be installed",
    )
    _require(
        'CMD ["python", "research_v1_krx_historical_worker_entrypoint.py"]'
        in rendered,
        "Dockerfile must default to preflight-only entrypoint",
    )
    cmd_lines = [line for line in lines if line.startswith("CMD ")]
    _require(len(cmd_lines) == 1, "Dockerfile must have exactly one CMD")
    _require(
        "--execute-identity-seed" not in cmd_lines[0],
        "Dockerfile CMD must not execute historical acquisition",
    )
    _require("EXPOSE " not in rendered, "worker Dockerfile must not expose a public port")
    for prefix in (
        "ENV KRX_ID=",
        "ENV KRX_PW=",
        "ENV KRX_AUTH_KEY=",
        "ENV KRX_HISTORICAL_ACQUISITION_CONSENT=",
        "ARG KRX_ID",
        "ARG KRX_PW",
        "ARG KRX_AUTH_KEY",
    ):
        _require(prefix not in rendered, f"secret/consent material forbidden in Dockerfile: {prefix}")
    return {
        "valid": True,
        "default_mode": "PREFLIGHT_ONLY",
        "requirements_installed": True,
        "public_port_exposed": False,
        "bulk_execute_in_default_cmd": False,
    }


def validate_files() -> dict[str, Any]:
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    return {
        "contract": validate_deployment_contract(contract),
        "requirements": validate_worker_requirements(
            REQUIREMENTS_PATH.read_text(encoding="utf-8")
        ),
        "dockerfile": validate_worker_dockerfile(
            DOCKERFILE_PATH.read_text(encoding="utf-8")
        ),
    }


if __name__ == "__main__":
    print(json.dumps(validate_files(), ensure_ascii=False, indent=2))
