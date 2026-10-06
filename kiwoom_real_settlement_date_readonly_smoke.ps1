# User-operated Kiwoom REAL read-only settlement + broker-date attestation smoke.
# Fixed REAL host. Calls OAuth + ka00001 + kt00001 + kt00017 only.
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
        BROKER_TODAY_ENDPOINT_OK=$false
        BROKER_DATE_HEADER_VALID=$false
        BROKER_TIME_FRESH=$false
        SOURCE_ACCOUNT_ORIGIN_AUTHENTICATED=$false
        SNAPSHOT_FRESHNESS_ATTESTED=$false
        TRADING_DATE_ORIGIN_ATTESTED=$false
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
    } catch { return $false }
}

if ($env:KIWOOM_ENV -ne "REAL") { Fail-Closed "CONFIG" }
if ($env:KIWOOM_BASE_URL -ne "https://api.kiwoom.com") { Fail-Closed "CONFIG" }
if ($env:KIWOOM_ORDERING_ENABLED -notin @("0","false","off","no")) { Fail-Closed "CONFIG" }
if ([string]::IsNullOrWhiteSpace($env:KIWOOM_APP_KEY) -or [string]::IsNullOrWhiteSpace($env:KIWOOM_APP_SECRET)) { Fail-Closed "CONFIG" }

try {
    $tokenBody = @{ grant_type="client_credentials"; appkey=$env:KIWOOM_APP_KEY; secretkey=$env:KIWOOM_APP_SECRET } | ConvertTo-Json -Compress
    $token = Invoke-RestMethod -Uri "https://api.kiwoom.com/oauth2/token" -Method Post -ContentType "application/json;charset=UTF-8" -Body $tokenBody
    if ($token.return_code -ne 0 -or [string]::IsNullOrWhiteSpace($token.token)) { Fail-Closed "TOKEN" ([int]$token.return_code) }

    $headers = @{ "authorization"="Bearer $($token.token)"; "api-id"="ka00001"; "cont-yn"="N"; "next-key"="" }
    $account = Invoke-RestMethod -Uri "https://api.kiwoom.com/api/dostk/acnt" -Method Post -Headers $headers -ContentType "application/json;charset=UTF-8" -Body "{}"
    if ($account.return_code -ne 0 -or [string]::IsNullOrWhiteSpace([string]$account.acctNo)) { Fail-Closed "ACCOUNT" ([int]$account.return_code) }

    $headers["api-id"] = "kt00001"
    $settlementBody = @{ qry_tp="2" } | ConvertTo-Json -Compress
    $settlement = Invoke-RestMethod -Uri "https://api.kiwoom.com/api/dostk/acnt" -Method Post -Headers $headers -ContentType "application/json;charset=UTF-8" -Body $settlementBody
    if ($settlement.return_code -ne 0) { Fail-Closed "SETTLEMENT" ([int]$settlement.return_code) }

    $settlementValid = (Require-Nonnegative-CashText $settlement.entr) -and
                       (Require-Nonnegative-CashText $settlement.pymn_alow_amt) -and
                       (Require-Nonnegative-CashText $settlement.d2_entra) -and
                       (Require-Nonnegative-CashText $settlement.ord_alow_amt)
    if (-not $settlementValid) { Fail-Closed "SETTLEMENT_FIELDS" 0 }

    $headers["api-id"] = "kt00017"
    $todayResponse = Invoke-WebRequest -UseBasicParsing -Uri "https://api.kiwoom.com/api/dostk/acnt" -Method Post -Headers $headers -ContentType "application/json;charset=UTF-8" -Body "{}"
    $today = $todayResponse.Content | ConvertFrom-Json
    if ($today.return_code -ne 0) { Fail-Closed "BROKER_TODAY" ([int]$today.return_code) }

    $dateHeader = [string]$todayResponse.Headers["Date"]
    if ([string]::IsNullOrWhiteSpace($dateHeader)) { Fail-Closed "BROKER_DATE_HEADER" 0 }

    $serverTime = [DateTimeOffset]::MinValue
    $parsed = [DateTimeOffset]::TryParse(
        $dateHeader,
        [System.Globalization.CultureInfo]::InvariantCulture,
        [System.Globalization.DateTimeStyles]::AssumeUniversal,
        [ref]$serverTime
    )
    if (-not $parsed) { Fail-Closed "BROKER_DATE_HEADER" 0 }

    $now = [DateTimeOffset]::UtcNow
    $ageSeconds = [Math]::Abs(($now - $serverTime.ToUniversalTime()).TotalSeconds)
    if ($ageSeconds -gt 300) { Fail-Closed "BROKER_TIME_STALE" 0 }

    $kst = [TimeSpan]::FromHours(9)
    $tradingDate = $serverTime.ToOffset($kst).ToString("yyyy-MM-dd")

    @{
        STAGE="REAL_SETTLEMENT_DATE_READ_ONLY_SMOKE"
        RETURN_CODE=0
        TOKEN_OK=$true
        ACCOUNT_ENDPOINT_OK=$true
        SETTLEMENT_ENDPOINT_OK=$true
        SETTLEMENT_FIELDS_VALID=$true
        BROKER_TODAY_ENDPOINT_OK=$true
        BROKER_DATE_HEADER_VALID=$true
        BROKER_TIME_FRESH=$true
        TRADING_DATE=$tradingDate
        SOURCE_ACCOUNT_ORIGIN_AUTHENTICATED=$true
        SNAPSHOT_FRESHNESS_ATTESTED=$true
        TRADING_DATE_ORIGIN_ATTESTED=$true
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
