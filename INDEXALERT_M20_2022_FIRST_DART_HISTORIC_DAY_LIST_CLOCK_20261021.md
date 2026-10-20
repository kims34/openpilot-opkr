# IndexAlert M20 fixed original 2022 Q3: historical DART day-list clock feasibility

**Research date 2026-10-21 KST.** **No first-disclosure intraday PIT admission. No CFS profit facts. No trading.**

## Why this differs from previous source probes

Official [OpenDART search API guide](https://opendart.fss.or.kr/guide/detail.do?apiGrpCd=DS001&apiId=2019001) defines `rcept_dt` as **YYYYMMDD receipt DATE**, not an auditable intraday first-publication timestamp. The 14-digit receipt number is an identifier, not a verified clock. DART's public **recent disclosures** list separately presents a **time** column beside the filing title and receipt day, and a dated navigation interface exists. Documentation/examples of `dsac001/mainAll.do?selectDate=YYYY.MM.DD&currentPage=N` describe pagination; this is a rendered public interface, **not** a documented immutable time-source API.

Earlier **frozen original cohort slot 5**, first-filed 2022-Q3 public DART viewer proof and safe archive remain intact: exactly four viewer finance sections, 329 total tables, two exact-label operating-profit candidate tables; no 2022 Q3 or comparative 2021 Q3 standalone 3-month CFS profit value, historical exact availability instant, unit, issuer/security point-in-time binding or full amendment financial-cell lineage proved. Early original standardized XBRL returned `014`, and separately queried current 2022 CFS normalized service returned unavailable `013/014` class. **No alpha/performance run is permitted.**

## New bounded read-only original receipt time-row path

- Code `research_v1_m20_first_historic_dart_listing_clock.py`, tests `test_research_v1_m20_first_historic_dart_listing_clock.py`, workflow `.github/workflows/indexalert-m20-first-historic-dart-clock.yml`.
- Starting with pre-existing official `corpCode.xml` + earliest `list.json` (two official authenticated GETs max), select exact original 2022-Q3 receipt and independently cross-check its official `rcept_dt` day; in private runtime, derive DART list query day. Query **at most eight** pagination-limited public `https://dart.fss.or.kr/dsac001/mainAll.do` pages, no API key in public request; bounded HTML response ≤2MB/page and 20-second request timeout.
- Parse only explicit `<tr>` row with exactly the **original 14-digit receipt** and at most one distinct **HH:MM[:SS] exact table cell**. Multiple receipts in a row, duplicate target rows, oversized malformed markup, strange time formats and unsupported API/missing row **fail closed**; never borrow a timestamp from another company's adjacent row.
- Persist **status/booleans/count of pages searched only**. Raw time, first receipt, company, issuer, day, original HTML, monetary amounts, source URLs with parameters and provider exception text never enter logs/artifacts. Even if visible, a historical list **time-cell rendering is not yet an independently certified original release timestamp**.
- Source commit `e8b7f09a861ccc951db90d03190cbc6e93bc85d2`, offline test commit `bf1cfb54352541a862f5e9b062921ada09890856`, narrow workflow commit `7dfe70f714decee0e320c7456f556ce05dc2215e`. Bounded paging refinement: `cf3487fd2e37f49af6086f3afac0ea82d4d3fc6c`, `b88a1d6f44dbab1052b9b0e9ee624bbfc822724d`, `e0f1856f14c46963a339ed9b2befd04f37effbf9`.

## Verified initial source status and bounded follow-up

- Initial [official one-page Actions #39515735269](https://github.com/kims34/openpilot-opkr/actions/runs/39515735269): **offline tests PASS**, official one-page query **SOURCE_GAP_FAIL_CLOSED** reason `HISTORIC_LIST_FIRST_RECEIPT_NOT_VISIBLE`. The first page did not show the exact first receipt in a parseable row. **This does not prove that 2022 filing-time data never existed**, nor that the market knew the filing at any particular time. Safe status artifact `12307203109`, digest `sha256:3839757b4e55fcab094b9efd59c2093d07d6a1f300d35ae6a5f184f2f98e7fa6`.
- Pagination is supported by prior DART interface usage references; the only additional permitted hypothesis is a hard maximum of **eight** pages of the same original receipt day without trading/account data. [Bounded official workflow #39516110459](https://github.com/kims34/openpilot-opkr/actions/runs/39516110459) started with offline tests and official source retrieval; at report creation, its final result was not yet verified. **Do not claim time-cell success without the actual completed logs and artifact**.
- Public interface documentation is not a historical signed publication ledger. Even an exact row/time match would be classified source metadata only; financial statement CFS accounting/PIT and intraday public release still need independent attestation.

## Mandatory safeguards

Original 2022/2021 standalone Q3 CFS operating-profit value/period/currency, first edition and correction chain, first-publication instant, official market calendar and historic company/security mapping remain unresolved. No Frozen H5/M20 changes, no cost/tax change, no Holdout/Champion promotion, no order/permission/funds access. `website_clock_is_authoritative_first_release_instant=false`, `exact_original_first_publication_timestamp_verified=false`, `m20_feature_pit_admitted=false`, `m20_performance_run_authorized=false`, `real_orders_authorized=false`, `ordering=DISABLED`. Keep Draft PR #412 unmerged. Do not create duplicate hourly automation.
