import pandas as pd
import pytest

from research_v1_krx_acquisition_receipt import (
    KRXAcquisitionReceiptError,
    build_acquisition_receipt,
)
from research_v1_krx_public_evidence import public_evidence_fingerprint_sha256


BASE = dict(
    source_family="KRX_INVESTOR_FLOW",
    intended_use_scope="INTERNAL_RESEARCH_CANDIDATE_FEATURE_PREPARATION",
    access_route="DATA_MARKETPLACE_AUTHENTICATED_WEB_SESSION",
    dataset_identifier="MDCSTAT02303",
    authorization_evidence_reference="approval-ref-2026-10-01-001",
    client_revision="e6ebac9b71482db127348d8a08ebc6743aa3b50e",
    retrieved_at="2026-10-01T12:00:00+09:00",
    request_metadata={
        "isuCd": "KR7005930003",
        "strtDd": "20260921",
        "endDd": "20260923",
        "askBid": "3",
        "trdVolVal": "2",
    },
)


def _frame(value=100):
    return pd.DataFrame(
        {
            "TRD_DD": ["2026-09-21", "2026-09-22"],
            "NET_BID_TRDVAL": [value, -20],
        }
    )


def test_receipt_is_deterministic_and_never_authorizes_promotion():
    a = build_acquisition_receipt(**BASE, response_frame=_frame())
    b = build_acquisition_receipt(**BASE, response_frame=_frame())
    assert a["receipt_fingerprint_sha256"] == b["receipt_fingerprint_sha256"]
    assert a["response_payload_sha256"] == b["response_payload_sha256"]
    assert a["response_rows"] == 2
    assert a["response_columns"] == ["TRD_DD", "NET_BID_TRDVAL"]
    assert a["alpha_or_final_judge_promotion_authorized"] is False
    assert a["sealed_holdout_authorized"] is False
    assert a["live_trading_authorized"] is False


def test_payload_change_changes_payload_and_receipt_fingerprint():
    a = build_acquisition_receipt(**BASE, response_frame=_frame(100))
    b = build_acquisition_receipt(**BASE, response_frame=_frame(101))
    assert a["response_payload_sha256"] != b["response_payload_sha256"]
    assert a["receipt_fingerprint_sha256"] != b["receipt_fingerprint_sha256"]


def test_schema_change_changes_schema_and_receipt_fingerprint():
    a = build_acquisition_receipt(**BASE, response_frame=_frame())
    changed = _frame().rename(columns={"NET_BID_TRDVAL": "NET_BID_TRDVOL"})
    b = build_acquisition_receipt(**BASE, response_frame=changed)
    assert a["response_schema_sha256"] != b["response_schema_sha256"]
    assert a["receipt_fingerprint_sha256"] != b["receipt_fingerprint_sha256"]


def test_request_change_changes_request_and_receipt_fingerprint():
    a = build_acquisition_receipt(**BASE, response_frame=_frame())
    changed = dict(BASE)
    changed["request_metadata"] = dict(BASE["request_metadata"], endDd="20260924")
    b = build_acquisition_receipt(**changed, response_frame=_frame())
    assert a["request_metadata_sha256"] != b["request_metadata_sha256"]
    assert a["receipt_fingerprint_sha256"] != b["receipt_fingerprint_sha256"]


@pytest.mark.parametrize(
    "request_metadata",
    [
        {"api_key": "must-not-enter-receipt", "isuCd": "KR7005930003"},
        {"headers": {"Authorization": "Bearer secret"}, "isuCd": "KR7005930003"},
        {"cookie": "session=secret", "isuCd": "KR7005930003"},
        {"nested": [{"password": "secret"}], "isuCd": "KR7005930003"},
    ],
)
def test_secret_like_request_metadata_fails_closed(request_metadata):
    args = dict(BASE)
    args["request_metadata"] = request_metadata
    with pytest.raises(KRXAcquisitionReceiptError, match="secret-like field"):
        build_acquisition_receipt(**args, response_frame=_frame())


def test_naive_retrieved_at_fails_closed():
    args = dict(BASE)
    args["retrieved_at"] = "2026-10-01 12:00:00"
    with pytest.raises(KRXAcquisitionReceiptError, match="timezone-aware"):
        build_acquisition_receipt(**args, response_frame=_frame())


def test_stale_public_contract_fingerprint_fails_closed():
    assert public_evidence_fingerprint_sha256() != "0" * 64
    with pytest.raises(KRXAcquisitionReceiptError, match="does not match current manifest"):
        build_acquisition_receipt(
            **BASE,
            response_frame=_frame(),
            public_contract_evidence_fingerprint="0" * 64,
        )


def test_unknown_route_and_family_fail_closed():
    args = dict(BASE)
    args["access_route"] = "UNOFFICIAL_PROXY"
    with pytest.raises(KRXAcquisitionReceiptError, match="unsupported access_route"):
        build_acquisition_receipt(**args, response_frame=_frame())

    args = dict(BASE)
    args["source_family"] = "KRX_UNKNOWN"
    with pytest.raises(KRXAcquisitionReceiptError, match="unsupported source_family"):
        build_acquisition_receipt(**args, response_frame=_frame())


def test_empty_result_is_receiptable_but_not_promotion_evidence():
    empty = pd.DataFrame(columns=["TRD_DD", "NET_BID_TRDVAL"])
    out = build_acquisition_receipt(**BASE, response_frame=empty)
    assert out["response_rows"] == 0
    assert out["alpha_or_final_judge_promotion_authorized"] is False
