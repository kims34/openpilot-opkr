import base64
import shutil
import subprocess
import pathlib
import unittest

S = pathlib.Path("kiwoom_real_account_scope_readonly_smoke.ps1").read_text(encoding="utf-8")

class RealAccountScopeSmokeTests(unittest.TestCase):
    def test_actual_paging_helpers_reject_unknown_rows_and_contradictory_cursor(self):
        runtimes=list(dict.fromkeys(runtime for runtime in (shutil.which('pwsh'),shutil.which('powershell')) if runtime))
        if not runtimes:
            self.skipTest('Offline PowerShell paging behavior covered by CI matrix')
        path=base64.b64encode(str(pathlib.Path('kiwoom_real_account_scope_readonly_smoke.ps1').resolve()).encode()).decode()
        harness=r'''$ErrorActionPreference='Stop'; $ProgressPreference='SilentlyContinue'
$path=[Text.Encoding]::UTF8.GetString([Convert]::FromBase64String('PATH_BASE64'))
$tokens=$null; $errors=$null
$ast=[Management.Automation.Language.Parser]::ParseFile($path,[ref]$tokens,[ref]$errors)
foreach ($name in @('Convert-ReadOnlyJson','Get-ReadOnlyReturnCode','Invoke-ReadOnlyPage','Get-PagedCount')) {
 $fn=$ast.Find({param($node) $node -is [Management.Automation.Language.FunctionDefinitionAst] -and $node.Name -eq $name},$true)
 if ($null -eq $fn) { throw 'HELPER_MISSING' }
 . ([ScriptBlock]::Create($fn.Extent.Text))
}
# Stub all HTTP. No credentials/configuration or full broker script are executed.
function Invoke-WebRequest {
 param([switch]$UseBasicParsing,[string]$Uri,[string]$Method,[object]$Headers,[string]$ContentType,[object]$Body,[int]$TimeoutSec)
 if ($TimeoutSec -ne 15) {throw 'HTTP_TIMEOUT_NOT_BOUND'}
 $script:Calls++
 if ($script:CycleThenEnd) {
  $script:ReplyHeaders=if ($script:Calls -le 2) {@{'cont-yn'='Y';'next-key'='fixture-cycle'}} else {@{'cont-yn'='N';'next-key'=''}}
 }
 if ($script:UniqueCursors) {$script:ReplyHeaders=@{'cont-yn'='Y';'next-key'=('fixture-'+$script:Calls)}}
 return [pscustomobject]@{Content=$script:Reply;Headers=$script:ReplyHeaders}
}
$script:Token='fixture'; $script:Calls=0; $script:ReplyHeaders=@{'cont-yn'='N';'next-key'=''}
foreach ($reply in @('{"return_code":0}','{"return_code":0,"cntr":null}','{"return_code":0,"cntr":{}}','{"return_code":0,"cntr":[null]}','{"return_code":0,"cntr":["row"]}')) {
 $script:Reply=$reply; $rejected=$false
 try {$null=Get-PagedCount -ApiId 'ka10076' -Body @{} -ArrayProperty 'cntr'}
 catch {if ($_.Exception.Message -ne 'PAGE_SCHEMA_BLOCKED') {throw 'PRIVATE_SCHEMA_ERROR_REQUIRED'}; $rejected=$true}
 if (-not $rejected) {throw 'UNKNOWN_ROWS_BECAME_COMPLETE'}
}
$script:Reply='{"return_code":0,"cntr":[]}'
$result=Get-PagedCount -ApiId 'ka10076' -Body @{} -ArrayProperty 'cntr'
if (-not $result.Complete -or $result.Count -ne 0) {throw 'EXPLICIT_EMPTY_REJECTED'}
$script:Reply='{"return_code":0,"cntr":[{},{}]}'
$result=Get-PagedCount -ApiId 'ka10076' -Body @{} -ArrayProperty 'cntr'
if (-not $result.Complete -or $result.Count -ne 2) {throw 'VALID_ROWS_REJECTED'}
foreach ($headers in @(@{'cont-yn'='N';'next-key'='unexpected'},@{'cont-yn'='Y';'next-key'=''})) {
 $script:ReplyHeaders=$headers; $rejected=$false
 try {$null=Invoke-ReadOnlyPage -ApiId 'ka10076' -Body @{}}
 catch {if ($_.Exception.Message -ne 'CONTINUATION_BLOCKED') {throw 'PRIVATE_CURSOR_ERROR_REQUIRED'}; $rejected=$true}
 if (-not $rejected) {throw 'CURSOR_CONTRADICTION_ACCEPTED'}
}
$script:CycleThenEnd=$true; $script:Calls=0; $rejected=$false
try {$null=Get-PagedCount -ApiId 'ka10076' -Body @{} -ArrayProperty 'cntr'}
catch {if ($_.Exception.Message -ne 'CONTINUATION_BLOCKED') {throw 'PRIVATE_CYCLE_ERROR_REQUIRED'}; $rejected=$true}
if (-not $rejected) {throw 'REPEATED_CURSOR_BECAME_COMPLETE'}
if ($script:Calls -ne 2) {throw 'CYCLE_WAS_NOT_STOPPED_EARLY'}
$script:CycleThenEnd=$false; $script:UniqueCursors=$true
$script:ReplyHeaders=@{'cont-yn'='Y';'next-key'='fixture-cursor'}
$before=$script:Calls
$result=Get-PagedCount -ApiId 'ka10076' -Body @{} -ArrayProperty 'cntr'
if ($result.Complete -or ($script:Calls-$before) -ne 10) {throw 'PAGING_CAP_BYPASSED'}
'''.replace('PATH_BASE64',path)
        encoded=base64.b64encode(harness.encode('utf-16le')).decode()
        for runtime in runtimes:
            with self.subTest(runtime=pathlib.Path(runtime).name):
                result=subprocess.run([runtime,'-NoProfile','-NonInteractive','-EncodedCommand',encoded],capture_output=True,text=True,timeout=30)
                self.assertEqual(result.returncode,0,result.stderr)

    def test_every_readonly_http_request_has_explicit_timeout(self):
        for filename in ('kiwoom_real_type00_readonly_smoke.ps1', 'kiwoom_real_settlement_readonly_smoke.ps1', 'kiwoom_real_settlement_date_readonly_smoke.ps1', 'kiwoom_real_account_scope_readonly_smoke.ps1'):
            text=pathlib.Path(filename).read_text(encoding='utf-8')
            calls=[line.strip() for line in text.splitlines() if '= Invoke-WebRequest ' in line]
            self.assertTrue(calls)
            for call in calls:
                self.assertIn('Invoke-WebRequest -TimeoutSec 15 ', call)

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
