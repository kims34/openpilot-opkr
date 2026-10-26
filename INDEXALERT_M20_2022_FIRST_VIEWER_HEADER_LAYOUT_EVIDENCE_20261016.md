# IndexAlert M20 first-receipt 2022 Q3 — explicit financial table HEADER ROW source audit

**Status as prepared: official read-only query in progress; no PIT/performance authority.**

## Baseline from independently completed official source

On 2026-10-15, [official DART Actions #38731230183](https://github.com/kims34/openpilot-opkr/actions/runs/38731230183) passed both offline and source jobs. Four first-receipt fixed-cohort-slot-5 financial-viewer subsections contained 329 HTML tables and **two** tables with exact operating-income/loss label rows, each with at least four numeric-looking peer cells. **One** of the two tables contains both literal `당분기` and `전분기`; zero such tables contain the literal `3개월`, exact consolidated-income-statement title, full 2022 or 2021 July–September period windows or monetary unit lexical marker. That prior scan checked *text anywhere within the table*; it DID NOT establish that literal quarter wording was in an actual header row or linked it to numeric columns.

Source report: [2026-10-15 official table-Q3 evidence](INDEXALERT_M20_2022_FIRST_VIEWER_TABLE_Q3_EVIDENCE_20261015.md). Immutable status-only source artifact `11971011193`, digest `sha256:145cbca42fd9336f9a375aa8a9475f3f11464ca08795a0ba1b65935dc0a3a153`. Do not use original financial numbers from this artifact (none stored).

## New independent, guarded structure hypothesis

At source revision `ab5b7239c04606453ef698b7f55264d202dc118d`:
- `research_v1_opendart_m20_2022_first_viewer_header_layout.py`
- `test_research_v1_opendart_m20_2022_first_viewer_header_layout.py`
- `.github/workflows/indexalert-m20-viewer-header-layout.yml`

The new `HTMLParser` reconstructs **only bounded same-table per-row cell records in transient memory**, distinguishing cells of type `th` and `td`, explicit `rowspan`/`colspan`, and **rows preceding each exact-label operating-income row**. It counts how many candidate rows are preceded by formal TH cells, quarter-word pairs in preceding row(s), three-month/cumulative/third-quarter labels, spans, and four numeric-looking peers. It does not save raw text, financial amounts, issuer/receipt IDs, column positions or returned source HTML. Nested tables, malformed spans, unbalanced rows, oversized cells and source changes cannot promote any PIT flag.

[Source verification #38821429470](https://github.com/kims34/openpilot-opkr/actions/runs/38821429470) had **offline unit/security tests SUCCESS**. The official bounded, exact-first-receipt DART viewer source job was **running when this line was prepared**; no new official structure count may be claimed before reading completed job logs and artifact. Official request ceiling remains two registry/list calls and five public DART viewer GETs (one exact first TOC plus four financial sections), no broker or order calls.

## Decision boundaries

A formal TH/TD heading with `당분기`/`전분기`, even if discovered, does **not** independently bind the four numeric peers to originally published 2022-Q3 or 2021-Q3 **standalone three-month consolidated operating profit**, nor guarantee original edition immutability, dated source availability, units, account taxonomy, corporate-action correctness, or security PIT. No guessing a numeric column, no backfilling amended/current data, no redefinition of the frozen cohort.

`original_cfs_identity_and_profit_colmap_verified=false`, `original_2022_q3_standalone_cfs_operating_amount_verified=false`, `original_2021_q3_standalone_comparator_verified=false`, `historical_first_publication_instant_verified=false`, `m20_feature_pit_admitted=false`, `m20_performance_run_authorized=false`, independent Holdout and Champion promotion disabled, real orders/funds/account changes not authorized, `ORDERING=DISABLED`. Draft PR #412 unmerged.


## 2026-10-16 unsupported original SGML/HTML span — explicitly ambiguous

[First official source run #38821429470](https://github.com/kims34/openpilot-opkr/actions/runs/38821429470): the **offline regressions PASSED**, while the bounded original-first-filing DART source step **failed closed** with the known safe `HEADER_CELL_SPAN_INVALID` class. The original viewer response included at least one rowspan/colspan that did not meet the narrow parser's initial numeric-span budget/shape requirement. It is unknown whether this attribute is malformed, an intentional HTML idiom or a nonfinancial-layout element; the diagnostic did not persist the attribute value or its table. Therefore the first run yielded **no valid candidate-header count** and must not be called source success.

Follow-up code+tests+workflow commit `bb61dc5da281c1a0388575de3e13e9cc30caa5a0` explicitly **classifies unsupported span attributes as UNVERIFIED**, records only their counts, and preserves strict false flags for `original_profit_numeric_column_assignment_verified`, source accounting/CFS/period PIT and all trading permissions. An unsupported span in a profit candidate table is separately counted; other tables cannot transfer their layout uncertainty to a selected operating-income row, yet the full accounting association remains unverified regardless. Synthetic tests include out-of-range `colspan` and `rowspan=0` with no raw attributes released.

[Repaired official Actions #38822004271](https://github.com/kims34/openpilot-opkr/actions/runs/38822004271) has **offline tests PASSED** and official source query was **in progress when written**. Do not claim its source counts or success until the completed run and counts-only artifact can be verified.


## 2026-10-16 finalized official source outcome — PASS, original PIT remains BLOCKED

The first official [Actions #38821429470](https://github.com/kims34/openpilot-opkr/actions/runs/38821429470) passed offline tests but **failed its official read-only source test** with `HEADER_CELL_SPAN_INVALID`. This was a bounded parser incompatibility with one or more DART viewer rowspan/colspan source attributes; it was **not** a verified issuer accounting error.

Guarded follow-up source/test/workflow commit `bb61dc5da281c1a0388575de3e13e9cc30caa5a0` reclassifies unsupported cell spans as COUNTED UNKNOWN LAYOUT without interpreting them as column assignments. [Official revised run #38822004271](https://github.com/kims34/openpilot-opkr/actions/runs/38822004271) **completed SUCCESS for both offline and actual original-receipt DART source jobs** (max 2 official registry/list calls and 5 source-only public viewer GETs).

| Fixed first-edition, four-financial-section source-only metric | Official result |
|---|---:|
| Financial-viewer HTML tables | 329 |
| Exact-label operating-income candidate tables / rows | 2 / 2 |
| Candidate rows with four numeric-looking peer cells | 2 |
| Candidate rows with at least one preceding `TH` header cell | 2 |
| Candidate rows with any `당분기` or `전분기` wording in earlier rows | 2 |
| Candidate rows with **both** `당분기` and `전분기` in earlier rows | **0** |
| Candidate rows with both quarter terms within the **same** earlier row | 0 |
| Candidates with earlier `3개월` literal | 0 |
| Candidates with earlier `누적` literal | 0 |
| Candidates with earlier `3분기` literal | 0 |
| Candidates with earlier merged `TH`/`TD` cells | 2 |
| Unsupported span attributes anywhere in the 329 tables | 2 |
| Unsupported span attributes in candidate operating-income tables | **0** |
| Candidate operating rows in nested tables | 0 |

The earlier whole-table text test detected one profit table with both `당분기` and `전분기` **somewhere within its text**, but **none** of the exact profit candidates has both terms in rows *preceding* that profit row. This proves no numeric cell-to-three-month header grouping and cannot select a value. The two unsupported span attributes did not occur within the two profit candidate tables; exact raw span syntax, table location and financial amounts were intentionally not persisted.

Counts-only official artifact `12013358036`, sha256 `9c6aa171cf30902a502b611096587389d5ba5d8d99aadec5300d92fba1ebef66` (7-day retention). No original source/issuer/receipt, row/cell text, amounts, exact coordinates or credentials stored.

**NO-GO** for original 2022 and 2021 Q3 standalone three-month CFS operating-profit account/period/units/column facts and first-publication time; historical corporate/security PIT and original-to-correction cell lineage remain unverified. Earlier initial standardized XBRL was `014`; current normalized API separately unavailable (`013/014` class). `m20_feature_pit_admitted=false`, `m20_performance_run_authorized=false`, `independent_holdout_authorized=false`, `champion_change_authorized=false`, no real orders/funds/account changes and `ORDERING=DISABLED`. Frozen H5/M20 unchanged, Draft PR #412 unmerged. Next investigation must use independently versioned original structured accounting evidence rather than repeating weaker lexical proximity searches.
