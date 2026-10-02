import pandas as pd
import pytest

from research_v1_krx_historical_identity import (
    KRXHistoricalIdentityError,
    identity_summary,
    reconstruct_historical_kospi_episodes,
)


def _master_row(snapshot, standard, symbol, listing, name="테스트", common=True):
    return {
        "decision_date": pd.Timestamp(snapshot),
        "standard_code": standard,
        "symbol": symbol,
        "name": name,
        "market_type_official": "KOSPI",
        "security_group_official": "주권",
        "stock_type_official": "보통주" if common else "우선주",
        "listing_date_official": pd.Timestamp(listing),
        "common_stock_identity_official": common,
    }


def _masters():
    return pd.DataFrame([
        _master_row("2015-06-15", "KR7005930003", "005930", "1975-06-11", "삼성전자"),
        _master_row("2015-06-15", "KR7005931001", "005935", "1989-03-13", "삼성전자우", common=False),
        _master_row("2016-01-04", "KR7222220000", "222222", "2016-01-04", "상폐보통"),
        _master_row("2020-01-02", "KR7123450000", "123456", "2020-01-02", "신규보통"),
        _master_row("2026-10-01", "KR7005930003", "005930", "1975-06-11", "삼성전자"),
        _master_row("2026-10-01", "KR7123450000", "123456", "2020-01-02", "신규보통"),
    ])


def _new():
    return pd.DataFrame([
        {
            "종목코드": "222222",
            "종목명": "상폐보통",
            "시장구분": "유가증권",
            "증권구분": "주권",
            "주식종류": "보통주",
            "상장일": "20160104",
            "상장폐지일": "20221230",
        },
        {
            "종목코드": "123456",
            "종목명": "신규보통",
            "시장구분": "유가증권시장",
            "증권구분": "주권",
            "주식종류": "보통주",
            "상장일": "20200102",
            "상장폐지일": "",
        },
        {
            "종목코드": "654321",
            "종목명": "코스닥",
            "시장구분": "코스닥",
            "증권구분": "주권",
            "주식종류": "보통주",
            "상장일": "20210101",
            "상장폐지일": "",
        },
    ])


def _delisted():
    return pd.DataFrame([
        {
            "종목코드": "222222",
            "종목명": "상폐보통",
            "시장구분": "유가증권",
            "증권구분": "주권",
            "주식종류": "보통주",
            "상장일": "20160104",
            "폐지일": "20221230",
        }
    ])


def test_reconstructs_stable_kospi_common_stock_episodes():
    out = reconstruct_historical_kospi_episodes(
        security_master_snapshots=_masters(),
        new_listing=_new(),
        delisted=_delisted(),
    )
    assert set(out["short_code"]) == {"005930", "123456", "222222"}
    assert out["standard_code"].str.len().eq(12).all()

    samsung = out[out["short_code"].eq("005930")].iloc[0]
    assert samsung["episode_key"] == "KOSPI|005930|1975-06-11"
    assert samsung["coverage_start"] == pd.Timestamp("2015-06-15")
    assert samsung["coverage_end"] == pd.Timestamp("2026-10-01")
    assert samsung["standard_code"] == "KR7005930003"
    assert samsung["source_start_master"]
    assert samsung["source_end_master_reconciled"]

    delisted = out[out["short_code"].eq("222222")].iloc[0]
    assert delisted["standard_code"] == "KR7222220000"
    assert delisted["source_new_listing"]
    assert delisted["source_delisted"]
    assert delisted["coverage_end"] == pd.Timestamp("2022-12-30")


def test_new_listing_requires_exact_same_day_standard_code_snapshot():
    masters = _masters()
    masters = masters[
        ~(
            masters["decision_date"].eq(pd.Timestamp("2020-01-02"))
            & masters["symbol"].eq("123456")
        )
    ]
    with pytest.raises(KRXHistoricalIdentityError, match="same-day standard-code mapping"):
        reconstruct_historical_kospi_episodes(
            security_master_snapshots=masters,
            new_listing=_new(),
            delisted=_delisted(),
        )


def test_end_snapshot_cannot_change_standard_code():
    masters = _masters()
    mask = (
        masters["decision_date"].eq(pd.Timestamp("2026-10-01"))
        & masters["symbol"].eq("123456")
    )
    masters.loc[mask, "standard_code"] = "KR7123459999"
    with pytest.raises(KRXHistoricalIdentityError, match="standard code changed"):
        reconstruct_historical_kospi_episodes(
            security_master_snapshots=masters,
            new_listing=_new(),
            delisted=_delisted(),
        )


def test_delisted_episode_must_exist_in_start_or_new_listing_identity():
    new = _new()
    new = new[~new["종목코드"].eq("222222")]
    with pytest.raises(KRXHistoricalIdentityError, match="not represented"):
        reconstruct_historical_kospi_episodes(
            security_master_snapshots=_masters(),
            new_listing=new,
            delisted=_delisted(),
        )


def test_overlapping_reused_short_code_episodes_fail_closed():
    masters = pd.concat([
        _masters(),
        pd.DataFrame([
            _master_row("2018-01-02", "KR7333330000", "333333", "2018-01-02", "A"),
            _master_row("2020-01-02", "KR7333331008", "333333", "2020-01-02", "B"),
            _master_row("2026-10-01", "KR7333331008", "333333", "2020-01-02", "B"),
        ]),
    ], ignore_index=True)
    new = pd.concat([
        _new(),
        pd.DataFrame([
            {"종목코드": "333333", "종목명": "A", "시장구분": "KOSPI", "증권구분": "주권", "주식종류": "보통주", "상장일": "20180102", "상장폐지일": "20210101"},
            {"종목코드": "333333", "종목명": "B", "시장구분": "KOSPI", "증권구분": "주권", "주식종류": "보통주", "상장일": "20200102", "상장폐지일": ""},
        ]),
    ], ignore_index=True)
    dl = pd.concat([
        _delisted(),
        pd.DataFrame([
            {"종목코드": "333333", "종목명": "A", "시장구분": "KOSPI", "증권구분": "주권", "주식종류": "보통주", "상장일": "20180102", "폐지일": "20210101"},
        ]),
    ], ignore_index=True)
    with pytest.raises(KRXHistoricalIdentityError, match="overlapping listing episodes"):
        reconstruct_historical_kospi_episodes(
            security_master_snapshots=masters,
            new_listing=new,
            delisted=dl,
        )


def test_summary_emits_counts_not_identifiers():
    out = reconstruct_historical_kospi_episodes(
        security_master_snapshots=_masters(),
        new_listing=_new(),
        delisted=_delisted(),
    )
    s = identity_summary(out)
    assert s["episode_count"] == 3
    assert s["all_standard_codes_resolved"] is True
    assert s["raw_identifiers_emitted"] is False
    assert "symbols" not in s
