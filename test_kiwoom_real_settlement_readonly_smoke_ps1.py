import pathlib
import unittest

S = pathlib.Path("kiwoom_real_settlement_readonly_smoke.ps1").read_text(encoding="utf-8")

class RealSettlementPowerShellSmokeTests(unittest.TestCase):
    def test_fixed_real_host_and_exact_readonly_calls(self):
        self.assertEqual(S.count("https://api.kiwoom.com/oauth2/token"), 1)
        self.assertEqual(S.count("https://api.kiwoom.com/api/dostk/acnt"), 2)
        self.assertIn('"api-id"="ka00001"', S)
        self.assertIn('$headers["api-id"] = "kt00001"', S)
        self.assertIn('qry_tp="2"', S)
        self.assertNotIn("https://mockapi.kiwoom.com", S)
        for api in ("kt10000","kt10001","kt10002","kt10003","kt10006","kt10007","kt10008","kt10009"):
            self.assertNotIn(api, S)

    def test_secrets_accounts_and_balances_are_not_printed(self):
        for forbidden in (
            "Write-Host $env:KIWOOM_APP_KEY", "Write-Host $env:KIWOOM_APP_SECRET",
            "Write-Output $env:KIWOOM_APP_KEY", "Write-Output $env:KIWOOM_APP_SECRET",
            "ConvertTo-Json $account", "ConvertTo-Json $settlement", "ConvertTo-Json $token",
            "deposit_cash_krw", "orderable_amount_krw",
        ):
            self.assertNotIn(forbidden, S)

    def test_fail_closed_authority_and_date_origin(self):
        self.assertIn('TRADING_DATE_ORIGIN_ATTESTED=$false', S)
        self.assertIn('REAL_ORDERS_AUTHORIZED=$false', S)
        self.assertIn('FUNDS_MOVEMENT_AUTHORIZED=$false', S)
        self.assertIn('PERMISSION_CHANGE_AUTHORIZED=$false', S)
        self.assertIn('GENUINE_LIVE_PROVENANCE_VERIFIED=$false', S)
        self.assertIn('$env:KIWOOM_ORDERING_ENABLED -notin @("0","false","off","no")', S)

    def test_required_settlement_fields_are_checked(self):
        for field in ("entr","pymn_alow_amt","d2_entra","ord_alow_amt"):
            self.assertIn("$settlement."+field, S)
        self.assertIn("Require-Nonnegative-CashText", S)
        self.assertIn("HMACSHA256", S)

if __name__ == "__main__":
    unittest.main()
