# User-operated Kiwoom REAL read-only settlement + broker-date attestation smoke.
# Fixed REAL host. Calls OAuth + ka00001 + kt00001 + kt00017 only.
# Never prints App Key, Secret, token, account number, balances, or provider bodies.
$ErrorActionPreference = "Stop"

function Convert-ReadOnlyJson([string]$Raw) {
    # Validate grammar and every object's keys before PowerShell can collapse them.
    # State is private to this invocation; no provider text is included in errors.
    try {
        if ($Raw.Length -gt 1048576 -or [Text.Encoding]::UTF8.GetByteCount($Raw) -gt 1048576) { throw 'invalid' }
        $state = @{ Position = 0 }
        $budget = [Diagnostics.Stopwatch]::StartNew()
        $stringToken = [regex]::new('\G"(?:[^"\\\x00-\x1f]|\\(?:["\\/bfnrt]|u[0-9a-fA-F]{4}))*"', [Text.RegularExpressions.RegexOptions]::None, [TimeSpan]::FromSeconds(1))
        $valueToken = [regex]::new('\G(?:true|false|null|-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?)', [Text.RegularExpressions.RegexOptions]::None, [TimeSpan]::FromSeconds(1))
        $spaceToken = [regex]::new('\G[ \t\r\n]*', [Text.RegularExpressions.RegexOptions]::None, [TimeSpan]::FromSeconds(1))
        function Skip-JsonSpace {
            if ($budget.ElapsedMilliseconds -gt 5000) { throw 'invalid' }
            $state.Position += $spaceToken.Match($Raw, $state.Position).Length
        }
        function Read-JsonString {
            $match = $stringToken.Match($Raw, $state.Position)
            if (-not $match.Success) { throw 'invalid' }
            $state.Position += $match.Length
            return $match.Value
        }
        function Read-JsonValue([int]$Depth) {
            Skip-JsonSpace
            if ($state.Position -ge $Raw.Length) { throw 'invalid' }
            $first = $Raw[$state.Position]
            if ($first -eq '{' -or $first -eq '[') {
                if ($Depth -ge 64) { throw 'invalid' }
                $object = $first -eq '{'
                $close = if ($object) { '}' } else { ']' }
                $state.Position++
                $keys = [Collections.Generic.HashSet[string]]::new([StringComparer]::OrdinalIgnoreCase)
                Skip-JsonSpace
                if ($state.Position -lt $Raw.Length -and $Raw[$state.Position] -eq $close) { $state.Position++; return }
                while ($true) {
                    if ($object) {
                        $encoded = Read-JsonString
                        $key = $encoded | ConvertFrom-Json -ErrorAction Stop
                        if (-not $keys.Add([string]$key)) { throw 'invalid' }
                        Skip-JsonSpace
                        if ($state.Position -ge $Raw.Length -or $Raw[$state.Position] -ne ':') { throw 'invalid' }
                        $state.Position++
                    }
                    Read-JsonValue ($Depth + 1)
                    Skip-JsonSpace
                    if ($state.Position -ge $Raw.Length) { throw 'invalid' }
                    if ($Raw[$state.Position] -eq $close) { $state.Position++; return }
                    if ($Raw[$state.Position] -ne ',') { throw 'invalid' }
                    $state.Position++
                    Skip-JsonSpace
                    # The next iteration requires a real member/value, prohibiting trailing commas.
                }
            }
            if ($first -eq '"') { $null = Read-JsonString; return }
            $match = $valueToken.Match($Raw, $state.Position)
            if (-not $match.Success) { throw 'invalid' }
            $state.Position += $match.Length
        }
        Skip-JsonSpace
        if ($state.Position -ge $Raw.Length -or $Raw[$state.Position] -ne '{') { throw 'invalid' }
        Read-JsonValue 0
        Skip-JsonSpace
        if ($state.Position -ne $Raw.Length) { throw 'invalid' }
        return $Raw | ConvertFrom-Json -ErrorAction Stop
    } catch {
        throw 'READ_ONLY_JSON_INVALID'
    }
}


function Get-ReadOnlyReturnCode([object]$Message, [string]$Raw, [bool]$ControlFrame = $true) {
    try {
        if ($null -eq $Message -or $null -eq $Message.PSObject.Properties['return_code']) {
            throw "READ_ONLY_PROTOCOL_RESPONSE_INVALID"
        }
        $code = $Message.return_code
        if (($code -isnot [int] -and $code -isnot [long]) -or $code -lt 0 -or $code -gt [int]::MaxValue) {
            throw "READ_ONLY_PROTOCOL_RESPONSE_INVALID"
        }
        $codeKeys = 0
        $nameKeys = 0
        foreach ($match in [regex]::Matches($Raw, '(?<!\\)"((?:[^"\\]|\\.)*)"\s*:')) {
            $key = ('"' + $match.Groups[1].Value + '"') | ConvertFrom-Json -ErrorAction Stop
            if ($key -ieq 'return_code') { $codeKeys++ }
            if ($key -ieq 'trnm') { $nameKeys++ }
        }
        if ($codeKeys -ne 1 -or ($ControlFrame -and $nameKeys -ne 1)) { throw "READ_ONLY_PROTOCOL_RESPONSE_INVALID" }
        return [int]$code
    } catch {
        throw "READ_ONLY_PROTOCOL_RESPONSE_INVALID"
    }
}

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
    $tokenWire = Invoke-WebRequest -TimeoutSec 15 -UseBasicParsing -Uri "https://api.kiwoom.com/oauth2/token" -Method Post -ContentType "application/json;charset=UTF-8" -Body $tokenBody
    $token = Convert-ReadOnlyJson -Raw $tokenWire.Content
    $tokenCode = Get-ReadOnlyReturnCode -Message $token -Raw $tokenWire.Content -ControlFrame $false
    if ($tokenCode -ne 0 -or $token.token -isnot [string] -or [string]::IsNullOrWhiteSpace($token.token)) { Fail-Closed "TOKEN" $tokenCode }

    $headers = @{ "authorization"="Bearer $($token.token)"; "api-id"="ka00001"; "cont-yn"="N"; "next-key"="" }
    $accountWire = Invoke-WebRequest -TimeoutSec 15 -UseBasicParsing -Uri "https://api.kiwoom.com/api/dostk/acnt" -Method Post -Headers $headers -ContentType "application/json;charset=UTF-8" -Body "{}"
    $account = Convert-ReadOnlyJson -Raw $accountWire.Content
    $accountCode = Get-ReadOnlyReturnCode -Message $account -Raw $accountWire.Content -ControlFrame $false
    if ($accountCode -ne 0 -or $account.acctNo -isnot [string] -or [string]::IsNullOrWhiteSpace($account.acctNo)) { Fail-Closed "ACCOUNT" $accountCode }

    $headers["api-id"] = "kt00001"
    $settlementBody = @{ qry_tp="2" } | ConvertTo-Json -Compress
    $settlementWire = Invoke-WebRequest -TimeoutSec 15 -UseBasicParsing -Uri "https://api.kiwoom.com/api/dostk/acnt" -Method Post -Headers $headers -ContentType "application/json;charset=UTF-8" -Body $settlementBody
    $settlement = Convert-ReadOnlyJson -Raw $settlementWire.Content
    $settlementCode = Get-ReadOnlyReturnCode -Message $settlement -Raw $settlementWire.Content -ControlFrame $false
    if ($settlementCode -ne 0) { Fail-Closed "SETTLEMENT" $settlementCode }

    $settlementValid = (Require-Nonnegative-CashText $settlement.entr) -and
                       (Require-Nonnegative-CashText $settlement.pymn_alow_amt) -and
                       (Require-Nonnegative-CashText $settlement.d2_entra) -and
                       (Require-Nonnegative-CashText $settlement.ord_alow_amt)
    if (-not $settlementValid) { Fail-Closed "SETTLEMENT_FIELDS" 0 }

    $headers["api-id"] = "kt00017"
    $todayResponse = Invoke-WebRequest -TimeoutSec 15 -UseBasicParsing -Uri "https://api.kiwoom.com/api/dostk/acnt" -Method Post -Headers $headers -ContentType "application/json;charset=UTF-8" -Body "{}"
    $today = Convert-ReadOnlyJson -Raw $todayResponse.Content
    $todayCode = Get-ReadOnlyReturnCode -Message $today -Raw $todayResponse.Content -ControlFrame $false
    if ($todayCode -ne 0) { Fail-Closed "BROKER_TODAY" $todayCode }

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
