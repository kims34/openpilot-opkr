import pandas as pd
import pytest

from research_v1_krx_historical_identity import (
    KRXHistoricalIdentityError,
    identity_summary,
    reconstruct_historical_kospi_episodes,
)


def _current():
    return pd.DataFrame([
        {
            "ISU_CD":"KR7005930003","ISU_SRT_CD":"005930","ISU_NM":"삼성전자",
            "LIST_DD":"19750611","MKT_TP_NM":"KOSPI","SECUGRP_NM":"주권",
            "KIND_STKCERT_TP_NM":"보통주",
        },
        {
            "ISU_CD":"KR7005931001","ISU_SRT_CD":"005935","ISU_NM":"삼성전자우",
            "LIST_DD":"19890313","MKT_TP_NM":"KOSPI","SECUGRP_NM":"주권",
            "KIND_STKCERT_TP_NM":"우선주",
        },
    ])


def _new():
    return pd.DataFrame([
        {
            "종목코드":"123456","종목명":"신규보통","시장구분":"유가증권시장",
            "증권구분":"주권","주식종류":"보통주","상장일":"20200102","상장폐지일":"",
        },
        {
            "종목코드":"654321","종목명":"코스닥","시장구분":"코스닥",
            "증권구분":"주권","주식종류":"보통주","상장일":"20210101","상장폐지일":"",
        },
    ])


def _delisted():
    return pd.DataFrame([
        {
            "종목코드":"222222","종목명":"상폐보통","시장구분":"유가증권",
            "증권구분":"주권","주식종류":"보통주","상장일":"20160104","폐지일":"20221230",
        }
    ])


def test_reconstructs_kospi_common_stock_episodes_without_name_join():
    out=reconstruct_historical_kospi_episodes(
        current_listed=_current(),new_listing=_new(),delisted=_delisted()
    )
    assert set(out["short_code"]) == {"005930","123456","222222"}
    assert "005935" not in set(out["short_code"])
    assert "654321" not in set(out["short_code"])
    samsung=out[out["short_code"].eq("005930")].iloc[0]
    assert samsung["episode_key"] == "KOSPI|005930|1975-06-11"
    assert samsung["coverage_start"] == pd.Timestamp("2015-06-15")
    assert samsung["coverage_end"] == pd.Timestamp("2026-10-01")
    assert samsung["standard_code"] == "KR7005930003"


def test_merges_current_and_new_listing_same_episode():
    current=pd.DataFrame([{
        "ISU_CD":"KR7123450000","ISU_SRT_CD":"123456","ISU_NM":"신규보통",
        "LIST_DD":"20200102","MKT_TP_NM":"KOSPI","SECUGRP_NM":"주권",
        "KIND_STKCERT_TP_NM":"보통주",
    }])
    out=reconstruct_historical_kospi_episodes(
        current_listed=current,new_listing=_new(),delisted=_delisted()
    )
    row=out[out["short_code"].eq("123456")].iloc[0]
    assert row["source_current"]
    assert row["source_new_listing"]
    assert row["standard_code"] == "KR7123450000"


def test_conflicting_delist_dates_fail_closed():
    new=_new().copy()
    new.loc[new["종목코드"].eq("123456"),"상장폐지일"]="20250101"
    delisted=pd.concat([
        _delisted(),
        pd.DataFrame([{
            "종목코드":"123456","종목명":"신규보통","시장구분":"KOSPI",
            "증권구분":"주권","주식종류":"보통주","상장일":"20200102","폐지일":"20250201",
        }])
    ],ignore_index=True)
    with pytest.raises(KRXHistoricalIdentityError,match="conflicting delisting_date"):
        reconstruct_historical_kospi_episodes(
            current_listed=_current(),new_listing=new,delisted=delisted
        )


def test_overlapping_reused_short_code_episodes_fail_closed():
    new=pd.DataFrame([
        {"종목코드":"333333","종목명":"A","시장구분":"KOSPI","증권구분":"주권","주식종류":"보통주","상장일":"20160101","상장폐지일":"20210101"},
        {"종목코드":"333333","종목명":"B","시장구분":"KOSPI","증권구분":"주권","주식종류":"보통주","상장일":"20200101","상장폐지일":""},
    ])
    with pytest.raises(KRXHistoricalIdentityError,match="overlapping listing episodes"):
        reconstruct_historical_kospi_episodes(
            current_listed=_current(),new_listing=new,delisted=_delisted()
        )


def test_summary_emits_counts_not_identifiers():
    out=reconstruct_historical_kospi_episodes(
        current_listed=_current(),new_listing=_new(),delisted=_delisted()
    )
    s=identity_summary(out)
    assert s["episode_count"] == 3
    assert s["raw_identifiers_emitted"] is False
    assert "symbols" not in s
