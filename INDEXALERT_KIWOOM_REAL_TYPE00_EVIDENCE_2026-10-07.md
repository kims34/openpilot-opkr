# Kiwoom REAL type00 read-only evidence — 2026-10-07 KST

User-operated read-only smoke result, redacted by construction.

Observed result:
- STAGE: WS_LOGIN
- RETURN_CODE: 805004
- DETAIL_CODE: 8050
- ERROR_CLASS: DEVICE_AUTH
- TOKEN_OK: true
- ACCOUNT_ENDPOINT_OK: true
- WS_CONNECTED: true
- WS_LOGIN_OK: false
- TYPE00_REG_SENT: false
- TYPE00_REG_ACK_OK: false
- TYPE00_EVENT_COUNT: 0
- ACCOUNT_MATCHED_TYPE00_EVENT_COUNT: 0
- BROKER_NATIVE_EXECUTION_ID_CAPTURE_TESTED: false
- GENUINE_LIVE_PROVENANCE_VERIFIED: false
- ORDERING: DISABLED
- REAL_ORDERS_AUTHORIZED: false
- FUNDS_MOVEMENT_AUTHORIZED: false
- PERMISSION_CHANGE_AUTHORIZED: false

Interpretation:
- Real OAuth token issuance succeeded.
- Real read-only account endpoint succeeded.
- REAL WebSocket TCP/TLS connection succeeded.
- The broker rejected LOGIN with embedded detail code 8050.
- Kiwoom's current official client classifies 8050 within DEVICE_AUTH_CODES and raises DeviceAuthenticationError.
- Therefore this is an external device-authentication blocker, not evidence of an Alpha, execution, or order-authority failure.
- No order, cancel/amend, funds movement, permission change, or genuine LIVE execution evidence occurred.
- The validation remains incomplete until a later read-only rerun passes LOGIN/REG after the owner resolves broker-side designated-device authentication.

No Champion/Frozen/research/promotion state changes.
