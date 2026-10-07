# User-operated Kiwoom REAL whole-account read-only scope smoke.
# Fixed REAL host. Read/query only: OAuth, ka00001, kt00001, kt00017,
# kt00007(all/open), ka10076(filled), kt00018(KRX/NXT).
# No order-create/amend/cancel/revoke or funds/permission action.
# Never prints credentials, token, account number, symbols, order IDs, prices,
# quantities, balances, holdings or provider bodies. Only booleans/counts/date.
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
        BROKER_TODAY_ENDPOINT_OK=$false
        TRADING_DATE_ORIGIN_ATTESTED=$false
        ORDER_HISTORY_ENDPOINT_OK=$false
        ORDER_HISTORY_COMPLETE=$false
        OPEN_ORDER_ENDPOINT_OK=$false
        OPEN_ORDER_COMPLETE=$false
        FILLED_ORDER_ENDPOINT_OK=$false
        FILLED_ORDER_COMPLETE=$false
        HOLDINGS_KRX_ENDPOINT_OK=$false
        HOLDINGS_KRX_COMPLETE=$false
        HOLDINGS_NXT_ENDPOINT_OK=$false
        HOLDINGS_NXT_COMPLETE=$false
        ACCOUNT_SCOPE_BASELINE_COMPLETE=$false
        BROKER_NATIVE_ORDER_SNAPSHOT_CAPTURE_TESTED=$false
        BROKER_NATIVE_EXECUTION_ID_CAPTURE_TESTED=$false
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

function Invoke-ReadOnlyPage(
    [string]$ApiId,
    [hashtable]$Body,
    [string]$ContYn = "N",
    [string]$NextKey = ""
) {
    if ($ApiId -notin @("ka00001","kt00001","kt00017","kt00007","ka10076","kt00018")) {
        throw "READ_ONLY_API_BLOCKED"
    }
    if ($ContYn -notin @("N","Y")) { throw "CONTINUATION_BLOCKED" }
    if (($ContYn -eq "Y") -and [string]::IsNullOrWhiteSpace($NextKey)) { throw "CONTINUATION_BLOCKED" }
    if (($ContYn -eq "N") -and -not [string]::IsNullOrEmpty($NextKey)) { throw "CONTINUATION_BLOCKED" }

    $headers = @{
        "authorization" = "Bearer $script:Token"
        "api-id" = $ApiId
        "cont-yn" = $ContYn
        "next-key" = $NextKey
    }
    $json = $Body | ConvertTo-Json -Compress
    $respArgs = @{
        UseBasicParsing = $true
        Uri = "https://api.kiwoom.com/api/dostk/acnt"
        Method = "Post"
        Headers = $headers
        ContentType = "application/json;charset=UTF-8"
        Body = $json
    }
    $resp = Invoke-WebRequest @respArgs
    $obj = Convert-ReadOnlyJson -Raw $resp.Content
    $responseCode = Get-ReadOnlyReturnCode -Message $obj -Raw $resp.Content -ControlFrame $false
    if ($responseCode -ne 0) {
        $e = New-Object System.Exception("PROVIDER_RETURN_CODE")
        $e.Data["return_code"] = $responseCode
        throw $e
    }

    $respCont = [string]$resp.Headers["cont-yn"]
    if ([string]::IsNullOrWhiteSpace($respCont)) { $respCont = "N" }
    if ($respCont -notin @("N","Y")) { throw "CONTINUATION_BLOCKED" }
    $respNext = [string]$resp.Headers["next-key"]
    if (($respCont -eq "Y") -and [string]::IsNullOrWhiteSpace($respNext)) { throw "CONTINUATION_BLOCKED" }
    if ($respNext.Length -gt 4096 -or $respNext.Contains([char]13) -or $respNext.Contains([char]10)) {
        throw "CONTINUATION_BLOCKED"
    }

    return @{
        Body = $obj
        ContYn = $respCont
        NextKey = $respNext
        DateHeader = [string]$resp.Headers["Date"]
    }
}

function Get-PagedCount(
    [string]$ApiId,
    [hashtable]$Body,
    [string]$ArrayProperty
) {
    $count = 0
    $cont = "N"
    $next = ""
    for ($pageNo = 1; $pageNo -le 10; $pageNo++) {
        $page = Invoke-ReadOnlyPage -ApiId $ApiId -Body $Body -ContYn $cont -NextKey $next
        $rows = $page.Body.$ArrayProperty
        if ($null -ne $rows) {
            if ($rows -is [System.Array]) {
                $count += $rows.Count
            } else {
                $count += 1
            }
        }
        if ($page.ContYn -ne "Y") {
            return @{ Count=$count; Complete=$true }
        }
        $cont = "Y"
        $next = $page.NextKey
    }
    return @{ Count=$count; Complete=$false }
}

if ($env:KIWOOM_ENV -ne "REAL") { Fail-Closed "CONFIG" }
if ($env:KIWOOM_BASE_URL -ne "https://api.kiwoom.com") { Fail-Closed "CONFIG" }
if ($env:KIWOOM_ORDERING_ENABLED -notin @("0","false","off","no")) { Fail-Closed "CONFIG" }
if ([string]::IsNullOrWhiteSpace($env:KIWOOM_APP_KEY) -or [string]::IsNullOrWhiteSpace($env:KIWOOM_APP_SECRET)) { Fail-Closed "CONFIG" }

try {
    $tokenBody = @{ grant_type="client_credentials"; appkey=$env:KIWOOM_APP_KEY; secretkey=$env:KIWOOM_APP_SECRET } | ConvertTo-Json -Compress
    $tokenArgs = @{ Uri="https://api.kiwoom.com/oauth2/token"; Method="Post"; ContentType="application/json;charset=UTF-8"; Body=$tokenBody }
    $tokenWire = Invoke-WebRequest -UseBasicParsing @tokenArgs
    $tokenResp = Convert-ReadOnlyJson -Raw $tokenWire.Content
    $tokenCode = Get-ReadOnlyReturnCode -Message $tokenResp -Raw $tokenWire.Content -ControlFrame $false
    if ($tokenCode -ne 0 -or $tokenResp.token -isnot [string] -or [string]::IsNullOrWhiteSpace($tokenResp.token)) {
        Fail-Closed "TOKEN" $tokenCode
    }
    $script:Token = [string]$tokenResp.token

    $accountPage = Invoke-ReadOnlyPage -ApiId "ka00001" -Body @{}
    if ($accountPage.Body.acctNo -isnot [string] -or [string]::IsNullOrWhiteSpace($accountPage.Body.acctNo)) { Fail-Closed "ACCOUNT" 0 }

    $settlementPage = Invoke-ReadOnlyPage -ApiId "kt00001" -Body @{ qry_tp="2" }
    $s = $settlementPage.Body
    $settlementValid = (Require-Nonnegative-CashText $s.entr) -and
                       (Require-Nonnegative-CashText $s.pymn_alow_amt) -and
                       (Require-Nonnegative-CashText $s.d2_entra) -and
                       (Require-Nonnegative-CashText $s.ord_alow_amt)
    if (-not $settlementValid) { Fail-Closed "SETTLEMENT_FIELDS" 0 }

    $todayPage = Invoke-ReadOnlyPage -ApiId "kt00017" -Body @{}
    $dateHeader = $todayPage.DateHeader
    if ([string]::IsNullOrWhiteSpace($dateHeader)) { Fail-Closed "BROKER_DATE_HEADER" 0 }

    $serverTime = [DateTimeOffset]::MinValue
    $parsed = [DateTimeOffset]::TryParse(
        $dateHeader,
        [System.Globalization.CultureInfo]::InvariantCulture,
        [System.Globalization.DateTimeStyles]::AssumeUniversal,
        [ref]$serverTime
    )
    if (-not $parsed) { Fail-Closed "BROKER_DATE_HEADER" 0 }
    $ageSeconds = [Math]::Abs(([DateTimeOffset]::UtcNow - $serverTime.ToUniversalTime()).TotalSeconds)
    if ($ageSeconds -gt 300) { Fail-Closed "BROKER_TIME_STALE" 0 }
    $tradingDate = $serverTime.ToOffset([TimeSpan]::FromHours(9)).ToString("yyyy-MM-dd")
    $ordDate = $serverTime.ToOffset([TimeSpan]::FromHours(9)).ToString("yyyyMMdd")

    $orderBody = @{
        qry_tp="1"; stk_bond_tp="0"; sell_tp="0"; dmst_stex_tp="%";
        ord_dt=$ordDate; stk_cd=""; fr_ord_no=""
    }
    $orders = Get-PagedCount -ApiId "kt00007" -Body $orderBody -ArrayProperty "acnt_ord_cntr_prps_dtl"
    if (-not $orders.Complete) { Fail-Closed "ORDER_HISTORY_PAGINATION" 0 }

    $openBody = @{
        qry_tp="3"; stk_bond_tp="0"; sell_tp="0"; dmst_stex_tp="%";
        ord_dt=$ordDate; stk_cd=""; fr_ord_no=""
    }
    $openOrders = Get-PagedCount -ApiId "kt00007" -Body $openBody -ArrayProperty "acnt_ord_cntr_prps_dtl"
    if (-not $openOrders.Complete) { Fail-Closed "OPEN_ORDER_PAGINATION" 0 }

    $fills = Get-PagedCount -ApiId "ka10076" -Body @{
        qry_tp="0"; sell_tp="0"; stex_tp="0"; stk_cd=""; ord_no=""
    } -ArrayProperty "cntr"
    if (-not $fills.Complete) { Fail-Closed "FILLED_ORDER_PAGINATION" 0 }

    $holdKrx = Get-PagedCount -ApiId "kt00018" -Body @{
        qry_tp="2"; dmst_stex_tp="KRX"
    } -ArrayProperty "acnt_evlt_remn_indv_tot"
    if (-not $holdKrx.Complete) { Fail-Closed "HOLDINGS_KRX_PAGINATION" 0 }

    $holdNxt = Get-PagedCount -ApiId "kt00018" -Body @{
        qry_tp="2"; dmst_stex_tp="NXT"
    } -ArrayProperty "acnt_evlt_remn_indv_tot"
    if (-not $holdNxt.Complete) { Fail-Closed "HOLDINGS_NXT_PAGINATION" 0 }

    @{
        STAGE="REAL_ACCOUNT_SCOPE_READ_ONLY_SMOKE"
        RETURN_CODE=0
        TOKEN_OK=$true
        ACCOUNT_ENDPOINT_OK=$true
        SETTLEMENT_ENDPOINT_OK=$true
        SETTLEMENT_FIELDS_VALID=$true
        BROKER_TODAY_ENDPOINT_OK=$true
        TRADING_DATE=$tradingDate
        TRADING_DATE_ORIGIN_ATTESTED=$true
        ORDER_HISTORY_ENDPOINT_OK=$true
        ORDER_HISTORY_COMPLETE=$true
        ORDER_HISTORY_ROWS=[int]$orders.Count
        OPEN_ORDER_ENDPOINT_OK=$true
        OPEN_ORDER_COMPLETE=$true
        OPEN_ORDER_ROWS=[int]$openOrders.Count
        FILLED_ORDER_ENDPOINT_OK=$true
        FILLED_ORDER_COMPLETE=$true
        FILLED_ORDER_ROWS=[int]$fills.Count
        HOLDINGS_KRX_ENDPOINT_OK=$true
        HOLDINGS_KRX_COMPLETE=$true
        HOLDING_ROWS_KRX=[int]$holdKrx.Count
        HOLDINGS_NXT_ENDPOINT_OK=$true
        HOLDINGS_NXT_COMPLETE=$true
        HOLDING_ROWS_NXT=[int]$holdNxt.Count
        ACCOUNT_SCOPE_BASELINE_COMPLETE=$true
        BROKER_NATIVE_ORDER_SNAPSHOT_CAPTURE_TESTED=$true
        BROKER_NATIVE_EXECUTION_ID_CAPTURE_TESTED=$false
        DURABLE_JOURNAL_BOUND=$false
        ACCOUNT_SETTLEMENT_ADMITTED=$false
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
        if ($_.Exception.Data.Contains("return_code")) {
            $code = [int]$_.Exception.Data["return_code"]
        } elseif ($null -ne $_.ErrorDetails.Message) {
            $j = $_.ErrorDetails.Message | ConvertFrom-Json
            if ($null -ne $j.return_code) { $code = [int]$j.return_code }
        }
    } catch {}
    Fail-Closed "NETWORK_OR_PROVIDER" $code
}
finally {
    $script:Token = $null
}
