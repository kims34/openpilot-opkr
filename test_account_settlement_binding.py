import tempfile,unittest
from order_intent_journal import OrderIntentJournal
from shadow_capital_allocator import ShadowCapitalAllocator
from account_settlement_binding import AccountSettlementBinder
from kiwoom_account_settlement_evidence import SettlementEvidenceError
class T(unittest.TestCase):
 def setUp(self):
  self.t=tempfile.NamedTemporaryFile(); self.j=OrderIntentJournal(self.t.name); self.a=ShadowCapitalAllocator(self.j); self.b=AccountSettlementBinder(self.j,self.a)
 def snap(self,positions=None):
  return {"settlement_admitted":False,"sale_proceeds_reusable":False,"snapshot_sha256":"a"*64,"positions":positions or []}
 def test_empty_consistent_binds_without_credit(self):
  r=self.b.bind(self.snap(),expected_capital_revision=0,expected_epoch=self.j.shadow_control()["epoch"])
  self.assertTrue(r["position_match"]); self.assertFalse(r["capital_released"]); self.assertFalse(r["sale_proceeds_credited"])
 def test_authority_flag_rejected(self):
  s=self.snap(); s["settlement_admitted"]=True
  with self.assertRaises(SettlementEvidenceError): self.b.bind(s,expected_capital_revision=0,expected_epoch=self.j.shadow_control()["epoch"])
 def test_sale_credit_flag_rejected(self):
  s=self.snap(); s["sale_proceeds_reusable"]=True
  with self.assertRaises(SettlementEvidenceError): self.b.bind(s,expected_capital_revision=0,expected_epoch=self.j.shadow_control()["epoch"])
if __name__=="__main__": unittest.main()
