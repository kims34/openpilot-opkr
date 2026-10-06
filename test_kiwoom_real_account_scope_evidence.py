import unittest
from kiwoom_real_account_scope_evidence import assess_redacted_account_scope

def valid():
    return {
        "STAGE":"REAL_ACCOUNT_SCOPE_READ_ONLY_SMOKE","RETURN_CODE":0,
        "TOKEN_OK":True,"ACCOUNT_ENDPOINT_OK":True,"SETTLEMENT_ENDPOINT_OK":True,
        "SETTLEMENT_FIELDS_VALID":True,"BROKER_TODAY_ENDPOINT_OK":True,
        "TRADING_DATE_ORIGIN_ATTESTED":True,"TRADING_DATE":"2026-10-07",
        "ORDER_HISTORY_ENDPOINT_OK":True,"ORDER_HISTORY_COMPLETE":True,"ORDER_HISTORY_ROWS":0,
        "OPEN_ORDER_ENDPOINT_OK":True,"OPEN_ORDER_COMPLETE":True,"OPEN_ORDER_ROWS":0,
        "FILLED_ORDER_ENDPOINT_OK":True,"FILLED_ORDER_COMPLETE":True,"FILLED_ORDER_ROWS":0,
        "HOLDINGS_KRX_ENDPOINT_OK":True,"HOLDINGS_KRX_COMPLETE":True,"HOLDING_ROWS_KRX":0,
        "HOLDINGS_NXT_ENDPOINT_OK":True,"HOLDINGS_NXT_COMPLETE":True,"HOLDING_ROWS_NXT":0,
        "ACCOUNT_SCOPE_BASELINE_COMPLETE":True,
        "BROKER_NATIVE_ORDER_SNAPSHOT_CAPTURE_TESTED":True,
        "BROKER_NATIVE_EXECUTION_ID_CAPTURE_TESTED":False,
        "DURABLE_JOURNAL_BOUND":False,"ACCOUNT_SETTLEMENT_ADMITTED":False,
        "GENUINE_LIVE_PROVENANCE_VERIFIED":False,"ORDERING":"DISABLED",
        "REAL_ORDERS_AUTHORIZED":False,"FUNDS_MOVEMENT_AUTHORIZED":False,
        "PERMISSION_CHANGE_AUTHORIZED":False,
    }

class RealAccountScopeEvidenceTests(unittest.TestCase):
    def test_valid_redacted_summary_preserves_non_admission(self):
        out=assess_redacted_account_scope(valid())
        self.assertTrue(out["account_scope_baseline_complete"])
        self.assertFalse(out["durable_journal_bound"])
        self.assertFalse(out["genuine_live_provenance_verified"])
        self.assertFalse(out["real_orders_authorized"])

    def test_missing_completeness_fails_closed(self):
        row=valid(); row["ORDER_HISTORY_COMPLETE"]=False
        with self.assertRaises(ValueError): assess_redacted_account_scope(row)

    def test_authority_overclaim_rejected(self):
        row=valid(); row["REAL_ORDERS_AUTHORIZED"]=True
        with self.assertRaises(ValueError): assess_redacted_account_scope(row)

    def test_negative_count_rejected(self):
        row=valid(); row["FILLED_ORDER_ROWS"]=-1
        with self.assertRaises(ValueError): assess_redacted_account_scope(row)

if __name__=="__main__": unittest.main()
