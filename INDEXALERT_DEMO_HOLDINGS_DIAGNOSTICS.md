# Explicit DEMO holdings diagnostics

Official reviewed source: Kiwoom-Securities/Kiwoom-REST-API@953e5dbff123f437ab4d11a78a95191a685eb51f, examples/국내주식/계좌/get_domestic_account_evaluation_balance.py.

The separate CLI `python -S -B kiwoom_demo_holdings_verifier.py --execute-demo-holdings-readonly` performs explicit DEMO TLS auth, account-field lookup, then exactly kt00018 qry_tp=2 / dmst_stex_tp=KRX. Unknown/additional arguments remain dry run. The original order-snapshot verifier and Docker CMD keep their original default.

Only the fixed mock host/read-only account path is permitted; orders, amendments, cancellation, token revoke, REAL, redirects, retries and automatic auth refresh remain unavailable. Max10 pages is a workload ceiling, never a completeness criterion. Missing/empty continuation headers, caps, loops, duplicate credit/loan identities or invalid holdings quantities block the entire result. Failed/unknown holdings counts remain null, never verified zero.

Account identity, ephemeral keyed fingerprint, raw rows and valuation values stay in memory. Public output contains counts/booleans only. Credit/loan lots stay distinct; reported tradeable quantity cannot exceed held quantity. Estimated asset/valuation fees are not actual settlement, ownership or cash release evidence. Diagnostic HMAC equality is not independent broker provenance.

Actual completed job/status/source pin and safe JSON are in INDEXALERT_DEMO_HOLDINGS_VERIFIER_STATUS.json. All source-account, completeness, freshness, trading-day, automation-ownership, cash, fee, capital-release, genuine LIVE, empirical closure, sealed-holdout and live-order authorities remain false. No public runtime ledger or private PIT/KRX volume is mutated. Isolated runtime root config must not be merged into canonical worker config.
