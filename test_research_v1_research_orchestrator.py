import unittest
from research_v1_research_orchestrator import orchestrate, build_research_queue, ResearchSignal

class ResearchOrchestratorTest(unittest.TestCase):
 def test_drift_creates_idea_only(self):
  x=orchestrate({"calibration_drift":True,"evidence_refs":{"calibration_drift":"audit://cal-1"}},core_version="CORE-v1")
  self.assertEqual(x["status"],"QUEUE_READY"); self.assertEqual(len(x["queue"]),1)
  q=x["queue"][0]; self.assertEqual(q["state"],"IDEA"); self.assertTrue(q["requires_preregistration"]); self.assertFalse(q["production_write_authority"]); self.assertFalse(q["automatic_promotion"])
 def test_no_signal_no_research_churn(self):
  x=orchestrate({},core_version="CORE-v1"); self.assertEqual(x["queue"],[])
 def test_missing_evidence_ref_is_not_queued(self):
  x=orchestrate({"regime_drift":True},core_version="CORE-v1"); self.assertEqual(x["queue"],[])
 def test_holdout_input_fails_closed(self):
  x=orchestrate({"sealed_holdout_accessed":True,"regime_drift":True,"evidence_refs":{"regime_drift":"x"}},core_version="CORE-v1")
  self.assertEqual(x["status"],"INVALID_INPUT"); self.assertEqual(x["queue"],[])
 def test_unknown_flags_do_not_create_freeform_research(self):
  x=orchestrate({"magic_alpha":True,"evidence_refs":{"magic_alpha":"x"}},core_version="CORE-v1"); self.assertEqual(x["queue"],[])
 def test_malformed_boolean_flags_do_not_create_research_churn(self):
  for flag in ("calibration_drift","execution_cost_drift","feature_freshness_drift","regime_drift","data_quality_drift","sealed_holdout_accessed"):
   for value in ("false","true",1,None):
    with self.subTest(flag=flag,value=value):
     x=orchestrate({flag:value,"evidence_refs":{flag:"audit://synthetic"}},core_version="CORE-v1")
     self.assertEqual(x["status"],"INVALID_INPUT"); self.assertEqual(x["queue"],[])
     self.assertFalse(x["core_mutation_allowed"]); self.assertFalse(x["live_order_authorized"])
 def test_missing_or_nonstring_evidence_is_never_stringified_into_proof(self):
  for ref in (None,0,False,[],{},""," "):
   with self.subTest(ref=ref):
    x=orchestrate({"regime_drift":True,"evidence_refs":{"regime_drift":ref}},core_version="CORE-v1")
    self.assertEqual(x["queue"],[])
 def test_malformed_reference_map_fails_closed(self):
  for refs in (None,"private",[],True):
   with self.subTest(refs=refs):
    x=orchestrate({"regime_drift":True,"evidence_refs":refs},core_version="CORE-v1")
    self.assertEqual(x["status"],"INVALID_INPUT"); self.assertEqual(x["queue"],[])
 def test_direct_signal_requires_exact_true_and_nonempty_evidence(self):
  for signal in (ResearchSignal("REGIME_DRIFT","false","audit://synthetic"),ResearchSignal("REGIME_DRIFT",True,None),ResearchSignal("REGIME_DRIFT",True," ")):
   with self.subTest(signal=signal):
    self.assertEqual(build_research_queue([signal],core_version="CORE-v1"),[])
if __name__=="__main__": unittest.main()
