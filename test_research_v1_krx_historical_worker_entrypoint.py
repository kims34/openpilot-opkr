from datetime import datetime, timezone
from pathlib import Path

import pytest

from research_v1_krx_historical_acquisition_preflight import CONSENT_SENTINEL
from research_v1_krx_historical_worker_entrypoint import (
    KRXHistoricalWorkerEntrypointError,
    execute_identity_seed,
    preflight_only,
)


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
        return {
            "completed": True,
            "resumed": False,
            "request_metadata_sha256": digest,
            "raw_object_sha256": digest,
            "raw_bytes_size": n,
            "response_rows": n,
            "response_schema_sha256": "a" * 64,
            "response_payload_sha256": "b" * 64,
            "receipt_fingerprint_sha256": "c" * 64,
            "network_request_attempted": False,
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
    assert out["raw_rows_emitted"] is False
    assert out["feature_performance_testing_authorized"] is False
    assert out["sealed_holdout_authorized"] is False
    assert out["live_trading_authorized"] is False

    batch = tmp_path / "private" / out["private_batch_relpath"]
    assert batch.is_file()
    assert batch.stat().st_mode & 0o777 == 0o600
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
