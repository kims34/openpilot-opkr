"""Checkpointed batch runner for independent KRX expected-scope attestation.

No network request can occur unless the separate expected-scope consent preflight
passes. The runner resumes only after verifying the private date scope, request
receipts and referenced content-addressed raw objects.

Public output contains counts/fingerprints only; expected security keys remain
inside the validated private root.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Callable, Mapping

from research_v1_krx_expected_scope_attestation import (
    CONTRACT_ID,
    build_calendar_discovery_plan,
)
from research_v1_krx_expected_scope_executor import (
    execute_expected_scope_date,
)
from research_v1_krx_acquisition_receipt import dataframe_payload_fingerprint, schema_fingerprint
from research_v1_krx_historical_fetchers import parse_openapi_raw
from research_v1_krx_expected_scope_materializer import materialize_one_date
from research_v1_krx_expected_scope_preflight import (
    evaluate_expected_scope_preflight,
)
from research_v1_krx_private_store import (
    read_private_json,
    read_raw_object,
    verify_raw_object,
    write_private_json,
)


CHECKPOINT_REL = "expected_scope/batch_state-v1.json"
STATE_VERSION = "2026-10-02.expected-scope-batch-v1"


class KRXExpectedScopeBatchError(RuntimeError):
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


def _task_fingerprint(tasks: list[Mapping[str, Any]]) -> str:
    return _sha256([str(x["task_id"]) for x in tasks])


def _load_or_init_state(
    *,
    root: str,
    git_worktree: str,
    tasks: list[Mapping[str, Any]],
) -> dict[str, Any]:
    expected_fp = _task_fingerprint(tasks)
    try:
        wrapped = read_private_json(
            root,
            CHECKPOINT_REL,
            git_worktree=git_worktree,
        )
        state = dict(wrapped["value"])
    except Exception as exc:
        if "missing" not in str(exc).lower():
            raise
        state = {
            "state_version": STATE_VERSION,
            "contract_id": CONTRACT_ID,
            "expected_task_count": len(tasks),
            "task_set_fingerprint_sha256": expected_fp,
            "completed": {},
            "completed_task_count": 0,
            "status": "PENDING",
            "batch_complete": False,
            "network_request_attempted": False,
            "source_gate_c_closed": False,
            "source_gate_d_closed": False,
            "source_gate_e_closed": False,
            "feature_performance_testing_authorized": False,
            "sealed_holdout_authorized": False,
            "live_trading_authorized": False,
        }
        write_private_json(
            root,
            CHECKPOINT_REL,
            state,
            git_worktree=git_worktree,
        )
        return state

    if state.get("state_version") != STATE_VERSION:
        raise KRXExpectedScopeBatchError("checkpoint state_version drift")
    if state.get("contract_id") != CONTRACT_ID:
        raise KRXExpectedScopeBatchError("checkpoint contract_id drift")
    if type(state.get("expected_task_count")) is not int or state["expected_task_count"] != len(tasks):
        raise KRXExpectedScopeBatchError("checkpoint task-count drift")
    if state.get("task_set_fingerprint_sha256") != expected_fp:
        raise KRXExpectedScopeBatchError("checkpoint task-set fingerprint drift")
    if not isinstance(state.get("completed"), Mapping):
        raise KRXExpectedScopeBatchError("checkpoint completed map invalid")
    completed = state["completed"]
    expected_dates = {str(task["request"]["params"]["basDd"]) for task in tasks}
    if any(not isinstance(day, str) or day not in expected_dates for day in completed):
        raise KRXExpectedScopeBatchError("checkpoint completed date outside frozen task set")
    if any(not isinstance(value, Mapping) for value in completed.values()):
        raise KRXExpectedScopeBatchError("checkpoint completion entry must be a mapping")
    if type(state.get("completed_task_count")) is not int or state["completed_task_count"] != len(completed):
        raise KRXExpectedScopeBatchError("checkpoint completed count does not match completed map")
    complete = len(completed) == len(tasks)
    if state.get("batch_complete") is not complete:
        raise KRXExpectedScopeBatchError("checkpoint completion flag does not match completed map")
    expected_status = "COMPLETE" if complete else ("IN_PROGRESS" if completed else "PENDING")
    if state.get("status") != expected_status:
        raise KRXExpectedScopeBatchError("checkpoint status does not match completed map")
    for field in ("source_gate_c_closed", "source_gate_d_closed", "source_gate_e_closed",
                  "feature_performance_testing_authorized", "sealed_holdout_authorized",
                  "live_trading_authorized"):
        if state.get(field) is not False:
            raise KRXExpectedScopeBatchError(f"checkpoint illegally claims authority: {field}")
    return state


def _verify_receipt(
    *,
    root: str,
    relpath: str,
    requested_date: str,
    dataset_identifier: str,
    git_worktree: str,
) -> dict[str, Any]:
    wrapped = read_private_json(
        root,
        relpath,
        git_worktree=git_worktree,
    )
    receipt = wrapped["value"]
    if receipt.get("contract_id") != CONTRACT_ID:
        raise KRXExpectedScopeBatchError("receipt contract drift")
    if receipt.get("requested_date") != requested_date:
        raise KRXExpectedScopeBatchError("receipt date drift")
    if receipt.get("dataset_identifier") != dataset_identifier:
        raise KRXExpectedScopeBatchError("receipt dataset drift")
    if type(receipt.get("raw_bytes_size")) is not int or receipt["raw_bytes_size"] < 0:
        raise KRXExpectedScopeBatchError("receipt raw byte count must be a non-negative integer")
    raw = read_raw_object(
        root, str(receipt.get("raw_object_sha256") or ""),
        expected_size=receipt["raw_bytes_size"], git_worktree=git_worktree,
    )
    frame = parse_openapi_raw(raw)
    if type(receipt.get("response_rows")) is not int or receipt["response_rows"] != len(frame):
        raise KRXExpectedScopeBatchError("receipt row count does not match verified raw response")
    if receipt.get("response_payload_sha256") != dataframe_payload_fingerprint(frame):
        raise KRXExpectedScopeBatchError("receipt payload does not match verified raw response")
    if receipt.get("response_schema_sha256") != schema_fingerprint(list(frame.columns), [str(x) for x in frame.dtypes]):
        raise KRXExpectedScopeBatchError("receipt schema does not match verified raw response")
    return {
        "metadata_sha256": wrapped["metadata_sha256"],
        "raw_object_sha256": receipt["raw_object_sha256"],
        "response_rows": receipt["response_rows"],
        "response_frame": frame,
    }


def _verify_completed_date(
    *,
    root: str,
    requested_date: str,
    completion: Mapping[str, Any],
    git_worktree: str,
) -> dict[str, Any]:
    scope_rel = str(completion.get("private_scope_relpath") or "")
    expected_prefix = f"expected_scope/dates/{requested_date}/"
    if not scope_rel.startswith(expected_prefix) or not scope_rel.endswith(".json"):
        raise KRXExpectedScopeBatchError("private scope relpath drift")
    scope_name = Path(scope_rel).name
    scope_digest = scope_name[:-5]
    if len(scope_digest) != 64 or any(ch not in "0123456789abcdef" for ch in scope_digest):
        raise KRXExpectedScopeBatchError("private scope content-address drift")
    wrapped = read_private_json(
        root,
        scope_rel,
        git_worktree=git_worktree,
    )
    if wrapped["metadata_sha256"] != completion.get(
        "private_scope_metadata_sha256"
    ):
        raise KRXExpectedScopeBatchError("private scope metadata checksum drift")

    scope = wrapped["value"]
    if scope.get("contract_id") != CONTRACT_ID:
        raise KRXExpectedScopeBatchError("private scope contract drift")
    if scope.get("requested_date") != requested_date:
        raise KRXExpectedScopeBatchError("private scope date drift")

    daily_rel = str(scope.get("daily_receipt_relpath") or "")
    if not daily_rel:
        raise KRXExpectedScopeBatchError("daily receipt missing")
    daily = _verify_receipt(
        root=root,
        relpath=daily_rel,
        requested_date=requested_date,
        dataset_identifier="stk_bydd_trd",
        git_worktree=git_worktree,
    )

    master_rel = scope.get("master_receipt_relpath")
    master = None
    if master_rel:
        master = _verify_receipt(
            root=root,
            relpath=str(master_rel),
            requested_date=requested_date,
            dataset_identifier="stk_isu_base_info",
            git_worktree=git_worktree,
        )
    elif scope.get("official_trading_date_observed") is True:
        raise KRXExpectedScopeBatchError(
            "trading date completion missing same-date master receipt"
        )

    if _sha256(scope) != scope_digest:
        raise KRXExpectedScopeBatchError("private scope content-address checksum drift")
    reconstructed = materialize_one_date(
        requested_date=requested_date, daily_trade=daily["response_frame"],
        security_master=None if master is None else master["response_frame"],
    )
    if scope.get("official_trading_date_observed") is not reconstructed["official_trading_date_observed"]:
        raise KRXExpectedScopeBatchError("private scope trading-date flag differs from verified raw response")
    for key in ("investor_expected_scope", "status_expected_scope"):
        expected_records = reconstructed[key].to_dict(orient="records")
        if not isinstance(scope.get(key), list) or scope[key] != expected_records:
            raise KRXExpectedScopeBatchError("private scope keys differ from verified raw responses")
    return {
        "requested_date": requested_date,
        "official_trading_date_observed": reconstructed["official_trading_date_observed"],
        "daily_receipt_metadata_sha256": daily["metadata_sha256"],
        "master_receipt_metadata_sha256": (
            None if master is None else master["metadata_sha256"]
        ),
    }


def execute_expected_scope_batch(
    *,
    environment: Mapping[str, str],
    git_worktree: str,
    fetcher=None,
    evaluation_time=None,
    max_new_dates: int | None = None,
) -> dict[str, Any]:
    """Execute or resume the frozen 4,127-date attestation sweep.

    max_new_dates is an operational pause limit. It never changes the frozen task
    set or completion criteria.
    """
    preflight = evaluate_expected_scope_preflight(
        environment=environment,
        git_worktree=git_worktree,
    )
    if not preflight["expected_scope_network_execution_authorized"]:
        raise KRXExpectedScopeBatchError(
            "expected-scope preflight blocked: "
            + ",".join(preflight["missing_requirements"])
        )

    if max_new_dates is not None:
        max_new_dates = int(max_new_dates)
        if max_new_dates < 0:
            raise KRXExpectedScopeBatchError("max_new_dates must be >= 0")

    tasks = build_calendar_discovery_plan()
    root = str(environment["KRX_PRIVATE_RAW_DIR"])
    state = _load_or_init_state(
        root=root,
        git_worktree=git_worktree,
        tasks=tasks,
    )
    completed = dict(state.get("completed") or {})
    # Verify every stored completion before fetching any missing date, including
    # completions beyond a gap that an operational pause would otherwise skip.
    verified_completed = {
        day: _verify_completed_date(
            root=root, requested_date=day, completion=completion,
            git_worktree=git_worktree,
        )
        for day, completion in completed.items()
    }

    resumed_count = 0
    executed_count = 0
    trading_date_count = 0
    for task in tasks:
        day = str(task["request"]["params"]["basDd"])
        if day in completed:
            verified = verified_completed[day]
            resumed_count += 1
            trading_date_count += int(
                verified["official_trading_date_observed"]
            )
            continue

        if max_new_dates is not None and executed_count >= max_new_dates:
            break

        kwargs = {
            "requested_date": day,
            "environment": environment,
            "git_worktree": git_worktree,
            "evaluation_time": evaluation_time,
        }
        if fetcher is not None:
            kwargs["fetcher"] = fetcher
        result = execute_expected_scope_date(**kwargs)
        if result.get("network_request_attempted") is not True:
            raise KRXExpectedScopeBatchError(
                "date executor did not report network request"
            )
        if result.get("source_gate_c_closed") is not False:
            raise KRXExpectedScopeBatchError(
                "date executor illegally closed Gate C"
            )

        completion = {
            "private_scope_relpath": result["private_scope_relpath"],
            "private_scope_metadata_sha256": result[
                "private_scope_metadata_sha256"
            ],
            "official_trading_date_observed": bool(
                result["official_trading_date_observed"]
            ),
            "investor_expected_key_count": int(
                result["investor_expected_key_count"]
            ),
            "status_expected_key_count": int(
                result["status_expected_key_count"]
            ),
        }
        _verify_completed_date(
            root=root,
            requested_date=day,
            completion=completion,
            git_worktree=git_worktree,
        )
        completed[day] = completion
        executed_count += 1
        trading_date_count += int(
            completion["official_trading_date_observed"]
        )

        state["completed"] = completed
        state["completed_task_count"] = len(completed)
        state["status"] = (
            "COMPLETE" if len(completed) == len(tasks) else "IN_PROGRESS"
        )
        state["batch_complete"] = len(completed) == len(tasks)
        state["network_request_attempted"] = True
        state["source_gate_c_closed"] = False
        state["source_gate_d_closed"] = False
        state["source_gate_e_closed"] = False
        state["feature_performance_testing_authorized"] = False
        state["sealed_holdout_authorized"] = False
        state["live_trading_authorized"] = False
        write_private_json(
            root,
            CHECKPOINT_REL,
            state,
            git_worktree=git_worktree,
        )

    final_state = _load_or_init_state(
        root=root,
        git_worktree=git_worktree,
        tasks=tasks,
    )
    return {
        "mode": "EXECUTE_EXPECTED_SCOPE_BATCH",
        "contract_id": CONTRACT_ID,
        "expected_task_count": len(tasks),
        "completed_task_count": int(
            final_state.get("completed_task_count", 0)
        ),
        "resumed_date_count": resumed_count,
        "newly_executed_date_count": executed_count,
        "batch_complete": bool(final_state.get("batch_complete", False)),
        "status": final_state.get("status"),
        "task_set_fingerprint_sha256": final_state[
            "task_set_fingerprint_sha256"
        ],
        "network_request_attempted": executed_count > 0,
        "raw_rows_emitted": False,
        "security_identifiers_emitted": False,
        "source_gate_c_closed": False,
        "source_gate_d_closed": False,
        "source_gate_e_closed": False,
        "feature_performance_testing_authorized": False,
        "sealed_holdout_authorized": False,
        "live_trading_authorized": False,
    }
