# Kiwoom type 00 realtime capture preparation — offline only

Reviewed official source tree: `953e5dbff123f437ab4d11a78a95191a685eb51f`.

`kiwoom_realtime_order_fill_subscription_contract.py` freezes the official domestic order/fill realtime registration shape for:
- WebSocket path `/api/dostk/websocket`;
- realtime type `00`;
- packet `REG` with account-level empty item list;
- the reviewed type 00 field allowlist including broker order number `9203`, execution number `909`, lifecycle time `908`, unit fill price `914` and unit fill quantity `915`.

This module is deliberately transport-free. It cannot open a WebSocket, obtain a token, subscribe, place an order, change permissions or establish genuine LIVE provenance. Even seeing a syntactically valid `909` in an offline row does not set `BROKER_NATIVE_EXECUTION_ID_CAPTURE_TESTED`.

The purpose is to remove request-shape ambiguity before a later independently reviewed, read/capture-only realtime transport is introduced. Any genuine execution-ID capture still requires authenticated broker-native observation and separate provenance admission.
