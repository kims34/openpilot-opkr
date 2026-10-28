# IndexAlert independent profitability source gate — 2026-10-28 16:44 KST

**Decision: M20 PIT NO-GO / M20 economic execution PROHIBITED.** This is a metadata-only independent read-only receipt, not source admission or deployment authority. Only this isolated documentation file may be added to the draft integration branch. No source, strategy, CI, KRX specialist, optimization, Frozen, Holdout, Champion, Top3, trading or deployment change. `ORDERING=false` is mandatory; the actual Railway environment value was **not** observed.

## Direct GitHub branch and PR reads

- Research `index-alert-research-v1` HEAD `3b8b7830612a6284d7c7a60628cb527cb741627a`.
- Development `index-alert-position-regen-fix-v1` HEAD `1e6367d2863a86c3470da13d81a955d277eba485`.
- KRX specialist `indexalert-krx-pit-source-audit-20261013` HEAD `073d2d49e95f69fb10b943b93e51bb179fb3c698`.
- All Draft/open/unmerged: #412 `bf3d9514a87c53b1775e22ec9ba7711f6cecc49f`; #413 `f003ef6247e16fcc71bd3b1b20cd4904c4d984c0`; #414 pre-receipt `52e4cbb7c041981f82a96a51e3b012947b591ddc`; #416 `053de553646fc4765d2616544ca1e8d6bbdde35f`; #418 `2f98401cc50a6c6a25808a98516efd5bf0c944ee`; KRX #420 `fab3cbbd63a951a4e081f9e7f08c1391ca308581`, #422 `c14857620973531013799e44625d43080904fd5f`, #423 `0e38004363cac9fc4475556b3a1c445de9af407f`. No source admission is implied by Draft PRs.

## Directly decoded GitHub Actions evidence

- [Watchdog run #40638905543](https://github.com/kims34/openpilot-opkr/actions/runs/40638905543), 2026-10-28 14:35 KST, job `122652181922` success. Log: 4 watchdog tests + 31 offline governance tests pass; `M20 PIT admission: NOT ATTESTED; orders: DISABLED; holdout: NOT AUTHORIZED`. Flags-only artifact ZIP digest `e2ba2a470207125f1d061b5378fe1a1e68f1676ad4dee9d5bae36686ec297903`; not an original data digest or a live environment check.
- [KRX offline #39721289545](https://github.com/kims34/openpilot-opkr/actions/runs/39721289545), job `119635081965` success, 164 synthetic/offline tests; no actual private 2021 13-day / 2022 14-day exact-set, official historical trading calendar, security status or fills.
- [Chronology Anchor #40534270813](https://github.com/kims34/openpilot-opkr/actions/runs/40534270813), job `122295113858` failed with HTTP 404 on prospective anchor endpoint; validation job `122295116456` skipped. No endpoint retry, mutation or bypass.
- [2021 original DART #40262558066](https://github.com/kims34/openpilot-opkr/actions/runs/40262558066), official read-only job `121379096007`: original ZIP SHA-256 `8728c0a3c12761ca19e9c6455bea8f1bed0e4c1ebc2e21dc263c373a82a2b625`, integrity checked; 13 operating-label table candidates and **zero** same-table Q3 2021 period matches; first-publication instant and three-month CFS operating profit cell unverified.
- [2022 original DART #38380988990](https://github.com/kims34/openpilot-opkr/actions/runs/38380988990), official read-only job `115241142185`: original ZIP received and CRC/bounded parse checked, 1,570 tables, 15 operating-row shapes, zero original Q3 three-month CFS profit binding. 2022 ZIP SHA-256 `56639d8f6ebbecf14cd8bc3179d75d01162e2cd7bbdf8f6a3c9479b44f5084bb` is a **previous** official receipt, not independently rehashed now. First publication instant, original-vs-correction lineage and full universe are not attested.
- Original ZIP bytes, private KRX volume bytes, and source SHA-256 were **not independently re-downloaded or rehashed in this run**. Source digest/CRC integrity is not historical PIT, economic validity or live-trading authorization.

## Evidence decision matrix

| Gate | Result |
|---|---|
| Source archive SHA provenance | Existing official log receipts only; no independent raw-byte replay this run |
| Original DART Q3 three-month consolidated operating-profit numeric fact, first publication, correction lineage | NOT VERIFIED |
| KRX 2017–2022 historical archive 1,565 weekday pair integrity | Previously reported PASS; not re-read here |
| 90 uncertain sessions, 27 invalid/nonpositive OHLC, 2021/2022 private exact-set, as-of market calendar | NOT RESOLVED |
| Issuer/security historical mapping, delisting/halts, corporate actions, market cap, fills/lot feasibility | NOT VERIFIED |
| Fees, taxes, slippage, 2x-cost stress, NetEV, PF, CAGR, MDD, ES95/ES99 after costs | NOT EVALUABLE; no admitted source or authorized M20 run |
| Railway runtime deployment logs and actual `ORDERING` variable | NOT VERIFIED (read-only discovery blocked by interactive authentication) |

## Railway boundary and next prerequisites

A single read-only `Railway.list_projects({})` call returned `User input required but current turn is running in a non-interactive mode.` Stop; no alternative credential, endpoint or bypass attempted.

Independent prerequisites remain: first-filed DART exact three-month consolidated numeric cell plus earliest public availability and amendment chain; official private KRX exact-day and historical security/tradability evidence; source SHA and source-timestamp matching; frozen pre-registered fill/fees/taxes/cost stress only **after** independent PIT approval. Maintain Frozen H5, M20 horizon20/purge20, WF504/126/126, sealed Holdout, Champion/Top3/NO_TRADE and no rank-4 backfill. No orders, funds, permissions, deployment, PR merge, Champion promotion or M20 profitability run.

**Change assessment:** no new source-admission proof or newly introduced critical blocker observed. Existing HTTP 404 and Railway authentication block persist.
