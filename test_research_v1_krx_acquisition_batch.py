import copy

import pandas as pd
import pytest

from research_v1_krx_acquisition_batch import (
    KRXAcquisitionBatchError,
    build_acquisition_batch_manifest,
)
from research_v1_krx_acquisition_receipt import build_acquisition_receipt


def _receipt(*, day="20260921", retrieved_at="2026-10-01T12:00:00+09:00", dataset="MDCSTAT02303", route="DATA_MARKETPLACE_AUTHENTICATED_WEB_SESSION", auth_ref="approval-ref-001", revision="client-rev-1"):
    frame = pd.DataFrame(
        {
            "TRD_DD": [day],
            "NET_BID_TRDVAL": [100],
        }
    )
    return build_acquisition_receipt(
        source_family="KRX_INVESTOR_FLOW",
        intended_use_scope="INTERNAL_RESEARCH_CANDIDATE_FEATURE_PREPARATION",
        access_route=route,
        dataset_identifier=dataset,
        authorization_evidence_reference=auth_ref,
        client_revision=revision,
        retrieved_at=retrieved_at,
        request_metadata={"strtDd": day, "endDd": day, "isuCd": "KR7005930003"},
        response_frame=frame,
    )


def test_batch_is_order_independent_and_never_grants_authority():
    a = _receipt(day="20260921", retrieved_at="2026-10-01T12:00:00+09:00")
    b = _receipt(day="20260922", retrieved_at="2026-10-01T12:01:00+09:00")
    x = build_acquisition_batch_manifest([a, b])
    y = build_acquisition_batch_manifest([b, a])
    assert x["batch_fingerprint_sha256"] == y["batch_fingerprint_sha256"]
    assert x["receipt_count"] == 2
    assert x["total_response_rows"] == 2
    assert x["coverage_validated"] is False
    assert x["pit_lineage_validated"] is False
    assert x["alpha_or_final_judge_promotion_authorized"] is False
    assert x["sealed_holdout_authorized"] is False
    assert x["live_trading_authorized"] is False


def test_duplicate_receipt_fails_closed():
    a = _receipt()
    with pytest.raises(KRXAcquisitionBatchError, match="duplicate receipts"):
        build_acquisition_batch_manifest([a, a])


@pytest.mark.parametrize(
    "field,changed",
    [
        ("dataset_identifier", "OTHER_DATASET"),
        ("access_route", "KRX_OPENAPI_APPROVED_SERVICE"),
        ("authorization_evidence_reference", "approval-ref-OTHER"),
        ("client_revision", "client-rev-OTHER"),
        ("intended_use_scope", "OTHER_SCOPE"),
    ],
)
def test_mixed_contract_fields_fail_closed(field, changed):
    a = _receipt(day="20260921", retrieved_at="2026-10-01T12:00:00+09:00")
    kwargs = {
        "day": "20260922",
        "retrieved_at": "2026-10-01T12:01:00+09:00",
        "dataset": "MDCSTAT02303",
        "route": "DATA_MARKETPLACE_AUTHENTICATED_WEB_SESSION",
        "auth_ref": "approval-ref-001",
        "revision": "client-rev-1",
    }
    mapping = {
        "dataset_identifier": "dataset",
        "access_route": "route",
        "authorization_evidence_reference": "auth_ref",
        "client_revision": "revision",
    }
    if field in mapping:
        kwargs[mapping[field]] = changed
        b = _receipt(**kwargs)
    else:
        b = _receipt(**kwargs)
        # Rebuild a valid receipt with a different scope rather than mutating a fingerprinted receipt.
        frame = pd.DataFrame({"TRD_DD": ["20260922"], "NET_BID_TRDVAL": [100]})
        b = build_acquisition_receipt(
            source_family="KRX_INVESTOR_FLOW",
            intended_use_scope=changed,
            access_route="DATA_MARKETPLACE_AUTHENTICATED_WEB_SESSION",
            dataset_identifier="MDCSTAT02303",
            authorization_evidence_reference="approval-ref-001",
            client_revision="client-rev-1",
            retrieved_at="2026-10-01T12:01:00+09:00",
            request_metadata={"strtDd": "20260922", "endDd": "20260922", "isuCd": "KR7005930003"},
            response_frame=frame,
        )
    with pytest.raises(KRXAcquisitionBatchError, match=f"mixes multiple {field}"):
        build_acquisition_batch_manifest([a, b])


def test_schema_drift_within_one_dataset_fails_closed():
    a = _receipt(day="20260921", retrieved_at="2026-10-01T12:00:00+09:00")
    frame = pd.DataFrame({"TRD_DD": ["20260922"], "NET_BID_TRDVOL": [100]})
    b = build_acquisition_receipt(
        source_family="KRX_INVESTOR_FLOW",
        intended_use_scope="INTERNAL_RESEARCH_CANDIDATE_FEATURE_PREPARATION",
        access_route="DATA_MARKETPLACE_AUTHENTICATED_WEB_SESSION",
        dataset_identifier="MDCSTAT02303",
        authorization_evidence_reference="approval-ref-001",
        client_revision="client-rev-1",
        retrieved_at="2026-10-01T12:01:00+09:00",
        request_metadata={"strtDd": "20260922", "endDd": "20260922", "isuCd": "KR7005930003"},
        response_frame=frame,
    )
    with pytest.raises(KRXAcquisitionBatchError, match="response_schema_sha256"):
        build_acquisition_batch_manifest([a, b])


def test_tampered_receipt_is_rejected_before_batching():
    a = _receipt()
    tampered = copy.deepcopy(a)
    tampered["response_rows"] = 999
    with pytest.raises(KRXAcquisitionBatchError, match="fingerprint mismatch"):
        build_acquisition_batch_manifest([tampered])


def test_receipt_claiming_promotion_authority_is_rejected_even_if_refingerprinted():
    from research_v1_krx_acquisition_batch import RECEIPT_BODY_FIELDS
    from research_v1_krx_acquisition_receipt import _sha256

    a = _receipt()
    forged = copy.deepcopy(a)
    forged["alpha_or_final_judge_promotion_authorized"] = True
    body = {field: forged[field] for field in RECEIPT_BODY_FIELDS}
    forged["receipt_fingerprint_sha256"] = _sha256(body)
    with pytest.raises(KRXAcquisitionBatchError, match="illegally claims promotion authority"):
        build_acquisition_batch_manifest([forged])
