"""Fail-closed validator for STATUS_ECONOMICS consent lifecycle."""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Mapping

PATH = Path("INDEXALERT_KRX_STATUS_ECONOMICS_CONSENT_CONTRACT.json")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")

SHELL = "FROZEN_SHELL_PREPARATION_NOT_COMPLETE_EXECUTION_NOT_AUTHORIZED"
PREPARED = "PREPARED_SCOPE_FROZEN_EXECUTION_NOT_AUTHORIZED"
IN_PROGRESS = "USER_AUTHORIZED_EXECUTION_IN_PROGRESS"
COMPLETE_CONSUMED = "EXECUTION_COMPLETE_AUTHORITY_CONSUMED"


class KRXStatusEconomicsConsentError(ValueError):
    pass


def _require(cond: bool, msg: str) -> None:
    if not cond:
        raise KRXStatusEconomicsConsentError(msg)


def _sha(value: Any, field: str) -> str:
    text = str(value or "").strip().lower()
    _require(bool(SHA256_RE.fullmatch(text)), f"{field} must be SHA-256")
    return text


def validate_contract(data: Mapping[str, Any]) -> dict[str, Any]:
    _require(isinstance(data, Mapping), "contract must be an object")
    _require(data.get("schema_version") == "1", "schema_version drift")
    _require(
        data.get("contract_id") == "INDEXALERT-KRX-STATUS-ECONOMICS-CONSENT-v1",
        "contract_id drift",
    )
    _require(data.get("stage") == "STATUS_ECONOMICS", "stage drift")
    status = str(data.get("status") or "")
    _require(
        status in {SHELL, PREPARED, IN_PROGRESS, COMPLETE_CONSUMED},
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

    prep = data.get("preparation_gate") or {}
    _require(
        prep.get("command")
        == "python research_v1_krx_historical_worker_entrypoint.py --prepare-status-economics",
        "prepare command drift",
    )
    _require(prep.get("network_request_attempted_required") is False, "prepare network guard lost")
    _require(
        prep.get("private_task_manifest_relpath")
        == "task_manifests/status-economics-v3.json",
        "manifest relpath drift",
    )
    _require(
        prep.get("exact_status_economics_ready_required") is False,
        "exact economics readiness guard lost",
    )
    _require(prep.get("raw_rows_publicly_emitted_required") is False, "raw-row public boundary drift")
    _require(
        prep.get("security_identifiers_publicly_emitted_required") is False,
        "identifier public boundary drift",
    )
    _require(prep.get("source_gate_c_closed_required") is False, "source gate C illegally closed")
    _require(prep.get("source_gate_d_closed_required") is False, "source gate D illegally closed")
    _require(prep.get("source_gate_e_closed_required") is False, "source gate E illegally closed")

    if status == SHELL:
        _require(pre.get("current_observed_complete") is False, "predecessor completion prematurely asserted")
        _require(prep.get("prepared_task_count") is None, "prepared task count prematurely frozen")
        _require(prep.get("prepared_task_set_fingerprint_sha256") is None, "prepared fingerprint prematurely frozen")
        _require(
            prep.get("prepared_private_manifest_metadata_sha256") is None,
            "prepared manifest hash prematurely frozen",
        )
        _require(prep.get("preparation_complete") is False, "preparation prematurely complete")
        _require(prep.get("execution_scope_frozen") is False, "execution scope prematurely frozen")
        _require(data.get("preparation_evidence_id") in (None, ""), "preparation evidence prematurely bound")
        prepared_count = None
        prepared_task_sha = None
        prepared_manifest_sha = None
        preparation_complete = False
        execution_scope_frozen = False
    else:
        _require(pre.get("current_observed_complete") is True, "prepared predecessor completion not asserted")
        _require(
            pre.get("completion_evidence_id")
            == "INDEXALERT-KRX-PER-SECURITY-HISTORY-EXEC-2026-10-03-v1",
            "prepared predecessor completion evidence drift",
        )
        task_count = int(prep.get("prepared_task_count", -1))
        _require(task_count > 0, "prepared task count must be positive")
        prepared_task_sha = _sha(
            prep.get("prepared_task_set_fingerprint_sha256"),
            "prepared_task_set_fingerprint_sha256",
        )
        prepared_manifest_sha = _sha(
            prep.get("prepared_private_manifest_metadata_sha256"),
            "prepared_private_manifest_metadata_sha256",
        )
        _require(prep.get("preparation_complete") is True, "prepared state missing completion")
        _require(prep.get("execution_scope_frozen") is True, "prepared execution scope not frozen")
        _require(
            prep.get("network_request_attempted") is False,
            "prepared status-economics preparation attempted network",
        )
        _require(prep.get("raw_rows_emitted") is False, "prepared raw rows emitted")
        _require(
            prep.get("security_identifiers_emitted") is False,
            "prepared security identifiers emitted",
        )
        _require(
            prep.get("exact_status_economics_ready") is False,
            "prepared exact status economics illegally ready",
        )
        _require(
            data.get("preparation_evidence_id")
            == "INDEXALERT-KRX-STATUS-ECONOMICS-PREP-v1",
            "preparation evidence binding drift",
        )
        prepared_count = task_count
        preparation_complete = True
        execution_scope_frozen = True

    user = data.get("user_authorization") or {}
    _require(
        user.get("exact_user_approval_phrase")
        == "I_AUTHORIZE_INDEXALERT_KRX_STATUS_ECONOMICS_v1",
        "approval phrase drift",
    )
    _require(user.get("one_shot") is True, "one-shot guard lost")
    _require(user.get("prior_stage_authorization_reusable") is False, "prior-stage approval reuse enabled")
    _require(user.get("reusable") is False, "approval reuse enabled")

    gate = data.get("runtime_gate") or {}
    _require(gate.get("both_consents_required") is True, "dual-consent guard lost")
    _require(gate.get("exact_prepared_scope_required") is True, "exact prepared scope guard lost")
    _require(gate.get("stage_consent_env") == "KRX_STATUS_ECONOMICS_CONSENT", "stage consent env drift")
    _require(
        gate.get("stage_consent_sentinel") == "I_AUTHORIZE_INDEXALERT_KRX_STATUS_ECONOMICS_v1",
        "stage sentinel drift",
    )
    _require(
        gate.get("entrypoint")
        == "python research_v1_krx_historical_worker_entrypoint.py --execute-status-economics",
        "entrypoint drift",
    )

    authority = data.get("authority") or {}
    for key in (
        "expected_scope_network_execution_authorized",
        "exact_status_economics_claim_allowed",
        "feature_performance_testing_authorized",
        "sealed_holdout_authorized",
        "shadow_s1_authorized",
        "genuine_live_authorized",
        "live_trading_authorized",
    ):
        _require(authority.get(key) is False, f"{key} illegally true")

    if status in {SHELL, PREPARED}:
        _require(user.get("authorized") is False, "stage cannot be pre-authorized")
        _require(user.get("consumed") is not True, "unexecuted authority marked consumed")
        _require(
            authority.get("status_economics_execution_authorized") is False,
            "status-economics stage cannot be pre-authorized",
        )
        _require(data.get("execution") in (None, {}), "execution record prematurely present")
        _require(data.get("completion") in (None, {}), "completion record prematurely present")
        authorized = False
        completed = False
        authority_consumed = False
    else:
        _require(bool(str(user.get("received_date_kst") or "").strip()), "authorization date required")
        deployment_id = str(user.get("consumed_for_deployment_id") or "").strip()
        source_revision = str(user.get("source_revision") or "").strip()
        _require(bool(deployment_id), "authorized deployment required")
        _require(bool(source_revision), "authorized source revision required")

        execution = data.get("execution") or {}
        _require(execution.get("deployment_id") == deployment_id, "execution deployment drift")
        _require(execution.get("source_revision") == source_revision, "execution source revision drift")
        _require(execution.get("mode") == "EXECUTE_STATUS_ECONOMICS", "execution mode drift")
        _require(int(execution.get("task_count", -1)) == prepared_count, "execution task count drift")
        _require(
            _sha(
                execution.get("task_set_fingerprint_sha256"),
                "execution task_set_fingerprint_sha256",
            )
            == prepared_task_sha,
            "execution task-set fingerprint drift",
        )
        _require(
            _sha(
                execution.get("private_manifest_metadata_sha256"),
                "execution private_manifest_metadata_sha256",
            )
            == prepared_manifest_sha,
            "execution manifest hash drift",
        )

        if status == IN_PROGRESS:
            _require(user.get("authorized") is True, "authorized execution record lost")
            _require(user.get("consumed") is not True, "active authority prematurely consumed")
            _require(
                authority.get("status_economics_execution_authorized") is True,
                "status-economics execution authority record lost",
            )
            _require(execution.get("execution_status") == "IN_PROGRESS", "execution status drift")
            _require(data.get("completion") in (None, {}), "completion record prematurely present")
            authorized = True
            completed = False
            authority_consumed = False
        else:
            _require(user.get("authorized") is False, "completed authority still active")
            _require(user.get("consumed") is True, "completed authority not marked consumed")
            _require(
                authority.get("status_economics_execution_authorized") is False,
                "completed status-economics authority still active",
            )
            _require(execution.get("execution_status") == "COMPLETE", "completed execution status drift")

            completion = data.get("completion") or {}
            _require(
                completion.get("evidence_id") == "INDEXALERT-KRX-STATUS-ECONOMICS-EXEC-v1",
                "completion evidence binding drift",
            )
            _require(
                int(completion.get("completed_task_count", -1)) == prepared_count,
                "completion task count drift",
            )
            _require(int(completion.get("failed_task_count", -1)) == 0, "completion has failed tasks")
            _require(completion.get("phase_status") == "COMPLETE", "completion phase status drift")
            _require(completion.get("phase_complete") is True, "completion phase_complete lost")
            _require(
                _sha(
                    completion.get("task_set_fingerprint_sha256"),
                    "completion task_set_fingerprint_sha256",
                )
                == prepared_task_sha,
                "completion task-set fingerprint drift",
            )
            _sha(
                completion.get("private_batch_metadata_sha256"),
                "completion private_batch_metadata_sha256",
            )
            for key in (
                "bulk_execution_consent_disabled_again",
                "status_economics_consent_disabled_again",
                "start_command_restored_to_preflight_only",
                "preflight_network_request_attempted_false",
            ):
                _require(completion.get(key) is True, f"completion {key} guard lost")
            for key in (
                "exact_status_economics_ready",
                "realized_fill_economics_proven",
                "realized_recovery_cashflows_proven",
                "source_gate_c_closed",
                "source_gate_d_closed",
                "source_gate_e_closed",
                "expected_scope_network_execution_authorized",
                "feature_performance_testing_authorized",
                "sealed_holdout_authorized",
                "shadow_s1_authorized",
                "genuine_live_authorized",
                "live_trading_authorized",
            ):
                _require(completion.get(key) is False, f"completion {key} illegally true")
            authorized = False
            completed = True
            authority_consumed = True

    return {
        "valid": True,
        "status": status,
        "prepared_task_count": prepared_count,
        "preparation_complete": preparation_complete,
        "execution_scope_frozen": execution_scope_frozen,
        "authorized": authorized,
        "completed": completed,
        "authority_consumed": authority_consumed,
        "prior_stage_authorization_reusable": False,
        "sealed_holdout_authorized": False,
        "live_trading_authorized": False,
    }


def validate_file(path: Path = PATH) -> dict[str, Any]:
    return validate_contract(json.loads(path.read_text(encoding="utf-8")))


if __name__ == "__main__":
    print(json.dumps(validate_file(), ensure_ascii=False, indent=2))
