from datetime import datetime, timezone
from pathlib import Path

import pytest

from research_v1_krx_historical_batch_state import (
    initialize_phase_state,
    record_task_completion,
)
from research_v1_krx_historical_worker_entrypoint import (
    STATUS_ECONOMICS_CONSENT_ENV,
    STATUS_ECONOMICS_CONSENT_SENTINEL,
    KRXHistoricalWorkerEntrypointError,
    execute_status_economics,
    load_frozen_status_economics_tasks,
    prepare_status_economics,
)
from research_v1_krx_private_store import write_raw_object, write_private_json


EVAL = datetime(2026, 10, 2, 11, 30, tzinfo=timezone.utc)


def _env(tmp_path, *, consent=False):
    env = {
        "KRX_ID": "present",
        "KRX_PW": "present",
        "KRX_AUTH_KEY": "present",
        "KRX_PRIVATE_RAW_DIR": str((tmp_path / "private").resolve()),
        "INDEXALERT_KRX_HIST_WORKER_ROLE": "DEDICATED_ONE_SHOT",
        "RAILWAY_SERVICE_NAME": "indexalert-krx-historical-worker",
    }
    if consent:
        env["KRX_HISTORICAL_ACQUISITION_CONSENT"] = (
            "I_AUTHORIZE_INDEXALERT_KRX_HIST_ACQ_v3"
        )
    return env


def _status_env(tmp_path):
    env = _env(tmp_path, consent=True)
    env[STATUS_ECONOMICS_CONSENT_ENV] = STATUS_ECONOMICS_CONSENT_SENTINEL
    return env


def _task(phase, char):
    return {
        "phase": phase,
        "task_id": char * 64,
        "source_family": "KRX_SECURITY_STATUS",
        "request_spec": {
            "kind": "delisted_stock_price" if phase == "STATUS_ECONOMICS" else "security_master",
            "params": {"isuCd": "KR7111110000"} if phase == "STATUS_ECONOMICS" else {"basDd": "20200102"},
        },
        "contains_security_identifier": phase == "STATUS_ECONOMICS",
    }


def _completion(root, worktree, payload):
    raw = write_raw_object(
        Path(root),
        payload,
        git_worktree=str(worktree),
    )
    return {
        "completed": True,
        "resumed": False,
        "network_request_attempted": True,
        "request_metadata_sha256": "1" * 64,
        "raw_object_sha256": raw["raw_object_sha256"],
        "raw_bytes_size": raw["raw_bytes_size"],
        "response_rows": 1,
        "retrieved_at": EVAL.isoformat(),
        "response_schema_sha256": "2" * 64,
        "response_payload_sha256": "3" * 64,
        "receipt_fingerprint_sha256": "4" * 64,
        "raw_rows_emitted": False,
        "feature_performance_testing_authorized": False,
        "sealed_holdout_authorized": False,
        "live_trading_authorized": False,
    }


def _complete_predecessors(tmp_path, worktree):
    root = str((tmp_path / "private").resolve())
    phases = [
        ("IDENTITY_SEED", "a"),
        ("IDENTITY_STANDARD_CODE_BINDING", "b"),
        ("PER_SECURITY_HISTORY", "c"),
    ]
    for idx, (phase, char) in enumerate(phases):
        task = _task(phase, char)
        initialize_phase_state(
            root=root,
            phase=phase,
            tasks=[task],
            git_worktree=str(worktree),
        )
        record_task_completion(
            root=root,
            phase=phase,
            task_id=task["task_id"],
            worker_result=_completion(
                root,
                worktree,
                f"{phase}-{idx}".encode(),
            ),
            git_worktree=str(worktree),
        )


def _status_task():
    return {
        "phase": "STATUS_ECONOMICS",
        "task_id": "d" * 64,
        "source_family": "KRX_SECURITY_STATUS",
        "request_spec": {
            "kind": "delisted_stock_price",
            "params": {
                "isuCd": "KR7111110000",
                "strtDd": "20240610",
                "endDd": "20240618",
            },
        },
        "contains_security_identifier": True,
    }


def _builder(*args, **kwargs):
    return [_status_task()], {
        "delisted_episode_count": 2,
        "cleanup_price_task_count": 1,
        "delisted_without_cleanup_interval_count": 1,
    }


def test_prepare_status_economics_is_network_free_and_never_exact_economics(tmp_path):
    worktree = (tmp_path / "repo").resolve()
    worktree.mkdir()
    _complete_predecessors(tmp_path, worktree)

    out = prepare_status_economics(
        environment=_env(tmp_path, consent=False),
        git_worktree=str(worktree),
        task_builder=_builder,
    )
    assert out["mode"] == "PREPARE_STATUS_ECONOMICS"
    assert out["task_count"] == 1
    assert out["network_request_attempted"] is False
    assert out["phase_complete"] is False
    assert out["exact_status_economics_ready"] is False
    assert out["source_gate_c_closed"] is False
    assert out["source_gate_d_closed"] is False
    assert out["source_gate_e_closed"] is False
    assert out["feature_performance_testing_authorized"] is False
    assert out["sealed_holdout_authorized"] is False
    assert out["live_trading_authorized"] is False
    assert "KR7111110000" not in str(out)


def test_execute_status_economics_blocks_without_bulk_consent(tmp_path):
    worktree = (tmp_path / "repo").resolve()
    worktree.mkdir()
    _complete_predecessors(tmp_path, worktree)
    prepare_status_economics(
        environment=_env(tmp_path, consent=False),
        git_worktree=str(worktree),
        task_builder=_builder,
    )
    calls = []
    with pytest.raises(KRXHistoricalWorkerEntrypointError, match="preflight blocked"):
        execute_status_economics(
            environment=_env(tmp_path, consent=False),
            git_worktree=str(worktree),
            executor=lambda **kwargs: calls.append(kwargs),
            task_loader=lambda *args, **kwargs: [_status_task()],
            evaluation_time=EVAL,
        )
    assert calls == []


def test_execute_status_economics_rejects_reused_bulk_consent_without_stage_consent(tmp_path):
    worktree = (tmp_path / "repo").resolve()
    worktree.mkdir()
    _complete_predecessors(tmp_path, worktree)
    prepare_status_economics(
        environment=_env(tmp_path, consent=False),
        git_worktree=str(worktree),
        task_builder=_builder,
    )
    calls = []
    loaders = []

    with pytest.raises(
        KRXHistoricalWorkerEntrypointError,
        match="EXPLICIT_STATUS_ECONOMICS_CONSENT",
    ):
        execute_status_economics(
            environment=_env(tmp_path, consent=True),
            git_worktree=str(worktree),
            executor=lambda **kwargs: calls.append(kwargs),
            task_loader=lambda *args, **kwargs: loaders.append(True) or [_status_task()],
            evaluation_time=EVAL,
        )
    assert calls == []
    assert loaders == []


def test_execute_status_economics_completes_context_only_with_consent(tmp_path):
    worktree = (tmp_path / "repo").resolve()
    worktree.mkdir()
    _complete_predecessors(tmp_path, worktree)
    prepare_status_economics(
        environment=_env(tmp_path, consent=False),
        git_worktree=str(worktree),
        task_builder=_builder,
    )
    calls = []

    def executor(**kwargs):
        calls.append(kwargs["spec"])
        return {
            **_completion(
                kwargs["environment"]["KRX_PRIVATE_RAW_DIR"],
                worktree,
                b"status-economics",
            ),
            "network_request_attempted": True,
        }

    out = execute_status_economics(
        environment=_status_env(tmp_path),
        git_worktree=str(worktree),
        executor=executor,
        task_loader=lambda *args, **kwargs: [_status_task()],
        evaluation_time=EVAL,
    )
    assert len(calls) == 1
    assert out["mode"] == "EXECUTE_STATUS_ECONOMICS"
    assert out["task_count"] == 1
    assert out["completed_task_count"] == 1
    assert out["network_request_attempt_count"] == 1
    assert out["phase_complete"] is True
    assert out["exact_status_economics_ready"] is False
    assert out["source_gate_c_closed"] is False
    assert out["source_gate_d_closed"] is False
    assert out["source_gate_e_closed"] is False
    assert out["feature_performance_testing_authorized"] is False
    assert out["sealed_holdout_authorized"] is False
    assert out["live_trading_authorized"] is False
    assert "KR7111110000" not in str(out)


def test_status_economics_manifest_drift_fails_closed(tmp_path):
    worktree = (tmp_path / "repo").resolve()
    worktree.mkdir()
    _complete_predecessors(tmp_path, worktree)
    out = prepare_status_economics(
        environment=_env(tmp_path, consent=False),
        git_worktree=str(worktree),
        task_builder=_builder,
    )
    root = (tmp_path / "private").resolve()
    import json
    manifest = json.loads((root / out["private_task_manifest_relpath"]).read_text(encoding="utf-8"))
    manifest["task_set_fingerprint_sha256"] = "0" * 64
    write_private_json(
        root,
        out["private_task_manifest_relpath"],
        manifest,
        git_worktree=str(worktree),
    )
    with pytest.raises(KRXHistoricalWorkerEntrypointError, match="manifest fingerprint drift"):
        load_frozen_status_economics_tasks(
            str(root),
            git_worktree=str(worktree),
            task_builder=_builder,
        )
