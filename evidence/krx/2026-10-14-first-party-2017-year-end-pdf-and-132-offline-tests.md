# KRX primary-domain public market-notice cross-check — 2017 year-end

**Reviewed:** 2026-10-14 16:20 KST. **Research-only, isolated audit branch** `indexalert-krx-pit-source-audit-20261013`.

## New first-party source found

Official Korea Exchange domain, directly indexed **PDF**:

[KRX Market Schedule in December 2017 and Trading Hours on January 2, 2018](https://www.krx.co.kr/res/pc/banner/2017marketinfo_en.pdf).

The **search-indexed PDF text** states:
- **2017-12-28:** last 2017 stock-market trading session.
- **2017-12-29:** 2017 year-end market holiday, no settlement.
- **2018-01-02:** KOSPI/KOSDAQ/KONEX stock-market regular session's opening time shifted from 09:00 to **10:00**, regular close remains 15:30.
- **Scope exclusion:** KRX OTC CCP does not have the stock-market year-end holiday exception; this must not be incorrectly mapped to the KOSPI cash market.

This cross-corroborates the **2017-12-29** closure candidate in [July 2017's 16-day secondary KRX holiday export transcription](https://financedata.github.io/posts/pandas-market-days-krx.html), and is independent public evidence for the **2018-01-02 10:00** exceptional cash-equity opening. The January 2 late opening **is NOT a full-day holiday**, nor proof of 2018 open-market price values. Year-end late-open events are distinct from 2017's later-confirmed October 2 extraordinary closure.

**Vital source limitation:** Web search indexed KRX PDF contents, but the available direct PDF byte retrieval/rendering failed. **Original PDF binary hash, revisions and first-publication timestamp were NOT authenticated or pinned.** The search-index result's crawl/publication metadata is **not** a reliable original 2017 source publication instant. This is *one first-party-hosted market notice lead*, not complete first-party date-canonical market calendar evidence for 2015–2026.

## Concrete implementation and CI

- [Market PDF source-specific evidence manifest](./2026-10-14-krx-official-2017-year-end-market-pdf-source.json), recording source URL/host, three typed KOSPI market events, year-end OTC CCP exception, and all unknown PIT/source-first-publication flags.
- [Strict public source event cross-check](../../research_v1_krx_official_2017_notice_crosscheck.py): refuses to substitute an OTC CCP market event, reinterpret Jan 2 10:00 opening as closure, or assert a 2017-10-02 holiday as present in the July version. Checks original PDF bytes and original first-published-at are **not claimed verified**.
- [Cross-check regression tests](../../test_indexalert_krx_official_2017_notice_crosscheck.py), including mistaken Jan 2 classification, false official PDF integrity claims and KOSPI/OTC scope confusion.
- [GitHub Actions run 38528243646](https://github.com/kims34/openpilot-opkr/actions/runs/38528243646): **SUCCESS, 132/132 offline tests**, commit `60f83115975bf969dfde26ebd5ad69f1a62acba5`.

These tests exercise code and provided evidence metadata only, **not** live KRX holiday API output or original PDF bytes. The available public KRX [holiday query/download](https://open.krx.co.kr/contents/MKD/01/0110/01100305/MKD01100305.jsp) showed an empty initial grid without per-year server data, and no supported direct no-auth calendar export or archived PDF bytes were accessible in this session. No provider OpenAPI calls were made or repeated.

## Actual private source state, unchanged

Railway `indexalert-krx-historical-worker` remains on successful Oct 12 deployment `16c93d7c-7cd0-4d84-a327-298d2805376c`, mounted private volume `/data`, development branch `index-alert-position-regen-fix-v1`. Previous pass compared six-year 2017–2022 original audit receipt hashes/counts to the sanitized GitHub manifests **6/6 exact matches**, which confirms receipt consistency only.

**3,071 SHA-backed weekday original checkpoint pairs, 184 provider-empty ambiguous dates, 27 quarantined historic securities** are unchanged. No private per-day source-empty receipts were directly checked against 2017-12-29 or any other public holiday. Original KRX calendar PIT source gates C/D **BLOCKED**, M20 profitability run and independent holdout **NOT AUTHORIZED**. Frozen H5, Champion baseline and `ORDERING=false` preserved. No live trading, account/broker permissions modification, extra authenticated KRX GETs, funds movement, Railway restart/deploy or private raw data disclosure.

**Next meaningful unlock:** obtain permitted official KOSPI cash market holiday annual original exports and historical publication/version lineage; then run the already coded **read-only Railway private snapshot SHA/date-set comparator**. The current connector cannot access the mounted worker volume or execute commands therein. A single notice cannot substitute for complete date-set original proof.
