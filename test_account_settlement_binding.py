import unittest
from account_settlement_binding import *
from early_live_admission_gate import EarlyLiveAdmissionEvidence
class T(unittest.TestCase):
 def base(self): return EarlyLiveAdmissionEvidence(True,True,True,0,0,True,True,True,True,True,True)
 def test_default_blocks(self):
  o=bind_settlement_to_early_live(self.base(),SettlementAdmission()); self.assertFalse(o["ready_for_final_user_authorization"])
 def test_admitted_settlement_only_reaches_structural_boundary(self):
  o=bind_settlement_to_early_live(self.base(),SettlementAdmission(True,True,True,True,0))
  self.assertTrue(o["account_settlement_structural_preconditions_satisfied"])
  self.assertFalse(o["independent_settlement_admission_verified"])
  self.assertFalse(o["account_settlement_admitted"])
  self.assertTrue(o["preconditions_structurally_satisfied"])
  self.assertFalse(o["independent_gate_admission_verified"])
  self.assertFalse(o["ready_for_final_user_authorization"])
  self.assertIn("INDEPENDENT_GATE_ADMISSION_NOT_IMPLEMENTED",o["blockers"])
  self.assertFalse(o["real_orders_authorized"])
 def test_unresolved_blocks(self):
  o=bind_settlement_to_early_live(self.base(),SettlementAdmission(True,True,True,True,1))
  self.assertFalse(o["account_settlement_structural_preconditions_satisfied"])
  self.assertFalse(o["independent_settlement_admission_verified"])
  self.assertFalse(o["account_settlement_admitted"])
 def test_coerced_fails(self):
  with self.assertRaises(SettlementBindingError): bind_settlement_to_early_live(self.base(),SettlementAdmission(1,True,True,True,0))
if __name__=="__main__": unittest.main()
