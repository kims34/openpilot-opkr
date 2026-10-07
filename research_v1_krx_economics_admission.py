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
    if not isinstance(summary, Mapping):
        raise KRXEconomicsAdmissionError(f"{phase} summary must be a mapping")
    if summary.get("phase") != phase or summary.get("status") != "COMPLETE":
        raise KRXEconomicsAdmissionError(f"{phase} is not COMPLETE")
    expected = summary.get("expected_task_count")
    completed = summary.get("completed_task_count")
    failed = summary.get("failed_task_count")
    if type(expected) is not int or expected != count:
        raise KRXEconomicsAdmissionError(f"{phase} expected task count drift")
    if type(completed) is not int or completed != count:
        raise KRXEconomicsAdmissionError(f"{phase} completed task count drift")
    if type(failed) is not int or failed != 0:
        raise KRXEconomicsAdmissionError(f"{phase} contains failed tasks")
    digest = summary.get("task_set_fingerprint_sha256")
    if type(digest) is not str or digest != fingerprint:
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
    non_false = [k for k in forbidden_true if status_economics.get(k) is not False]
    if non_false:
        raise KRXEconomicsAdmissionError(
            "downstream authority must be exact false: " + ",".join(non_false)
        )

    if status_economics.get("cleanup_price_context_complete") is not True:
        raise KRXEconomicsAdmissionError("cleanup price context is not complete")

    # Exact task counts/fingerprints validate only the supplied completion
    # metadata shape. This network-free compositor cannot authenticate the
    # underlying private acquisition artifacts or independently admit scope.
    return {
        "krx_historical_scope_completion_metadata_valid": True,
        "per_security_history_completion_metadata_valid": True,
        "cleanup_price_context_completion_metadata_valid": True,
        "independent_krx_historical_scope_admission_verified": False,
        "krx_historical_scope_verified": False,
        "per_security_history_complete": False,
        "cleanup_price_context_complete": False,
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
        "blocking_conditions": (
            "INDEPENDENT_KRX_HISTORICAL_SCOPE_ADMISSION_NOT_IMPLEMENTED",
            "INDEPENDENT_REALIZED_FILL_AND_RECOVERY_ECONOMICS_EVIDENCE",
        ),
        "next_blocker": "INDEPENDENT_KRX_HISTORICAL_SCOPE_ADMISSION_NOT_IMPLEMENTED",
    }


def audit_terminal_treatment_coverage(
    *,
    delisted_episode_count: int,
    cleanup_price_episode_count: int,
    independently_resolved_no_cleanup_episode_count: int = 0,
) -> dict[str, Any]:
    """Network-free aggregate claim audit; never authenticates resolution evidence."""
    values = (
        delisted_episode_count,
        cleanup_price_episode_count,
        independently_resolved_no_cleanup_episode_count,
    )
    if any(type(value) is not int for value in values):
        raise KRXEconomicsAdmissionError("coverage counts must be exact integers")
    total, cleanup, claimed_resolved = values
    if min(total, cleanup, claimed_resolved) < 0:
        raise KRXEconomicsAdmissionError("coverage counts cannot be negative")
    if cleanup > total:
        raise KRXEconomicsAdmissionError("cleanup episode count exceeds delisted total")
    no_cleanup = total - cleanup
    if claimed_resolved > no_cleanup:
        raise KRXEconomicsAdmissionError(
            "resolved no-cleanup count exceeds no-cleanup episode count"
        )
    structural_unresolved = no_cleanup - claimed_resolved
    return {
        "delisted_episode_count": total,
        "cleanup_price_context_episode_count": cleanup,
        "no_cleanup_interval_episode_count": no_cleanup,
        "claimed_independently_resolved_no_cleanup_episode_count": claimed_resolved,
        "independent_terminal_treatment_resolution_verified": False,
        "independently_resolved_no_cleanup_episode_count": 0,
        "structural_unresolved_terminal_treatment_episode_count": structural_unresolved,
        "unresolved_terminal_treatment_episode_count": no_cleanup,
        "terminal_treatment_coverage_structural_claim_complete": structural_unresolved == 0,
        "terminal_treatment_coverage_complete": False,
        "exact_status_economics_ready": False,
        "feature_performance_testing_authorized": False,
        "sealed_holdout_authorized": False,
        "shadow_s1_authorized": False,
        "fresh_confirmation_s2_authorized": False,
        "live_trading_authorized": False,
        "security_identifiers_emitted": False,
    }
