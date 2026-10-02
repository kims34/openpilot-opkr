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
    _require(data.get("schema_version") == "2", "schema_version drift")
    _require(data.get("contract_id") == "INDEXALERT-KRX-HIST-EXEC-v2", "contract_id drift")
    _require(data.get("acquisition_plan_id") == "INDEXALERT-KRX-HIST-ACQ-v3", "plan binding drift")
    _require(data.get("supersedes_contract_id") == "INDEXALERT-KRX-HIST-EXEC-v1", "superseded contract drift")
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
        "contract_id": "INDEXALERT-KRX-HIST-EXEC-v2",
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
