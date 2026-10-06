# User-operated Kiwoom REAL settlement read-only smoke.
# Fixed REAL host. Calls OAuth + ka00001 + kt00001(qry_tp=2) only.
# Never prints App Key, Secret, token, account number, balances, or provider bodies.
$ErrorActionPreference = "Stop"

function Fail-Closed([string]$Stage, [int]$Code = -1) {
    @{
        STAGE=$Stage
        RETURN_CODE=$Code
        TOKEN_OK=$false
        ACCOUNT_ENDPOINT_OK=$false
        SETTLEMENT_ENDPOINT_OK=$false
        SETTLEMENT_FIELDS_VALID=$false
        ORDERING="DISABLED"
        REAL_ORDERS_AUTHORIZED=$false
        FUNDS_MOVEMENT_AUTHORIZED=$false
        PERMISSION_CHANGE_AUTHORIZED=$false
        GENUINE_LIVE_PROVENANCE_VERIFIED=$false
    } | ConvertTo-Json -Compress
    exit 2
}

function Require-Nonnegative-CashText([object]$Value) {
    if ($Value -isnot [string]) { return $false }
    if ($Value -notmatch '^\+?(?:[0-9]+|[0-9]{1,3}(?:,[0-9]{3})+)(?:\.[0-9]+)?$') { return $false }
    try {
        $normalized = $Value.Replace(",", "")
        $number = [decimal]::Parse($normalized, [System.Globalization.CultureInfo]::InvariantCulture)
        return $number -ge 0
    } catch {
        return $false
    }
}

if ($env:KIWOOM_ENV -ne "REAL") { Fail-Closed "CONFIG" }
if ($env:KIWOOM_BASE_URL -ne "https://api.kiwoom.com") { Fail-Closed "CONFIG" }
if ($env:KIWOOM_ORDERING_ENABLED -notin @("0","false","off","no")) { Fail-Closed "CONFIG" }
if ([string]::IsNullOrWhiteSpace($env:KIWOOM_APP_KEY) -or [string]::IsNullOrWhiteSpace($env:KIWOOM_APP_SECRET)) { Fail-Closed "CONFIG" }

try {
    $tokenBody = @{ grant_type="client_credentials"; appkey=$env:KIWOOM_APP_KEY; secretkey=$env:KIWOOM_APP_SECRET } | ConvertTo-Json -Compress
    $tokenArgs = @{ Uri="https://api.kiwoom.com/oauth2/token"; Method="Post"; ContentType="application/json;charset=UTF-8"; Body=$tokenBody }
    $token = Invoke-RestMethod @tokenArgs
    if ($token.return_code -ne 0 -or [string]::IsNullOrWhiteSpace($token.token)) { Fail-Closed "TOKEN" ([int]$token.return_code) }

    $headers = @{ "authorization"="Bearer $($token.token)"; "api-id"="ka00001"; "cont-yn"="N"; "next-key"="" }
    $accountArgs = @{ Uri="https://api.kiwoom.com/api/dostk/acnt"; Method="Post"; Headers=$headers; ContentType="application/json;charset=UTF-8"; Body="{}" }
    $account = Invoke-RestMethod @accountArgs
    if ($account.return_code -ne 0 -or [string]::IsNullOrWhiteSpace([string]$account.acctNo)) { Fail-Closed "ACCOUNT" ([int]$account.return_code) }

    $fingerprintKeyText = "indexalert-fingerprint-key-v1" + [char]0 + $env:KIWOOM_APP_SECRET
    $keyBytes = [System.Security.Cryptography.SHA256]::HashData([System.Text.Encoding]::UTF8.GetBytes($fingerprintKeyText))
    $hmac = [System.Security.Cryptography.HMACSHA256]::new($keyBytes)
    try {
        $fingerprintDataText = "indexalert-kiwoom-account-fingerprint-v1" + [char]0 + [string]$account.acctNo
        $data = [System.Text.Encoding]::UTF8.GetBytes($fingerprintDataText)
        $fingerprintBytes = $hmac.ComputeHash($data)
        $fingerprint = "sha256:" + ([Convert]::ToHexString($fingerprintBytes).ToLowerInvariant())
    } finally {
        $hmac.Dispose()
        [Array]::Clear($keyBytes, 0, $keyBytes.Length)
    }

    $headers["api-id"] = "kt00001"
    $settlementBody = @{ qry_tp="2" } | ConvertTo-Json -Compress
    $settlementArgs = @{ Uri="https://api.kiwoom.com/api/dostk/acnt"; Method="Post"; Headers=$headers; ContentType="application/json;charset=UTF-8"; Body=$settlementBody }
    $settlement = Invoke-RestMethod @settlementArgs
    if ($settlement.return_code -ne 0) { Fail-Closed "SETTLEMENT" ([int]$settlement.return_code) }

    $valid = (Require-Nonnegative-CashText $settlement.entr) -and (Require-Nonnegative-CashText $settlement.pymn_alow_amt) -and (Require-Nonnegative-CashText $settlement.d2_entra) -and (Require-Nonnegative-CashText $settlement.ord_alow_amt)
    if (-not $valid) { Fail-Closed "SETTLEMENT_FIELDS" 0 }

    @{
        STAGE="REAL_SETTLEMENT_READ_ONLY_SMOKE"
        RETURN_CODE=0
        TOKEN_OK=$true
        ACCOUNT_ENDPOINT_OK=$true
        SETTLEMENT_ENDPOINT_OK=$true
        SETTLEMENT_FIELDS_VALID=$true
        ACCOUNT_FINGERPRINT=$fingerprint
        CAPTURED_AT=[DateTimeOffset]::UtcNow.ToString("o")
        SOURCE_ACCOUNT_ORIGIN_AUTHENTICATED=$true
        SNAPSHOT_FRESHNESS_ATTESTED=$true
        TRADING_DATE_ORIGIN_ATTESTED=$false
        ORDERING="DISABLED"
        REAL_ORDERS_AUTHORIZED=$false
        FUNDS_MOVEMENT_AUTHORIZED=$false
        PERMISSION_CHANGE_AUTHORIZED=$false
        GENUINE_LIVE_PROVENANCE_VERIFIED=$false
    } | ConvertTo-Json -Compress
}
catch {
    $code = -1
    try {
        $j = $_.ErrorDetails.Message | ConvertFrom-Json
        if ($null -ne $j.return_code) { $code = [int]$j.return_code }
    } catch {}
    Fail-Closed "NETWORK_OR_PROVIDER" $code
}
