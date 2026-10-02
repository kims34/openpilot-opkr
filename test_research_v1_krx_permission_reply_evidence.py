import json
from pathlib import Path

import pytest

from research_v1_krx_permission_reply_evidence import (
    KRXPermissionReplyEvidenceError,
    validate_file,
    validate_permission_reply_evidence,
)


PATH = Path("INDEXALERT_KRX_PERMISSION_REPLY_EVIDENCE.json")


def _data():
    return json.loads(PATH.read_text(encoding="utf-8"))


def test_committed_permission_reply_evidence_v3_grants_scope_limited_full_history_rights():
    out = validate_file()
    assert out["valid"] is True
    assert out["automated_collection_authorized"] is True
    assert out["high_frequency_collection_authorized"] is True
    assert out["full_historical_download_rights_authorized"] is True
    assert out["bulk_historical_acquisition_rights_authorized"] is True
    assert out["bulk_historical_network_execution_authorized_by_user"] is False
    assert out["permission_state"] == "PERMITTED_NO_SEPARATE_APPROVAL"
    assert out["gate_f_status_for_personal_research"] == "PASS"
    assert out["gate_a_status_ceiling_from_permission_alone"] == "PARTIAL"
    assert out["feature_performance_testing_authorized"] is False
    assert out["sealed_holdout_authorized"] is False
    assert out["live_trading_authorized"] is False


def test_recipient_identity_must_remain_redacted():
    data = _data()
    data["email_metadata"]["recipient_redacted"] = False
    with pytest.raises(KRXPermissionReplyEvidenceError, match="recipient must stay redacted"):
        validate_permission_reply_evidence(data)


def test_distribution_sale_and_leakage_prohibitions_cannot_be_weakened():
    for key in ("external_leakage", "external_sale", "third_party_distribution"):
        data = _data()
        data["prohibited_scope"][key] = False
        with pytest.raises(KRXPermissionReplyEvidenceError, match="prohibition weakened"):
            validate_permission_reply_evidence(data)


def test_rights_do_not_self_authorize_bulk_network_execution():
    data = _data()
    data["project_classification"]["bulk_historical_network_execution_authorized_by_user"] = True
    with pytest.raises(KRXPermissionReplyEvidenceError, match="bulk network execution illegally pre-authorized"):
        validate_permission_reply_evidence(data)


def test_rights_do_not_prove_technical_coverage_or_pit():
    for key in (
        "exact_bld_schema_equivalence",
        "actual_source_availability_for_every_required_date",
        "stable_security_mapping_across_all_history",
        "record_level_pit_lineage",
        "completeness_of_status_economics",
        "model_performance_validity",
    ):
        data = _data()
        data["still_not_proven_by_permission_text"][key] = False
        with pytest.raises(KRXPermissionReplyEvidenceError, match="evidence boundary weakened"):
            validate_permission_reply_evidence(data)


def test_user_attested_origin_must_not_be_upgraded_to_independently_verified():
    data = _data()
    data["project_classification"]["issuer_independently_verified"] = True
    with pytest.raises(KRXPermissionReplyEvidenceError, match="origin must not be overstated"):
        validate_permission_reply_evidence(data)


def test_human_permission_doc_tracks_v3_hash_and_unknown_latest_timestamp():
    text = Path("INDEXALERT_KRX_PERMISSION_REPLY_EVIDENCE.md").read_text(encoding="utf-8")
    assert "INDEXALERT-KRX-PERMISSION-REPLY-2026-10-02-v3" in text
    assert "7361065e06599f947216233fc84e97126b1675de5af41068114cf6ef9577e304" in text
    assert "latest v3 reply exact timestamp: **not re-provided / intentionally unknown**" in text
    assert "complete full-historical-period download and query" in text
    assert "high-frequency collection" in text
    assert "Gate F intended-use rights may now be treated as **PASS**" in text
    assert "c50a76bb22d8e16b48b9b2eb56c78ab97f620068ed4fae4a65cd4bf6f4ae5f38" not in text
