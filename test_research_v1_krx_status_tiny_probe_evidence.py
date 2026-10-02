import json
from pathlib import Path

import pytest

from research_v1_krx_status_tiny_probe_evidence import (
    KRXStatusTinyProbeEvidenceError,
    validate_file,
    validate_status_tiny_probe_evidence,
)

PATH = Path("INDEXALERT_KRX_STATUS_TINY_PROBE_EVIDENCE.json")


def _data():
    return json.loads(PATH.read_text(encoding="utf-8"))


def test_committed_status_tiny_probe_evidence_is_partial_not_pass():
    out = validate_file()
    assert out["valid"] is True
    assert out["gate_a"] == "PARTIAL"
    assert out["gate_b"] == "PARTIAL"
    assert out["gate_c"] == "BLOCKED"
    assert out["gate_d"] == "BLOCKED"
    assert out["judge_security_status_ready"] is False
    assert out["sealed_holdout_authorized"] is False
    assert out["live_trading_authorized"] is False


def test_tiny_probe_cannot_self_promote_gate_a_or_judge():
    data = _data()
    data["gate_state_after_probe"]["A"] = "PASS"
    with pytest.raises(KRXStatusTinyProbeEvidenceError, match="gate state drift"):
        validate_status_tiny_probe_evidence(data)

    data = _data()
    data["authority"]["judge_security_status_ready"] = True
    with pytest.raises(KRXStatusTinyProbeEvidenceError, match="illegally true"):
        validate_status_tiny_probe_evidence(data)


def test_live_validated_blds_are_frozen():
    data = _data()
    for row in data["probes"]:
        if row["name"] == "cleanup_trading_candidate_bld":
            row["bld"] = "dbms/MDC/STAT/issue/WRONG"
    with pytest.raises(KRXStatusTinyProbeEvidenceError, match="cleanup BLD drift"):
        validate_status_tiny_probe_evidence(data)


def test_numeric_market_data_cannot_be_reclassified_as_persisted():
    data = _data()
    data["numeric_market_data_persisted"] = True
    with pytest.raises(KRXStatusTinyProbeEvidenceError, match="must not be persisted"):
        validate_status_tiny_probe_evidence(data)
