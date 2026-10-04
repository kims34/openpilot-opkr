import pytest

import research_v1_krx_historical_worker_entrypoint as worker


def _env(tmp_path):
    return {
        "KRX_ID": "present",
        "KRX_PW": "present",
        "KRX_AUTH_KEY": "present",
        "KRX_PRIVATE_RAW_DIR": str((tmp_path / "private").resolve()),
        "INDEXALERT_KRX_HIST_WORKER_ROLE": "DEDICATED_ONE_SHOT",
        "RAILWAY_SERVICE_NAME": "indexalert-krx-historical-worker",
    }


def _state():
    return {
        "plan_id": "INDEXALERT-KRX-HIST-ACQ-v3",
        "execution_contract_id": "INDEXALERT-KRX-HIST-EXEC-v3",
        "phase": "STATUS_ECONOMICS",
        "status": "COMPLETE",
        "expected_task_count": 5,
        "completed_task_count": 5,
        "failed_task_count": 0,
        "task_set_fingerprint_sha256": "a" * 64,
        "phase_complete": True,
        "source_gate_c_closed": False,
        "source_gate_d_closed": False,
        "source_gate_e_closed": False,
        "feature_performance_testing_authorized": False,
        "sealed_holdout_authorized": False,
        "live_trading_authorized": False,
    }


def _manifest():
    return {
        "phase": "STATUS_ECONOMICS",
        "task_count": 5,
        "task_set_fingerprint_sha256": "a" * 64,
    }


def _batch():
    return {
        "phase": "STATUS_ECONOMICS",
        "task_count": 5,
        "completed_task_count": 5,
        "resumed_task_count": 1,
        "network_request_attempt_count": 4,
        "task_set_fingerprint_sha256": "a" * 64,
        "exact_status_economics_ready": False,
        "source_gate_c_closed": False,
        "source_gate_d_closed": False,
        "source_gate_e_closed": False,
        "feature_performance_testing_authorized": False,
        "sealed_holdout_authorized": False,
        "live_trading_authorized": False,
    }


def _pin(monkeypatch):
    monkeypatch.setattr(worker, "STATUS_ECONOMICS_EXPECTED_TASK_COUNT", 5)
    monkeypatch.setattr(
        worker,
        "STATUS_ECONOMICS_EXPECTED_TASK_SET_SHA256",
        "a" * 64,
    )
    monkeypatch.setattr(
        worker,
        "STATUS_ECONOMICS_EXPECTED_MANIFEST_SHA256",
        "b" * 64,
    )


def test_status_economics_finalizer_blocks_when_scope_pin_is_missing(tmp_path, monkeypatch):
    monkeypatch.setattr(worker, "STATUS_ECONOMICS_EXPECTED_TASK_COUNT", None)
    monkeypatch.setattr(worker, "STATUS_ECONOMICS_EXPECTED_TASK_SET_SHA256", None)
    monkeypatch.setattr(worker, "STATUS_ECONOMICS_EXPECTED_MANIFEST_SHA256", None)
    worktree = (tmp_path / "repo").resolve()
    worktree.mkdir()
    with pytest.raises(
        worker.KRXHistoricalWorkerEntrypointError,
        match="frozen scope not code-pinned",
    ):
        worker.finalize_status_economics_metadata(
            environment=_env(tmp_path),
            git_worktree=str(worktree),
            state_loader=lambda *args, **kwargs: {
                "value": _state(),
                "metadata_sha256": "1" * 64,
            },
            manifest_loader=lambda *args, **kwargs: {
                "value": _manifest(),
                "metadata_sha256": "b" * 64,
            },
            batch_loader=lambda *args, **kwargs: {
                "value": _batch(),
                "metadata_sha256": "c" * 64,
            },
        )


def test_status_economics_finalizer_is_network_free_and_metadata_only(
    tmp_path,
    monkeypatch,
):
    _pin(monkeypatch)
    worktree = (tmp_path / "repo").resolve()
    worktree.mkdir()

    out = worker.finalize_status_economics_metadata(
        environment=_env(tmp_path),
        git_worktree=str(worktree),
        state_loader=lambda *args, **kwargs: {
            "value": _state(),
            "metadata_sha256": "1" * 64,
        },
        manifest_loader=lambda *args, **kwargs: {
            "value": _manifest(),
            "metadata_sha256": "b" * 64,
        },
        batch_loader=lambda *args, **kwargs: {
            "value": _batch(),
            "metadata_sha256": "c" * 64,
        },
    )

    assert out["mode"] == "FINALIZE_STATUS_ECONOMICS_METADATA"
    assert out["status"] == "COMPLETE"
    assert out["expected_task_count"] == 5
    assert out["completed_task_count"] == 5
    assert out["failed_task_count"] == 0
    assert out["resumed_task_count"] == 1
    assert out["network_request_attempt_count"] == 4
    assert out["private_batch_metadata_sha256"] == "c" * 64
    assert out["network_request_attempted"] is False
    assert out["raw_rows_emitted"] is False
    assert out["security_identifiers_emitted"] is False
    assert out["cleanup_price_context_complete"] is True
    assert out["exact_status_economics_ready"] is False
    assert out["realized_fill_economics_proven"] is False
    assert out["realized_recovery_cashflows_proven"] is False
    assert out["sealed_holdout_authorized"] is False
    assert out["live_trading_authorized"] is False


def test_status_economics_finalizer_rejects_manifest_or_batch_drift(
    tmp_path,
    monkeypatch,
):
    _pin(monkeypatch)
    worktree = (tmp_path / "repo").resolve()
    worktree.mkdir()

    with pytest.raises(
        worker.KRXHistoricalWorkerEntrypointError,
        match="manifest metadata SHA-256 drift",
    ):
        worker.finalize_status_economics_metadata(
            environment=_env(tmp_path),
            git_worktree=str(worktree),
            state_loader=lambda *args, **kwargs: {
                "value": _state(),
                "metadata_sha256": "1" * 64,
            },
            manifest_loader=lambda *args, **kwargs: {
                "value": _manifest(),
                "metadata_sha256": "0" * 64,
            },
            batch_loader=lambda *args, **kwargs: {
                "value": _batch(),
                "metadata_sha256": "c" * 64,
            },
        )

    batch = _batch()
    batch["network_request_attempt_count"] = 3
    with pytest.raises(
        worker.KRXHistoricalWorkerEntrypointError,
        match="network/resume accounting drift",
    ):
        worker.finalize_status_economics_metadata(
            environment=_env(tmp_path),
            git_worktree=str(worktree),
            state_loader=lambda *args, **kwargs: {
                "value": _state(),
                "metadata_sha256": "1" * 64,
            },
            manifest_loader=lambda *args, **kwargs: {
                "value": _manifest(),
                "metadata_sha256": "b" * 64,
            },
            batch_loader=lambda *args, **kwargs: {
                "value": batch,
                "metadata_sha256": "c" * 64,
            },
        )


def test_status_economics_finalizer_rejects_incomplete_or_claim_escalation(
    tmp_path,
    monkeypatch,
):
    _pin(monkeypatch)
    worktree = (tmp_path / "repo").resolve()
    worktree.mkdir()

    state = _state()
    state["status"] = "IN_PROGRESS"
    state["phase_complete"] = False
    with pytest.raises(
        worker.KRXHistoricalWorkerEntrypointError,
        match="phase is not COMPLETE",
    ):
        worker.finalize_status_economics_metadata(
            environment=_env(tmp_path),
            git_worktree=str(worktree),
            state_loader=lambda *args, **kwargs: {
                "value": state,
                "metadata_sha256": "1" * 64,
            },
            manifest_loader=lambda *args, **kwargs: {
                "value": _manifest(),
                "metadata_sha256": "b" * 64,
            },
            batch_loader=lambda *args, **kwargs: {
                "value": _batch(),
                "metadata_sha256": "c" * 64,
            },
        )

    batch = _batch()
    batch["exact_status_economics_ready"] = True
    with pytest.raises(
        worker.KRXHistoricalWorkerEntrypointError,
        match="exact_status_economics_ready illegally true",
    ):
        worker.finalize_status_economics_metadata(
            environment=_env(tmp_path),
            git_worktree=str(worktree),
            state_loader=lambda *args, **kwargs: {
                "value": _state(),
                "metadata_sha256": "1" * 64,
            },
            manifest_loader=lambda *args, **kwargs: {
                "value": _manifest(),
                "metadata_sha256": "b" * 64,
            },
            batch_loader=lambda *args, **kwargs: {
                "value": batch,
                "metadata_sha256": "c" * 64,
            },
        )
