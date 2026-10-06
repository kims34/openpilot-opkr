import unittest
from early_live_admission_gate import EarlyLiveAdmissionEvidence, assess_early_live_readiness

class EarlyLiveAdmissionGateTests(unittest.TestCase):
    def test_default_fails_closed(self):
        out = assess_early_live_readiness(EarlyLiveAdmissionEvidence())
        self.assertFalse(out["ready_for_final_user_authorization"])
        self.assertFalse(out["real_orders_authorized"])

    def test_all_preconditions_only_reach_final_authorization_boundary(self):
        e = EarlyLiveAdmissionEvidence(True, True, True, 0, 0, True, True, True, True, True, True)
        out = assess_early_live_readiness(e)
        self.assertTrue(out["ready_for_final_user_authorization"])
        self.assertFalse(out["early_live_authorized"])
        self.assertFalse(out["real_orders_authorized"])

    def test_unresolved_or_breach_blocks(self):
        base = dict(
            successor_alpha_admitted=True,
            source_pit_status_economics_pass=True,
            exact_policy_shadow_complete=True,
            broker_native_provenance_capture_tested=True,
            durable_order_journal_tested=True,
            account_settlement_tested=True,
            pretrade_risk_tested=True,
            cancel_reconnect_kill_tested=True,
            numeric_capital_limits_frozen=True,
        )
        for key in ("unresolved_reconciliation_count", "risk_breach_count"):
            out = assess_early_live_readiness(EarlyLiveAdmissionEvidence(**base, **{key: 1}))
            self.assertFalse(out["ready_for_final_user_authorization"])

    def test_non_boolean_gate_values_fail_closed(self):
        for value in (1, 0, "true", None):
            with self.assertRaises(ValueError):
                assess_early_live_readiness(
                    EarlyLiveAdmissionEvidence(successor_alpha_admitted=value, source_pit_status_economics_pass=True, exact_policy_shadow_complete=True, broker_native_provenance_capture_tested=True, durable_order_journal_tested=True, account_settlement_tested=True, pretrade_risk_tested=True, cancel_reconnect_kill_tested=True, numeric_capital_limits_frozen=True)
                )

    def test_invalid_counts_fail_closed(self):
        for value in (True, -1, 1.5, "0"):
            with self.assertRaises(ValueError):
                assess_early_live_readiness(
                    EarlyLiveAdmissionEvidence(unresolved_reconciliation_count=value)
                )

if __name__ == "__main__":
    unittest.main()
