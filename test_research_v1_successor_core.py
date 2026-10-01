import unittest
from research_v1_successor_core import assess_successor_eligibility, build_successor_artifact, assess_shadow_promotion

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

class SuccessorCoreTest(unittest.TestCase):
    def test_good_research_builds_shadow_candidate_not_production(self):
        t={"classification":"ACCEPTED_CHALLENGER","trial_id":"T1"}
        o=build_successor_artifact(trial=t,gates=gates(),current_core_version="v1",successor_version="v2",policy_payload={"x":1})
        self.assertTrue(o["successor_build_eligible"])
        self.assertEqual(o["artifact"]["state"],"SHADOW_CANDIDATE")
        self.assertFalse(o["artifact"]["production_active"])
        self.assertFalse(o["live_order_authorized"])

    def test_posthoc_change_blocks_successor(self):
        g=gates(); g["criteria_changed_after_results"]=True
        o=assess_successor_eligibility(trial={"classification":"ACCEPTED_CHALLENGER"},gates=g,current_core_version="v1")
        self.assertFalse(o["successor_build_eligible"])

    def test_missing_gate_blocks(self):
        g=gates(); g["cost_stress_passed"]=False
        o=assess_successor_eligibility(trial={"classification":"ACCEPTED_CHALLENGER"},gates=g,current_core_version="v1")
        self.assertFalse(o["successor_build_eligible"])

    def test_full_confirmation_yields_eligibility_not_mutation_authority(self):
        a={"state":"SHADOW_CANDIDATE"}
        c={"shadow_s1_passed":True,"fresh_confirmation_s2_passed":True,"sealed_holdout_contract_passed":True,"all_external_blockers_closed":True,"execution_blocker_closed":True}
        o=assess_shadow_promotion(artifact=a,confirmation=c)
        self.assertTrue(o["promotion_eligible"])
        self.assertTrue(o["automatic_code_update_eligible"])
        self.assertFalse(o["automatic_code_update_allowed"])
        self.assertFalse(o["promotion_authority_verified"])
        self.assertFalse(o["automatic_live_order_activation_allowed"])
        self.assertFalse(o["live_order_authorized"])

    def test_caller_booleans_never_grant_code_update_authority(self):
        a={"state":"SHADOW_CANDIDATE"}
        c={"shadow_s1_passed":True,"fresh_confirmation_s2_passed":True,"sealed_holdout_contract_passed":True,"all_external_blockers_closed":True,"execution_blocker_closed":True,"automatic_code_update_allowed":True,"promotion_authority_verified":True}
        o=assess_shadow_promotion(artifact=a,confirmation=c)
        self.assertTrue(o["promotion_eligible"])
        self.assertFalse(o["automatic_code_update_allowed"])
        self.assertFalse(o["promotion_authority_verified"])

    def test_open_external_blocker_prevents_promotion(self):
        a={"state":"SHADOW_CANDIDATE"}
        c={"shadow_s1_passed":True,"fresh_confirmation_s2_passed":True,"sealed_holdout_contract_passed":True,"all_external_blockers_closed":False,"execution_blocker_closed":True}
        self.assertFalse(assess_shadow_promotion(artifact=a,confirmation=c)["promotion_eligible"])

if __name__=="__main__":
    unittest.main()
