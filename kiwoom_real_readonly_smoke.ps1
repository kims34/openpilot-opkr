# User-operated Kiwoom REAL read-only smoke.
# Fixed REAL host. Exactly two provider calls: OAuth token + ka00001 account query.
# Never prints App Key, Secret, token, account identifiers, or provider response bodies.
$ErrorActionPreference = "Stop"

function Fail-Closed([string]$Stage, [int]$Code = -1) {
    @{
        STAGE=$Stage
        RETURN_CODE=$Code
        TOKEN_OK=$false
        ACCOUNT_ENDPOINT_OK=$false
        ORDERING="DISABLED"
        REAL_ORDERS_AUTHORIZED=$false
        FUNDS_MOVEMENT_AUTHORIZED=$false
        PERMISSION_CHANGE_AUTHORIZED=$false
        GENUINE_LIVE_PROVENANCE_VERIFIED=$false
    } | ConvertTo-Json -Compress
    exit 2
}

if ($env:KIWOOM_ENV -ne "REAL") { Fail-Closed "CONFIG" }
if ($env:KIWOOM_BASE_URL -ne "https://api.kiwoom.com") { Fail-Closed "CONFIG" }
if ($env:KIWOOM_ORDERING_ENABLED -notin @("0","false","off","no")) { Fail-Closed "CONFIG" }
if ([string]::IsNullOrWhiteSpace($env:KIWOOM_APP_KEY) -or
    [string]::IsNullOrWhiteSpace($env:KIWOOM_APP_SECRET)) { Fail-Closed "CONFIG" }

try {
    $tokenBody = @{
        grant_type = "client_credentials"
        appkey = $env:KIWOOM_APP_KEY
        secretkey = $env:KIWOOM_APP_SECRET
    } | ConvertTo-Json -Compress

    $tokenArgs = @{
        Uri = "https://api.kiwoom.com/oauth2/token"
        Method = "Post"
        ContentType = "application/json;charset=UTF-8"
        Body = $tokenBody
    }
    $token = Invoke-RestMethod @tokenArgs

    if ($token.return_code -ne 0 -or [string]::IsNullOrWhiteSpace($token.token)) {
        Fail-Closed "TOKEN" ([int]$token.return_code)
    }

    $headers = @{
        "authorization" = "Bearer $($token.token)"
        "api-id" = "ka00001"
        "cont-yn" = "N"
        "next-key" = ""
    }

    $accountArgs = @{
        Uri = "https://api.kiwoom.com/api/dostk/acnt"
        Method = "Post"
        Headers = $headers
        ContentType = "application/json;charset=UTF-8"
        Body = "{}"
    }
    $account = Invoke-RestMethod @accountArgs

    if ($account.return_code -ne 0) {
        Fail-Closed "ACCOUNT" ([int]$account.return_code)
    }

    @{
        STAGE="REAL_READ_ONLY_SMOKE"
        RETURN_CODE=0
        TOKEN_OK=$true
        ACCOUNT_ENDPOINT_OK=$true
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
