import pytest

import research_v1_krx_historical_worker_entrypoint as worker


def _state(completed=11750, failed=0, fingerprint=None):
    return {
        "plan_id": "INDEXALERT-KRX-HIST-ACQ-v3",
        "execution_contract_id": "INDEXALERT-KRX-HIST-EXEC-v3",
        "phase": "PER_SECURITY_HISTORY",
        "status": "IN_PROGRESS",
        "expected_task_count": worker.PER_SECURITY_EXPECTED_TASK_COUNT,
        "completed_task_count": completed,
        "failed_task_count": failed,
        "task_set_fingerprint_sha256": (
            fingerprint or worker.PER_SECURITY_EXPECTED_TASK_SET_SHA256
        ),
        "phase_complete": completed == worker.PER_SECURITY_EXPECTED_TASK_COUNT,
        "security_identifiers_emitted": False,
        "raw_rows_emitted": False,
        "source_gate_c_closed": False,
        "source_gate_d_closed": False,
        "source_gate_e_closed": False,
        "feature_performance_testing_authorized": False,
        "sealed_holdout_authorized": False,
        "live_trading_authorized": False,
    }


def _loader(state):
    return lambda *args, **kwargs: {
        "value": state,
        "metadata_sha256": "a" * 64,
    }


def test_initial_zero_checkpoint_does_not_require_resume_consent():
    out = worker._require_per_security_resume_consent_if_checkpointed(
        environment={},
        root="/private",
        git_worktree="/repo",
        state_loader=_loader(_state(completed=0)),
    )
    assert out["completed_task_count"] == 0
    assert out["remaining_task_count"] == 14296
    assert out["network_request_attempted"] is False


def test_partial_checkpoint_requires_distinct_resume_consent():
    with pytest.raises(
        worker.KRXHistoricalWorkerEntrypointError,
        match="EXPLICIT_PER_SECURITY_HISTORY_RESUME_CONSENT",
    ):
        worker._require_per_security_resume_consent_if_checkpointed(
            environment={},
            root="/private",
            git_worktree="/repo",
            state_loader=_loader(_state()),
        )

    out = worker._require_per_security_resume_consent_if_checkpointed(
        environment={
            worker.PER_SECURITY_RESUME_CONSENT_ENV:
                worker.PER_SECURITY_RESUME_CONSENT_SENTINEL
        },
        root="/private",
        git_worktree="/repo",
        state_loader=_loader(_state()),
    )
    assert out["completed_task_count"] == 11750
    assert out["remaining_task_count"] == 2546
    assert out["failed_task_count"] == 0
    assert out["security_identifiers_emitted"] is False
    assert out["raw_rows_emitted"] is False


def test_partial_checkpoint_rejects_wrong_resume_consent():
    with pytest.raises(
        worker.KRXHistoricalWorkerEntrypointError,
        match="EXPLICIT_PER_SECURITY_HISTORY_RESUME_CONSENT",
    ):
        worker._require_per_security_resume_consent_if_checkpointed(
            environment={worker.PER_SECURITY_RESUME_CONSENT_ENV: "WRONG"},
            root="/private",
            git_worktree="/repo",
            state_loader=_loader(_state()),
        )


def test_resume_guard_rejects_failed_tasks_or_fingerprint_drift():
    env = {
        worker.PER_SECURITY_RESUME_CONSENT_ENV:
            worker.PER_SECURITY_RESUME_CONSENT_SENTINEL
    }
    with pytest.raises(
        worker.KRXHistoricalWorkerEntrypointError,
        match="has failed tasks",
    ):
        worker._require_per_security_resume_consent_if_checkpointed(
            environment=env,
            root="/private",
            git_worktree="/repo",
            state_loader=_loader(_state(failed=1)),
        )

    with pytest.raises(
        worker.KRXHistoricalWorkerEntrypointError,
        match="fingerprint drift",
    ):
        worker._require_per_security_resume_consent_if_checkpointed(
            environment=env,
            root="/private",
            git_worktree="/repo",
            state_loader=_loader(_state(fingerprint="0" * 64)),
        )
