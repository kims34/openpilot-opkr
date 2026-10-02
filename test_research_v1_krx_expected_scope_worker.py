from pathlib import Path

import pytest

from research_v1_krx_expected_scope_preflight import CONSENT_SENTINEL
from research_v1_krx_expected_scope_worker import (
    KRXExpectedScopeWorkerError,
    run_expected_scope_worker,
)


def _env(tmp_path, *, consent=False):
    out = {
        "KRX_AUTH_KEY": "present",
        "KRX_PRIVATE_RAW_DIR": str((tmp_path / "private").resolve()),
        "INDEXALERT_KRX_HIST_WORKER_ROLE": "DEDICATED_ONE_SHOT",
        "RAILWAY_SERVICE_NAME": "indexalert-krx-historical-worker",
    }
    if consent:
        out["KRX_EXPECTED_SCOPE_ATTESTATION_CONSENT"] = CONSENT_SENTINEL
    return out


def test_expected_scope_worker_defaults_to_network_free_preflight(tmp_path):
    worktree=(tmp_path/"repo").resolve()
    worktree.mkdir()
    out=run_expected_scope_worker(
        execute=False,
        environment=_env(tmp_path, consent=False),
        git_worktree=str(worktree),
        batch_runner=lambda **kwargs: (_ for _ in ()).throw(
            AssertionError("batch runner must not be called")
        ),
    )
    assert out["mode"]=="PREFLIGHT_ONLY"
    assert out["network_request_attempted"] is False
    assert out["preflight"]["expected_scope_network_execution_authorized"] is False
    assert out["plan"]["calendar_date_count"]==4127
    assert out["source_gate_c_closed"] is False
    assert out["sealed_holdout_authorized"] is False
    assert out["live_trading_authorized"] is False


def test_expected_scope_worker_blocks_execute_without_distinct_consent(tmp_path):
    worktree=(tmp_path/"repo").resolve()
    worktree.mkdir()
    calls=[]
    with pytest.raises(KRXExpectedScopeWorkerError, match="preflight blocked"):
        run_expected_scope_worker(
            execute=True,
            environment=_env(tmp_path, consent=False),
            git_worktree=str(worktree),
            batch_runner=lambda **kwargs: calls.append(kwargs),
        )
    assert calls==[]


def test_historical_bulk_consent_never_substitutes_for_expected_scope_consent(tmp_path):
    worktree=(tmp_path/"repo").resolve()
    worktree.mkdir()
    env=_env(tmp_path, consent=False)
    env["KRX_HISTORICAL_ACQUISITION_CONSENT"]="I_AUTHORIZE_INDEXALERT_KRX_HIST_ACQ_v3"
    calls=[]
    with pytest.raises(KRXExpectedScopeWorkerError, match="preflight blocked"):
        run_expected_scope_worker(
            execute=True,
            environment=env,
            git_worktree=str(worktree),
            batch_runner=lambda **kwargs: calls.append(kwargs),
        )
    assert calls==[]


def test_exact_expected_scope_consent_can_enter_batch_but_grants_no_other_authority(tmp_path):
    worktree=(tmp_path/"repo").resolve()
    worktree.mkdir()
    calls=[]

    def runner(**kwargs):
        calls.append(kwargs)
        return {
            "mode":"EXECUTE_EXPECTED_SCOPE_BATCH",
            "contract_id":"INDEXALERT-KRX-EXPECTED-SCOPE-ATTESTATION-v1",
            "expected_task_count":4127,
            "completed_task_count":0,
            "resumed_date_count":0,
            "newly_executed_date_count":0,
            "batch_complete":False,
            "status":"PENDING",
            "task_set_fingerprint_sha256":"a"*64,
            "network_request_attempted":False,
            "raw_rows_emitted":False,
            "security_identifiers_emitted":False,
            "source_gate_c_closed":False,
            "source_gate_d_closed":False,
            "source_gate_e_closed":False,
            "feature_performance_testing_authorized":False,
            "sealed_holdout_authorized":False,
            "live_trading_authorized":False,
        }

    out=run_expected_scope_worker(
        execute=True,
        environment=_env(tmp_path, consent=True),
        git_worktree=str(worktree),
        max_new_dates=0,
        batch_runner=runner,
    )
    assert len(calls)==1
    assert calls[0]["max_new_dates"]==0
    assert out["mode"]=="EXECUTE_EXPECTED_SCOPE_BATCH"
    assert out["source_gate_c_closed"] is False
    assert out["feature_performance_testing_authorized"] is False
    assert out["sealed_holdout_authorized"] is False
    assert out["live_trading_authorized"] is False


def test_expected_scope_worker_rejects_illegal_authority_from_batch(tmp_path):
    worktree=(tmp_path/"repo").resolve()
    worktree.mkdir()

    def bad_runner(**kwargs):
        return {
            "source_gate_c_closed":True,
            "sealed_holdout_authorized":False,
            "live_trading_authorized":False,
        }

    with pytest.raises(KRXExpectedScopeWorkerError, match="illegally closed Gate C"):
        run_expected_scope_worker(
            execute=True,
            environment=_env(tmp_path, consent=True),
            git_worktree=str(worktree),
            batch_runner=bad_runner,
        )
