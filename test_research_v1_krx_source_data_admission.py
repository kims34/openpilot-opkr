import copy

import pandas as pd
import pytest

from research_v1_krx_acquisition_batch import build_acquisition_batch_manifest
from research_v1_krx_acquisition_receipt import build_acquisition_receipt
from research_v1_krx_public_evidence import public_evidence_fingerprint_sha256
from research_v1_krx_source_data_admission import (
    KRXSourceDataAdmissionError,
    assess_investor_flow_source_data_admission,
)
from research_v1_krx_source_gates import audit_source_gates


SCOPE = "INTERNAL_RESEARCH_CANDIDATE_FEATURE_PREPARATION"


def _gates(all_pass=True, scope=SCOPE):
    statuses = {gate: "PASS" for gate in "ABCDEF"}
    if not all_pass:
        statuses["C"] = "BLOCKED"
    return audit_source_gates(
        source_family="KRX_INVESTOR_FLOW",
        intended_use_scope=scope,
        statuses=statuses,
        evidence={gate: f"evidence-{gate}" for gate in "ABCDEF"},
    )


def _batch(scope=SCOPE):
    receipt = build_acquisition_receipt(
        source_family="KRX_INVESTOR_FLOW",
        intended_use_scope=scope,
        access_route="DATA_MARKETPLACE_AUTHENTICATED_WEB_SESSION",
        dataset_identifier="MDCSTAT02303",
        authorization_evidence_reference="approval-ref-001",
        client_revision="client-rev-1",
        retrieved_at="2026-10-01T12:00:00+09:00",
        request_metadata={
            "strtDd": "20260921",
            "endDd": "20260921",
            "isuCd": "KR7005930003",
        },
        response_frame=pd.DataFrame(
            {"TRD_DD": ["20260921"], "NET_BID_TRDVAL": [100]}
        ),
    )
    return build_acquisition_batch_manifest([receipt])


def _lineage(valid=True, public_current=True):
    return {
        "lineage_structurally_valid": valid,
        "public_contract_evidence_matches_current": public_current,
        "public_contract_evidence_fingerprint": public_evidence_fingerprint_sha256(),
        "feature_performance_testing_authorized": False,
        "sealed_holdout_authorized": False,
    }


def _coverage(complete=True):
    return {
        "coverage_structurally_complete": complete,
        "feature_performance_testing_authorized": False,
        "sealed_holdout_authorized": False,
    }


def test_all_source_structure_can_only_reach_registry_review_not_performance():
    out = assess_investor_flow_source_data_admission(
        source_gate_audit=_gates(True),
        acquisition_batch_manifest=_batch(),
        lineage_audit=_lineage(True, True),
        coverage_audit=_coverage(True),
    )
    assert out["source_contract_closed"] is True
    assert out["acquisition_batch_integrity_valid"] is True
    assert out["pit_lineage_structurally_valid"] is True
    assert out["historical_coverage_structurally_complete"] is True
    assert out["source_data_structurally_admissible"] is True
    assert out["eligible_for_experiment_registry_review"] is True
    assert out["blocking_conditions"] == []
    assert out["feature_performance_testing_authorized"] is False
    assert out["sealed_holdout_authorized"] is False
    assert out["alpha_or_final_judge_promotion_authorized"] is False
    assert out["live_trading_authorized"] is False


def test_open_source_gate_blocks_admission_even_with_other_evidence_valid():
    out = assess_investor_flow_source_data_admission(
        source_gate_audit=_gates(False),
        acquisition_batch_manifest=_batch(),
        lineage_audit=_lineage(True, True),
        coverage_audit=_coverage(True),
    )
    assert out["source_data_structurally_admissible"] is False
    assert "SOURCE_CONTRACT_A_TO_F_NOT_CLOSED" in out["blocking_conditions"]


@pytest.mark.parametrize(
    "lineage_valid,coverage_complete,public_current,expected_blocker",
    [
        (False, True, True, "PIT_LINEAGE_NOT_STRUCTURALLY_VALID"),
        (True, False, True, "HISTORICAL_COVERAGE_NOT_STRUCTURALLY_COMPLETE"),
        (True, True, False, "PUBLIC_CONTRACT_EVIDENCE_NOT_CURRENT"),
    ],
)
def test_each_structural_blocker_fails_closed(
    lineage_valid, coverage_complete, public_current, expected_blocker
):
    out = assess_investor_flow_source_data_admission(
        source_gate_audit=_gates(True),
        acquisition_batch_manifest=_batch(),
        lineage_audit=_lineage(lineage_valid, public_current),
        coverage_audit=_coverage(coverage_complete),
    )
    assert out["source_data_structurally_admissible"] is False
    assert expected_blocker in out["blocking_conditions"]


def test_use_scope_mismatch_blocks_admission():
    out = assess_investor_flow_source_data_admission(
        source_gate_audit=_gates(True, scope=SCOPE),
        acquisition_batch_manifest=_batch(scope="OTHER_INTERNAL_SCOPE"),
        lineage_audit=_lineage(True, True),
        coverage_audit=_coverage(True),
    )
    assert out["source_family_and_scope_consistent"] is False
    assert "SOURCE_FAMILY_OR_USE_SCOPE_MISMATCH" in out["blocking_conditions"]
    assert out["source_data_structurally_admissible"] is False


def test_tampered_batch_manifest_is_rejected():
    batch = _batch()
    tampered = copy.deepcopy(batch)
    tampered["total_response_rows"] = 999
    with pytest.raises(KRXSourceDataAdmissionError, match="batch fingerprint mismatch"):
        assess_investor_flow_source_data_admission(
            source_gate_audit=_gates(True),
            acquisition_batch_manifest=tampered,
            lineage_audit=_lineage(True, True),
            coverage_audit=_coverage(True),
        )


def test_wrong_source_family_is_rejected():
    gates = _gates(True)
    gates = copy.deepcopy(gates)
    gates["source_family"] = "KRX_SECURITY_STATUS"
    with pytest.raises(KRXSourceDataAdmissionError, match="not KRX_INVESTOR_FLOW"):
        assess_investor_flow_source_data_admission(
            source_gate_audit=gates,
            acquisition_batch_manifest=_batch(),
            lineage_audit=_lineage(True, True),
            coverage_audit=_coverage(True),
        )
