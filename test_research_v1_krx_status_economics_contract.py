from pathlib import Path

from research_v1_krx_status_economics import (
    ALLOWED_FILL_EVIDENCE,
    ALLOWED_RECOVERY_EVIDENCE,
    FORBIDDEN_EXACT_EVIDENCE,
)


CONTRACT = Path("INDEXALERT_KRX_STATUS_ECONOMICS_CONTRACT.md")


def test_contract_mentions_all_executable_evidence_classes():
    text = CONTRACT.read_text(encoding="utf-8")
    for name in sorted(ALLOWED_FILL_EVIDENCE):
        assert name in text
    for name in sorted(ALLOWED_RECOVERY_EVIDENCE):
        assert name in text
    for name in sorted(FORBIDDEN_EXACT_EVIDENCE):
        assert name in text or name.replace("_", " ").lower() in text.lower()


def test_contract_freezes_quantity_conservation_and_independent_scope_attestation():
    text = CONTRACT.read_text(encoding="utf-8")
    assert "expected_scope_attested=true" in text
    assert "affected_qty = verified_exit_fill_qty + verified_recovery_qty" in text
    assert "No missing fill or recovery quantity may be imputed" in text
    assert "empty affected-position set is acceptable only when that empty set is independently attested" in text


def test_contract_never_turns_exact_status_economics_into_promotion_authority():
    text = CONTRACT.read_text(encoding="utf-8")
    assert "judge_security_status_ready=false" in text
    assert "feature_performance_testing_authorized=false" in text
    assert "sealed_holdout_authorized=false" in text
    assert "alpha_or_final_judge_promotion_authorized=false" in text
    assert "live_trading_authorized=false" in text
    assert "project-level exact halt/delisting economics blocker remains open" in text
