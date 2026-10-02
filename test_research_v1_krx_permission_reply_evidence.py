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


def test_committed_permission_reply_evidence_is_fail_closed():
    out = validate_file()
    assert out["valid"] is True
    assert out["automated_collection_authorized"] is False
    assert out["sufficient_for_data_marketplace_tiny_probe_preflight"] is False
    assert out["gate_a_status_ceiling"] == "BLOCKED"
    assert out["gate_f_evidence_strengthened"] is True
    assert out["sealed_holdout_authorized"] is False
    assert out["live_trading_authorized"] is False


def test_automation_cannot_be_inferred_from_ambiguous_screenshot():
    data = _data()
    data["project_classification"]["automated_collection_authorized"] = True
    with pytest.raises(KRXPermissionReplyEvidenceError, match="automation authority illegally true"):
        validate_permission_reply_evidence(data)


def test_tiny_probe_cannot_be_authorized_from_ambiguous_screenshot():
    data = _data()
    data["project_classification"]["sufficient_for_data_marketplace_tiny_probe_preflight"] = True
    with pytest.raises(KRXPermissionReplyEvidenceError, match="tiny-probe preflight illegally authorized"):
        validate_permission_reply_evidence(data)


def test_sender_identity_cannot_be_upgraded_without_new_evidence_record():
    data = _data()
    data["visible_sender_identity"] = True
    with pytest.raises(KRXPermissionReplyEvidenceError, match="sender visibility must remain false"):
        validate_permission_reply_evidence(data)


def test_low_frequency_internal_research_scope_must_remain_recorded():
    data = _data()
    data["supported_scope"]["low_frequency_querying"] = False
    with pytest.raises(KRXPermissionReplyEvidenceError, match="low_frequency_querying must remain true"):
        validate_permission_reply_evidence(data)
