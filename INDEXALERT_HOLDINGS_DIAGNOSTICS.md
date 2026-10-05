# Private offline holdings diagnostics

kt00018 official primary source examples/국내주식/계좌/get_domestic_account_evaluation_balance.py was actually reviewed at Kiwoom-Securities/Kiwoom-REST-API commit953e5dbff123f437ab4d11a78a95191a685eb51f. This module adds no API to the transport allowlist and makes no request.

Validate declared account fingerprint and timezone-bearing capture time without attesting origin or freshness. Preserve exact broker symbol and separate credit/loan lots; require integer nonnegative held/tradeable quantities, tradeable<=held, valid nonnegative valuation amount, no duplicate lot, no unknown/private account fields. Return a process-private view; repr/report omit account, symbol, timestamp and values. Drop names and valuation/estimated fee-tax fields. Input is unchanged. Empty rows do not establish verified zero account positions or completeness.

This view cannot establish automation ownership, reusable cash, realized PnL, executed fees/tax, settled sale proceeds, full/fresh account snapshot, source admission or trading authority. Never substitute kt00018 estimated fees for per-execution or settled costs. All authority markers false.

Validation:8 new synthetic offline cases; full local206 tests passed. Future work requires complete paginated snapshot capture, independent account/day scope, ownership lots, official settlement linkage and existing frozen risk gates. Additional actual request scopes remain unactivated.
