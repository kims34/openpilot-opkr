# IndexAlert independent profitability gate audit — 2026-11-01 13:42 KST

**Scope:** read-only source evidence and policy gates only. No M20 profitability execution, data ingestion, sealed Holdout access, live trading, deployment, permission/funds change, merge, or Champion promotion. This document is isolated from the KRX/PIT and optimization workstreams.

## Independently checked refs
- Research `index-alert-research-v1`: `3b8b7830612a6284d7c7a60628cb527cb741627a`.
- Development `index-alert-position-regen-fix-v1`: `1e6367d2863a86c3470da13d81a955d277eba485`.
- KRX source audit `indexalert-krx-pit-source-audit-20261013`: `073d2d49e95f69fb10b943b93e51bb179fb3c698`.
- Draft, open, unmerged PRs: #414, #412, #420, #422, #423. Source: GitHub PR metadata 2026-11-01.
- Latest visible Watchdog run [#41264126871](https://github.com/kims34/openpilot-opkr/actions/runs/41264126871) created 2026-11-01 02:11 UTC, succeeded. Its actual job log: `M20 PIT admission: NOT ATTESTED; orders: DISABLED; holdout: NOT AUTHORIZED`. Offline tests passed, which is a safety contract check, **not** original data PIT admission.
- [Chronology Anchor #41091128151](https://github.com/kims34/openpilot-opkr/actions/runs/41091128151) failed at 2026-10-30 17:13 UTC: HTTP 404 fetching `/anchor/latest`; chronology record and downstream validation skipped.
- [OpenDART official original source run #38381866190](https://github.com/kims34/openpilot-opkr/actions/runs/38381866190): official 2022 document receipt digest recorded as `56639d8f6ebbecf14cd8bc3179d75d01162e2cd7bbdf8f6a3c9479b44f5084bb`, 15 candidate operating-profit row shapes, neither 2022 nor 2021 quarter window bound to the table. This is a recorded receipt digest **not independently recomputed from original ZIP bytes in this audit**.
- KRX Draft #420 documents 90 uncertain historical sessions and 27 nonpositive common-stock OHLC cases; #422/#423 are offline candidate comparators, not approved historical trading calendars.

## Railway read-only observations
- Production `indexalert-pit-rebuild` latest returned runtime log 2026-10-31 14:46:01 UTC: `FAIL_CLOSED`, `COMMON_OHLC_NONPOSITIVE`, 27 nonpositive OHLC rows, `independent_source_admission_verified=false`, `independent_chronology_admission_verified=false`, `independent_model_admission_verified=false`, `live_order_authorized=false`, `ordering=DISABLED`.
- Historical KRX worker production deployment dated 2026-10-12 remains on development commit `1e6367d`; private volume mounted at `/data`. No private-volume read or fresh SHA recomputation was performed here.
- Kiwoom real read-only service latest deployment is labeled SUCCESS (2026-10-29 06:21 UTC), but the deploy log shows only container start; this is **not evidence of successful broker authentication or order authorization**.
- `get_staged_changes` and `describe_environment` return `staged=null`; `get_status` simultaneously reports an empty `pendingWork` staged patch dated 2026-10-29. This read inconsistency is not a deployment authorization.

## Independent admission matrix
| Gate | Audit conclusion |
|---|---|
| Immutable original source SHA and vintage | **NOT ATTESTED**: source receipt hash recorded, raw ZIP independent rehash unavailable; original publication instant and full correction chain unverified |
| Financial PIT and security mapping | **NOT ATTESTED**: original 3-month consolidated operating profit and comparison window unbound; historical issuer-to-security mapping unverified |
| Market calendar / tradability | **NOT ATTESTED**: 90 uncertain sessions, 27 nonpositive OHLC rows, per-security status, limit/suspension and executable entry/exit evidence unresolved |
| Costs, fees, slippage, taxes | **NOT ATTESTED**: no independently admitted executable after-cost ledger |
| NetEV, PF, CAGR, MDD, ES95, ES99 | **NOT EVALUABLE** without approved original PIT panel and cost/tradability ledger; no performance run attempted |
| Frozen / Holdout / Champion / Top3 | **UNCHANGED**: no reselection, optimization, unsealing or promotion |
| M20 execution / live ordering | **NO-GO**, `ORDERING=false`, no funds, permissions or real orders |

## Required sequence before a future M20 decision
1. Independently attest original OpenDART raw bytes and first publication/correction timeline; prove exact comparable consolidated quarterly facts and historical issuer mapping.
2. Independently resolve market-specific KRX session classification, nonpositive OHLC quarantines, and security-day executable tradability.
3. Pin a fully specified executable costs/tax/slippage ledger and immutable pre-registered cohort, while preserving Frozen/Holdout/Champion/Top3.
4. Only after explicit independent source/PIT admission, seek separate authorization for **one** frozen M20 evaluation; otherwise remain fail-closed.

No new source admission or profitability result is claimed.
