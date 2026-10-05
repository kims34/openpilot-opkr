import unittest
from research_v1_continuous_research import validate_preregistration, protocol_fingerprint, evaluate_trial, queue_item

def p():
 return {"schema_version":"1","trial_id":"T-001","core_version":"CORE-v1","hypothesis":"new PIT-safe family improves executable NetEV","dataset_window":"development-only","pit_contract":"existing-frozen-PIT","target_horizon":"H5","primary_metrics":["NetEV","PF","MDD","ES95","ES99"],"acceptance_criteria":{"use":"preregistered-only"},"cost_assumptions":{"use":"existing-frozen-cost-contract"},"evaluation_protocol":"purged-walk-forward","preregistered_at":"2026-10-02T03:00:00+09:00","data_roles":["development","calibration"],"automatic_production_promotion":False,"live_order_authorized":False}

class ContinuousResearchGovernanceTest(unittest.TestCase):
 def test_valid_protocol_can_only_become_challenger(self):
  x=p(); fp=protocol_fingerprint(x); out=evaluate_trial(x,fp,{"all_preregistered_acceptance_criteria_passed":True})
  self.assertEqual(out["classification"],"ACCEPTED_CHALLENGER"); self.assertFalse(out["production_promotion_allowed"]); self.assertFalse(out["live_order_authorized"])
 def test_protocol_mutation_invalidates(self):
  x=p(); fp=protocol_fingerprint(x); x["target_horizon"]="H10"; out=evaluate_trial(x,fp,{"all_preregistered_acceptance_criteria_passed":True})
  self.assertEqual(out["classification"],"INVALIDATED"); self.assertIn("PROTOCOL_CHANGED_AFTER_PREREGISTRATION",out["blockers"])
 def test_holdout_is_forbidden(self):
  x=p(); x["data_roles"].append("sealed_holdout"); self.assertFalse(validate_preregistration(x)["valid"])
 def test_posthoc_change_invalidates(self):
  x=p(); out=evaluate_trial(x,protocol_fingerprint(x),{"all_preregistered_acceptance_criteria_passed":True,"criteria_changed_after_results":True})
  self.assertEqual(out["classification"],"INVALIDATED")
 def test_queue_has_no_production_authority(self):
  self.assertFalse(queue_item("drift","test new feature family","CORE-v1")["production_write_authority"])
 def test_truthy_nonboolean_acceptance_cannot_admit_challenger(self):
  for value in ("false","true",1,0,None,[],{},[True]):
   with self.subTest(value=value):
    x=p(); out=evaluate_trial(x,protocol_fingerprint(x),{"all_preregistered_acceptance_criteria_passed":value})
    self.assertEqual(out["classification"],"INVALIDATED")
    self.assertIn("INVALID_RESULT_BOOLEAN:all_preregistered_acceptance_criteria_passed",out["blockers"])
    self.assertFalse(out["production_promotion_allowed"])
 def test_boolean_false_and_missing_acceptance_remain_rejected(self):
  for results in ({},{"all_preregistered_acceptance_criteria_passed":False}):
   x=p(); self.assertEqual(evaluate_trial(x,protocol_fingerprint(x),results)["classification"],"REJECTED")
 def test_invalid_declared_role_shape_never_bypasses_holdout_boundary(self):
  for roles in ("sealed_holdout",{"sealed_holdout":True},[None],[1],[""],[],None):
   with self.subTest(roles=roles):
    x=p(); x["data_roles"]=roles
    out=evaluate_trial(x,protocol_fingerprint(x),{"all_preregistered_acceptance_criteria_passed":True})
    self.assertEqual(out["classification"],"INVALIDATED")
    self.assertIn("INVALID_DATA_ROLES",out["blockers"])
 def test_normalized_forbidden_roles_stay_blocked(self):
  for role in (" SEALED_HOLDOUT ","holdout","Final_Holdout"):
   with self.subTest(role=role):
    x=p(); x["data_roles"]=["development",role]
    self.assertIn("SEALED_HOLDOUT_FORBIDDEN",validate_preregistration(x)["blockers"])
 def test_nonboolean_risk_or_authority_flags_invalidate(self):
  for flag in ("sealed_holdout_accessed","criteria_changed_after_results"):
   for value in ("false",0,None):
    with self.subTest(flag=flag,value=value):
     x=p(); out=evaluate_trial(x,protocol_fingerprint(x),{"all_preregistered_acceptance_criteria_passed":True,flag:value})
     self.assertEqual(out["classification"],"INVALIDATED")
     self.assertIn("INVALID_RESULT_BOOLEAN:"+flag,out["blockers"])
  for flag in ("automatic_production_promotion","live_order_authorized"):
   x=p(); x[flag]="false"
   self.assertIn("INVALID_PROTOCOL_BOOLEAN:"+flag,validate_preregistration(x)["blockers"])

if __name__=="__main__": unittest.main()
