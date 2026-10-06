from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import pytest

from research_v1_krx_expected_scope_executor import (
    DAILY_ENDPOINT,
    MASTER_ENDPOINT,
    KRXExpectedScopeExecutorError,
    execute_expected_scope_date,
)
from research_v1_krx_expected_scope_preflight import CONSENT_SENTINEL
from research_v1_krx_historical_worker_core import FetchResult


EVAL = datetime(2026, 10, 2, 12, 45, tzinfo=timezone.utc)


def _env(tmp_path, *, consent=True, service="indexalert-krx-historical-worker"):
    out = {
        "KRX_AUTH_KEY": "present",
        "KRX_PRIVATE_RAW_DIR": str((tmp_path / "private").resolve()),
        "INDEXALERT_KRX_HIST_WORKER_ROLE": "DEDICATED_ONE_SHOT",
        "RAILWAY_SERVICE_NAME": service,
    }
    if consent:
        out["KRX_EXPECTED_SCOPE_ATTESTATION_CONSENT"] = CONSENT_SENTINEL
    return out


def _result(frame, *, raw=b'{"OutBlock_1":[]}', endpoint="daily"):
    return FetchResult(
        raw_bytes=raw,
        response_frame=frame,
        retrieved_at=EVAL.isoformat(),
        transport_status=f"FAKE_{endpoint}",
        network_request_attempted=True,
    )


def test_expected_scope_executor_blocks_before_fetch_without_separate_consent(tmp_path):
    worktree = (tmp_path / "repo").resolve()
    worktree.mkdir()
    calls = []

    with pytest.raises(KRXExpectedScopeExecutorError, match="preflight blocked"):
        execute_expected_scope_date(
            requested_date="20260923",
            environment=_env(tmp_path, consent=False),
            git_worktree=str(worktree),
            fetcher=lambda **kwargs: calls.append(kwargs),
            evaluation_time=EVAL,
        )
    assert calls == []


def test_expected_scope_executor_rejects_wrong_service_before_fetch(tmp_path):
    worktree = (tmp_path / "repo").resolve()
    worktree.mkdir()
    calls = []

    with pytest.raises(KRXExpectedScopeExecutorError, match="preflight blocked"):
        execute_expected_scope_date(
            requested_date="20260923",
            environment=_env(tmp_path, service="some-private-worker"),
            git_worktree=str(worktree),
            fetcher=lambda **kwargs: calls.append(kwargs),
            evaluation_time=EVAL,
        )
    assert calls == []


def test_empty_daily_date_makes_one_request_and_never_invents_scope(tmp_path):
    worktree = (tmp_path / "repo").resolve()
    worktree.mkdir()
    calls = []

    def fetcher(**kwargs):
        calls.append(kwargs)
        assert kwargs["endpoint"] == DAILY_ENDPOINT
        assert kwargs["params"] == {"basDd": "20260927"}
        assert kwargs["network_authorized"] is True
        return _result(
            pd.DataFrame(columns=["BAS_DD","ISU_CD","ISU_NM","MKT_NM"]),
            raw=b'{"OutBlock_1":[]}',
        )

    out = execute_expected_scope_date(
        requested_date="2026-09-27",
        environment=_env(tmp_path),
        git_worktree=str(worktree),
        fetcher=fetcher,
        evaluation_time=EVAL,
    )
    assert len(calls) == 1
    assert out["official_trading_date_observed"] is False
    assert out["investor_expected_key_count"] == 0
    assert out["status_expected_key_count"] == 0
    assert out["master_request_performed"] is False
    assert out["network_request_attempted"] is True
    assert out["raw_rows_emitted"] is False
    assert out["security_identifiers_emitted"] is False
    assert out["source_gate_c_closed"] is False
    assert out["feature_performance_testing_authorized"] is False
    assert out["sealed_holdout_authorized"] is False
    assert out["live_trading_authorized"] is False
    assert "005930" not in str(out)
    assert (tmp_path / "private" / out["private_scope_relpath"]).is_file()


def test_trading_date_fetches_same_date_master_and_keeps_keys_private(tmp_path):
    worktree = (tmp_path / "repo").resolve()
    worktree.mkdir()
    calls = []

    daily = pd.DataFrame([
        {"BAS_DD":"20260923","ISU_CD":"KR7005930003","ISU_NM":"삼성전자","MKT_NM":"KOSPI"},
        {"BAS_DD":"20260923","ISU_CD":"KR7000660001","ISU_NM":"SK하이닉스","MKT_NM":"KOSPI"},
    ])
    master = pd.DataFrame([
        {"ISU_CD":"KR7005930003","ISU_SRT_CD":"005930","ISU_NM":"삼성전자","LIST_DD":"19750611","MKT_TP_NM":"KOSPI","SECUGRP_NM":"주권","KIND_STKCERT_TP_NM":"보통주"},
        {"ISU_CD":"KR7000660001","ISU_SRT_CD":"000660","ISU_NM":"SK하이닉스","LIST_DD":"19961226","MKT_TP_NM":"KOSPI","SECUGRP_NM":"주권","KIND_STKCERT_TP_NM":"보통주"},
    ])

    def fetcher(**kwargs):
        calls.append(kwargs)
        assert kwargs["params"] == {"basDd": "20260923"}
        assert kwargs["network_authorized"] is True
        if kwargs["endpoint"] == DAILY_ENDPOINT:
            return _result(daily, raw=b'{"OutBlock_1":[{"BAS_DD":"20260923"}]}')
        assert kwargs["endpoint"] == MASTER_ENDPOINT
        return _result(master, raw=b'{"OutBlock_1":[{"ISU_CD":"KR7005930003"}]}', endpoint="master")

    out = execute_expected_scope_date(
        requested_date="20260923",
        environment=_env(tmp_path),
        git_worktree=str(worktree),
        fetcher=fetcher,
        evaluation_time=EVAL,
    )
    assert [x["endpoint"] for x in calls] == [DAILY_ENDPOINT, MASTER_ENDPOINT]
    assert out["official_trading_date_observed"] is True
    assert out["daily_trade_rows"] == 2
    assert out["security_master_rows"] == 2
    assert out["investor_expected_key_count"] == 2
    assert out["status_expected_key_count"] == 2
    assert out["master_request_performed"] is True
    assert len(out["daily_receipt_fingerprint_sha256"]) == 64
    assert len(out["master_receipt_fingerprint_sha256"]) == 64
    assert out["source_gate_c_closed"] is False
    assert out["source_gate_d_closed"] is False
    assert out["source_gate_e_closed"] is False
    assert "005930" not in str(out)
    assert "KR7005930003" not in str(out)

    private = (
        tmp_path / "private" / out["private_scope_relpath"]
    ).read_text(encoding="utf-8")
    assert "005930" in private
    assert "KR7005930003" in private


def test_daily_response_date_mismatch_fails_closed(tmp_path):
    worktree = (tmp_path / "repo").resolve()
    worktree.mkdir()
    daily = pd.DataFrame([
        {"BAS_DD":"20260922","ISU_CD":"KR7005930003","ISU_NM":"삼성전자","MKT_NM":"KOSPI"},
    ])
    calls = []

    def fetcher(**kwargs):
        calls.append(kwargs)
        if kwargs["endpoint"] == DAILY_ENDPOINT:
            return _result(daily, raw=b'{"OutBlock_1":[{"BAS_DD":"20260922"}]}')
        master = pd.DataFrame([
            {"ISU_CD":"KR7005930003","ISU_SRT_CD":"005930","ISU_NM":"삼성전자","LIST_DD":"19750611","MKT_TP_NM":"KOSPI","SECUGRP_NM":"주권","KIND_STKCERT_TP_NM":"보통주"},
        ])
        return _result(master, endpoint="master")

    with pytest.raises(Exception, match="exactly match"):
        execute_expected_scope_date(
            requested_date="20260923",
            environment=_env(tmp_path),
            git_worktree=str(worktree),
            fetcher=fetcher,
            evaluation_time=EVAL,
        )
    assert len(calls) == 2


def test_same_request_same_payload_reuses_immutable_receipt_and_scope(tmp_path):
    worktree = (tmp_path / "repo").resolve()
    worktree.mkdir()
    calls = []

    daily = pd.DataFrame([
        {"BAS_DD":"20260923","ISU_CD":"KR7005930003","ISU_NM":"삼성전자","MKT_NM":"KOSPI"},
    ])
    master = pd.DataFrame([
        {"ISU_CD":"KR7005930003","ISU_SRT_CD":"005930","ISU_NM":"삼성전자","LIST_DD":"19750611","MKT_TP_NM":"KOSPI","SECUGRP_NM":"주권","KIND_STKCERT_TP_NM":"보통주"},
    ])

    def fetcher(**kwargs):
        calls.append(kwargs["endpoint"])
        if kwargs["endpoint"] == DAILY_ENDPOINT:
            return _result(daily, raw=b'{"OutBlock_1":[{"BAS_DD":"20260923","v":"same"}]}')
        return _result(master, raw=b'{"OutBlock_1":[{"ISU_CD":"KR7005930003","v":"same"}]}', endpoint="master")

    first = execute_expected_scope_date(
        requested_date="20260923",
        environment=_env(tmp_path),
        git_worktree=str(worktree),
        fetcher=fetcher,
        evaluation_time=EVAL,
    )
    second = execute_expected_scope_date(
        requested_date="20260923",
        environment=_env(tmp_path),
        git_worktree=str(worktree),
        fetcher=fetcher,
        evaluation_time=EVAL,
    )

    assert len(calls) == 4
    assert first["private_scope_relpath"] == second["private_scope_relpath"]
    assert first["private_scope_metadata_sha256"] == second["private_scope_metadata_sha256"]
    assert len(list((tmp_path / "private" / "expected_scope" / "dates" / "20260923").glob("*.json"))) == 1
    assert len(list((tmp_path / "private" / "expected_scope" / "receipts" / "20260923" / "stk_bydd_trd").glob("*.json"))) == 1
    assert len(list((tmp_path / "private" / "expected_scope" / "receipts" / "20260923" / "stk_isu_base_info").glob("*.json"))) == 1


def test_same_request_different_payload_fails_reconciliation_without_overwrite(tmp_path):
    worktree = (tmp_path / "repo").resolve()
    worktree.mkdir()

    daily1 = pd.DataFrame([
        {"BAS_DD":"20260923","ISU_CD":"KR7005930003","ISU_NM":"삼성전자","MKT_NM":"KOSPI"},
    ])
    daily2 = pd.DataFrame([
        {"BAS_DD":"20260923","ISU_CD":"KR7000660001","ISU_NM":"SK하이닉스","MKT_NM":"KOSPI"},
    ])
    master = pd.DataFrame([
        {"ISU_CD":"KR7005930003","ISU_SRT_CD":"005930","ISU_NM":"삼성전자","LIST_DD":"19750611","MKT_TP_NM":"KOSPI","SECUGRP_NM":"주권","KIND_STKCERT_TP_NM":"보통주"},
    ])

    phase = {"second": False}
    def fetcher(**kwargs):
        if kwargs["endpoint"] == DAILY_ENDPOINT:
            frame = daily2 if phase["second"] else daily1
            raw = b'{"OutBlock_1":[{"BAS_DD":"20260923","v":"two"}]}' if phase["second"] else b'{"OutBlock_1":[{"BAS_DD":"20260923","v":"one"}]}'
            return _result(frame, raw=raw)
        return _result(master, raw=b'{"OutBlock_1":[{"ISU_CD":"KR7005930003"}]}', endpoint="master")

    execute_expected_scope_date(
        requested_date="20260923",
        environment=_env(tmp_path),
        git_worktree=str(worktree),
        fetcher=fetcher,
        evaluation_time=EVAL,
    )
    receipt_dir = tmp_path / "private" / "expected_scope" / "receipts" / "20260923" / "stk_bydd_trd"
    before = sorted(p.name for p in receipt_dir.glob("*.json"))
    assert len(before) == 1

    phase["second"] = True
    with pytest.raises(KRXExpectedScopeExecutorError, match="conflicting payload"):
        execute_expected_scope_date(
            requested_date="20260923",
            environment=_env(tmp_path),
            git_worktree=str(worktree),
            fetcher=fetcher,
            evaluation_time=EVAL,
        )

    after = sorted(p.name for p in receipt_dir.glob("*.json"))
    assert after == before


@pytest.mark.parametrize("field,value", [
    ("transport_status", None), ("transport_status", False),
    ("transport_status", 200), ("transport_status", {}),
    ("transport_status", []), ("transport_status", ""),
    ("transport_status", "   "),
    ("retrieved_at", None), ("retrieved_at", False),
    ("retrieved_at", 0), ("retrieved_at", EVAL),
    ("retrieved_at", ""), ("retrieved_at", "NaT"),
    ("retrieved_at", "not-a-date"), ("retrieved_at", "2026-10-02T12:45:00"),
])
def test_fetch_metadata_rejected_before_private_write(tmp_path, monkeypatch, field, value):
    from dataclasses import replace
    import research_v1_krx_expected_scope_executor as executor

    worktree = (tmp_path / "repo").resolve()
    worktree.mkdir()
    calls = []
    def forbidden_write(*args, **kwargs):
        pytest.fail("malformed fetch metadata must fail before private write")
    monkeypatch.setattr(executor, "write_raw_object", forbidden_write)
    result = replace(_result(pd.DataFrame()), **{field: value})
    def fetcher(**kwargs):
        calls.append(kwargs)
        return result
    with pytest.raises(KRXExpectedScopeExecutorError, match=field):
        execute_expected_scope_date(
            requested_date="20260927", environment=_env(tmp_path),
            git_worktree=str(worktree), fetcher=fetcher, evaluation_time=EVAL,
        )
    assert len(calls) == 1
    assert not (tmp_path / "private" / "expected_scope").exists()


@pytest.mark.parametrize("stamp", ["2026-10-02T12:45:00+00:00", "2026-10-02T21:45:00+09:00"])
def test_fetch_metadata_preserves_explicit_transport_and_aware_time(stamp):
    from dataclasses import replace
    from research_v1_krx_expected_scope_executor import _ensure_fetch_result

    # Synthetic fixture metadata only; does not assert genuine transport origin.
    result = replace(_result(pd.DataFrame()), retrieved_at=stamp)
    assert _ensure_fetch_result(result) is result
    assert result.transport_status == "FAKE_daily"
