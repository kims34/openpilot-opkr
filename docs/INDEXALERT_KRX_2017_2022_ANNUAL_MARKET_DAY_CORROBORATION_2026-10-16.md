# IndexAlert KRX 2017–2022 independently corroborated annual trading-day counts

**Observed:** 2026-10-16 KST. **Verdict:** **6/6 ANNUAL AGGREGATE COUNT MATCH / 0/90 DATE-SPECIFIC PRIVATE GAP IDENTITIES ADMITTED**. Official historic calendar/issuer-security PIT, M20 profitability, Holdout, Tiny Live and trades remain BLOCKED.

## Two independently obtained evidence legs

1. **Railway production raw-storage leg:** Read-only `IndexAlert / production / indexalert-krx-historical-worker` log for historical deployment `16c93d7c-7cd0-4d84-a327-298d2805376c` produced `INDEXALERT_KRX_PRIVATE_MISSING_2017_2022_YEAR` and `INDEXALERT_MISSING_2017_2022_INTEGRITY_YEAR/FINAL`. All **1,565/1,565** captured 2017–2022 weekday pairs have stored/schema SHA integrity, with annual zero-row or unclassified exchange calendar/source-gap counts: **17, 17, 15, 14, 13, 14 = 90**. The actual list of 90 private dates was **NOT read** and SHA text **does not itself certify KRX publisher, original as-of date or market open/closed state**.
2. **External contemporaneous/reported-market leg:** A 2020-12-28 news record explicitly attributes 2017–2020 exchange holiday and trading day counts to the Korea Exchange; a **2021-08-04** contemporaneous Korea Exchange announcement changes *planned* 2021 trading-day count by closing three additional weekdays; and a 2023-05-31 securities-research report (table 1) explicitly attributes actual 2021/2022 counts to KRX/QuantiWise. These published yearly aggregates are independent of the Railway logs and were **not** obtained by a newly approved KRX data service.

| Year | Private stored weekdays (Railway) | Private zero-row/unknown dates | Private derived nonempty days | Independently published trading days | Difference |
| --- | ---: | ---: | ---: | ---: | ---: |
| 2017 | 260 | 17 | 243 | 243 | 0 |
| 2018 | 261 | 17 | 244 | 244 | 0 |
| 2019 | 261 | 15 | 246 | 246 | 0 |
| 2020 | 262 | 14 | 248 | 248 | 0 |
| 2021 | 261 | 13 | 248 | 248 **actual revised** | 0 |
| 2022 | 260 | 14 | 246 | 246 | 0 |
| **Total** | **1,565** | **90** | **1,475** | **1,475** | **0** |

**Arithmetic:** each row checks `stored_weekday_pairs - source_empty_days = historically_reported_exchange_trading_days`. Independent date distribution must **still be proved** before it is valid to call any of the 90 empty days a holiday: a panel missing one real open session and including a false positive day elsewhere could have the exact same count. Nonempty count is **not certification of entire source universe or of executable trades**.

## Time-vintage finding: 2021 as-published 251 vs final 248

- At **2020-12-28** contemporaneous announcement, KRX initially planned **251 trading days / 10 weekday closures** in 2021. The article includes 10 explicit planned holiday dates. This planned (as-of 2020) schedule is not an error.
- The **2021-08-04** exchange communication subsequently announced **three additional stock-market closure weekdays**: **2021-08-16**, **2021-10-04**, **2021-10-11**. KRX's own public [KIND original stock-market closure notice dated 2021-08-04](https://kind.krx.co.kr/external/2021/08/04/000158/20210804000347/99340.htm) specifically verifies 2021-08-16 as a market closure; the contemporaneous 2021-08-04 exchange announcement reported all three (linked below).
- Therefore `251 initial - 3 new closures = 248 final`; and `261 weekdays - (10 initial + 3 additional closures) = 248`. This precisely matches private 2021 `13` empty/unknown weekdays but **does not prove the private zero-row 2021 dates are exactly those 13 dates**. No original 2021 private date list has been compared.
- Chronology matters: **do not impose the August-04 revision onto signals dated before August 04 as though it was publicly known**. Later calendar revisions need their separate available-at event, and retroactive full-year hindsight cannot enter historical PIT features.

## External verifiable sources (metadata/reference only, no new provider API access)

- Historic 2017–2020 reported KRX annual trading days/closures, and *original* 2021 planned 251/10 (published 2020-12-28): https://www.yna.co.kr/view/AKR20201225031900002
- Contemporaneous 2021 change 3 closures (published 2021-08-04): https://www.yna.co.kr/view/AKR20210804093200002
- Contemporaneous exchange-hosted 2021-08-16 closure original notice: https://kind.krx.co.kr/external/2021/08/04/000158/20210804000347/99340.htm
- 2023-05-31 Mirae Asset Securities Research table 1, KRX/QuantiWise sourced actual **2021=248, 2022=246**: https://securities.miraeasset.com/bbs/download/2108898.pdf?attachmentId=2108898 (p. 4; independently visually inspected the table).
- KRX public yearly day-by-day market closing lookup: https://open.krx.co.kr/contents/MKD/01/0110/01100305/MKD01100305.jsp (specific 2017–2022 day-by-day published coverage/source version remains unverified, do not treat query UI itself as records).

## Required NEXT private source owner reconciliation (no changes here)

1. Extract **exactly** those privately stored 90 exception-date keys plus each original raw empty-day SHA receipt **inside an approved read-only private worker**, never post private receipt IDs, token/hash-bonded security identifiers, keys or raw stock rows to GitHub. Check six years' **set equality**, not just annual counts.
2. Privately match every unknown day to an independently authenticated, appropriately dated KRX KOSPI/KOSDAQ official closing/schedule/publication record for that market and its as-of vintage. If the source index lists positive official open/trades for a purported empty-day, fail closed as a **true capture gap**. Lack of index data cannot prove closure; a present-day holiday page may not preserve authentic first-publication vintage.
3. Produce an immutable audit receipt with `year -> unknown_day_count, independently_authenticated_closed_count, unresolved_count, conflict_count, source_hashes` **without private actual dates/financial values in a public artifact**, and require every missing/contradictory source to remain NOT ADMITTED. Authenticate original release time separately from an arbitrary local file modification time.
4. Independently prove historical per-security listing/delisting/suspension, price/corporate-action adjustments, issuer-security mapping, fills/taxes/costs, and exclude all unverified stocks; *even exact all-year calendar agreement does not certify individual stock tradeability*. The unrelated **2026-09-28** `27/803` prospective nonpositive OHLC quarantine is separate and unchanged.
5. Only after validated original daily publisher/as-of PIT full-universe panel and original DART 2022/2021 Q3 standalone CFS accounting facts are admitted may one unchanged pre-registered M20 full-economics experiment be considered. Any independent sealed Holdout and Tiny Live require separate authority.

**Explicit flags:** `aggregate_six_year_counts_correlate=true`, `actual_private_90_date_set_compared=false`, `original_publisher_day_source_authenticated=false`, `historical_market_calendar_pit_admitted=false`, `security_day_tradability_verified=false`, `m20_feature_pit_admitted=false`, `m20_performance_run_authorized=false`, `holdout_accessed=false`, `live_orders_authorized=false`, `ordering=DISABLED`. Original Frozen H5/M20, 504/126/126, Champion/Top3 and source-lock baseline unchanged; PR Draft/unmerged. No Railway state, new KRX API service, broker/funds/permissions or real orders modified.
