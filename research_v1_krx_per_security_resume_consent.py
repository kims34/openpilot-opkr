"""Fail-closed validator for PER_SECURITY_HISTORY resume consent."""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Mapping

PATH = Path("INDEXALERT_KRX_PER_SECURITY_HISTORY_RESUME_CONSENT_CONTRACT.json")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")

WAITING = "WAITING_FOR_EXPLICIT_USER_AUTHORIZATION"
VERIFIED_WAITING = "FIX_VERIFIED_WAITING_FOR_EXPLICIT_USER_AUTHORIZATION"
READY = "USER_AUTHORIZED_RESUME_READY"
IN_PROGRESS = "RESUME_EXECUTION_IN_PROGRESS"
COMPLETE_CONSUMED = "RESUME_COMPLETE_AUTHORITY_CONSUMED"


class KRXPerSecurityResumeConsentError(ValueError):
    pass


def _require(cond: bool, msg: str) -> None:
    if not cond:
        raise KRXPerSecurityResumeConsentError(msg)


def _sha(value: Any, field: str) -> str:
    text = str(value or "").strip().lower()
    _require(bool(SHA256_RE.fullmatch(text)), f"{field} must be SHA-256")
    return text


def validate_contract(data: Mapping[str, Any]) -> dict[str, Any]:
    _require(isinstance(data, Mapping), "contract must be an object")
    _require(data.get("schema_version") == "1", "schema_version drift")
    _require(
        data.get("contract_id")
        == "INDEXALERT-KRX-PER-SECURITY-HISTORY-RESUME-CONSENT-v1",
        "contract_id drift",
    )
    _require(data.get("stage") == "PER_SECURITY_HISTORY_RESUME", "stage drift")
    status = str(data.get("status") or "")
    _require(
        status in {WAITING, VERIFIED_WAITING, READY, IN_PROGRESS, COMPLETE_CONSUMED},
        "status drift",
    )

    scope = data.get("frozen_scope") or {}
    _require(int(scope.get("expected_task_count", -1)) == 14296, "expected count drift")
    _require(int(scope.get("checkpoint_completed_task_count", -1)) == 11750, "checkpoint count drift")
    _require(int(scope.get("remaining_task_count", -1)) == 2546, "remaining count drift")
    _require(int(scope.get("failed_task_count", -1)) == 0, "failed count drift")
    _require(scope.get("phase_status") == "IN_PROGRESS", "checkpoint phase status drift")
    _require(scope.get("phase_complete") is False, "checkpoint phase_complete drift")
    _require(
        _sha(scope.get("task_set_fingerprint_sha256"), "task_set_fingerprint_sha256")
        == "fb5b883c6fe0e9c15e88aea9bdf874ddd7a11ae8a009c2ddf91c4e4249a8ba38",
        "task-set fingerprint drift",
    )
    _require(
        _sha(
            scope.get("private_task_manifest_metadata_sha256"),
            "private_task_manifest_metadata_sha256",
        )
        == "0d98f45168cedeecc013e95c71abe661ca1fac9df0403ba477d2f5653572c116",
        "private manifest hash drift",
    )
    _require(
        scope.get("interruption_evidence_id")
        == "INDEXALERT-KRX-PER-SECURITY-HISTORY-INTERRUPTION-2026-10-03-v1",
        "interruption evidence binding drift",
    )
    _require(
        int(scope["checkpoint_completed_task_count"])
        + int(scope["remaining_task_count"])
        == int(scope["expected_task_count"]),
        "checkpoint accounting drift",
    )

    fix = data.get("code_fix") or {}
    _require(
        fix.get("bug_reason_code") == "ALPHANUMERIC_SHORT_CODE_VALIDATOR_MISMATCH",
        "bug reason drift",
    )
    _require(
        fix.get("short_code_contract") == "ASCII_ALPHANUMERIC_EXACTLY_6",
        "short-code contract drift",
    )
    _require(fix.get("regression_test_required") is True, "regression-test guard lost")
    _require(fix.get("official_krx_ci_required") is True, "CI guard lost")

    user = data.get("user_authorization") or {}
    _require(
        user.get("exact_user_approval_phrase")
        == "I_AUTHORIZE_INDEXALERT_KRX_PER_SECURITY_HISTORY_RESUME_v1",
        "resume approval phrase drift",
    )
    _require(user.get("one_shot") is True, "one-shot guard lost")
    _require(user.get("original_authorization_reusable") is False, "original approval reuse enabled")
    _require(user.get("reusable") is False, "resume approval reuse enabled")

    gate = data.get("runtime_gate") or {}
    _require(
        gate.get("resume_consent_env") == "KRX_PER_SECURITY_HISTORY_RESUME_CONSENT",
        "resume consent env drift",
    )
    _require(
        gate.get("resume_consent_sentinel")
        == "I_AUTHORIZE_INDEXALERT_KRX_PER_SECURITY_HISTORY_RESUME_v1",
        "resume sentinel drift",
    )
    _require(gate.get("bulk_consent_env") == "KRX_HISTORICAL_ACQUISITION_CONSENT", "bulk env drift")
    _require(gate.get("stage_consent_env") == "KRX_PER_SECURITY_HISTORY_CONSENT", "stage env drift")
    _require(gate.get("exact_checkpoint_required") is True, "checkpoint guard lost")
    _require(gate.get("exact_frozen_scope_required") is True, "frozen-scope guard lost")
    _require(gate.get("fresh_deployment_required") is True, "fresh-deployment guard lost")
    _require(
        gate.get("redeploy_existing_crashed_deployment_forbidden") is True,
        "crashed deployment reuse guard lost",
    )
    _require(
        gate.get("entrypoint")
        == "python research_v1_krx_historical_worker_entrypoint.py --execute-per-security-history",
        "resume entrypoint drift",
    )

    def _require_verified_fix() -> tuple[str, str]:
        source_revision = str(gate.get("source_revision") or "").strip()
        fix_revision = str(fix.get("source_revision") or "").strip()
        preflight_revision = str(gate.get("preflight_source_revision") or "").strip()
        preflight_deployment = str(gate.get("preflight_deployment_id") or "").strip()
        _require(bool(source_revision), "resume source revision required")
        _require(bool(fix_revision), "code-fix source revision required")
        _require(fix_revision == source_revision, "code-fix source binding drift")
        _require(fix.get("official_krx_ci_passed") is True, "official KRX CI proof missing")
        _require(gate.get("preflight_verified") is True, "resume preflight not verified")
        _require(bool(preflight_deployment), "resume preflight deployment required")
        _require(preflight_revision == source_revision, "resume preflight source drift")
        _require(
            gate.get("preflight_network_request_attempted") is False,
            "resume preflight attempted network",
        )
        _require(
            gate.get("preflight_dockerfile") == "Dockerfile.krx-historical-worker",
            "resume preflight Dockerfile drift",
        )
        return source_revision, preflight_deployment


    authority = data.get("authority") or {}
    for key in (
        "status_economics_execution_authorized",
        "expected_scope_network_execution_authorized",
        "feature_performance_testing_authorized",
        "sealed_holdout_authorized",
        "shadow_s1_authorized",
        "genuine_live_authorized",
        "live_trading_authorized",
    ):
        _require(authority.get(key) is False, f"{key} illegally true")

    if status == WAITING:
        _require(user.get("authorized") is False, "resume cannot be pre-authorized")
        _require(user.get("received_date_kst") is None, "authorization date prematurely present")
        _require(fix.get("source_revision") is None, "fix source prematurely bound")
        _require(fix.get("official_krx_ci_passed") is False, "CI state prematurely verified")
        _require(gate.get("deployment_id") is None, "deployment prematurely bound")
        _require(gate.get("source_revision") is None, "runtime source prematurely bound")
        _require(gate.get("preflight_verified") is False, "preflight prematurely verified")
        _require(gate.get("preflight_deployment_id") is None, "preflight deployment prematurely bound")
        _require(gate.get("preflight_source_revision") is None, "preflight source prematurely bound")
        _require(gate.get("preflight_network_request_attempted") is None, "preflight network state prematurely bound")
        _require(gate.get("preflight_dockerfile") is None, "preflight Dockerfile prematurely bound")
        _require(authority.get("resume_network_execution_authorized") is False, "resume authority illegally true")
        _require(data.get("completion") in (None, {}), "completion prematurely present")
        authorized = False
        completed = False
    elif status == VERIFIED_WAITING:
        source_revision, _ = _require_verified_fix()
        _require(user.get("authorized") is False, "verified waiting cannot be authorized")
        _require(user.get("received_date_kst") is None, "authorization date prematurely present")
        _require(gate.get("deployment_id") is None, "execution deployment prematurely bound")
        _require(authority.get("resume_network_execution_authorized") is False, "resume authority illegally true")
        _require(data.get("completion") in (None, {}), "completion prematurely present")
        authorized = False
        completed = False
    elif status in {READY, IN_PROGRESS}:
        source_revision, _ = _require_verified_fix()
        _require(user.get("authorized") is True, "resume authorization record lost")
        _require(user.get("consumed") is not True, "resume authority prematurely consumed")
        _require(bool(str(user.get("received_date_kst") or "").strip()), "resume authorization date required")
        deployment_id = str(gate.get("deployment_id") or "").strip()
        _require(bool(deployment_id), "resume deployment required")
        _require(
            deployment_id != "bc79d1b5-5fb8-46c7-8067-682e61947014",
            "crashed deployment cannot be reused",
        )
        _require(authority.get("resume_network_execution_authorized") is True, "resume authority record lost")
        _require(data.get("completion") in (None, {}), "completion prematurely present")
        authorized = True
        completed = False
    else:
        _require_verified_fix()
        _require(user.get("authorized") is False, "completed resume authority still active")
        _require(user.get("consumed") is True, "completed resume authority not consumed")
        _require(authority.get("resume_network_execution_authorized") is False, "completed resume authority still active")
        completion = data.get("completion") or {}
        _require(
            completion.get("evidence_id")
            == "INDEXALERT-KRX-PER-SECURITY-HISTORY-EXEC-2026-10-03-v1",
            "completion evidence binding drift",
        )
        _require(int(completion.get("completed_task_count", -1)) == 14296, "completion count drift")
        _require(int(completion.get("failed_task_count", -1)) == 0, "completion has failures")
        _require(completion.get("phase_status") == "COMPLETE", "completion phase status drift")
        _require(completion.get("phase_complete") is True, "completion phase_complete lost")
        for key in (
            "bulk_execution_consent_disabled_again",
            "per_security_consent_disabled_again",
            "resume_consent_disabled_again",
            "start_command_restored_to_preflight_only",
            "preflight_network_request_attempted_false",
        ):
            _require(completion.get(key) is True, f"{key} guard lost")
        authorized = False
        completed = True

    return {
        "valid": True,
        "status": status,
        "checkpoint_completed_task_count": 11750,
        "remaining_task_count": 2546,
        "authorized": authorized,
        "completed": completed,
        "sealed_holdout_authorized": False,
        "live_trading_authorized": False,
    }


def validate_file(path: Path = PATH) -> dict[str, Any]:
    return validate_contract(json.loads(path.read_text(encoding="utf-8")))


if __name__ == "__main__":
    print(json.dumps(validate_file(), ensure_ascii=False, indent=2))
