# Kiwoom Railway credential-mode evidence — 2026-10-08

Status: **BLOCKED_USER_CREDENTIAL_REPLACEMENT — REAL credentials are not present in the Railway REAL read-only services.**

Tiny Live priority: A — broker REAL account/authentication/order-transport prerequisite.

Two independent Railway services were probed without changing or exposing their stored credential values:

1. `indexalert-kiwoom-real-readonly-run`
2. `indexalert-kiwoom-real-readonly`

The probe performs OAuth client-credentials token issuance only against Kiwoom's official REAL and DEMO hosts using the same already-stored in-memory credentials. It emits booleans and numeric return/detail codes only. It never emits App Key, App Secret, access token, account number, IP address, provider return message, symbol, order or execution data.

Observed in both services:

- DEMO (`https://mockapi.kiwoom.com/oauth2/token`):
  - HTTP 200
  - return_code = 0
  - token_present = true
  - expiry_present = true
  - token_type_present = true

- REAL (`https://api.kiwoom.com/oauth2/token`):
  - HTTP 200
  - return_code = 2
  - detail_code = 8030
  - token_present = false
  - expiry_present = false
  - token_type_present = false

Interpretation: the credentials currently stored in both Railway services are DEMO-mode credentials, not REAL-mode credentials. The previously observed REAL WebSocket 8050 path cannot be retested from Railway until actual REAL App Key/Secret values are placed into the REAL read-only service.

Required user action:
- In Railway, replace only `KIWOOM_APP_KEY` and `KIWOOM_APP_SECRET` for the REAL read-only service with the broker-issued REAL OpenAPI credentials.
- Keep `KIWOOM_ENV=REAL`, `KIWOOM_BASE_URL=https://api.kiwoom.com`, and `KIWOOM_ORDERING_ENABLED=false`.
- Do not paste credentials into GitHub or chat.

After that change, rerun the existing one-shot REAL read-only smoke. The smoke is limited to token issuance, read-only account lookup, WebSocket LOGIN and type00 REG.

Authority remains unchanged:
- ORDERING=DISABLED
- REAL_ORDERS_AUTHORIZED=false
- FUNDS_MOVEMENT_AUTHORIZED=false
- PERMISSION_CHANGE_AUTHORIZED=false
- GENUINE_LIVE_PROVENANCE_VERIFIED=false

This blocker is authentication configuration only. It is not evidence of strategy profitability, execution provenance, Shadow admission or Tiny Live authorization.
