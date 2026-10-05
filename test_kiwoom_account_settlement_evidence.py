import unittest
from kiwoom_account_settlement_evidence import *

A="sha256:"+"a"*64
def dep(**kw):
 d={"api_id":"kt00001","official_schema_commit":OFFICIAL_SCHEMA_COMMIT,"account_fingerprint":A,"trading_date":"2026-10-05","return_code":0,
 "summary":{"entr":"100000","ord_alow_amt":"90000","pymn_alow_amt":"80000","d1_entra":"110000","d1_sel_exct_amt":"10000","d2_entra":"120000","d2_sel_exct_amt":"20000"}}
 d.update(kw); return d
def ev(**kw):
 d={"api_id":"kt00018","official_schema_commit":OFFICIAL_SCHEMA_COMMIT,"account_fingerprint":A,"trading_date":"2026-10-05","return_code":0,
 "summary":{"tot_pur_amt":"50000","tot_evlt_amt":"52000","prsm_dpst_aset_amt":"152000"},
 "positions":[{"stk_cd":"005930","rmnd_qty":"1","trde_able_qty":"1","pur_amt":"50000","pur_cmsn":"10","evlt_amt":"52000","sell_cmsn":"10","tax":"0","sum_cmsn":"20"}]}
 d.update(kw); return d
class T(unittest.TestCase):
 def test_exact_snapshot_is_non_authoritative(self):
  x=normalize_account_snapshot(account_fingerprint=A,trading_date="2026-10-05",deposit=dep(),evaluation=ev())
  self.assertEqual(x["cash"]["orderable"],"90000"); self.assertFalse(x["sale_proceeds_reusable"]); self.assertFalse(settlement_credit_allowed(x))
 def test_account_mismatch_fails(self):
  with self.assertRaises(SettlementEvidenceError): normalize_account_snapshot(account_fingerprint=A,trading_date="2026-10-05",deposit=dep(),evaluation=ev(account_fingerprint="sha256:"+"b"*64))
 def test_missing_cost_fails(self):
  e=ev(); del e["positions"][0]["tax"]
  with self.assertRaises(SettlementEvidenceError): normalize_account_snapshot(account_fingerprint=A,trading_date="2026-10-05",deposit=dep(),evaluation=e)
 def test_negative_fee_fails(self):
  e=ev(); e["positions"][0]["pur_cmsn"]="-1"
  with self.assertRaises(SettlementEvidenceError): normalize_account_snapshot(account_fingerprint=A,trading_date="2026-10-05",deposit=dep(),evaluation=e)
 def test_tradable_exceeds_position_fails(self):
  e=ev(); e["positions"][0]["trde_able_qty"]="2"
  with self.assertRaises(SettlementEvidenceError): normalize_account_snapshot(account_fingerprint=A,trading_date="2026-10-05",deposit=dep(),evaluation=e)
 def test_schema_drift_fails(self):
  with self.assertRaises(SettlementEvidenceError): normalize_account_snapshot(account_fingerprint=A,trading_date="2026-10-05",deposit=dep(official_schema_commit="x"),evaluation=ev())
 def test_duplicate_symbol_fails(self):
  e=ev(); e["positions"].append(dict(e["positions"][0]))
  with self.assertRaises(SettlementEvidenceError): normalize_account_snapshot(account_fingerprint=A,trading_date="2026-10-05",deposit=dep(),evaluation=e)
 def test_d2_sell_not_promoted_to_cash(self):
  x=normalize_account_snapshot(account_fingerprint=A,trading_date="2026-10-05",deposit=dep(),evaluation=ev())
  self.assertEqual(x["cash"]["d2_sell_settlement"],"20000"); self.assertNotEqual(x["cash"]["orderable"],x["cash"]["d2_sell_settlement"])
if __name__=="__main__": unittest.main()
