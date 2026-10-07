import base64
import shutil
import subprocess
import pathlib
import unittest

S = pathlib.Path("kiwoom_real_settlement_readonly_smoke.ps1").read_text(encoding="utf-8")

class RealSettlementPowerShellSmokeTests(unittest.TestCase):
    def test_settlement_responses_use_strict_offline_helpers(self):
        self.assertEqual(S.count('-ControlFrame $false'), 3)
        for name in ('token', 'account', 'settlement'):
            self.assertIn(f'${name} = Convert-ReadOnlyJson -Raw ${name}Wire.Content', S)
        runtimes = list(dict.fromkeys(runtime for runtime in (shutil.which('pwsh'), shutil.which('powershell')) if runtime))
        if not runtimes:
            self.skipTest('PowerShell runtime behavior covered by CI matrix')
        harness = r'''$ErrorActionPreference='Stop'
$path=[Text.Encoding]::UTF8.GetString([Convert]::FromBase64String('PATH_BASE64'))
$tokens=$null; $errors=$null
$ast=[Management.Automation.Language.Parser]::ParseFile($path,[ref]$tokens,[ref]$errors)
if ($errors.Count -ne 0) { throw 'SYNTAX_INVALID' }
foreach ($name in @('Convert-ReadOnlyJson','Get-ReadOnlyReturnCode','Require-Nonnegative-CashText')) {
 $fn=$ast.Find({param($node) $node -is [Management.Automation.Language.FunctionDefinitionAst] -and $node.Name -eq $name},$true)
 if ($null -eq $fn) { throw 'HELPER_MISSING' }
 . ([ScriptBlock]::Create($fn.Extent.Text))
}
$obj=Convert-ReadOnlyJson -Raw '{"return_code":0,"entr":"1,000","pymn_alow_amt":"900","d2_entra":"800","ord_alow_amt":"700"}'
if ((Get-ReadOnlyReturnCode -Message $obj -Raw '{"return_code":0}' -ControlFrame $false) -ne 0) { throw 'VALID_REJECTED' }
if (-not (Require-Nonnegative-CashText $obj.entr)) { throw 'VALID_CASH_REJECTED' }
foreach ($raw in @('{"return_code":false}','{"return_code":"0"}','{"return_code":0.5}','{"return_code":0,"return_code":0}','{"return_code":0,"entr":"10","entr":"1000"}','{"return_code":0,"nested":{"a":1,"a":2}}','{"return_code":0,"entr":NaN}')) {
 $rejected=$false
 try { $obj=Convert-ReadOnlyJson -Raw $raw; $null=Get-ReadOnlyReturnCode -Message $obj -Raw $raw -ControlFrame $false }
 catch { if ($_.Exception.Message -notin @('READ_ONLY_JSON_INVALID','READ_ONLY_PROTOCOL_RESPONSE_INVALID')) { throw 'PRIVATE_ERROR_REQUIRED' }; $rejected=$true }
 if (-not $rejected) { throw 'AMBIGUITY_ACCEPTED' }
}
if (Require-Nonnegative-CashText (-1)) { throw 'INVALID_CASH_ACCEPTED' }
'''
        for filename in ('kiwoom_real_settlement_readonly_smoke.ps1', 'kiwoom_real_settlement_date_readonly_smoke.ps1', 'kiwoom_real_account_scope_readonly_smoke.ps1'):
            path = base64.b64encode(str(pathlib.Path(filename).resolve()).encode()).decode()
            encoded = base64.b64encode(harness.replace('PATH_BASE64', path).encode('utf-16le')).decode()
            for runtime in runtimes:
                with self.subTest(script=filename, runtime=pathlib.Path(runtime).name):
                    result = subprocess.run([runtime, '-NoProfile', '-NonInteractive', '-EncodedCommand', encoded], capture_output=True, text=True, timeout=30)
                    self.assertEqual(result.returncode, 0, result.stderr)

    def test_date_and_scope_success_paths_use_strict_response_guards(self):
        for filename, count in (('kiwoom_real_settlement_date_readonly_smoke.ps1',4), ('kiwoom_real_account_scope_readonly_smoke.ps1',2)):
            text = pathlib.Path(filename).read_text(encoding='utf-8')
            self.assertEqual(text.count('-ControlFrame $false'), count)
            self.assertNotIn('Invoke-RestMethod', text)
            self.assertIn('acctNo -isnot [string]', text)

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

    def test_windows_powershell_51_compatible_crypto_surface(self):
        self.assertIn("[System.Security.Cryptography.SHA256]::Create()", S)
        self.assertIn("[System.BitConverter]::ToString", S)
        self.assertNotIn("::HashData(", S)
        self.assertNotIn("::ToHexString(", S)

if __name__ == "__main__":
    unittest.main()
