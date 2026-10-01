import unittest

from research_v1_successor_core import (
    assess_shadow_promotion,
    assess_successor_eligibility,
    build_successor_artifact,
)


def gates():
    return {
        "accepted_challenger": True,
        "independent_oos_passed": True,
        "cost_stress_passed": True,
        "tail_risk_passed": True,
        "recent_stability_passed": True,
        "pit_integrity_passed": True,
        "no_leakage_verified": True,
        "frozen_protocol_match": True,
        "sealed_holdout_used": False,
        "criteria_changed_after_results": False,
    }


def full_confirmation():
    return {
        "shadow_s1_passed": True,
        "fresh_confirmation_s2_passed": True,
        "sealed_holdout_contract_passed": True,
        "all_external_blockers_closed": True,
        "execution_blocker_closed": True,
    }


class SuccessorCoreTest(unittest.TestCase):
    def test_good_research_builds_shadow_candidate_not_production(self):
        trial = {"classification": "ACCEPTED_CHALLENGER", "trial_id": "T1"}
        result = build_successor_artifact(
            trial=trial,
            gates=gates(),
            current_core_version="v1",
            successor_version="v2",
            policy_payload={"x": 1},
        )
        self.assertTrue(result["successor_build_eligible"])
        self.assertEqual(result["artifact"]["state"], "SHADOW_CANDIDATE")
        self.assertFalse(result["artifact"]["production_active"])
        self.assertFalse(result["artifact"]["promotion_authority_granted"])
        self.assertFalse(result["artifact"]["automatic_code_update_allowed"])
        self.assertFalse(result["live_order_authorized"])

    def test_posthoc_change_blocks_successor(self):
        gate_state = gates()
        gate_state["criteria_changed_after_results"] = True
        result = assess_successor_eligibility(
            trial={"classification": "ACCEPTED_CHALLENGER"},
            gates=gate_state,
            current_core_version="v1",
        )
        self.assertFalse(result["successor_build_eligible"])

    def test_missing_gate_blocks(self):
        gate_state = gates()
        gate_state["cost_stress_passed"] = False
        result = assess_successor_eligibility(
            trial={"classification": "ACCEPTED_CHALLENGER"},
            gates=gate_state,
            current_core_version="v1",
        )
        self.assertFalse(result["successor_build_eligible"])

    def test_caller_true_booleans_are_structural_only_not_promotion_authority(self):
        result = assess_shadow_promotion(
            artifact={"state": "SHADOW_CANDIDATE"},
            confirmation=full_confirmation(),
        )
        self.assertTrue(result["promotion_conditions_structurally_satisfied"])
        self.assertEqual(
            result["classification"],
            "PROMOTION_CONDITIONS_SATISFIED_AUTHORITY_BLOCKED",
        )
        self.assertIn("INDEPENDENT_GATE_ADMISSION_NOT_IMPLEMENTED", result["blockers"])
        self.assertFalse(result["caller_gate_booleans_are_authority"])
        self.assertFalse(result["independent_gate_admission_verified"])
        self.assertFalse(result["promotion_authority_verified"])
        self.assertFalse(result["promotion_eligible"])
        self.assertFalse(result["promotion_authority_granted"])
        self.assertFalse(result["automatic_code_update_eligible"])
        self.assertFalse(result["automatic_code_update_allowed"])
        self.assertFalse(result["automatic_live_order_activation_allowed"])
        self.assertFalse(result["live_order_authorized"])

    def test_spoofed_independent_gate_boolean_cannot_grant_authority(self):
        confirmation = full_confirmation()
        confirmation["independent_gate_bundle_verified"] = True
        confirmation["promotion_authority_verified"] = True
        confirmation["promotion_authority_granted"] = True
        confirmation["automatic_code_update_allowed"] = True
        result = assess_shadow_promotion(
            artifact={"state": "SHADOW_CANDIDATE"},
            confirmation=confirmation,
        )
        self.assertTrue(result["promotion_conditions_structurally_satisfied"])
        self.assertFalse(result["independent_gate_admission_verified"])
        self.assertFalse(result["promotion_authority_verified"])
        self.assertFalse(result["promotion_eligible"])
        self.assertFalse(result["automatic_code_update_eligible"])
        self.assertFalse(result["automatic_code_update_allowed"])
        self.assertFalse(result["live_order_authorized"])

    def test_open_external_blocker_prevents_even_structural_conditions(self):
        confirmation = full_confirmation()
        confirmation["all_external_blockers_closed"] = False
        result = assess_shadow_promotion(
            artifact={"state": "SHADOW_CANDIDATE"},
            confirmation=confirmation,
        )
        self.assertFalse(result["promotion_conditions_structurally_satisfied"])
        self.assertFalse(result["promotion_eligible"])
        self.assertIn("EXTERNAL_BLOCKERS_OPEN", result["blockers"])
        self.assertIn("INDEPENDENT_GATE_ADMISSION_NOT_IMPLEMENTED", result["blockers"])


if __name__ == "__main__":
    unittest.main()
