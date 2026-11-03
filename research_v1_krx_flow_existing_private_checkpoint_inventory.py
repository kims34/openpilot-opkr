"""Network-free, public-safe inventory of *existing* private KRX checkpoints.

Consumes in-memory manifest/state objects supplied ONLY from the existing
dedicated private worker. Does not authenticate the caller, read files, parse
KRX numeric market rows, make KRX/broker requests, or authorize resumption.

The manifest contains private issuer identifiers; never log or publish it.
Output contains coarse counts only. Even 2022 nonempty completed checkpoints
are retrieval-vintage data, NOT evidence of as-published 2022 PIT.
"""
from __future__ import annotations

from collections import Counter
from datetime import datetime
import hashlib
import json
import re
from typing import Any, Mapping

PHASE = "PER_SECURITY_HISTORY"
PLAN = "INDEXALERT-KRX-HIST-ACQ-v3"
EXECUTION = "INDEXALERT-KRX-HIST-EXEC-v3"
FROZEN_COUNT = 14296
FROZEN_FLOW_COUNT = 9485
FROZEN_HALT_COUNT = 4811
FROZEN_TASK_SET_SHA256 = (
    "fb5b883c6fe0e9c15e88aea9bdf874ddd7a11ae8a009c2ddf91c4e4249a8ba38"
)
FROZEN_PRIVATE_MANIFEST_METADATA_SHA256 = (
    "0d98f45168cedeecc013e95c71abe661ca1fac9df0403ba477d2f5653572c116"
)
HEX64 = re.compile(r"^[0-9a-f]{64}$")
ID12 = re.compile(r"^[0-9A-Z]{12}$")
DATE8 = re.compile(r"^[0-9]{8}$")
KIND_SOURCE = {
    "investor_trading_individual_daily": "KRX_INVESTOR_FLOW",
    "trading_halt": "KRX_SECURITY_STATUS",
}


class KRXExistingFlowInventoryError(ValueError):
    """All failures are static codes: never include confidential task inputs."""


def _require(condition: bool, code: str) -> None:
    if not condition:
        raise KRXExistingFlowInventoryError(code)


def _sha(value: Any) -> str:
    raw = json.dumps(
        value, ensure_ascii=False, sort_keys=True,
        separators=(",", ":"), default=str,
    ).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _digest(value: Any) -> bool:
    return type(value) is str and HEX64.fullmatch(value) is not None


def _date(value: Any) -> datetime:
    _require(type(value) is str and DATE8.fullmatch(value) is not None,
             "INVALID_PRIVATE_DATE")
    try:
        date = datetime.strptime(value, "%Y%m%d")
    except ValueError:
        raise KRXExistingFlowInventoryError("INVALID_PRIVATE_DATE") from None
    _require(date.strftime("%Y%m%d") == value, "INVALID_PRIVATE_DATE")
    return date


def summarise_existing_flow_checkpoints(
    manifest: Mapping[str, Any],
    phase_state: Mapping[str, Any],
    *,
    expected_by_kind: Mapping[str, int],
    expected_task_fingerprint_sha256: str,
) -> dict[str, Any]:
    """Audit internal consistency, but never claim original KRX authenticity.

    This is a **per-type inventory**, not a data-source PIT validator. Task IDs
    are recomputed using the pinned KRX orchestration format to detect edits,
    and completion metadata are checked against that *declared* manifest.
    The actual private original response bytes must still be independently
    re-hashed from the approved private volume by the KRX source owner.
    """
    _require(isinstance(manifest, Mapping) and isinstance(phase_state, Mapping),
             "PRIVATE_INPUT_OBJECT_REQUIRED")
    _require(manifest.get("plan_id") == PLAN
             and phase_state.get("plan_id") == PLAN
             and manifest.get("execution_contract_id") == EXECUTION
             and phase_state.get("execution_contract_id") == EXECUTION,
             "FROZEN_PLAN_DRIFT")
    _require(manifest.get("phase") == PHASE and phase_state.get("phase") == PHASE,
             "PHASE_DRIFT")
    _require(_digest(expected_task_fingerprint_sha256),
             "EXPECTED_TASK_FINGERPRINT_INVALID")
    tasks = manifest.get("tasks")
    _require(type(tasks) is list and bool(tasks), "PRIVATE_TASKS_MISSING")
    _require(type(manifest.get("task_count")) is int
             and manifest["task_count"] == len(tasks), "MANIFEST_TASK_COUNT_DRIFT")
    task_kind = {}
    by_kind = Counter()
    flow_2022_tasks = set()
    for task in tasks:
        _require(isinstance(task, Mapping), "INVALID_PRIVATE_TASK")
        _require(task.get("phase") == PHASE
                 and task.get("plan_id") == PLAN
                 and task.get("execution_contract_id") == EXECUTION
                 and task.get("contains_security_identifier") is True,
                 "UNPINNED_PRIVATE_TASK")
        task_id = task.get("task_id")
        _require(_digest(task_id), "INVALID_TASK_ID")
        signed_fields = {k: v for k, v in task.items() if k != "task_id"}
        _require(_sha(signed_fields) == task_id, "TASK_CONTENT_FINGERPRINT_DRIFT")
        _require(task_id not in task_kind, "DUPLICATE_PRIVATE_TASK")
        spec = task.get("request_spec")
        _require(isinstance(spec, Mapping), "REQUEST_SPEC_MISSING")
        kind = spec.get("kind")
        _require(type(kind) is str and kind in KIND_SOURCE
                 and task.get("source_family") == KIND_SOURCE[kind],
                 "UNSUPPORTED_DATASET_FAMILY")
        params = spec.get("params")
        _require(isinstance(params, Mapping), "REQUEST_PARAMS_MISSING")
        _require(type(params.get("isuCd")) is str
                 and ID12.fullmatch(params["isuCd"]) is not None,
                 "PRIVATE_ISSUE_FORMAT_DRIFT")
        start = _date(params.get("strtDd"))
        end = _date(params.get("endDd"))
        _require(start <= end, "REVERSED_PRIVATE_REQUEST_PERIOD")
        # The historical task set is partitioned into issuer/year-bounded
        # investor windows; other statuses legitimately span multiple years.
        if kind == "investor_trading_individual_daily":
            _require(start.year == end.year, "FLOW_YEAR_WINDOW_DRIFT")
            _require(set(params) == {"isuCd", "strtDd", "endDd"},
                     "FLOW_REQUEST_PARAMS_DRIFT")
            if start.year == 2022:
                flow_2022_tasks.add(task_id)
        else:
            _require(set(params) == {"isuCd", "isuCd2", "strtDd", "endDd"}
                     and isinstance(params["isuCd2"], str)
                     and re.fullmatch(r"[0-9A-Z]{6}", params["isuCd2"]) is not None,
                     "HALT_REQUEST_PARAMS_DRIFT")
        task_kind[task_id] = kind
        by_kind[kind] += 1

    expected = dict(expected_by_kind)
    _require(set(expected) == set(KIND_SOURCE)
             and all(type(v) is int and v >= 0 for v in expected.values()),
             "EXPECTED_TASK_TYPE_COUNTS_INVALID")
    _require(dict(by_kind) == expected, "FROZEN_TASK_MIX_DRIFT")
    ids = sorted(task_kind)
    expected_fp = _sha(ids)
    _require(expected_fp == expected_task_fingerprint_sha256
             and manifest.get("task_set_fingerprint_sha256") == expected_fp
             and phase_state.get("task_set_fingerprint_sha256") == expected_fp,
             "PRIVATE_TASK_SET_FINGERPRINT_DRIFT")
    state_ids = phase_state.get("expected_task_ids_sha256")
    _require(type(state_ids) is list and state_ids == ids,
             "PRIVATE_EXPECTED_TASK_MEMBERSHIP_DRIFT")
    _require(type(phase_state.get("expected_task_count")) is int
             and phase_state["expected_task_count"] == len(ids),
             "PRIVATE_STATE_TASK_COUNT_DRIFT")
    completed = phase_state.get("completed")
    _require(isinstance(completed, Mapping), "PRIVATE_COMPLETION_MAP_MISSING")
    _require(type(phase_state.get("completed_task_count")) is int
             and phase_state["completed_task_count"] == len(completed),
             "PRIVATE_COMPLETION_COUNT_DRIFT")
    _require(type(phase_state.get("failed_task_count")) is int
             and phase_state["failed_task_count"] == 0,
             "PRIVATE_FAILED_TASKS_PRESENT")
    _require(set(completed).issubset(task_kind), "UNKNOWN_COMPLETED_TASK_ID")

    by_kind_completed = Counter()
    completed_2022 = 0
    nonempty_2022 = 0
    empty_2022 = 0
    # Original 2026-10-03 record_task_completion persisted exactly these
    # eight metadata fields, with no user-selectable extra authority keys.
    # A state-file writer that appends source/holdout/trading approval claims,
    # raw numeric rows or private paths has NOT produced an original checkpoint.
    original_completion_fields = {
        "task_id", "request_metadata_sha256", "raw_object_sha256",
        "raw_bytes_size", "response_rows", "response_schema_sha256",
        "response_payload_sha256", "receipt_fingerprint_sha256",
    }
    for task_id, record in completed.items():
        _require(isinstance(record, Mapping) and record.get("task_id") == task_id,
                 "INVALID_COMPLETION_RECEIPT")
        _require(set(record) == original_completion_fields,
                 "ORIGINAL_COMPLETION_FIELDS_DRIFT")
        for field in (
            "raw_object_sha256", "request_metadata_sha256",
            "response_schema_sha256", "response_payload_sha256",
            "receipt_fingerprint_sha256",
        ):
            _require(_digest(record.get(field)), "COMPLETION_DIGEST_MISSING")
        _require(type(record.get("response_rows")) is int
                 and record["response_rows"] >= 0
                 and type(record.get("raw_bytes_size")) is int
                 and record["raw_bytes_size"] >= 0,
                 "INVALID_COMPLETION_LENGTH")
        by_kind_completed[task_kind[task_id]] += 1
        if task_id in flow_2022_tasks:
            completed_2022 += 1
            nonempty_2022 += record["response_rows"] > 0
            empty_2022 += record["response_rows"] == 0

    total_done = len(completed)
    _require(phase_state.get("phase_complete") is (total_done == len(ids)),
             "PRIVATE_PHASE_COMPLETENESS_DRIFT")
    return {
        "evidence_class": "PRIVATE_CHECKPOINT_METADATA_COUNTS_ONLY",
        "frozen_task_count": len(ids),
        "completed_tasks": total_done,
        "remaining_tasks": len(ids) - total_done,
        "investor_flow_total_tasks": by_kind["investor_trading_individual_daily"],
        "investor_flow_completed_checkpoints": by_kind_completed["investor_trading_individual_daily"],
        "investor_flow_pending_checkpoints": (
            by_kind["investor_trading_individual_daily"]
            - by_kind_completed["investor_trading_individual_daily"]
        ),
        "trading_halt_completed_checkpoints": by_kind_completed["trading_halt"],
        "year_2022_flow_expected_tasks": len(flow_2022_tasks),
        "year_2022_flow_completed_checkpoints": completed_2022,
        "year_2022_flow_pending_checkpoints": len(flow_2022_tasks) - completed_2022,
        "year_2022_flow_nonempty_response_checkpoints": nonempty_2022,
        "year_2022_flow_empty_response_checkpoints": empty_2022,
        "private_raw_objects_reverified_in_this_function": False,
        "source_owner_private_manifest_storage_origin_verified": False,
        "independent_original_2022_publication_vintage_verified": False,
        "historical_issuer_universe_and_tradability_verified": False,
        "source_admitted": False,
        "performance_testing_authorized": False,
        "sealed_holdout_authorized": False,
        "ordering_enabled": False,
        "network_request_attempted": False,
        "raw_rows_or_identifiers_emitted": False,
    }



def _verify_original_execution_prefix(
    manifest: Mapping[str, Any],
    phase_state: Mapping[str, Any],
    *,
    expected_flow_count: int,
) -> dict[str, Any]:
    """Verify the actual original sequential execution prefix, in memory.

    Pinned 2026-10-03 planner sorts KRX_INVESTOR_FLOW before
    KRX_SECURITY_STATUS. Its one-shot entrypoint iterates tasks in order
    and records completion immediately after each successful request.
    A count alone can never prove this property; the PRIVATE completion
    ID set must equal the first N IDs from the pinned ordered manifest.
    """
    tasks = manifest["tasks"]
    _require(type(expected_flow_count) is int
             and 0 <= expected_flow_count <= len(tasks),
             "INVALID_EXPECTED_FLOW_PREFIX")
    _require(all(
        task["source_family"] == (
            "KRX_INVESTOR_FLOW" if index < expected_flow_count
            else "KRX_SECURITY_STATUS"
        ) for index, task in enumerate(tasks)
    ), "ORIGINAL_FLOW_FIRST_TASK_ORDER_DRIFT")
    completed = phase_state["completed"]
    actual_ids = set(completed)
    prefix_ids = {task["task_id"] for task in tasks[:len(completed)]}
    _require(actual_ids == prefix_ids, "NONCONTIGUOUS_ORIGINAL_EXECUTION_PREFIX")
    return {
        "original_flow_first_task_order_verified": True,
        "original_execution_completion_prefix_verified": True,
        "flow_completed_by_verified_prefix": min(len(completed), expected_flow_count),
        "flow_remaining_by_verified_prefix": (
            expected_flow_count - min(len(completed), expected_flow_count)
        ),
        "original_source_data_bytes_independently_verified": False,
        "original_2022_flow_vintage_verified": False,
    }


def summarise_frozen_2026_10_03_checkpoint_set(
    manifest: Mapping[str, Any], phase_state: Mapping[str, Any],
) -> dict[str, Any]:
    """Demand exact previously frozen task list; never trust self-claimed count."""
    result = summarise_existing_flow_checkpoints(
        manifest, phase_state,
        expected_by_kind={
            "investor_trading_individual_daily": FROZEN_FLOW_COUNT,
            "trading_halt": FROZEN_HALT_COUNT,
        },
        expected_task_fingerprint_sha256=FROZEN_TASK_SET_SHA256,
    )
    order = _verify_original_execution_prefix(
        manifest, phase_state, expected_flow_count=FROZEN_FLOW_COUNT,
    )
    _require(result["investor_flow_completed_checkpoints"]
             == order["flow_completed_by_verified_prefix"],
             "FLOW_PREFIX_COMPLETION_MISMATCH")
    result.update(order)
    return result
