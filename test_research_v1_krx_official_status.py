import pandas as pd
import pytest

from research_v1_krx_official_status import (
    KRXOfficialStatusError,
    KRX_DELIST_PRICE_SOURCE,
    KRX_DELIST_SOURCE,
    KRX_HALT_SOURCE,
    KRX_OPENAPI_BASIC_SOURCE,
    audit_official_coverage,
    delisted_mask_for_dates,
    halt_mask_for_dates,
    normalise_basic_info,
    normalise_delisted_prices,
    normalise_delisting_history,
    normalise_halt_history,
)


def _basic():
    return pd.DataFrame([
        {
            "ISU_CD": "KR7005930003",
            "ISU_SRT_CD": "005930",
            "ISU_NM": "삼성전자",
            "MKT_TP_NM": "KOSPI",
            "SECUGRP_NM": "주권",
            "KIND_STKCERT_TP_NM": "보통주",
            "LIST_DD": "1975/06/11",
        },
        {
            "ISU_CD": "KR7005931001",
            "ISU_SRT_CD": "005935",
            "ISU_NM": "삼성전자우",
            "MKT_TP_NM": "KOSPI",
            "SECUGRP_NM": "주권",
            "KIND_STKCERT_TP_NM": "구형우선주",
            "LIST_DD": "1989/09/25",
        },
    ])


def _halts():
    return pd.DataFrame([
        {
            "종목코드": "123456",
            "종목명": "가상종목",
            "시장구분": "KOSPI",
            "정지일": "2026-09-10",
            "재개일": "2026-09-15",
        },
        {
            "종목코드": "654321",
            "종목명": "가상장기정지",
            "시장구분": "KOSPI",
            "정지일": "2026-09-20",
            "재개일": "",
        },
    ])


def _delist():
    return pd.DataFrame([
        {
            "종목코드": "123456",
            "종목명": "가상종목",
            "시장구분": "KOSPI",
            "증권구분": "주권",
            "주식종류": "보통주",
            "상장일": "2010-01-04",
            "폐지일": "2026-09-30",
            "폐지사유": "테스트",
        }
    ])


def _delist_prices():
    return pd.DataFrame([
        {
            "일자": "2026-09-29",
            "종목코드": "123456",
            "종목명": "가상종목",
            "시가": 1000,
            "고가": 1050,
            "저가": 900,
            "종가": 950,
            "거래량": 10000,
            "거래대금": 9500000,
        }
    ])


def test_basic_info_uses_official_stock_type_not_symbol_name_heuristic():
    x = normalise_basic_info(
        _basic(),
        asof_date="2026-09-29",
        available_at="2026-09-29 20:00:00+09:00",
    ).set_index("symbol")
    assert x.loc["005930", "standard_code"] == "KR7005930003"
    assert bool(x.loc["005930", "common_stock_identity_official"])
    assert not bool(x.loc["005935", "common_stock_identity_official"])
    assert bool(x["security_scope_identity_validated"].all())
    assert set(x["source"]) == {KRX_OPENAPI_BASIC_SOURCE}


def test_basic_info_fails_closed_without_availability_lineage():
    with pytest.raises(KRXOfficialStatusError):
        normalise_basic_info(_basic(), asof_date="2026-09-29", available_at=None)


def test_unofficial_source_cannot_impersonate_krx_evidence():
    with pytest.raises(KRXOfficialStatusError):
        normalise_basic_info(
            _basic(),
            asof_date="2026-09-29",
            available_at="2026-09-29 20:00:00+09:00",
            source="UNOFFICIAL_MIRROR",
        )


def test_halt_interval_is_closed_open_at_resume_date():
    halts = normalise_halt_history(
        _halts(), available_at="2026-09-29 21:00:00+09:00"
    )
    rows = pd.DataFrame([
        {"decision_date": "2026-09-09", "symbol": "123456"},
        {"decision_date": "2026-09-10", "symbol": "123456"},
        {"decision_date": "2026-09-14", "symbol": "123456"},
        {"decision_date": "2026-09-15", "symbol": "123456"},
        {"decision_date": "2026-09-29", "symbol": "654321"},
    ])
    assert halt_mask_for_dates(rows, halts).tolist() == [False, True, True, False, True]
    assert set(halts["source"]) == {KRX_HALT_SOURCE}


def test_delisting_is_ineligible_from_delisting_date_forward():
    d = normalise_delisting_history(
        _delist(), available_at="2026-09-29 21:00:00+09:00"
    )
    rows = pd.DataFrame([
        {"decision_date": "2026-09-29", "symbol": "123456"},
        {"decision_date": "2026-09-30", "symbol": "123456"},
        {"decision_date": "2026-10-01", "symbol": "123456"},
    ])
    assert delisted_mask_for_dates(rows, d).tolist() == [False, True, True]
    assert set(d["source"]) == {KRX_DELIST_SOURCE}


def test_delisted_price_ohlc_is_validated():
    p = normalise_delisted_prices(
        _delist_prices(), available_at="2026-09-29 21:00:00+09:00"
    )
    assert len(p) == 1
    assert set(p["source"]) == {KRX_DELIST_PRICE_SOURCE}

    bad = _delist_prices()
    bad.loc[0, "고가"] = 800
    with pytest.raises(KRXOfficialStatusError):
        normalise_delisted_prices(bad, available_at="2026-09-29 21:00:00+09:00")


def test_structural_coverage_never_claims_judge_ready_by_itself():
    identity = normalise_basic_info(
        _basic(),
        asof_date="2026-09-29",
        available_at="2026-09-29 20:00:00+09:00",
    )
    halts = normalise_halt_history(
        _halts(), available_at="2026-09-29 21:00:00+09:00"
    )
    delist = normalise_delisting_history(
        _delist(), available_at="2026-09-29 21:00:00+09:00"
    )
    prices = normalise_delisted_prices(
        _delist_prices(), available_at="2026-09-29 21:00:00+09:00"
    )
    out = audit_official_coverage(
        requested_start="2015-06-15",
        requested_end="2026-09-29",
        identity_snapshots=identity,
        halts=halts,
        delistings=delist,
        delisted_prices=prices,
    )
    assert out["structural_inputs_ready_for_coverage_check"] is True
    assert out["judge_security_status_ready"] is False
    assert out["availability_lineage_complete"] is True
    assert out["identity_snapshot_start"] == "2026-09-29"
    assert out["identity_snapshot_end"] == "2026-09-29"
    assert out["identity_span_covers_requested_period"] is False
    assert out["identity_history_gap"] is True


def test_basic_info_requires_standard_code():
    bad = _basic().drop(columns=["ISU_CD"])
    with pytest.raises(KRXOfficialStatusError, match="standard issue code"):
        normalise_basic_info(
            bad,
            asof_date="2026-09-29",
            available_at="2026-09-29 20:00:00+09:00",
        )


def test_basic_info_rejects_invalid_standard_code():
    bad = _basic()
    bad.loc[0, "ISU_CD"] = "005930"
    with pytest.raises(KRXOfficialStatusError, match="invalid standard issue code"):
        normalise_basic_info(
            bad,
            asof_date="2026-09-29",
            available_at="2026-09-29 20:00:00+09:00",
        )
