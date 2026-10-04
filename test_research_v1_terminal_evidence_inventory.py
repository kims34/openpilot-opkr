import pytest

from research_v1_krx_economics_admission import KRXEconomicsAdmissionError
from research_v1_terminal_evidence_inventory import audit_terminal_evidence_inventory


def test_empty_inventory_exposes_all_56_as_unresolved():
    out = audit_terminal_evidence_inventory([])
    assert out["expected_no_cleanup_episode_count"] == 56
    assert out["valid_terminal_evidence_count"] == 0
    assert out["unresolved_terminal_evidence_count"] == 56
    assert out["terminal_evidence_inventory_complete"] is False
    assert out["sealed_holdout_authorized"] is False


def test_one_proven_recovery_reduces_gap_without_opening_authority():
    row = {
        "episode_evidence_key": "opaque-episode-1",
        "terminal_treatment": "CASH_RECOVERY",
        "source_artifact_sha256": "a" * 64,
        "pit_available_at": "2025-01-02T09:00:00+09:00",
        "amount": 123.0,
    }
    out = audit_terminal_evidence_inventory([row])
    assert out["valid_terminal_evidence_count"] == 1
    assert out["unresolved_terminal_evidence_count"] == 55
    assert out["exact_status_economics_ready"] is False


def test_zero_recovery_requires_explicit_zero():
    row = {
        "episode_evidence_key": "opaque-episode-1",
        "terminal_treatment": "ZERO_RECOVERY_PROVEN",
        "source_artifact_sha256": "a" * 64,
        "pit_available_at": "2025-01-02T09:00:00+09:00",
        "amount": 1,
    }
    with pytest.raises(KRXEconomicsAdmissionError, match="nonzero"):
        audit_terminal_evidence_inventory([row])


def test_duplicate_episode_evidence_fails_closed():
    row = {
        "episode_evidence_key": "opaque-episode-1",
        "terminal_treatment": "ZERO_RECOVERY_PROVEN",
        "source_artifact_sha256": "a" * 64,
        "pit_available_at": "2025-01-02T09:00:00+09:00",
        "amount": 0,
    }
    with pytest.raises(KRXEconomicsAdmissionError, match="duplicate"):
        audit_terminal_evidence_inventory([row, dict(row)])
