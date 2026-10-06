import pathlib
import unittest

SCRIPT = pathlib.Path("kiwoom_real_readonly_smoke.ps1").read_text(encoding="utf-8")

class RealPowerShellSmokeTests(unittest.TestCase):
    def test_fixed_real_host_only(self):
        self.assertIn("https://api.kiwoom.com/oauth2/token", SCRIPT)
        self.assertIn("https://api.kiwoom.com/api/dostk/acnt", SCRIPT)
        self.assertNotIn("https://mockapi.kiwoom.com", SCRIPT)

    def test_only_reviewed_readonly_api_is_called(self):
        self.assertIn('"api-id" = "ka00001"', SCRIPT)
        for api in ("kt10000","kt10001","kt10002","kt10003"):
            self.assertNotIn(api, SCRIPT)

    def test_real_mode_and_ordering_disabled_are_required(self):
        self.assertIn('$env:KIWOOM_ENV -ne "REAL"', SCRIPT)
        self.assertIn('$env:KIWOOM_BASE_URL -ne "https://api.kiwoom.com"', SCRIPT)
        self.assertIn("KIWOOM_ORDERING_ENABLED", SCRIPT)
        self.assertIn('REAL_ORDERS_AUTHORIZED=$false', SCRIPT)
        self.assertIn('FUNDS_MOVEMENT_AUTHORIZED=$false', SCRIPT)
        self.assertIn('PERMISSION_CHANGE_AUTHORIZED=$false', SCRIPT)

    def test_private_values_and_payloads_are_not_printed(self):
        for expr in (
            "Write-Host $env:KIWOOM_APP_KEY",
            "Write-Host $env:KIWOOM_APP_SECRET",
            "Write-Output $env:KIWOOM_APP_KEY",
            "Write-Output $env:KIWOOM_APP_SECRET",
            "ConvertTo-Json $account",
            "ConvertTo-Json $token",
            "$_.Exception.Message",
        ):
            self.assertNotIn(expr, SCRIPT)

if __name__ == "__main__":
    unittest.main()
