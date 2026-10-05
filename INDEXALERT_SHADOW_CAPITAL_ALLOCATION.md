# Offline durable capital allocation

This module couples existing user-ceiling validation to a durable local SHADOW claim under one SQLite BEGIN IMMEDIATE transaction. It does not authorize broker requests, strategy execution, genuine LIVE evidence or production trading.

## Behaviour
- Controls start disabled with a zero ceiling; configuration changes leave MASTER_OFF and require a fresh local safety epoch.
- Baseline capital retains the existing positions/open-buy/uncertain/fees accounting. Caller-supplied baseline excludes reservations managed by this allocator; its real-account provenance is unverified.
- Each registered BUY reserves quantity times its conservative limit price plus a nonnegative fee buffer. Baseline and all retained reservations must fit the existing absolute user maximum.
- Reservation and local claim commit together. A stale capital revision, Kill, batch barrier, duplicate claim or unresolved submission rolls the reservation back.
- Concurrent workers serialize both ceiling check and reservation; neither can spend a cached available-capital calculation.
- Once initialized, the legacy BUY claim entry requires the allocator's reservation. Existing unreserved open BUY intents cannot be silently ignored.
- No automatic release after ACK, timeout, cancel, partial/full fill or baseline refresh. No expected EXIT/REPLACE proceeds are credited. Only conservative retained-reservation diagnostics are implemented.

## Remaining integration
An independently admitted account/settlement adapter must prove fills, valuations, cancellation finality, scope and source freshness before actual cash reuse. Retained reservations cannot be manually zeroed to manufacture capacity. This offline allocator has no settlement release capability and cannot run repeated real trading cycles by itself.

Real pretrade NetEV/market freshness/capacity/risk checks and an admitted broker/gate adapter remain separate. No new fee rate, strategy threshold, cutoff or promotion rule is introduced. Fifteen allocator tests plus the existing journal/reconciliation/risk suite pass locally (76 tests total).
