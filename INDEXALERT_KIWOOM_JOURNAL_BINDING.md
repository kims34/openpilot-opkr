# Offline Kiwoom normalized-source journal bridge

This is offline development plumbing, not broker/account source admission or an order-capable adapter. Frozen research/execution criteria, cutoff and holdout stay unchanged. No provider requests, credentials, actual orders, cash movements or production integration.

## Official reviewed schema
The existing pinned Kiwoom source tree is953e5dbff123f437ab4d11a78a95191a685eb51f in Kiwoom-Securities/Kiwoom-REST-API. Re-read official blob81c1d7ea1900b092ea417c67bc42d019edf81255 (examples/국내주식/실시간시세/subscribe_domestic_order_fill_async.py). Its column labels identify909 as execution number,915 as unit fill quantity,914 as unit fill price and938/939 as daily trading fee/tax. Daily totals must not be summed as per-execution costs.

## Implemented scope and behaviour
- One journal retains one declared account fingerprint/trading date across restart. Switching either rejects and blocks diagnostics. Normalized rows have no raw account number and type00 times have no date: this bridge cannot authenticate those external scope declarations. It never grants LIVE admission.
- Bind an existing claimed/acknowledged order identity and explicit native side code. Native side semantics are not independently attested; no unknown broker code is automatically mapped to BUY/SELL.
- Validate pinned source contract/schema/API/granularity and strict non-admission markers, account/day/order/symbol/submitted quantity/raw-side equality, native execution ID, exact integer quantity, positive price and valid HHMMSS.
- Require both reported and unit quantity/price to agree. Missing or ambiguous unit semantics reject instead of treating a cumulative amount as another execution. Amend/original-order chains are intentionally not auto-mapped.
- New native executions and private source bindings commit atomically. Exact duplicates are idempotent after later fills/restart and under concurrent workers; conflicting economics/time/scope quarantine without rewriting quantities.
- Enforce current quantity/remaining consistency; out-of-order or missing fills stay blocked until the missing native records are supplied. The caller must retain/replay source records; this bridge does not collect/store an authoritative raw inbox.
- REST kt00007/ka10076 rows compare identity and aggregate/remaining quantities to existing journal fills only. They never create executions, clear uncertainty or admit a whole-account snapshot. Status/direction/fee/price semantics and actual account completeness remain outside that comparison.
- Source conflicts persist MASTER_OFF, quarantine claimed intents, set the durable batch barrier and remove settlement snapshot bindings. Reports/errors omit private identifiers; all origin/admission/cash-settlement flags stay false.

## Verification and remaining work
20 new bridge tests plus existing87 safety and16 native-normalizer cases pass locally:123 total. Cases include aggregate-as-fill rejection, source drift, self-LIVE flags, duplicate conflicts, missing/ambiguous unit fields, account/day mismatch, restart, gap recovery, native-binding transaction abort and concurrent duplicates. No private dataset, market/provider request or strategy/holdout path used.

Still required: independently admitted raw account/date/side/event provenance and completeness, raw-source inbox/replay/admission, amend/cancel chain semantics, actual partial/full-fill asset/fee/tax/sale settlement, frozen pretrade/risk checks and permitted actual broker/Kill/cancel integration. Technical binding success does not close any source/performance/LIVE gate.
