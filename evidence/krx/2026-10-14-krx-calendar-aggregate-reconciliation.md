# KRX private source empty-day totals vs diagnostic third-party exchange calendar
**Observation date: 2026-10-14 KST. Status: COUNT-LEVEL TRIAGE ONLY. Not official day-level calendar certification or PIT admission.**

## Concrete new finding

The original Railway worker SHA-bound 2015–2026 year receipts, without any additional KRX endpoint call, report **184** weekdays with empty KOSPI daily-trade responses and uncertain cause. These are existing year-level counts, not a newly requested dataset.

As an independent *diagnostic* exercise, the locally installed open-source `exchange_calendars==4.13.1` `XKRX` calendar was queried offline for 2015–2025 full years and **2026-01-01 through 2026-10-08**. That 2026 cutoff is inferred from the worker reporting **201 weekday checkpoints** from January and must be confirmed against original exact date receipts. No third-party dates or any KRX raw price/security rows were copied into this public evidence.

| Year | Private worker weekday checkpoints | Worker empty daily responses (unresolved) | Secondary XKRX weekday closures | Count difference |
|---|---:|---:|---:|---:|
| 2015 | 261 | 13 | 13 | 0 |
| 2016 | 261 | 15 | 15 | 0 |
| 2017 | 260 | 17 | 17 | 0 |
| 2018 | 261 | 17 | 17 | 0 |
| 2019 | 261 | 15 | 15 | 0 |
| 2020 | 262 | 14 | 14 | 0 |
| 2021 | 261 | 13 | 13 | 0 |
| 2022 | 260 | 14 | 14 | 0 |
| 2023 | 260 | 15 | 15 | 0 |
| 2024 | 262 | 18 | 18 | 0 |
| 2025 | 261 | 19 | 19 | 0 |
| 2026 | 201 | 14 | 12 | 2 until exceptional announced closures are considered |
| **Total** | **3,071** | **184** | **182** | **2** |

**2015–2025:** all 11 years have **exactly equal annual counts** (170 recorded empty provider days vs 170 calendar closed weekdays).

**2026:** the reference calendar counts **12** non-session weekdays through October 8 versus the worker's **14** empty responses. The third-party calendar is missing **2026-06-03 (local election)** and **2026-07-17 (Constitution Day)** as exceptional stock-market holiday dates. News reporting [KRX's May 20, 2026 announcement](https://www.mt.co.kr/stock/2026/05/20/2026052010314634386) directly names both closed-market days. KRX's public [KOSPI holiday rules](https://regulation.krx.co.kr/contents/RGL/03/03010100/RGL03010100T1.jsp) establish that elections and exchange-designated holidays can close the market; a [KRX-hosted simulation bulletin board](https://strn.krx.co.kr/corebbs5/BHPSTRN0401/list) separately lists both dates, but the simulation platform is not evidence of actual original cash-stock trading observations. The news account supports the market-closure claim, not the original KRX date-by-date series or PIT availability times.

Thus the **secondary calendar 182 weekdays + two reported exceptional closure dates = 184**, numerically equal to all 184 unresolved worker daily empty-response counts.

**CRITICAL:** numeric agreement of counts does not establish equality of dates. It is theoretically possible for a missing valid trading date and a nonempty erroneous holiday date to cancel within a year. This exercise did **not** inspect or compare the exact 184 private dates with independent original KRX calendar entries. It cannot turn an empty provider response into a certified holiday, nor does it prove original member-security coverage, corrected corporate actions, halt/resume episodes, timestamp PIT or security tradability. In particular, neither the election day nor Constitution Day has been proven to be among the two private provider-empty dates via exact receipt comparison.

## Reproducible (without hidden data) boundary

- [Machine-readable aggregate reference](./2026-10-14-krx-calendar-count-candidates.json), generated from the above offline comparison.
- [Offline candidate counter](../../research_v1_krx_calendar_count_triage.py) and [unit tests](../../test_indexalert_krx_calendar_count_triage.py), checking all annual tallies against the pre-existing source manifest with no required pip dependencies and **never approving PIT**.
- No new KRX API calls were made, no Railway configuration or stored data changed, no auto-orders, no Champion/H5/Frozen/Holdout changes.
- Maintain **all 184 ambiguous days in the original source manifest** and all **27 flagged securities in quarantine**. Source contract gates C and D stay BLOCKED. This is a stronger prioritization clue, not a new source-admission status.

## Next actual-data validation — authorized private-only operation required

1. On the dedicated private Railway volume, use existing offline `research_v1_krx_openapi_private_integrity_audit._check_one` SHA-bound per-day metadata; **do not fetch any KRX original bytes again**.
2. Obtain an independently authenticated original KRX cash-equity holiday/session schedule valid for each relevant historic year. Check licence/rights and version/effective-time metadata. A current `XKRX` software calendar or modern KRX web rule is insufficient as final authoritative evidence.
3. Compare the **exact** historical dates privately, then publish only year-level total classifications, unresolved mismatch **counts** and aggregate evidence fingerprints. Do not publish private original market rows, issuer IDs or protected date-level raw records.
4. Even full official market calendar matching does not verify the 27 securities' individual halt/delist/cleanup status or PIT chronology. These remain separate mandatory gates.

`COUNT_CANDIDATES_MATCH; ACTUAL_DATE_SET_NOT_ATTESTED; PIT_NOT_ADMITTED; ORDERS_DISABLED`.
