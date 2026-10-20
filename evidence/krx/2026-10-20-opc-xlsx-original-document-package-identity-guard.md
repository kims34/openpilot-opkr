# Offline KRX XLSX original-file package integrity: OPC root and content types

Review date: **2026-10-20 KST**. Non-deployed isolated branch: `indexalert-krx-pit-source-audit-20261013`.

## Real unsafe acceptance path removed

[Prior strict holiday XLSX reader](../../research_v1_krx_calendar_xlsx_source_validator.py) already verified the raw source SHA-256 against the independent expected document digest and separately checked `xl/workbook.xml` -> `xl/worksheets/sheet1.xml` relationships. However, it could **incorrectly accept ZIP packages that were not valid workbooks**, where `_rels/.rels` was absent or pointed at a different root document, and where `[Content_Types].xml` had missing/ambiguous workbook or worksheet declarations. It could therefore parse a decoy `xl/workbook.xml` plus `sheet1.xml` that an ordinary Office application would not actually open as the asserted spreadsheet.

### Source-code fix

- `_rels/.rels` is now required and its sole `officeDocument` relationship must target the canonical `xl/workbook.xml` (allowing both package-root relative forms).
- `[Content_Types].xml` is parsed. It must declare the canonical workbook and worksheet OOXML MIME types; if styles are supplied the styles OOXML type must also be declared. Absent, duplicate, and contradictory overrides fail closed.
- Existing single visible worksheet, worksheets' relationship binding, explicit complete-date styles, hidden/filtered row controls, and content SHA/claim comparison still apply.
- These are strict format identity/consistency checks only. They do **not** authenticate the content's KRX origin, original publication date, document rights or historic PIT availability.

### Tests and execution

The [synthetic XLSX tests](../../test_indexalert_krx_calendar_xlsx_source_validator.py) now build fully anchored OPC container metadata and cover missing/misdirected/duplicate root document relationships, missing workbook content type, wrong worksheet type, duplicate type declaration, valid relative root paths, and unchanged date-row reconciliation.

[GitHub Actions run **#39347457419**](https://github.com/kims34/openpilot-opkr/actions/runs/39347457419) **SUCCESS, 157/157 offline tests** at commit `e7ca10da86575cb71eea60d645382ee30d940262`; initial root relationship guard commit `ee22283524aa4c761a27f58aa978c7e69ff971a4`, initial content type guard `531a8abeef5ae66a0acd684ced1ef902d3e67123`. Two intermediate CI runs failed because the old synthetic ZIP fixtures omitted required package metadata; final repaired standards-typed synthetic fixtures passed. No genuine source bytes or private KRX data were placed in CI.

## Source/PIT gate and Railway operational boundaries unchanged

The authorized original worker `indexalert-krx-historical-worker` was last verified unchanged from the **2026-10-12 SUCCESS** deployment `16c93d7c-7cd0-4d84-a327-298d2805376c`, on the original development branch with protected `/data` mount. The audit branch code is not deployed. No new authenticated KRX original market-data API requests, no credentials, restarts, service configuration changes, model backtest/holdout orders, or funds movements occurred.

The prior documented **12/12 annual stored original receipt count/empty count/SHA equality** (3,071 weekday SHA-backed pairs) remains storage-only provenance; **184** weekday original responses are still not matched date-by-date to a full-year *official original, historically versioned* KOSPI cash equity calendar. The 2025 partial first-party long-holiday PDF remains **15 KRX source-calendar weekday candidates** only, not 15 cleared private dates or a complete calendar. **27** quarantined securities are not released. Source C/D, historical-security-status PIT, M20 profitability, independent holdout and Tiny Live remain blocked; **`ORDERING=false`**.

Next: Acquire lawful original date-complete year-by-year KRX cash-market holiday export and publication/version record; pin exact original bytes and SHA, stage only in the protected worker; run the existing read-only annual exact date-set verifier under separate authorization. Unsupported legacy binary XLS must remain rejected absent a independently reviewed original-format parser.
