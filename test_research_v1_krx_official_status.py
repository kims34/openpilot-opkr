import pandas as pd

from research_v1_krx_official_status import (
    audit_official_coverage,
    normalise_basic_info,
    normalise_delisted_prices,
    normalise_delisting_history,
    normalise_halt_history,
)


def _basic():
    return pd.DataFrame([
        {
            "ISU_SRT_CD": "005930",
            "ISU_ABBRV": "삼성전자",
            "MKT_TP_NM": "KOSPI",
            "KIND_STKCERT_TP_NM": "보통주",
            "LIST_DD": "19750611",
        },
        {
            "ISU_SRT_CD": "005935",
            "ISU_ABBRV": "삼성전자우",
            "MKT_TP_NM": "KOSPI",
            "KIND_STKCERT_TP_NM": "우선주",
            "LIST_DD": "19890201",
        },
    ])


def _halts():
    return pd.DataFrame([
        {
            "ISU_SRT_CD": "005930",
            "ISU_ABBRV": "삼성전자",
            "TRD_STOP_DD": "20260901",
            "TRD_RESUME_DD": "20260902",
            "TRD_STOP_REASON": "테스트",
        }
    ])


def _delist():
    return pd.DataFrame([
        {
            "ISU_SRT_CD": "123456",
            "ISU_ABBRV": "테스트상폐",
            "KIND_STKCERT_TP_NM": "보통주",
            "DELIST_DD": "20260831",
            "DELIST_REASON": "테스트",
        }
    ])


def _delist_prices():
    return pd.DataFrame([
        {
            "ISU_SRT_CD": "123456",
            "ISU_ABBRV": "테스트상폐",
            "TDD_CLSPRC": "100",
            "TDD_OPNPRC": "110",
            "TDD": "20260831",
        }
    ])


def test_normalise_basic_info_preserves_official_security_type_and_lineage():
    out = normalise_basic_info(
        _basic(),
        asof_date="2026-09-29",
        available_at="2026-09-29 20:00:00+09:00",
    )
    assert set(out["symbol"]) == {"005930", "005935"}
    assert set(out["security_type_official"]) == {"보통주", "우선주"}
    assert out["available_at"].notna().all()
    assert out["asof_date"].nunique() == 1


def test_normalise_halt_history_keeps_status_dates_and_availability():
    out = normalise_halt_history(
        _halts(), available_at="2026-09-29 21:00:00+09:00"
    )
    assert out.loc[0, "symbol"] == "005930"
    assert str(out.loc[0, "halt_date"].date()) == "2026-09-01"
    assert str(out.loc[0, "resume_date"].date()) == "2026-09-02"
    assert out["available_at"].notna().all()


def test_normalise_delisting_history_keeps_official_type():
    out = normalise_delisting_history(
        _delist(), available_at="2026-09-29 21:00:00+09:00"
    )
    assert out.loc[0, "security_type_official"] == "보통주"
    assert str(out.loc[0, "delist_date"].date()) == "2026-08-31"


def test_normalise_delisted_prices_preserves_terminal_price():
    out = normalise_delisted_prices(
        _delist_prices(), available_at="2026-09-29 21:00:00+09:00"
    )
    assert float(out.loc[0, "close"]) == 100.0
    assert float(out.loc[0, "open"]) == 110.0
    assert out["available_at"].notna().all()


def test_audit_fails_closed_when_structural_inputs_are_missing():
    out = audit_official_coverage(
        requested_start="2015-06-15",
        requested_end="2026-09-29",
        identity_snapshots=pd.DataFrame(),
        halts=pd.DataFrame(),
        delistings=pd.DataFrame(),
        delisted_prices=pd.DataFrame(),
    )
    assert out["structural_inputs_ready_for_coverage_check"] is False
    assert out["judge_security_status_ready"] is False
    assert out["identity_history_gap"] is True


def test_audit_fails_closed_when_only_current_identity_snapshot_exists():
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
