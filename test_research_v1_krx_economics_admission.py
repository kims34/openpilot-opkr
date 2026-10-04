import pytest

from research_v1_krx_economics_admission import (
    KRXEconomicsAdmissionError,
    audit_krx_economics_admission,
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


def test_completed_krx_scope_is_admitted_without_promoting_economics():
    out = audit_krx_economics_admission(PER, STATUS)
    assert out["krx_historical_scope_verified"] is True
    assert out["cleanup_price_context_complete"] is True
    assert out["exact_status_economics_ready"] is False
    assert out["sealed_holdout_authorized"] is False
    assert out["shadow_s1_authorized"] is False
    assert out["fresh_confirmation_s2_authorized"] is False
    assert out["live_trading_authorized"] is False
    assert out["next_blocker"] == "INDEPENDENT_REALIZED_FILL_AND_RECOVERY_ECONOMICS_EVIDENCE"


def test_task_fingerprint_drift_fails_closed():
    bad = dict(STATUS)
    bad["task_set_fingerprint_sha256"] = "0" * 64
    with pytest.raises(KRXEconomicsAdmissionError, match="fingerprint drift"):
        audit_krx_economics_admission(PER, bad)


def test_illegal_downstream_authority_fails_closed():
    bad = dict(STATUS)
    bad["sealed_holdout_authorized"] = True
    with pytest.raises(KRXEconomicsAdmissionError, match="illegally true"):
        audit_krx_economics_admission(PER, bad)


def test_incomplete_cleanup_context_fails_closed():
    bad = dict(STATUS)
    bad["cleanup_price_context_complete"] = False
    with pytest.raises(KRXEconomicsAdmissionError, match="not complete"):
        audit_krx_economics_admission(PER, bad)
