# IndexAlert KRX six-year market-session *count* reconciliation — 2026-10-16 KST

**Source status: PARTIAL AGGREGATE COUNT CORROBORATION ONLY. NOT a validated original per-date market calendar, stock-day status, PIT, accepted universe, economic backtest or order permission.**

## Read-only private Railway source log recheck — no new provider query or raw data mutation

Railway production `IndexAlert` project `d1c1a050-b7d6-41ce-b300-13c20f82a20a`; existing `indexalert-krx-historical-worker` service `003812ee-102b-42b6-bda4-36925885b428`, existing deployment `16c93d7c-7cd0-4d84-a327-298d2805376c` in SUCCESS state at audit. Read-only deploy logs produced exactly **six** `INDEXALERT_KRX_PRIVATE_MISSING_2017_2022_YEAR` summaries; no 90 underlying private day records, stock identifiers, tokens or raw source rows were extracted.

| Year | Stored weekday pairs | Private source-empty / official-calendar-UNVERIFIED dates | Publicly reported equity-market holidays at evidence vintage | Status |
|---|---:|---:|---|---|
| 2017 | 260 | 17 | 17 in KRX-derived retrospective 2020 publication | **Count coincidence, date identities NOT VERIFIED** |
| 2018 | 261 | 17 | 17 in KRX-derived retrospective 2020 publication | **Count coincidence, date identities NOT VERIFIED** |
| 2019 | 261 | 15 | 15 in KRX-derived retrospective 2020 publication | **Count coincidence, date identities NOT VERIFIED** |
| 2020 | 262 | 14 | 14 in KRX-derived 2020 publication | **Count coincidence, date identities NOT VERIFIED** |
| 2021 | 261 | **13** | 10 in KRX-derived 2020-12-28 forecast + **3 subsequently added exchange closures published 2021-08-04** | **Plausible vintage-complete 13-date calendar candidate; private date identities NOT VERIFIED** |
| 2022 | 260 | 14 | Definitive complete original KRX holiday calendar **NOT independently inspected here**; at least two contemporaneously announced stock-market election closures | **14 unresolved; no holiday-count corroboration claimed** |
| **Total** | **1,565** | **90** | **No aggregate authorisation** | **Official per-date PIT NOT VERIFIED** |

The six private per-year source logs separately report `original_pit_admitted=false`, `trading_allowed=false`, and `PRIVATE_RAW_SOURCE_CAPTURED_NOT_PIT`. The summarized totals `17+17+15+14+13+14=90` are actual per-year worker output. KRX-derived **public counts** for 2017-2020 are from the **2020-12-28 retrospective/public forecast source** below; these counts are *not* original 2017-2020 daily as-of notices.

### 2021 dated candidate closure list with as-of/vintage separation

The KRX-sourced 2020-12-28 contemporaneous published next-year holiday table enumerated **10** planned stock market closed weekdays:

- 2021-01-01 — New Year
- 2021-02-11, 2021-02-12 — Lunar New Year
- 2021-03-01 — Independence Movement Day
- 2021-05-05 — Children's Day
- 2021-05-19 — Buddha's Birthday
- 2021-09-20, 2021-09-21, 2021-09-22 — Chuseok
- 2021-12-31 — Exchange year-end closure

[2020-12-28 Yonhap original KRX-derived full table](https://www.yna.co.kr/view/AKR20201225031900002) — initial source publication vintage. The original public 251-day trading forecast equals 261 weekdays minus these 10 closings. **Do not use the forecast as final after August 2021.**

Separately, the government expanded substitute public holidays in [2021-08-03 contemporary announcement](https://www.yna.co.kr/view/AKR20210803023800001), and the exchange explicitly announced **three additional exchange closed sessions** on [2021-08-04](https://www.newspim.com/news/view/20210804000631):

- 2021-08-16 — substitute National Liberation Day
- 2021-10-04 — substitute National Foundation Day
- 2021-10-11 — substitute Hangul Day

Thus **261 expected weekdays minus 10 planned minus 3 subsequently added = 248** candidate final open sessions. This numerical equality to 13 private-source-unclassified 2021 dates is **only an aggregate consistency signal, not even one individually matched PIT market date**. Keep the original 10-date vintage and later three-date 2021-08-04 amendment separately so that earlier backtest time decisions cannot access a future 2021-Aug announcement.

### 2022 known exception-day leads, without claiming complete count certification

[2022-02-10 exchange announcement reported by Yonhap](https://www.yna.co.kr/view/AKR20220210072200002) confirms closures on **2022-03-09 presidential election** and **2022-06-01 local election**, before both dates. Treat these only as two contemporaneous public holiday candidates; they do not verify all 14 privately unknown 2022 days or 2022 per-security statuses. An unrelated personal holiday calendar is not enough for official PIT admission.

## Required owner-side actual reconciliation (not executed)

1. **Read the 2017–2022 existing private original daily receipt hashes/dates** under already approved read-only scope. For 2021, compare the **exact set** of 13 unverified days with the 13 explicit dated candidate market closings above; require matched market type, authoritative as-of issuance/changes, genuine original source bytes and cryptographic receipt lineage. Distinguish archival source-empty from explicit official exchange CLOSED.
2. For 2017–2020 and 2022, fetch or independently authenticate the **actual dated official year-specific exchange closure notices** and as-of amendments, then match each *individual* original SHA-linked date. Retrospective annual count match never permits converting a row to a verified holiday.
3. A planned holiday changed or announced partway through 2021 must be used according to its actual available-at time. Verify full venue calendar per year; a KOSPI index record can corroborate an **open market**, not individual stock-day trading. Absence of an index record alone proves neither holiday nor suspension.
4. Separately quarantine **2026-09-28** prospective H5 **27/803** nonpositive common-stock OHLC rows. These are unrelated to the historical 90 date gaps. Historical security master PIT, halt/delist/corporate actions and legitimate fills are a separate requirement even if all 90 dates are eventually identified.
5. M20 after-cost/tax historical profitability cannot run until KRX and original-first-filed DART earnings PIT proofs both pass. Frozen H5/M20, purged WF/CPCV/Holdout/Champion/Top3/NO_TRADE, `ORDERING=false`, untouched; no new endpoint approval, active provider requests, Railway deployment, API keys, service modifications, account/funds, merge, live order or permissions change.

**Decision at this checkpoint:** 2017–2021 **76** annual gap counts align arithmetically with publicly reported market holiday counts after respecting 2021 vintage revision; however **0 of the private 90 dates have been independently matched to dated official original evidence in this audit**, and this note does not approve those 76. 2022's remaining 14 are separately unclassified.
