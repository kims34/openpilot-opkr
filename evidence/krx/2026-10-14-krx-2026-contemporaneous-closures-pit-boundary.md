# 2026 exceptional KRX cash-equity holiday notices — time-bounded secondary evidence

**Updated 2026-10-14 KST.** Branch `indexalert-krx-pit-source-audit-20261013`. **NOT ORIGINAL KRX NOTICE, NOT HISTORICAL MARKET-DATA PIT CERTIFICATION.**

## Verified bounded finding

The public [KRX holiday page](https://open.krx.co.kr/contents/MKD/01/0110/01100305/MKD01100305.jsp) exposes date search/download controls and the `일자 / 요일 / 비고` grid, but its web-readable initial response contained no populated daily data and no independently downloadable 2015–2026 official original holiday dataset. This run did not invent a dynamic query or download API endpoint and did not make any protected KRX OpenAPI call.

Contemporaneous [NewsPim article, **2026-05-20 10:58 KST**](https://www.newspim.com/news/view/20260520000433) reports KRX's announcement that **Wednesday 2026-06-03 (local election)** and **Friday 2026-07-17 (Constitution Day)** would close the cash securities market, together with other relevant markets. [MBC 2026-05-20 reporting](https://imnews.imbc.com/news/2026/econo/article/6823907_36932.html) independently describes the same KRX-attributed announcement. Article publication at 10:58 KST bounds **the newspaper report's availability**, not the earlier original KRX notice's precise first public timestamp.

These two dates agree with the **two extra 2026 reported exchange closures omitted from the `exchange_calendars/XKRX 4.13.1` candidate annual count exercise**. This is materially stronger public dating evidence for those two expected exceptional closures, but **not proof of either date appearing among the 14 private 2026 provider-empty daily receipts** and does not resolve any part of the 184-day original KRX private-calendar/source-set mismatch by itself.

## Reproducible offline evidence

- [Two-date secondary notice manifest](./2026-10-14-krx-secondary-contemporaneous-notice-2026.json) pins article URLs, its actual reported publication timestamp, market scope, 2026-06-03 / 2026-07-17, and explicitly false original KRX verification/PIT/authorizations.
- [As-of checker](../../research_v1_krx_2026_notice_asof_boundary.py) distinguishes original KRX notice authentication (unknown) from newspaper availability (article publication time). It refuses to treat the newspaper report as known before 2026-05-20 10:58+09:00; even after that time its output remains a **secondary news candidate only**, never an original exchange-source status or broker trading permission.
- [Synthetic and manifest regression tests](../../test_indexalert_krx_2026_notice_asof_boundary.py) include forged original-KRX notice admission, backdated as-of claims, later publication than the closure, unsupported non-KST timestamps, and mismatch against prior secondary annual count evidence.
- [GitHub Actions 38498688545](https://github.com/kims34/openpilot-opkr/actions/runs/38498688545): **SUCCESS, 103/103 tests**, commit `0d75bce7f6dd927e638dfa1e7ad201c31eac2b16`. All tests run on safe metadata/synthetic inputs, without reading protected daily market records or sending additional provider requests.

## Live private-data boundaries

Read-only Railway service inventory showed `indexalert-krx-historical-worker` SUCCESS deployment `16c93d7c-7cd0-4d84-a327-298d2805376c` from development branch `index-alert-position-regen-fix-v1`, attached volume `/data`. The worker has the `KRX_PRIVATE_RAW_DIR` environment **variable name** registered; its value was not read. Runtime command remains `research_v1_krx_openapi_missing_2017_2022_integrity_audit.py --audit`; no live service change was staged. The isolated research branch code is not deployed to this worker and the tools have no private mounted-volume shell. No real source date-level comparison executed.

**Remaining truthful gate state:** original source pairs integrity checkpoints **3,071**, KRX session/source ambiguous days **184**, privately quarantined problematic historical securities **27**. Historical original KRX dated cash equity holiday source, complete issuer historical status/identifier and first-publication PIT remain outstanding. Source contracts C/D **BLOCKED**. Independent M20 profitability run, holdout, Champion promotion, broker order, funds movement **NOT AUTHORIZED**. `ORDERING=false` frozen.

## Next source evidence needed

A permitted, unmodified annual original KRX holiday export for 2015–2026 with independent document provenance and issue/version timestamps, **plus authorized private execution** of the already-coded row validator and year SHA-bound receipt comparator on the attached volume. Source material should stay within its authorized private storage. No public KRX page scrape, copyrighted original data publication or extra provider OpenAPI 6-GET repeat is authorized by this note.
