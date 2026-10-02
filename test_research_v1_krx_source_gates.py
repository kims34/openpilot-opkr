from pathlib import Path

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


def test_normative_docs_freeze_gate_labels_and_canonical_names():
    docs = [
        Path("INDEXALERT_KRX_SOURCE_ACCESS_CONTRACT.md"),
        Path("INDEXALERT_KRX_SOURCE_GATE_AUDIT.md"),
        Path("INDEXALERT_MASTER_SPEC.md"),
    ]
    for path in docs:
        text = path.read_text(encoding="utf-8")
        for gate, definition in SOURCE_GATE_DEFINITIONS.items():
            assert f"Gate {gate}" in text, f"{path} missing Gate {gate}"
            assert definition["name"] in text, (
                f"{path} missing canonical name for Gate {gate}: {definition['name']}"
            )


def test_summary_and_handoff_docs_preserve_all_canonical_gate_names():
    docs = [
        Path("INDEXALERT_RESEARCH_STATUS.md"),
        Path("INDEXALERT_CONTINUITY_SNAPSHOT.md"),
    ]
    for path in docs:
        text = path.read_text(encoding="utf-8")
        for gate, definition in SOURCE_GATE_DEFINITIONS.items():
            assert definition["name"] in text, (
                f"{path} missing canonical name for Gate {gate}: {definition['name']}"
            )


def test_canonical_docs_preserve_non_promotion_boundary():
    master = Path("INDEXALERT_MASTER_SPEC.md").read_text(encoding="utf-8")
    contract = Path("INDEXALERT_KRX_SOURCE_ACCESS_CONTRACT.md").read_text(encoding="utf-8")
    audit = Path("INDEXALERT_KRX_SOURCE_GATE_AUDIT.md").read_text(encoding="utf-8")
    status = Path("INDEXALERT_RESEARCH_STATUS.md").read_text(encoding="utf-8")
    handoff = Path("INDEXALERT_CONTINUITY_SNAPSHOT.md").read_text(encoding="utf-8")

    assert "Even six PASS results" in master
    assert "All six gates passing means only" in contract
    assert "one-shot sealed holdout" in audit
    assert "one-shot sealed holdout" in status
    assert "sealed holdout" in handoff
    assert "Purged/CPCV" in master
    assert "distributional NetEV" in master
    assert "live trading" in audit
    assert "live trading" in handoff


def test_canonical_source_docs_freeze_structured_authorization_evidence_boundary():
    contract = Path("INDEXALERT_KRX_SOURCE_ACCESS_CONTRACT.md").read_text(encoding="utf-8")
    audit = Path("INDEXALERT_KRX_SOURCE_GATE_AUDIT.md").read_text(encoding="utf-8")
    status = Path("INDEXALERT_RESEARCH_STATUS.md").read_text(encoding="utf-8")
    handoff = Path("INDEXALERT_CONTINUITY_SNAPSHOT.md").read_text(encoding="utf-8")

    for name, text in {
        "contract": contract,
        "audit": audit,
        "status": status,
        "handoff": handoff,
    }.items():
        assert "research_v1_krx_authorization_evidence.py" in text, (
            f"{name} missing structured authorization evidence validator"
        )
        assert "KRX_AUTH_EVIDENCE_JSON" in text, (
            f"{name} missing structured authorization evidence configuration contract"
        )
        assert "KRX_EXPLICIT_PROBE_CONSENT" in text, (
            f"{name} missing explicit per-run consent boundary"
        )
        assert "network-free" in text.lower(), (
            f"{name} missing network-free readiness boundary"
        )

    assert "opaque approval reference is not validated evidence" in contract
    # Authenticated, explicitly-consented tiny probes now establish route
    # reachability for both declared Data Marketplace source families.  This
    # may raise Gate A only to PARTIAL; full-history/source-contract closure
    # remains separate and Gate A must never be inferred PASS from a tiny probe.
    assert "**Security/status:** A PARTIAL" in status
    assert "**Investor flow:** A PARTIAL" in status
    assert "Security/status: A PARTIAL" in handoff
    assert "Investor flow: A PARTIAL" in handoff
    assert "Gate A" in status and "PARTIAL" in status
    assert "Gate A" in handoff and "PARTIAL" in handoff
