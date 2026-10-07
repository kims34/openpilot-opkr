# User-operated Kiwoom REAL type00 read-only WebSocket smoke.
# Fixed REAL hosts. OAuth + ka00001 read-only account identity + WebSocket LOGIN/REG type00 only.
# No order-create/amend/cancel/revoke, no funds movement, no permission change.
# Output is booleans/counts only; never prints token, account, order IDs, symbols, prices, quantities or provider bodies.
$ErrorActionPreference = "Stop"

$script:TokenOk = $false
$script:AccountEndpointOk = $false
$script:WsConnected = $false
$script:WsLoginOk = $false
$script:Type00RegSent = $false
$script:Type00RegAckOk = $false
$script:DetailCode = $null
$script:ErrorClass = $null

function Set-SanitizedErrorDetail([object]$Message) {
    $text = [string]$Message
    $m = [regex]::Match($text, '(?:\[|CODE=)(\d{3,5})(?::|\b)')
    if ($m.Success) {
        $script:DetailCode = [int]$m.Groups[1].Value
        switch ($script:DetailCode) {
            { $_ -in 8001,8002,8011,8012 } { $script:ErrorClass = "INVALID_CREDENTIALS"; break }
            { $_ -in 8003,8005,8006,8009,8015,8016 } { $script:ErrorClass = "INVALID_TOKEN"; break }
            { $_ -in 8030,8031 } { $script:ErrorClass = "MODE_MISMATCH"; break }
            { $_ -in 8010,8040,8050,8103 } { $script:ErrorClass = "DEVICE_AUTH"; break }
            default { $script:ErrorClass = "UNCLASSIFIED" }
        }
    }
}

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

function Get-Type00ReadOnlyObservation([object]$Message, [string]$Account) {
    try {
        if ($Message -isnot [Management.Automation.PSCustomObject] -or
            $Message.trnm -isnot [string] -or $Message.trnm.ToUpperInvariant() -ne 'REAL' -or
            $Message.data -isnot [array] -or [string]::IsNullOrWhiteSpace($Account)) { throw 'invalid' }
        $allowed = @('9201','9203','9205','9001','912','913','302','900','901','902','903',
                     '904','905','906','907','908','909','910','911','10','27','28','914',
                     '915','938','939','919','920','921','922','923','10010','2134','2135','2136')
        $events = 0; $matched = 0; $execution = $false
        foreach ($entry in $Message.data) {
            if ($entry -isnot [Management.Automation.PSCustomObject] -or $entry.type -isnot [string]) { throw 'invalid' }
            if ($entry.type -ne '00') { continue }
            $values = $entry.values
            if ($values -isnot [Management.Automation.PSCustomObject]) { throw 'invalid' }
            foreach ($property in $values.PSObject.Properties) {
                if ($property.Name -cnotin $allowed -or $property.Value -isnot [string] -or $property.Value.Length -gt 4096) { throw 'invalid' }
            }
            $events++
            if ($values.'9201' -ceq $Account) {
                $matched++
                if ($values.'913' -ceq ([string][char]0xCCB4 + [char]0xACB0) -and
                    -not [string]::IsNullOrWhiteSpace($values.'909') -and
                    -not [string]::IsNullOrWhiteSpace($values.'908') -and
                    -not [string]::IsNullOrWhiteSpace($values.'914') -and
                    -not [string]::IsNullOrWhiteSpace($values.'915')) { $execution = $true }
            }
        }
        return @{ Events=$events; Matched=$matched; ExecutionFieldsObserved=$execution }
    } catch { throw 'TYPE00_FRAME_SCHEMA_INVALID' }
}

function Emit-Failure([string]$Stage, [int]$Code = -1) {
    @{
        STAGE=$Stage
        RETURN_CODE=$Code
        DETAIL_CODE=$script:DetailCode
        ERROR_CLASS=$script:ErrorClass
        TOKEN_OK=$script:TokenOk
        ACCOUNT_ENDPOINT_OK=$script:AccountEndpointOk
        WS_CONNECTED=$script:WsConnected
        WS_LOGIN_OK=$script:WsLoginOk
        TYPE00_REG_SENT=$script:Type00RegSent
        TYPE00_REG_ACK_OK=$script:Type00RegAckOk
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
        $null = $Ws.SendAsync($segment, [System.Net.WebSockets.WebSocketMessageType]::Text, $true, $cts.Token).GetAwaiter().GetResult()
    } finally {
        $cts.Dispose()
    }
}

function Convert-StrictWebSocketText([byte[]]$Bytes) {
    try {
        $utf8 = New-Object System.Text.UTF8Encoding -ArgumentList $false, $true
        return $utf8.GetString($Bytes)
    } catch {
        throw "WEBSOCKET_UTF8_INVALID"
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
        return Convert-StrictWebSocketText -Bytes $stream.ToArray()
    } finally {
        $stream.Dispose()
        $cts.Dispose()
    }
}

function Get-ReadOnlyMessageName([object]$Message) {
    if ($Message -isnot [Management.Automation.PSCustomObject] -or
        $Message.trnm -isnot [string] -or [string]::IsNullOrWhiteSpace($Message.trnm)) {
        throw 'READ_ONLY_MESSAGE_NAME_INVALID'
    }
    return $Message.trnm.ToUpperInvariant()
}

function Is-Ping([object]$Obj, [string]$Raw) {
    if ($Raw.Trim().ToUpperInvariant() -eq "PING") { return $true }
    if ($null -ne $Obj) {
        try { return (Get-ReadOnlyMessageName -Message $Obj) -eq "PING" }
        catch { return $false }
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
    $tokenWire = Invoke-WebRequest -UseBasicParsing -Uri "https://api.kiwoom.com/oauth2/token" -Method Post -ContentType "application/json;charset=UTF-8" -Body $tokenBody
    try {
        $tokenResp = Convert-ReadOnlyJson -Raw $tokenWire.Content
        $tokenCode = Get-ReadOnlyReturnCode -Message $tokenResp -Raw $tokenWire.Content -ControlFrame $false
    } catch { Emit-Failure "TOKEN_PROTOCOL" }
    if ($tokenCode -ne 0 -or $tokenResp.token -isnot [string] -or [string]::IsNullOrWhiteSpace($tokenResp.token)) {
        Emit-Failure "TOKEN" $tokenCode
    }
    $script:Token = [string]$tokenResp.token
    $script:TokenOk = $true

    $headers = @{ authorization="Bearer $script:Token"; "api-id"="ka00001"; "cont-yn"="N"; "next-key"="" }
    $accountResp = Invoke-WebRequest -UseBasicParsing -Uri "https://api.kiwoom.com/api/dostk/acnt" -Method Post -Headers $headers -ContentType "application/json;charset=UTF-8" -Body "{}"
    try {
        $accountObj = Convert-ReadOnlyJson -Raw $accountResp.Content
        $accountCode = Get-ReadOnlyReturnCode -Message $accountObj -Raw $accountResp.Content -ControlFrame $false
    } catch { Emit-Failure "ACCOUNT_PROTOCOL" }
    if ($accountCode -ne 0 -or $accountObj.acctNo -isnot [string] -or [string]::IsNullOrWhiteSpace($accountObj.acctNo)) {
        Emit-Failure "ACCOUNT" $accountCode
    }
    $script:Account = [string]$accountObj.acctNo
    $script:AccountEndpointOk = $true

    $ws = New-Object System.Net.WebSockets.ClientWebSocket
    $connectCts = New-Object System.Threading.CancellationTokenSource
    try {
        $connectCts.CancelAfter(10000)
        $null = $ws.ConnectAsync([Uri]"wss://api.kiwoom.com:10000/api/dostk/websocket", $connectCts.Token).GetAwaiter().GetResult()
    } finally {
        $connectCts.Dispose()
    }
    if ($ws.State -ne [System.Net.WebSockets.WebSocketState]::Open) { Emit-Failure "WS_CONNECT" 0 }
    $script:WsConnected = $true

    Send-Text -Ws $ws -Text (@{ trnm="LOGIN"; token=$script:Token } | ConvertTo-Json -Compress)
    $loginOk = $false
    for ($i=0; $i -lt 10 -and -not $loginOk; $i++) {
        $raw = Receive-Text -Ws $ws -TimeoutMs 5000
        if ($null -eq $raw) { Emit-Failure "WS_LOGIN_CLOSED" 0 }
        $obj = $null
        try { $obj = Convert-ReadOnlyJson -Raw $raw } catch {}
        if (Is-Ping -Obj $obj -Raw $raw) {
            Send-PingEcho -Ws $ws -Raw $raw
            continue
        }
        try { $name = Get-ReadOnlyMessageName -Message $obj }
        catch { Emit-Failure "WS_LOGIN_PROTOCOL" }
        if ($name -ne "LOGIN") {
            Emit-Failure "WS_LOGIN_PROTOCOL" 0
        }
        try { $code = Get-ReadOnlyReturnCode -Message $obj -Raw $raw }
        catch { Emit-Failure "WS_LOGIN_PROTOCOL" }
        if ($code -ne 0) { Set-SanitizedErrorDetail $obj.return_msg; Emit-Failure "WS_LOGIN" $code }
        $loginOk = $true
    }
    if (-not $loginOk) { Emit-Failure "WS_LOGIN_TIMEOUT" 0 }
    $script:WsLoginOk = $true

    $reg = @{
        trnm="REG"
        grp_no="1"
        refresh="1"
        data=@(@{ item=@(); type=@("00") })
    } | ConvertTo-Json -Compress -Depth 5
    Send-Text -Ws $ws -Text $reg
    $script:Type00RegSent = $true

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
            # TaskCanceledException derives from OperationCanceledException.
            # A second TaskCanceledException catch is rejected by Windows PowerShell
            # as already handled, so the base cancellation type is intentionally
            # the single timeout handler here.
            continue
        }
        if ($null -eq $raw) { break }
        $obj = $null
        try { $obj = Convert-ReadOnlyJson -Raw $raw } catch {}
        if (Is-Ping -Obj $obj -Raw $raw) {
            Send-PingEcho -Ws $ws -Raw $raw
            continue
        }
        try { $trnm = Get-ReadOnlyMessageName -Message $obj }
        catch { Emit-Failure "TYPE00_JSON_PROTOCOL" }
        if ($trnm -eq "REG") {
            try { $code = Get-ReadOnlyReturnCode -Message $obj -Raw $raw }
            catch { Emit-Failure "TYPE00_REG_PROTOCOL" }
            if ($code -ne 0) { Set-SanitizedErrorDetail $obj.return_msg; Emit-Failure "TYPE00_REG" $code }
            $regAck = $true
            $script:Type00RegAckOk = $true
            continue
        }
        if ($trnm -ne "REAL") { continue }
        try { $observation = Get-Type00ReadOnlyObservation -Message $obj -Account $script:Account }
        catch { Emit-Failure "TYPE00_FRAME_PROTOCOL" }
        $events += $observation.Events
        $accountMatched += $observation.Matched
        $executionObserved = $executionObserved -or $observation.ExecutionFieldsObserved
    }

    if (-not $regAck) { Emit-Failure "TYPE00_SUBSCRIPTION_UNOBSERVED" 0 }

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
                    $null = $ws.CloseAsync([System.Net.WebSockets.WebSocketCloseStatus]::NormalClosure, "read-only smoke complete", $closeCts.Token).GetAwaiter().GetResult()
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
