# KRX 2022: complete 14-day public holiday *candidate* comparator — 2026-10-18

**Classification: OFFLINE EXPERIMENTAL, READ-ONLY WHEN SEPARATELY AUTHORIZED, NOT OFFICIAL MARKET-PIT APPROVED.** This isolated Draft is based on the KRX specialist's separate still-Draft #420. No KRX endpoint, secret, Railway deployment, broker, code merge, original private 2022 volume read or actual model profitability run was performed in this work.

## Why this matters

Actual read-only 2026-10-12 Railway `indexalert-krx-historical-worker` deployment log for **2022** reports:
- `260/260` stored weekday original KRX-approved **daily/master** pairs SHA/backing-content integrity verified.
- `14` source-empty days, all classified `unverified_calendar_or_source_gap`. Source-empty does **not** mean market holiday, nor stock-day tradability.
- Original private 2022 full-year snapshot digest pinned to `0b110aaa452f43788e9880f4bf769981dee5f31c617485ca49cc7e7918306c9e`.
- `historical_pit_source_admitted=false`, `performance_run_authorized=false`, `real_orders_authorized=false`.

Separate [Draft PR #422](https://github.com/kims34/openpilot-opkr/pull/422) already prepared the **2021** private original 13-day comparator. This PR is the **non-overlapping 2022** counterpart; it does not modify #420 or #422 code and MUST NOT be deployed or merged automatically.

## Explicit public 2022 candidates: 11 regular + 2 election + 1 year-end = 14

| Date(s), YYYY-MM-DD | Category | Evidence-vintage cautions |
|---|---|---|
| 2022-01-31, 02-01, 02-02 | Lunar New Year | Public holiday pattern; original KRX announcement/authentic as-of receipt for Jan 31 still separately needed |
| 2022-03-01 | Independence Movement Day | Regular market-holiday candidate |
| 2022-05-05 | Children's Day | Regular market-holiday candidate |
| 2022-06-06 | Memorial Day | Regular market-holiday candidate |
| 2022-08-15 | Liberation Day | Regular market-holiday candidate |
| 2022-09-09, 09-12 | Chuseok & substitute | Regular market-holiday candidate |
| 2022-10-03, 10-10 | National Foundation / Hangul substitute holiday | Regular market-holiday candidate |
| 2022-03-09, 06-01 | **Presidential / local elections** | KRX **2022-02-10** announcement, before each event, not a timeless original from Jan 1 |
| 2022-12-30 | **Exchange year-end closing** | KRX **2022-12-15** announcement; do not use as an as-of known 2022 January decision |

Actual contemporary sources and rules:
- [KRX trading holiday rules](https://global.krx.co.kr/contents/GLB/06/0602/0602010201/GLB0602010201T1.jsp) include statutory public holidays, election days, last exchange business day before Dec 31, and extraordinary closings.
- [2022-02-10 Yonhap report of KRX official stock-market closure statement](https://www.yna.co.kr/view/AKR20220210072200002), confirms election holidays of March 9 and June 1.
- [2022-12-15 Yonhap report of KRX year-end exchange statement](https://www.yna.co.kr/view/AKR20221215067400002), confirms Dec 30 stock-market closing and Dec 29 final 2022 session.
- [2022-02-01 contemporary local market holiday compilation](https://www.mediainnews.com/news/articleView.html?idxno=21240) lists the 2022 weekday closures; this source is **secondary**, cannot verify first KRX publication dates for each ordinary holiday or original private stored SHA receipts.
- [KRX official market closing holiday lookup](https://open.krx.co.kr/contents/MKD/01/0110/01100305/MKD01100305.jsp) is dynamic, year-specific historical output and its publication-vintage *not* independently obtained here.

**Caveat:** All 14 candidates are weekdays and numerically equal the 2022 worker's 14 unverified empty-day *count*. This equality says **nothing** about whether the precise stored day IDs match. In particular this is not complete original 2022 official holiday-vintage proof; later year-end announcements cannot be used for earlier features.

## Prepared independent 2022 original private exact-set audit

- `research_v1_krx_private_2022_calendar_candidate_audit.py` defaults to `DRY_RUN_NO_PRIVATE_STORAGE_READ`, permits `--audit` only in the **existing named dedicated worker** environment with dedicated `/data` private volume, and only reads the already approved 2022 stored dataset, no network/official source calls.
- Before comparing **in memory** it executes existing `audit_private_range` to re-verify complete `260` weekday pairs, dual original raw SHA bytes/schema, `14` old source-empty dates, pinned full 2022 snapshot fingerprint and all denied permissions. Second pass re-reads all `260` `_check_one` receipts and recomputes same snapshot fingerprint to fail closed on changed in-flight private storage.
- Exact original private SHA-backed *empty source* day set is compared against this fixed public 14-date candidate set (not just both totals of 14); returns **only counters**, e.g. matched / missing / unexpected, plus `...NOT_PIT` classification. Private raw dates and original rows/hashes never appear in output or GitHub Actions. Same-count/different-date mismatch is rejected as verification.
- All authority flags are literal false: `official_market_status_admitted=false`, `full_universe_source_admitted=false`, `m20_performance_run_authorized=false`, `independent_holdout_authorized=false`, `real_orders_authorized=false`, `ordering=DISABLED`.
- Separate `test_research_v1_krx_private_2022_calendar_candidate_audit.py` contains **synthetic only** positive and adversarial fixtures; `.github/workflows/indexalert-krx-private-2022-calendar-candidate-offline-ci.yml` has no secrets, API provider requests, or volume mount. A passing CI confirms code's synthetic contradiction response **ONLY**.

## Hard boundary and next real evidence

**NO ACTUAL PRIVATE 2022 EXACT-SET RECONCILIATION WAS EXECUTED HERE.** Only the authorized KRX worker owner, after independent review/explicit deployment/access authorization, can run `python research_v1_krx_private_2022_calendar_candidate_audit.py --audit` in the worker's verified original private volume. A real exact-set match, should one ever occur, remains **private-source-date vs public-source-candidate corroboration, not authoritative original KRX calendar source-PIT**.

For 2017–2022 all 90 gaps remain unapproved until individual authenticated original exchange calendar, market type, as-of/publication vintage and stock-level listing/suspension/delist/corporate action independently validated. The prospective 2026-09-28 **27** nonpositive OHLC stock rows are entirely separate and quarantined. OpenDART first-published 2022/2021 Q3 CFS profit/period + issuer identity still incomplete. The entire H5/M20 Frozen framework, WF504/126/126, PIT/Purged/CPCV, sealed Holdout, Champion/Top3, NO_TRADE, costs/fees/taxes unchanged. **ORDERING=false.** Draft-only, unmerged, no live order, capital, permission, API subscription or Railway deployment.


## Independent source cross-check — 2026-10-19 KST (historical publication vintages; still NOT PIT)

After code CI SUCCESS, independently opened the three publicly dated sources without invoking any KRX private API or Railway container and cross-checked the exact 14 public candidate classes:

1. The **Korean government's 2022-01-11 contemporaneous holiday list**, sourced from the Ministry of Personnel Management, explicitly enumerates 2022-01-31 to 02-02, 03-01, 03-09 presidential election, 05-05, 06-01 local election, 06-06, 08-15, 09-09 to 09-11 (weekend members excluded), 09-12 substitute, 10-03, 10-10 substitute. URL: https://www.korea.kr/multi/visualNewsView.do?newsId=148897861 . **This authenticates a public-holiday calendar, not original exchange data or issuer/tradability.**
2. [Yonhap dated **2022-02-10 10:50 KST**](https://www.yna.co.kr/view/AKR20220210072200002) reports the **KRX** itself confirmed the securities market closed for 2022-03-09 and 2022-06-01 elections. This is independent contemporary exchange corroboration, as a journalistic transcription, NOT the exchange's raw original signed calendar payload.
3. [Yonhap dated **2022-12-15 10:31 KST**](https://www.yna.co.kr/view/AKR20221215067400002) reports KRX designated 2022-12-30 a securities/derivatives year-end closure and **2022-12-29** the year's final market session. This vintage became available in December and must **not** be backdated into pre-December source knowledge.

The 11 ordinary weekday holiday candidates, 2 explicit election closures, and 1 KRX year-end closure total **14 unique 2022 weekdays** (public evidence only). Compare to the actual Railway worker 2022 output of **14** private-source empty days: the public-date candidate **count** matches, but **exact original stored date-set not actually read or reconciled**.

Completed Actions:
- [Run #39132923556](https://github.com/kims34/openpilot-opkr/actions/runs/39132923556) exact PR #423 code branch HEAD `f69ca017cfd365b9ab81ccbf00ef42b06fbb9d4f`, **one job SUCCESS**, Python 3.12 and **12/12** synthetic negative/positive tests PASS; default CLI invocation validated `DRY_RUN_NO_PRIVATE_STORAGE_READ`, `official_market_status_admitted=false`, `ordering=DISABLED`.
- The source SHA identity for original Railway private 2022 remains fixed at `0b110aaa452f43788e9880f4bf769981dee5f31c617485ca49cc7e7918306c9e`. Its full live rehash/2022 exact set comparison has NOT been executed, and none of the 14 source-empty days are promoted to official market days.

**Authority and isolation:** [Draft PR #423](https://github.com/kims34/openpilot-opkr/pull/423) remains unmerged; [2021 separate Draft PR #422](https://github.com/kims34/openpilot-opkr/pull/422) untouched. Actual worker-volume execution needs separate owner authorization and code availability, currently absent. No new API permissions, official KRX endpoints, Railway deployment, model/Champion, sealed Holdout, funds or live orders; `ORDERING=false`.

## 2026-10-19 primary KRX KIND first-party market-scope verification and mandatory anti-cross-venue regression

Independent **first-party actual KRX KIND direct official notice** (not third-party press/Google snippet):

- [KRX KIND original **2022-02-10** KOSDAQ election day market-closure notice](https://kind.krx.co.kr/external/2022/02/10/000126/20220209001809/71985.htm) explicitly specifies `대상시장: 전체 코스닥시장`, `휴장일자: 2022-03-09, 2022-06-01`, official KOSDAQ market rule Article 5. This is genuinely an exchange-issued dated notice **for KOSDAQ only**. It proves neither original 2022 per-day KOSPI private source nor KOSPI venue holiday/PIT as-of market decision.
- [KRX KIND original **2021-09-27** KOSDAQ Oct substitute holiday notice](https://kind.krx.co.kr/external/2021/09/27/000113/20210915000217/71985.htm) explicitly specifies `대상시장: 전체 코스닥시장`, `휴장일자: 2021-10-04, 2021-10-11`. This is a helpful independent public archival 2021-source clue, but not KOSPI first-party proof.
- [KRX KIND original **2021-08-04** KOSPI Aug substitute holiday notice](https://kind.krx.co.kr/external/2021/08/04/000158/20210804000347/99340.htm) explicitly specifies `대상시장: 유가증권시장`, `휴장일자: 2021-08-16`. This one **is in the KOSPI venue**, but still does not prove the SHA-pinned privately stored 2021 day and precise first-publication **clock time**.

The preexisting 2022 PRIVATE worker stores **KOSPI market data**; its exact-date classifier must never use an original KIND notice whose stated market is KOSDAQ as KOSPI original market-source evidence. News reporting closures for stock markets generally and national public-holiday legal text remain independent *supporting* evidence, not substitutes for a venue-specific primary source.

New narrowly scoped research-only code commit `8dfde89e047bb29a8c314fb444376e16a3b61f24` records a 2022 KOSDAQ KIND primary source link and a strict separate market-scope classification in the offline candidate result:
`private_2022_market_scope="KOSPI"`; `identified_krx_kind_primary_notice_market_scope="KOSDAQ"`; `cross_venue_kosdaq_primary_notice_is_kospi_evidence=false`; `matched_kospi_first_party_original_kind_election_notice_count=0`; `krx_kind_primary_notice_original_publication_instant_verified=false`.
The companion adversarial offline regression commit `3b5650aa47e1868a5934ed0461b5f1050e89cd18` asserts **a synthetically matching complete 14-day set still cannot certify KOSPI from the original KOSDAQ notice, or authorize M20/performance/orders**.

These market-scope flags are **human-verified external-document hints**, not a programmatic cryptographic authentication of the original exchange notice or its historical availability. No first-party KOSPI 2022 election/other close-day notice has yet been independently retrieved in this particular PR. No new official API, private Railway data/worker, manifest, broker permission or production state was accessed or modified.

**PIT gate still closed:** Neither synthetic 2022 date equality nor partial primary public KOSDAQ notice authenticates original 2022 private KOSPI exact 14-day source-empty set, KOSPI official per-day market status, security tradability, corporate actions, OpenDART M20 or after-cost/tax returns. `ORDERING=false`, dependent Draft PR unmerged.
