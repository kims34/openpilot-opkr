# M20 2022 Q3 earliest DART viewer TOC cross-check — official success

**Date:** 2026-10-15 (KST)
**Status:** SOURCE-METADATA GATE PASSED; M20 PIT / actual profitability / Holdout / live remains **NO-GO**.
**Proof:** [Actions #38678909079](https://github.com/kims34/openpilot-opkr/actions/runs/38678909079) — **offline safety PASS** and **real read-only OpenDART + first-receipt DART viewer PASS**.

## Why this is different

Previous SHA-pinned first-filed SGML `document.xml` inspections found 1,570 tables, 15 operating-profit/loss text-row candidates, zero `SECTION` or `SUBSECTION` tags and zero exact CFS title / standalone Q3 2022 and 2021 date-window bindings. Those searches cannot establish consolidated standalone 3-month financial cells. The current normalized CFS API independently returned a `013/014` missing-data/file class; original XBRL archive separately returned `014`.

This verification uses a **second DART-host viewer representation**, not new proximity scans of the same original SGML. It resolves the *strictly first submitted* 2022 Q3 receipt from the existing fixed cohort slot 5 official registry+index, then requests `https://dart.fss.or.kr/dsaf001/main.do` **once**, without including the API secret in that public call. All requests are bounded, HTTPS-only, no redirects, no raw HTML or financial values saved. The original selected receipt is private to the process. Two official API calls plus one public viewer request maximum.

The viewer's JavaScript TOC records (similar to OpenDartReader's documented public `sub_docs` interface) are validated for the exact original receipt, with mismatched receipts hard-stopped.

## Real official source-only counts

| Result | Value |
|---|---:|
| Exact first receipt TOC records found | **62** |
| Generic financial-statement headings in TOC | **4** |
| Notes headings in TOC | **2** |
| Exact `연결손익계산서` / `연결포괄손익계산서` TOC headings | **0** |
| `dart3.xsd` viewer query parameter present | **true** |
| Structured CFS original section/financial period binding | **false** |

A `dart3.xsd` query-parameter label is **not** a validated XSD file or official specification. It also does not bind current/prior quarter earnings cells, reporting entity, currency or original availability time. The TOC title labels may be generic; **no authoritative CFS operating-profit fact is inferred**.

## Evidence and isolated code

- Source: `research_v1_opendart_m20_2022_first_viewer_toc.py`
- Unit tests: `test_research_v1_opendart_m20_2022_first_viewer_toc.py`
- Dedicated CI: `.github/workflows/indexalert-m20-2022-first-viewer-toc.yml`
- Official successful source commit: `98a7506e980382c15e89355557d6f1f1b8762b52`
- Flags-only artifact ID `11947372356`, ZIP digest `sha256:4ebad37517994eb7fa41012a90061200746656ffbb021a072d71d04b1460d3c4`, 7-day retention.

Official background documents:
- https://opendart.fss.or.kr/guide/main.do?apiGrpCd=DS001 — official disclosure original download API catalogue.
- https://opendart.fss.or.kr/guide/main.do?apiGrpCd=DS003 — original XBRL and structured accounts are separate endpoints.
- Public OpenDartReader `sub_docs()` implementation is **non-authoritative supporting code**, not a grant of historical PIT validity.

## Next gates — remain separate

1. Privately map the four generic first-receipt financial-statement TOC entries into exact original viewer subdocuments and source/statement/period labels *without saving values or identifiers*. Reject multiple versions or ambiguous sections.
2. Independently verify exact 2022 Q3 and comparative 2021 Q3 three-month CFS operating-profit facts with monetary units and source edition, rather than choosing a candidate earnings row by adjacency.
3. Obtain trustworthy historical public availability time and issuer/security history separately. DART viewer metadata does **not** certify intraday first publication; a 2022 date in an index is not a timestamp.

**Unchanged:** Frozen H5/M20, fixed cohort slot, original report selection, Champion, taxes/costs, Purged/CPCV, Walk-Forward and Holdout. `m20_feature_pit_admitted=false`, `m20_performance_run_authorized=false`, `real_orders_authorized=false`, no funds/permissions changes and `ORDERING=DISABLED`. Draft PR #412 remains unmerged.
