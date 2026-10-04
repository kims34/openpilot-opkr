"""Fail-closed admission audit for completed KRX historical acquisition phases.

This module is deliberately network-free. It binds public-safe completion
metadata to the frozen KRX scopes and prevents cleanup-price context from being
misrepresented as realized execution/recovery economics or promotion authority.
"""
from __future__ import annotations

from typing import Any, Mapping

PER_SECURITY_TASK_COUNT = 14296
PER_SECURITY_TASK_SET_SHA256 = "fb5b883c6fe0e9c15e88aea9bdf874ddd7a11ae8a009c2ddf91c4e4249a8ba38"
STATUS_ECONOMICS_TASK_COUNT = 27
STATUS_ECONOMICS_TASK_SET_SHA256 = "b3738dca89ab5cb6966a1e3158f995b75cbf6e2ae2cd4c199f02c95a8ba4c1d8"


class KRXEconomicsAdmissionError(ValueError):
    pass


def _require_complete(
    summary: Mapping[str, Any], *, phase: str, count: int, fingerprint: str
) -> None:
    if summary.get("phase") != phase or summary.get("status") != "COMPLETE":
        raise KRXEconomicsAdmissionError(f"{phase} is not COMPLETE")
    if int(summary.get("expected_task_count", -1)) != count:
        raise KRXEconomicsAdmissionError(f"{phase} expected task count drift")
    if int(summary.get("completed_task_count", -1)) != count:
        raise KRXEconomicsAdmissionError(f"{phase} completed task count drift")
    if int(summary.get("failed_task_count", -1)) != 0:
        raise KRXEconomicsAdmissionError(f"{phase} contains failed tasks")
    if str(summary.get("task_set_fingerprint_sha256") or "") != fingerprint:
        raise KRXEconomicsAdmissionError(f"{phase} task-set fingerprint drift")


def audit_krx_economics_admission(
    per_security: Mapping[str, Any],
    status_economics: Mapping[str, Any],
) -> dict[str, Any]:
    """Audit completed public metadata without opening any downstream gate."""
    _require_complete(
        per_security,
        phase="PER_SECURITY_HISTORY",
        count=PER_SECURITY_TASK_COUNT,
        fingerprint=PER_SECURITY_TASK_SET_SHA256,
    )
    _require_complete(
        status_economics,
        phase="STATUS_ECONOMICS",
        count=STATUS_ECONOMICS_TASK_COUNT,
        fingerprint=STATUS_ECONOMICS_TASK_SET_SHA256,
    )

    # STATUS_ECONOMICS proves only the frozen cleanup-price context. These
    # downstream claims require independent evidence and remain fail-closed.
    forbidden_true = (
        "exact_status_economics_ready",
        "realized_fill_economics_proven",
        "realized_recovery_cashflows_proven",
        "source_gate_c_closed",
        "source_gate_d_closed",
        "source_gate_e_closed",
        "feature_performance_testing_authorized",
        "sealed_holdout_authorized",
        "shadow_s1_authorized",
        "genuine_live_authorized",
        "live_trading_authorized",
    )
    illegally_true = [k for k in forbidden_true if status_economics.get(k) is True]
    if illegally_true:
        raise KRXEconomicsAdmissionError(
            "downstream authority illegally true: " + ",".join(illegally_true)
        )

    if status_economics.get("cleanup_price_context_complete") is not True:
        raise KRXEconomicsAdmissionError("cleanup price context is not complete")

    return {
        "krx_historical_scope_verified": True,
        "per_security_history_complete": True,
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
        "fresh_confirmation_s2_authorized": False,
        "genuine_live_authorized": False,
        "live_trading_authorized": False,
        "next_blocker": "INDEPENDENT_REALIZED_FILL_AND_RECOVERY_ECONOMICS_EVIDENCE",
    }
