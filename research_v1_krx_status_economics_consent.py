"""Fail-closed validator for STATUS_ECONOMICS consent shell."""
from __future__ import annotations
import json
from pathlib import Path
from typing import Any, Mapping

PATH = Path("INDEXALERT_KRX_STATUS_ECONOMICS_CONSENT_CONTRACT.json")


class KRXStatusEconomicsConsentError(ValueError):
    pass


def _require(cond: bool, msg: str) -> None:
    if not cond:
        raise KRXStatusEconomicsConsentError(msg)


def validate_contract(data: Mapping[str, Any]) -> dict[str, Any]:
    _require(isinstance(data, Mapping), "contract must be an object")
    _require(data.get("schema_version") == "1", "schema_version drift")
    _require(data.get("contract_id") == "INDEXALERT-KRX-STATUS-ECONOMICS-CONSENT-v1", "contract_id drift")
    _require(data.get("stage") == "STATUS_ECONOMICS", "stage drift")
    _require(
        data.get("status")
        == "FROZEN_SHELL_PREPARATION_NOT_COMPLETE_EXECUTION_NOT_AUTHORIZED",
        "status drift",
    )

    pre = data.get("predecessor") or {}
    _require(pre.get("phase") == "PER_SECURITY_HISTORY", "predecessor drift")
    _require(int(pre.get("expected_task_count", -1)) == 14296, "predecessor count drift")
    _require(
        pre.get("expected_task_set_fingerprint_sha256")
        == "fb5b883c6fe0e9c15e88aea9bdf874ddd7a11ae8a009c2ddf91c4e4249a8ba38",
        "predecessor fingerprint drift",
    )
    _require(pre.get("exact_complete_required") is True, "exact-complete guard lost")
    _require(int(pre.get("failed_task_count_required", -1)) == 0, "failed-count guard drift")
    _require(pre.get("post_run_relock_required") is True, "post-run relock guard lost")
    _require(pre.get("current_observed_complete") is False, "predecessor completion prematurely asserted")

    prep = data.get("preparation_gate") or {}
    _require(
        prep.get("command")
        == "python research_v1_krx_historical_worker_entrypoint.py --prepare-status-economics",
        "prepare command drift",
    )
    _require(prep.get("network_request_attempted_required") is False, "prepare network guard lost")
    _require(prep.get("private_task_manifest_relpath") == "task_manifests/status-economics-v3.json", "manifest relpath drift")
    _require(prep.get("prepared_task_count") is None, "prepared task count prematurely frozen")
    _require(prep.get("prepared_task_set_fingerprint_sha256") is None, "prepared fingerprint prematurely frozen")
    _require(prep.get("prepared_private_manifest_metadata_sha256") is None, "prepared manifest hash prematurely frozen")
    _require(prep.get("exact_status_economics_ready_required") is False, "exact economics readiness guard lost")
    _require(prep.get("preparation_complete") is False, "preparation prematurely complete")
    _require(prep.get("execution_scope_frozen") is False, "execution scope prematurely frozen")

    user = data.get("user_authorization") or {}
    _require(user.get("exact_user_approval_phrase") == "I_AUTHORIZE_INDEXALERT_KRX_STATUS_ECONOMICS_v1", "approval phrase drift")
    _require(user.get("authorized") is False, "stage cannot be pre-authorized")
    _require(user.get("one_shot") is True, "one-shot guard lost")
    _require(user.get("prior_stage_authorization_reusable") is False, "prior-stage approval reuse enabled")
    _require(user.get("reusable") is False, "approval reuse enabled")

    gate = data.get("runtime_gate") or {}
    _require(gate.get("both_consents_required") is True, "dual-consent guard lost")
    _require(gate.get("exact_prepared_scope_required") is True, "exact prepared scope guard lost")
    _require(gate.get("stage_consent_env") == "KRX_STATUS_ECONOMICS_CONSENT", "stage consent env drift")
    _require(gate.get("stage_consent_sentinel") == "I_AUTHORIZE_INDEXALERT_KRX_STATUS_ECONOMICS_v1", "stage sentinel drift")
    _require(
        gate.get("entrypoint")
        == "python research_v1_krx_historical_worker_entrypoint.py --execute-status-economics",
        "entrypoint drift",
    )

    authority = data.get("authority") or {}
    for key in (
        "status_economics_execution_authorized",
        "expected_scope_network_execution_authorized",
        "exact_status_economics_claim_allowed",
        "feature_performance_testing_authorized",
        "sealed_holdout_authorized",
        "shadow_s1_authorized",
        "genuine_live_authorized",
        "live_trading_authorized",
    ):
        _require(authority.get(key) is False, f"{key} illegally true")

    return {
        "valid": True,
        "preparation_complete": False,
        "execution_scope_frozen": False,
        "authorized": False,
        "prior_stage_authorization_reusable": False,
        "sealed_holdout_authorized": False,
        "live_trading_authorized": False,
    }


def validate_file(path: Path = PATH) -> dict[str, Any]:
    return validate_contract(json.loads(path.read_text(encoding="utf-8")))


if __name__ == "__main__":
    print(json.dumps(validate_file(), ensure_ascii=False, indent=2))
