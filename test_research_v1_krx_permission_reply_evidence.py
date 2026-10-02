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


def test_committed_permission_reply_evidence_is_explicit_but_scope_limited():
    out = validate_file()
    assert out["valid"] is True
    assert out["automated_collection_authorized"] is True
    assert out["permission_state"] == "PERMITTED_NO_SEPARATE_APPROVAL"
    assert out["sufficient_for_data_marketplace_tiny_probe_preflight"] is True
    assert out["gate_a_status_ceiling_before_authenticated_probe"] == "BLOCKED"
    assert out["gate_a_status_ceiling_after_successful_tiny_probe"] == "PARTIAL"
    assert out["gate_f_evidence_strengthened"] is True
    assert out["sealed_holdout_authorized"] is False
    assert out["live_trading_authorized"] is False


def test_recipient_identity_must_remain_redacted():
    data = _data()
    data["email_metadata"]["recipient_redacted"] = False
    with pytest.raises(KRXPermissionReplyEvidenceError, match="recipient must stay redacted"):
        validate_permission_reply_evidence(data)


def test_automation_permission_cannot_be_removed_or_broadened():
    data = _data()
    data["project_classification"]["automated_collection_authorized"] = False
    with pytest.raises(KRXPermissionReplyEvidenceError, match="explicit automation permission lost"):
        validate_permission_reply_evidence(data)

    data = _data()
    data["not_authorized_or_not_proven"]["bulk_or_high_frequency_collection"] = False
    with pytest.raises(KRXPermissionReplyEvidenceError, match="limit weakened"):
        validate_permission_reply_evidence(data)


def test_user_attested_origin_must_not_be_upgraded_to_independently_verified():
    data = _data()
    data["project_classification"]["issuer_independently_verified"] = True
    with pytest.raises(KRXPermissionReplyEvidenceError, match="origin must not be overstated"):
        validate_permission_reply_evidence(data)


def test_reply_timestamp_is_frozen():
    data = _data()
    data["email_metadata"]["reply_at"] = "2026-10-02T14:41:00+09:00"
    with pytest.raises(KRXPermissionReplyEvidenceError, match="reply timestamp drift"):
        validate_permission_reply_evidence(data)
