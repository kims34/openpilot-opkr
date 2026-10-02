import json
from pathlib import Path

import pytest

from research_v1_krx_investor_flow_tiny_probe_evidence import (
    KRXInvestorFlowTinyProbeEvidenceError,
    validate_file,
    validate_investor_flow_tiny_probe_evidence,
)

PATH = Path("INDEXALERT_KRX_INVESTOR_FLOW_TINY_PROBE_EVIDENCE.json")


def _data():
    return json.loads(PATH.read_text(encoding="utf-8"))


def test_committed_investor_flow_tiny_probe_is_partial_not_performance_ready():
    out = validate_file()
    assert out["valid"] is True
    assert out["gate_a"] == "PARTIAL"
    assert out["gate_b"] == "PARTIAL"
    assert out["gate_c"] == "BLOCKED"
    assert out["gate_d"] == "PARTIAL"
    assert out["feature_performance_testing_authorized"] is False
    assert out["sealed_holdout_authorized"] is False
    assert out["live_trading_authorized"] is False


def test_tiny_probe_cannot_self_authorize_feature_research():
    data = _data()
    data["authority"]["feature_performance_testing_authorized"] = True
    with pytest.raises(KRXInvestorFlowTinyProbeEvidenceError, match="illegally true"):
        validate_investor_flow_tiny_probe_evidence(data)


def test_investor_bld_schema_and_pit_floor_are_frozen():
    data = _data()
    data["probe"]["bld"] = "dbms/MDC/STAT/standard/WRONG"
    with pytest.raises(KRXInvestorFlowTinyProbeEvidenceError, match="BLD drift"):
        validate_investor_flow_tiny_probe_evidence(data)

    data = _data()
    data["pit_policy"]["official_publication_floor"] = "15:30 Asia/Seoul"
    with pytest.raises(KRXInvestorFlowTinyProbeEvidenceError, match="PIT publication floor drift"):
        validate_investor_flow_tiny_probe_evidence(data)


def test_tiny_probe_cannot_promote_gate_a_or_history_coverage():
    data = _data()
    data["gate_state_after_probe"]["A"] = "PASS"
    with pytest.raises(KRXInvestorFlowTinyProbeEvidenceError, match="gate state drift"):
        validate_investor_flow_tiny_probe_evidence(data)

    data = _data()
    data["gate_state_after_probe"]["C"] = "PARTIAL"
    with pytest.raises(KRXInvestorFlowTinyProbeEvidenceError, match="gate state drift"):
        validate_investor_flow_tiny_probe_evidence(data)
