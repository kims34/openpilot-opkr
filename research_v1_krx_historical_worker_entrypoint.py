"""Dedicated one-shot entrypoint for staged KRX historical acquisition.

Default behavior is network-free preflight only.

Actual network execution is limited to explicitly implemented frozen stages
(identity seed, identity binding, prepared per-security history and prepared
status-economics price context) and requires the exact frozen authority for the
requested stage. In particular, identity binding requires BOTH:
- the exact v3 bulk-acquisition consent sentinel; and
- a separate exact identity-binding stage consent sentinel.
The completed IDENTITY_SEED authorization cannot be reused for binding.
- dedicated worker role
- non-public Railway service identity
- safe private persistent raw directory
- KRX_ID / KRX_PW / KRX_AUTH_KEY

Each phase is predecessor-gated. STATUS_ECONOMICS can execute only after the
prepared PER_SECURITY_HISTORY phase has completed and an immutable private
status-economics manifest has been frozen.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
from typing import Any, Mapping

from research_v1_krx_historical_acquisition_preflight import (
    evaluate_historical_acquisition_preflight,
)
from research_v1_krx_historical_batch_orchestrator import (
    PLAN_ID,
    EXECUTION_CONTRACT_ID,
    build_identity_seed_tasks,
    public_task_summary,
)
from research_v1_krx_historical_batch_state import (
    KRXHistoricalBatchStateError,
    initialize_phase_state,
    public_phase_summary,
    record_task_completion,
    require_phase_complete,
)
from research_v1_krx_historical_identity_materializer import (
    build_identity_binding_tasks_from_private_seed,
    build_per_security_history_tasks_from_private_identity,
    build_status_economics_tasks_from_private_identity,
    public_delisted_start_master_mapping_summary,
    public_identity_master_code_shape_summary,
    public_new_listing_master_mapping_summary,
)
from research_v1_krx_historical_request_executor import execute_request_spec
from research_v1_krx_private_store import (
    KRXPrivateStoreError,
    read_private_json,
    write_private_json,
)


CLIENT_REVISION = "krx-data-api@e6ebac9b71482db127348d8a08ebc6743aa3b50e"
PRIVATE_BATCH_REL = "batches/identity-seed-v3.json"
IDENTITY_BINDING_BATCH_REL = "batches/identity-standard-code-binding-v3.json"
IDENTITY_BINDING_TASK_MANIFEST_REL = "task_manifests/identity-standard-code-binding-v1.json"
IDENTITY_BINDING_EXPECTED_TASK_COUNT = 145
IDENTITY_BINDING_EXPECTED_TASK_SET_SHA256 = "b3e9c845d74b0b479af0fd95d9015de92697fbd82b7bf07f9765378dfafd11d9"
IDENTITY_BINDING_EXPECTED_MANIFEST_SHA256 = "940f446caec81dd1a4a7b3a01053ae3f6a6ef6c79654e23bf2b971dca3622a6c"
PER_SECURITY_TASK_MANIFEST_REL = "task_manifests/per-security-history-v3.json"
PER_SECURITY_BATCH_REL = "batches/per-security-history-v3.json"
PER_SECURITY_EXPECTED_TASK_COUNT = 14296
PER_SECURITY_EXPECTED_TASK_SET_SHA256 = "fb5b883c6fe0e9c15e88aea9bdf874ddd7a11ae8a009c2ddf91c4e4249a8ba38"
PER_SECURITY_EXPECTED_MANIFEST_SHA256 = "0d98f45168cedeecc013e95c71abe661ca1fac9df0403ba477d2f5653572c116"
STATUS_ECONOMICS_TASK_MANIFEST_REL = "task_manifests/status-economics-v3.json"
STATUS_ECONOMICS_BATCH_REL = "batches/status-economics-v3.json"
IDENTITY_BINDING_CONSENT_ENV = "KRX_IDENTITY_BINDING_CONSENT"
IDENTITY_BINDING_CONSENT_SENTINEL = "I_AUTHORIZE_INDEXALERT_KRX_IDENTITY_BINDING_v1"
PER_SECURITY_CONSENT_ENV = "KRX_PER_SECURITY_HISTORY_CONSENT"
PER_SECURITY_CONSENT_SENTINEL = "I_AUTHORIZE_INDEXALERT_KRX_PER_SECURITY_HISTORY_v1"
STATUS_ECONOMICS_CONSENT_ENV = "KRX_STATUS_ECONOMICS_CONSENT"
STATUS_ECONOMICS_CONSENT_SENTINEL = "I_AUTHORIZE_INDEXALERT_KRX_STATUS_ECONOMICS_v1"


class KRXHistoricalWorkerEntrypointError(RuntimeError):
    pass


def _require_frozen_identity_binding_summary(
    summary: Mapping[str, Any],
    *,
    manifest_metadata_sha256: str | None = None,
) -> None:
    if int(summary.get("task_count", -1)) != IDENTITY_BINDING_EXPECTED_TASK_COUNT:
        raise KRXHistoricalWorkerEntrypointError(
            "identity binding frozen task count drift"
        )
    if (
        str(summary.get("task_set_fingerprint_sha256") or "")
        != IDENTITY_BINDING_EXPECTED_TASK_SET_SHA256
    ):
        raise KRXHistoricalWorkerEntrypointError(
            "identity binding frozen task-set fingerprint drift"
        )
    if (
        manifest_metadata_sha256 is not None
        and str(manifest_metadata_sha256) != IDENTITY_BINDING_EXPECTED_MANIFEST_SHA256
    ):
        raise KRXHistoricalWorkerEntrypointError(
            "identity binding frozen manifest metadata SHA-256 drift"
        )


def _require_frozen_per_security_summary(
    summary: Mapping[str, Any],
    *,
    manifest_metadata_sha256: str | None = None,
) -> None:
    if int(summary.get("task_count", -1)) != PER_SECURITY_EXPECTED_TASK_COUNT:
        raise KRXHistoricalWorkerEntrypointError(
            "per-security frozen task count drift"
        )
    if (
        str(summary.get("task_set_fingerprint_sha256") or "")
        != PER_SECURITY_EXPECTED_TASK_SET_SHA256
    ):
        raise KRXHistoricalWorkerEntrypointError(
            "per-security frozen task-set fingerprint drift"
        )
    if (
        manifest_metadata_sha256 is not None
        and str(manifest_metadata_sha256) != PER_SECURITY_EXPECTED_MANIFEST_SHA256
    ):
        raise KRXHistoricalWorkerEntrypointError(
            "per-security frozen manifest metadata SHA-256 drift"
        )


def _require_completed_predecessor(
    *,
    root: str,
    phase: str,
    git_worktree: str,
) -> dict[str, Any]:
    try:
        return require_phase_complete(
            root=root,
            phase=phase,
            git_worktree=git_worktree,
        )
    except (KRXPrivateStoreError, KRXHistoricalBatchStateError) as exc:
        raise KRXHistoricalWorkerEntrypointError(
            f"prior phase {phase} is not complete"
        ) from exc


def _require_exact_stage_consent(
    environment: Mapping[str, str],
    *,
    env_name: str,
    sentinel: str,
    requirement_name: str,
) -> None:
    if str(environment.get(env_name) or "").strip() != sentinel:
        raise KRXHistoricalWorkerEntrypointError(
            f"stage consent blocked: {requirement_name}"
        )


def _require_identity_binding_stage_consent(environment: Mapping[str, str]) -> None:
    _require_exact_stage_consent(
        environment,
        env_name=IDENTITY_BINDING_CONSENT_ENV,
        sentinel=IDENTITY_BINDING_CONSENT_SENTINEL,
        requirement_name="EXPLICIT_IDENTITY_STANDARD_CODE_BINDING_CONSENT",
    )


def _public_preflight(environment: Mapping[str, str]) -> dict[str, Any]:
    out = evaluate_historical_acquisition_preflight(environment=environment)
    return {
        "plan_id": out["plan_id"],
        "execution_contract_id": out["execution_contract_id"],
        "rights_authorized": out["rights_authorized"],
        "high_frequency_collection_authorized": out[
            "high_frequency_collection_authorized"
        ],
        "full_historical_download_rights_authorized": out[
            "full_historical_download_rights_authorized"
        ],
        "krx_id_present": out["krx_id_present"],
        "krx_pw_present": out["krx_pw_present"],
        "krx_openapi_auth_key_present": out["krx_openapi_auth_key_present"],
        "dedicated_worker_role_present": out["dedicated_worker_role_present"],
        "railway_service_name": out["railway_service_name"],
        "forbidden_public_service": out["forbidden_public_service"],
        "dedicated_worker_isolation_ok": out["dedicated_worker_isolation_ok"],
        "private_raw_dir_configured": out["private_raw_dir_configured"],
        "private_raw_dir_valid": out["private_raw_dir_valid"],
        "explicit_execution_consent_present": out[
            "explicit_execution_consent_present"
        ],
        "historical_acquisition_network_execution_authorized": out[
            "historical_acquisition_network_execution_authorized"
        ],
        "missing_requirements": list(out["missing_requirements"]),
        "network_request_attempted": False,
        "feature_performance_testing_authorized": False,
        "sealed_holdout_authorized": False,
        "live_trading_authorized": False,
    }


def preflight_only(environment: Mapping[str, str] | None = None) -> dict[str, Any]:
    env = dict(os.environ if environment is None else environment)
    tasks = build_identity_seed_tasks()
    return {
        "mode": "PREFLIGHT_ONLY",
        "preflight": _public_preflight(env),
        "identity_seed": public_task_summary(tasks),
        "network_request_attempted": False,
        "raw_rows_emitted": False,
        "feature_performance_testing_authorized": False,
        "sealed_holdout_authorized": False,
        "live_trading_authorized": False,
    }


def status_per_security_history(
    *,
    environment: Mapping[str, str] | None = None,
    git_worktree: str | None = None,
    state_loader=read_private_json,
) -> dict[str, Any]:
    """Return only public-safe aggregate PER_SECURITY_HISTORY progress.

    This is strictly network-free. It reads only the persisted private phase
    state, then projects it through public_phase_summary so task IDs, security
    identifiers and raw KRX rows can never be emitted.
    """
    env = dict(os.environ if environment is None else environment)
    preflight = evaluate_historical_acquisition_preflight(
        environment=env,
        git_worktree=git_worktree,
    )
    if not preflight["rights_authorized"]:
        raise KRXHistoricalWorkerEntrypointError(
            "per-security status blocked: KRX_FULL_HISTORY_RIGHTS"
        )
    if not preflight["dedicated_worker_isolation_ok"]:
        raise KRXHistoricalWorkerEntrypointError(
            "per-security status blocked: DEDICATED_WORKER_SERVICE_ISOLATION"
        )
    if not preflight["private_raw_dir_configured"] or not preflight["private_raw_dir_valid"]:
        raise KRXHistoricalWorkerEntrypointError(
            "per-security status blocked: SAFE_KRX_PRIVATE_RAW_DIR"
        )

    worktree = git_worktree or str(Path.cwd().resolve())
    root = str(env["KRX_PRIVATE_RAW_DIR"])
    state = state_loader(
        root,
        "batch_state/PER_SECURITY_HISTORY.json",
        git_worktree=worktree,
    )["value"]
    safe = public_phase_summary(state)

    if safe.get("phase") != "PER_SECURITY_HISTORY":
        raise KRXHistoricalWorkerEntrypointError(
            "per-security status phase drift"
        )
    if int(safe.get("expected_task_count", -1)) != PER_SECURITY_EXPECTED_TASK_COUNT:
        raise KRXHistoricalWorkerEntrypointError(
            "per-security status expected task count drift"
        )
    if (
        str(safe.get("task_set_fingerprint_sha256") or "")
        != PER_SECURITY_EXPECTED_TASK_SET_SHA256
    ):
        raise KRXHistoricalWorkerEntrypointError(
            "per-security status task-set fingerprint drift"
        )

    return {
        "mode": "STATUS_PER_SECURITY_HISTORY",
        "summary": safe,
        "network_request_attempted": False,
        "security_identifiers_emitted": False,
        "raw_rows_emitted": False,
        "feature_performance_testing_authorized": False,
        "sealed_holdout_authorized": False,
        "live_trading_authorized": False,
    }


def finalize_per_security_history_metadata(
    *,
    environment: Mapping[str, str] | None = None,
    git_worktree: str | None = None,
    state_loader=read_private_json,
    batch_loader=read_private_json,
) -> dict[str, Any]:
    """Return public-safe completion metadata only after exact phase COMPLETE.

    Strictly network-free and read-only. It never emits private task rows,
    request parameters, security identifiers, credentials or raw response data.
    """
    env = dict(os.environ if environment is None else environment)
    preflight = evaluate_historical_acquisition_preflight(
        environment=env,
        git_worktree=git_worktree,
    )
    if not preflight["rights_authorized"]:
        raise KRXHistoricalWorkerEntrypointError(
            "per-security finalization blocked: KRX_FULL_HISTORY_RIGHTS"
        )
    if not preflight["dedicated_worker_isolation_ok"]:
        raise KRXHistoricalWorkerEntrypointError(
            "per-security finalization blocked: DEDICATED_WORKER_SERVICE_ISOLATION"
        )
    if not preflight["private_raw_dir_configured"] or not preflight["private_raw_dir_valid"]:
        raise KRXHistoricalWorkerEntrypointError(
            "per-security finalization blocked: SAFE_KRX_PRIVATE_RAW_DIR"
        )

    worktree = git_worktree or str(Path.cwd().resolve())
    root = str(env["KRX_PRIVATE_RAW_DIR"])

    state_read = state_loader(
        root,
        "batch_state/PER_SECURITY_HISTORY.json",
        git_worktree=worktree,
    )
    safe = public_phase_summary(state_read["value"])
    if safe.get("phase") != "PER_SECURITY_HISTORY":
        raise KRXHistoricalWorkerEntrypointError(
            "per-security finalization phase drift"
        )
    if safe.get("status") != "COMPLETE" or safe.get("phase_complete") is not True:
        raise KRXHistoricalWorkerEntrypointError(
            "per-security finalization blocked: phase is not COMPLETE"
        )
    if int(safe.get("expected_task_count", -1)) != PER_SECURITY_EXPECTED_TASK_COUNT:
        raise KRXHistoricalWorkerEntrypointError(
            "per-security finalization expected task count drift"
        )
    if int(safe.get("completed_task_count", -1)) != PER_SECURITY_EXPECTED_TASK_COUNT:
        raise KRXHistoricalWorkerEntrypointError(
            "per-security finalization completed task count drift"
        )
    if int(safe.get("failed_task_count", -1)) != 0:
        raise KRXHistoricalWorkerEntrypointError(
            "per-security finalization has failed tasks"
        )
    if (
        str(safe.get("task_set_fingerprint_sha256") or "")
        != PER_SECURITY_EXPECTED_TASK_SET_SHA256
    ):
        raise KRXHistoricalWorkerEntrypointError(
            "per-security finalization task-set fingerprint drift"
        )

    batch_read = batch_loader(
        root,
        PER_SECURITY_BATCH_REL,
        git_worktree=worktree,
    )
    batch = batch_read["value"]
    if batch.get("phase") != "PER_SECURITY_HISTORY":
        raise KRXHistoricalWorkerEntrypointError(
            "per-security batch phase drift"
        )
    if int(batch.get("task_count", -1)) != PER_SECURITY_EXPECTED_TASK_COUNT:
        raise KRXHistoricalWorkerEntrypointError(
            "per-security batch task count drift"
        )
    if int(batch.get("completed_task_count", -1)) != PER_SECURITY_EXPECTED_TASK_COUNT:
        raise KRXHistoricalWorkerEntrypointError(
            "per-security batch completion count drift"
        )
    resumed = int(batch.get("resumed_task_count", -1))
    network = int(batch.get("network_request_attempt_count", -1))
    if resumed < 0 or network < 0 or resumed + network != PER_SECURITY_EXPECTED_TASK_COUNT:
        raise KRXHistoricalWorkerEntrypointError(
            "per-security batch network/resume accounting drift"
        )
    if (
        str(batch.get("task_set_fingerprint_sha256") or "")
        != PER_SECURITY_EXPECTED_TASK_SET_SHA256
    ):
        raise KRXHistoricalWorkerEntrypointError(
            "per-security batch task-set fingerprint drift"
        )
    for key in (
        "source_gate_c_closed",
        "source_gate_d_closed",
        "source_gate_e_closed",
        "feature_performance_testing_authorized",
        "sealed_holdout_authorized",
        "live_trading_authorized",
    ):
        if batch.get(key) is not False:
            raise KRXHistoricalWorkerEntrypointError(
                f"per-security batch {key} illegally true"
            )

    return {
        "mode": "FINALIZE_PER_SECURITY_HISTORY_METADATA",
        "phase": "PER_SECURITY_HISTORY",
        "status": "COMPLETE",
        "expected_task_count": PER_SECURITY_EXPECTED_TASK_COUNT,
        "completed_task_count": PER_SECURITY_EXPECTED_TASK_COUNT,
        "failed_task_count": 0,
        "resumed_task_count": resumed,
        "network_request_attempt_count": network,
        "task_set_fingerprint_sha256": PER_SECURITY_EXPECTED_TASK_SET_SHA256,
        "private_batch_metadata_sha256": batch_read["metadata_sha256"],
        "private_batch_relpath": PER_SECURITY_BATCH_REL,
        "network_request_attempted": False,
        "security_identifiers_emitted": False,
        "raw_rows_emitted": False,
        "status_economics_authorized": False,
        "expected_scope_network_execution_authorized": False,
        "feature_performance_testing_authorized": False,
        "sealed_holdout_authorized": False,
        "genuine_live_authorized": False,
        "live_trading_authorized": False,
    }


def execute_identity_seed(
    *,
    environment: Mapping[str, str] | None = None,
    git_worktree: str | None = None,
    executor=execute_request_spec,
    evaluation_time: datetime | None = None,
) -> dict[str, Any]:
    """Execute only the fixed 27-task identity seed stage.

    Public return data is metadata-only. Per-task request details and raw bytes
    stay inside the private volume through the lower worker layers.
    """
    env = dict(os.environ if environment is None else environment)
    preflight = evaluate_historical_acquisition_preflight(
        environment=env,
        git_worktree=git_worktree,
    )
    if not preflight["historical_acquisition_network_execution_authorized"]:
        raise KRXHistoricalWorkerEntrypointError(
            "historical acquisition preflight blocked: "
            + ",".join(preflight["missing_requirements"])
        )

    tasks = build_identity_seed_tasks()
    task_summary = public_task_summary(tasks)
    if task_summary["task_count"] != 27:
        raise KRXHistoricalWorkerEntrypointError(
            "identity seed task count must remain exactly 27"
        )

    phase_state = initialize_phase_state(
        root=str(env["KRX_PRIVATE_RAW_DIR"]),
        phase="IDENTITY_SEED",
        tasks=tasks,
        git_worktree=(git_worktree or str(Path.cwd().resolve())),
    )

    completed = []
    resumed = 0
    network_attempt_count = 0
    now = evaluation_time or datetime.now(timezone.utc)
    if now.tzinfo is None or now.utcoffset() is None:
        raise KRXHistoricalWorkerEntrypointError(
            "evaluation_time must be timezone-aware"
        )

    worktree = git_worktree or str(Path.cwd().resolve())
    for ordinal, task in enumerate(tasks, start=1):
        result = executor(
            spec=task["request_spec"],
            environment=env,
            git_worktree=worktree,
            client_revision=CLIENT_REVISION,
            evaluation_time=now,
        )
        if not result.get("completed"):
            raise KRXHistoricalWorkerEntrypointError(
                f"identity seed task {ordinal} did not complete"
            )
        if result.get("resumed"):
            resumed += 1
        if result.get("network_request_attempted"):
            network_attempt_count += 1
        phase_state = record_task_completion(
            root=str(env["KRX_PRIVATE_RAW_DIR"]),
            phase="IDENTITY_SEED",
            task_id=task["task_id"],
            worker_result=result,
            git_worktree=worktree,
        )
        completed.append(
            {
                "ordinal": ordinal,
                "task_id": task["task_id"],
                "request_metadata_sha256": result["request_metadata_sha256"],
                "raw_object_sha256": result["raw_object_sha256"],
                "raw_bytes_size": int(result["raw_bytes_size"]),
                "response_rows": int(result["response_rows"]),
                "retrieved_at": result["retrieved_at"],
                "response_schema_sha256": result["response_schema_sha256"],
                "response_payload_sha256": result["response_payload_sha256"],
                "receipt_fingerprint_sha256": result[
                    "receipt_fingerprint_sha256"
                ],
                "resumed": bool(result.get("resumed")),
            }
        )

    final_phase_state = require_phase_complete(
        root=str(env["KRX_PRIVATE_RAW_DIR"]),
        phase="IDENTITY_SEED",
        git_worktree=worktree,
    )
    safe_phase = public_phase_summary(final_phase_state)
    if safe_phase["completed_task_count"] != 27 or not safe_phase["phase_complete"]:
        raise KRXHistoricalWorkerEntrypointError(
            "identity seed phase did not reach exact COMPLETE state"
        )

    raw_root = str(env.get("KRX_PRIVATE_RAW_DIR") or "").strip()
    private_batch = {
        "batch_version": "2026-10-02.identity-seed-v3",
        "plan_id": PLAN_ID,
        "execution_contract_id": EXECUTION_CONTRACT_ID,
        "phase": "IDENTITY_SEED",
        "task_set_fingerprint_sha256": task_summary[
            "task_set_fingerprint_sha256"
        ],
        "task_count": len(tasks),
        "completed_task_count": len(completed),
        "resumed_task_count": resumed,
        "network_request_attempt_count": network_attempt_count,
        "phase_state_fingerprint_sha256": safe_phase[
            "task_set_fingerprint_sha256"
        ],
        "tasks": completed,
        "feature_performance_testing_authorized": False,
        "sealed_holdout_authorized": False,
        "live_trading_authorized": False,
    }
    batch_write = write_private_json(
        raw_root,
        PRIVATE_BATCH_REL,
        private_batch,
        git_worktree=worktree,
    )

    return {
        "mode": "EXECUTE_IDENTITY_SEED",
        "plan_id": PLAN_ID,
        "execution_contract_id": EXECUTION_CONTRACT_ID,
        "task_count": len(tasks),
        "completed_task_count": len(completed),
        "resumed_task_count": resumed,
        "network_request_attempt_count": network_attempt_count,
        "task_set_fingerprint_sha256": task_summary[
            "task_set_fingerprint_sha256"
        ],
        "private_batch_metadata_sha256": batch_write["metadata_sha256"],
        "private_batch_relpath": PRIVATE_BATCH_REL,
        "phase_status": safe_phase["status"],
        "phase_complete": safe_phase["phase_complete"],
        "phase_completed_task_count": safe_phase["completed_task_count"],
        "raw_rows_emitted": False,
        "feature_performance_testing_authorized": False,
        "sealed_holdout_authorized": False,
        "live_trading_authorized": False,
    }


def prepare_identity_standard_code_binding(
    *,
    environment: Mapping[str, str] | None = None,
    git_worktree: str | None = None,
    task_builder=build_identity_binding_tasks_from_private_seed,
) -> dict[str, Any]:
    """Freeze the exact identity-binding task set without network access.

    This consumes only the already-completed private IDENTITY_SEED evidence.
    It deliberately does not require either network-execution consent because
    it cannot issue a request.
    """
    env = dict(os.environ if environment is None else environment)
    preflight = evaluate_historical_acquisition_preflight(
        environment=env,
        git_worktree=git_worktree,
    )
    if not preflight["rights_authorized"]:
        raise KRXHistoricalWorkerEntrypointError(
            "identity binding preparation blocked: KRX_FULL_HISTORY_RIGHTS"
        )
    if not preflight["dedicated_worker_isolation_ok"]:
        raise KRXHistoricalWorkerEntrypointError(
            "identity binding preparation blocked: DEDICATED_WORKER_SERVICE_ISOLATION"
        )
    if not preflight["private_raw_dir_configured"] or not preflight["private_raw_dir_valid"]:
        raise KRXHistoricalWorkerEntrypointError(
            "identity binding preparation blocked: SAFE_KRX_PRIVATE_RAW_DIR"
        )

    worktree = git_worktree or str(Path.cwd().resolve())
    root = str(env["KRX_PRIVATE_RAW_DIR"])
    _require_completed_predecessor(
        root=root,
        phase="IDENTITY_SEED",
        git_worktree=worktree,
    )
    tasks = task_builder(root, git_worktree=worktree)
    summary = public_task_summary(tasks)
    if summary["task_count"] <= 0:
        raise KRXHistoricalWorkerEntrypointError(
            "identity standard-code binding task set is empty"
        )
    if task_builder is build_identity_binding_tasks_from_private_seed:
        _require_frozen_identity_binding_summary(summary)

    state = initialize_phase_state(
        root=root,
        phase="IDENTITY_STANDARD_CODE_BINDING",
        tasks=tasks,
        git_worktree=worktree,
    )
    safe_phase = public_phase_summary(state)

    private_manifest = {
        "manifest_version": "2026-10-02.identity-standard-code-binding-v1",
        "plan_id": PLAN_ID,
        "execution_contract_id": EXECUTION_CONTRACT_ID,
        "phase": "IDENTITY_STANDARD_CODE_BINDING",
        "task_count": len(tasks),
        "task_set_fingerprint_sha256": summary["task_set_fingerprint_sha256"],
        "tasks": tasks,
        "network_request_attempted": False,
        "raw_rows_emitted": False,
        "feature_performance_testing_authorized": False,
        "sealed_holdout_authorized": False,
        "live_trading_authorized": False,
    }
    manifest_write = write_private_json(
        root,
        IDENTITY_BINDING_TASK_MANIFEST_REL,
        private_manifest,
        git_worktree=worktree,
    )
    if task_builder is build_identity_binding_tasks_from_private_seed:
        _require_frozen_identity_binding_summary(
            summary,
            manifest_metadata_sha256=manifest_write["metadata_sha256"],
        )

    return {
        "mode": "PREPARE_IDENTITY_STANDARD_CODE_BINDING",
        "plan_id": PLAN_ID,
        "execution_contract_id": EXECUTION_CONTRACT_ID,
        "task_count": int(summary["task_count"]),
        "task_count_by_kind": dict(summary["task_count_by_kind"]),
        "task_set_fingerprint_sha256": summary["task_set_fingerprint_sha256"],
        "private_task_manifest_metadata_sha256": manifest_write["metadata_sha256"],
        "private_task_manifest_relpath": IDENTITY_BINDING_TASK_MANIFEST_REL,
        "phase_status": safe_phase["status"],
        "phase_complete": safe_phase["phase_complete"],
        "network_request_attempted": False,
        "security_identifiers_emitted": False,
        "raw_rows_emitted": False,
        "feature_performance_testing_authorized": False,
        "sealed_holdout_authorized": False,
        "live_trading_authorized": False,
    }


def load_frozen_identity_binding_tasks(
    root: str,
    *,
    git_worktree: str | None = None,
    task_builder=build_identity_binding_tasks_from_private_seed,
) -> list[dict[str, Any]]:
    """Load and verify the prepared private IDENTITY_STANDARD_CODE_BINDING tasks."""
    worktree = git_worktree or str(Path.cwd().resolve())
    regenerated = task_builder(root, git_worktree=worktree)
    regenerated_summary = public_task_summary(regenerated)
    manifest_read = read_private_json(
        root,
        IDENTITY_BINDING_TASK_MANIFEST_REL,
        git_worktree=worktree,
    )
    manifest = manifest_read["value"]
    if task_builder is build_identity_binding_tasks_from_private_seed:
        _require_frozen_identity_binding_summary(
            regenerated_summary,
            manifest_metadata_sha256=manifest_read["metadata_sha256"],
        )

    if manifest.get("plan_id") != PLAN_ID:
        raise KRXHistoricalWorkerEntrypointError(
            "identity binding task manifest plan drift"
        )
    if manifest.get("execution_contract_id") != EXECUTION_CONTRACT_ID:
        raise KRXHistoricalWorkerEntrypointError(
            "identity binding task manifest execution contract drift"
        )
    if manifest.get("phase") != "IDENTITY_STANDARD_CODE_BINDING":
        raise KRXHistoricalWorkerEntrypointError(
            "identity binding task manifest phase drift"
        )
    if int(manifest.get("task_count", -1)) != len(regenerated):
        raise KRXHistoricalWorkerEntrypointError(
            "identity binding task manifest count drift"
        )
    if (
        manifest.get("task_set_fingerprint_sha256")
        != regenerated_summary["task_set_fingerprint_sha256"]
    ):
        raise KRXHistoricalWorkerEntrypointError(
            "identity binding task manifest fingerprint drift"
        )

    frozen = list(manifest.get("tasks") or [])
    if frozen != regenerated:
        raise KRXHistoricalWorkerEntrypointError(
            "identity binding private task ordering/content drift"
        )

    initialize_phase_state(
        root=root,
        phase="IDENTITY_STANDARD_CODE_BINDING",
        tasks=frozen,
        git_worktree=worktree,
    )
    return frozen


def execute_identity_standard_code_binding(
    *,
    environment: Mapping[str, str] | None = None,
    git_worktree: str | None = None,
    executor=execute_request_spec,
    task_loader=load_frozen_identity_binding_tasks,
    evaluation_time: datetime | None = None,
) -> dict[str, Any]:
    """Execute exact listing-date security-master requests after seed completion."""
    env = dict(os.environ if environment is None else environment)
    preflight = evaluate_historical_acquisition_preflight(
        environment=env,
        git_worktree=git_worktree,
    )
    if not preflight["historical_acquisition_network_execution_authorized"]:
        raise KRXHistoricalWorkerEntrypointError(
            "historical acquisition preflight blocked: "
            + ",".join(preflight["missing_requirements"])
        )
    _require_identity_binding_stage_consent(env)

    worktree = git_worktree or str(Path.cwd().resolve())
    root = str(env["KRX_PRIVATE_RAW_DIR"])
    _require_completed_predecessor(
        root=root,
        phase="IDENTITY_SEED",
        git_worktree=worktree,
    )
    tasks = task_loader(root, git_worktree=worktree)
    task_summary = public_task_summary(tasks)
    if task_summary["task_count"] <= 0:
        raise KRXHistoricalWorkerEntrypointError(
            "identity standard-code binding task set is empty"
        )
    if task_loader is load_frozen_identity_binding_tasks:
        _require_frozen_identity_binding_summary(task_summary)

    initialize_phase_state(
        root=str(env["KRX_PRIVATE_RAW_DIR"]),
        phase="IDENTITY_STANDARD_CODE_BINDING",
        tasks=tasks,
        git_worktree=worktree,
    )

    completed = []
    resumed = 0
    network_attempt_count = 0
    now = evaluation_time or datetime.now(timezone.utc)
    if now.tzinfo is None or now.utcoffset() is None:
        raise KRXHistoricalWorkerEntrypointError(
            "evaluation_time must be timezone-aware"
        )

    for ordinal, task in enumerate(tasks, start=1):
        result = executor(
            spec=task["request_spec"],
            environment=env,
            git_worktree=worktree,
            client_revision=CLIENT_REVISION,
            evaluation_time=now,
        )
        if not result.get("completed"):
            raise KRXHistoricalWorkerEntrypointError(
                f"identity binding task {ordinal} did not complete"
            )
        if result.get("resumed"):
            resumed += 1
        if result.get("network_request_attempted"):
            network_attempt_count += 1
        record_task_completion(
            root=str(env["KRX_PRIVATE_RAW_DIR"]),
            phase="IDENTITY_STANDARD_CODE_BINDING",
            task_id=task["task_id"],
            worker_result=result,
            git_worktree=worktree,
        )
        completed.append(
            {
                "ordinal": ordinal,
                "task_id": task["task_id"],
                "request_metadata_sha256": result["request_metadata_sha256"],
                "raw_object_sha256": result["raw_object_sha256"],
                "raw_bytes_size": int(result["raw_bytes_size"]),
                "response_rows": int(result["response_rows"]),
                "retrieved_at": result["retrieved_at"],
                "response_schema_sha256": result["response_schema_sha256"],
                "response_payload_sha256": result["response_payload_sha256"],
                "receipt_fingerprint_sha256": result[
                    "receipt_fingerprint_sha256"
                ],
                "resumed": bool(result.get("resumed")),
            }
        )

    final_phase_state = require_phase_complete(
        root=str(env["KRX_PRIVATE_RAW_DIR"]),
        phase="IDENTITY_STANDARD_CODE_BINDING",
        git_worktree=worktree,
    )
    safe_phase = public_phase_summary(final_phase_state)
    if safe_phase["completed_task_count"] != len(tasks) or not safe_phase["phase_complete"]:
        raise KRXHistoricalWorkerEntrypointError(
            "identity standard-code binding phase did not reach exact COMPLETE state"
        )

    private_batch = {
        "batch_version": "2026-10-02.identity-standard-code-binding-v3",
        "plan_id": PLAN_ID,
        "execution_contract_id": EXECUTION_CONTRACT_ID,
        "phase": "IDENTITY_STANDARD_CODE_BINDING",
        "task_set_fingerprint_sha256": task_summary[
            "task_set_fingerprint_sha256"
        ],
        "task_count": len(tasks),
        "completed_task_count": len(completed),
        "resumed_task_count": resumed,
        "network_request_attempt_count": network_attempt_count,
        "phase_state_fingerprint_sha256": safe_phase[
            "task_set_fingerprint_sha256"
        ],
        "tasks": completed,
        "feature_performance_testing_authorized": False,
        "sealed_holdout_authorized": False,
        "live_trading_authorized": False,
    }
    batch_write = write_private_json(
        str(env["KRX_PRIVATE_RAW_DIR"]),
        IDENTITY_BINDING_BATCH_REL,
        private_batch,
        git_worktree=worktree,
    )

    return {
        "mode": "EXECUTE_IDENTITY_STANDARD_CODE_BINDING",
        "plan_id": PLAN_ID,
        "execution_contract_id": EXECUTION_CONTRACT_ID,
        "task_count": len(tasks),
        "completed_task_count": len(completed),
        "resumed_task_count": resumed,
        "network_request_attempt_count": network_attempt_count,
        "task_set_fingerprint_sha256": task_summary[
            "task_set_fingerprint_sha256"
        ],
        "private_batch_metadata_sha256": batch_write["metadata_sha256"],
        "private_batch_relpath": IDENTITY_BINDING_BATCH_REL,
        "phase_status": safe_phase["status"],
        "phase_complete": safe_phase["phase_complete"],
        "phase_completed_task_count": safe_phase["completed_task_count"],
        "raw_rows_emitted": False,
        "feature_performance_testing_authorized": False,
        "sealed_holdout_authorized": False,
        "live_trading_authorized": False,
    }


def diagnose_identity_master_code_shapes(
    *,
    environment: Mapping[str, str] | None = None,
    git_worktree: str | None = None,
    summary_loader=public_identity_master_code_shape_summary,
) -> dict[str, Any]:
    """Network-free aggregate diagnostic for private master short-code shapes."""
    env = dict(os.environ if environment is None else environment)
    preflight = evaluate_historical_acquisition_preflight(
        environment=env,
        git_worktree=git_worktree,
    )
    if not preflight["rights_authorized"]:
        raise KRXHistoricalWorkerEntrypointError(
            "identity code-shape diagnostic blocked: KRX_FULL_HISTORY_RIGHTS"
        )
    if not preflight["dedicated_worker_isolation_ok"]:
        raise KRXHistoricalWorkerEntrypointError(
            "identity code-shape diagnostic blocked: DEDICATED_WORKER_SERVICE_ISOLATION"
        )
    if not preflight["private_raw_dir_configured"] or not preflight["private_raw_dir_valid"]:
        raise KRXHistoricalWorkerEntrypointError(
            "identity code-shape diagnostic blocked: SAFE_KRX_PRIVATE_RAW_DIR"
        )

    worktree = git_worktree or str(Path.cwd().resolve())
    summary = summary_loader(
        str(env["KRX_PRIVATE_RAW_DIR"]),
        git_worktree=worktree,
    )
    if summary.get("network_request_attempted") is not False:
        raise KRXHistoricalWorkerEntrypointError(
            "identity code-shape diagnostic attempted network access"
        )
    if summary.get("identifiers_emitted") is not False:
        raise KRXHistoricalWorkerEntrypointError(
            "identity code-shape diagnostic emitted identifiers"
        )
    return {
        "mode": "DIAGNOSE_IDENTITY_MASTER_CODE_SHAPES",
        "summary": dict(summary),
        "network_request_attempted": False,
        "security_identifiers_emitted": False,
        "raw_rows_emitted": False,
        "feature_performance_testing_authorized": False,
        "sealed_holdout_authorized": False,
        "live_trading_authorized": False,
    }


def diagnose_new_listing_master_mapping(
    *,
    environment: Mapping[str, str] | None = None,
    git_worktree: str | None = None,
    summary_loader=public_new_listing_master_mapping_summary,
) -> dict[str, Any]:
    """Network-free aggregate diagnostic for private new-listing/master mapping."""
    env = dict(os.environ if environment is None else environment)
    preflight = evaluate_historical_acquisition_preflight(
        environment=env,
        git_worktree=git_worktree,
    )
    if not preflight["rights_authorized"]:
        raise KRXHistoricalWorkerEntrypointError(
            "new-listing mapping diagnostic blocked: KRX_FULL_HISTORY_RIGHTS"
        )
    if not preflight["dedicated_worker_isolation_ok"]:
        raise KRXHistoricalWorkerEntrypointError(
            "new-listing mapping diagnostic blocked: DEDICATED_WORKER_SERVICE_ISOLATION"
        )
    if not preflight["private_raw_dir_configured"] or not preflight["private_raw_dir_valid"]:
        raise KRXHistoricalWorkerEntrypointError(
            "new-listing mapping diagnostic blocked: SAFE_KRX_PRIVATE_RAW_DIR"
        )

    worktree = git_worktree or str(Path.cwd().resolve())
    summary = summary_loader(
        str(env["KRX_PRIVATE_RAW_DIR"]),
        git_worktree=worktree,
    )
    if summary.get("network_request_attempted") is not False:
        raise KRXHistoricalWorkerEntrypointError(
            "new-listing mapping diagnostic attempted network access"
        )
    if summary.get("identifiers_emitted") is not False:
        raise KRXHistoricalWorkerEntrypointError(
            "new-listing mapping diagnostic emitted identifiers"
        )
    if summary.get("names_emitted") is not False:
        raise KRXHistoricalWorkerEntrypointError(
            "new-listing mapping diagnostic emitted names"
        )
    return {
        "mode": "DIAGNOSE_NEW_LISTING_MASTER_MAPPING",
        "summary": dict(summary),
        "network_request_attempted": False,
        "security_identifiers_emitted": False,
        "names_emitted": False,
        "raw_rows_emitted": False,
        "feature_performance_testing_authorized": False,
        "sealed_holdout_authorized": False,
        "live_trading_authorized": False,
    }


def diagnose_delisted_start_master_mapping(
    *,
    environment: Mapping[str, str] | None = None,
    git_worktree: str | None = None,
    summary_loader=public_delisted_start_master_mapping_summary,
) -> dict[str, Any]:
    """Network-free aggregate diagnostic for delisted/start-master mapping."""
    env = dict(os.environ if environment is None else environment)
    preflight = evaluate_historical_acquisition_preflight(
        environment=env,
        git_worktree=git_worktree,
    )
    if not preflight["rights_authorized"]:
        raise KRXHistoricalWorkerEntrypointError(
            "delisted/start mapping diagnostic blocked: KRX_FULL_HISTORY_RIGHTS"
        )
    if not preflight["dedicated_worker_isolation_ok"]:
        raise KRXHistoricalWorkerEntrypointError(
            "delisted/start mapping diagnostic blocked: DEDICATED_WORKER_SERVICE_ISOLATION"
        )
    if not preflight["private_raw_dir_configured"] or not preflight["private_raw_dir_valid"]:
        raise KRXHistoricalWorkerEntrypointError(
            "delisted/start mapping diagnostic blocked: SAFE_KRX_PRIVATE_RAW_DIR"
        )
    worktree = git_worktree or str(Path.cwd().resolve())
    summary = summary_loader(
        str(env["KRX_PRIVATE_RAW_DIR"]),
        git_worktree=worktree,
    )
    if summary.get("network_request_attempted") is not False:
        raise KRXHistoricalWorkerEntrypointError(
            "delisted/start mapping diagnostic attempted network access"
        )
    if summary.get("identifiers_emitted") is not False:
        raise KRXHistoricalWorkerEntrypointError(
            "delisted/start mapping diagnostic emitted identifiers"
        )
    if summary.get("names_emitted") is not False:
        raise KRXHistoricalWorkerEntrypointError(
            "delisted/start mapping diagnostic emitted names"
        )
    return {
        "mode": "DIAGNOSE_DELISTED_START_MASTER_MAPPING",
        "summary": dict(summary),
        "network_request_attempted": False,
        "security_identifiers_emitted": False,
        "names_emitted": False,
        "raw_rows_emitted": False,
        "feature_performance_testing_authorized": False,
        "sealed_holdout_authorized": False,
        "live_trading_authorized": False,
    }


def prepare_per_security_history(
    *,
    environment: Mapping[str, str] | None = None,
    git_worktree: str | None = None,
    task_builder=build_per_security_history_tasks_from_private_identity,
) -> dict[str, Any]:
    """Freeze PER_SECURITY_HISTORY task set without performing network access.

    This preparation step requires the dedicated worker/private-storage boundary
    and a completed identity-binding predecessor, but deliberately does not
    require the bulk network consent sentinel because it cannot issue a request.
    """
    env = dict(os.environ if environment is None else environment)
    preflight = evaluate_historical_acquisition_preflight(
        environment=env,
        git_worktree=git_worktree,
    )
    if not preflight["rights_authorized"]:
        raise KRXHistoricalWorkerEntrypointError(
            "per-security preparation blocked: KRX_FULL_HISTORY_RIGHTS"
        )
    if not preflight["dedicated_worker_isolation_ok"]:
        raise KRXHistoricalWorkerEntrypointError(
            "per-security preparation blocked: DEDICATED_WORKER_SERVICE_ISOLATION"
        )
    if not preflight["private_raw_dir_configured"] or not preflight["private_raw_dir_valid"]:
        raise KRXHistoricalWorkerEntrypointError(
            "per-security preparation blocked: SAFE_KRX_PRIVATE_RAW_DIR"
        )

    worktree = git_worktree or str(Path.cwd().resolve())
    root = str(env["KRX_PRIVATE_RAW_DIR"])
    tasks = task_builder(root, git_worktree=worktree)
    summary = public_task_summary(tasks)
    if summary["task_count"] <= 0:
        raise KRXHistoricalWorkerEntrypointError(
            "per-security history task set is empty"
        )
    if task_builder is build_per_security_history_tasks_from_private_identity:
        _require_frozen_per_security_summary(summary)

    state = initialize_phase_state(
        root=root,
        phase="PER_SECURITY_HISTORY",
        tasks=tasks,
        git_worktree=worktree,
    )
    safe_phase = public_phase_summary(state)

    private_manifest = {
        "manifest_version": "2026-10-02.per-security-history-v3",
        "plan_id": PLAN_ID,
        "execution_contract_id": EXECUTION_CONTRACT_ID,
        "phase": "PER_SECURITY_HISTORY",
        "task_count": len(tasks),
        "task_set_fingerprint_sha256": summary[
            "task_set_fingerprint_sha256"
        ],
        "tasks": tasks,
        "network_request_attempted": False,
        "source_gate_c_closed": False,
        "source_gate_d_closed": False,
        "source_gate_e_closed": False,
        "feature_performance_testing_authorized": False,
        "sealed_holdout_authorized": False,
        "live_trading_authorized": False,
    }
    manifest_write = write_private_json(
        root,
        PER_SECURITY_TASK_MANIFEST_REL,
        private_manifest,
        git_worktree=worktree,
    )
    if task_builder is build_per_security_history_tasks_from_private_identity:
        _require_frozen_per_security_summary(
            summary,
            manifest_metadata_sha256=manifest_write["metadata_sha256"],
        )

    return {
        "mode": "PREPARE_PER_SECURITY_HISTORY",
        "plan_id": PLAN_ID,
        "execution_contract_id": EXECUTION_CONTRACT_ID,
        "task_count": int(summary["task_count"]),
        "task_count_by_kind": dict(summary["task_count_by_kind"]),
        "task_set_fingerprint_sha256": summary[
            "task_set_fingerprint_sha256"
        ],
        "private_task_manifest_metadata_sha256": manifest_write[
            "metadata_sha256"
        ],
        "private_task_manifest_relpath": PER_SECURITY_TASK_MANIFEST_REL,
        "phase_status": safe_phase["status"],
        "phase_complete": safe_phase["phase_complete"],
        "network_request_attempted": False,
        "security_identifiers_emitted": False,
        "raw_rows_emitted": False,
        "source_gate_c_closed": False,
        "source_gate_d_closed": False,
        "source_gate_e_closed": False,
        "feature_performance_testing_authorized": False,
        "sealed_holdout_authorized": False,
        "live_trading_authorized": False,
    }


def prepare_status_economics(
    *,
    environment: Mapping[str, str] | None = None,
    git_worktree: str | None = None,
    task_builder=build_status_economics_tasks_from_private_identity,
) -> dict[str, Any]:
    """Freeze KRX delisted-price context tasks without network access.

    This phase never claims exact realized fill/recovery economics. It prepares
    only official MDCSTAT23902 cleanup-window price context for episodes that
    actually have an official cleanup interval.
    """
    env = dict(os.environ if environment is None else environment)
    preflight = evaluate_historical_acquisition_preflight(
        environment=env,
        git_worktree=git_worktree,
    )
    if not preflight["rights_authorized"]:
        raise KRXHistoricalWorkerEntrypointError(
            "status-economics preparation blocked: KRX_FULL_HISTORY_RIGHTS"
        )
    if not preflight["dedicated_worker_isolation_ok"]:
        raise KRXHistoricalWorkerEntrypointError(
            "status-economics preparation blocked: DEDICATED_WORKER_SERVICE_ISOLATION"
        )
    if not preflight["private_raw_dir_configured"] or not preflight["private_raw_dir_valid"]:
        raise KRXHistoricalWorkerEntrypointError(
            "status-economics preparation blocked: SAFE_KRX_PRIVATE_RAW_DIR"
        )

    worktree = git_worktree or str(Path.cwd().resolve())
    root = str(env["KRX_PRIVATE_RAW_DIR"])
    tasks, event_summary = task_builder(root, git_worktree=worktree)
    summary = public_task_summary(tasks)
    if summary["task_count"] <= 0:
        raise KRXHistoricalWorkerEntrypointError(
            "status-economics price-context task set is empty; "
            "exact status economics remains open"
        )

    state = initialize_phase_state(
        root=root,
        phase="STATUS_ECONOMICS",
        tasks=tasks,
        git_worktree=worktree,
    )
    safe_phase = public_phase_summary(state)

    private_manifest = {
        "manifest_version": "2026-10-02.status-economics-v3",
        "plan_id": PLAN_ID,
        "execution_contract_id": EXECUTION_CONTRACT_ID,
        "phase": "STATUS_ECONOMICS",
        "task_count": len(tasks),
        "task_set_fingerprint_sha256": summary[
            "task_set_fingerprint_sha256"
        ],
        "event_summary": dict(event_summary),
        "tasks": tasks,
        "network_request_attempted": False,
        "exact_status_economics_ready": False,
        "source_gate_c_closed": False,
        "source_gate_d_closed": False,
        "source_gate_e_closed": False,
        "feature_performance_testing_authorized": False,
        "sealed_holdout_authorized": False,
        "live_trading_authorized": False,
    }
    manifest_write = write_private_json(
        root,
        STATUS_ECONOMICS_TASK_MANIFEST_REL,
        private_manifest,
        git_worktree=worktree,
    )

    return {
        "mode": "PREPARE_STATUS_ECONOMICS",
        "plan_id": PLAN_ID,
        "execution_contract_id": EXECUTION_CONTRACT_ID,
        "task_count": int(summary["task_count"]),
        "delisted_episode_count": int(event_summary["delisted_episode_count"]),
        "cleanup_price_task_count": int(event_summary["cleanup_price_task_count"]),
        "delisted_without_cleanup_interval_count": int(
            event_summary["delisted_without_cleanup_interval_count"]
        ),
        "task_set_fingerprint_sha256": summary[
            "task_set_fingerprint_sha256"
        ],
        "private_task_manifest_metadata_sha256": manifest_write[
            "metadata_sha256"
        ],
        "private_task_manifest_relpath": STATUS_ECONOMICS_TASK_MANIFEST_REL,
        "phase_status": safe_phase["status"],
        "phase_complete": safe_phase["phase_complete"],
        "network_request_attempted": False,
        "security_identifiers_emitted": False,
        "raw_rows_emitted": False,
        "exact_status_economics_ready": False,
        "source_gate_c_closed": False,
        "source_gate_d_closed": False,
        "source_gate_e_closed": False,
        "feature_performance_testing_authorized": False,
        "sealed_holdout_authorized": False,
        "live_trading_authorized": False,
    }


def load_frozen_per_security_history_tasks(
    root: str,
    *,
    git_worktree: str | None = None,
    task_builder=build_per_security_history_tasks_from_private_identity,
) -> list[dict[str, Any]]:
    """Load and verify the prepared private PER_SECURITY_HISTORY task set."""
    worktree = git_worktree or str(Path.cwd().resolve())
    regenerated = task_builder(root, git_worktree=worktree)
    regenerated_summary = public_task_summary(regenerated)
    manifest_read = read_private_json(
        root,
        PER_SECURITY_TASK_MANIFEST_REL,
        git_worktree=worktree,
    )
    manifest = manifest_read["value"]
    if task_builder is build_per_security_history_tasks_from_private_identity:
        _require_frozen_per_security_summary(
            regenerated_summary,
            manifest_metadata_sha256=manifest_read["metadata_sha256"],
        )

    if manifest.get("plan_id") != PLAN_ID:
        raise KRXHistoricalWorkerEntrypointError(
            "per-security task manifest plan drift"
        )
    if manifest.get("execution_contract_id") != EXECUTION_CONTRACT_ID:
        raise KRXHistoricalWorkerEntrypointError(
            "per-security task manifest execution contract drift"
        )
    if manifest.get("phase") != "PER_SECURITY_HISTORY":
        raise KRXHistoricalWorkerEntrypointError(
            "per-security task manifest phase drift"
        )
    if int(manifest.get("task_count", -1)) != len(regenerated):
        raise KRXHistoricalWorkerEntrypointError(
            "per-security task manifest count drift"
        )
    if (
        manifest.get("task_set_fingerprint_sha256")
        != regenerated_summary["task_set_fingerprint_sha256"]
    ):
        raise KRXHistoricalWorkerEntrypointError(
            "per-security task manifest fingerprint drift"
        )

    frozen = list(manifest.get("tasks") or [])
    if len(frozen) != len(regenerated):
        raise KRXHistoricalWorkerEntrypointError(
            "per-security private task rows missing"
        )
    frozen_ids = [str(row.get("task_id") or "") for row in frozen]
    regenerated_ids = [str(row.get("task_id") or "") for row in regenerated]
    if frozen_ids != regenerated_ids:
        raise KRXHistoricalWorkerEntrypointError(
            "per-security private task ordering/content drift"
        )

    # Re-initialize only to verify that the persisted phase state is bound to
    # exactly this frozen task set. Existing state with any drift fails closed.
    initialize_phase_state(
        root=root,
        phase="PER_SECURITY_HISTORY",
        tasks=frozen,
        git_worktree=worktree,
    )
    return frozen


def execute_per_security_history(
    *,
    environment: Mapping[str, str] | None = None,
    git_worktree: str | None = None,
    executor=execute_request_spec,
    task_loader=load_frozen_per_security_history_tasks,
    evaluation_time: datetime | None = None,
) -> dict[str, Any]:
    """Execute only the already-prepared PER_SECURITY_HISTORY task set.

    This is a bulk network stage. It always re-runs the full historical
    acquisition preflight, including exact user bulk-consent sentinel, dedicated
    worker isolation, private storage and credential presence.
    """
    env = dict(os.environ if environment is None else environment)
    preflight = evaluate_historical_acquisition_preflight(
        environment=env,
        git_worktree=git_worktree,
    )
    if not preflight["historical_acquisition_network_execution_authorized"]:
        raise KRXHistoricalWorkerEntrypointError(
            "historical acquisition preflight blocked: "
            + ",".join(preflight["missing_requirements"])
        )
    _require_exact_stage_consent(
        env,
        env_name=PER_SECURITY_CONSENT_ENV,
        sentinel=PER_SECURITY_CONSENT_SENTINEL,
        requirement_name="EXPLICIT_PER_SECURITY_HISTORY_CONSENT",
    )

    worktree = git_worktree or str(Path.cwd().resolve())
    root = str(env["KRX_PRIVATE_RAW_DIR"])
    tasks = task_loader(root, git_worktree=worktree)
    summary = public_task_summary(tasks)
    if summary["task_count"] <= 0:
        raise KRXHistoricalWorkerEntrypointError(
            "per-security history frozen task set is empty"
        )
    if task_loader is load_frozen_per_security_history_tasks:
        _require_frozen_per_security_summary(summary)

    completed = []
    resumed = 0
    network_attempt_count = 0
    now = evaluation_time or datetime.now(timezone.utc)
    if now.tzinfo is None or now.utcoffset() is None:
        raise KRXHistoricalWorkerEntrypointError(
            "evaluation_time must be timezone-aware"
        )

    for ordinal, task in enumerate(tasks, start=1):
        result = executor(
            spec=task["request_spec"],
            environment=env,
            git_worktree=worktree,
            client_revision=CLIENT_REVISION,
            evaluation_time=now,
        )
        if not result.get("completed"):
            raise KRXHistoricalWorkerEntrypointError(
                f"per-security history task {ordinal} did not complete"
            )
        if result.get("resumed"):
            resumed += 1
        if result.get("network_request_attempted"):
            network_attempt_count += 1
        record_task_completion(
            root=root,
            phase="PER_SECURITY_HISTORY",
            task_id=task["task_id"],
            worker_result=result,
            git_worktree=worktree,
        )
        completed.append(
            {
                "ordinal": ordinal,
                "task_id": task["task_id"],
                "request_metadata_sha256": result["request_metadata_sha256"],
                "raw_object_sha256": result["raw_object_sha256"],
                "raw_bytes_size": int(result["raw_bytes_size"]),
                "response_rows": int(result["response_rows"]),
                "retrieved_at": result["retrieved_at"],
                "response_schema_sha256": result["response_schema_sha256"],
                "response_payload_sha256": result["response_payload_sha256"],
                "receipt_fingerprint_sha256": result[
                    "receipt_fingerprint_sha256"
                ],
                "resumed": bool(result.get("resumed")),
            }
        )

    final_phase_state = require_phase_complete(
        root=root,
        phase="PER_SECURITY_HISTORY",
        git_worktree=worktree,
    )
    safe_phase = public_phase_summary(final_phase_state)
    if (
        safe_phase["completed_task_count"] != len(tasks)
        or not safe_phase["phase_complete"]
    ):
        raise KRXHistoricalWorkerEntrypointError(
            "per-security history phase did not reach exact COMPLETE state"
        )

    private_batch = {
        "batch_version": "2026-10-02.per-security-history-v3",
        "plan_id": PLAN_ID,
        "execution_contract_id": EXECUTION_CONTRACT_ID,
        "phase": "PER_SECURITY_HISTORY",
        "task_set_fingerprint_sha256": summary[
            "task_set_fingerprint_sha256"
        ],
        "task_count": len(tasks),
        "completed_task_count": len(completed),
        "resumed_task_count": resumed,
        "network_request_attempt_count": network_attempt_count,
        "phase_state_fingerprint_sha256": safe_phase[
            "task_set_fingerprint_sha256"
        ],
        "tasks": completed,
        "source_gate_c_closed": False,
        "source_gate_d_closed": False,
        "source_gate_e_closed": False,
        "feature_performance_testing_authorized": False,
        "sealed_holdout_authorized": False,
        "live_trading_authorized": False,
    }
    batch_write = write_private_json(
        root,
        PER_SECURITY_BATCH_REL,
        private_batch,
        git_worktree=worktree,
    )

    return {
        "mode": "EXECUTE_PER_SECURITY_HISTORY",
        "plan_id": PLAN_ID,
        "execution_contract_id": EXECUTION_CONTRACT_ID,
        "task_count": len(tasks),
        "completed_task_count": len(completed),
        "resumed_task_count": resumed,
        "network_request_attempt_count": network_attempt_count,
        "task_set_fingerprint_sha256": summary[
            "task_set_fingerprint_sha256"
        ],
        "private_batch_metadata_sha256": batch_write["metadata_sha256"],
        "private_batch_relpath": PER_SECURITY_BATCH_REL,
        "phase_status": safe_phase["status"],
        "phase_complete": safe_phase["phase_complete"],
        "phase_completed_task_count": safe_phase["completed_task_count"],
        "security_identifiers_emitted": False,
        "raw_rows_emitted": False,
        "source_gate_c_closed": False,
        "source_gate_d_closed": False,
        "source_gate_e_closed": False,
        "feature_performance_testing_authorized": False,
        "sealed_holdout_authorized": False,
        "live_trading_authorized": False,
    }



def load_frozen_status_economics_tasks(
    root: str,
    *,
    git_worktree: str | None = None,
    task_builder=build_status_economics_tasks_from_private_identity,
) -> list[dict[str, Any]]:
    """Load and verify the prepared private STATUS_ECONOMICS task set."""
    worktree = git_worktree or str(Path.cwd().resolve())
    regenerated, event_summary = task_builder(root, git_worktree=worktree)
    regenerated_summary = public_task_summary(regenerated)
    manifest = read_private_json(
        root,
        STATUS_ECONOMICS_TASK_MANIFEST_REL,
        git_worktree=worktree,
    )["value"]

    if manifest.get("plan_id") != PLAN_ID:
        raise KRXHistoricalWorkerEntrypointError(
            "status-economics task manifest plan drift"
        )
    if manifest.get("execution_contract_id") != EXECUTION_CONTRACT_ID:
        raise KRXHistoricalWorkerEntrypointError(
            "status-economics task manifest execution contract drift"
        )
    if manifest.get("phase") != "STATUS_ECONOMICS":
        raise KRXHistoricalWorkerEntrypointError(
            "status-economics task manifest phase drift"
        )
    if int(manifest.get("task_count", -1)) != len(regenerated):
        raise KRXHistoricalWorkerEntrypointError(
            "status-economics task manifest count drift"
        )
    if (
        manifest.get("task_set_fingerprint_sha256")
        != regenerated_summary["task_set_fingerprint_sha256"]
    ):
        raise KRXHistoricalWorkerEntrypointError(
            "status-economics task manifest fingerprint drift"
        )
    if dict(manifest.get("event_summary") or {}) != dict(event_summary):
        raise KRXHistoricalWorkerEntrypointError(
            "status-economics event-summary drift"
        )

    frozen = list(manifest.get("tasks") or [])
    if len(frozen) != len(regenerated):
        raise KRXHistoricalWorkerEntrypointError(
            "status-economics private task rows missing"
        )
    frozen_ids = [str(row.get("task_id") or "") for row in frozen]
    regenerated_ids = [str(row.get("task_id") or "") for row in regenerated]
    if frozen_ids != regenerated_ids:
        raise KRXHistoricalWorkerEntrypointError(
            "status-economics private task ordering/content drift"
        )

    initialize_phase_state(
        root=root,
        phase="STATUS_ECONOMICS",
        tasks=frozen,
        git_worktree=worktree,
    )
    return frozen


def execute_status_economics(
    *,
    environment: Mapping[str, str] | None = None,
    git_worktree: str | None = None,
    executor=execute_request_spec,
    task_loader=load_frozen_status_economics_tasks,
    evaluation_time: datetime | None = None,
) -> dict[str, Any]:
    """Execute only the prepared official cleanup-price context task set.

    This bulk network stage requires the exact frozen historical acquisition
    consent and private dedicated-worker boundary. Completion still does not
    prove realized fills, recovery cash flows or exact status economics.
    """
    env = dict(os.environ if environment is None else environment)
    preflight = evaluate_historical_acquisition_preflight(
        environment=env,
        git_worktree=git_worktree,
    )
    if not preflight["historical_acquisition_network_execution_authorized"]:
        raise KRXHistoricalWorkerEntrypointError(
            "historical acquisition preflight blocked: "
            + ",".join(preflight["missing_requirements"])
        )
    _require_exact_stage_consent(
        env,
        env_name=STATUS_ECONOMICS_CONSENT_ENV,
        sentinel=STATUS_ECONOMICS_CONSENT_SENTINEL,
        requirement_name="EXPLICIT_STATUS_ECONOMICS_CONSENT",
    )

    worktree = git_worktree or str(Path.cwd().resolve())
    root = str(env["KRX_PRIVATE_RAW_DIR"])
    tasks = task_loader(root, git_worktree=worktree)
    summary = public_task_summary(tasks)
    if summary["task_count"] <= 0:
        raise KRXHistoricalWorkerEntrypointError(
            "status-economics frozen task set is empty"
        )

    completed = []
    resumed = 0
    network_attempt_count = 0
    now = evaluation_time or datetime.now(timezone.utc)
    if now.tzinfo is None or now.utcoffset() is None:
        raise KRXHistoricalWorkerEntrypointError(
            "evaluation_time must be timezone-aware"
        )

    for ordinal, task in enumerate(tasks, start=1):
        result = executor(
            spec=task["request_spec"],
            environment=env,
            git_worktree=worktree,
            client_revision=CLIENT_REVISION,
            evaluation_time=now,
        )
        if not result.get("completed"):
            raise KRXHistoricalWorkerEntrypointError(
                f"status-economics task {ordinal} did not complete"
            )
        if result.get("resumed"):
            resumed += 1
        if result.get("network_request_attempted"):
            network_attempt_count += 1
        record_task_completion(
            root=root,
            phase="STATUS_ECONOMICS",
            task_id=task["task_id"],
            worker_result=result,
            git_worktree=worktree,
        )
        completed.append(
            {
                "ordinal": ordinal,
                "task_id": task["task_id"],
                "request_metadata_sha256": result["request_metadata_sha256"],
                "raw_object_sha256": result["raw_object_sha256"],
                "raw_bytes_size": int(result["raw_bytes_size"]),
                "response_rows": int(result["response_rows"]),
                "retrieved_at": result["retrieved_at"],
                "response_schema_sha256": result["response_schema_sha256"],
                "response_payload_sha256": result["response_payload_sha256"],
                "receipt_fingerprint_sha256": result[
                    "receipt_fingerprint_sha256"
                ],
                "resumed": bool(result.get("resumed")),
            }
        )

    final_phase_state = require_phase_complete(
        root=root,
        phase="STATUS_ECONOMICS",
        git_worktree=worktree,
    )
    safe_phase = public_phase_summary(final_phase_state)
    if (
        safe_phase["completed_task_count"] != len(tasks)
        or not safe_phase["phase_complete"]
    ):
        raise KRXHistoricalWorkerEntrypointError(
            "status-economics phase did not reach exact COMPLETE state"
        )

    private_batch = {
        "batch_version": "2026-10-02.status-economics-v3",
        "plan_id": PLAN_ID,
        "execution_contract_id": EXECUTION_CONTRACT_ID,
        "phase": "STATUS_ECONOMICS",
        "task_set_fingerprint_sha256": summary[
            "task_set_fingerprint_sha256"
        ],
        "task_count": len(tasks),
        "completed_task_count": len(completed),
        "resumed_task_count": resumed,
        "network_request_attempt_count": network_attempt_count,
        "phase_state_fingerprint_sha256": safe_phase[
            "task_set_fingerprint_sha256"
        ],
        "tasks": completed,
        "exact_status_economics_ready": False,
        "source_gate_c_closed": False,
        "source_gate_d_closed": False,
        "source_gate_e_closed": False,
        "feature_performance_testing_authorized": False,
        "sealed_holdout_authorized": False,
        "live_trading_authorized": False,
    }
    batch_write = write_private_json(
        root,
        STATUS_ECONOMICS_BATCH_REL,
        private_batch,
        git_worktree=worktree,
    )

    return {
        "mode": "EXECUTE_STATUS_ECONOMICS",
        "plan_id": PLAN_ID,
        "execution_contract_id": EXECUTION_CONTRACT_ID,
        "task_count": len(tasks),
        "completed_task_count": len(completed),
        "resumed_task_count": resumed,
        "network_request_attempt_count": network_attempt_count,
        "task_set_fingerprint_sha256": summary[
            "task_set_fingerprint_sha256"
        ],
        "private_batch_metadata_sha256": batch_write["metadata_sha256"],
        "private_batch_relpath": STATUS_ECONOMICS_BATCH_REL,
        "phase_status": safe_phase["status"],
        "phase_complete": safe_phase["phase_complete"],
        "phase_completed_task_count": safe_phase["completed_task_count"],
        "security_identifiers_emitted": False,
        "raw_rows_emitted": False,
        "exact_status_economics_ready": False,
        "source_gate_c_closed": False,
        "source_gate_d_closed": False,
        "source_gate_e_closed": False,
        "feature_performance_testing_authorized": False,
        "sealed_holdout_authorized": False,
        "live_trading_authorized": False,
    }

def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="IndexAlert KRX historical acquisition dedicated worker"
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--execute-identity-seed",
        action="store_true",
        help=(
            "Execute the fixed 27-request identity-seed stage. Without an "
            "execute flag the command is network-free preflight only."
        ),
    )
    group.add_argument(
        "--prepare-identity-standard-code-binding",
        action="store_true",
        help=(
            "Network-free: after IDENTITY_SEED is complete, derive and freeze "
            "the exact listing-date security-master task set. No KRX request "
            "is issued and no execution consent is required."
        ),
    )
    group.add_argument(
        "--execute-identity-standard-code-binding",
        action="store_true",
        help=(
            "After IDENTITY_SEED is complete, execute one exact security-master "
            "snapshot request per KOSPI common-stock listing date derived from "
            "the private seed history."
        ),
    )
    group.add_argument(
        "--diagnose-identity-master-code-shapes",
        action="store_true",
        help=(
            "Network-free: report only aggregate short-code shape counts from "
            "completed private identity seed/binding material. Never emits "
            "security identifiers or raw rows."
        ),
    )
    group.add_argument(
        "--diagnose-new-listing-master-mapping",
        action="store_true",
        help=(
            "Network-free: report only aggregate mapping-gap counts between "
            "private new-listing history and same-day security-master snapshots. "
            "Never emits identifiers, names, or raw rows."
        ),
    )
    group.add_argument(
        "--diagnose-delisted-start-master-mapping",
        action="store_true",
        help=(
            "Network-free: report only aggregate mapping-gap counts between "
            "pre-start delisted history and the research-start security master. "
            "Never emits identifiers, names, or raw rows."
        ),
    )
    group.add_argument(
        "--status-per-security-history",
        action="store_true",
        help=(
            "Network-free: read only public-safe aggregate progress for the "
            "frozen PER_SECURITY_HISTORY phase. Never emits task IDs, security "
            "identifiers, credentials, or raw KRX rows."
        ),
    )
    group.add_argument(
        "--finalize-per-security-history-metadata",
        action="store_true",
        help=(
            "Network-free/read-only: only after exact PER_SECURITY_HISTORY "
            "completion, return public-safe aggregate completion/batch metadata. "
            "Never emits task rows, identifiers, credentials or raw KRX data."
        ),
    )
    group.add_argument(
        "--prepare-per-security-history",
        action="store_true",
        help=(
            "Network-free: after identity binding is complete, reconstruct "
            "historical episodes and freeze the exact private halt/investor "
            "PER_SECURITY_HISTORY task set."
        ),
    )
    group.add_argument(
        "--execute-per-security-history",
        action="store_true",
        help=(
            "Bulk network stage: execute only the already-prepared immutable "
            "PER_SECURITY_HISTORY task set. Requires exact historical bulk "
            "execution consent and every frozen worker preflight gate."
        ),
    )
    group.add_argument(
        "--prepare-status-economics",
        action="store_true",
        help=(
            "Network-free: after PER_SECURITY_HISTORY is complete, freeze "
            "official cleanup-window MDCSTAT23902 price-context tasks. This "
            "never claims exact realized fill/recovery economics."
        ),
    )
    group.add_argument(
        "--execute-status-economics",
        action="store_true",
        help=(
            "Bulk network stage: execute only the already-prepared immutable "
            "STATUS_ECONOMICS cleanup-price context task set. Requires exact "
            "historical bulk execution consent and every frozen worker gate."
        ),
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    if args.execute_identity_seed:
        result = execute_identity_seed()
    elif args.prepare_identity_standard_code_binding:
        result = prepare_identity_standard_code_binding()
    elif args.execute_identity_standard_code_binding:
        result = execute_identity_standard_code_binding()
    elif args.diagnose_identity_master_code_shapes:
        result = diagnose_identity_master_code_shapes()
    elif args.diagnose_new_listing_master_mapping:
        result = diagnose_new_listing_master_mapping()
    elif args.diagnose_delisted_start_master_mapping:
        result = diagnose_delisted_start_master_mapping()
    elif args.status_per_security_history:
        result = status_per_security_history()
    elif args.finalize_per_security_history_metadata:
        result = finalize_per_security_history_metadata()
    elif args.prepare_per_security_history:
        result = prepare_per_security_history()
    elif args.execute_per_security_history:
        result = execute_per_security_history()
    elif args.prepare_status_economics:
        result = prepare_status_economics()
    elif args.execute_status_economics:
        result = execute_status_economics()
    else:
        result = preflight_only()
    print("INDEXALERT_KRX_HIST_WORKER=" + json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
