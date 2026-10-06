import pathlib
import unittest

class KiwoomRealType00ReadOnlyPowerShellTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text=pathlib.Path("kiwoom_real_type00_readonly_smoke.ps1").read_text(encoding="utf-8")

    def test_fixed_real_hosts_and_read_only_account_query(self):
        self.assertIn('https://api.kiwoom.com/oauth2/token',self.text)
        self.assertIn('https://api.kiwoom.com/api/dostk/acnt',self.text)
        self.assertIn('wss://api.kiwoom.com:10000/api/dostk/websocket',self.text)
        self.assertIn('"api-id"="ka00001"',self.text)

    def test_only_login_and_type00_registration_are_sent(self):
        self.assertIn('trnm="LOGIN"',self.text)
        self.assertIn('trnm="REG"',self.text)
        self.assertIn('type=@("00")',self.text)
        for forbidden in ("/api/dostk/ordr","kt10000","kt10001","kt10002","kt10003"):
            self.assertNotIn(forbidden,self.text)

    def test_ordering_must_be_disabled_and_authority_stays_false(self):
        self.assertIn('KIWOOM_ORDERING_ENABLED',self.text)
        self.assertIn('ORDERING="DISABLED"',self.text)
        self.assertIn('REAL_ORDERS_AUTHORIZED=$false',self.text)
        self.assertIn('FUNDS_MOVEMENT_AUTHORIZED=$false',self.text)
        self.assertIn('PERMISSION_CHANGE_AUTHORIZED=$false',self.text)
        self.assertIn('GENUINE_LIVE_PROVENANCE_VERIFIED=$false',self.text)

    def test_private_values_are_not_emitted(self):
        self.assertNotIn('Write-Host',self.text)
        self.assertNotIn('Write-Output $script:Account',self.text)
        self.assertNotIn('Write-Output $script:Token',self.text)
        self.assertIn('TYPE00_EVENT_COUNT',self.text)
        self.assertIn('ACCOUNT_MATCHED_TYPE00_EVENT_COUNT',self.text)

    def test_timeout_catch_is_windows_powershell_parse_safe(self):
        self.assertIn("catch [System.OperationCanceledException]", self.text)
        self.assertNotIn("catch [System.Threading.Tasks.TaskCanceledException]", self.text)

    def test_execution_capture_requires_account_match_and_native_fields(self):
        self.assertIn("values.'9201' -eq $script:Account",self.text)
        for fid in ("'909'","'908'","'914'","'915'"):
            self.assertIn(fid,self.text)
        self.assertIn('BROKER_NATIVE_EXECUTION_ID_CAPTURE_TESTED=[bool]$executionObserved',self.text)

if __name__=="__main__": unittest.main()
