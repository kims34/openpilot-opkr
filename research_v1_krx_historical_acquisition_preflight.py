"""Network-free preflight for the frozen KRX historical acquisition plan.

It validates rights, plan identity/fingerprint, credential presence and an exact
user execution-consent sentinel. It never imports the KRX client and never
performs a network request.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Mapping

from research_v1_krx_historical_acquisition_plan import validate_file as validate_plan_file
from research_v1_krx_historical_acquisition_rights import validate_file as validate_rights_file
from research_v1_krx_historical_execution_contract import validate_file as validate_execution_contract_file
from research_v1_krx_private_store import (
    KRXPrivateStoreError,
    validate_private_root_path,
)


PLAN_PATH = Path("INDEXALERT_KRX_HISTORICAL_ACQUISITION_PLAN.json")
CONSENT_ENV = "KRX_HISTORICAL_ACQUISITION_CONSENT"
CONSENT_SENTINEL = "I_AUTHORIZE_INDEXALERT_KRX_HIST_ACQ_v2"


def evaluate_historical_acquisition_preflight(
    *,
    environment: Mapping[str, str] | None = None,
    git_worktree: str | os.PathLike[str] | None = None,
) -> dict[str, Any]:
    env=dict(os.environ if environment is None else environment)
    plan=validate_plan_file(PLAN_PATH)
    rights=validate_rights_file()
    execution_contract=validate_execution_contract_file()

    id_present=bool(str(env.get("KRX_ID") or "").strip())
    pw_present=bool(str(env.get("KRX_PW") or "").strip())
    openapi_key_present=bool(str(env.get("KRX_AUTH_KEY") or "").strip())
    consent=str(env.get(CONSENT_ENV) or "").strip()
    consent_ok=consent == CONSENT_SENTINEL
    raw_root_text=str(env.get("KRX_PRIVATE_RAW_DIR") or "").strip()
    raw_root_valid=False
    raw_root_error=None
    if raw_root_text:
        try:
            validate_private_root_path(
                raw_root_text,
                git_worktree=(Path.cwd() if git_worktree is None else git_worktree),
            )
            raw_root_valid=True
        except KRXPrivateStoreError as exc:
            raw_root_error=str(exc)

    missing=[]
    if not id_present:
        missing.append("KRX_ID")
    if not pw_present:
        missing.append("KRX_PW")
    if not openapi_key_present:
        missing.append("KRX_AUTH_KEY")
    if not rights["rights_authorized"]:
        missing.append("KRX_FULL_HISTORY_RIGHTS")
    if not execution_contract["private_persistent_storage_required"]:
        missing.append("PRIVATE_PERSISTENT_STORAGE_CONTRACT")
    if not raw_root_text:
        missing.append("KRX_PRIVATE_RAW_DIR")
    elif not raw_root_valid:
        missing.append("SAFE_KRX_PRIVATE_RAW_DIR")
    if not consent_ok:
        missing.append("EXPLICIT_HISTORICAL_ACQUISITION_EXECUTION_CONSENT")

    ready=not missing
    return {
        "plan_id":plan["plan_id"],
        "plan_fingerprint_sha256":plan["plan_fingerprint_sha256"],
        "rights_authorized":rights["rights_authorized"],
        "high_frequency_collection_authorized":rights["high_frequency_collection_authorized"],
        "full_historical_download_rights_authorized":rights["full_historical_download_rights_authorized"],
        "krx_id_present":id_present,
        "krx_pw_present":pw_present,
        "krx_openapi_auth_key_present":openapi_key_present,
        "execution_contract_id":execution_contract["contract_id"],
        "private_persistent_storage_required":execution_contract["private_persistent_storage_required"],
        "private_raw_dir_configured":bool(raw_root_text),
        "private_raw_dir_valid":raw_root_valid,
        "private_raw_dir_error":raw_root_error,
        "explicit_execution_consent_present":consent_ok,
        "historical_acquisition_network_execution_authorized":ready,
        "network_request_attempted":False,
        "missing_requirements":missing,
        "feature_performance_testing_authorized":False,
        "sealed_holdout_authorized":False,
        "live_trading_authorized":False,
        "guardrail":"This preflight is network-free. Even a ready result authorizes only execution of the frozen acquisition plan, not source admission, performance testing, holdout or trading.",
    }


if __name__=="__main__":
    print(json.dumps(evaluate_historical_acquisition_preflight(),ensure_ascii=False,indent=2))
