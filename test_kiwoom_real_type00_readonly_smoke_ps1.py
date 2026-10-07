import base64
import shutil
import subprocess
import pathlib
import unittest

class KiwoomRealType00ReadOnlyPowerShellTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text=pathlib.Path("kiwoom_real_type00_readonly_smoke.ps1").read_text(encoding="utf-8")

    def test_acknowledgements_require_explicit_unambiguous_integer_codes(self):
        self.assertEqual(self.text.count('Get-ReadOnlyReturnCode -Message $obj -Raw $raw'), 2)
        self.assertNotIn('$code = 0', self.text)
        self.assertEqual(self.text.count('$obj = Convert-ReadOnlyJson -Raw $raw'), 2)
        self.assertIn('$tokenResp = Convert-ReadOnlyJson -Raw $tokenWire.Content', self.text)
        self.assertIn('$accountObj = Convert-ReadOnlyJson -Raw $accountResp.Content', self.text)
        self.assertEqual(self.text.count('-ControlFrame $false'), 2)
        self.assertIn('$tokenResp.token -isnot [string]', self.text)
        self.assertIn('$accountObj.acctNo -isnot [string]', self.text)
        self.assertIn('return Convert-StrictWebSocketText -Bytes $stream.ToArray()', self.text)
        self.assertIn('Get-Type00ReadOnlyObservation -Message $obj -Account $script:Account', self.text)
        runtimes = [shutil.which(name) for name in ('pwsh', 'powershell')]
        runtimes = list(dict.fromkeys(runtime for runtime in runtimes if runtime))
        if not runtimes:
            self.skipTest('PowerShell unavailable locally; behavioral matrix runs in CI')
        path = base64.b64encode(str(pathlib.Path('kiwoom_real_type00_readonly_smoke.ps1').resolve()).encode()).decode()
        harness = r'''$ErrorActionPreference = 'Stop'
$path = [Text.Encoding]::UTF8.GetString([Convert]::FromBase64String('PATH_BASE64'))
$tokens=$null; $errors=$null
$ast=[System.Management.Automation.Language.Parser]::ParseFile($path,[ref]$tokens,[ref]$errors)
if ($errors.Count -ne 0) { throw 'SYNTAX_INVALID' }
$fn=$ast.Find({param($node) $node -is [System.Management.Automation.Language.FunctionDefinitionAst] -and $node.Name -eq 'Get-ReadOnlyReturnCode'},$true)
if ($null -eq $fn) { throw 'HELPER_MISSING' }
# Only the pure helper is executed. Never dot-source broker/credential flow.
. ([ScriptBlock]::Create($fn.Extent.Text))
foreach ($name in @('LOGIN','REG')) {
  foreach ($expected in @(0,805004)) {
    $raw='{"trnm":"'+$name+'","return_code":'+$expected+'}'
    $obj=$raw | ConvertFrom-Json
    if ((Get-ReadOnlyReturnCode -Message $obj -Raw $raw) -ne $expected) { throw 'VALID_CODE_REJECTED' }
  }
}
foreach ($raw in @('{"return_code":0}', '{"return_code":805004}')) {
  $obj=$raw | ConvertFrom-Json
  if ((Get-ReadOnlyReturnCode -Message $obj -Raw $raw -ControlFrame $false) -ne $obj.return_code) { throw 'REST_VALID_REJECTED' }
}
foreach ($raw in @('{}','{"return_code":false}','{"return_code":"0"}','{"return_code":0.5}','{"return_code":null}','{"return_code":805004,"return_code":0}')) {
  $rejected=$false
  try { $obj=$raw | ConvertFrom-Json; $null=Get-ReadOnlyReturnCode -Message $obj -Raw $raw -ControlFrame $false }
  catch { $rejected=$true }
  if (-not $rejected) { throw 'REST_INVALID_ACCEPTED' }
}
$json=$ast.Find({param($node) $node -is [System.Management.Automation.Language.FunctionDefinitionAst] -and $node.Name -eq 'Convert-ReadOnlyJson'},$true)
if ($null -eq $json) { throw 'JSON_HELPER_MISSING' }
. ([ScriptBlock]::Create($json.Extent.Text))
$valid='{"return_code":0,"token":"fixture","data":[{"values":{"909":"0007","915":"1"}},{"values":{"909":"0008"}}],"nested":{"a":true,"b":null,"c":-12.5e2},"text":"quote\\\" : embedded"}'
$obj=Convert-ReadOnlyJson -Raw $valid
if ($obj.return_code -ne 0 -or $obj.data[0].values.'909' -cne '0007' -or $obj.nested.c -ne -1250) { throw 'JSON_VALID_CHANGED' }
$invalidJson=@(
'{"return_code":0,"token":"a","token":"b"}',
'{"acctNo":"a","acctNo":"b"}',
'{"a":{"909":"x","909":"y"}}',
'{"a":1,"\u0061":2}',
'{"a":1,"A":2}',
'{"a":NaN}', '{"a":Infinity}', '{"a":undefined}',
'{"a":01}', '{"a":+1}', '{"a":.5}', '{"a":1.}',
'{"a":1,}', '{"a":[1,]}', '{/*comment*/"a":1}',
'{"a":"\x41"}', '{"a":true}garbage', '[{}]',
('{"a":"' + [char]1 + '"}'),
('{"a":' + ('[' * 64) + '0' + (']' * 64) + '}'),
('{"a":"' + ('x' * 1048576) + '"}')
)
foreach ($raw in $invalidJson) {
  $rejected=$false
  try { $null=Convert-ReadOnlyJson -Raw $raw }
  catch { if ($_.Exception.Message -ne 'READ_ONLY_JSON_INVALID') { throw 'JSON_PRIVATE_ERROR_REQUIRED' }; $rejected=$true }
  if (-not $rejected) { throw 'JSON_INVALID_ACCEPTED' }
}
$null=Convert-ReadOnlyJson -Raw ('{"a":' + ('[' * 63) + '0' + (']' * 63) + '}')
$observer=$ast.Find({param($node) $node -is [System.Management.Automation.Language.FunctionDefinitionAst] -and $node.Name -eq 'Get-Type00ReadOnlyObservation'},$true)
if ($null -eq $observer) { throw 'OBSERVER_MISSING' }
if ($null -ne $observer) {
  . ([ScriptBlock]::Create($observer.Extent.Text))
  $fixture='{"trnm":"REAL","data":[{"type":"00","values":{"9201":"fixture-account","913":"체결","909":"0007","908":"120000","914":"100","915":"1"}},{"type":"00","values":{"9201":"other-account"}},{"type":"01"}]}'
  $summary=Get-Type00ReadOnlyObservation -Message (Convert-ReadOnlyJson -Raw $fixture) -Account 'fixture-account'
  if ($summary.Events -ne 2) { throw 'OBSERVATION_COUNT_INVALID' }
  if ($summary.Matched -ne 1) { throw 'OBSERVATION_ACCOUNT_INVALID' }
  if (-not $summary.ExecutionFieldsObserved) { throw 'OBSERVATION_FILL_INVALID' }
  $summary=Get-Type00ReadOnlyObservation -Message (Convert-ReadOnlyJson -Raw $fixture) -Account 'unmatched'
  if ($summary.Matched -ne 0 -or $summary.ExecutionFieldsObserved) { throw 'ACCOUNT_BINDING_INVALID' }
  $summary=Get-Type00ReadOnlyObservation -Message (Convert-ReadOnlyJson -Raw '{"trnm":"REAL","data":[{"type":"00","values":{"9201":"fixture-account","913":"접수"}}]}') -Account 'fixture-account'
  if ($summary.ExecutionFieldsObserved) { throw 'LIFECYCLE_CANNOT_PROVE_FILL' }
  foreach ($raw in @(
    '{"trnm":"REAL","data":null}',
    '{"trnm":"REAL","data":{"type":"00","values":{}}}',
    '{"trnm":"REAL","data":[null]}',
    '{"trnm":"REAL","data":[{"type":"00","values":{"909":7}}]}',
    '{"trnm":"REAL","data":[{"type":"00","values":{"9201":null}}]}',
    '{"trnm":"REAL","data":[{"type":"00","values":{"909":[]}}]}',
    '{"trnm":"REAL","data":[{"type":"00","values":{"unknown":"x"}}]}',
    ('{"trnm":"REAL","data":[{"type":"00","values":{"909":"' + ('x' * 4097) + '"}}]}')
  )) {
    $rejected=$false
    try { $null=Get-Type00ReadOnlyObservation -Message (Convert-ReadOnlyJson -Raw $raw) -Account 'fixture-account' }
    catch { if ($_.Exception.Message -ne 'TYPE00_FRAME_SCHEMA_INVALID') { throw 'SCHEMA_PRIVATE_ERROR_REQUIRED' }; $rejected=$true }
    if (-not $rejected) { throw 'SCHEMA_INVALID_ACCEPTED' }
  }
}
foreach ($name in @('Get-ReadOnlyMessageName','Is-Ping')) {
 $fn=$ast.Find({param($node) $node -is [Management.Automation.Language.FunctionDefinitionAst] -and $node.Name -eq $name},$true)
 if ($null -eq $fn) { throw 'MESSAGE_HELPER_MISSING' }
 . ([ScriptBlock]::Create($fn.Extent.Text))
}
foreach ($raw in @('{"trnm":["LOGIN"],"return_code":0}','{"trnm":["REG"],"return_code":0}','{"trnm":["PING"]}','{"trnm":null}','{"trnm":true}','{"trnm":1}','{}','{"trnm":" "}')) {
 $obj=Convert-ReadOnlyJson -Raw $raw
 $rejected=$false
 try { $null=Get-ReadOnlyMessageName -Message $obj }
 catch { if ($_.Exception.Message -ne 'READ_ONLY_MESSAGE_NAME_INVALID') { throw 'MESSAGE_PRIVATE_ERROR_REQUIRED' }; $rejected=$true }
 if (-not $rejected) { throw 'COERCED_MESSAGE_ACCEPTED' }
 if (Is-Ping -Obj $obj -Raw $raw) { throw 'COERCED_PING_ACCEPTED' }
}
if (-not (Is-Ping -Obj $null -Raw 'PING')) { throw 'PLAIN_PING_REJECTED' }
if (-not (Is-Ping -Obj (Convert-ReadOnlyJson -Raw '{"trnm":"ping"}') -Raw '{"trnm":"ping"}')) { throw 'JSON_PING_REJECTED' }
if ((Get-ReadOnlyMessageName -Message (Convert-ReadOnlyJson -Raw '{"trnm":"login"}')) -cne 'LOGIN') { throw 'VALID_MESSAGE_REJECTED' }
$decode=$ast.Find({param($node) $node -is [System.Management.Automation.Language.FunctionDefinitionAst] -and $node.Name -eq 'Convert-StrictWebSocketText'},$true)
if ($null -eq $decode) { throw 'UTF8_HELPER_MISSING' }
. ([ScriptBlock]::Create($decode.Extent.Text))
if ((Convert-StrictWebSocketText -Bytes ([byte[]]@(65,66))) -ne 'AB') { throw 'UTF8_VALID_REJECTED' }
foreach ($bytes in @(([byte[]]@(255)),([byte[]]@(192,128)),([byte[]]@(226,130)),([byte[]]@(237,160,128)))) {
  $rejected=$false
  try { $null=Convert-StrictWebSocketText -Bytes $bytes }
  catch { if ($_.Exception.Message -ne 'WEBSOCKET_UTF8_INVALID') { throw 'UTF8_PRIVATE_ERROR_REQUIRED' }; $rejected=$true }
  if (-not $rejected) { throw 'UTF8_INVALID_ACCEPTED' }
}
$invalid=@(
'{"trnm":"LOGIN"}',
'{"trnm":"LOGIN","return_code":null}',
'{"trnm":"LOGIN","return_code":false}',
'{"trnm":"LOGIN","return_code":"0"}',
'{"trnm":"LOGIN","return_code":0.5}',
'{"trnm":"LOGIN","return_code":-1}',
'{"trnm":"LOGIN","return_code":2147483648}',
'{"trnm":"LOGIN","return_code":805004,"return_code":0}',
'{"trnm":"LOGIN","return_code":0,"return_code":0}',
'{"trnm":"LOGIN","return_code":0,"return_\u0063ode":0}',
'{"trnm":"LOGIN","return_code":0,"RETURN_CODE":0}',
'{"trnm":"LOGIN","trnm":"LOGIN","return_code":0}',
'{"trnm":"REG","return_code":0,"nested":{"return_code":0}}'
)
foreach ($raw in $invalid) {
  $rejected=$false
  try { $obj=$raw | ConvertFrom-Json -ErrorAction Stop } catch { $rejected=$true }
  if (-not $rejected) {
    try { $null=Get-ReadOnlyReturnCode -Message $obj -Raw $raw }
    catch {
      if ($_.Exception.Message -ne 'READ_ONLY_PROTOCOL_RESPONSE_INVALID') { throw 'PRIVATE_ERROR_REQUIRED' }
      $rejected=$true
    }
  }
  if (-not $rejected) { throw 'AMBIGUOUS_ACK_ACCEPTED' }
}
'''.replace('PATH_BASE64', path)
        encoded = base64.b64encode(harness.encode('utf-16le')).decode()
        for runtime in runtimes:
            with self.subTest(runtime=pathlib.Path(runtime).name):
                result = subprocess.run([runtime, '-NoProfile', '-NonInteractive', '-EncodedCommand', encoded], capture_output=True, text=True, timeout=30)
                self.assertEqual(result.returncode, 0, result.stderr)

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

    def test_failure_diagnostics_preserve_completed_stage_without_raw_message(self):
        for marker in ("$script:TokenOk", "$script:AccountEndpointOk", "$script:WsConnected", "$script:WsLoginOk"):
            self.assertIn(marker, self.text)
        self.assertIn("DETAIL_CODE", self.text)
        self.assertIn("ERROR_CLASS", self.text)
        self.assertIn("Set-SanitizedErrorDetail $obj.return_msg", self.text)
        self.assertNotIn("RETURN_MSG=", self.text)

    def test_async_void_results_are_suppressed(self):
        self.assertIn("$null = $Ws.SendAsync", self.text)
        self.assertIn("$null = $ws.ConnectAsync", self.text)
        self.assertIn("$null = $ws.CloseAsync", self.text)

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
        self.assertIn("values.'9201' -ceq $Account",self.text)
        for fid in ("'909'","'908'","'914'","'915'"):
            self.assertIn(fid,self.text)
        self.assertIn('BROKER_NATIVE_EXECUTION_ID_CAPTURE_TESTED=[bool]$executionObserved',self.text)

if __name__=="__main__": unittest.main()
