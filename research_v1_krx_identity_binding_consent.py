"""Fail-closed validator for KRX IDENTITY_STANDARD_CODE_BINDING consent."""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Mapping

from research_v1_krx_historical_worker_entrypoint import (
    IDENTITY_BINDING_CONSENT_ENV,
    IDENTITY_BINDING_CONSENT_SENTINEL,
)

PATH = Path("INDEXALERT_KRX_IDENTITY_BINDING_CONSENT_CONTRACT.json")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


class KRXIdentityBindingConsentError(ValueError):
    pass


def _require(cond: bool, msg: str) -> None:
    if not cond:
        raise KRXIdentityBindingConsentError(msg)


def validate_contract(data: Mapping[str, Any]) -> dict[str, Any]:
    _require(isinstance(data, Mapping), "contract must be an object")
    _require(data.get("schema_version") == "1", "schema_version drift")
    _require(
        data.get("contract_id") == "INDEXALERT-KRX-IDENTITY-BINDING-CONSENT-v1",
        "contract_id drift",
    )
    _require(data.get("stage") == "IDENTITY_STANDARD_CODE_BINDING", "stage drift")

    prereq = data.get("prerequisite") or {}
    _require(
        prereq.get("identity_seed_evidence_id")
        == "INDEXALERT-KRX-HIST-IDENTITY-SEED-2026-10-02-v1",
        "identity seed evidence binding drift",
    )
    _require(prereq.get("identity_seed_phase_complete") is True, "seed completion lost")
    _require(
        int(prereq.get("identity_seed_completed_task_count", -1)) == 27,
        "seed task count drift",
    )
    seed_sha = str(prereq.get("identity_seed_private_batch_metadata_sha256") or "")
    _require(bool(SHA256_RE.fullmatch(seed_sha)), "seed batch SHA-256 invalid")

    user = data.get("user_authorization") or {}
    _require(
        user.get("exact_user_approval_phrase")
        == "I_AUTHORIZE_INDEXALERT_KRX_IDENTITY_BINDING_v1",
        "user approval phrase drift",
    )
    _require(user.get("authorized") is False, "binding cannot be pre-authorized")
    _require(user.get("one_shot") is True, "binding authorization must be one-shot")
    _require(
        user.get("prior_identity_seed_authorization_reusable") is False,
        "seed authorization reuse illegally allowed",
    )

    runtime = data.get("runtime_gate") or {}
    _require(
        runtime.get("bulk_consent_env") == "KRX_HISTORICAL_ACQUISITION_CONSENT",
        "bulk consent env drift",
    )
    _require(
        runtime.get("bulk_consent_sentinel")
        == "I_AUTHORIZE_INDEXALERT_KRX_HIST_ACQ_v3",
        "bulk consent sentinel drift",
    )
    _require(
        runtime.get("stage_consent_env") == IDENTITY_BINDING_CONSENT_ENV,
        "binding consent env drift",
    )
    _require(
        runtime.get("stage_consent_sentinel") == IDENTITY_BINDING_CONSENT_SENTINEL,
        "binding consent sentinel drift",
    )
    _require(runtime.get("both_consents_required") is True, "dual-consent guard lost")
    _require(
        runtime.get("entrypoint")
        == "python research_v1_krx_historical_worker_entrypoint.py --execute-identity-standard-code-binding",
        "binding entrypoint drift",
    )

    lock = data.get("post_run_lock") or {}
    for key in (
        "disable_bulk_consent_again",
        "disable_stage_consent_again",
        "restore_preflight_only_start_command",
    ):
        _require(lock.get(key) is True, f"{key} guard lost")
    _require(
        lock.get("raw_rows_publicly_emitted") is False,
        "raw-row publication illegally enabled",
    )
    _require(
        lock.get("later_stage_auto_authorization") is False,
        "later-stage auto authorization illegally enabled",
    )

    authority = data.get("authority") or {}
    for key in (
        "expected_scope_network_execution_authorized",
        "per_security_history_execution_authorized",
        "status_economics_execution_authorized",
        "feature_performance_testing_authorized",
        "sealed_holdout_authorized",
        "shadow_s1_authorized",
        "live_trading_authorized",
    ):
        _require(authority.get(key) is False, f"{key} illegally true")

    return {
        "valid": True,
        "stage": "IDENTITY_STANDARD_CODE_BINDING",
        "authorized": False,
        "one_shot": True,
        "prior_seed_authorization_reusable": False,
        "dual_consent_required": True,
        "sealed_holdout_authorized": False,
        "live_trading_authorized": False,
    }


def validate_file(path: Path = PATH) -> dict[str, Any]:
    return validate_contract(json.loads(path.read_text(encoding="utf-8")))


if __name__ == "__main__":
    print(json.dumps(validate_file(), ensure_ascii=False, indent=2))
