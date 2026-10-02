from datetime import datetime, timezone
from pathlib import Path

import pytest

from research_v1_krx_historical_acquisition_preflight import CONSENT_SENTINEL
from research_v1_krx_historical_batch_state import (
    initialize_phase_state,
    record_task_completion,
)
from research_v1_krx_historical_worker_entrypoint import (
    IDENTITY_BINDING_CONSENT_ENV,
    IDENTITY_BINDING_CONSENT_SENTINEL,
    KRXHistoricalWorkerEntrypointError,
    execute_identity_seed,
    execute_identity_standard_code_binding,
    execute_per_security_history,
    prepare_per_security_history,
    prepare_status_economics,
    preflight_only,
)
from research_v1_krx_private_store import write_raw_object


EVAL = datetime(2026, 10, 2, 11, 0, tzinfo=timezone.utc)


def _env(tmp_path, *, consent=False):
    out = {
        "KRX_ID": "present",
        "KRX_PW": "present",
        "KRX_AUTH_KEY": "present",
        "KRX_PRIVATE_RAW_DIR": str((tmp_path / "private").resolve()),
        "INDEXALERT_KRX_HIST_WORKER_ROLE": "DEDICATED_ONE_SHOT",
        "RAILWAY_SERVICE_NAME": "indexalert-krx-historical-worker",
    }
    if consent:
        out["KRX_HISTORICAL_ACQUISITION_CONSENT"] = CONSENT_SENTINEL
    return out


def test_default_preflight_mode_is_network_free_and_reports_missing_consent(tmp_path):
    worktree = (tmp_path / "repo").resolve()
    worktree.mkdir()
    out = preflight_only(_env(tmp_path, consent=False))
    assert out["mode"] == "PREFLIGHT_ONLY"
    assert out["preflight"]["historical_acquisition_network_execution_authorized"] is False
    assert "EXPLICIT_HISTORICAL_ACQUISITION_EXECUTION_CONSENT" in out["preflight"]["missing_requirements"]
    assert out["identity_seed"]["task_count"] == 27
    assert out["network_request_attempted"] is False
    assert out["raw_rows_emitted"] is False
    assert out["sealed_holdout_authorized"] is False
    assert out["live_trading_authorized"] is False


def test_execute_mode_blocks_before_executor_without_exact_bulk_consent(tmp_path):
    worktree = (tmp_path / "repo").resolve()
    worktree.mkdir()
    calls = []

    def executor(**kwargs):
        calls.append(kwargs)
        raise AssertionError("must not execute")

    with pytest.raises(KRXHistoricalWorkerEntrypointError, match="preflight blocked"):
        execute_identity_seed(
            environment=_env(tmp_path, consent=False),
            git_worktree=str(worktree),
            executor=executor,
            evaluation_time=EVAL,
        )
    assert calls == []


def test_identity_seed_executes_exactly_27_tasks_and_writes_private_batch(tmp_path):
    worktree = (tmp_path / "repo").resolve()
    worktree.mkdir()
    calls = []

    def executor(**kwargs):
        calls.append(kwargs["spec"])
        n = len(calls)
        digest = f"{n:064x}"[-64:]
        raw = write_raw_object(
            Path(kwargs["environment"]["KRX_PRIVATE_RAW_DIR"]),
            f"identity-seed-{n}".encode(),
            git_worktree=kwargs["git_worktree"],
        )
        return {
            "completed": True,
            "resumed": False,
            "request_metadata_sha256": digest,
            "raw_object_sha256": raw["raw_object_sha256"],
            "raw_bytes_size": raw["raw_bytes_size"],
            "response_rows": n,
            "retrieved_at": EVAL.isoformat(),
            "response_schema_sha256": "a" * 64,
            "response_payload_sha256": "b" * 64,
            "receipt_fingerprint_sha256": "c" * 64,
            "network_request_attempted": False,
            "raw_rows_emitted": False,
            "feature_performance_testing_authorized": False,
            "sealed_holdout_authorized": False,
            "live_trading_authorized": False,
        }

    out = execute_identity_seed(
        environment=_env(tmp_path, consent=True),
        git_worktree=str(worktree),
        executor=executor,
        evaluation_time=EVAL,
    )
    assert len(calls) == 27
    assert out["mode"] == "EXECUTE_IDENTITY_SEED"
    assert out["task_count"] == 27
    assert out["completed_task_count"] == 27
    assert out["resumed_task_count"] == 0
    assert out["network_request_attempt_count"] == 0
    assert out["phase_status"] == "COMPLETE"
    assert out["phase_complete"] is True
    assert out["phase_completed_task_count"] == 27
    assert out["raw_rows_emitted"] is False
    assert out["feature_performance_testing_authorized"] is False
    assert out["sealed_holdout_authorized"] is False
    assert out["live_trading_authorized"] is False

    batch = tmp_path / "private" / out["private_batch_relpath"]
    assert batch.is_file()
    assert batch.stat().st_mode & 0o777 == 0o600
    assert "retrieved_at" in batch.read_text(encoding="utf-8")
    rendered = str(out)
    assert "005930" not in rendered
    assert "KR7005930003" not in rendered


def test_entrypoint_cannot_run_on_forbidden_public_service_even_with_consent(tmp_path):
    worktree = (tmp_path / "repo").resolve()
    worktree.mkdir()
    env = _env(tmp_path, consent=True)
    env["RAILWAY_SERVICE_NAME"] = "indexalert-runtime"
    calls = []

    with pytest.raises(KRXHistoricalWorkerEntrypointError, match="DEDICATED_WORKER_SERVICE_ISOLATION"):
        execute_identity_seed(
            environment=env,
            git_worktree=str(worktree),
            executor=lambda **kwargs: calls.append(kwargs),
            evaluation_time=EVAL,
        )
    assert calls == []


def test_entrypoint_requires_timezone_aware_execution_time(tmp_path):
    worktree = (tmp_path / "repo").resolve()
    worktree.mkdir()
    with pytest.raises(KRXHistoricalWorkerEntrypointError, match="timezone-aware"):
        execute_identity_seed(
            environment=_env(tmp_path, consent=True),
            git_worktree=str(worktree),
            executor=lambda **kwargs: {},
            evaluation_time=datetime(2026, 10, 2, 11, 0),
        )


def _complete_seed_predecessor(tmp_path, worktree):
    root = (tmp_path / "private").resolve()
    task = {"phase": "IDENTITY_SEED", "task_id": "d" * 64}
    initialize_phase_state(root=str(root), phase="IDENTITY_SEED", tasks=[task])
    raw = write_raw_object(root, b"seed-predecessor", git_worktree=str(worktree))
    record_task_completion(
        root=str(root),
        phase="IDENTITY_SEED",
        task_id=task["task_id"],
        worker_result={
            "completed": True,
            "request_metadata_sha256": "1" * 64,
            "raw_object_sha256": raw["raw_object_sha256"],
            "raw_bytes_size": raw["raw_bytes_size"],
            "response_rows": 1,
            "response_schema_sha256": "2" * 64,
            "response_payload_sha256": "3" * 64,
            "receipt_fingerprint_sha256": "4" * 64,
            "raw_rows_emitted": False,
            "feature_performance_testing_authorized": False,
            "sealed_holdout_authorized": False,
            "live_trading_authorized": False,
        },
        git_worktree=str(worktree),
    )


def _binding_env(tmp_path):
    env = _env(tmp_path, consent=True)
    env[IDENTITY_BINDING_CONSENT_ENV] = IDENTITY_BINDING_CONSENT_SENTINEL
    return env


def _binding_task():
    return {
        "phase": "IDENTITY_STANDARD_CODE_BINDING",
        "task_id": "e" * 64,
        "request_spec": {
            "kind": "security_master",
            "params": {"basDd": "20200102"},
        },
        "contains_security_identifier": False,
    }


def test_identity_binding_blocks_before_executor_without_bulk_consent(tmp_path):
    worktree = (tmp_path / "repo").resolve()
    worktree.mkdir()
    _complete_seed_predecessor(tmp_path, worktree)
    calls = []

    with pytest.raises(KRXHistoricalWorkerEntrypointError, match="preflight blocked"):
        execute_identity_standard_code_binding(
            environment=_env(tmp_path, consent=False),
            git_worktree=str(worktree),
            executor=lambda **kwargs: calls.append(kwargs),
            task_builder=lambda *args, **kwargs: [_binding_task()],
            evaluation_time=EVAL,
        )
    assert calls == []


def test_identity_binding_rejects_reused_bulk_consent_without_stage_consent(tmp_path):
    worktree = (tmp_path / "repo").resolve()
    worktree.mkdir()
    _complete_seed_predecessor(tmp_path, worktree)
    calls = []
    builders = []

    with pytest.raises(
        KRXHistoricalWorkerEntrypointError,
        match="EXPLICIT_IDENTITY_STANDARD_CODE_BINDING_CONSENT",
    ):
        execute_identity_standard_code_binding(
            environment=_env(tmp_path, consent=True),
            git_worktree=str(worktree),
            executor=lambda **kwargs: calls.append(kwargs),
            task_builder=lambda *args, **kwargs: builders.append(True) or [_binding_task()],
            evaluation_time=EVAL,
        )
    assert calls == []
    assert builders == []


def test_identity_binding_requires_completed_seed_phase(tmp_path):
    worktree = (tmp_path / "repo").resolve()
    worktree.mkdir()
    with pytest.raises(Exception, match="prior phase IDENTITY_SEED"):
        execute_identity_standard_code_binding(
            environment=_binding_env(tmp_path),
            git_worktree=str(worktree),
            executor=lambda **kwargs: {},
            task_builder=lambda *args, **kwargs: [_binding_task()],
            evaluation_time=EVAL,
        )


def test_identity_binding_executes_private_task_set_after_seed_completion(tmp_path):
    worktree = (tmp_path / "repo").resolve()
    worktree.mkdir()
    _complete_seed_predecessor(tmp_path, worktree)
    calls = []

    def executor(**kwargs):
        calls.append(kwargs["spec"])
        raw = write_raw_object(
            Path(kwargs["environment"]["KRX_PRIVATE_RAW_DIR"]),
            b"binding-master",
            git_worktree=kwargs["git_worktree"],
        )
        return {
            "completed": True,
            "resumed": False,
            "request_metadata_sha256": "5" * 64,
            "raw_object_sha256": raw["raw_object_sha256"],
            "raw_bytes_size": raw["raw_bytes_size"],
            "response_rows": 1,
            "retrieved_at": EVAL.isoformat(),
            "response_schema_sha256": "6" * 64,
            "response_payload_sha256": "7" * 64,
            "receipt_fingerprint_sha256": "8" * 64,
            "network_request_attempted": False,
            "raw_rows_emitted": False,
            "feature_performance_testing_authorized": False,
            "sealed_holdout_authorized": False,
            "live_trading_authorized": False,
        }

    out = execute_identity_standard_code_binding(
        environment=_binding_env(tmp_path),
        git_worktree=str(worktree),
        executor=executor,
        task_builder=lambda *args, **kwargs: [_binding_task()],
        evaluation_time=EVAL,
    )
    assert len(calls) == 1
    assert out["mode"] == "EXECUTE_IDENTITY_STANDARD_CODE_BINDING"
    assert out["task_count"] == 1
    assert out["completed_task_count"] == 1
    assert out["phase_complete"] is True
    assert out["phase_status"] == "COMPLETE"
    assert out["raw_rows_emitted"] is False
    assert out["feature_performance_testing_authorized"] is False
    assert out["sealed_holdout_authorized"] is False
    assert out["live_trading_authorized"] is False
    assert "20200102" not in str(out)
    assert (tmp_path / "private" / out["private_batch_relpath"]).is_file()


def _complete_binding_predecessor(tmp_path, worktree):
    _complete_seed_predecessor(tmp_path, worktree)
    root = (tmp_path / "private").resolve()
    task = _binding_task()
    initialize_phase_state(
        root=str(root),
        phase="IDENTITY_STANDARD_CODE_BINDING",
        tasks=[task],
        git_worktree=str(worktree),
    )
    raw = write_raw_object(root, b"binding-predecessor", git_worktree=str(worktree))
    record_task_completion(
        root=str(root),
        phase="IDENTITY_STANDARD_CODE_BINDING",
        task_id=task["task_id"],
        worker_result={
            "completed": True,
            "request_metadata_sha256": "9" * 64,
            "raw_object_sha256": raw["raw_object_sha256"],
            "raw_bytes_size": raw["raw_bytes_size"],
            "response_rows": 1,
            "response_schema_sha256": "a" * 64,
            "response_payload_sha256": "b" * 64,
            "receipt_fingerprint_sha256": "c" * 64,
            "raw_rows_emitted": False,
            "feature_performance_testing_authorized": False,
            "sealed_holdout_authorized": False,
            "live_trading_authorized": False,
        },
        git_worktree=str(worktree),
    )


def _per_security_task():
    return {
        "phase": "PER_SECURITY_HISTORY",
        "task_id": "f" * 64,
        "source_family": "KRX_SECURITY_STATUS",
        "request_spec": {
            "kind": "trading_halt",
            "params": {
                "isuCd": "KR7005930003",
                "isuCd2": "005930",
                "strtDd": "20150615",
                "endDd": "20170613",
            },
        },
        "contains_security_identifier": True,
    }


def test_prepare_per_security_history_requires_completed_binding(tmp_path):
    worktree = (tmp_path / "repo").resolve()
    worktree.mkdir()
    _complete_seed_predecessor(tmp_path, worktree)
    with pytest.raises(Exception, match="prior phase IDENTITY_STANDARD_CODE_BINDING"):
        prepare_per_security_history(
            environment=_env(tmp_path, consent=False),
            git_worktree=str(worktree),
            task_builder=lambda *args, **kwargs: [_per_security_task()],
        )


def test_prepare_per_security_history_is_network_free_without_bulk_consent(tmp_path):
    worktree = (tmp_path / "repo").resolve()
    worktree.mkdir()
    _complete_binding_predecessor(tmp_path, worktree)

    out = prepare_per_security_history(
        environment=_env(tmp_path, consent=False),
        git_worktree=str(worktree),
        task_builder=lambda *args, **kwargs: [_per_security_task()],
    )
    assert out["mode"] == "PREPARE_PER_SECURITY_HISTORY"
    assert out["task_count"] == 1
    assert out["task_count_by_kind"] == {"trading_halt": 1}
    assert out["phase_status"] == "PENDING"
    assert out["phase_complete"] is False
    assert out["network_request_attempted"] is False
    assert out["security_identifiers_emitted"] is False
    assert out["raw_rows_emitted"] is False
    assert out["source_gate_c_closed"] is False
    assert out["source_gate_d_closed"] is False
    assert out["source_gate_e_closed"] is False
    assert out["feature_performance_testing_authorized"] is False
    assert out["sealed_holdout_authorized"] is False
    assert out["live_trading_authorized"] is False
    assert "005930" not in str(out)
    assert "KR7005930003" not in str(out)

    manifest = tmp_path / "private" / out["private_task_manifest_relpath"]
    assert manifest.is_file()
    assert manifest.stat().st_mode & 0o777 == 0o600
    private_text = manifest.read_text(encoding="utf-8")
    assert "005930" in private_text
    assert "KR7005930003" in private_text


def test_prepare_per_security_history_rejects_public_runtime_even_network_free(tmp_path):
    worktree = (tmp_path / "repo").resolve()
    worktree.mkdir()
    _complete_binding_predecessor(tmp_path, worktree)
    env = _env(tmp_path, consent=False)
    env["RAILWAY_SERVICE_NAME"] = "indexalert-runtime"

    with pytest.raises(
        KRXHistoricalWorkerEntrypointError,
        match="DEDICATED_WORKER_SERVICE_ISOLATION",
    ):
        prepare_per_security_history(
            environment=env,
            git_worktree=str(worktree),
            task_builder=lambda *args, **kwargs: [_per_security_task()],
        )


def _prepare_per_security_predecessor(tmp_path, worktree):
    _complete_binding_predecessor(tmp_path, worktree)
    return prepare_per_security_history(
        environment=_env(tmp_path, consent=False),
        git_worktree=str(worktree),
        task_builder=lambda *args, **kwargs: [_per_security_task()],
    )


def test_execute_per_security_history_blocks_without_bulk_consent(tmp_path):
    worktree = (tmp_path / "repo").resolve()
    worktree.mkdir()
    _prepare_per_security_predecessor(tmp_path, worktree)
    calls = []

    with pytest.raises(KRXHistoricalWorkerEntrypointError, match="preflight blocked"):
        execute_per_security_history(
            environment=_env(tmp_path, consent=False),
            git_worktree=str(worktree),
            executor=lambda **kwargs: calls.append(kwargs),
            task_loader=lambda *args, **kwargs: [_per_security_task()],
            evaluation_time=EVAL,
        )
    assert calls == []


def test_execute_per_security_history_uses_only_prepared_frozen_tasks(tmp_path):
    worktree = (tmp_path / "repo").resolve()
    worktree.mkdir()
    _prepare_per_security_predecessor(tmp_path, worktree)
    calls = []

    def executor(**kwargs):
        calls.append(kwargs["spec"])
        raw = write_raw_object(
            Path(kwargs["environment"]["KRX_PRIVATE_RAW_DIR"]),
            b"per-security-history",
            git_worktree=kwargs["git_worktree"],
        )
        return {
            "completed": True,
            "resumed": False,
            "request_metadata_sha256": "1" * 64,
            "raw_object_sha256": raw["raw_object_sha256"],
            "raw_bytes_size": raw["raw_bytes_size"],
            "response_rows": 1,
            "retrieved_at": EVAL.isoformat(),
            "response_schema_sha256": "2" * 64,
            "response_payload_sha256": "3" * 64,
            "receipt_fingerprint_sha256": "4" * 64,
            "network_request_attempted": True,
            "raw_rows_emitted": False,
            "feature_performance_testing_authorized": False,
            "sealed_holdout_authorized": False,
            "live_trading_authorized": False,
        }

    out = execute_per_security_history(
        environment=_env(tmp_path, consent=True),
        git_worktree=str(worktree),
        executor=executor,
        task_loader=lambda *args, **kwargs: [_per_security_task()],
        evaluation_time=EVAL,
    )
    assert len(calls) == 1
    assert out["mode"] == "EXECUTE_PER_SECURITY_HISTORY"
    assert out["task_count"] == 1
    assert out["completed_task_count"] == 1
    assert out["network_request_attempt_count"] == 1
    assert out["phase_complete"] is True
    assert out["phase_status"] == "COMPLETE"
    assert out["security_identifiers_emitted"] is False
    assert out["raw_rows_emitted"] is False
    assert out["source_gate_c_closed"] is False
    assert out["source_gate_d_closed"] is False
    assert out["source_gate_e_closed"] is False
    assert out["feature_performance_testing_authorized"] is False
    assert out["sealed_holdout_authorized"] is False
    assert out["live_trading_authorized"] is False
    assert "005930" not in str(out)
    assert "KR7005930003" not in str(out)
    assert (tmp_path / "private" / out["private_batch_relpath"]).is_file()


def test_load_frozen_per_security_tasks_rejects_manifest_drift(tmp_path):
    from research_v1_krx_historical_worker_entrypoint import (
        load_frozen_per_security_history_tasks,
    )
    from research_v1_krx_private_store import write_private_json

    worktree = (tmp_path / "repo").resolve()
    worktree.mkdir()
    _prepare_per_security_predecessor(tmp_path, worktree)
    root = (tmp_path / "private").resolve()

    manifest_path = root / "task_manifests" / "per-security-history-v3.json"
    import json
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    data["task_set_fingerprint_sha256"] = "0" * 64
    write_private_json(
        root,
        "task_manifests/per-security-history-v3.json",
        data,
        git_worktree=str(worktree),
    )

    with pytest.raises(
        KRXHistoricalWorkerEntrypointError,
        match="manifest fingerprint drift",
    ):
        load_frozen_per_security_history_tasks(
            str(root),
            git_worktree=str(worktree),
            task_builder=lambda *args, **kwargs: [_per_security_task()],
        )


def _complete_per_security_predecessor(tmp_path, worktree):
    _complete_binding_predecessor(tmp_path, worktree)
    root = (tmp_path / "private").resolve()
    task = _per_security_task()
    initialize_phase_state(
        root=str(root),
        phase="PER_SECURITY_HISTORY",
        tasks=[task],
        git_worktree=str(worktree),
    )
    raw = write_raw_object(root, b"per-security-predecessor", git_worktree=str(worktree))
    record_task_completion(
        root=str(root),
        phase="PER_SECURITY_HISTORY",
        task_id=task["task_id"],
        worker_result={
            "completed": True,
            "request_metadata_sha256": "a" * 64,
            "raw_object_sha256": raw["raw_object_sha256"],
            "raw_bytes_size": raw["raw_bytes_size"],
            "response_rows": 1,
            "response_schema_sha256": "b" * 64,
            "response_payload_sha256": "c" * 64,
            "receipt_fingerprint_sha256": "d" * 64,
            "raw_rows_emitted": False,
            "feature_performance_testing_authorized": False,
            "sealed_holdout_authorized": False,
            "live_trading_authorized": False,
        },
        git_worktree=str(worktree),
    )


def _status_economics_task():
    return {
        "phase": "STATUS_ECONOMICS",
        "task_id": "1" * 64,
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


def _status_economics_builder(*args, **kwargs):
    return (
        [_status_economics_task()],
        {
            "delisted_episode_count": 2,
            "cleanup_price_task_count": 1,
            "delisted_without_cleanup_interval_count": 1,
        },
    )


def test_prepare_status_economics_requires_completed_per_security_history(tmp_path):
    worktree = (tmp_path / "repo").resolve()
    worktree.mkdir()
    _complete_binding_predecessor(tmp_path, worktree)

    with pytest.raises(Exception, match="prior phase PER_SECURITY_HISTORY"):
        prepare_status_economics(
            environment=_env(tmp_path, consent=False),
            git_worktree=str(worktree),
            task_builder=_status_economics_builder,
        )


def test_prepare_status_economics_is_network_free_and_never_exact_fill_ready(tmp_path):
    worktree = (tmp_path / "repo").resolve()
    worktree.mkdir()
    _complete_per_security_predecessor(tmp_path, worktree)

    out = prepare_status_economics(
        environment=_env(tmp_path, consent=False),
        git_worktree=str(worktree),
        task_builder=_status_economics_builder,
    )
    assert out["mode"] == "PREPARE_STATUS_ECONOMICS"
    assert out["task_count"] == 1
    assert out["delisted_episode_count"] == 2
    assert out["cleanup_price_task_count"] == 1
    assert out["delisted_without_cleanup_interval_count"] == 1
    assert out["phase_status"] == "PENDING"
    assert out["phase_complete"] is False
    assert out["network_request_attempted"] is False
    assert out["security_identifiers_emitted"] is False
    assert out["raw_rows_emitted"] is False
    assert out["exact_status_economics_ready"] is False
    assert out["source_gate_c_closed"] is False
    assert out["source_gate_d_closed"] is False
    assert out["source_gate_e_closed"] is False
    assert out["feature_performance_testing_authorized"] is False
    assert out["sealed_holdout_authorized"] is False
    assert out["live_trading_authorized"] is False
    assert "KR7111110000" not in str(out)

    manifest = tmp_path / "private" / out["private_task_manifest_relpath"]
    assert manifest.is_file()
    private_text = manifest.read_text(encoding="utf-8")
    assert "KR7111110000" in private_text
    assert '"exact_status_economics_ready":false' in private_text.replace(" ", "").replace("\n", "")
