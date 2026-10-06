import pathlib
import unittest

SCRIPT = pathlib.Path("kiwoom_demo_readonly_smoke.ps1").read_text(encoding="utf-8")

class DemoPowerShellSmokeTests(unittest.TestCase):
    def test_fixed_demo_host_only(self):
        self.assertIn("https://mockapi.kiwoom.com/oauth2/token", SCRIPT)
        self.assertIn("https://mockapi.kiwoom.com/api/dostk/acnt", SCRIPT)
        self.assertNotIn("https://api.kiwoom.com", SCRIPT)

    def test_only_reviewed_readonly_api_is_called(self):
        self.assertIn('"api-id" = "ka00001"', SCRIPT)
        for api in ("kt10000","kt10001","kt10002","kt10003"):
            self.assertNotIn(api, SCRIPT)

    def test_ordering_must_be_disabled(self):
        self.assertIn("KIWOOM_ORDERING_ENABLED", SCRIPT)
        self.assertIn('ORDERING="DISABLED"', SCRIPT)
        self.assertIn("REAL_ORDERS_AUTHORIZED=$false", SCRIPT)
        self.assertIn("FUNDS_MOVEMENT_AUTHORIZED=$false", SCRIPT)
        self.assertIn("PERMISSION_CHANGE_AUTHORIZED=$false", SCRIPT)

    def test_private_values_are_never_directly_written(self):
        for expr in (
            "Write-Host $env:KIWOOM_APP_KEY",
            "Write-Host $env:KIWOOM_APP_SECRET",
            "Write-Output $env:KIWOOM_APP_KEY",
            "Write-Output $env:KIWOOM_APP_SECRET",
            "ConvertTo-Json $account",
            "ConvertTo-Json $token",
        ):
            self.assertNotIn(expr, SCRIPT)

if __name__ == "__main__":
    unittest.main()
