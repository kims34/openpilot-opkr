"""Fail-closed validator for KRX worker provisioning consent contract."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

PATH = Path("INDEXALERT_KRX_WORKER_PROVISIONING_CONSENT_CONTRACT.json")


class KRXWorkerProvisioningConsentError(ValueError):
    pass


def _require(cond: bool, msg: str) -> None:
    if not cond:
        raise KRXWorkerProvisioningConsentError(msg)


def validate_contract(data: Mapping[str, Any]) -> dict[str, Any]:
    _require(isinstance(data, Mapping), "contract must be an object")
    _require(data.get("schema_version") == "1", "schema_version drift")
    _require(data.get("contract_id") == "INDEXALERT-KRX-WORKER-PROVISIONING-v1", "contract_id drift")
    _require(
        data.get("exact_user_approval_phrase") == "I_AUTHORIZE_INDEXALERT_KRX_WORKER_PROVISIONING_v1",
        "approval phrase drift",
    )
    _require("may incur" in str(data.get("cost_notice") or ""), "cost notice missing")

    allowed = set(data.get("allowed_mutations_after_explicit_approval") or [])
    _require(any("indexalert-krx-historical-worker" in x for x in allowed), "worker creation scope missing")
    _require(any("dedicated persistent volume at /data" in x for x in allowed), "dedicated volume scope missing")
    _require(any("preflight-only deployment" in x for x in allowed), "preflight-only scope missing")

    forbidden = " ".join(str(x) for x in (data.get("explicitly_not_authorized") or []))
    for marker in (
        "KRX_HISTORICAL_ACQUISITION_CONSENT",
        "KRX_EXPECTED_SCOPE_ATTESTATION_CONSENT",
        "--execute-identity-seed",
        "--execute-per-security-history",
        "sealed holdout",
        "live trading",
    ):
        _require(marker in forbidden, f"forbidden scope marker missing: {marker}")

    secret = data.get("secret_boundary") or {}
    _require(
        set(secret.get("required_worker_secret_names") or []) == {"KRX_ID", "KRX_PW", "KRX_AUTH_KEY"},
        "secret-name set drift",
    )
    _require(secret.get("secret_values_must_not_be_committed_to_git") is True, "git secret guard lost")
    _require(secret.get("secret_values_must_not_be_sent_in_chat") is True, "chat secret guard lost")

    auth = data.get("authority") or {}
    for key in (
        "worker_secret_configuration_authorized",
        "bulk_network_execution_authorized_by_user",
        "expected_scope_network_execution_authorized_by_user",
        "sealed_holdout_authorized",
        "live_trading_authorized",
    ):
        _require(auth.get(key) is False, f"{key} illegally true")

    provisioning_authorized = auth.get("provisioning_authorized_by_user")
    _require(isinstance(provisioning_authorized, bool), "provisioning authorization must be boolean")

    if provisioning_authorized:
        _require(auth.get("worker_service_creation_authorized") is True, "worker service creation authorization missing")
        _require(auth.get("dedicated_volume_creation_authorized") is True, "dedicated volume creation authorization missing")
        record = data.get("execution_record") or {}
        _require(record.get("provisioning_completed") is True, "authorized provisioning requires completed execution record")
        _require(bool(record.get("authorized_at")), "authorized_at missing")
        _require(bool(record.get("service_id")), "service_id missing")
        _require(bool(record.get("volume_id")), "volume_id missing")
        _require(record.get("corrected_preflight_deployment_status") == "SUCCESS", "preflight deployment not successful")
        _require(record.get("preflight_mode") == "PREFLIGHT_ONLY", "preflight mode drift")
        _require(record.get("network_request_attempted") is False, "KRX network request illegally attempted")
        _require(
            record.get("historical_acquisition_network_execution_authorized") is False,
            "historical acquisition execution illegally authorized",
        )
        _require(
            record.get("expected_scope_network_execution_authorized") is False,
            "expected-scope execution illegally authorized",
        )
        _require(record.get("sealed_holdout_authorized") is False, "sealed holdout illegally authorized")
        _require(record.get("live_trading_authorized") is False, "live trading illegally authorized")
    else:
        _require(auth.get("worker_service_creation_authorized") is False, "worker service creation illegally true")
        _require(auth.get("dedicated_volume_creation_authorized") is False, "dedicated volume creation illegally true")

    return {
        "valid": True,
        "provisioning_authorized_by_user": provisioning_authorized,
        "worker_service_creation_authorized": auth.get("worker_service_creation_authorized") is True,
        "dedicated_volume_creation_authorized": auth.get("dedicated_volume_creation_authorized") is True,
        "worker_secret_configuration_authorized": False,
        "bulk_network_execution_authorized_by_user": False,
        "expected_scope_network_execution_authorized_by_user": False,
        "sealed_holdout_authorized": False,
        "live_trading_authorized": False,
    }


def validate_file(path: Path = PATH) -> dict[str, Any]:
    return validate_contract(json.loads(path.read_text(encoding="utf-8")))


if __name__ == "__main__":
    print(json.dumps(validate_file(), ensure_ascii=False, indent=2))
