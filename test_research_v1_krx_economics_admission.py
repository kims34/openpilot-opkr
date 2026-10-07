import pytest

from research_v1_krx_economics_admission import (
    KRXEconomicsAdmissionError,
    audit_krx_economics_admission,
    audit_terminal_treatment_coverage,
)


PER = {
    "phase": "PER_SECURITY_HISTORY",
    "status": "COMPLETE",
    "expected_task_count": 14296,
    "completed_task_count": 14296,
    "failed_task_count": 0,
    "task_set_fingerprint_sha256": "fb5b883c6fe0e9c15e88aea9bdf874ddd7a11ae8a009c2ddf91c4e4249a8ba38",
}

STATUS = {
    "phase": "STATUS_ECONOMICS",
    "status": "COMPLETE",
    "expected_task_count": 27,
    "completed_task_count": 27,
    "failed_task_count": 0,
    "task_set_fingerprint_sha256": "b3738dca89ab5cb6966a1e3158f995b75cbf6e2ae2cd4c199f02c95a8ba4c1d8",
    "cleanup_price_context_complete": True,
    "exact_status_economics_ready": False,
    "realized_fill_economics_proven": False,
    "realized_recovery_cashflows_proven": False,
    "source_gate_c_closed": False,
    "source_gate_d_closed": False,
    "source_gate_e_closed": False,
    "feature_performance_testing_authorized": False,
    "sealed_holdout_authorized": False,
    "shadow_s1_authorized": False,
    "genuine_live_authorized": False,
    "live_trading_authorized": False,
}


def test_completed_krx_scope_metadata_never_self_admits_historical_scope():
    out = audit_krx_economics_admission(PER, STATUS)
    assert out["krx_historical_scope_completion_metadata_valid"] is True
    assert out["per_security_history_completion_metadata_valid"] is True
    assert out["cleanup_price_context_completion_metadata_valid"] is True
    assert out["independent_krx_historical_scope_admission_verified"] is False
    assert out["krx_historical_scope_verified"] is False
    assert out["per_security_history_complete"] is False
    assert out["cleanup_price_context_complete"] is False
    assert out["exact_status_economics_ready"] is False
    assert out["sealed_holdout_authorized"] is False
    assert out["shadow_s1_authorized"] is False
    assert out["fresh_confirmation_s2_authorized"] is False
    assert out["live_trading_authorized"] is False
    assert out["blocking_conditions"] == (
        "INDEPENDENT_KRX_HISTORICAL_SCOPE_ADMISSION_NOT_IMPLEMENTED",
        "INDEPENDENT_REALIZED_FILL_AND_RECOVERY_ECONOMICS_EVIDENCE",
    )
    assert out["next_blocker"] == "INDEPENDENT_KRX_HISTORICAL_SCOPE_ADMISSION_NOT_IMPLEMENTED"


def test_task_fingerprint_drift_fails_closed():
    bad = dict(STATUS)
    bad["task_set_fingerprint_sha256"] = "0" * 64
    with pytest.raises(KRXEconomicsAdmissionError, match="fingerprint drift"):
        audit_krx_economics_admission(PER, bad)


def test_downstream_authority_fields_must_be_present_exact_false():
    for value in (True, None, 0, "false"):
        bad = dict(STATUS)
        bad["sealed_holdout_authorized"] = value
        with pytest.raises(KRXEconomicsAdmissionError, match="exact false"):
            audit_krx_economics_admission(PER, bad)


def test_incomplete_cleanup_context_fails_closed():
    bad = dict(STATUS)
    bad["cleanup_price_context_complete"] = False
    with pytest.raises(KRXEconomicsAdmissionError, match="not complete"):
        audit_krx_economics_admission(PER, bad)


def test_terminal_treatment_gap_is_quantified_without_identifiers():
    out = audit_terminal_treatment_coverage(
        delisted_episode_count=83,
        cleanup_price_episode_count=27,
    )
    assert out["no_cleanup_interval_episode_count"] == 56
    assert out["claimed_independently_resolved_no_cleanup_episode_count"] == 0
    assert out["independently_resolved_no_cleanup_episode_count"] == 0
    assert out["independent_terminal_treatment_resolution_verified"] is False
    assert out["unresolved_terminal_treatment_episode_count"] == 56
    assert out["terminal_treatment_coverage_complete"] is False
    assert out["security_identifiers_emitted"] is False
    assert out["sealed_holdout_authorized"] is False



def test_claimed_terminal_resolution_cannot_create_verified_complete_coverage():
    out = audit_terminal_treatment_coverage(
        delisted_episode_count=83,
        cleanup_price_episode_count=27,
        independently_resolved_no_cleanup_episode_count=56,
    )
    assert out["claimed_independently_resolved_no_cleanup_episode_count"] == 56
    assert out["terminal_treatment_coverage_structural_claim_complete"] is True
    assert out["independent_terminal_treatment_resolution_verified"] is False
    assert out["independently_resolved_no_cleanup_episode_count"] == 0
    assert out["unresolved_terminal_treatment_episode_count"] == 56
    assert out["terminal_treatment_coverage_complete"] is False


@pytest.mark.parametrize("value", [True, 1.0, "83", None])
def test_coverage_counts_require_exact_integers(value):
    with pytest.raises(KRXEconomicsAdmissionError, match="exact integers"):
        audit_terminal_treatment_coverage(
            delisted_episode_count=value,
            cleanup_price_episode_count=27,
        )


@pytest.mark.parametrize("field,value", [
    ("expected_task_count", True),
    ("completed_task_count", "14296"),
    ("failed_task_count", False),
])
def test_completion_counts_do_not_coerce_types(field, value):
    bad = dict(PER)
    bad[field] = value
    with pytest.raises(KRXEconomicsAdmissionError):
        audit_krx_economics_admission(bad, STATUS)

def test_terminal_treatment_count_inconsistency_fails_closed():
    with pytest.raises(KRXEconomicsAdmissionError, match="exceeds delisted total"):
        audit_terminal_treatment_coverage(
            delisted_episode_count=83,
            cleanup_price_episode_count=84,
        )
