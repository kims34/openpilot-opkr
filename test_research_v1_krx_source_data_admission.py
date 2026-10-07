import copy

import pandas as pd
import pytest

from research_v1_krx_acquisition_batch import build_acquisition_batch_manifest
from research_v1_krx_acquisition_receipt import build_acquisition_receipt, _sha256
from research_v1_krx_public_evidence import public_evidence_fingerprint_sha256
from research_v1_krx_source_data_admission import (
    BATCH_BODY_FIELDS,
    KRXSourceDataAdmissionError,
    assess_investor_flow_source_data_admission,
)
from research_v1_krx_source_gates import audit_source_gates


SCOPE = "INTERNAL_RESEARCH_CANDIDATE_FEATURE_PREPARATION"
AUTH_EVIDENCE_FP = "c" * 64


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


def _batch(scope=SCOPE, auth_evidence_fp=AUTH_EVIDENCE_FP):
    receipt = build_acquisition_receipt(
        source_family="KRX_INVESTOR_FLOW",
        intended_use_scope=scope,
        access_route="DATA_MARKETPLACE_AUTHENTICATED_WEB_SESSION",
        dataset_identifier="MDCSTAT02303",
        authorization_evidence_reference="approval-ref-001",
        authorization_evidence_fingerprint_sha256=auth_evidence_fp,
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
    assert out["authorization_evidence_fingerprint_present"] is True
    assert out["authorization_evidence_provenance_bound"] is False
    assert out["independent_authorization_evidence_binding_verified"] is False
    assert out["independent_admission_blocking_conditions"] == [
        "INDEPENDENT_AUTHORIZATION_EVIDENCE_BINDING_NOT_IMPLEMENTED"
    ]
    assert out["authorization_evidence_fingerprint_sha256"] == AUTH_EVIDENCE_FP
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


def test_missing_structured_authorization_fingerprint_is_rejected():
    batch = _batch()
    tampered = copy.deepcopy(batch)
    tampered.pop("authorization_evidence_fingerprint_sha256")
    with pytest.raises(KRXSourceDataAdmissionError, match="missing required fields"):
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


@pytest.mark.parametrize("field", [
    "alpha_or_final_judge_promotion_authorized",
    "sealed_holdout_authorized",
    "live_trading_authorized",
])
@pytest.mark.parametrize("value", [None, 0, "", [], {}, 1, "false"])
def test_rehashed_batch_requires_exact_false_authority_flags(field, value):
    # A valid fingerprint must not turn malformed authority values into evidence.
    batch = _batch()
    batch[field] = value
    batch["batch_fingerprint_sha256"] = _sha256(
        {name: batch[name] for name in BATCH_BODY_FIELDS}
    )
    with pytest.raises(KRXSourceDataAdmissionError, match="illegally claims authority"):
        assess_investor_flow_source_data_admission(
            source_gate_audit=_gates(True), acquisition_batch_manifest=batch,
            lineage_audit=_lineage(True, True), coverage_audit=_coverage(True),
        )

@pytest.mark.parametrize("field,value", [
    ("receipt_count", True), ("receipt_count", "1"), ("receipt_count", 1.8),
    ("receipt_count", None), ("receipt_count", 0), ("receipt_count", -1),
    ("total_response_rows", True), ("total_response_rows", "1"),
    ("total_response_rows", 1.8), ("total_response_rows", None),
    ("total_response_rows", -1),
    ("receipt_fingerprints_sha256", "x"),
    ("receipt_fingerprints_sha256", {"a" * 64: True}),
    ("receipt_fingerprints_sha256", ["not-a-digest"]),
    ("receipt_fingerprints_sha256", [None]),
    ("receipt_fingerprints_sha256", [[]]),
    ("receipt_fingerprints_sha256", []),
    ("receipt_fingerprints_sha256", ["a" * 64, "a" * 64]),
])
def test_rehashed_batch_rejects_malformed_counts_and_receipt_digests(field, value):
    batch = _batch()
    batch[field] = value
    batch["batch_fingerprint_sha256"] = _sha256(
        {name: batch[name] for name in BATCH_BODY_FIELDS}
    )
    with pytest.raises(KRXSourceDataAdmissionError):
        assess_investor_flow_source_data_admission(
            source_gate_audit=_gates(True), acquisition_batch_manifest=batch,
            lineage_audit=_lineage(True, True), coverage_audit=_coverage(True),
        )

@pytest.mark.parametrize("field", ["coverage_validated", "pit_lineage_validated"])
@pytest.mark.parametrize("value", [None, 0, 0.0, "", [], {}, True, "false"])
def test_rehashed_batch_cannot_claim_coverage_or_pit_authority(field, value):
    batch = _batch()
    batch[field] = value
    batch["batch_fingerprint_sha256"] = _sha256(
        {name: batch[name] for name in BATCH_BODY_FIELDS}
    )
    with pytest.raises(KRXSourceDataAdmissionError, match="illegally claims authority"):
        assess_investor_flow_source_data_admission(
            source_gate_audit=_gates(True), acquisition_batch_manifest=batch,
            lineage_audit=_lineage(True, True), coverage_audit=_coverage(True),
        )

@pytest.mark.parametrize("field", [
    "source_family", "intended_use_scope", "access_route", "dataset_identifier",
    "authorization_evidence_reference", "client_revision", "public_contract_evidence_version",
])
@pytest.mark.parametrize("value", [None, 0, {}, ""])
def test_rehashed_direct_batch_rejects_non_string_contracts(field, value):
    batch = _batch()
    batch[field] = value
    batch["batch_fingerprint_sha256"] = _sha256(
        {name: batch[name] for name in BATCH_BODY_FIELDS}
    )
    with pytest.raises(KRXSourceDataAdmissionError):
        assess_investor_flow_source_data_admission(
            source_gate_audit=_gates(True), acquisition_batch_manifest=batch,
            lineage_audit=_lineage(True, True), coverage_audit=_coverage(True),
        )


@pytest.mark.parametrize("field,value", [
    ("authorization_evidence_fingerprint_sha256", int("1" * 64)),
    ("response_schema_sha256", "not-a-digest"),
    ("public_contract_evidence_fingerprint_sha256", None),
    ("access_route", "UNOFFICIAL_PROXY"),
    ("authorization_evidence_reference", "TOKEN=synthetic-placeholder"),
])
def test_rehashed_direct_batch_preserves_acquisition_contract(field, value):
    batch = _batch()
    batch[field] = value
    batch["batch_fingerprint_sha256"] = _sha256(
        {name: batch[name] for name in BATCH_BODY_FIELDS}
    )
    with pytest.raises(KRXSourceDataAdmissionError):
        assess_investor_flow_source_data_admission(
            source_gate_audit=_gates(True), acquisition_batch_manifest=batch,
            lineage_audit=_lineage(True, True), coverage_audit=_coverage(True),
        )


@pytest.mark.parametrize("gate", list("ABCDEF"))
@pytest.mark.parametrize("status", ["PARTIAL", "BLOCKED"])
def test_stale_source_closed_summary_cannot_hide_open_gate(gate, status):
    gates = _gates(True)
    gates["gates"][gate]["status"] = status
    with pytest.raises(KRXSourceDataAdmissionError, match="summary/authority drift"):
        assess_investor_flow_source_data_admission(
            source_gate_audit=gates, acquisition_batch_manifest=_batch(),
            lineage_audit=_lineage(), coverage_audit=_coverage(),
        )


@pytest.mark.parametrize("field", [
    "all_source_gates_pass", "source_contract_closed_for_declared_scope",
    "alpha_or_final_judge_promotion_authorized",
    "sealed_holdout_authorized_by_source_audit_alone",
    "live_trading_authorized_by_source_audit_alone",
])
@pytest.mark.parametrize("value", [None, 0, "false"])
def test_source_audit_summary_requires_exact_canonical_booleans(field, value):
    gates = _gates(True)
    gates[field] = value
    with pytest.raises(KRXSourceDataAdmissionError, match="summary/authority drift"):
        assess_investor_flow_source_data_admission(
            source_gate_audit=gates, acquisition_batch_manifest=_batch(),
            lineage_audit=_lineage(), coverage_audit=_coverage(),
        )


@pytest.mark.parametrize("mutation", ["missing_gate", "extra_gate", "non_mapping", "missing_entries",
                                     "status_nonstring", "invalid_status", "evidence_null", "evidence_blank"])
def test_source_audit_incomplete_or_malformed_entries_fail_closed(mutation):
    gates = _gates(True)
    if mutation == "missing_gate":
        del gates["gates"]["C"]
    elif mutation == "extra_gate":
        gates["gates"]["G"] = gates["gates"]["A"]
    elif mutation == "non_mapping":
        gates["gates"]["C"] = []
    elif mutation == "missing_entries":
        del gates["gates"]
    elif mutation == "status_nonstring":
        gates["gates"]["C"]["status"] = 1
    elif mutation == "invalid_status":
        gates["gates"]["C"]["status"] = "IDEA"
    elif mutation == "evidence_null":
        gates["gates"]["C"]["evidence"] = None
    else:
        gates["gates"]["C"]["evidence"] = " "
    with pytest.raises(KRXSourceDataAdmissionError):
        assess_investor_flow_source_data_admission(
            source_gate_audit=gates, acquisition_batch_manifest=_batch(),
            lineage_audit=_lineage(), coverage_audit=_coverage(),
        )
