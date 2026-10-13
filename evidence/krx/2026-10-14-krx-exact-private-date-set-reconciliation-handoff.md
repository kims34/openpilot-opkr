# KRX historical day-set cross-check — implementation and remaining primary-source gate

Date: **2026-10-14 KST**. Disposition: **offline code prepared; production private 184-day date-by-date comparison NOT performed; no PIT admission**.

## What changed in this work cycle

1. Read GitHub audit and development branch heads and Railway KRX historical worker deployments/logs. The latest KRX historical worker remains the 2026-10-12 SUCCESS deployment (source commit `1e6367d2863a86c3470da13d81a955d277eba485`); there were **no later runtime logs** matching the checked 2026-10-13+ interval and no new worker deployments.
2. Verified the original worker's `research_v1_krx_openapi_private_integrity_audit._check_one` returns per-day *SHA-backed* source-pair receipt metadata on the authorized private volume. It verifies stored raw object bytes/size, raw content hashes, parsed schema/quality and the original stored capture checkpoint before returning metadata. It does **not** prove original historical data publication time, official holidays, delistings or order fill.
3. Added [read-only exact date-set comparator](../../research_v1_krx_private_date_set_comparator.py) and [synthetic fail-closed regression suite](../../test_indexalert_krx_private_date_set_comparator.py). The comparator requires an exact source-checkpoint for *every requested weekday* and a separately supplied dated closed-session list. It reports only counts and SHA digests, not KRX private original price rows, issuer identifiers or individual confidential receipt metadata. It distinguishes (a) empty provider responses on reference-closed days, (b) empty responses on reference-open days and (c) nonempty responses on reference-closed days. Importantly, it blocks the scenario where two year-level counts happen to match but the actual dates differ.
4. Added an *optional cross-check* against the **existing original private audit's year-snapshot SHA256 computation**, using its canonical per-checkpoint structure. This is a guard against silent private-source replacement; it is not calendar or PIT certification.
5. CI remains strictly offline: synthetic-only tests require no KRX API token, no Railway private source records and no network calls. Only GitHub audit branch files changed, no Railway config/start command modification and no real transaction.

## Primary-source routes checked

The [KRX public holiday table](https://open.krx.co.kr/contents/MKD/01/0110/01100305/MKD01100305.jsp) has a market selector and a calendar-date search/export interface. The [KRX annual market calendar](https://global.krx.co.kr/contents/GLB/05/0501/0501060000/GLB0501060000T3.jsp) lists annual selection buttons including 2015–2020, 2022–2025; displayed page rendering does not by itself prove that all 2015–2026 original KOSPI cash-equity trading-day dates, effective market scopes and initial publication timestamps have been downloaded or authenticated. KRX [KOSPI trading/holiday rules](https://global.krx.co.kr/contents/GLB/06/0602/0602010201/GLB0602010201T1.jsp) cover national elections, Labor Day, year-end and special exchange closures; they cannot replace original individual daily event-source evidence. The [2026 May 20 KRX announcement reported by Yonhap](https://www.yna.co.kr/amp/view/AKR20260520064251008) confirms the 2026-06-03 election closure and 2026-07-17 Constitution Day closure, but it does not establish the exact stored private KRX empty-response days.

The third-party `exchange_calendars==4.13.1` XKRX annual count comparison is an **unauthenticated diagnostic candidate**, not an independently certified KRX source. Its adjusted count agreement is not a date-level match.

## Reproducible next bounded **private** verification

- Keep existing official KRX OpenAPI six-GET controlled sample closed: no repeat or additional protected endpoint without separate source-specific permission.
- For each pinned year window, run original SHA-backed `_check_one` on the currently deployed **dedicated KRX private volume only**. Feed its in-memory metadata into `audit_private_scope` with exact reference holiday dates; pin expected empty day count and expected original SHA256 snapshot using the already recorded year receipts.
- Source and independently verify the **original KRX cash-equity session calendar for 2015–2026**; retain original record evidence and source version/availability information within its permitted scope. A public page link, self-declared source fingerprint, or today's trading calendar is insufficient as original as-of evidence.
- Publish only yearly totals, SHA digests and honest blocked/failed states; never export exact private market-data rows, users' secrets or proprietary source objects.
- Current Railway worker points to the development branch and not this isolated audit branch. This source comparator **was not deployed or executed against the private worker**, and it would be incorrect to say the 184 unresolved dates were actually matched.
- Keep the **27 questionable securities quarantined** pending original official halt/resumption/cleanup/delist/corporate-action status; a passing market-level calendar comparison cannot release a single security.
- Never set M20 source PIT approved, unlock frozen or holdout, change Champion, set ordering to true, place orders or move funds from these diagnostics.

Status: **3,071 stored weekday source checkpoints; 184 unresolved date-level source/calendar classifications; 27 securities excluded; no newly PIT-admitted full universe; gates C/D BLOCKED.**
