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


@pytest.mark.parametrize("field,value", [
    ("receipt_version", None), ("receipt_version", "obsolete"),
    ("request_metadata_sha256", None), ("request_metadata_sha256", "f" * 64),
    ("retrieved_at", None), ("retrieved_at", 1), ("retrieved_at", "NaT"),
    ("retrieved_at", "not-a-time"), ("retrieved_at", "2026-10-02T12:55:00"),
    ("transport_status", None), ("transport_status", 1), ("transport_status", ""),
    ("network_request_attempted", False), ("network_request_attempted", 1),
    ("network_request_attempted", None), ("network_request_attempted", "true"),
    ("raw_object_sha256", int("1" * 64)), ("raw_object_sha256", None),
])
def test_resume_rejects_receipt_request_time_or_transport_contract_drift(tmp_path, field, value):
    from research_v1_krx_private_store import write_private_json
    worktree = (tmp_path / "repo").resolve()
    worktree.mkdir()
    env = _env(tmp_path)
    execute_expected_scope_batch(environment=env, git_worktree=str(worktree),
        fetcher=_empty_fetcher([]), evaluation_time=EVAL, max_new_dates=1)
    root = tmp_path / "private"
    scope = json.loads(next((root / "expected_scope/dates/20150615").glob("*.json")).read_text())
    rel = scope["daily_receipt_relpath"]
    receipt = json.loads((root / rel).read_text())
    receipt[field] = value
    write_private_json(root, rel, receipt, git_worktree=worktree)
    calls = []
    with pytest.raises(KRXExpectedScopeBatchError):
        execute_expected_scope_batch(environment=env, git_worktree=str(worktree),
            fetcher=_empty_fetcher(calls), evaluation_time=EVAL, max_new_dates=0)
    assert calls == []


@pytest.mark.parametrize("field", [
    "raw_rows_emitted", "source_gate_c_closed", "source_gate_d_closed", "source_gate_e_closed",
    "feature_performance_testing_authorized", "sealed_holdout_authorized", "live_trading_authorized",
])
@pytest.mark.parametrize("value", [True, 0, None, "false"])
def test_resume_rejects_receipt_non_false_authority_fields(tmp_path, field, value):
    from research_v1_krx_private_store import write_private_json
    worktree = (tmp_path / "repo").resolve()
    worktree.mkdir()
    env = _env(tmp_path)
    execute_expected_scope_batch(environment=env, git_worktree=str(worktree),
        fetcher=_empty_fetcher([]), evaluation_time=EVAL, max_new_dates=1)
    root = tmp_path / "private"
    scope = json.loads(next((root / "expected_scope/dates/20150615").glob("*.json")).read_text())
    rel = scope["daily_receipt_relpath"]
    receipt = json.loads((root / rel).read_text())
    receipt[field] = value
    write_private_json(root, rel, receipt, git_worktree=worktree)
    calls = []
    with pytest.raises(KRXExpectedScopeBatchError, match="illegally claims authority"):
        execute_expected_scope_batch(environment=env, git_worktree=str(worktree),
            fetcher=_empty_fetcher(calls), evaluation_time=EVAL, max_new_dates=0)
    assert calls == []


def test_resume_rejects_relocated_receipt_with_valid_raw_and_metadata(tmp_path):
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
    receipt = json.loads((root / scope["daily_receipt_relpath"]).read_text())
    wrong_rel = "expected_scope/receipts/20150615/stk_bydd_trd/" + "f"*64 + ".json"
    write_private_json(root, wrong_rel, receipt, git_worktree=worktree)
    scope["daily_receipt_relpath"] = wrong_rel
    import research_v1_krx_expected_scope_batch as batch
    scope_rel = f"expected_scope/dates/20150615/{batch._sha256(scope)}.json"
    written = write_private_json(root, scope_rel, scope, git_worktree=worktree)
    state["completed"]["20150615"]["private_scope_relpath"] = scope_rel
    state["completed"]["20150615"]["private_scope_metadata_sha256"] = written["metadata_sha256"]
    write_private_json(root, state_rel, state, git_worktree=worktree)
    calls = []
    with pytest.raises(KRXExpectedScopeBatchError, match="receipt content-address checksum"):
        execute_expected_scope_batch(environment=env, git_worktree=str(worktree),
            fetcher=_empty_fetcher(calls), evaluation_time=EVAL, max_new_dates=0)
    assert calls == []


@pytest.mark.parametrize("relpath", [
    "other/20150615/stk_bydd_trd/" + "a"*64 + ".json",
    "expected_scope/receipts/20150616/stk_bydd_trd/" + "a"*64 + ".json",
    "expected_scope/receipts/20150615/stk_isu_base_info/" + "a"*64 + ".json",
    "expected_scope/receipts/20150615/stk_bydd_trd/not-a-digest.json",
])
def test_receipt_path_is_bound_to_frozen_dataset_date_before_private_read(monkeypatch, relpath):
    import research_v1_krx_expected_scope_batch as batch
    def forbidden_read(*args, **kwargs):
        pytest.fail("unexpected private read")
    monkeypatch.setattr(batch, "read_private_json", forbidden_read)
    with pytest.raises(KRXExpectedScopeBatchError, match="content-address path drift"):
        batch._verify_receipt(root="unused", relpath=relpath, requested_date="20150615",
            dataset_identifier="stk_bydd_trd", git_worktree="unused")


@pytest.mark.parametrize("relpath", [
    None, False, {}, 123,
    "expected_scope/dates/20260927/nested/" + "a" * 64 + ".json",
    "expected_scope/dates/20260927/../20260927/" + "a" * 64 + ".json",
    "expected_scope/dates/20260926/" + "a" * 64 + ".json",
])
def test_completed_scope_noncanonical_directory_rejected_before_private_read(tmp_path, monkeypatch, relpath):
    import research_v1_krx_expected_scope_batch as batch
    def forbidden_read(*args, **kwargs):
        pytest.fail("noncanonical scope path must be rejected before private read")
    monkeypatch.setattr(batch, "read_private_json", forbidden_read)
    with pytest.raises(batch.KRXExpectedScopeBatchError, match="private scope relpath"):
        batch._verify_completed_date(
            root=str(tmp_path / "private"), requested_date="20260927",
            completion={"private_scope_relpath": relpath}, git_worktree=str(tmp_path / "repo"),
        )


@pytest.mark.parametrize("field", [
    "source_gate_c_closed", "source_gate_d_closed", "source_gate_e_closed",
    "feature_performance_testing_authorized", "sealed_holdout_authorized", "live_trading_authorized",
])
def test_rehashed_private_scope_authority_claim_fails_before_refetch(tmp_path, field):
    from pathlib import Path
    from research_v1_krx_private_store import write_private_json
    import research_v1_krx_expected_scope_batch as batch
    worktree = (tmp_path / "repo").resolve()
    worktree.mkdir()
    env = _env(tmp_path)
    execute_expected_scope_batch(environment=env, git_worktree=str(worktree),
        fetcher=_empty_fetcher([]), evaluation_time=EVAL, max_new_dates=1)
    root = tmp_path / "private"
    state_path = root / batch.CHECKPOINT_REL
    state = json.loads(state_path.read_text())
    entry = state["completed"]["20150615"]
    scope = json.loads((root / entry["private_scope_relpath"]).read_text())
    scope[field] = True
    rel = str(Path(entry["private_scope_relpath"]).parent / (batch._sha256(scope) + ".json"))
    written = write_private_json(str(root), rel, scope, git_worktree=str(worktree))
    entry["private_scope_relpath"] = rel
    entry["private_scope_metadata_sha256"] = written["metadata_sha256"]
    state_path.write_text(json.dumps(state) + "\n")
    state_path.chmod(0o600)
    calls = []
    with pytest.raises(KRXExpectedScopeBatchError, match="private scope illegally claims authority"):
        execute_expected_scope_batch(environment=env, git_worktree=str(worktree),
            fetcher=_empty_fetcher(calls), evaluation_time=EVAL, max_new_dates=0)
    assert calls == []


@pytest.mark.parametrize("field,value", [
    ("official_trading_date_observed", True), ("official_trading_date_observed", 0),
    ("investor_expected_key_count", 1), ("investor_expected_key_count", "0"),
    ("investor_expected_key_count", False),
    ("status_expected_key_count", 1), ("status_expected_key_count", "0"),
    ("status_expected_key_count", False),
])
def test_completion_summary_drift_fails_before_refetch(tmp_path, field, value):
    import research_v1_krx_expected_scope_batch as batch
    worktree = (tmp_path / "repo").resolve()
    worktree.mkdir()
    env = _env(tmp_path)
    execute_expected_scope_batch(environment=env, git_worktree=str(worktree),
        fetcher=_empty_fetcher([]), evaluation_time=EVAL, max_new_dates=1)
    state_path = tmp_path / "private" / batch.CHECKPOINT_REL
    state = json.loads(state_path.read_text())
    state["completed"]["20150615"][field] = value
    state_path.write_text(json.dumps(state) + "\n")
    state_path.chmod(0o600)
    calls = []
    with pytest.raises(KRXExpectedScopeBatchError, match="completion"):
        execute_expected_scope_batch(environment=env, git_worktree=str(worktree),
            fetcher=_empty_fetcher(calls), evaluation_time=EVAL, max_new_dates=0)
    assert calls == []


@pytest.mark.parametrize("field,value", [
    ("official_trading_date_observed", 0), ("official_trading_date_observed", "false"),
    ("official_trading_date_observed", None), ("official_trading_date_observed", {}),
    ("investor_expected_key_count", 0.5), ("investor_expected_key_count", False),
    ("investor_expected_key_count", "0"), ("investor_expected_key_count", None),
    ("investor_expected_key_count", -1),
    ("status_expected_key_count", 0.5), ("status_expected_key_count", False),
    ("status_expected_key_count", "0"), ("status_expected_key_count", None),
    ("status_expected_key_count", -1),
])
def test_date_result_type_cannot_be_coerced_into_valid_completion(tmp_path, monkeypatch, field, value):
    import research_v1_krx_expected_scope_batch as batch
    worktree = (tmp_path / "repo").resolve()
    worktree.mkdir()
    original = batch.execute_expected_scope_date
    def corrupted_summary(**kwargs):
        result = original(**kwargs)
        result[field] = value
        return result
    monkeypatch.setattr(batch, "execute_expected_scope_date", corrupted_summary)
    with pytest.raises(KRXExpectedScopeBatchError, match="date executor"):
        execute_expected_scope_batch(environment=_env(tmp_path), git_worktree=str(worktree),
            fetcher=_empty_fetcher([]), evaluation_time=EVAL, max_new_dates=1)
    state = json.loads((tmp_path / "private" / batch.CHECKPOINT_REL).read_text())
    assert state["completed"] == {}
    assert state["completed_task_count"] == 0
