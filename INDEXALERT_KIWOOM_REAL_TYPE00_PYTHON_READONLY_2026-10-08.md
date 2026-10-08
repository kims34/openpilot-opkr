# Kiwoom REAL type00 Python read-only smoke — Tiny Live A-blocker

Purpose: remove the dependency on a local Windows PC for the existing read-only REAL WebSocket authentication check.

The script uses only the currently documented Kiwoom REAL paths already used by the project:
- POST /oauth2/token with client_credentials;
- read-only ka00001 account-number lookup;
- wss://api.kiwoom.com:10000/api/dostk/websocket;
- LOGIN with the exact freshly issued access token;
- REG for realtime type 00 only.

It contains no order-create/amend/cancel endpoint and refuses to start unless KIWOOM_ENV=REAL, KIWOOM_BASE_URL=https://api.kiwoom.com and KIWOOM_ORDERING_ENABLED is explicitly false/off/0/no.

Output is limited to booleans, counts, stage/return/detail codes and token age. Token, App Key/Secret, account number, order/execution IDs, symbols, prices, quantities, raw provider frames and IP addresses are never emitted.

A successful LOGIN/REG closes only REAL realtime transport/authentication plumbing. It does not establish a real fill observation, genuine LIVE execution provenance, Alpha/Shadow admission or Tiny Live authorization. All order/funds/permission flags remain false.
