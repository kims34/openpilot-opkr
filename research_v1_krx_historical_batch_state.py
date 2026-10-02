"""Private phase/batch state for the KRX historical acquisition job.

This module is offline/storage-only. It never performs network access.
A phase is COMPLETE only when every preregistered task ID has a verified
completion record bound to a private raw object and receipt fingerprint.

Only hashes/counts are stored in phase state. Security identifiers and raw rows
are never written into batch-state metadata and never emitted publicly.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
from typing import Any, Iterable, Mapping

from research_v1_krx_historical_batch_orchestrator import (
    EXECUTION_CONTRACT_ID,
    PHASE_ORDER,
    PLAN_ID,
)
from research_v1_krx_private_store import (
    read_private_json,
    verify_raw_object,
    write_private_json,
)


SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
STATE_VERSION = "2026-10-02.v1"


class KRXHistoricalBatchStateError(ValueError):
    pass


def _sha256(value: Any) -> str:
    payload = json.dumps(
        value,
        sort_keys=True,
        ensure_ascii=False,
        separators=(",", ":"),
        default=str,
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _require_sha(value: Any, field: str) -> str:
    text = str(value or "").strip().lower()
    if not SHA256_RE.fullmatch(text):
        raise KRXHistoricalBatchStateError(f"{field} must be SHA-256")
    return text


def _state_relpath(phase: str) -> str:
    if phase not in PHASE_ORDER:
        raise KRXHistoricalBatchStateError(f"unknown phase: {phase}")
    return f"batch_state/{phase}.json"


def _task_ids(tasks: Iterable[Mapping[str, Any]], phase: str) -> list[str]:
    ids = []
    for row in tasks:
        if str(row.get("phase") or "") != phase:
            raise KRXHistoricalBatchStateError("task phase mismatch")
        ids.append(_require_sha(row.get("task_id"), "task_id"))
    if not ids:
        raise KRXHistoricalBatchStateError("phase task set is empty")
    if len(ids) != len(set(ids)):
        raise KRXHistoricalBatchStateError("duplicate task_id in phase")
    return sorted(ids)


def initialize_phase_state(
    *,
    root: str,
    phase: str,
    tasks: Iterable[Mapping[str, Any]],
    git_worktree: str | None = None,
) -> dict[str, Any]:
    """Initialize or verify one frozen phase task set."""
    ids = _task_ids(tasks, phase)
    task_set_fp = _sha256(ids)
    rel = _state_relpath(phase)

    try:
        existing = read_private_json(
            root, rel, git_worktree=git_worktree
        )["value"]
    except Exception as exc:
        if "missing" not in str(exc).lower():
            raise
        existing = None

    if existing is not None:
        if existing.get("plan_id") != PLAN_ID:
            raise KRXHistoricalBatchStateError("existing phase plan_id drift")
        if existing.get("execution_contract_id") != EXECUTION_CONTRACT_ID:
            raise KRXHistoricalBatchStateError("existing phase execution contract drift")
        if existing.get("phase") != phase:
            raise KRXHistoricalBatchStateError("existing phase name drift")
        if existing.get("task_set_fingerprint_sha256") != task_set_fp:
            raise KRXHistoricalBatchStateError(
                "phase task set changed after initialization"
            )
        if int(existing.get("expected_task_count", -1)) != len(ids):
            raise KRXHistoricalBatchStateError("phase expected task count drift")
        return dict(existing)

    state = {
        "state_version": STATE_VERSION,
        "plan_id": PLAN_ID,
        "execution_contract_id": EXECUTION_CONTRACT_ID,
        "phase": phase,
        "status": "PENDING",
        "expected_task_count": len(ids),
        "task_set_fingerprint_sha256": task_set_fp,
        "expected_task_ids_sha256": ids,
        "completed": {},
        "completed_task_count": 0,
        "failed_task_count": 0,
        "phase_complete": False,
        "source_gate_c_closed": False,
        "source_gate_d_closed": False,
        "source_gate_e_closed": False,
        "feature_performance_testing_authorized": False,
        "sealed_holdout_authorized": False,
        "live_trading_authorized": False,
    }
    write_private_json(root, rel, state, git_worktree=git_worktree)
    return state


def record_task_completion(
    *,
    root: str,
    phase: str,
    task_id: str,
    worker_result: Mapping[str, Any],
    git_worktree: str | None = None,
) -> dict[str, Any]:
    """Record one verified worker completion idempotently."""
    tid = _require_sha(task_id, "task_id")
    rel = _state_relpath(phase)
    state = read_private_json(root, rel, git_worktree=git_worktree)["value"]

    if state.get("plan_id") != PLAN_ID:
        raise KRXHistoricalBatchStateError("phase plan_id drift")
    if state.get("execution_contract_id") != EXECUTION_CONTRACT_ID:
        raise KRXHistoricalBatchStateError("phase execution contract drift")
    if state.get("phase") != phase:
        raise KRXHistoricalBatchStateError("phase name drift")

    expected = set(state.get("expected_task_ids_sha256") or [])
    if tid not in expected:
        raise KRXHistoricalBatchStateError("completion task_id was not preregistered")

    if worker_result.get("completed") is not True:
        raise KRXHistoricalBatchStateError("worker_result is not completed")
    raw_sha = _require_sha(worker_result.get("raw_object_sha256"), "raw_object_sha256")
    receipt_fp = _require_sha(
        worker_result.get("receipt_fingerprint_sha256"),
        "receipt_fingerprint_sha256",
    )
    request_sha = _require_sha(
        worker_result.get("request_metadata_sha256"),
        "request_metadata_sha256",
    )
    size = int(worker_result.get("raw_bytes_size", -1))
    if size < 0:
        raise KRXHistoricalBatchStateError("raw_bytes_size invalid")
    rows = int(worker_result.get("response_rows", -1))
    if rows < 0:
        raise KRXHistoricalBatchStateError("response_rows invalid")
    if worker_result.get("raw_rows_emitted") is not False:
        raise KRXHistoricalBatchStateError("worker result exposed raw rows")
    for key in (
        "feature_performance_testing_authorized",
        "sealed_holdout_authorized",
        "live_trading_authorized",
    ):
        if worker_result.get(key) is not False:
            raise KRXHistoricalBatchStateError(f"{key} illegally true")

    verify_raw_object(
        root,
        raw_sha,
        expected_size=size,
        git_worktree=git_worktree,
    )

    entry = {
        "task_id": tid,
        "request_metadata_sha256": request_sha,
        "raw_object_sha256": raw_sha,
        "raw_bytes_size": size,
        "response_rows": rows,
        "response_schema_sha256": _require_sha(
            worker_result.get("response_schema_sha256"),
            "response_schema_sha256",
        ),
        "response_payload_sha256": _require_sha(
            worker_result.get("response_payload_sha256"),
            "response_payload_sha256",
        ),
        "receipt_fingerprint_sha256": receipt_fp,
    }

    completed = dict(state.get("completed") or {})
    if tid in completed and completed[tid] != entry:
        raise KRXHistoricalBatchStateError(
            "same task_id produced conflicting completion metadata"
        )
    completed[tid] = entry

    state["completed"] = completed
    state["completed_task_count"] = len(completed)
    state["phase_complete"] = len(completed) == int(state["expected_task_count"])
    state["status"] = "COMPLETE" if state["phase_complete"] else "IN_PROGRESS"

    # Completing a request phase is provenance progress only. It never closes
    # source gates or authorizes research/holdout/live paths by itself.
    state["source_gate_c_closed"] = False
    state["source_gate_d_closed"] = False
    state["source_gate_e_closed"] = False
    state["feature_performance_testing_authorized"] = False
    state["sealed_holdout_authorized"] = False
    state["live_trading_authorized"] = False

    write_private_json(root, rel, state, git_worktree=git_worktree)
    return dict(state)


def require_phase_complete(
    *,
    root: str,
    phase: str,
    git_worktree: str | None = None,
) -> dict[str, Any]:
    state = read_private_json(
        root, _state_relpath(phase), git_worktree=git_worktree
    )["value"]
    if state.get("phase_complete") is not True or state.get("status") != "COMPLETE":
        raise KRXHistoricalBatchStateError(f"phase {phase} is not complete")
    if int(state.get("completed_task_count", -1)) != int(
        state.get("expected_task_count", -2)
    ):
        raise KRXHistoricalBatchStateError("phase completion count mismatch")
    return dict(state)


def public_phase_summary(state: Mapping[str, Any]) -> dict[str, Any]:
    """Return only public-safe counts/fingerprints; no task IDs."""
    return {
        "plan_id": state.get("plan_id"),
        "execution_contract_id": state.get("execution_contract_id"),
        "phase": state.get("phase"),
        "status": state.get("status"),
        "expected_task_count": int(state.get("expected_task_count", 0)),
        "completed_task_count": int(state.get("completed_task_count", 0)),
        "failed_task_count": int(state.get("failed_task_count", 0)),
        "task_set_fingerprint_sha256": state.get("task_set_fingerprint_sha256"),
        "phase_complete": bool(state.get("phase_complete", False)),
        "security_identifiers_emitted": False,
        "raw_rows_emitted": False,
        "source_gate_c_closed": False,
        "source_gate_d_closed": False,
        "source_gate_e_closed": False,
        "feature_performance_testing_authorized": False,
        "sealed_holdout_authorized": False,
        "live_trading_authorized": False,
    }
