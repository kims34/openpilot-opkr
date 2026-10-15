# KRX first-party year-end sources and corrected 2026 May20 public as-of boundary

Date: 2026-10-16 KST. Research-only audit branch: `indexalert-krx-pit-source-audit-20261013`.

## Primary KRX website source leads — meaningful evidence improvement

The original year-end evidence matrix already included a direct 2024 KRX KIND market notice and various broker/news republications. We located **KRX-hosted first-party KOSPI disclosure/listing handbooks** providing two further independent historical year-end event descriptions:

1. [KRX KIND original hosted KOSPI 2025 disclosure/listing handbook, pdf on first-party domain](https://kind.krx.co.kr/external/dst/reference/11635/%EC%9C%A0%EA%B0%80%EC%A6%9D%EA%B6%8C%EC%8B%9C%EC%9E%A5%20%EA%B3%B5%EC%8B%9C_%EC%83%81%EC%9E%A5%20%EC%97%85%EB%AC%B4%ED%95%B4%EC%84%A4%EC%84%9C.pdf), **PDF zero-based page 95 / printed page 096**, visually checked: December 29, 2025 **trading**, December 30 **last trading**, December 31 **year-end closed**. This is an illustrated 2025 dividend reference calculation, **NOT a complete official 2025 market session calendar nor proof it was public during 2025**. We did not obtain/download full binary for independent SHA or original version/first-availability authentication.
2. [KRX KIND original hosted 2023 KOSPI disclosure/listing handbook](https://kind.krx.co.kr/external/dst/reference/10827/%EC%9C%A0%EA%B0%80%EC%A6%9D%EA%B6%8C%EC%8B%9C%EC%9E%A5%20%EA%B3%B5%EC%8B%9C_%EC%83%81%EC%9E%A5%20%EC%97%85%EB%AC%B4%ED%95%B4%EC%84%A4%EC%84%9C.pdf) is search-indexed with the year-end 2023 example (Dec 28 final session, Dec 29 closed). **13 MB file exceeded our web reader full-download capacity, so we did not directly inspect or SHA-authenticate the original 2023 PDF page.** This is a first-party-hosted *search-index source lead only*, not original-page authentication.

A strictly typed [2023 and 2025 year-end primary-host evidence manifest](./2026-10-16-krx-primary-hosted-historical-year-end-market-guides.json) records the differing observation levels, year-specific dates, and all PIT/source/volume proof gates as false. Do not overwrite the earlier as-of candidates with retrospective handbooks or use an inspected first-party PDF sample as the **complete** annual original closure file.

## 2026 original-market event source timing improvement

Earlier [NewsPim article published 2026-05-20 10:58 KST](https://www.newspim.com/news/view/20260520000433) was the lower bound for the previous secondary-candidate validator. However, [Yonhap original report published **2026-05-20 10:34 KST**](https://www.yna.co.kr/amp/view/AKR20260520064200008) reported the very same KRX-announced KOSPI/KOSDAQ securities market closures on **2026-06-03** (local elections) and **2026-07-17** (Constitution Day). Both announcements are **ahead of the corresponding market holiday dates**. Publicly dated newspaper reporting is **not original KRX release** and never proves the private OpenAPI responses on those dates were empty.

The original first-party [KRX KIND KONEX closure notice `20260520000110`](https://kind.krx.co.kr/common/disclsviewer.do?acptNo=20260520000110&docno=&method=searchInitInfo) is dated May20 and mentions the same two closing dates, but **covers KONEX not KOSPI cash equities**, so its original filing cannot substitute for a KOSPI-specific market-source attestation. The original KRX-wide press-release exact first-publication instant is still unknown.

- Updated [2026 contemporaneous-news candidate manifest](./2026-10-14-krx-secondary-contemporaneous-notice-2026.json) with the earlier original Yonhap timestamp and independent first-party different-market KIND cross-reference.
- Corrected [as-of evaluator](../../research_v1_krx_2026_notice_asof_boundary.py): expose **secondary article evidence** at 10:34 KST onward, deny at 10:33:59, keep cash-KOSPI and KONEX separate, deny forged source/timestamp and all premature original PIT claims.
- [Regression tests](../../test_indexalert_krx_2026_notice_asof_boundary.py) cover those exact minute boundaries, bad source promotion and timestamp forgery.
- [GitHub Actions run #38821504163](https://github.com/kims34/openpilot-opkr/actions/runs/38821504163): **SUCCESS 152/152 offline tests**, commit `3b2a7f012a280bbed2c2243788d04e53d6bc2ea9`. The intermediate commit before updating pre-existing tests failed CI; final revision passed.

## True protected-source state (unchanged)

Railway `indexalert-krx-historical-worker` remained on 2026-10-12 SUCCESS deployment `16c93d7c-7cd0-4d84-a327-298d2805376c` with protected `/data` volume and original development branch. The separate GitHub audit branch was not deployed and no private raw date bytes were read.

**184** ambiguous source-empty weekdays remain **unclassified by official-date original receipts**; **27** securities remain quarantined. Source PIT C/D, M20 profitability, sealed holdout and real-trading authorization remain blocked, with Frozen/Champion unchanged, `ORDERING=false`, **no authenticated KRX API calls, account authorization changes or funds movement**. Source discovery adds public evidence but not original exchange file SHA/first-published-at/version or any actual date-by-date provider read. Retrospective market examples MUST NOT be retroactively injected into earlier trading-decision calendars.

**Next true unblock:** obtain permitted original full-year KOSPI cash equities market dates with publication/change history and document SHA, and execute the existing read-only comparison inside the authorized worker, recording sanitized SHA/count differences while not broadening data rights.
