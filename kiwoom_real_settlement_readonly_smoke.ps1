# User-operated Kiwoom REAL settlement read-only smoke.
# Fixed REAL host. Calls OAuth + ka00001 + kt00001(qry_tp=2) only.
# Never prints App Key, Secret, token, account number, balances, or provider bodies.
$ErrorActionPreference = "Stop"

function Convert-ReadOnlyJson([string]$Raw) {
    # Validate grammar and every object's keys before PowerShell can collapse them.
    # State is private to this invocation; no provider text is included in errors.
    try {
        if ($Raw.Length -gt 1048576 -or [Text.Encoding]::UTF8.GetByteCount($Raw) -gt 1048576) { throw 'invalid' }
        $state = @{ Position = 0 }
        $stringToken = [regex]::new('\G"(?:[^"\\\x00-\x1f]|\\(?:["\\/bfnrt]|u[0-9a-fA-F]{4}))*"')
        $valueToken = [regex]::new('\G(?:true|false|null|-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?)')
        function Skip-JsonSpace {
            while ($state.Position -lt $Raw.Length -and $Raw[$state.Position] -in @(' ', "`t", "`r", "`n")) { $state.Position++ }
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
    $tokenWire = Invoke-WebRequest -UseBasicParsing @tokenArgs
    $token = Convert-ReadOnlyJson -Raw $tokenWire.Content
    $tokenCode = Get-ReadOnlyReturnCode -Message $token -Raw $tokenWire.Content -ControlFrame $false
    if ($tokenCode -ne 0 -or $token.token -isnot [string] -or [string]::IsNullOrWhiteSpace($token.token)) { Fail-Closed "TOKEN" $tokenCode }

    $headers = @{ "authorization"="Bearer $($token.token)"; "api-id"="ka00001"; "cont-yn"="N"; "next-key"="" }
    $accountArgs = @{ Uri="https://api.kiwoom.com/api/dostk/acnt"; Method="Post"; Headers=$headers; ContentType="application/json;charset=UTF-8"; Body="{}" }
    $accountWire = Invoke-WebRequest -UseBasicParsing @accountArgs
    $account = Convert-ReadOnlyJson -Raw $accountWire.Content
    $accountCode = Get-ReadOnlyReturnCode -Message $account -Raw $accountWire.Content -ControlFrame $false
    if ($accountCode -ne 0 -or $account.acctNo -isnot [string] -or [string]::IsNullOrWhiteSpace($account.acctNo)) { Fail-Closed "ACCOUNT" $accountCode }

    # Windows PowerShell 5.1 / .NET Framework compatible fingerprinting.
    # Avoid newer SHA256.HashData / Convert.ToHexString APIs.
    $fingerprintKeyText = "indexalert-fingerprint-key-v1" + [char]0 + $env:KIWOOM_APP_SECRET
    $sha256 = [System.Security.Cryptography.SHA256]::Create()
    try {
        $keyBytes = $sha256.ComputeHash([System.Text.Encoding]::UTF8.GetBytes($fingerprintKeyText))
    } finally {
        $sha256.Dispose()
    }
    $hmac = New-Object System.Security.Cryptography.HMACSHA256 -ArgumentList (, $keyBytes)
    try {
        $fingerprintDataText = "indexalert-kiwoom-account-fingerprint-v1" + [char]0 + [string]$account.acctNo
        $data = [System.Text.Encoding]::UTF8.GetBytes($fingerprintDataText)
        $fingerprintBytes = $hmac.ComputeHash($data)
        $hex = ([System.BitConverter]::ToString($fingerprintBytes)).Replace("-", "").ToLowerInvariant()
        $fingerprint = "sha256:" + $hex
    } finally {
        $hmac.Dispose()
        [Array]::Clear($keyBytes, 0, $keyBytes.Length)
    }

    $headers["api-id"] = "kt00001"
    $settlementBody = @{ qry_tp="2" } | ConvertTo-Json -Compress
    $settlementArgs = @{ Uri="https://api.kiwoom.com/api/dostk/acnt"; Method="Post"; Headers=$headers; ContentType="application/json;charset=UTF-8"; Body=$settlementBody }
    $settlementWire = Invoke-WebRequest -UseBasicParsing @settlementArgs
    $settlement = Convert-ReadOnlyJson -Raw $settlementWire.Content
    $settlementCode = Get-ReadOnlyReturnCode -Message $settlement -Raw $settlementWire.Content -ControlFrame $false
    if ($settlementCode -ne 0) { Fail-Closed "SETTLEMENT" $settlementCode }

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
    if ($code -eq -1) {
        Fail-Closed "LOCAL_COMPATIBILITY_OR_NETWORK" $code
    }
    Fail-Closed "NETWORK_OR_PROVIDER" $code
}
