# IndexAlert M20 — OpenDART receipt-date-only historical PIT admission floor

**Date:** 2026-10-20 KST. **Status:** independent OFFLINE time-source contract validated; original CFS financial facts / historical public-availability PIT **NO-GO**.

## Official source distinction

OpenDART's [official disclosure-list API guide](https://opendart.fss.or.kr/guide/detail.do?apiGrpCd=DS001&apiId=2019001) documents `rcept_dt` as an eight-digit receipt **date** `YYYYMMDD`, and `rcept_no` as a fourteen-digit filing identifier; the list API does **not** document a verified intraday first-public-disclosure timestamp. The fourteen-digit receipt ID is **not** a publication clock. The date of receipt must not be treated as proof that a numerical fact was available before any trading decision on that day.

The prior first-filed original fixed-cohort-slot-5 2022 Q3 DART archival checks (four original viewer finance subsections / 329 HTML tables / two operating-profit label candidates) remain intact, but the original **2022 and 2021 standalone July–September three-month consolidated income statement operating-profit cells** and historical first-publication instant remain unverified. The later/revised vintage must not silently backfill original-era features.

## New separate safety boundary — not alpha, not source admission

- Added `research_v1_m20_dart_receipt_date_floor.py`, `test_research_v1_m20_dart_receipt_date_floor.py`, and `.github/workflows/indexalert-m20-dart-receipt-date-floor.yml` at source commit `c9dac09df5446dfef7c37c5d9a6f1641819bcb49`.
- Input contract requires strict `YYYYMMDD` date-only receipt; first-original filing provenance separately attested; an **independently attested, sorted, duplicate-free official historical trading-session calendar**; a particular requested session explicitly present in that calendar. **No** weekdays/holidays/timezone/publication timestamps synthesized from a receipt ID or date. Same-receipt-day and earlier sessions are automatically rejected; days strictly later may be flagged merely as *date-floor candidates*, **never** financially/PIT authorized.
- If official calendar or original filing provenance is unverified, or input has intraday notation, malformed dates, missing sessions, duplicate/unsorted calendars, or out-of-range horizon, the function fails closed or returns non-admission. A later candidate can still be wrong if historical **actual public availability** or original edition itself is missing; therefore a positive date-only candidate is never sufficient to admit a strategy or run a performance test.
- Source tests use **synthetic dates only**; no real company, receipt, original financial amount, official KRX calendar or actual publication claim was introduced. No OpenDART/DART, Railway, KRX or broker request is made by this workflow.

## Independently verified CI and preserved artifact

[GitHub Actions #39347856501](https://github.com/kims34/openpilot-opkr/actions/runs/39347856501): **SUCCESS** — 14 offline regression cases, static no-network/no-broker check, and synthetic safety status JSON. Counts-only/status-only artifact ID `12231767134`, SHA256 `9d929bd0cd287a16387b50453390f5f790d7b854b98f8ecceb5eeb30cddabaa0`, seven-day retention until 2026-10-27T00:28:40Z. The artifact has no real receipt, trade session, time, issuer, financial data, calendar, title or identifier.

## Mandatory unresolved independent evidence for actual financial feature research

1. **Original accounting source**: first-published 2022 Q3 three-month consolidated operating-profit account and the 2021 comparative Q3 three-month value, with original statement/row/period/currency/amount identity and version-correction chain proven.
2. **Historical first public availability**: independent timestamp (or independently attested earliest public-access date plus conservative source delay); `rcept_dt` alone is receipt date not a verified first-release clock.
3. **Official historical trade sessions and issuer↔security PIT**: independently validated official market calendar, security status, corporate actions, currency/fiscal units and amendment as-of chronology. Do not infer calendar dates from weekdays or today.
4. Only after all source/holdout/cost/tax/PIT criteria from the frozen strategy are met may any higher-level strategy decision be reconsidered; this date-floor safety contract itself has no authorization powers.

**Preserve Frozen H5/M20, fees/taxes, independent Holdout, pre-registered experiments, Champion, all Railway and broker settings.** `m20_feature_pit_admitted=false`, `m20_performance_run_authorized=false`, `independent_holdout_authorized=false`, `champion_change_authorized=false`, `real_orders_authorized=false`, `funds_movement_authorized=false`, `permissions_change_authorized=false`, `ORDERING=DISABLED`. Keep Draft PR #412 unmerged. The prior sealed original-source archive remains separate; it was not changed or reinterpreted.

### Evidence provenance links
- OpenDART official API disclosure-list schema: https://opendart.fss.or.kr/guide/detail.do?apiGrpCd=DS001&apiId=2019001
- Original 30-day source-count capsule audit and offline replay: `INDEXALERT_M20_2022_Q3_FOUR_SOURCE_REPLAY_CAPSULE_20261018.md`
- Original precise CFS cell identity remains unverified per `INDEXALERT_M20_2022_FIRST_VIEWER_HEADER_LAYOUT_EVIDENCE_20261016.md`.
