from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import pytest

from research_v1_krx_historical_acquisition_preflight import CONSENT_SENTINEL
from research_v1_krx_historical_worker_core import (
    FetchResult,
    KRXHistoricalWorkerError,
    execute_private_request,
)


EVAL = datetime(2026, 10, 2, 9, 30, tzinfo=timezone.utc)


def _env(tmp_path: Path, *, consent: bool = True) -> dict[str, str]:
    out = {
        "KRX_ID": "present",
        "KRX_PW": "present",
        "KRX_AUTH_KEY": "present",
        "KRX_PRIVATE_RAW_DIR": str((tmp_path / "private-krx").resolve()),
    }
    if consent:
        out["KRX_HISTORICAL_ACQUISITION_CONSENT"] = CONSENT_SENTINEL
    return out


def _request():
    return {
        "isuCd": "KR7005930003",
        "strtDd": "20260921",
        "endDd": "20260923",
        "askBid": "3",
        "trdVolVal": "2",
    }


def _fake_result(network=False):
    return FetchResult(
        raw_bytes=b'{"OutBlock_1":[{"TRD_DD":"20260921"}]}',
        response_frame=pd.DataFrame(
            {
                "TRD_DD": ["2026-09-21", "2026-09-22"],
                "NET_BID_TRDVAL": [100, -20],
            }
        ),
        retrieved_at="2026-10-02T18:30:00+09:00",
        transport_status="FAKE_OK",
        network_request_attempted=network,
    )


def test_worker_blocks_before_fetcher_without_exact_bulk_consent(tmp_path):
    worktree = (tmp_path / "repo").resolve()
    worktree.mkdir()
    calls = []

    def fetcher(_):
        calls.append(1)
        return _fake_result()

    with pytest.raises(KRXHistoricalWorkerError, match="preflight blocked"):
        execute_private_request(
            environment=_env(tmp_path, consent=False),
            git_worktree=str(worktree),
            source_family="KRX_INVESTOR_FLOW",
            dataset_identifier="MDCSTAT02303",
            request_metadata=_request(),
            client_revision="offline-test",
            fetcher=fetcher,
            evaluation_time=EVAL,
        )
    assert calls == []


def test_worker_persists_private_raw_receipt_manifest_and_checkpoint_offline(tmp_path):
    worktree = (tmp_path / "repo").resolve()
    worktree.mkdir()
    calls = []

    def fetcher(request):
        calls.append(dict(request))
        return _fake_result(network=False)

    out = execute_private_request(
        environment=_env(tmp_path),
        git_worktree=str(worktree),
        source_family="KRX_INVESTOR_FLOW",
        dataset_identifier="MDCSTAT02303",
        request_metadata=_request(),
        client_revision="offline-test",
        fetcher=fetcher,
        evaluation_time=EVAL,
    )
    assert len(calls) == 1
    assert out["completed"] is True
    assert out["resumed"] is False
    assert out["network_request_attempted"] is False
    assert out["raw_rows_emitted"] is False
    assert out["response_rows"] == 2
    assert len(out["raw_object_sha256"]) == 64
    assert len(out["receipt_fingerprint_sha256"]) == 64
    assert out["feature_performance_testing_authorized"] is False
    assert out["sealed_holdout_authorized"] is False
    assert out["live_trading_authorized"] is False

    root = Path(_env(tmp_path)["KRX_PRIVATE_RAW_DIR"])
    assert list((root / "objects" / "sha256").rglob("*.bin"))
    assert list((root / "receipts").rglob("*.json"))
    assert list((root / "manifests").rglob("*.json"))
    assert list((root / "checkpoints").rglob("*.json"))


def test_worker_resume_verifies_private_object_and_does_not_refetch(tmp_path):
    worktree = (tmp_path / "repo").resolve()
    worktree.mkdir()
    first_calls = []

    def first_fetcher(request):
        first_calls.append(dict(request))
        return _fake_result(network=False)

    first = execute_private_request(
        environment=_env(tmp_path),
        git_worktree=str(worktree),
        source_family="KRX_INVESTOR_FLOW",
        dataset_identifier="MDCSTAT02303",
        request_metadata=_request(),
        client_revision="offline-test",
        fetcher=first_fetcher,
        evaluation_time=EVAL,
    )
    assert len(first_calls) == 1

    def forbidden_fetcher(_):
        raise AssertionError("resume must not invoke fetcher")

    resumed = execute_private_request(
        environment=_env(tmp_path),
        git_worktree=str(worktree),
        source_family="KRX_INVESTOR_FLOW",
        dataset_identifier="MDCSTAT02303",
        request_metadata=_request(),
        client_revision="offline-test",
        fetcher=forbidden_fetcher,
        evaluation_time=EVAL,
    )
    assert resumed["completed"] is True
    assert resumed["resumed"] is True
    assert resumed["network_request_attempted"] is False
    assert resumed["raw_object_sha256"] == first["raw_object_sha256"]
    assert resumed["receipt_fingerprint_sha256"] == first["receipt_fingerprint_sha256"]


def test_worker_resume_fails_closed_after_raw_object_tamper(tmp_path):
    worktree = (tmp_path / "repo").resolve()
    worktree.mkdir()

    first = execute_private_request(
        environment=_env(tmp_path),
        git_worktree=str(worktree),
        source_family="KRX_INVESTOR_FLOW",
        dataset_identifier="MDCSTAT02303",
        request_metadata=_request(),
        client_revision="offline-test",
        fetcher=lambda _: _fake_result(network=False),
        evaluation_time=EVAL,
    )
    root = Path(_env(tmp_path)["KRX_PRIVATE_RAW_DIR"])
    target = next((root / "objects" / "sha256").rglob(f"{first['raw_object_sha256']}.bin"))
    target.write_bytes(b"tampered")
    target.chmod(0o600)

    with pytest.raises(Exception, match="checksum mismatch"):
        execute_private_request(
            environment=_env(tmp_path),
            git_worktree=str(worktree),
            source_family="KRX_INVESTOR_FLOW",
            dataset_identifier="MDCSTAT02303",
            request_metadata=_request(),
            client_revision="offline-test",
            fetcher=lambda _: (_ for _ in ()).throw(AssertionError("must not fetch")),
            evaluation_time=EVAL,
        )


def test_worker_rejects_unsupported_family_before_fetch(tmp_path):
    worktree = (tmp_path / "repo").resolve()
    worktree.mkdir()
    with pytest.raises(KRXHistoricalWorkerError, match="unsupported source family"):
        execute_private_request(
            environment=_env(tmp_path),
            git_worktree=str(worktree),
            source_family="KRX_UNKNOWN",
            dataset_identifier="UNKNOWN",
            request_metadata={"x": "1"},
            client_revision="offline-test",
            fetcher=lambda _: _fake_result(network=False),
            evaluation_time=EVAL,
        )
