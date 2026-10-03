import pytest

import research_v1_krx_historical_worker_entrypoint as worker


def _summary():
    return {
        "task_count": 5,
        "task_set_fingerprint_sha256": "a" * 64,
    }


def test_status_economics_scope_is_blocked_until_code_pinned():
    assert worker.STATUS_ECONOMICS_EXPECTED_TASK_COUNT is None
    assert worker.STATUS_ECONOMICS_EXPECTED_TASK_SET_SHA256 is None
    assert worker.STATUS_ECONOMICS_EXPECTED_MANIFEST_SHA256 is None

    with pytest.raises(
        worker.KRXHistoricalWorkerEntrypointError,
        match="frozen scope not code-pinned",
    ):
        worker._require_frozen_status_economics_summary(_summary())


def test_status_economics_scope_passes_only_exact_pinned_values(monkeypatch):
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

    worker._require_frozen_status_economics_summary(
        _summary(),
        manifest_metadata_sha256="b" * 64,
    )

    bad = _summary()
    bad["task_count"] = 4
    with pytest.raises(
        worker.KRXHistoricalWorkerEntrypointError,
        match="frozen task count drift",
    ):
        worker._require_frozen_status_economics_summary(bad)

    bad = _summary()
    bad["task_set_fingerprint_sha256"] = "0" * 64
    with pytest.raises(
        worker.KRXHistoricalWorkerEntrypointError,
        match="frozen task-set fingerprint drift",
    ):
        worker._require_frozen_status_economics_summary(bad)

    with pytest.raises(
        worker.KRXHistoricalWorkerEntrypointError,
        match="frozen manifest metadata SHA-256 drift",
    ):
        worker._require_frozen_status_economics_summary(
            _summary(),
            manifest_metadata_sha256="0" * 64,
        )
