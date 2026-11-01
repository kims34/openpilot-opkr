# IndexAlert independent profitability admission gate — 2026-11-01 20:45 KST

**Scope:** documentation-only, independent read-only audit of GitHub/Railway evidence. No source approval, PIT admission, profitability backtest, Holdout access, trading or deployment authority is conferred. Other workstream ownership remains separate.

## Pinned current repository state
- Research `index-alert-research-v1`: `3b8b7830612a6284d7c7a60628cb527cb741627a`.
- Development `index-alert-position-regen-fix-v1`: `1e6367d2863a86c3470da13d81a955d277eba485`.
- KRX specialist `indexalert-krx-pit-source-audit-20261013`: `073d2d49e95f69fb10b943b93e51bb179fb3c698`.
- PR #414: Draft/open/unmerged, head before this note `49bdc4c6e0f05652c1d92018789f1d4f7e29ab54`; #412 Draft/open/unmerged head `bf3d9514a87c53b1775e22ec9ba7711f6cecc49f`; #420/#422/#423 Draft/open/unmerged. This audit does not merge or modify their research code.
- [Watchdog Actions #41292056320](https://github.com/kims34/openpilot-opkr/actions/runs/41292056320): actual job #124805130699 successful; four fail-closed watchdog tests and 31 research governance tests passed. Log: `M20 PIT admission: NOT ATTESTED; orders: DISABLED; holdout: NOT AUTHORIZED`. This validates offline guards, not real historical data.
- [Chronology Actions #41091128151](https://github.com/kims34/openpilot-opkr/actions/runs/41091128151): auto-anchor failed at public prospective payload fetch; chronology validation skipped. No independently admitted chronology.
 
## Source provenance and PIT
- OpenDART first-filed 2022 document ZIP SHA-256 `56639d8f6ebbecf14cd8bc3179d75d01162e2cd7bbdf8f6a3c9479b44f5084bb` is **recorded** in source-only PR #412, not independently rehashed from raw ZIP in this audit. Fifteen candidate operating-profit row shapes do not prove exact consolidated three-month operating profit; bounded filing index does not establish complete correction lineage or first-publication intraday timestamps. Prior-period and historical symbol mapping are not independently admitted.
- KRX #420's isolated 2017–2022 scope reports 1,565 SHA-backed weekday pairs with 90 uncertain calendar/source-empty sessions and separate 27 nonpositive OHLC cases; #422/#423 are offline comparators, not executed authenticated original private day-set reconciliation. KRX specialist's wider 2015–2026 3,071-pair/184-ambiguous-day scope is a **different denominator** and cannot be conflated with the 90. Neither storage hashes nor synthetic parser tests authorize exchange calendar, security-level tradability, first-availability PIT or historical fills.
- Railway `indexalert-pit-rebuild` latest returned deploy log `2026-11-01T11:45:49.623447369Z` (20:45:49 KST): `status=FAIL_CLOSED`, `error_reason_code=COMMON_OHLC_NONPOSITIVE`, 27 nonpositive OHLC and zero-volume/value rows among 803 common-stock rows, `session_manifest_sha256=null`, independent source/chronology/model admission all false, `ordering=DISABLED`, no order or funds authorization. Rejected-source receipt points to 2026-09-28.
- Railway KRX historical worker deployment status SUCCESS, but no new original source logs in inspected period. Kiwoom REAL read-only latest deployment SUCCESS (2026-10-29) with only container start lines; no independently demonstrated successful brokerage authentication or tradable execution.
- Railway `get_staged_changes` and `get_status` report no stagedChanges, but `get_status.pendingWork` contains zero-change staged patch `e113dacb-6705-4416-9997-dc694539d382`; do not apply/accept. No deployment action taken.

## Executability and economic gate
- Missing independently PIT-certified daily market session, security listing/status, liquidity/lot/price limits, executable bid-ask and fill, timestamp-safe source availability, corporate-action and symbol history. Historical orderable quantity and fills are not established.
- Missing verified brokerage commissions, venue/exchange fees, applicable sale taxes, spread/slippage, market impact, partial fills, limit-up/down, turnover, cash timing and rejected-order effects. Without admitted transaction-level series, after-tax **NetEV, PF, CAGR, MDD, ES95 and ES99 are NOT EVALUABLE** (not zero); no M20 backtest is run.
- Keep Frozen/Holdout/Champion/Top3, preregistration and existing holdout separation immutable. No leakage, optimisation using holdout, champion promotion, permission changes, credentials, orders, funds, deployments, PR merges or changes to other owners' work.
- **Decision: M20 profitability NO-GO; ORDERING=false/DISABLED.** Only new authenticated original-source and independent PIT/tradability/cost evidence could justify reconsideration; no such admission found in this inspection.
