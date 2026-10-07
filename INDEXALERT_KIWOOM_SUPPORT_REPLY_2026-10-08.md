# Kiwoom Open API Q&A follow-up — 2026-10-08 KST

Scope: redacted authentication interpretation only. No credentials, token values, account values, orders, fills or private broker frames are stored here.

Broker reply summary:
- Question referenced REAL WebSocket LOGIN return 805004 / embedded detail 8050 after successful token issuance and REST account lookup.
- Kiwoom replied that there is no difference between REST and WebSocket in the allowed-IP rule.
- Kiwoom asked the client to verify that the token passed to WebSocket LOGIN is not incorrect or expired.

Engineering consequence:
- Do not continue to classify this specific observed 8050 as a designated-device/IP blocker.
- Keep the blocker at TOKEN_OR_LOGIN_AUTH until a new user-operated read-only smoke narrows it.
- The smoke now emits only additional redacted facts: token canonicality, presence of token metadata fields, whether the exact freshly issued in-memory token was accepted by the REST account endpoint, whether the same issued in-memory token was then used for WebSocket LOGIN, and token age in seconds at LOGIN.
- No token value, token hash, account number, App Key/Secret, IP address, order ID, execution ID, symbol, price or quantity is emitted.
- If a fresh token is accepted by REST and used seconds later unchanged in the official LOGIN shape but 8050 persists, the next broker escalation can state that contradiction without exposing secrets.

Authority remains unchanged:
- ORDERING=DISABLED
- REAL_ORDERS_AUTHORIZED=false
- FUNDS_MOVEMENT_AUTHORIZED=false
- PERMISSION_CHANGE_AUTHORIZED=false
- GENUINE_LIVE_PROVENANCE_VERIFIED=false
