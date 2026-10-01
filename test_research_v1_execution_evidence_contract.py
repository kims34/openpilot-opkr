from pathlib import Path


CONTRACT = Path("INDEXALERT_EXECUTION_EVIDENCE_CONTRACT.md")
PROVENANCE = Path("INDEXALERT_LIVE_EXECUTION_PROVENANCE_CONTRACT.md")


def test_contract_separates_live_structure_from_empirical_sufficiency():
    text = CONTRACT.read_text(encoding="utf-8")
    assert "live_structural_execution_evidence_present=true" in text
    assert "live_empirical_execution_evidence_ready=false" in text
    assert "empirical_execution_blocker_closed=false" in text
    assert "promotion_ready=true" in text  # named only in the explicit non-authority list
    assert "must **not** merely from that fact set" in text


def test_contract_requires_frozen_numerical_sufficiency_protocol():
    text = CONTRACT.read_text(encoding="utf-8")
    assert "research_v1_execution_sufficiency_protocol.py" in text
    assert "minimum LIVE observation count" in text
    assert "minimum filled/no-fill/partial-fill observation counts" in text
    assert "slippage, latency, capacity and tail evidence" in text
    assert "fixed before any genuine LIVE observation" in text
    assert "execution_metric_gates_passed=true" in text


def test_contract_time_seals_protocol_before_first_live_observation():
    text = CONTRACT.read_text(encoding="utf-8")
    assert "strictly earlier" in text
    assert "first LIVE recommendation" in text
    assert "rejected as post-hoc" in text
    assert "Unit-test fixture values remain non-evidence" in text
    assert "fixed before any genuine LIVE observation" in text


def test_metric_pass_cannot_authenticate_genuine_live_provenance():
    text = CONTRACT.read_text(encoding="utf-8")
    provenance = PROVENANCE.read_text(encoding="utf-8")
    assert "INDEXALERT_LIVE_EXECUTION_PROVENANCE_CONTRACT.md" in text
    assert "genuine_live_provenance_verified=false" in text
    assert "live_empirical_execution_evidence_ready=false" in text
    assert "empirical_execution_blocker_closed=false" in text
    assert "source label, CSV SHA-256" in text
    assert "A file hash proves byte identity only" in provenance
    assert "broker-native" in provenance
    assert "row-level mapping" in provenance


def test_contract_keeps_shadow_paper_live_semantics_distinct():
    text = CONTRACT.read_text(encoding="utf-8")
    assert "PROSPECTIVE_SHADOW_DECISION_LOG" in text
    assert "PROSPECTIVE_PAPER_EXECUTION_LOG" in text
    assert "PROSPECTIVE_LIVE_EXECUTION_LOG" in text
    assert "Paper observations" in text
    assert "not evidence of real-market fill quality" in text
    assert "Real-account ordering remains disabled" in text
