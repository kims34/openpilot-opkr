"""Fail-closed validator for KRX per-security consent/resume lifecycle."""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Mapping

PATH = Path("INDEXALERT_KRX_PER_SECURITY_HISTORY_CONSENT_CONTRACT.json")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")

IN_PROGRESS = "USER_AUTHORIZED_EXECUTION_IN_PROGRESS"
INTERRUPTED_CONSUMED = "EXECUTION_INTERRUPTED_AUTHORITY_CONSUMED"
RESUME_IN_PROGRESS = "RESUME_USER_AUTHORIZED_EXECUTION_IN_PROGRESS"
COMPLETE_CONSUMED = "EXECUTION_COMPLETE_AUTHORITY_CONSUMED"

TASK_COUNT = 14296
CHECKPOINT_COUNT = 11750
REMAINING_COUNT = 2546
TASK_SHA = "fb5b883c6fe0e9c15e88aea9bdf874ddd7a11ae8a009c2ddf91c4e4249a8ba38"
MANIFEST_SHA = "0d98f45168cedeecc013e95c71abe661ca1fac9df0403ba477d2f5653572c116"
ORIGINAL_DEPLOYMENT = "bc79d1b5-5fb8-46c7-8067-682e61947014"
ORIGINAL_REVISION = "9009c48a00394063c813d29219507ee2190ce09e"
INTERRUPTION_EVIDENCE_ID = "INDEXALERT-KRX-PER-SECURITY-HISTORY-INTERRUPTION-2026-10-03-v1"
COMPLETION_EVIDENCE_ID = "INDEXALERT-KRX-PER-SECURITY-HISTORY-EXEC-2026-10-03-v1"
RESUME_SENTINEL = "I_AUTHORIZE_INDEXALERT_KRX_PER_SECURITY_HISTORY_RESUME_v1"


class KRXPerSecurityConsentError(ValueError):
    pass


def _require(cond: bool, msg: str) -> None:
    if not cond:
        raise KRXPerSecurityConsentError(msg)


def _sha(value: Any, field: str) -> str:
    text = str(value or "").strip().lower()
    _require(bool(SHA256_RE.fullmatch(text)), f"{field} must be SHA-256")
    return text


def _validate_interruption(intr: Mapping[str, Any]) -> None:
    _require(intr.get("deployment_id") == ORIGINAL_DEPLOYMENT, "interruption deployment drift")
    _require(intr.get("source_revision") == ORIGINAL_REVISION, "interruption source revision drift")
    _require(intr.get("crashed_at_utc") == "2026-10-03T00:45:16Z", "interruption timestamp drift")
    _require(intr.get("error_class") == "KRXHistoricalRequestExecutorError", "interruption error class drift")
    _require(intr.get("reason_code") == "ALPHANUMERIC_SHORT_CODE_VALIDATOR_MISMATCH", "interruption reason drift")
    _require(intr.get("raw_security_identifier_emitted") is False, "interruption leaked identifier")
    _require(int(intr.get("checkpoint_count_observed", -1)) == CHECKPOINT_COUNT, "checkpoint count drift")
    _require(int(intr.get("remaining_task_count", -1)) == REMAINING_COUNT, "remaining task count drift")
    _require(intr.get("checkpoint_preservation_verified") is True, "checkpoint preservation not verified")
    _require(intr.get("checkpoint_probe_deployment_id") == "92439b24-644a-4d3d-a888-9e0ba568bfac", "checkpoint probe deployment drift")
    _require(intr.get("checkpoint_probe_source_revision") == "d156f0dc6056924a798679bd9e93e1f2eb0241fc", "checkpoint probe source revision drift")
    _require(intr.get("checkpoint_probe_network_request_attempted") is False, "checkpoint probe attempted network")
    _require(int(intr.get("checkpoint_probe_failed_task_count", -1)) == 0, "checkpoint probe failure drift")
    _require(intr.get("checkpoint_probe_phase_complete") is False, "checkpoint probe illegally complete")
    _require(intr.get("interruption_evidence_id") == INTERRUPTION_EVIDENCE_ID, "interruption evidence binding drift")
    for key in (
        "bulk_execution_consent_disabled_again",
        "per_security_consent_disabled_again",
        "start_command_restored_to_preflight_only",
        "restart_policy_never",
    ):
        _require(intr.get(key) is True, f"interruption {key} guard lost")
    _require(intr.get("resume_requires_new_user_authorization") is True, "new resume authorization guard lost")
    _require(intr.get("resume_consent_env") == "KRX_PER_SECURITY_HISTORY_RESUME_CONSENT", "resume consent env drift")
    _require(intr.get("resume_consent_sentinel") == RESUME_SENTINEL, "resume consent sentinel drift")
    for key in (
        "later_stage_auto_authorization",
        "status_economics_authorized",
        "expected_scope_network_execution_authorized",
        "feature_performance_testing_authorized",
        "sealed_holdout_authorized",
        "genuine_live_authorized",
        "live_trading_authorized",
    ):
        _require(intr.get(key) is False, f"interruption {key} illegally true")


def _validate_resume_binding(data: Mapping[str, Any], *, complete: bool) -> None:
    auth = data.get("resume_authorization") or {}
    _require(auth.get("exact_user_approval_phrase") == RESUME_SENTINEL, "resume approval phrase drift")
    _require(bool(str(auth.get("received_date_kst") or "").strip()), "resume authorization date required")
    _require(auth.get("one_shot") is True, "resume one-shot guard lost")
    _require(auth.get("reusable") is False, "resume approval reuse enabled")
    _require(auth.get("same_frozen_scope_only") is True, "resume scope expansion enabled")
    deployment = str(auth.get("consumed_for_deployment_id") or "").strip()
    revision = str(auth.get("source_revision") or "").strip()
    _require(bool(deployment), "resume deployment binding required")
    _require(bool(revision), "resume source revision binding required")

    rex = data.get("resume_execution") or {}
    _require(rex.get("deployment_id") == deployment, "resume execution deployment drift")
    _require(rex.get("source_revision") == revision, "resume execution source revision drift")
    _require(
        rex.get("start_command")
        == "python research_v1_krx_historical_worker_entrypoint.py --execute-per-security-history",
        "resume start command drift",
    )
    _require(int(rex.get("task_count", -1)) == TASK_COUNT, "resume task count drift")
    _require(rex.get("task_set_fingerprint_sha256") == TASK_SHA, "resume task-set fingerprint drift")
    _require(int(rex.get("checkpoint_count_at_start", -1)) == CHECKPOINT_COUNT, "resume checkpoint count drift")
    _require(int(rex.get("remaining_task_count_at_start", -1)) == REMAINING_COUNT, "resume remaining count drift")
    _require(rex.get("interruption_evidence_id") == INTERRUPTION_EVIDENCE_ID, "resume interruption evidence drift")
    _require(rex.get("resume_consent_env") == "KRX_PER_SECURITY_HISTORY_RESUME_CONSENT", "resume consent env drift")
    _require(rex.get("resume_consent_sentinel") == RESUME_SENTINEL, "resume consent sentinel drift")
    for key in (
        "later_stage_auto_authorization",
        "status_economics_authorized",
        "expected_scope_network_execution_authorized",
        "feature_performance_testing_authorized",
        "sealed_holdout_authorized",
        "genuine_live_authorized",
        "live_trading_authorized",
    ):
        _require(rex.get(key) is False, f"resume execution {key} illegally true")

    if complete:
        _require(auth.get("authorized") is False, "completed resume authority still active")
        _require(auth.get("consumed") is True, "completed resume authority not consumed")
        _require(rex.get("execution_status") == "COMPLETE", "resume completed execution status drift")
    else:
        _require(auth.get("authorized") is True, "resume authorization record lost")
        _require(auth.get("consumed") is not True, "resume authority prematurely consumed")
        _require(rex.get("execution_status") == "IN_PROGRESS", "resume execution status drift")


def validate_contract(data: Mapping[str, Any]) -> dict[str, Any]:
    _require(isinstance(data, Mapping), "contract must be an object")
    _require(data.get("schema_version") == "1", "schema_version drift")
    _require(data.get("contract_id") == "INDEXALERT-KRX-PER-SECURITY-HISTORY-CONSENT-v1", "contract_id drift")
    _require(data.get("stage") == "PER_SECURITY_HISTORY", "stage drift")
    status = str(data.get("status") or "")
    _require(
        status in {IN_PROGRESS, INTERRUPTED_CONSUMED, RESUME_IN_PROGRESS, COMPLETE_CONSUMED},
        "status drift",
    )

    pre = data.get("prerequisite") or {}
    _require(pre.get("identity_binding_phase_complete") is True, "identity binding prerequisite lost")
    _require(int(pre.get("identity_binding_completed_task_count", -1)) == 145, "identity binding count drift")

    prepared = data.get("prepared_task_set") or {}
    _require(int(prepared.get("task_count", -1)) == TASK_COUNT, "prepared task count drift")
    _require(
        prepared.get("task_count_by_kind")
        == {"investor_trading_individual_daily": 9485, "trading_halt": 4811},
        "prepared task-kind counts drift",
    )
    _require(_sha(prepared.get("task_set_fingerprint_sha256"), "task_set_fingerprint_sha256") == TASK_SHA, "prepared task-set fingerprint drift")
    _require(_sha(prepared.get("private_task_manifest_metadata_sha256"), "private_task_manifest_metadata_sha256") == MANIFEST_SHA, "prepared private manifest hash drift")
    _require(prepared.get("network_request_attempted_during_prepare") is False, "prepare network guard lost")

    user = data.get("user_authorization") or {}
    _require(user.get("exact_user_approval_phrase") == "I_AUTHORIZE_INDEXALERT_KRX_PER_SECURITY_HISTORY_v1", "approval phrase drift")
    _require(user.get("received_date_kst") == "2026-10-03", "authorization date drift")
    _require(user.get("consumed_for_deployment_id") == ORIGINAL_DEPLOYMENT, "authorized deployment drift")
    _require(user.get("source_revision") == ORIGINAL_REVISION, "authorized source revision drift")
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

    execution = data.get("execution") or {}
    _require(execution.get("deployment_id") == ORIGINAL_DEPLOYMENT, "execution deployment drift")
    _require(execution.get("source_revision") == ORIGINAL_REVISION, "execution source revision drift")
    _require(
        execution.get("start_command")
        == "python research_v1_krx_historical_worker_entrypoint.py --execute-per-security-history",
        "execution start command drift",
    )
    _require(int(execution.get("task_count", -1)) == TASK_COUNT, "execution task count drift")
    _require(execution.get("task_set_fingerprint_sha256") == TASK_SHA, "execution task-set fingerprint drift")
    for key in (
        "later_stage_auto_authorization",
        "status_economics_authorized",
        "expected_scope_network_execution_authorized",
        "feature_performance_testing_authorized",
        "sealed_holdout_authorized",
        "genuine_live_authorized",
        "live_trading_authorized",
    ):
        _require(execution.get(key) is False, f"execution {key} illegally true")

    lock = data.get("post_run_lock") or {}
    for key in ("disable_bulk_consent_again", "disable_stage_consent_again", "restore_preflight_only_start_command"):
        _require(lock.get(key) is True, f"{key} guard lost")
    _require(lock.get("raw_rows_publicly_emitted") is False, "raw-row public leak allowed")
    _require(lock.get("later_stage_auto_authorization") is False, "later-stage auto authority enabled")

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

    if status == IN_PROGRESS:
        _require(user.get("authorized") is True, "authorized execution record lost")
        _require(user.get("consumed") is not True, "active authority prematurely marked consumed")
        _require(execution.get("execution_status") == "IN_PROGRESS", "execution status drift")
        _require(authority.get("per_security_history_execution_authorized") is True, "per-security execution authority record lost")
        _require(data.get("completion") in (None, {}), "completion record prematurely present")
        _require(data.get("interruption") in (None, {}), "interruption record prematurely present")
        _require(data.get("resume_authorization") in (None, {}), "resume authorization prematurely present")
        _require(data.get("resume_execution") in (None, {}), "resume execution prematurely present")
        return {
            "valid": True, "task_count": TASK_COUNT, "authorized": True,
            "completed": False, "interrupted": False, "resuming": False,
            "authority_consumed": False, "one_shot": True,
            "later_stage_auto_authorization": False,
        }

    _require(user.get("authorized") is False, "consumed authority still active")
    _require(user.get("consumed") is True, "consumed authority not marked consumed")

    if status == INTERRUPTED_CONSUMED:
        _require(authority.get("per_security_history_execution_authorized") is False, "consumed per-security execution authority still active")
        _require(execution.get("execution_status") == "INTERRUPTED", "interrupted execution status drift")
        _require(data.get("completion") in (None, {}), "interrupted run cannot have completion record")
        _require(data.get("resume_authorization") in (None, {}), "resume authorization prematurely present")
        _require(data.get("resume_execution") in (None, {}), "resume execution prematurely present")
        intr = data.get("interruption") or {}
        _validate_interruption(intr)
        _require(intr.get("resume_authorized") is False, "resume illegally authorized")
        return {
            "valid": True, "task_count": TASK_COUNT, "authorized": False,
            "completed": False, "interrupted": True, "resuming": False,
            "authority_consumed": True, "one_shot": True,
            "later_stage_auto_authorization": False,
        }

    intr = data.get("interruption") or {}
    _validate_interruption(intr)
    _require(execution.get("execution_status") == "INTERRUPTED", "original interrupted execution status drift")

    if status == RESUME_IN_PROGRESS:
        _require(authority.get("per_security_history_execution_authorized") is True, "resume per-security execution authority record lost")
        _require(intr.get("resume_authorized") is True, "resume authorization state not admitted")
        _validate_resume_binding(data, complete=False)
        _require(data.get("completion") in (None, {}), "resume run cannot have completion record")
        return {
            "valid": True, "task_count": TASK_COUNT, "authorized": True,
            "completed": False, "interrupted": True, "resuming": True,
            "authority_consumed": False, "one_shot": True,
            "later_stage_auto_authorization": False,
        }

    _require(authority.get("per_security_history_execution_authorized") is False, "completed per-security execution authority still active")
    completion = data.get("completion") or {}

    if data.get("resume_execution"):
        _require(intr.get("resume_authorized") is True, "completed resume was never authorized")
        _validate_resume_binding(data, complete=True)
        _require(int(completion.get("resumed_task_count", -1)) == CHECKPOINT_COUNT, "completion resumed task count drift")
        _require(int(completion.get("network_request_attempt_count", -1)) == REMAINING_COUNT, "completion network request count drift")
        _require(completion.get("interruption_evidence_id") == INTERRUPTION_EVIDENCE_ID, "completion interruption evidence drift")
    else:
        _require(execution.get("execution_status") == "COMPLETE", "completed execution status drift")

    _require(completion.get("evidence_id") == COMPLETION_EVIDENCE_ID, "completion evidence binding drift")
    _require(int(completion.get("completed_task_count", -1)) == TASK_COUNT, "completion task count drift")
    _require(int(completion.get("failed_task_count", -1)) == 0, "completion has failed tasks")
    _require(completion.get("phase_status") == "COMPLETE", "completion phase status drift")
    _require(completion.get("phase_complete") is True, "completion phase_complete lost")
    _require(completion.get("task_set_fingerprint_sha256") == TASK_SHA, "completion task-set fingerprint drift")
    for key in (
        "bulk_execution_consent_disabled_again",
        "per_security_consent_disabled_again",
        "start_command_restored_to_preflight_only",
        "preflight_network_request_attempted_false",
    ):
        _require(completion.get(key) is True, f"completion {key} guard lost")
    if data.get("resume_execution"):
        _require(completion.get("resume_consent_disabled_again") is True, "completion resume consent guard lost")
    for key in (
        "status_economics_authorized",
        "expected_scope_network_execution_authorized",
        "feature_performance_testing_authorized",
        "sealed_holdout_authorized",
        "genuine_live_authorized",
        "live_trading_authorized",
    ):
        _require(completion.get(key) is False, f"completion {key} illegally true")

    return {
        "valid": True, "task_count": TASK_COUNT, "authorized": False,
        "completed": True, "interrupted": bool(data.get("resume_execution")),
        "resuming": False, "authority_consumed": True, "one_shot": True,
        "later_stage_auto_authorization": False,
    }


def validate_file(path: Path = PATH) -> dict[str, Any]:
    return validate_contract(json.loads(path.read_text(encoding="utf-8")))


if __name__ == "__main__":
    print(json.dumps(validate_file(), ensure_ascii=False, indent=2))
