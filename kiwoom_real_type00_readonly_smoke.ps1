# User-operated Kiwoom REAL type00 read-only WebSocket smoke.
# Fixed REAL hosts. OAuth + ka00001 read-only account identity + WebSocket LOGIN/REG type00 only.
# No order-create/amend/cancel/revoke, no funds movement, no permission change.
# Output is booleans/counts only; never prints token, account, order IDs, symbols, prices, quantities or provider bodies.
$ErrorActionPreference = "Stop"

function Emit-Failure([string]$Stage, [int]$Code = -1) {
    @{
        STAGE=$Stage
        RETURN_CODE=$Code
        TOKEN_OK=$false
        ACCOUNT_ENDPOINT_OK=$false
        WS_CONNECTED=$false
        WS_LOGIN_OK=$false
        TYPE00_REG_SENT=$false
        TYPE00_REG_ACK_OK=$false
        TYPE00_EVENT_COUNT=0
        ACCOUNT_MATCHED_TYPE00_EVENT_COUNT=0
        BROKER_NATIVE_EXECUTION_ID_CAPTURE_TESTED=$false
        GENUINE_LIVE_PROVENANCE_VERIFIED=$false
        ORDERING="DISABLED"
        REAL_ORDERS_AUTHORIZED=$false
        FUNDS_MOVEMENT_AUTHORIZED=$false
        PERMISSION_CHANGE_AUTHORIZED=$false
    } | ConvertTo-Json -Compress
    exit 2
}

function Send-Text([System.Net.WebSockets.ClientWebSocket]$Ws, [string]$Text) {
    $bytes = [System.Text.Encoding]::UTF8.GetBytes($Text)
    $segment = New-Object 'System.ArraySegment[byte]' -ArgumentList (, $bytes)
    $cts = New-Object System.Threading.CancellationTokenSource
    try {
        $cts.CancelAfter(5000)
        $Ws.SendAsync($segment, [System.Net.WebSockets.WebSocketMessageType]::Text, $true, $cts.Token).GetAwaiter().GetResult()
    } finally {
        $cts.Dispose()
    }
}

function Receive-Text([System.Net.WebSockets.ClientWebSocket]$Ws, [int]$TimeoutMs) {
    $buffer = New-Object byte[] 8192
    $stream = New-Object System.IO.MemoryStream
    $cts = New-Object System.Threading.CancellationTokenSource
    try {
        $cts.CancelAfter($TimeoutMs)
        do {
            $segment = New-Object 'System.ArraySegment[byte]' -ArgumentList (, $buffer)
            $result = $Ws.ReceiveAsync($segment, $cts.Token).GetAwaiter().GetResult()
            if ($result.MessageType -eq [System.Net.WebSockets.WebSocketMessageType]::Close) {
                return $null
            }
            if ($result.MessageType -ne [System.Net.WebSockets.WebSocketMessageType]::Text) {
                throw "NON_TEXT_WEBSOCKET_FRAME"
            }
            if ($result.Count -gt 0) {
                $stream.Write($buffer, 0, $result.Count)
            }
            if ($stream.Length -gt 1048576) {
                throw "WEBSOCKET_FRAME_TOO_LARGE"
            }
        } while (-not $result.EndOfMessage)
        return [System.Text.Encoding]::UTF8.GetString($stream.ToArray())
    } finally {
        $stream.Dispose()
        $cts.Dispose()
    }
}

function Is-Ping([object]$Obj, [string]$Raw) {
    if ($Raw.Trim().ToUpperInvariant() -eq "PING") { return $true }
    if ($null -ne $Obj -and [string]$Obj.trnm -ne "") {
        return ([string]$Obj.trnm).ToUpperInvariant() -eq "PING"
    }
    return $false
}

function Send-PingEcho([System.Net.WebSockets.ClientWebSocket]$Ws, [string]$Raw) {
    Send-Text -Ws $Ws -Text $Raw
}

if ($env:KIWOOM_ENV -ne "REAL") { Emit-Failure "CONFIG" }
if ($env:KIWOOM_BASE_URL -ne "https://api.kiwoom.com") { Emit-Failure "CONFIG" }
if ($env:KIWOOM_ORDERING_ENABLED -notin @("0","false","off","no")) { Emit-Failure "CONFIG" }
if ([string]::IsNullOrWhiteSpace($env:KIWOOM_APP_KEY) -or [string]::IsNullOrWhiteSpace($env:KIWOOM_APP_SECRET)) { Emit-Failure "CONFIG" }

$ws = $null
$script:Token = $null
$script:Account = $null
try {
    $tokenBody = @{ grant_type="client_credentials"; appkey=$env:KIWOOM_APP_KEY; secretkey=$env:KIWOOM_APP_SECRET } | ConvertTo-Json -Compress
    $tokenResp = Invoke-RestMethod -Uri "https://api.kiwoom.com/oauth2/token" -Method Post -ContentType "application/json;charset=UTF-8" -Body $tokenBody
    if ($tokenResp.return_code -ne 0 -or [string]::IsNullOrWhiteSpace([string]$tokenResp.token)) {
        Emit-Failure "TOKEN" ([int]$tokenResp.return_code)
    }
    $script:Token = [string]$tokenResp.token

    $headers = @{ authorization="Bearer $script:Token"; "api-id"="ka00001"; "cont-yn"="N"; "next-key"="" }
    $accountResp = Invoke-WebRequest -UseBasicParsing -Uri "https://api.kiwoom.com/api/dostk/acnt" -Method Post -Headers $headers -ContentType "application/json;charset=UTF-8" -Body "{}"
    $accountObj = $accountResp.Content | ConvertFrom-Json
    if ($accountObj.return_code -ne 0 -or [string]::IsNullOrWhiteSpace([string]$accountObj.acctNo)) {
        Emit-Failure "ACCOUNT" ([int]$accountObj.return_code)
    }
    $script:Account = [string]$accountObj.acctNo

    $ws = New-Object System.Net.WebSockets.ClientWebSocket
    $connectCts = New-Object System.Threading.CancellationTokenSource
    try {
        $connectCts.CancelAfter(10000)
        $ws.ConnectAsync([Uri]"wss://api.kiwoom.com:10000/api/dostk/websocket", $connectCts.Token).GetAwaiter().GetResult()
    } finally {
        $connectCts.Dispose()
    }
    if ($ws.State -ne [System.Net.WebSockets.WebSocketState]::Open) { Emit-Failure "WS_CONNECT" 0 }

    Send-Text -Ws $ws -Text (@{ trnm="LOGIN"; token=$script:Token } | ConvertTo-Json -Compress)
    $loginOk = $false
    for ($i=0; $i -lt 10 -and -not $loginOk; $i++) {
        $raw = Receive-Text -Ws $ws -TimeoutMs 5000
        if ($null -eq $raw) { Emit-Failure "WS_LOGIN_CLOSED" 0 }
        $obj = $null
        try { $obj = $raw | ConvertFrom-Json } catch {}
        if (Is-Ping -Obj $obj -Raw $raw) {
            Send-PingEcho -Ws $ws -Raw $raw
            continue
        }
        if ($null -eq $obj -or ([string]$obj.trnm).ToUpperInvariant() -ne "LOGIN") {
            Emit-Failure "WS_LOGIN_PROTOCOL" 0
        }
        $code = 0
        if ($null -ne $obj.return_code) { $code = [int]$obj.return_code }
        if ($code -ne 0) { Emit-Failure "WS_LOGIN" $code }
        $loginOk = $true
    }
    if (-not $loginOk) { Emit-Failure "WS_LOGIN_TIMEOUT" 0 }

    $reg = @{
        trnm="REG"
        grp_no="1"
        refresh="1"
        data=@(@{ item=@(); type=@("00") })
    } | ConvertTo-Json -Compress -Depth 5
    Send-Text -Ws $ws -Text $reg

    $regAck = $false
    $events = 0
    $accountMatched = 0
    $executionObserved = $false
    $deadline = [DateTimeOffset]::UtcNow.AddSeconds(8)
    while ([DateTimeOffset]::UtcNow -lt $deadline) {
        $remaining = [int][Math]::Max(250, [Math]::Min(2000, ($deadline - [DateTimeOffset]::UtcNow).TotalMilliseconds))
        try {
            $raw = Receive-Text -Ws $ws -TimeoutMs $remaining
        } catch [System.OperationCanceledException] {
            continue
        } catch [System.Threading.Tasks.TaskCanceledException] {
            continue
        }
        if ($null -eq $raw) { break }
        $obj = $null
        try { $obj = $raw | ConvertFrom-Json } catch { continue }
        if (Is-Ping -Obj $obj -Raw $raw) {
            Send-PingEcho -Ws $ws -Raw $raw
            continue
        }
        $trnm = ([string]$obj.trnm).ToUpperInvariant()
        if ($trnm -eq "REG") {
            $code = 0
            if ($null -ne $obj.return_code) { $code = [int]$obj.return_code }
            if ($code -ne 0) { Emit-Failure "TYPE00_REG" $code }
            $regAck = $true
            continue
        }
        if ($trnm -ne "REAL") { continue }
        foreach ($entry in @($obj.data)) {
            if ($null -eq $entry -or [string]$entry.type -ne "00") { continue }
            $values = $entry.values
            if ($null -eq $values) { continue }
            $events++
            if ([string]$values.'9201' -eq $script:Account) {
                $accountMatched++
                if (([string]$values.'913' -eq "체결") -and
                    -not [string]::IsNullOrWhiteSpace([string]$values.'909') -and
                    -not [string]::IsNullOrWhiteSpace([string]$values.'908') -and
                    -not [string]::IsNullOrWhiteSpace([string]$values.'914') -and
                    -not [string]::IsNullOrWhiteSpace([string]$values.'915')) {
                    $executionObserved = $true
                }
            }
        }
    }

    if (-not $regAck -and $events -eq 0) { Emit-Failure "TYPE00_SUBSCRIPTION_UNOBSERVED" 0 }

    @{
        STAGE="REAL_TYPE00_READ_ONLY_SMOKE"
        RETURN_CODE=0
        TOKEN_OK=$true
        ACCOUNT_ENDPOINT_OK=$true
        WS_CONNECTED=$true
        WS_LOGIN_OK=$true
        TYPE00_REG_SENT=$true
        TYPE00_REG_ACK_OK=$regAck
        TYPE00_EVENT_COUNT=[int]$events
        ACCOUNT_MATCHED_TYPE00_EVENT_COUNT=[int]$accountMatched
        BROKER_NATIVE_EXECUTION_ID_CAPTURE_TESTED=[bool]$executionObserved
        GENUINE_LIVE_PROVENANCE_VERIFIED=$false
        ORDERING="DISABLED"
        REAL_ORDERS_AUTHORIZED=$false
        FUNDS_MOVEMENT_AUTHORIZED=$false
        PERMISSION_CHANGE_AUTHORIZED=$false
    } | ConvertTo-Json -Compress
}
catch {
    Emit-Failure "LOCAL_COMPATIBILITY_OR_NETWORK" -1
}
finally {
    if ($null -ne $ws) {
        try {
            if ($ws.State -eq [System.Net.WebSockets.WebSocketState]::Open) {
                $closeCts = New-Object System.Threading.CancellationTokenSource
                try {
                    $closeCts.CancelAfter(3000)
                    $ws.CloseAsync([System.Net.WebSockets.WebSocketCloseStatus]::NormalClosure, "read-only smoke complete", $closeCts.Token).GetAwaiter().GetResult()
                } finally {
                    $closeCts.Dispose()
                }
            }
        } catch {}
        $ws.Dispose()
    }
    $script:Account = $null
    $script:Token = $null
}
