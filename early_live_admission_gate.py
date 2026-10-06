"""Fail-closed admission gate for future capital-capped Early Live.

This module never submits orders, changes broker permissions, or grants authority
from local caller booleans. It only evaluates whether independently supplied
canonical gate admissions are all present. Real-account activation still requires
separate explicit user authorization immediately before enabling ordering.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class EarlyLiveAdmissionEvidence:
    successor_alpha_admitted: bool = False
    source_pit_status_economics_pass: bool = False
    exact_policy_shadow_complete: bool = False
    unresolved_reconciliation_count: int = 0
    risk_breach_count: int = 0
    broker_native_provenance_capture_tested: bool = False
    durable_order_journal_tested: bool = False
    account_settlement_tested: bool = False
    pretrade_risk_tested: bool = False
    cancel_reconnect_kill_tested: bool = False
    numeric_capital_limits_frozen: bool = False


def assess_early_live_readiness(evidence: EarlyLiveAdmissionEvidence) -> dict:
    if type(evidence) is not EarlyLiveAdmissionEvidence:
        raise ValueError("canonical EarlyLiveAdmissionEvidence required")
    counts = (evidence.unresolved_reconciliation_count, evidence.risk_breach_count)
    if any(type(v) is not int or v < 0 for v in counts):
        raise ValueError("counts must be nonnegative integers")

    gates = {
        "successor_alpha_admitted": evidence.successor_alpha_admitted,
        "source_pit_status_economics_pass": evidence.source_pit_status_economics_pass,
        "exact_policy_shadow_complete": evidence.exact_policy_shadow_complete,
        "zero_unresolved_reconciliation": evidence.unresolved_reconciliation_count == 0,
        "zero_risk_breaches": evidence.risk_breach_count == 0,
        "broker_native_provenance_capture_tested": evidence.broker_native_provenance_capture_tested,
        "durable_order_journal_tested": evidence.durable_order_journal_tested,
        "account_settlement_tested": evidence.account_settlement_tested,
        "pretrade_risk_tested": evidence.pretrade_risk_tested,
        "cancel_reconnect_kill_tested": evidence.cancel_reconnect_kill_tested,
        "numeric_capital_limits_frozen": evidence.numeric_capital_limits_frozen,
    }
    ready_for_final_user_authorization = all(v is True for v in gates.values())
    return {
        "protocol_id": "INDEXALERT-CAPITAL-CAPPED-EARLY-LIVE-v2",
        "gates": gates,
        "ready_for_final_user_authorization": ready_for_final_user_authorization,
        # This assessor can never itself authorize trading.
        "early_live_authorized": False,
        "real_orders_authorized": False,
        "funds_movement_authorized": False,
        "broker_permission_change_authorized": False,
    }
