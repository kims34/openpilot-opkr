from datetime import datetime, timezone
import json
from pathlib import Path

import pandas as pd
import pytest

from research_v1_krx_expected_scope_batch import (
    KRXExpectedScopeBatchError,
    execute_expected_scope_batch,
)
from research_v1_krx_expected_scope_preflight import CONSENT_SENTINEL
from research_v1_krx_historical_worker_core import FetchResult


EVAL = datetime(2026, 10, 2, 12, 55, tzinfo=timezone.utc)


def _env(tmp_path, *, consent=True):
    out = {
        "KRX_AUTH_KEY": "present",
        "KRX_PRIVATE_RAW_DIR": str((tmp_path / "private").resolve()),
        "INDEXALERT_KRX_HIST_WORKER_ROLE": "DEDICATED_ONE_SHOT",
        "RAILWAY_SERVICE_NAME": "indexalert-krx-historical-worker",
    }
    if consent:
        out["KRX_EXPECTED_SCOPE_ATTESTATION_CONSENT"] = CONSENT_SENTINEL
    return out


def _empty_fetcher(calls):
    def fetcher(**kwargs):
        calls.append((kwargs["endpoint"], dict(kwargs["params"])))
        frame = pd.DataFrame(
            columns=["BAS_DD","ISU_CD","ISU_NM","MKT_NM"]
        )
        return FetchResult(
            raw_bytes=b'{"OutBlock_1":[]}',
            response_frame=frame,
            retrieved_at=EVAL.isoformat(),
            transport_status="FAKE_EMPTY",
            network_request_attempted=True,
        )
    return fetcher


def test_expected_scope_batch_blocks_before_fetch_without_separate_consent(tmp_path):
    worktree = (tmp_path / "repo").resolve()
    worktree.mkdir()
    calls = []
    with pytest.raises(KRXExpectedScopeBatchError, match="preflight blocked"):
        execute_expected_scope_batch(
            environment=_env(tmp_path, consent=False),
            git_worktree=str(worktree),
            fetcher=_empty_fetcher(calls),
            evaluation_time=EVAL,
            max_new_dates=1,
        )
    assert calls == []


def test_expected_scope_batch_checkpoints_and_resumes_without_refetch(tmp_path):
    worktree = (tmp_path / "repo").resolve()
    worktree.mkdir()
    calls = []

    first = execute_expected_scope_batch(
        environment=_env(tmp_path),
        git_worktree=str(worktree),
        fetcher=_empty_fetcher(calls),
        evaluation_time=EVAL,
        max_new_dates=2,
    )
    assert len(calls) == 2
    assert first["expected_task_count"] == 4127
    assert first["completed_task_count"] == 2
    assert first["newly_executed_date_count"] == 2
    assert first["batch_complete"] is False
    assert first["status"] == "IN_PROGRESS"
    assert first["raw_rows_emitted"] is False
    assert first["security_identifiers_emitted"] is False
    assert first["source_gate_c_closed"] is False
    assert first["sealed_holdout_authorized"] is False
    assert first["live_trading_authorized"] is False

    second_calls = []
    second = execute_expected_scope_batch(
        environment=_env(tmp_path),
        git_worktree=str(worktree),
        fetcher=_empty_fetcher(second_calls),
        evaluation_time=EVAL,
        max_new_dates=0,
    )
    assert second_calls == []
    assert second["completed_task_count"] == 2
    assert second["resumed_date_count"] == 2
    assert second["newly_executed_date_count"] == 0
    assert second["batch_complete"] is False


def test_expected_scope_batch_resume_fails_closed_after_raw_tamper(tmp_path):
    worktree = (tmp_path / "repo").resolve()
    worktree.mkdir()
    calls = []

    execute_expected_scope_batch(
        environment=_env(tmp_path),
        git_worktree=str(worktree),
        fetcher=_empty_fetcher(calls),
        evaluation_time=EVAL,
        max_new_dates=1,
    )
    root = tmp_path / "private"
    scope = json.loads(
        (root / "expected_scope/dates/20150615.json").read_text(
            encoding="utf-8"
        )
    )
    receipt = json.loads(
        (root / scope["daily_receipt_relpath"]).read_text(encoding="utf-8")
    )
    digest = receipt["raw_object_sha256"]
    obj = root / "objects/sha256" / digest[:2] / f"{digest}.bin"
    obj.write_bytes(b"tampered")
    obj.chmod(0o600)

    with pytest.raises(Exception, match="checksum mismatch"):
        execute_expected_scope_batch(
            environment=_env(tmp_path),
            git_worktree=str(worktree),
            fetcher=_empty_fetcher([]),
            evaluation_time=EVAL,
            max_new_dates=0,
        )


def test_expected_scope_batch_task_set_is_frozen_even_when_paused(tmp_path):
    worktree = (tmp_path / "repo").resolve()
    worktree.mkdir()
    out = execute_expected_scope_batch(
        environment=_env(tmp_path),
        git_worktree=str(worktree),
        fetcher=_empty_fetcher([]),
        evaluation_time=EVAL,
        max_new_dates=0,
    )
    assert out["expected_task_count"] == 4127
    assert out["completed_task_count"] == 0
    assert len(out["task_set_fingerprint_sha256"]) == 64
    assert out["network_request_attempted"] is False
    assert out["source_gate_c_closed"] is False
    assert out["source_gate_d_closed"] is False
    assert out["source_gate_e_closed"] is False
    assert out["feature_performance_testing_authorized"] is False
