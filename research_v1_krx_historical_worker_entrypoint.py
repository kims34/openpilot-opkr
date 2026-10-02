"""Dedicated one-shot entrypoint for staged KRX historical acquisition.

Default behavior is network-free preflight only.

Actual network execution is intentionally limited to the first frozen stage
(IDENTITY_SEED) and requires ALL of:
- --execute-identity-seed
- exact v3 bulk-acquisition consent sentinel in the environment
- dedicated worker role
- non-public Railway service identity
- safe private persistent raw directory
- KRX_ID / KRX_PW / KRX_AUTH_KEY

Later phases are not executable from this entrypoint yet. Identity reconstruction
and exact listing-date master binding must complete before per-security history
can be scheduled.
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
from research_v1_krx_historical_request_executor import execute_request_spec
from research_v1_krx_private_store import write_private_json


CLIENT_REVISION = "krx-data-api@e6ebac9b71482db127348d8a08ebc6743aa3b50e"
PRIVATE_BATCH_REL = "batches/identity-seed-v3.json"


class KRXHistoricalWorkerEntrypointError(RuntimeError):
    pass


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
        completed.append(
            {
                "ordinal": ordinal,
                "task_id": task["task_id"],
                "request_metadata_sha256": result["request_metadata_sha256"],
                "raw_object_sha256": result["raw_object_sha256"],
                "raw_bytes_size": int(result["raw_bytes_size"]),
                "response_rows": int(result["response_rows"]),
                "response_schema_sha256": result["response_schema_sha256"],
                "response_payload_sha256": result["response_payload_sha256"],
                "receipt_fingerprint_sha256": result[
                    "receipt_fingerprint_sha256"
                ],
                "resumed": bool(result.get("resumed")),
            }
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
        "raw_rows_emitted": False,
        "feature_performance_testing_authorized": False,
        "sealed_holdout_authorized": False,
        "live_trading_authorized": False,
    }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="IndexAlert KRX historical acquisition dedicated worker"
    )
    parser.add_argument(
        "--execute-identity-seed",
        action="store_true",
        help=(
            "Execute the fixed 27-request identity-seed stage. Without this "
            "flag the command is network-free preflight only."
        ),
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    if args.execute_identity_seed:
        result = execute_identity_seed()
    else:
        result = preflight_only()
    print("INDEXALERT_KRX_HIST_WORKER=" + json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
