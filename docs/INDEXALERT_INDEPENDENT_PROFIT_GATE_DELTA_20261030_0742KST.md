# IndexAlert independent profitability gate — 2026-10-30 07:42 KST

## Scope and no-write boundary
Read-only cross-check of GitHub research/development/KRX workstream refs, Draft PRs, Actions and Railway production. This is the sole permitted isolated **documentation-only** write attempt in Draft PR #414 branch; it grants no source, PIT, profitability, Holdout or trading approval. No source capture, private-volume reads, KRX requests, backtest, deployment, merge, orders, funds, credentials, permissions, Champion or Top3 changes.

## Current refs and PR status (direct GitHub API)
- Research `index-alert-research-v1`: `3b8b7830612a6284d7c7a60628cb527cb741627a`.
- Development `index-alert-position-regen-fix-v1`: `1e6367d2863a86c3470da13d81a955d277eba485`.
- KRX specialist `indexalert-krx-pit-source-audit-20261013`: `073d2d49e95f69fb10b943b93e51bb179fb3c698`.
- PR #412 `bf3d951`, #413 `f003ef6`, #414 pre-write `c2ee4db`, #416 `053de55`, #418 `2f98401`, #420 `fab3cbb`, #422 `c148576`, #423 `0e38004`: all observed Draft/open/unmerged. #420/#422/#423 are offline KRX calendar/exceptions comparison tools, **not** certified original-private exact date sets or historical tradability.

## Actions, source and SHA evidence
- GitHub REST Actions: **4,621** runs; newest [Watchdog #40960712047](https://github.com/kims34/openpilot-opkr/actions/runs/40960712047), created 2026-10-29 21:47:26 UTC (2026-10-30 06:47:26 KST), SUCCESS. Direct job `123752419542` logs: watchdog/governance offline safety checks passed; explicit `M20 PIT admission: NOT ATTESTED; orders: DISABLED; holdout: NOT AUTHORIZED`. This is safety regression only, not performance/source admission.
- [Chronology Anchor #40914179246](https://github.com/kims34/openpilot-opkr/actions/runs/40914179246) job `123589876652`: `HTTP Error 404: Not Found` fetching public `/anchor/latest`, chronology append and validation skipped. Existing unresolved chronology blocker; do not infer a published PIT instant.
- [OpenDART original #38381866190](https://github.com/kims34/openpilot-opkr/actions/runs/38381866190) job `115244084285` directly re-read: fixed 2022 first-edition document reported ZIP digest `56639d8f6ebbecf14cd8bc3179d75d01162e2cd7bbdf8f6a3c9479b44f5084bb`, 15 operating-row table-shape candidates, `financial_values_extracted=false`, `original_cfs_q3_three_month_operating_profit_verified=false`, `historical_publication_instant_pit_verified=false`, `full_correction_lineage_verified=false`, `m20_performance_run_authorized=false`. Source ZIP **bytes were not independently fetched and rehashed** in this audit. No original 2021/2022 exact CFS 3-month values, correction chain, issuer vintage or first-publication timestamp approved.
- Independently re-read GitHub Contents blobs for `research_v1_runtime_manifest.py`: #418 head Git blob `108f66714602a1bd3ae42c34dcca7c16e38f460b` (103 lines) versus #413 base and `refs/pull/418/merge` blob `e0055c66c59398fd4a1158077446d886b54c4e37` (188 lines). Git blob SHA-1 context mismatch remains; it is **not** source ZIP SHA-256. No repinning or merge-context bypass.
- Original protected KRX archive bytes, 2021 13-day/2022 14-day private exact date sets, complete issuer-level PIT/tradability, corporate-action adjustment and real fill receipts were not accessed or independently verified. Historical 1,565 stored weekday-pair SHA receipts establish storage consistency only; 90 uncertain sessions and 27 common-stock nonpositive OHLC remain blocked.

## Railway production direct observation
- Project `d1c1a050-b7d6-41ce-b300-13c20f82a20a`, production `83d5840b-270e-4d3f-a941-a37fd4a55ff7`.
- PIT service `indexalert-pit-rebuild`, deployment `8b354fc1-cfb2-4ef0-863e-67f7f5dda2b5` SUCCESS, 1 running/0 crashed. Latest returned log at **2026-10-29 14:46:21.992 UTC** (23:46:21 KST), `status=FAIL_CLOSED`, `ordering=DISABLED`, `real_orders_authorized=false`, independent source/chronology/model admission false, 803 common-stock rows, 27 nonpositive OHLC and 27 zero-volume/value rows, `session_manifest_sha256=null`. No later logs in the queried range; ~8h observation gap is **not** itself proof of outage or a changed gate.
- Kiwoom REAL read-only service deployment `a77fb922-b679-4d88-92c4-03054ec579cd` SUCCESS but environment replica status 0 running/1 crashed; current deployment log returned only startup and empty message, not a fresh root cause. Previous auth 8050/WS failure remains historical, not newly reproduced in this window.
- KRX worker still has its dedicated volume; no protected original access or worker commands. Other Railway warnings/critical and an empty staged patch are not M20 source approval; no deployment accepted.

## Independent profitability verdict
**M20 NO-GO.** Source original-byte SHA, as-published PIT, historical security tradability, fees/commissions/spread/slippage/partial-fill/capacity/tax, and immutable code/runtime/source closure are not independently admitted. Therefore **after-cost/tax NetEV, PF, CAGR, MDD, ES95 and ES99 = NOT EVALUABLE**, not zero and not a numeric estimate. Do not execute M20 or touch sealed Holdout. Preserve Frozen H5/M20 (horizon20, purge20, WF504/126/126), Champion, Top3/no rank-4 backfill, NO_TRADE and `ORDERING=false`. No newly proven source approval or new blocker category this run.

## Required independent evidence before reconsideration
Source-owner original OpenDART 2021/2022 first-publication CFS three-month operating profit plus full corrections and timestamp; KRX-owner original per-security historical session, trading status, adjustment and execution feasibility; runtime-owner immutable head/base/merge manifest consistency; independent executable fees/taxes/slippage and capacity. All must be separately admitted before one preregistered M20 profitability test.
