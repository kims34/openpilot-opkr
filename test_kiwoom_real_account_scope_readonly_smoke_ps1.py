import pathlib
import unittest

S = pathlib.Path("kiwoom_real_account_scope_readonly_smoke.ps1").read_text(encoding="utf-8")

class RealAccountScopeSmokeTests(unittest.TestCase):
    def test_fixed_real_host_and_reviewed_query_ids_only(self):
        self.assertEqual(S.count("https://api.kiwoom.com/oauth2/token"), 1)
        self.assertIn("https://api.kiwoom.com/api/dostk/acnt", S)
        for api in ("ka00001","kt00001","kt00017","kt00007","ka10076","kt00018"):
            self.assertIn(api, S)
        for api in ("kt10000","kt10001","kt10002","kt10003","kt10006","kt10007","kt10008","kt10009"):
            self.assertNotIn(api, S)

    def test_whole_scope_requests_are_explicit(self):
        for marker in (
            'qry_tp="1"; stk_bond_tp="0"; sell_tp="0"; dmst_stex_tp="%"',
            'qry_tp="3"; stk_bond_tp="0"; sell_tp="0"; dmst_stex_tp="%"',
            'qry_tp="0"; sell_tp="0"; stex_tp="0"; stk_cd=""; ord_no=""',
            'qry_tp="2"; dmst_stex_tp="KRX"',
            'qry_tp="2"; dmst_stex_tp="NXT"',
        ):
            self.assertIn(marker, S)
        self.assertIn("Get-PagedCount", S)
        self.assertIn("$pageNo -le 10", S)

    def test_output_is_counts_and_flags_not_private_rows(self):
        for marker in (
            "ORDER_HISTORY_ROWS", "OPEN_ORDER_ROWS", "FILLED_ORDER_ROWS",
            "HOLDING_ROWS_KRX", "HOLDING_ROWS_NXT", "ACCOUNT_SCOPE_BASELINE_COMPLETE"
        ):
            self.assertIn(marker, S)
        for bad in (
            "ACCOUNT_FINGERPRINT=",
            "ConvertTo-Json $accountPage.Body",
            "ConvertTo-Json $settlementPage.Body",
            "Write-Host $env:KIWOOM_APP_KEY",
            "Write-Host $env:KIWOOM_APP_SECRET",
        ):
            self.assertNotIn(bad, S)

    def test_execution_identity_and_authority_remain_false(self):
        for marker in (
            "BROKER_NATIVE_EXECUTION_ID_CAPTURE_TESTED=$false",
            "DURABLE_JOURNAL_BOUND=$false",
            "ACCOUNT_SETTLEMENT_ADMITTED=$false",
            'ORDERING="DISABLED"',
            "REAL_ORDERS_AUTHORIZED=$false",
            "FUNDS_MOVEMENT_AUTHORIZED=$false",
            "PERMISSION_CHANGE_AUTHORIZED=$false",
            "GENUINE_LIVE_PROVENANCE_VERIFIED=$false",
        ):
            self.assertIn(marker, S)

if __name__ == "__main__":
    unittest.main()
