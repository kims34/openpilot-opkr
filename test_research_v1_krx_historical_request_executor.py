from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import pytest

from research_v1_krx_historical_acquisition_preflight import CONSENT_SENTINEL
from research_v1_krx_historical_request_executor import (
    CLEANUP_CURRENT,
    KRXHistoricalRequestExecutorError,
    execute_request_spec,
    validate_request_spec,
)
from research_v1_krx_historical_worker_core import FetchResult, KRXHistoricalWorkerError


EVAL=datetime(2026,10,2,10,45,tzinfo=timezone.utc)


def _catalog(name):
    specs={
        "investor_trading_individual_daily":{
            "bld":"dbms/MDC/STAT/standard/MDCSTAT02303",
            "method":"csv",
            "menu_id":"MDC0201020302",
            "defaults":{"askBid":"3","trdVolVal":"2","isuCd2":""},
            "required":["isuCd","strtDd","endDd"],
        },
        "trading_halt":{
            "bld":"dbms/MDC/STAT/issue/MDCSTAT21301",
            "method":"json",
            "menu_id":"MDC0202",
            "defaults":{"param1isuCd_finder_stkisu0_3":"ALL"},
            "required":["isuCd","isuCd2","strtDd","endDd"],
            "max_period_days":730,
        },
        "new_listing":{
            "bld":"dbms/MDC/STAT/issue/MDCSTAT20001",
            "method":"csv",
            "menu_id":"MDC0201",
            "defaults":{"mktId":"ALL"},
            "required":["strtDd","endDd"],
        },
        "delisted":{
            "bld":"dbms/MDC/STAT/issue/MDCSTAT23801",
            "method":"csv",
            "menu_id":"MDC0202",
            "defaults":{"mktId":"ALL"},
            "required":["strtDd","endDd"],
        },
        "delisted_stock_price":{
            "bld":"dbms/MDC/STAT/issue/MDCSTAT23902",
            "method":"csv",
            "menu_id":"MDC0202",
            "defaults":{"isuCd2":""},
            "required":["isuCd","strtDd","endDd"],
        },
    }
    return specs[name]


def _env(tmp_path, *, consent=True):
    out={
        "KRX_ID":"present",
        "KRX_PW":"present",
        "KRX_AUTH_KEY":"present",
        "KRX_PRIVATE_RAW_DIR":str((tmp_path/"private").resolve()),
        "INDEXALERT_KRX_HIST_WORKER_ROLE":"DEDICATED_ONE_SHOT",
        "RAILWAY_SERVICE_NAME":"indexalert-krx-historical-worker",
    }
    if consent:
        out["KRX_HISTORICAL_ACQUISITION_CONSENT"]=CONSENT_SENTINEL
    return out


def _fake_dm(**kwargs):
    return FetchResult(
        raw_bytes=b"date,value\n20260921,1\n",
        response_frame=pd.DataFrame({"date":["2026-09-21"],"value":[1]}),
        retrieved_at="2026-10-02T19:45:00+09:00",
        transport_status="FAKE_DM_OK",
        network_request_attempted=False,
    )


def _fake_openapi(**kwargs):
    return FetchResult(
        raw_bytes=b'{"OutBlock_1":[{"ISU_CD":"KR7005930003","ISU_SRT_CD":"005930"}]}',
        response_frame=pd.DataFrame({"ISU_CD":["KR7005930003"],"ISU_SRT_CD":["005930"]}),
        retrieved_at="2026-10-02T19:45:00+09:00",
        transport_status="FAKE_OPENAPI_OK",
        network_request_attempted=False,
    )


def test_request_spec_resolves_investor_defaults_and_standard_code():
    out=validate_request_spec(
        {
            "kind":"investor_trading_individual_daily",
            "params":{"isuCd":"KR7005930003","strtDd":"20260101","endDd":"20261231"},
        },
        catalog_getter=_catalog,
    )
    assert out["source_family"]=="KRX_INVESTOR_FLOW"
    assert out["dataset_identifier"]=="MDCSTAT02303"
    assert out["params"]["askBid"]=="3"
    assert out["params"]["trdVolVal"]=="2"
    assert out["params"]["isuCd"]=="KR7005930003"


def test_request_spec_rejects_short_code_as_standard_code_and_oversize_halt_window():
    with pytest.raises(KRXHistoricalRequestExecutorError,match="12-character standard code"):
        validate_request_spec(
            {
                "kind":"investor_trading_individual_daily",
                "params":{"isuCd":"005930","strtDd":"20260101","endDd":"20261231"},
            },
            catalog_getter=_catalog,
        )

    with pytest.raises(KRXHistoricalRequestExecutorError,match="exceeds max_period_days=730"):
        validate_request_spec(
            {
                "kind":"trading_halt",
                "params":{
                    "isuCd":"KR7000300004","isuCd2":"000300",
                    "strtDd":"20240101","endDd":"20260102",
                },
            },
            catalog_getter=_catalog,
        )


def test_trading_halt_accepts_official_alphanumeric_short_code():
    out = validate_request_spec(
        {
            "kind": "trading_halt",
            "params": {
                "isuCd": "KR7000300004",
                "isuCd2": "a12345",
                "strtDd": "20250101",
                "endDd": "20250131",
            },
        },
        catalog_getter=_catalog,
    )
    assert out["params"]["isuCd2"] == "A12345"


def test_trading_halt_rejects_non_ascii_or_non_alphanumeric_short_code():
    for bad in ("12345", "1234567", "12-345", "Ａ12345"):
        with pytest.raises(
            KRXHistoricalRequestExecutorError,
            match="six-character alphanumeric short code",
        ):
            validate_request_spec(
                {
                    "kind": "trading_halt",
                    "params": {
                        "isuCd": "KR7000300004",
                        "isuCd2": bad,
                        "strtDd": "20250101",
                        "endDd": "20250131",
                    },
                },
                catalog_getter=_catalog,
            )


def test_cleanup_current_is_snapshot_only_and_has_no_fake_historical_dates():
    out=validate_request_spec({"kind":CLEANUP_CURRENT,"params":{"mktId":"ALL"}})
    assert out["dataset_identifier"]=="MDCSTAT23701"
    assert out["params"]=={"mktId":"ALL"}
    with pytest.raises(KRXHistoricalRequestExecutorError,match="accepts only mktId=ALL"):
        validate_request_spec(
            {"kind":CLEANUP_CURRENT,"params":{"mktId":"ALL","strtDd":"20240101"}}
        )


def test_execute_investor_request_uses_worker_receipt_store_without_public_rows(tmp_path):
    worktree=(tmp_path/"repo").resolve()
    worktree.mkdir()
    out=execute_request_spec(
        spec={
            "kind":"investor_trading_individual_daily",
            "params":{"isuCd":"KR7005930003","strtDd":"20260921","endDd":"20260923"},
        },
        environment=_env(tmp_path),
        git_worktree=str(worktree),
        client_revision="offline-executor-test",
        catalog_getter=_catalog,
        dm_fetch=_fake_dm,
        evaluation_time=EVAL,
    )
    assert out["completed"] is True
    assert out["raw_rows_emitted"] is False
    assert out["response_rows"]==1
    assert out["feature_performance_testing_authorized"] is False
    assert list((tmp_path/"private"/"objects"/"sha256").rglob("*.bin"))


def test_execute_openapi_security_master_routes_through_same_private_worker(tmp_path):
    worktree=(tmp_path/"repo").resolve()
    worktree.mkdir()
    out=execute_request_spec(
        spec={"kind":"security_master","params":{"basDd":"20150615"}},
        environment=_env(tmp_path),
        git_worktree=str(worktree),
        client_revision="offline-openapi-executor-test",
        openapi_fetch=_fake_openapi,
        evaluation_time=EVAL,
    )
    assert out["completed"] is True
    assert out["response_rows"]==1
    assert out["sealed_holdout_authorized"] is False


def test_executor_never_calls_fetch_adapter_without_bulk_consent(tmp_path):
    worktree=(tmp_path/"repo").resolve()
    worktree.mkdir()
    calls=[]
    def forbidden(**kwargs):
        calls.append(kwargs)
        return _fake_dm(**kwargs)

    with pytest.raises(KRXHistoricalWorkerError,match="preflight blocked"):
        execute_request_spec(
            spec={
                "kind":"investor_trading_individual_daily",
                "params":{"isuCd":"KR7005930003","strtDd":"20260921","endDd":"20260923"},
            },
            environment=_env(tmp_path,consent=False),
            git_worktree=str(worktree),
            client_revision="blocked-test",
            catalog_getter=_catalog,
            dm_fetch=forbidden,
            evaluation_time=EVAL,
        )
    assert calls==[]
