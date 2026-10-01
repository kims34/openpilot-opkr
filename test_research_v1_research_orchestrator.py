import unittest
from research_v1_research_orchestrator import orchestrate

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
if __name__=="__main__": unittest.main()
