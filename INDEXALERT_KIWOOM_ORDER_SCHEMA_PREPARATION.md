# Kiwoom order-capable schema preparation — offline only

Reviewed official Kiwoom source tree: `953e5dbff123f437ab4d11a78a95191a685eb51f`.

The repository now contains `kiwoom_order_request_contract.py`, a pure offline request-envelope builder for the reviewed domestic-stock order schemas:
- `kt10000` buy
- `kt10001` sell
- `kt10002` modify
- `kt10003` cancel
- path `/api/dostk/ordr`.

The module has no HTTP client, token handling, credentials, account discovery, broker connection or send method. Every result keeps broker request sent=false and real order/funds/permission authority=false. Its purpose is to freeze and test field-level request semantics before any separately reviewed activation-stage adapter exists.

This is not permission to submit, amend or cancel a real order. A later network adapter must remain absent/disabled until all governing admission gates are satisfied and the owner gives separate explicit authorization immediately before real-account ordering is enabled.
