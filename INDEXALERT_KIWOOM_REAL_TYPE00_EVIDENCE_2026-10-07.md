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
- A Kiwoom Open API Q&A reply received 2026-10-08 states that REST and WebSocket do not have different allowed-IP rules and asks the client to check whether the LOGIN token is incorrect or expired.
- Therefore the prior local DEVICE_AUTH interpretation is superseded for this observed 8050. The safe classification is TOKEN_OR_LOGIN_AUTH until a fresh-token rerun resolves the discrepancy.
- The official Kiwoom WebSocket guide uses the raw issued access token in the LOGIN packet, while REST uses the same access token as a Bearer token. The existing smoke already follows that shape.
- This remains an authentication-path blocker, not evidence of an Alpha, execution, or order-authority failure.
- No order, cancel/amend, funds movement, permission change, or genuine LIVE execution evidence occurred.
- The validation remains incomplete until a later read-only rerun records the new redacted fresh-token diagnostics and passes LOGIN/REG, or produces enough evidence for a narrower broker escalation.

No Champion/Frozen/research/promotion state changes.
