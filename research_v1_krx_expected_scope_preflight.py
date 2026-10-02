"""Network-free preflight for independent KRX expected-scope attestation.

This preflight is deliberately separate from the historical Data Marketplace
bulk-acquisition consent. It authorizes no network request unless the exact
expected-scope consent sentinel is present.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Mapping

from research_v1_krx_expected_scope_attestation import validate_file as validate_scope_contract
from research_v1_krx_private_store import (
    KRXPrivateStoreError,
    validate_private_root_path,
)

CONSENT_ENV = "KRX_EXPECTED_SCOPE_ATTESTATION_CONSENT"
CONSENT_SENTINEL = "I_AUTHORIZE_INDEXALERT_KRX_EXPECTED_SCOPE_ATTESTATION_v1"
WORKER_ROLE_ENV = "INDEXALERT_KRX_HIST_WORKER_ROLE"
WORKER_ROLE_VALUE = "DEDICATED_ONE_SHOT"
SERVICE_ENV = "RAILWAY_SERVICE_NAME"
EXPECTED_SERVICE = "indexalert-krx-historical-worker"
FORBIDDEN_SERVICES = {"indexalert-runtime","indexalert-backend","indexalert-push"}


def evaluate_expected_scope_preflight(
    *,
    environment: Mapping[str, str] | None = None,
    git_worktree: str | os.PathLike[str] | None = None,
) -> dict[str, Any]:
    env = dict(os.environ if environment is None else environment)
    contract = validate_scope_contract()

    auth_key_present = bool(str(env.get("KRX_AUTH_KEY") or "").strip())
    consent_ok = str(env.get(CONSENT_ENV) or "").strip() == CONSENT_SENTINEL
    worker_role = str(env.get(WORKER_ROLE_ENV) or "").strip()
    worker_role_ok = worker_role == WORKER_ROLE_VALUE
    service = str(env.get(SERVICE_ENV) or "").strip()
    service_ok = service == EXPECTED_SERVICE
    forbidden_service = service in FORBIDDEN_SERVICES

    raw_root_text = str(env.get("KRX_PRIVATE_RAW_DIR") or "").strip()
    raw_root_valid = False
    raw_root_error = None
    if raw_root_text:
        try:
            validate_private_root_path(
                raw_root_text,
                git_worktree=(Path.cwd() if git_worktree is None else git_worktree),
            )
            raw_root_valid = True
        except KRXPrivateStoreError as exc:
            raw_root_error = str(exc)

    missing = []
    if not auth_key_present:
        missing.append("KRX_AUTH_KEY")
    if not worker_role_ok:
        missing.append("DEDICATED_ONE_SHOT_WORKER_ROLE")
    if not service_ok or forbidden_service:
        missing.append("DEDICATED_WORKER_SERVICE_ISOLATION")
    if not raw_root_text:
        missing.append("KRX_PRIVATE_RAW_DIR")
    elif not raw_root_valid:
        missing.append("SAFE_KRX_PRIVATE_RAW_DIR")
    if not consent_ok:
        missing.append("EXPLICIT_EXPECTED_SCOPE_ATTESTATION_CONSENT")

    ready = not missing
    return {
        "contract_id": contract["contract_id"],
        "calendar_date_count": contract["calendar_date_count"],
        "krx_openapi_auth_key_present": auth_key_present,
        "dedicated_worker_role_present": worker_role_ok,
        "railway_service_name": service or None,
        "dedicated_worker_service_ok": bool(service_ok and not forbidden_service),
        "private_raw_dir_configured": bool(raw_root_text),
        "private_raw_dir_valid": raw_root_valid,
        "private_raw_dir_error": raw_root_error,
        "explicit_execution_consent_present": consent_ok,
        "expected_scope_network_execution_authorized": ready,
        "missing_requirements": missing,
        "network_request_attempted": False,
        "source_gate_c_closed": False,
        "source_gate_d_closed": False,
        "source_gate_e_closed": False,
        "feature_performance_testing_authorized": False,
        "sealed_holdout_authorized": False,
        "live_trading_authorized": False,
        "guardrail": (
            "This preflight is network-free and separate from historical bulk "
            "Data Marketplace consent. A ready result authorizes only the frozen "
            "OpenAPI expected-scope attestation job."
        ),
    }


if __name__ == "__main__":
    print(json.dumps(evaluate_expected_scope_preflight(), ensure_ascii=False, indent=2))
