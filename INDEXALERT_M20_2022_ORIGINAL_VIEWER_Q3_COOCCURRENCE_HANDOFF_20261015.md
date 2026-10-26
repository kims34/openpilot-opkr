# IndexAlert M20: first-submitted 2022 Q3 DART viewer source-subdocument correlation

**Safety: no PIT feature admission, no M20 return estimates, no independent Holdout and no real orders.**

## Confirmed by completed read-only official source

[GitHub Actions #38706084440](https://github.com/kims34/openpilot-opkr/actions/runs/38706084440) (commit `595743780a11b203fa37e29dbb3a83e5c4ba31d4`) **passed both offline source tests and official DART original viewer queries** on 2026-10-15. Exactly **four financial-statement-associated entries** linked to the frozen slot-5 original 2022 Q3 first receipt were read from the original DART viewer's table-of-contents metadata. Four viewer sections returned HTML and collectively contained **329 table tags** and **two exact-label operating-income row candidates**. Of the four, two contained lexical exact consolidated-income-statement titles, two contained literal `3개월`, and all four mentioned both calendar years. Raw amounts, full HTML, receipt and issuer identifiers, secret credentials and subdocument URLs were not retained. Official counts-only artifact ID `11958577751`, digest `sha256:6968c8d31404b8fc87f2c08d0bb92e00c7fd72c564d20f46f2994cb0a808d106` (7-day retention).

The above source **does not prove which viewer subdocument contains which operating-profit line, or how the original cells align with actual standalone third-quarter periods**. Lexical year mentions are insufficient. Earlier original 2022 first-filing SGML ZIP SHA pin remained verified but had 15 unbound operating-profit candidates and lacked explicit CFS section/period bindings. Current normalized 2022 Q3 financial API remained unavailable, and original 2022 XBRL separately gave `014`.

## Follow-up: pre-registered narrow same-subdocument source-shape test

New isolated code `research_v1_opendart_m20_2022_first_viewer_cooccurrence.py`, offline test `test_research_v1_opendart_m20_2022_first_viewer_cooccurrence.py`, and `.github/workflows/indexalert-m20-viewer-section-cooccurrence.yml` test whether the same original first-receipt financial-viewer subsection shows an operating-profit text row alongside CFS headings, literal three-month labels and *complete* 2022/2021 July–September date spans. Counts only; no original cell or version binding is admitted even if all hints coexist. Up to two official API reads and five bounded public-viewer GETs with no credentials in public requests. SHA/workflow source commit `8703a83d5430b064b3e67d2091c912d034c6c60e`.

[Follow-up Actions #38708786002](https://github.com/kims34/openpilot-opkr/actions/runs/38708786002) had **offline security regressions SUCCESS**; its actual official DART source job was **still in progress at this note's authoring**. Do not publish new same-subdocument counts or claim success until completed official logs and artifact are verified. The separate offline TOC-safety job previously failed because it omitted `requests`; later code commits already installed the offline dependencies and later corresponding offline runs succeeded. This was CI environment setup, not a financial source discovery.

## Strict independent blockers

Exact **first-original** 2022 Q3 consolidated standalone three-month operating income and 2021 Q3 three-month comparator, monetary unit, row/statement period identity, full corrected filing vintage lineage, historical public release instant and issuer/security survivorship-safe mapping are **not verified**. A DART viewer is a rendering and may be altered; the first receipt number alone does not independently prove immutable historical availability. Do not backfill revised values. Maintain all frozen H5/M20 definitions, champion, taxes/costs, PIT, Walk-Forward/CPCV, independent Holdout and real trading limits. `m20_feature_pit_admitted=false`, `m20_performance_run_authorized=false`, `independent_holdout_authorized=false`, `champion_change_authorized=false`, `real_orders_authorized=false`, `funds_movement_authorized=false`, `permissions_change_authorized=false`, `ORDERING=DISABLED`.

Research Draft PR #412 must stay unmerged while authoritative source/PIT data remain missing.


## 2026-10-15 official conclusion — source-only cooccurrence SUCCESS, original PIT still NO-GO

[Actual official run #38708786002](https://github.com/kims34/openpilot-opkr/actions/runs/38708786002) completed with **both offline and official jobs SUCCESS**. It ran the bounded exact-first-receipt fixed slot-5 2022-Q3 DART viewer source, selecting the four generic financial TOC subsections. Every count below is a **same-rendered-viewer-subdocument text hint** and does not identify a precise accounting table, cell, currency, or historical public availability:

| Pre-registered source diagnostic | Official count |
| --- | ---: |
| First-original finance viewer subsections | 4 |
| Exact operating-profit row text candidates in those subsections | 2 |
| Subsections with operating-profit row + exact CFS income statement wording | **1** |
| Subsections with operating-profit row + literal three-month wording | **1** |
| Subsections with operating-profit row + complete 2022 July 1–September 30 date window | **0** |
| Subsections with operating-profit row + complete 2021 July 1–September 30 date window | **0** |
| Subsections with operating-profit row + both full period windows | **0** |
| Subsections matching operating-profit, CFS wording, three months and both full windows together | **0** |

The two counts of one do **not** certify they are the same specific source subsection; no account/currency/fact or edition tie is established. This narrows subsequent manual original-document provenance work to at least one lexical consolidated earnings subsection, but **2022/2021 Q3 quarterly CFS operating-income values remain unverified**. No PIT vintage is admitted. The current normalized 2022 Q3 CFS API previously returned an unavailable class `013/014`; the independent 2022 first-report XBRL route returned `014`.

Official immutable status-only artifact `11958909398`, digest `sha256:d615ae2888883df0fe1cb7ce093cc4ed4faa84ef8b8ebca39785ef74b83f8aa3`, 7-day retention. Source+test+workflow code SHA `8703a83d5430b064b3e67d2091c912d034c6c60e`. The independently added offline TOC safety CI initially failed because `requests` was not installed; subsequent revised offline-only runs completed SUCCESS, which cannot be confused with first-receipt official source verification.

**Decision: preserve frozen M20 and research holdout exactly as before.** `original_2022_2021_three_month_cfs_profit_values_verified=false`, `m20_feature_pit_admitted=false`, `m20_performance_run_authorized=false`, `independent_holdout_authorized=false`, `champion_change_authorized=false`, `real_orders_authorized=false`, `funds_movement_authorized=false`, `permissions_change_authorized=false`, and `ORDERING=DISABLED`. Draft PR #412 must remain unmerged.
