import unittest
from account_settlement_binding import *
from early_live_admission_gate import EarlyLiveAdmissionEvidence
class T(unittest.TestCase):
 def base(self): return EarlyLiveAdmissionEvidence(True,True,True,0,0,True,True,True,True,True,True)
 def test_default_blocks(self):
  o=bind_settlement_to_early_live(self.base(),SettlementAdmission()); self.assertFalse(o["ready_for_final_user_authorization"])
 def test_admitted_only_reaches_boundary(self):
  o=bind_settlement_to_early_live(self.base(),SettlementAdmission(True,True,True,True,0)); self.assertTrue(o["ready_for_final_user_authorization"]); self.assertFalse(o["real_orders_authorized"])
 def test_unresolved_blocks(self): self.assertFalse(bind_settlement_to_early_live(self.base(),SettlementAdmission(True,True,True,True,1))["account_settlement_admitted"])
 def test_coerced_fails(self):
  with self.assertRaises(SettlementBindingError): bind_settlement_to_early_live(self.base(),SettlementAdmission(1,True,True,True,0))
if __name__=="__main__": unittest.main()
