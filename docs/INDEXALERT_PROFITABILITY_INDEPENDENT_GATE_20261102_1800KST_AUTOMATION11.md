# IndexAlert independent profitability gate — 2026-11-02 18:00 KST

**Decision: M20 NO-GO.** Read-only evidence consolidation, isolated documentation only. This is NOT source admission, a backtest, trading permission, or approval to access Frozen/Holdout.

## Pinned GitHub refs and independent checks
- Research `index-alert-research-v1` == `3b8b7830612a6284d7c7a60628cb527cb741627a` (ahead 0, behind 0).
- Development `index-alert-position-regen-fix-v1` == `1e6367d2863a86c3470da13d81a955d277eba485` (ahead 0, behind 0).
- KRX specialist `indexalert-krx-pit-source-audit-20261013` == `073d2d49e95f69fb10b943b93e51bb179fb3c698` (ahead 0, behind 0).
- PRs #414, #412, #420, #422, #423: all open, Draft, unmerged. PR #414 head before this audit: `66aa2b781cba18e949337a21cc3f3498c96718dd`; PR #412: `bf3d9514a87c53b1775e22ec9ba7711f6cecc49f`; KRX #420: `fab3cbbd63a951a4e081f9e7f08c1391ca308581`; #422: `c14857620973531013799e44625d43080904fd5f`; #423: `0e38004363cac9fc4475556b3a1c445de9af407f`.
- [Watchdog Actions #41368406818](https://github.com/kims34/openpilot-opkr/actions/runs/41368406818), job 125033414398, actual log: 4/4 safety-contract and 31/31 research-governance tests passed; `M20 PIT admission: NOT ATTESTED; orders: DISABLED; holdout: NOT AUTHORIZED`. The repository-wide latest Actions run list was not available via this connector; this is a **selected confirmed run**, not asserted to be globally newest.
- [Chronology Anchor #41091128151](https://github.com/kims34/openpilot-opkr/actions/runs/41091128151): job 124184971844 failed HTTP 404; validation job 124184974604 skipped. No retry, bypass or new execution.

## Independent original-source log cross-check (NOT raw ZIP rehash)
- [Official 2022 first-original #38392847048](https://github.com/kims34/openpilot-opkr/actions/runs/38392847048), job 115280695115: recorded original document SHA-256 `56639d8f6ebbecf14cd8bc3179d75d01162e2cd7bbdf8f6a3c9479b44f5084bb`, integrity PASS. Official [layout #38380988990](https://github.com/kims34/openpilot-opkr/actions/runs/38380988990) examined 1,570 table shapes and 15 operating-profit label candidates, with **zero** exact 2022/2021 Q3 three-month CFS period bindings. 2022 original XBRL 014 gap unresolved.
- [Official 2021 first-original #40262532310](https://github.com/kims34/openpilot-opkr/actions/runs/40262532310), job 121377826016: recorded SHA-256 `8728c0a3c12761ca19e9c6455bea8f1bed0e4c1ebc2e21dc263c373a82a2b625`, 1,728 table shapes, 13 operating-label candidates, zero same-table 2021 Q3 / three-month binding. Both years' exact first-available publication instant, full correction lineage, original standalone CFS quarterly amount and historic issuer/security mapping are NOT VERIFIED.
- These SHA values were **independently read from prior official Actions job logs**, not recomputed from source ZIP bytes in this run. ZIP integrity is not financial semantic or PIT admission.

## KRX / Railway read-only state
- Historic 2017–2022 private KRX daily/master original SHA pairs: previously recorded 1,565/1,565 stored integrity PASS, **90 historical source-empty / exchange-calendar sessions still unauthenticated**. Draft KRX comparator PRs are synthetic/offline only; no private source replay or 90-day closure.
- Prospective 2026-09-28 source failure: **27 nonpositive common-stock OHLC rows of 803**, distinct from historical 90. Latest returned `indexalert-pit-rebuild` deploy log **2026-11-01 14:46:22 UTC**: `FAIL_CLOSED`, `COMMON_OHLC_NONPOSITIVE`, all independent source/model/chronology admissions false, `ordering=DISABLED`, no orders.
- Railway production status: PIT rebuild 1 running replica; Kiwoom REAL read-only service deployment marked SUCCESS but **0 running / 1 crashed**. `get_staged_changes` returned null while `environment_status` returned old pending patch `e113dacb-6705-4416-9997-dc694539d382` with empty changes: inconsistent read-only views; no patch accepted or deployed. No new production deployments observed beyond 2026-10-29.
- Historical official market-day/individual security trading status, delisting/halts, corporate actions, market cap and executable bid/ask, lot, tick, fill and capacity remain NOT VERIFIED.

## Economic authorization and guardrails
- Without PIT-valid original financial inputs and tradability, independently pinned commissions, exchange fees, transaction taxes, bid/ask spread, slippage, impact, lot/tick rounding and 2x-cost stress, **after-tax NetEV / PF / CAGR / MDD / ES95 / ES99 are NOT EVALUABLE** (not zero and not a PASS).
- Do not run M20 performance, economic replay or independent Holdout. Preserve Frozen H5/M20, Champion/Top3 with no rank-4 backfill, M20 horizon20, purge20, WF504/126/126, sealed Holdout and NO_TRADE; `ORDERING=false` / `DISABLED`.
- No trading, money movement, permissions, deployment, PR merge, Champion promotion, new API calls, or duplicated specialist work. Reassess only on new independently authenticated official PIT/market evidence and fixed cost/tax assumptions.
