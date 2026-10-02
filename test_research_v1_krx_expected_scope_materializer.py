import pandas as pd
import pytest

from research_v1_krx_expected_scope_materializer import (
    KRXExpectedScopeMaterializerError,
    bind_scope_contract_fingerprint,
    materialize_one_date,
    public_date_summary,
)


def _daily():
    return pd.DataFrame([
        {"BAS_DD":"20260923","ISU_CD":"KR7005930003","ISU_NM":"삼성전자","MKT_NM":"KOSPI"},
        {"BAS_DD":"20260923","ISU_CD":"KR7000660001","ISU_NM":"SK하이닉스","MKT_NM":"KOSPI"},
        {"BAS_DD":"20260923","ISU_CD":"KR7000010001","ISU_NM":"우선주","MKT_NM":"KOSPI"},
    ])


def _master():
    return pd.DataFrame([
        {"ISU_CD":"KR7005930003","ISU_SRT_CD":"005930","ISU_NM":"삼성전자","LIST_DD":"19750611","MKT_TP_NM":"KOSPI","SECUGRP_NM":"주권","KIND_STKCERT_TP_NM":"보통주"},
        {"ISU_CD":"KR7000660001","ISU_SRT_CD":"000660","ISU_NM":"SK하이닉스","LIST_DD":"19961226","MKT_TP_NM":"KOSPI","SECUGRP_NM":"주권","KIND_STKCERT_TP_NM":"보통주"},
        {"ISU_CD":"KR7000010001","ISU_SRT_CD":"000015","ISU_NM":"우선주","LIST_DD":"19800101","MKT_TP_NM":"KOSPI","SECUGRP_NM":"주권","KIND_STKCERT_TP_NM":"우선주"},
    ])


def test_same_date_official_inputs_materialize_independent_expected_scopes():
    out = materialize_one_date(
        requested_date="20260923",
        daily_trade=_daily(),
        security_master=_master(),
    )
    assert out["official_trading_date_observed"] is True
    assert len(out["investor_expected_scope"]) == 2
    assert len(out["status_expected_scope"]) == 2
    assert set(out["investor_expected_scope"]["symbol"]) == {"005930","000660"}
    assert set(out["status_expected_scope"]["symbol"]) == {"005930","000660"}
    safe = public_date_summary(out)
    assert safe["investor_expected_key_count"] == 2
    assert safe["status_expected_key_count"] == 2
    assert safe["security_identifiers_emitted"] is False
    assert safe["raw_rows_emitted"] is False
    assert safe["network_request_attempted"] is False
    assert "005930" not in str(safe)


def test_empty_daily_response_never_invents_trading_date_or_scope():
    empty = _daily().iloc[0:0].copy()
    out = materialize_one_date(
        requested_date="20260924",
        daily_trade=empty,
        security_master=None,
    )
    assert out["official_trading_date_observed"] is False
    assert out["investor_expected_scope"].empty
    assert out["status_expected_scope"].empty


def test_nonempty_daily_requires_exact_date_and_same_date_identity():
    daily = _daily()
    daily.loc[0,"BAS_DD"] = "20260922"
    with pytest.raises(KRXExpectedScopeMaterializerError, match="exactly match"):
        materialize_one_date(
            requested_date="20260923",
            daily_trade=daily,
            security_master=_master(),
        )

    with pytest.raises(KRXExpectedScopeMaterializerError, match="security_master required"):
        materialize_one_date(
            requested_date="20260923",
            daily_trade=_daily(),
            security_master=None,
        )


def test_expected_scope_never_promotes_preference_or_priority_share_to_common_stock():
    out = materialize_one_date(
        requested_date="20260923",
        daily_trade=_daily(),
        security_master=_master(),
    )
    assert "000015" not in set(out["status_expected_scope"]["symbol"])
    assert "000015" not in set(out["investor_expected_scope"]["symbol"])


def test_scope_contract_fingerprint_is_required_and_key_preserving():
    out = materialize_one_date(
        requested_date="20260923",
        daily_trade=_daily(),
        security_master=_master(),
    )
    frame = bind_scope_contract_fingerprint(
        out["investor_expected_scope"],
        date_column="event_date",
        fingerprint="a"*64,
    )
    assert frame["scope_contract_fingerprint_sha256"].eq("a"*64).all()
    assert list(frame.columns) == [
        "event_date","symbol","isu_cd","scope_contract_fingerprint_sha256"
    ]

    with pytest.raises(KRXExpectedScopeMaterializerError, match="SHA-256"):
        bind_scope_contract_fingerprint(
            out["investor_expected_scope"],
            date_column="event_date",
            fingerprint="bad",
        )
