"""Fail-closed validator for KRX worker provisioning consent contract."""
from __future__ import annotations
import json
from pathlib import Path
from typing import Any, Mapping

PATH=Path("INDEXALERT_KRX_WORKER_PROVISIONING_CONSENT_CONTRACT.json")

class KRXWorkerProvisioningConsentError(ValueError):
    pass

def _require(cond: bool, msg: str) -> None:
    if not cond:
        raise KRXWorkerProvisioningConsentError(msg)

def validate_contract(data: Mapping[str, Any]) -> dict[str, Any]:
    _require(isinstance(data, Mapping), "contract must be an object")
    _require(data.get("schema_version")=="1", "schema_version drift")
    _require(data.get("contract_id")=="INDEXALERT-KRX-WORKER-PROVISIONING-v1", "contract_id drift")
    _require(data.get("exact_user_approval_phrase")=="I_AUTHORIZE_INDEXALERT_KRX_WORKER_PROVISIONING_v1", "approval phrase drift")
    _require("may incur" in str(data.get("cost_notice") or ""), "cost notice missing")

    allowed=set(data.get("allowed_mutations_after_explicit_approval") or [])
    _require(any("indexalert-krx-historical-worker" in x for x in allowed), "worker creation scope missing")
    _require(any("dedicated persistent volume at /data" in x for x in allowed), "dedicated volume scope missing")
    _require(any("preflight-only deployment" in x for x in allowed), "preflight-only scope missing")

    forbidden=" ".join(str(x) for x in (data.get("explicitly_not_authorized") or []))
    for marker in (
        "KRX_HISTORICAL_ACQUISITION_CONSENT",
        "KRX_EXPECTED_SCOPE_ATTESTATION_CONSENT",
        "--execute-identity-seed",
        "--execute-per-security-history",
        "sealed holdout",
        "live trading",
    ):
        _require(marker in forbidden, f"forbidden scope marker missing: {marker}")

    secret=data.get("secret_boundary") or {}
    _require(set(secret.get("required_worker_secret_names") or [])=={"KRX_ID","KRX_PW","KRX_AUTH_KEY"}, "secret-name set drift")
    _require(secret.get("secret_values_must_not_be_committed_to_git") is True, "git secret guard lost")
    _require(secret.get("secret_values_must_not_be_sent_in_chat") is True, "chat secret guard lost")

    auth=data.get("authority") or {}
    for key in (
        "provisioning_authorized_by_user",
        "worker_service_creation_authorized",
        "dedicated_volume_creation_authorized",
        "worker_secret_configuration_authorized",
        "bulk_network_execution_authorized_by_user",
        "expected_scope_network_execution_authorized_by_user",
        "sealed_holdout_authorized",
        "live_trading_authorized",
    ):
        _require(auth.get(key) is False, f"{key} illegally true")

    return {
        "valid":True,
        "provisioning_authorized_by_user":False,
        "bulk_network_execution_authorized_by_user":False,
        "expected_scope_network_execution_authorized_by_user":False,
        "sealed_holdout_authorized":False,
        "live_trading_authorized":False,
    }

def validate_file(path: Path=PATH) -> dict[str, Any]:
    return validate_contract(json.loads(path.read_text(encoding="utf-8")))

if __name__=="__main__":
    print(json.dumps(validate_file(),ensure_ascii=False,indent=2))
