import pytest

import research_v1_krx_historical_worker_entrypoint as worker


def _summary():
    return {
        "task_count": 27,
        "task_set_fingerprint_sha256": "b3738dca89ab5cb6966a1e3158f995b75cbf6e2ae2cd4c199f02c95a8ba4c1d8",
    }


def test_status_economics_scope_is_code_pinned_to_network_free_preparation():
    assert worker.STATUS_ECONOMICS_EXPECTED_TASK_COUNT == 27
    assert worker.STATUS_ECONOMICS_EXPECTED_TASK_SET_SHA256 == "b3738dca89ab5cb6966a1e3158f995b75cbf6e2ae2cd4c199f02c95a8ba4c1d8"
    assert worker.STATUS_ECONOMICS_EXPECTED_MANIFEST_SHA256 == "e744530ae017510477c7353c917b5d4c9d8cccec8c0ed4543b6434b133628a79"

    worker._require_frozen_status_economics_summary(
        _summary(),
        manifest_metadata_sha256=worker.STATUS_ECONOMICS_EXPECTED_MANIFEST_SHA256,
    )


def test_status_economics_scope_rejects_any_drift(monkeypatch):
    bad = _summary()
    bad["task_count"] = 26
    with pytest.raises(worker.KRXHistoricalWorkerEntrypointError, match="frozen task count drift"):
        worker._require_frozen_status_economics_summary(bad)

    bad = _summary()
    bad["task_set_fingerprint_sha256"] = "0" * 64
    with pytest.raises(worker.KRXHistoricalWorkerEntrypointError, match="frozen task-set fingerprint drift"):
        worker._require_frozen_status_economics_summary(bad)

    with pytest.raises(worker.KRXHistoricalWorkerEntrypointError, match="frozen manifest metadata SHA-256 drift"):
        worker._require_frozen_status_economics_summary(
            _summary(),
            manifest_metadata_sha256="0" * 64,
        )

    monkeypatch.setattr(worker, "STATUS_ECONOMICS_EXPECTED_TASK_COUNT", None)
    with pytest.raises(worker.KRXHistoricalWorkerEntrypointError, match="frozen scope not code-pinned"):
        worker._require_frozen_status_economics_summary(_summary())
