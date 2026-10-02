import json
from pathlib import Path

import pytest

from research_v1_krx_data_marketplace_readiness_evidence import (
    KRXReadinessEvidenceError,
    validate_file,
    validate_readiness_evidence,
)

PATH = Path("INDEXALERT_KRX_DATA_MARKETPLACE_READINESS_EVIDENCE.json")


def _data():
    return json.loads(PATH.read_text(encoding="utf-8"))


def test_committed_readiness_evidence_is_ready_but_network_free():
    out = validate_file()
    assert out["valid"] is True
    assert out["ready_for_explicitly_consented_tiny_probe"] is True
    assert out["network_request_attempted"] is False
    assert out["authenticated_probe_completed"] is False
    assert out["gate_a_pass"] is False
    assert out["sealed_holdout_authorized"] is False
    assert out["live_trading_authorized"] is False


def test_readiness_cannot_be_reinterpreted_as_authenticated_probe():
    data = _data()
    data["authority"]["authenticated_probe_completed"] = True
    with pytest.raises(KRXReadinessEvidenceError, match="cannot be claimed complete"):
        validate_readiness_evidence(data)


def test_readiness_cannot_grant_gate_a_or_live_authority():
    data = _data()
    data["authority"]["gate_a_pass"] = True
    with pytest.raises(KRXReadinessEvidenceError, match="Gate A cannot pass"):
        validate_readiness_evidence(data)

    data = _data()
    data["authority"]["live_trading_authorized"] = True
    with pytest.raises(KRXReadinessEvidenceError, match="illegally true"):
        validate_readiness_evidence(data)


def test_explicit_consent_must_remain_the_only_missing_requirement():
    data = _data()
    data["source_families"]["KRX_SECURITY_STATUS"]["remaining_requirements_before_manual_probe"] = []
    with pytest.raises(KRXReadinessEvidenceError, match="remaining requirement drift"):
        validate_readiness_evidence(data)
