# Kiwoom Railway credential-mode evidence — 2026-10-08

## Later 2026-10-08 KST REAL authentication evidence (supersedes DEMO-key as CURRENT blocker)

Verified on the owner's registered-IP Windows machine, with the already available REAL credentials, a fresh user-operated **read-only** smoke:
- `TOKEN_OK=true`, `ACCOUNT_ENDPOINT_OK=true`, `REST_ACCOUNT_ACCEPTED_ISSUED_TOKEN=true` and `WS_CONNECTED=true`;
- `WS_LOGIN_USED_ISSUED_TOKEN=true`, `TOKEN_AGE_SECONDS_AT_WS_LOGIN=0`, token canonical/expiry/type presence all true;
- `STAGE=WS_LOGIN`, `RETURN_CODE=805004`, embedded `DETAIL_CODE=8050`, `ERROR_CLASS=TOKEN_OR_LOGIN_AUTH`;
- `WS_LOGIN_OK=false`, no type00 REG/ACK and no broker execution provenance;
- the local public IP matched the allowed IP in the owner's official REAL API registration screen, which showed a current registration. Neither the actual IP nor credentials are recorded here.
- Owner submitted the updated 8050 WebSocket authentication evidence to Kiwoom support and will supply their reply.

Separately, the isolated Railway REAL-read-only service successfully built/deployed a one-shot smoke image (`6afe4255-cb67-4f4f-93a8-bb03021935d2`), but its **application** returned `STAGE=TOKEN`, `RETURN_CODE=3`, `DETAIL_CODE=8050`, `TOKEN_OK=false`. Railway deployment `SUCCESS` is NOT token/authentication success. Source IP/credential consistency there is not independently established; values are redacted.

The earlier Railway pair of `return_code=2 / detail_code=8030` DEMO-mode results remains HISTORICAL and may not be asserted as the current state after owner variable updates. Do not demand credential re-issuance, repeating the local smoke or Railway upgrades merely from those superseded results. Do not assert IP as the proven cause of the current 8050; support response pending.

Remaining AUTH blocker: independently establish REAL WebSocket LOGIN/type00 registration before progressing. Structural GitHub CI/deployment checks do not make accepted LIVE broker/strategy evidence. `ORDERING=DISABLED`; `REAL_ORDERS_AUTHORIZED=false`; `FUNDS_MOVEMENT_AUTHORIZED=false`; `PERMISSION_CHANGE_AUTHORIZED=false`. The user's registered-IP smoke and all broker credentials are private; no keys/tokens/accounts/public IP values go to GitHub.


Historical status: **SUPERSEDED_DEMO_CREDENTIAL_PROBE_ONLY — not an active key-replacement request.** Current REAL credential and `8050` evidence is recorded above.

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

Historical interpretation at that earlier probe time: those then-stored credentials behaved as DEMO-mode credentials. This finding does **not** describe the subsequently updated REAL read-only smoke or registered-IP Windows probe. Current owner-operated REAL OAuth/account succeeded but WebSocket LOGIN returned `805004/8050`; the subsequent Railway REAL token attempt independently returned `8050` at TOKEN stage.

**Superseded historical action only (do not repeat):** earlier instructions requested replacing DEMO keys in the isolated REAL read-only service. REAL credentials were subsequently updated; the registered-IP Windows REAL token/account smoke succeeded. The pending owner action is to provide Kiwoom's official response to `8050`, not to reissue keys or modify IPs. Keep `KIWOOM_ENV=REAL`, `KIWOOM_BASE_URL=https://api.kiwoom.com`, and `KIWOOM_ORDERING_ENABLED=false`. Never paste credentials into GitHub or chat; further REAL smoke is read-only and should follow the supported fix.

Authority remains unchanged:
- ORDERING=DISABLED
- REAL_ORDERS_AUTHORIZED=false
- FUNDS_MOVEMENT_AUTHORIZED=false
- PERMISSION_CHANGE_AUTHORIZED=false
- GENUINE_LIVE_PROVENANCE_VERIFIED=false

This blocker is authentication configuration only. It is not evidence of strategy profitability, execution provenance, Shadow admission or Tiny Live authorization.
