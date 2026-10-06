# Kiwoom REAL type 00 read-only WebSocket smoke

Prepared script: `kiwoom_real_type00_readonly_smoke.ps1`.

Boundary:
- fixed REAL HTTPS host `https://api.kiwoom.com`;
- fixed REAL WebSocket host `wss://api.kiwoom.com:10000/api/dostk/websocket`;
- OAuth token plus read-only `ka00001` account identity;
- WebSocket `LOGIN`;
- only realtime `REG` for type `00`;
- no order create/modify/cancel endpoint;
- ordering configuration must remain disabled.

The script retains token/account only in process memory, compares type00 field `9201` privately to the read-only account identity, and emits only booleans/counts. It never prints account number, token, order ID, execution ID, symbol, price, quantity or raw provider frame.

A syntactically/account-matched broker execution event with type00 fields `909`, `908`, `914`, `915` and order status `체결` may set `BROKER_NATIVE_EXECUTION_ID_CAPTURE_TESTED=true` for this narrow transport-capture check. Even then, `GENUINE_LIVE_PROVENANCE_VERIFIED`, order authority, funds authority and permission authority remain false. Full provenance/admission and durable journal binding remain separate gates.

This user-operated check is deferred until the owner says local actions can resume. No real order is required merely to test LOGIN/REG connectivity, although execution-ID capture cannot become true unless an eligible account execution event actually occurs during the short observation window.
