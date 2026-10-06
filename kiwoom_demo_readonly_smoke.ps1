# User-operated Kiwoom DEMO read-only smoke.
# Fixed DEMO host. Exactly two provider calls: OAuth token + ka00001 account query.
# Never prints App Key, Secret, token, account identifiers, or provider response bodies.
$ErrorActionPreference = "Stop"

function Fail-Closed([string]$Stage) {
    @{ STAGE=$Stage; TOKEN_OK=$false; ACCOUNT_ENDPOINT_OK=$false; ORDERING="DISABLED";
       REAL_ORDERS_AUTHORIZED=$false; FUNDS_MOVEMENT_AUTHORIZED=$false;
       PERMISSION_CHANGE_AUTHORIZED=$false } | ConvertTo-Json -Compress
    exit 2
}

if ($env:KIWOOM_ENV -ne "DEMO") { Fail-Closed "CONFIG" }
if ($env:KIWOOM_BASE_URL -ne "https://mockapi.kiwoom.com") { Fail-Closed "CONFIG" }
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
        Uri = "https://mockapi.kiwoom.com/oauth2/token"
        Method = "Post"
        ContentType = "application/json;charset=UTF-8"
        Body = $tokenBody
    }
    $token = Invoke-RestMethod @tokenArgs

    if ($token.return_code -ne 0 -or [string]::IsNullOrWhiteSpace($token.token)) {
        Fail-Closed "TOKEN"
    }

    $headers = @{
        "authorization" = "Bearer $($token.token)"
        "api-id" = "ka00001"
        "cont-yn" = "N"
        "next-key" = ""
    }
    $accountArgs = @{
        Uri = "https://mockapi.kiwoom.com/api/dostk/acnt"
        Method = "Post"
        Headers = $headers
        ContentType = "application/json;charset=UTF-8"
        Body = "{}"
    }
    $account = Invoke-RestMethod @accountArgs

    if ($account.return_code -ne 0) { Fail-Closed "ACCOUNT" }

    @{
        STAGE="DEMO_READ_ONLY_SMOKE"
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
    Fail-Closed "NETWORK_OR_PROVIDER"
}
