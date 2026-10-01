import pytest

from research_v1_krx_source_gates import (
    SOURCE_GATE_DEFINITIONS,
    audit_source_gates,
)


def _evidence():
    return {gate: f"evidence-{gate}" for gate in "ABCDEF"}


def test_source_gate_contract_is_exactly_a_to_f():
    assert list(SOURCE_GATE_DEFINITIONS) == list("ABCDEF")
    assert SOURCE_GATE_DEFINITIONS["A"]["name"] == "AUTHORIZED_OFFICIAL_ROUTE"
    assert SOURCE_GATE_DEFINITIONS["B"]["name"] == "EXACT_DATASET_SCHEMA_MAPPING"
    assert SOURCE_GATE_DEFINITIONS["C"]["name"] == "HISTORICAL_COVERAGE_SECURITY_MAPPING"
    assert SOURCE_GATE_DEFINITIONS["D"]["name"] == "PIT_AVAILABILITY_LINEAGE"
    assert SOURCE_GATE_DEFINITIONS["E"]["name"] == "REPRODUCIBLE_INTEGRITY_FAIL_CLOSED"
    assert SOURCE_GATE_DEFINITIONS["F"]["name"] == "INTENDED_USE_RIGHTS"


def test_partial_gate_never_closes_source_contract():
    out = audit_source_gates(
        source_family="KRX_STATUS",
        intended_use_scope="INTERNAL_RESEARCH",
        statuses={
            "A": "PASS",
            "B": "PASS",
            "C": "PASS",
            "D": "PASS",
            "E": "PARTIAL",
            "F": "PASS",
        },
        evidence=_evidence(),
    )
    assert out["all_source_gates_pass"] is False
    assert out["source_contract_closed_for_declared_scope"] is False
    assert out["gates"]["E"]["status"] == "PARTIAL"


def test_all_source_gates_pass_still_does_not_authorize_promotion_or_holdout():
    out = audit_source_gates(
        source_family="KRX_INVESTOR_FLOW",
        intended_use_scope="INTERNAL_RESEARCH",
        statuses={gate: "PASS" for gate in "ABCDEF"},
        evidence=_evidence(),
    )
    assert out["all_source_gates_pass"] is True
    assert out["source_contract_closed_for_declared_scope"] is True
    assert out["alpha_or_final_judge_promotion_authorized"] is False
    assert out["sealed_holdout_authorized_by_source_audit_alone"] is False
    assert out["live_trading_authorized_by_source_audit_alone"] is False


def test_missing_gate_fails_closed():
    with pytest.raises(ValueError, match="exactly A-F"):
        audit_source_gates(
            source_family="KRX_STATUS",
            intended_use_scope="INTERNAL_RESEARCH",
            statuses={gate: "BLOCKED" for gate in "ABCDE"},
            evidence=_evidence(),
        )


def test_unknown_gate_status_is_rejected():
    statuses = {gate: "BLOCKED" for gate in "ABCDEF"}
    statuses["D"] = "UNKNOWN"
    with pytest.raises(ValueError, match="invalid status"):
        audit_source_gates(
            source_family="KRX_STATUS",
            intended_use_scope="INTERNAL_RESEARCH",
            statuses=statuses,
            evidence=_evidence(),
        )


def test_empty_evidence_is_rejected():
    evidence = _evidence()
    evidence["C"] = ""
    with pytest.raises(ValueError, match="non-empty evidence"):
        audit_source_gates(
            source_family="KRX_STATUS",
            intended_use_scope="INTERNAL_RESEARCH",
            statuses={gate: "BLOCKED" for gate in "ABCDEF"},
            evidence=evidence,
        )
