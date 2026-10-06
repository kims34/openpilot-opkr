# Kiwoom REAL whole-account read-only scope evidence — 2026-10-07

User-operated observation from the fixed-host read-only boundary. This record intentionally excludes credentials, token, full account number, account fingerprint, balances, symbols, order IDs, prices, quantities, holdings rows, and provider response bodies.

Observed result:
- STAGE: REAL_ACCOUNT_SCOPE_READ_ONLY_SMOKE
- RETURN_CODE: 0
- TOKEN_OK: true
- ACCOUNT_ENDPOINT_OK: true
- SETTLEMENT_ENDPOINT_OK: true
- SETTLEMENT_FIELDS_VALID: true
- BROKER_TODAY_ENDPOINT_OK: true
- TRADING_DATE_ORIGIN_ATTESTED: true
- TRADING_DATE: 2026-10-07
- ORDER_HISTORY_ENDPOINT_OK: true
- ORDER_HISTORY_COMPLETE: true
- ORDER_HISTORY_ROWS: 0
- OPEN_ORDER_ENDPOINT_OK: true
- OPEN_ORDER_COMPLETE: true
- OPEN_ORDER_ROWS: 0
- FILLED_ORDER_ENDPOINT_OK: true
- FILLED_ORDER_COMPLETE: true
- FILLED_ORDER_ROWS: 0
- HOLDINGS_KRX_ENDPOINT_OK: true
- HOLDINGS_KRX_COMPLETE: true
- HOLDING_ROWS_KRX: 0
- HOLDINGS_NXT_ENDPOINT_OK: true
- HOLDINGS_NXT_COMPLETE: true
- HOLDING_ROWS_NXT: 0
- ACCOUNT_SCOPE_BASELINE_COMPLETE: true
- BROKER_NATIVE_ORDER_SNAPSHOT_CAPTURE_TESTED: true

Still false / not established:
- BROKER_NATIVE_EXECUTION_ID_CAPTURE_TESTED: false
- DURABLE_JOURNAL_BOUND: false
- ACCOUNT_SETTLEMENT_ADMITTED: false
- GENUINE_LIVE_PROVENANCE_VERIFIED: false
- REAL_ORDERS_AUTHORIZED: false
- FUNDS_MOVEMENT_AUTHORIZED: false
- PERMISSION_CHANGE_AUTHORIZED: false
- ORDERING: DISABLED

Interpretation: the REAL read-only account-scope baseline succeeded for the observed trading date and returned a complete zero-row account baseline across reviewed order/fill/holding queries. This is connectivity/scope evidence only. It does not prove execution-ID capture, durable journal binding, genuine LIVE provenance, settlement admission, or any order/funds/permission authority.
