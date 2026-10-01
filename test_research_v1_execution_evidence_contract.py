from pathlib import Path


CONTRACT = Path("INDEXALERT_EXECUTION_EVIDENCE_CONTRACT.md")


def test_contract_separates_live_structure_from_empirical_sufficiency():
    text = CONTRACT.read_text(encoding="utf-8")
    assert "live_structural_execution_evidence_present=true" in text
    assert "live_empirical_execution_evidence_ready=false" in text
    assert "empirical_execution_sufficiency_assessed=false" in text
    assert "empirical_execution_blocker_closed=false" in text
    assert "promotion_ready=true" in text  # named only in the explicit non-authority list
    assert "must **not** merely from that fact set" in text


def test_contract_requires_future_preregistered_sufficiency_protocol():
    text = CONTRACT.read_text(encoding="utf-8")
    assert "separate preregistered execution-sufficiency protocol" in text
    assert "research_v1_execution_sufficiency_protocol.py" in text
    assert "No numeric sample threshold may be invented after observing the live outcomes" in text
    assert "fill/no-fill/partial-fill" in text
    assert "latency/expiry" in text
    assert "capacity" in text
    assert "tail" in text


def test_contract_time_seals_protocol_before_first_live_observation():
    text = CONTRACT.read_text(encoding="utf-8")
    assert "strictly earlier" in text
    assert "first LIVE recommendation" in text
    assert "rejected as post-hoc" in text
    assert "unit-test fixtures are illustrative test data only" in text


def test_valid_protocol_never_claims_execution_sufficiency_by_itself():
    text = CONTRACT.read_text(encoding="utf-8")
    assert "Valid execution-sufficiency protocol = preregistered criteria only" in text
    assert "empirical_execution_sufficiency_assessed=false" in text
    assert "empirical_execution_blocker_closed=false" in text
    assert "sealed_holdout_authorized=false" in text
    assert "live_trading_authorized=false" in text
    assert "later evaluator may assess genuine LIVE evidence" in text


def test_contract_keeps_shadow_paper_live_semantics_distinct():
    text = CONTRACT.read_text(encoding="utf-8")
    assert "PROSPECTIVE_SHADOW_DECISION_LOG" in text
    assert "PROSPECTIVE_PAPER_EXECUTION_LOG" in text
    assert "PROSPECTIVE_LIVE_EXECUTION_LOG" in text
    assert "Paper observations" in text
    assert "not evidence of real-market fill quality" in text
    assert "Real-account ordering remains disabled" in text
