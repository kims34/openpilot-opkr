# 2017 KRX historical holiday calendar: 16 listed before late holiday / 17 after

**Date of review:** 2026-10-14 KST. **Source classification: archived third-party mirror + official government decision + KRX-attributed September stock-exchange closure news.** No original KRX XLS bytes, original exchange calendar version timestamp, or private Railway day-level receipt files were accessed.

## Material new original-date investigation

1. [FinanceData blog published 2017-07-16 15:45 KST](https://financedata.github.io/posts/pandas-market-days-krx.html) transcribes a KRX 2017 holiday XLS export into **16** listed weekday closure dates. The blog links the underlying archived `hdays-2017-KRX.xls` via its public Gist [raw-file path](https://gist.githubusercontent.com/FinanceData/e09b8a5d720f3e7d89818fa1bfca4f5f/raw/699d9eea9ef72fb49ddc240e965d66dc731c224c/hdays-2017-KRX.xls). This archived binary could **not** be opened/downloaded by the current tool connection and thus its bytes, checksum, true upload date and KRX origin are not independently authenticated. The blog's displayed table has no **2017-10-02** entry. Do not label this a verified KRX-original July version.
2. **2017-09-05 09:31 KST:** [Yonhap contemporary report](https://www.yna.co.kr/view/AKR20170904189651001) describes the government's approval of 2017-10-02 (Monday) as an extraordinary national holiday. The [government's own personnel administration press release, published 2017-09-08](https://www.mpm.go.kr/mpm/comm/newsPress/newsPressRelease/?boardId=bbs_0000000000000029&category=&cntId=2421&mode=view&pageIdx=176) confirms the cabinet's September 5 designation decision. A government holiday designation is **not automatically an authenticated original exchange-session record**.
3. The [KRX-attributed closure notice](https://gostock66.blogspot.com/2017/09/2017-10-2.html), reproduced on a 2017-09-27 blog post, gives the **KRX original notice listing date as 2017-09-18** (no original KRX notice binary or precise KRX first-publication timestamp). [Yonhap 2017-09-15 market report](https://www.yna.co.kr/view/AKR20170915179300008) independently describes the ten-day stock-market break caused by the added 10/02 closure, so the closure was publicly discussed in advance. Later media coverage does not establish an original exchange source's specific first instant.
4. The 16 historic blog table days **plus the separately confirmed 2017-10-02 closure = 17 weekday closure candidates**. Offline-installed nonofficial `exchange_calendars==4.13.1/XKRX` returns **exactly the same 17 dates** for 2017. The earlier sanitized original Railway checkpoint manifest has **260 verified 2017 weekday pairs and 17 empty-date response counts**. Thus 17=17 is a **count match** and the two independent public/secondary *holiday candidates* have identical date sets; it is **not proof the 17 private Railway response-empty dates equal those candidates**.

## PIT leakage avoided

- The July 2017 third-party snapshot remains **16 days** in its own provenance record. The 10/02 extra holiday is not backfilled into the July evidence as though already present.
- The government holiday announcement can only be considered after its reported 2017-09-05 publication timestamp, and is classified as government evidence.
- Because the KRX notice original first-publication *time* is unverified (reproduction says date 2017-09-18), the as-of helper conservatively adds the one extra **candidate** starting 2017-09-19 00:00 KST, not earlier and not as an authenticated original KRX source.
- No inference about original KRX unpublished calendar updates, 2017 security tradability, available-at for financial data, corporate actions, tax or execution is permitted from a year-level count match.

## Code, pinned manifest and offline evidence

- [Machine-readable 2017 16→17 temporal manifest](./2026-10-14-krx-2017-holiday-temporal-source-reconciliation.json), containing public 16 days, original public URLs and time boundaries, late additional 10/02, 17-day offline diagnostic and explicit original private-source block.
- [As-of validator](../../research_v1_krx_2017_temporal_calendar_reconciliation.py), [10 regression tests](../../test_indexalert_krx_2017_temporal_calendar_reconciliation.py): prevent future holiday leaking into July, distinguish September 5 government vs September 18 exchange notice, deny source promotion, detect forged counts and provenance.
- [GitHub Actions #38504922428](https://github.com/kims34/openpilot-opkr/actions/runs/38504922428), audit-branch commit `ba3a9813c9cd594b19b6318b4de379721f897496`: **SUCCESS, 123/123 deterministic offline tests**. Zero KRX API requests, no Railway volume access, no trading.
- Railway KRX original worker remains attached to the existing `/data` volume on dev branch `index-alert-position-regen-fix-v1`, latest deployment `16c93d7c-7cd0-4d84-a327-298d2805376c` SUCCESS from Oct 12. No new deployment or original date-set comparison happened here.

## What is still strictly blocked

The actual **17 private source-empty 2017 dates** have not been enumerated and matched; the 2017 evidence therefore cannot decrement the total **184 ambiguous provider-empty dates** by 17 or by one. **27 historic securities remain quarantined**, KRX source contracts C/D remain **BLOCKED**, full 2015–2026 historical KOSPI calendar not official-original certified. H5/Frozen, Champion, NetEV, seal/holdout unchanged; M20 profitability testing, real orders and funds movement not authorized; `ORDERING=false`.

**Result:** We have an evidence-based explanation for one 2017 count discrepancy stemming from an actual intra-year market closure amendment and an explicit historical as-of safeguard, not a verified source/PIT promotion.
