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
        from research_v1_krx_historical_fetchers import parse_openapi_raw
        frame = parse_openapi_raw(b'{"OutBlock_1":[]}')
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
    scope_path = next((root / "expected_scope" / "dates" / "20150615").glob("*.json"))
    scope = json.loads(scope_path.read_text(encoding="utf-8"))
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


def test_expected_scope_batch_resume_rejects_scope_path_drift(tmp_path):
    worktree = (tmp_path / "repo").resolve()
    worktree.mkdir()
    execute_expected_scope_batch(
        environment=_env(tmp_path),
        git_worktree=str(worktree),
        fetcher=_empty_fetcher([]),
        evaluation_time=EVAL,
        max_new_dates=1,
    )
    root = tmp_path / "private"
    state_path = root / "expected_scope" / "batch_state-v1.json"
    state = json.loads(state_path.read_text(encoding="utf-8"))
    state["completed"]["20150615"]["private_scope_relpath"] = "expected_scope/dates/20150615.json"
    state_path.write_text(json.dumps(state, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    state_path.chmod(0o600)

    with pytest.raises(KRXExpectedScopeBatchError, match="private scope relpath drift"):
        execute_expected_scope_batch(
            environment=_env(tmp_path),
            git_worktree=str(worktree),
            fetcher=_empty_fetcher([]),
            evaluation_time=EVAL,
            max_new_dates=0,
        )


@pytest.mark.parametrize("field,value", [
    ("expected_task_count", "1"), ("expected_task_count", 1.0), ("expected_task_count", True),
    ("completed_task_count", 0), ("completed_task_count", "1"), ("completed_task_count", 1.0), ("completed_task_count", True),
    ("batch_complete", False), ("batch_complete", 1), ("batch_complete", "true"),
    ("status", "PENDING"), ("status", "IN_PROGRESS"),
])
def test_resume_rejects_inconsistent_completion_metadata(monkeypatch, field, value):
    import research_v1_krx_expected_scope_batch as batch
    tasks = [{"task_id": "task", "request": {"params": {"basDd": "20150615"}}}]
    state = {
        "state_version": batch.STATE_VERSION, "contract_id": batch.CONTRACT_ID,
        "expected_task_count": 1, "task_set_fingerprint_sha256": batch._task_fingerprint(tasks),
        "completed": {"20150615": {}}, "completed_task_count": 1,
        "batch_complete": True, "status": "COMPLETE",
        **{key: False for key in ("source_gate_c_closed", "source_gate_d_closed", "source_gate_e_closed",
                                  "feature_performance_testing_authorized", "sealed_holdout_authorized", "live_trading_authorized")},
    }
    state[field] = value
    monkeypatch.setattr(batch, "read_private_json", lambda *args, **kwargs: {"value": state})
    with pytest.raises(KRXExpectedScopeBatchError):
        batch._load_or_init_state(root="unused", git_worktree="unused", tasks=tasks)


@pytest.mark.parametrize("field", [
    "source_gate_c_closed", "source_gate_d_closed", "source_gate_e_closed",
    "feature_performance_testing_authorized", "sealed_holdout_authorized", "live_trading_authorized",
])
@pytest.mark.parametrize("value", [True, 0, None, "false"])
def test_resume_rejects_non_false_authority_claims(monkeypatch, field, value):
    import research_v1_krx_expected_scope_batch as batch
    tasks = [{"task_id": "task", "request": {"params": {"basDd": "20150615"}}}]
    state = {
        "state_version": batch.STATE_VERSION, "contract_id": batch.CONTRACT_ID,
        "expected_task_count": 1, "task_set_fingerprint_sha256": batch._task_fingerprint(tasks),
        "completed": {}, "completed_task_count": 0, "batch_complete": False, "status": "PENDING",
        **{key: False for key in ("source_gate_c_closed", "source_gate_d_closed", "source_gate_e_closed",
                                  "feature_performance_testing_authorized", "sealed_holdout_authorized", "live_trading_authorized")},
    }
    state[field] = value
    monkeypatch.setattr(batch, "read_private_json", lambda *args, **kwargs: {"value": state})
    with pytest.raises(KRXExpectedScopeBatchError, match="illegally claims authority"):
        batch._load_or_init_state(root="unused", git_worktree="unused", tasks=tasks)


def test_paused_resume_verifies_completion_beyond_first_missing_date(tmp_path):
    worktree = (tmp_path / "repo").resolve()
    worktree.mkdir()
    execute_expected_scope_batch(
        environment=_env(tmp_path), git_worktree=str(worktree),
        fetcher=_empty_fetcher([]), evaluation_time=EVAL, max_new_dates=2,
    )
    root = tmp_path / "private"
    state_path = root / "expected_scope" / "batch_state-v1.json"
    state = json.loads(state_path.read_text())
    del state["completed"]["20150615"]
    state["completed_task_count"] = 1
    state_path.write_text(json.dumps(state) + "\n")
    state_path.chmod(0o600)
    scope_path = next((root / "expected_scope" / "dates" / "20150616").glob("*.json"))
    scope = json.loads(scope_path.read_text())
    receipt = json.loads((root / scope["daily_receipt_relpath"]).read_text())
    digest = receipt["raw_object_sha256"]
    obj = root / "objects/sha256" / digest[:2] / f"{digest}.bin"
    obj.write_bytes(b"tampered")
    obj.chmod(0o600)
    calls = []
    with pytest.raises(Exception, match="checksum mismatch"):
        execute_expected_scope_batch(
            environment=_env(tmp_path), git_worktree=str(worktree),
            fetcher=_empty_fetcher(calls), evaluation_time=EVAL, max_new_dates=0,
        )
    assert calls == []


@pytest.mark.parametrize("field,value", [
    ("response_rows", 1),
    ("response_payload_sha256", "f" * 64),
    ("response_schema_sha256", "f" * 64),
])
def test_resume_rejects_receipt_metadata_inconsistent_with_verified_raw(tmp_path, field, value):
    from research_v1_krx_private_store import write_private_json
    worktree = (tmp_path / "repo").resolve()
    worktree.mkdir()
    env = _env(tmp_path)
    execute_expected_scope_batch(environment=env, git_worktree=str(worktree),
        fetcher=_empty_fetcher([]), evaluation_time=EVAL, max_new_dates=1)
    root = tmp_path / "private"
    scope_path = next((root / "expected_scope/dates/20150615").glob("*.json"))
    scope = json.loads(scope_path.read_text())
    receipt_rel = scope["daily_receipt_relpath"]
    receipt = json.loads((root / receipt_rel).read_text())
    receipt[field] = value
    write_private_json(root, receipt_rel, receipt, git_worktree=worktree)
    calls = []
    with pytest.raises(KRXExpectedScopeBatchError, match="verified raw response"):
        execute_expected_scope_batch(environment=env, git_worktree=str(worktree),
            fetcher=_empty_fetcher(calls), evaluation_time=EVAL, max_new_dates=0)
    assert calls == []


@pytest.mark.parametrize("key,date_key", [
    ("investor_expected_scope", "event_date"),
    ("status_expected_scope", "snapshot_date"),
])
def test_resume_rejects_self_rehashed_scope_keys_absent_from_verified_raw(tmp_path, key, date_key):
    import research_v1_krx_expected_scope_batch as batch
    from research_v1_krx_private_store import write_private_json
    worktree = (tmp_path / "repo").resolve()
    worktree.mkdir()
    env = _env(tmp_path)
    execute_expected_scope_batch(environment=env, git_worktree=str(worktree),
        fetcher=_empty_fetcher([]), evaluation_time=EVAL, max_new_dates=1)
    root = tmp_path / "private"
    state_rel = "expected_scope/batch_state-v1.json"
    state = json.loads((root / state_rel).read_text())
    old_scope_rel = state["completed"]["20150615"]["private_scope_relpath"]
    scope = json.loads((root / old_scope_rel).read_text())
    scope[key] = [{date_key: "2015-06-15", "symbol": "005930", "isu_cd": "KR7005930003"}]
    new_rel = f"expected_scope/dates/20150615/{batch._sha256(scope)}.json"
    written = write_private_json(root, new_rel, scope, git_worktree=worktree)
    state["completed"]["20150615"]["private_scope_relpath"] = new_rel
    state["completed"]["20150615"]["private_scope_metadata_sha256"] = written["metadata_sha256"]
    write_private_json(root, state_rel, state, git_worktree=worktree)
    calls = []
    with pytest.raises(KRXExpectedScopeBatchError, match="keys differ from verified raw"):
        execute_expected_scope_batch(environment=env, git_worktree=str(worktree),
            fetcher=_empty_fetcher(calls), evaluation_time=EVAL, max_new_dates=0)
    assert calls == []
