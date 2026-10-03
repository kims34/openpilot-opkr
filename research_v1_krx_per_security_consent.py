"""Fail-closed validator for KRX per-security one-shot consent contract."""
from __future__ import annotations
import json, re
from pathlib import Path
from typing import Any, Mapping

PATH = Path("INDEXALERT_KRX_PER_SECURITY_HISTORY_CONSENT_CONTRACT.json")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
IN_PROGRESS = "USER_AUTHORIZED_EXECUTION_IN_PROGRESS"
INTERRUPTED_CONSUMED = "EXECUTION_INTERRUPTED_AUTHORITY_CONSUMED"
COMPLETE_CONSUMED = "EXECUTION_COMPLETE_AUTHORITY_CONSUMED"

class KRXPerSecurityConsentError(ValueError):
    pass

def _require(cond: bool, msg: str) -> None:
    if not cond:
        raise KRXPerSecurityConsentError(msg)

def validate_contract(data: Mapping[str, Any]) -> dict[str, Any]:
    _require(isinstance(data, Mapping), "contract must be an object")
    _require(data.get("schema_version") == "1", "schema_version drift")
    _require(data.get("contract_id") == "INDEXALERT-KRX-PER-SECURITY-HISTORY-CONSENT-v1", "contract_id drift")
    _require(data.get("stage") == "PER_SECURITY_HISTORY", "stage drift")
    status = str(data.get("status") or "")
    _require(status in {IN_PROGRESS, INTERRUPTED_CONSUMED, COMPLETE_CONSUMED}, "status drift")

    pre = data.get("prerequisite") or {}
    _require(pre.get("identity_binding_phase_complete") is True, "identity binding prerequisite lost")
    _require(int(pre.get("identity_binding_completed_task_count", -1)) == 145, "identity binding count drift")

    prepared = data.get("prepared_task_set") or {}
    _require(int(prepared.get("task_count", -1)) == 14296, "prepared task count drift")
    _require(prepared.get("task_count_by_kind") == {
        "investor_trading_individual_daily": 9485,
        "trading_halt": 4811,
    }, "prepared task-kind counts drift")
    for field in ("task_set_fingerprint_sha256", "private_task_manifest_metadata_sha256"):
        _require(bool(SHA256_RE.fullmatch(str(prepared.get(field) or ""))), f"{field} must be SHA-256")
    _require(prepared.get("task_set_fingerprint_sha256") == "fb5b883c6fe0e9c15e88aea9bdf874ddd7a11ae8a009c2ddf91c4e4249a8ba38", "prepared task-set fingerprint drift")
    _require(prepared.get("private_task_manifest_metadata_sha256") == "0d98f45168cedeecc013e95c71abe661ca1fac9df0403ba477d2f5653572c116", "prepared private manifest hash drift")
    _require(prepared.get("network_request_attempted_during_prepare") is False, "prepare network guard lost")

    user = data.get("user_authorization") or {}
    _require(user.get("exact_user_approval_phrase") == "I_AUTHORIZE_INDEXALERT_KRX_PER_SECURITY_HISTORY_v1", "approval phrase drift")
    _require(user.get("received_date_kst") == "2026-10-03", "authorization date drift")
    _require(user.get("consumed_for_deployment_id") == "bc79d1b5-5fb8-46c7-8067-682e61947014", "authorized deployment drift")
    _require(user.get("source_revision") == "9009c48a00394063c813d29219507ee2190ce09e", "authorized source revision drift")
    _require(user.get("one_shot") is True, "one-shot guard lost")
    _require(user.get("earlier_stage_authorization_reusable") is False, "earlier approval reuse illegally enabled")
    _require(user.get("reusable") is False, "approval reuse illegally enabled")

    gate = data.get("runtime_gate") or {}
    _require(gate.get("both_consents_required") is True, "dual consent guard lost")
    _require(gate.get("bulk_consent_env") == "KRX_HISTORICAL_ACQUISITION_CONSENT", "bulk consent env drift")
    _require(gate.get("stage_consent_env") == "KRX_PER_SECURITY_HISTORY_CONSENT", "stage consent env drift")
    _require(gate.get("stage_consent_sentinel") == "I_AUTHORIZE_INDEXALERT_KRX_PER_SECURITY_HISTORY_v1", "stage sentinel drift")
    _require(gate.get("entrypoint") == "python research_v1_krx_historical_worker_entrypoint.py --execute-per-security-history", "entrypoint drift")

    execution = data.get("execution") or {}
    _require(execution.get("deployment_id") == "bc79d1b5-5fb8-46c7-8067-682e61947014", "execution deployment drift")
    _require(execution.get("source_revision") == "9009c48a00394063c813d29219507ee2190ce09e", "execution source revision drift")
    _require(execution.get("start_command") == "python research_v1_krx_historical_worker_entrypoint.py --execute-per-security-history", "execution start command drift")
    _require(int(execution.get("task_count", -1)) == 14296, "execution task count drift")
    _require(execution.get("task_set_fingerprint_sha256") == "fb5b883c6fe0e9c15e88aea9bdf874ddd7a11ae8a009c2ddf91c4e4249a8ba38", "execution task-set fingerprint drift")
    for key in ("later_stage_auto_authorization","status_economics_authorized","expected_scope_network_execution_authorized","feature_performance_testing_authorized","sealed_holdout_authorized","genuine_live_authorized","live_trading_authorized"):
        _require(execution.get(key) is False, f"execution {key} illegally true")

    lock = data.get("post_run_lock") or {}
    for key in ("disable_bulk_consent_again","disable_stage_consent_again","restore_preflight_only_start_command"):
        _require(lock.get(key) is True, f"{key} guard lost")
    _require(lock.get("raw_rows_publicly_emitted") is False, "raw-row public leak allowed")
    _require(lock.get("later_stage_auto_authorization") is False, "later-stage auto authority enabled")

    authority = data.get("authority") or {}
    for key in ("status_economics_execution_authorized","expected_scope_network_execution_authorized","feature_performance_testing_authorized","sealed_holdout_authorized","shadow_s1_authorized","genuine_live_authorized","live_trading_authorized"):
        _require(authority.get(key) is False, f"{key} illegally true")

    if status == IN_PROGRESS:
        _require(user.get("authorized") is True, "authorized execution record lost")
        _require(user.get("consumed") is not True, "active authority prematurely marked consumed")
        _require(execution.get("execution_status") == "IN_PROGRESS", "execution status drift")
        _require(authority.get("per_security_history_execution_authorized") is True, "per-security execution authority record lost")
        _require(data.get("completion") in (None, {}), "completion record prematurely present")
        _require(data.get("interruption") in (None, {}), "interruption record prematurely present")
        return {"valid":True,"task_count":14296,"authorized":True,"completed":False,"interrupted":False,"authority_consumed":False,"one_shot":True,"later_stage_auto_authorization":False}

    _require(user.get("authorized") is False, "consumed authority still active")
    _require(user.get("consumed") is True, "consumed authority not marked consumed")
    _require(authority.get("per_security_history_execution_authorized") is False, "consumed per-security execution authority still active")

    if status == INTERRUPTED_CONSUMED:
        _require(execution.get("execution_status") == "INTERRUPTED", "interrupted execution status drift")
        _require(data.get("completion") in (None, {}), "interrupted run cannot have completion record")
        intr = data.get("interruption") or {}
        _require(intr.get("deployment_id") == "bc79d1b5-5fb8-46c7-8067-682e61947014", "interruption deployment drift")
        _require(intr.get("source_revision") == "9009c48a00394063c813d29219507ee2190ce09e", "interruption source revision drift")
        _require(intr.get("crashed_at_utc") == "2026-10-03T00:45:16Z", "interruption timestamp drift")
        _require(intr.get("error_class") == "KRXHistoricalRequestExecutorError", "interruption error class drift")
        _require(intr.get("reason_code") == "ALPHANUMERIC_SHORT_CODE_VALIDATOR_MISMATCH", "interruption reason drift")
        _require(intr.get("raw_security_identifier_emitted") is False, "interruption leaked identifier")
        _require(int(intr.get("checkpoint_count_observed", -1)) == 11750, "checkpoint count drift")
        _require(int(intr.get("remaining_task_count", -1)) == 2546, "remaining task count drift")
        _require(intr.get("checkpoint_preservation_verified") is True, "checkpoint preservation not verified")
        _require(intr.get("checkpoint_probe_deployment_id") == "92439b24-644a-4d3d-a888-9e0ba568bfac", "checkpoint probe deployment drift")
        _require(intr.get("checkpoint_probe_source_revision") == "d156f0dc6056924a798679bd9e93e1f2eb0241fc", "checkpoint probe source revision drift")
        _require(intr.get("checkpoint_probe_network_request_attempted") is False, "checkpoint probe attempted network")
        _require(int(intr.get("checkpoint_probe_failed_task_count", -1)) == 0, "checkpoint probe failure drift")
        _require(intr.get("checkpoint_probe_phase_complete") is False, "checkpoint probe illegally complete")
        _require(intr.get("interruption_evidence_id") == "INDEXALERT-KRX-PER-SECURITY-HISTORY-INTERRUPTION-2026-10-03-v1", "interruption evidence binding drift")
        for key in ("bulk_execution_consent_disabled_again","per_security_consent_disabled_again","start_command_restored_to_preflight_only","restart_policy_never"):
            _require(intr.get(key) is True, f"interruption {key} guard lost")
        _require(intr.get("resume_authorized") is False, "resume illegally authorized")
        _require(intr.get("resume_requires_new_user_authorization") is True, "new resume authorization guard lost")
        for key in ("later_stage_auto_authorization","status_economics_authorized","expected_scope_network_execution_authorized","feature_performance_testing_authorized","sealed_holdout_authorized","genuine_live_authorized","live_trading_authorized"):
            _require(intr.get(key) is False, f"interruption {key} illegally true")
        return {"valid":True,"task_count":14296,"authorized":False,"completed":False,"interrupted":True,"authority_consumed":True,"one_shot":True,"later_stage_auto_authorization":False}

    _require(execution.get("execution_status") == "COMPLETE", "completed execution status drift")
    completion = data.get("completion") or {}
    _require(completion.get("evidence_id") == "INDEXALERT-KRX-PER-SECURITY-HISTORY-EXEC-2026-10-03-v1", "completion evidence binding drift")
    _require(int(completion.get("completed_task_count", -1)) == 14296, "completion task count drift")
    _require(int(completion.get("failed_task_count", -1)) == 0, "completion has failed tasks")
    _require(completion.get("phase_status") == "COMPLETE", "completion phase status drift")
    _require(completion.get("phase_complete") is True, "completion phase_complete lost")
    _require(completion.get("task_set_fingerprint_sha256") == "fb5b883c6fe0e9c15e88aea9bdf874ddd7a11ae8a009c2ddf91c4e4249a8ba38", "completion task-set fingerprint drift")
    for key in ("bulk_execution_consent_disabled_again","per_security_consent_disabled_again","start_command_restored_to_preflight_only","preflight_network_request_attempted_false"):
        _require(completion.get(key) is True, f"completion {key} guard lost")
    for key in ("status_economics_authorized","expected_scope_network_execution_authorized","feature_performance_testing_authorized","sealed_holdout_authorized","genuine_live_authorized","live_trading_authorized"):
        _require(completion.get(key) is False, f"completion {key} illegally true")
    return {"valid":True,"task_count":14296,"authorized":False,"completed":True,"interrupted":False,"authority_consumed":True,"one_shot":True,"later_stage_auto_authorization":False}

def validate_file(path: Path = PATH) -> dict[str, Any]:
    return validate_contract(json.loads(path.read_text(encoding="utf-8")))

if __name__ == "__main__":
    print(json.dumps(validate_file(), ensure_ascii=False, indent=2))
