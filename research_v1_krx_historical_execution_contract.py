"""Fail-closed validator for the KRX historical execution contract."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping


PATH = Path("INDEXALERT_KRX_HISTORICAL_EXECUTION_CONTRACT.json")


class KRXHistoricalExecutionContractError(ValueError):
    pass


def _require(cond: bool, msg: str) -> None:
    if not cond:
        raise KRXHistoricalExecutionContractError(msg)


def validate_execution_contract(data: Mapping[str, Any]) -> dict[str, Any]:
    _require(isinstance(data, Mapping), "execution contract must be an object")
    _require(data.get("schema_version") == "3", "schema_version drift")
    _require(data.get("contract_id") == "INDEXALERT-KRX-HIST-EXEC-v3", "contract_id drift")
    _require(data.get("acquisition_plan_id") == "INDEXALERT-KRX-HIST-ACQ-v3", "plan binding drift")
    _require(data.get("supersedes_contract_id") == "INDEXALERT-KRX-HIST-EXEC-v2", "superseded contract drift")
    _require(data.get("superseded_before_any_bulk_network_execution") is True, "execution-contract supersession timing drift")
    _require(data.get("execution_authorized") is False, "contract must not self-authorize execution")

    repo = data.get("repository_context") or {}
    _require(repo.get("repository") == "kims34/openpilot-opkr", "repository binding drift")
    _require(repo.get("repository_public") is True, "public-repository boundary drift")
    _require(repo.get("raw_data_in_repository_forbidden") is True, "raw-in-repo prohibition lost")

    iso = data.get("execution_isolation") or {}
    _require(iso.get("dedicated_one_shot_worker_required") is True, "dedicated-worker requirement lost")
    _require(iso.get("production_web_process_must_not_run_bulk_job") is True, "production-process guard lost")
    _require(iso.get("concurrent_public_web_serving_from_raw_root_forbidden") is True, "raw web-serving guard lost")
    _require(iso.get("network_execution_requires_exact_plan_preflight") is True, "preflight requirement lost")
    _require(
        iso.get("exact_consent_sentinel") == "I_AUTHORIZE_INDEXALERT_KRX_HIST_ACQ_v3",
        "bulk consent sentinel drift",
    )
    _require(
        iso.get("dedicated_worker_role_env") == "INDEXALERT_KRX_HIST_WORKER_ROLE",
        "dedicated worker role env drift",
    )
    _require(
        iso.get("dedicated_worker_role_value") == "DEDICATED_ONE_SHOT",
        "dedicated worker role value drift",
    )
    _require(
        iso.get("railway_service_name_env") == "RAILWAY_SERVICE_NAME",
        "Railway service-name env drift",
    )
    _require(
        set(iso.get("forbidden_public_service_names") or [])
        == {"indexalert-runtime", "indexalert-backend", "indexalert-push"},
        "forbidden public service names drift",
    )
    _require(
        iso.get("forbidden_public_service_bulk_execution") is True,
        "public-service bulk-execution prohibition lost",
    )

    stage = (data.get("stage_specific_authority") or {}).get(
        "identity_standard_code_binding"
    ) or {}
    _require(stage.get("network_free_prepare_required") is True, "binding preparation guard lost")
    _require(stage.get("private_task_manifest_required") is True, "binding manifest guard lost")
    _require(stage.get("bulk_consent_env") == "KRX_HISTORICAL_ACQUISITION_CONSENT", "binding bulk consent env drift")
    _require(stage.get("bulk_consent_sentinel") == "I_AUTHORIZE_INDEXALERT_KRX_HIST_ACQ_v3", "binding bulk sentinel drift")
    _require(stage.get("stage_consent_env") == "KRX_IDENTITY_BINDING_CONSENT", "binding stage consent env drift")
    _require(stage.get("stage_consent_sentinel") == "I_AUTHORIZE_INDEXALERT_KRX_IDENTITY_BINDING_v1", "binding stage sentinel drift")
    _require(stage.get("both_consents_required") is True, "binding dual-consent guard lost")
    _require(stage.get("currently_authorized") is False, "binding stage cannot be pre-authorized")
    _require(stage.get("prior_identity_seed_authorization_reusable") is False, "seed authority reuse illegally allowed")
    _require(stage.get("later_stage_auto_authorization") is False, "binding later-stage auto authority illegally enabled")

    stage_auth = data.get("stage_specific_authority") or {}

    per_security = stage_auth.get("per_security_history") or {}
    _require(per_security.get("predecessor_phase") == "IDENTITY_STANDARD_CODE_BINDING", "per-security predecessor drift")
    _require(per_security.get("network_free_prepare_required") is True, "per-security preparation guard lost")
    _require(per_security.get("private_task_manifest_required") is True, "per-security manifest guard lost")
    _require(per_security.get("stage_consent_env") == "KRX_PER_SECURITY_HISTORY_CONSENT", "per-security stage consent env drift")
    _require(per_security.get("stage_consent_sentinel") == "I_AUTHORIZE_INDEXALERT_KRX_PER_SECURITY_HISTORY_v1", "per-security stage sentinel drift")
    _require(per_security.get("both_consents_required") is True, "per-security dual-consent guard lost")
    _require(per_security.get("currently_authorized") is False, "per-security stage cannot be pre-authorized")
    _require(per_security.get("prior_stage_authorization_reusable") is False, "per-security prior-stage reuse illegally allowed")
    _require(per_security.get("later_stage_auto_authorization") is False, "per-security later-stage auto authority illegally enabled")
    _require(
        per_security.get("preparation_evidence_id")
        == "INDEXALERT-KRX-PER-SECURITY-HISTORY-PREP-2026-10-03-v1",
        "per-security preparation evidence binding drift",
    )
    _require(int(per_security.get("prepared_task_count", -1)) == 14296, "per-security prepared task count drift")
    _require(
        per_security.get("prepared_task_count_by_kind")
        == {
            "investor_trading_individual_daily": 9485,
            "trading_halt": 4811,
        },
        "per-security prepared task-kind counts drift",
    )
    _require(
        per_security.get("prepared_task_set_fingerprint_sha256")
        == "fb5b883c6fe0e9c15e88aea9bdf874ddd7a11ae8a009c2ddf91c4e4249a8ba38",
        "per-security prepared task-set drift",
    )
    _require(
        per_security.get("prepared_private_task_manifest_metadata_sha256")
        == "0d98f45168cedeecc013e95c71abe661ca1fac9df0403ba477d2f5653572c116",
        "per-security prepared manifest hash drift",
    )
    _require(
        per_security.get("prepared_private_task_manifest_relpath")
        == "task_manifests/per-security-history-v3.json",
        "per-security prepared manifest relpath drift",
    )
    _require(
        per_security.get("network_request_attempted_during_prepare") is False,
        "per-security preparation illegally attempted network",
    )
    _require(per_security.get("exact_prepared_scope_required") is True, "per-security exact prepared scope guard lost")

    status_economics = stage_auth.get("status_economics") or {}
    _require(status_economics.get("predecessor_phase") == "PER_SECURITY_HISTORY", "status-economics predecessor drift")
    _require(status_economics.get("network_free_prepare_required") is True, "status-economics preparation guard lost")
    _require(status_economics.get("private_task_manifest_required") is True, "status-economics manifest guard lost")
    _require(status_economics.get("stage_consent_env") == "KRX_STATUS_ECONOMICS_CONSENT", "status-economics stage consent env drift")
    _require(status_economics.get("stage_consent_sentinel") == "I_AUTHORIZE_INDEXALERT_KRX_STATUS_ECONOMICS_v1", "status-economics stage sentinel drift")
    _require(status_economics.get("both_consents_required") is True, "status-economics dual-consent guard lost")
    _require(status_economics.get("currently_authorized") is False, "status-economics stage cannot be pre-authorized")
    _require(status_economics.get("prior_stage_authorization_reusable") is False, "status-economics prior-stage reuse illegally allowed")
    _require(status_economics.get("exact_status_economics_claim_allowed") is False, "exact status economics claim illegally allowed")
    _require(status_economics.get("later_stage_auto_authorization") is False, "status-economics later-stage auto authority illegally enabled")

    storage = data.get("private_storage") or {}
    for key in (
        "persistent_private_volume_required",
        "raw_root_must_be_absolute",
        "raw_root_inside_git_worktree_forbidden",
        "raw_root_under_public_static_directory_forbidden",
        "content_addressed_objects",
        "overwrite_existing_raw_object_forbidden",
        "atomic_write_required",
        "fsync_before_rename_required",
        "raw_artifact_upload_to_github_forbidden",
        "raw_rows_in_actions_logs_forbidden",
    ):
        _require(storage.get(key) is True, f"{key} guard lost")
    _require(storage.get("raw_root_env") == "KRX_PRIVATE_RAW_DIR", "raw-root env drift")
    _require(storage.get("directory_mode_octal") == "0700", "directory mode drift")
    _require(storage.get("file_mode_octal") == "0600", "file mode drift")
    _require(storage.get("recommended_mount_root") == "/data/indexalert/krx-historical-v3", "recommended mount root drift")
    _require(
        storage.get("object_relpath_template")
        == "objects/sha256/{first2}/{sha256}.bin",
        "object path template drift",
    )

    correction = data.get("source_contract_correction") or {}
    _require(
        correction.get("historical_cleanup_source")
        == "MDCSTAT23801 delisted-history cleanup-period fields",
        "historical cleanup source correction drift",
    )
    _require(
        correction.get("current_cleanup_reconciliation_source")
        == "MDCSTAT23701 mktId=ALL snapshot",
        "current cleanup reconciliation source drift",
    )
    _require(
        correction.get("mdcstat237_historical_date_window_assumption_forbidden") is True,
        "MDCSTAT237 historical-window prohibition lost",
    )

    capture = data.get("source_capture") or {}
    for key in (
        "raw_response_bytes_required",
        "raw_bytes_sha256_required",
        "raw_bytes_size_required",
        "parsed_dataframe_payload_sha256_required",
        "parsed_schema_sha256_required",
        "request_metadata_sha256_required",
        "retrieved_at_timezone_aware_required",
        "transport_status_required",
        "acquisition_receipt_required",
        "raw_object_manifest_required",
        "raw_object_manifest_must_not_contain_credentials",
    ):
        _require(capture.get(key) is True, f"{key} guard lost")

    resume = data.get("checkpoint_and_resume") or {}
    for key in (
        "checkpoint_after_every_request",
        "completed_request_requires_raw_object_and_receipt",
        "resume_only_from_verified_raw_object_and_receipt",
        "retry_never_overwrites_prior_object",
        "same_request_different_payload_must_create_new_object_and_fail_reconciliation",
        "auth_failure_abort_batch",
        "schema_drift_abort_batch",
        "identity_mapping_failure_abort_before_per_security_requests",
    ):
        _require(resume.get(key) is True, f"{key} guard lost")

    forbidden = set(data.get("forbidden_public_output") or [])
    for key in (
        "raw_rows",
        "raw_response_bytes",
        "security_level_numeric_values_from_raw_responses",
        "KRX_ID",
        "KRX_PW",
        "KRX_AUTH_KEY",
        "cookies",
        "session_tokens",
        "authorization_headers",
    ):
        _require(key in forbidden, f"forbidden public output missing: {key}")

    authority = data.get("authority") or {}
    _require(authority.get("rights_to_acquire") is True, "rights-to-acquire lost")
    for key in (
        "bulk_network_execution_authorized_by_user",
        "source_gate_c_closed",
        "source_gate_d_closed",
        "source_gate_e_closed",
        "feature_performance_testing_authorized",
        "sealed_holdout_authorized",
        "live_trading_authorized",
    ):
        _require(authority.get(key) is False, f"{key} illegally true")

    return {
        "valid": True,
        "contract_id": "INDEXALERT-KRX-HIST-EXEC-v3",
        "plan_id": "INDEXALERT-KRX-HIST-ACQ-v3",
        "rights_to_acquire": True,
        "bulk_network_execution_authorized_by_user": False,
        "private_persistent_storage_required": True,
        "raw_publication_forbidden": True,
        "gate_c_closed": False,
        "gate_d_closed": False,
        "gate_e_closed": False,
        "feature_performance_testing_authorized": False,
        "sealed_holdout_authorized": False,
        "live_trading_authorized": False,
    }


def validate_file(path: Path = PATH) -> dict[str, Any]:
    return validate_execution_contract(json.loads(path.read_text(encoding="utf-8")))


if __name__ == "__main__":
    print(json.dumps(validate_file(), ensure_ascii=False, indent=2))
