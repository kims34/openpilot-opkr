# Kiwoom REAL settlement read-only evidence — 2026-10-07 KST

Evidence class: **user-operated external REAL account / read-only settlement plumbing only**

A user-operated run of the repository's fixed-host REAL settlement read-only smoke completed successfully after the Windows PowerShell 5.1 compatibility fix.

Retained redacted observations:

- `TOKEN_OK=true`
- `ACCOUNT_ENDPOINT_OK=true`
- `SETTLEMENT_ENDPOINT_OK=true`
- `SETTLEMENT_FIELDS_VALID=true`
- `SOURCE_ACCOUNT_ORIGIN_AUTHENTICATED=true`
- `SNAPSHOT_FRESHNESS_ATTESTED=true`
- `TRADING_DATE_ORIGIN_ATTESTED=false`
- `ORDERING=DISABLED`
- `REAL_ORDERS_AUTHORIZED=false`
- `FUNDS_MOVEMENT_AUTHORIZED=false`
- `PERMISSION_CHANGE_AUTHORIZED=false`
- `GENUINE_LIVE_PROVENANCE_VERIFIED=false`

The locally generated account fingerprint and capture timestamp are intentionally **not** retained in the repository. App Key, App Secret, access token, full account number, cash balances and provider response bodies are also excluded.

This observation verifies only that the reviewed REAL OAuth/account/settlement read-only path returned a structurally valid settlement response in the user's session, bound to the locally authenticated account context, with a fresh local capture. It does not independently attest the broker trading date.

Therefore the composed settlement gate remains fail-closed:
- `settlement_fields_verified=true`
- `source_account_origin_authenticated=true`
- `snapshot_freshness_attested=true`
- `trading_date_origin_attested=false`
- `account_settlement_admitted=false`

No order-create, amend, cancel, revoke, funds-transfer or broker-permission action was invoked. This result does not close Shadow, genuine LIVE execution provenance/sufficiency, source/PIT/status-economics, successor Alpha, promotion, sealed-holdout or Early-Live gates.
