import hashlib
from pathlib import Path

import pytest

from research_v1_krx_historical_batch_state import (
    KRXHistoricalBatchStateError,
    initialize_phase_state,
    public_phase_summary,
    record_task_completion,
    require_phase_complete,
)
from research_v1_krx_private_store import write_raw_object


def _task(phase: str, seed: str) -> dict:
    tid = hashlib.sha256(seed.encode()).hexdigest()
    return {"phase": phase, "task_id": tid}


def _worker_result(root: Path, payload: bytes, seed: str) -> dict:
    raw = write_raw_object(root, payload)
    h = lambda x: hashlib.sha256(x.encode()).hexdigest()
    return {
        "completed": True,
        "request_metadata_sha256": h(seed + "-request"),
        "raw_object_sha256": raw["raw_object_sha256"],
        "raw_bytes_size": raw["raw_bytes_size"],
        "response_rows": 1,
        "response_schema_sha256": h(seed + "-schema"),
        "response_payload_sha256": h(seed + "-payload"),
        "receipt_fingerprint_sha256": h(seed + "-receipt"),
        "raw_rows_emitted": False,
        "feature_performance_testing_authorized": False,
        "sealed_holdout_authorized": False,
        "live_trading_authorized": False,
    }


def test_one_request_never_means_phase_complete(tmp_path):
    root = (tmp_path / "private").resolve()
    tasks = [_task("IDENTITY_SEED", "a"), _task("IDENTITY_SEED", "b")]
    state = initialize_phase_state(root=str(root), phase="IDENTITY_SEED", tasks=tasks)
    assert state["expected_task_count"] == 2
    assert state["phase_complete"] is False

    first = record_task_completion(
        root=str(root),
        phase="IDENTITY_SEED",
        task_id=tasks[0]["task_id"],
        worker_result=_worker_result(root, b"one", "a"),
    )
    assert first["status"] == "IN_PROGRESS"
    assert first["completed_task_count"] == 1
    assert first["phase_complete"] is False
    assert first["source_gate_c_closed"] is False
    assert first["source_gate_d_closed"] is False
    assert first["source_gate_e_closed"] is False
    with pytest.raises(KRXHistoricalBatchStateError, match="not complete"):
        require_phase_complete(root=str(root), phase="IDENTITY_SEED")


def test_phase_completes_only_after_all_preregistered_tasks(tmp_path):
    root = (tmp_path / "private").resolve()
    tasks = [_task("IDENTITY_SEED", "a"), _task("IDENTITY_SEED", "b")]
    initialize_phase_state(root=str(root), phase="IDENTITY_SEED", tasks=tasks)
    for idx, task in enumerate(tasks):
        state = record_task_completion(
            root=str(root),
            phase="IDENTITY_SEED",
            task_id=task["task_id"],
            worker_result=_worker_result(root, f"raw-{idx}".encode(), str(idx)),
        )
    assert state["status"] == "COMPLETE"
    assert state["completed_task_count"] == 2
    assert state["phase_complete"] is True
    checked = require_phase_complete(root=str(root), phase="IDENTITY_SEED")
    assert checked["source_gate_c_closed"] is False
    assert checked["source_gate_d_closed"] is False
    assert checked["source_gate_e_closed"] is False
    assert checked["feature_performance_testing_authorized"] is False
    assert checked["sealed_holdout_authorized"] is False
    assert checked["live_trading_authorized"] is False


def test_next_phase_cannot_initialize_before_predecessor_complete(tmp_path):
    root = (tmp_path / "private").resolve()
    seed = [_task("IDENTITY_SEED", "seed")]
    initialize_phase_state(root=str(root), phase="IDENTITY_SEED", tasks=seed)

    binding = [_task("IDENTITY_STANDARD_CODE_BINDING", "binding")]
    with pytest.raises(KRXHistoricalBatchStateError, match="prior phase IDENTITY_SEED is not complete"):
        initialize_phase_state(
            root=str(root),
            phase="IDENTITY_STANDARD_CODE_BINDING",
            tasks=binding,
        )

    record_task_completion(
        root=str(root),
        phase="IDENTITY_SEED",
        task_id=seed[0]["task_id"],
        worker_result=_worker_result(root, b"seed", "seed"),
    )
    state = initialize_phase_state(
        root=str(root),
        phase="IDENTITY_STANDARD_CODE_BINDING",
        tasks=binding,
    )
    assert state["phase"] == "IDENTITY_STANDARD_CODE_BINDING"
    assert state["phase_complete"] is False


def test_unknown_or_conflicting_completion_fails_closed(tmp_path):
    root = (tmp_path / "private").resolve()
    tasks = [_task("IDENTITY_SEED", "a")]
    initialize_phase_state(root=str(root), phase="IDENTITY_SEED", tasks=tasks)

    with pytest.raises(KRXHistoricalBatchStateError, match="not preregistered"):
        record_task_completion(
            root=str(root),
            phase="IDENTITY_SEED",
            task_id=hashlib.sha256(b"unknown").hexdigest(),
            worker_result=_worker_result(root, b"x", "x"),
        )

    result = _worker_result(root, b"one", "same")
    record_task_completion(
        root=str(root),
        phase="IDENTITY_SEED",
        task_id=tasks[0]["task_id"],
        worker_result=result,
    )
    changed = dict(result)
    changed["response_rows"] = 2
    with pytest.raises(KRXHistoricalBatchStateError, match="conflicting completion metadata"):
        record_task_completion(
            root=str(root),
            phase="IDENTITY_SEED",
            task_id=tasks[0]["task_id"],
            worker_result=changed,
        )


def test_phase_task_set_cannot_change_after_initialization(tmp_path):
    root = (tmp_path / "private").resolve()
    initialize_phase_state(
        root=str(root),
        phase="IDENTITY_SEED",
        tasks=[_task("IDENTITY_SEED", "a")],
    )
    with pytest.raises(KRXHistoricalBatchStateError, match="task set changed"):
        initialize_phase_state(
            root=str(root),
            phase="IDENTITY_SEED",
            tasks=[_task("IDENTITY_SEED", "b")],
        )


def test_public_summary_exposes_counts_and_hashes_only(tmp_path):
    root = (tmp_path / "private").resolve()
    tasks = [_task("IDENTITY_SEED", "secret-security-identifier")]
    state = initialize_phase_state(root=str(root), phase="IDENTITY_SEED", tasks=tasks)
    out = public_phase_summary(state)
    assert out["expected_task_count"] == 1
    assert out["completed_task_count"] == 0
    assert out["security_identifiers_emitted"] is False
    assert out["raw_rows_emitted"] is False
    assert "expected_task_ids_sha256" not in out
    assert tasks[0]["task_id"] not in str(out)
    assert out["source_gate_c_closed"] is False
    assert out["source_gate_d_closed"] is False
    assert out["source_gate_e_closed"] is False
