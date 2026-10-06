import pathlib
import unittest

S = pathlib.Path("kiwoom_real_settlement_date_readonly_smoke.ps1").read_text(encoding="utf-8")

class RealSettlementDateSmokeTests(unittest.TestCase):
    def test_fixed_real_host_and_only_reviewed_readonly_ids(self):
        self.assertEqual(S.count("https://api.kiwoom.com/oauth2/token"), 1)
        self.assertEqual(S.count("https://api.kiwoom.com/api/dostk/acnt"), 3)
        self.assertIn('"api-id"="ka00001"', S)
        self.assertIn('$headers["api-id"] = "kt00001"', S)
        self.assertIn('$headers["api-id"] = "kt00017"', S)
        for api in ("kt10000","kt10001","kt10002","kt10003","kt10006","kt10007","kt10008","kt10009"):
            self.assertNotIn(api, S)

    def test_no_private_account_or_cash_output(self):
        for bad in (
            "ACCOUNT_FINGERPRINT=", "ConvertTo-Json $account", "ConvertTo-Json $settlement",
            "ConvertTo-Json $today", "Write-Host $env:KIWOOM_APP_KEY",
            "Write-Host $env:KIWOOM_APP_SECRET", "deposit_cash_krw", "orderable_amount_krw"
        ):
            self.assertNotIn(bad, S)

    def test_broker_date_is_header_bound_and_fresh(self):
        self.assertIn('$todayResponse.Headers["Date"]', S)
        self.assertIn("[DateTimeOffset]::TryParse", S)
        self.assertIn("$ageSeconds -gt 300", S)
        self.assertIn('TRADING_DATE_ORIGIN_ATTESTED=$true', S)
        self.assertIn('BROKER_TODAY_ENDPOINT_OK=$true', S)

    def test_authority_stays_disabled(self):
        for marker in (
            'ORDERING="DISABLED"', "REAL_ORDERS_AUTHORIZED=$false",
            "FUNDS_MOVEMENT_AUTHORIZED=$false", "PERMISSION_CHANGE_AUTHORIZED=$false",
            "GENUINE_LIVE_PROVENANCE_VERIFIED=$false"
        ):
            self.assertIn(marker, S)

if __name__ == "__main__":
    unittest.main()
