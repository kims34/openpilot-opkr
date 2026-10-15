# M20 2022-Q3 fixed original viewer: table-level period wording check

**Date:** 2026-10-15 (KST). **Source accounting/PIT decision: NO-GO.**

## Independently verified previous run

Actual bounded read-only [official source run #38708786002](https://github.com/kims34/openpilot-opkr/actions/runs/38708786002) **PASSED both offline and official source jobs**. Exactly four first-submitted fixed slot-5 DART public viewer financial subsections were inspected. They contained two exact-label operating-income row candidates; one subsection contained an operating-profit row and consolidated-income heading text; one contained an operating-profit row and a literal three-month token. **No** such subsection included the complete 2022-07-01 to 2022-09-30 or 2021-07-01 to 2021-09-30 source date-window text, and zero combined all source hints. **The two 'one' counts may concern different subsections** and cannot be joined. Counts-only evidence artifact `11958909398` / sha256 `d615ae2888883df0fe1cb7ce093cc4ed4faa84ef8b8ebca39785ef74b83f8aa3` (7-day retention). DART original receipt metadata is tied to the fixed 2022 Q3 first filing, but the viewer is only a rendering, not immutable fiscal-PIT evidence.

## New separate TABLE-level (rather than subsection-level) research audit

Added bounded source-only `research_v1_opendart_m20_2022_first_viewer_table_q3.py`, synthetic offline tests `test_research_v1_opendart_m20_2022_first_viewer_table_q3.py` and workflow `.github/workflows/indexalert-m20-viewer-table-q3-source.yml`, source commit `af048d8d202d63a6fb41527e622658588cb1f339`. It reuses the same four first-filing financial TOC sections and performs only bounded read-only HTML table-structure checks. An exact operating-profit row must be inside the same parsed table as any three-month *text*, current/prior quarter text, 2022/2021 full Q3 dates, numeric-peer cell shapes, unit words, or CFS title words. Nested table candidates are separately flagged rather than conclusively assigned. The literal text `3개월` anywhere in the table **does not establish a column heading**, and no accounting cells or amounts are persisted.

[Actual GitHub Actions #38731230183](https://github.com/kims34/openpilot-opkr/actions/runs/38731230183) had **offline tests PASSED**, official 4-section source job **IN PROGRESS at document creation**. No new official table-level counts are claimed here; they require the completed source job and status-only artifact verification.

The previous 2022 original XBRL endpoint returned `014`; current normalized 2022 Q3 CFS endpoint failed closed as unavailable (`013/014` source class). No qualified first-original 2022 Q3 and comparative 2021 Q3 *standalone three-month CFS operating-profit accounts and values*, currency, exact original publication time, amendment-to-cell lineage, or historical issuer↔security PIT mapping is established. Keep source-current viewer data out of any backfilled historical features.

Frozen H5/M20, cost/tax model, PIT, Holdout, Champion and any Railway/broker ordering settings remain unchanged. `m20_feature_pit_admitted=false`, `m20_performance_run_authorized=false`, `independent_holdout_authorized=false`, `champion_change_authorized=false`, `real_orders_authorized=false`, no funds or permissions, `ORDERING=DISABLED`. Draft PR #412 remains unmerged. No new scheduled task created.
