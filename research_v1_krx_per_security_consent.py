"""Fail-closed validator for KRX per-security one-shot consent contract."""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Mapping

PATH = Path("INDEXALERT_KRX_PER_SECURITY_HISTORY_CONSENT_CONTRACT.json")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


class KRXPerSecurityConsentError(ValueError):
    pass


def _require(cond: bool, msg: str) -> None:
    if not cond:
        raise KRXPerSecurityConsentError(msg)


def validate_contract(data: Mapping[str, Any]) -> dict[str, Any]:
    _require(isinstance(data, Mapping), "contract must be an object")
    _require(data.get("schema_version") == "1", "schema_version drift")
    _require(
        data.get("contract_id") == "INDEXALERT-KRX-PER-SECURITY-HISTORY-CONSENT-v1",
        "contract_id drift",
    )
    _require(data.get("stage") == "PER_SECURITY_HISTORY", "stage drift")
    _require(data.get("status") == "FROZEN_NOT_YET_USER_AUTHORIZED", "status drift")

    pre = data.get("prerequisite") or {}
    _require(pre.get("identity_binding_phase_complete") is True, "identity binding prerequisite lost")
    _require(int(pre.get("identity_binding_completed_task_count", -1)) == 145, "identity binding count drift")

    prepared = data.get("prepared_task_set") or {}
    _require(int(prepared.get("task_count", -1)) == 14296, "prepared task count drift")
    _require(
        prepared.get("task_count_by_kind")
        == {
            "investor_trading_individual_daily": 9485,
            "trading_halt": 4811,
        },
        "prepared task-kind counts drift",
    )
    for field in ("task_set_fingerprint_sha256", "private_task_manifest_metadata_sha256"):
        _require(bool(SHA256_RE.fullmatch(str(prepared.get(field) or ""))), f"{field} must be SHA-256")
    _require(
        prepared.get("task_set_fingerprint_sha256")
        == "fb5b883c6fe0e9c15e88aea9bdf874ddd7a11ae8a009c2ddf91c4e4249a8ba38",
        "prepared task-set fingerprint drift",
    )
    _require(
        prepared.get("private_task_manifest_metadata_sha256")
        == "0d98f45168cedeecc013e95c71abe661ca1fac9df0403ba477d2f5653572c116",
        "prepared private manifest hash drift",
    )
    _require(prepared.get("network_request_attempted_during_prepare") is False, "prepare network guard lost")

    user = data.get("user_authorization") or {}
    _require(
        user.get("exact_user_approval_phrase")
        == "I_AUTHORIZE_INDEXALERT_KRX_PER_SECURITY_HISTORY_v1",
        "approval phrase drift",
    )
    _require(user.get("authorized") is False, "stage cannot be pre-authorized")
    _require(user.get("one_shot") is True, "one-shot guard lost")
    _require(user.get("earlier_stage_authorization_reusable") is False, "earlier approval reuse illegally enabled")
    _require(user.get("reusable") is False, "approval reuse illegally enabled")

    gate = data.get("runtime_gate") or {}
    _require(gate.get("both_consents_required") is True, "dual consent guard lost")
    _require(gate.get("bulk_consent_env") == "KRX_HISTORICAL_ACQUISITION_CONSENT", "bulk consent env drift")
    _require(gate.get("stage_consent_env") == "KRX_PER_SECURITY_HISTORY_CONSENT", "stage consent env drift")
    _require(gate.get("stage_consent_sentinel") == "I_AUTHORIZE_INDEXALERT_KRX_PER_SECURITY_HISTORY_v1", "stage sentinel drift")
    _require(
        gate.get("entrypoint")
        == "python research_v1_krx_historical_worker_entrypoint.py --execute-per-security-history",
        "entrypoint drift",
    )

    lock = data.get("post_run_lock") or {}
    for key in (
        "disable_bulk_consent_again",
        "disable_stage_consent_again",
        "restore_preflight_only_start_command",
    ):
        _require(lock.get(key) is True, f"{key} guard lost")
    _require(lock.get("raw_rows_publicly_emitted") is False, "raw-row public leak allowed")
    _require(lock.get("later_stage_auto_authorization") is False, "later-stage auto authority enabled")

    authority = data.get("authority") or {}
    for key in (
        "per_security_history_execution_authorized",
        "status_economics_execution_authorized",
        "expected_scope_network_execution_authorized",
        "feature_performance_testing_authorized",
        "sealed_holdout_authorized",
        "shadow_s1_authorized",
        "genuine_live_authorized",
        "live_trading_authorized",
    ):
        _require(authority.get(key) is False, f"{key} illegally true")

    return {
        "valid": True,
        "task_count": 14296,
        "authorized": False,
        "one_shot": True,
        "later_stage_auto_authorization": False,
    }


def validate_file(path: Path = PATH) -> dict[str, Any]:
    return validate_contract(json.loads(path.read_text(encoding="utf-8")))


if __name__ == "__main__":
    print(json.dumps(validate_file(), ensure_ascii=False, indent=2))
