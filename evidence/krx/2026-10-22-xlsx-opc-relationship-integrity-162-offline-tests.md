# KRX holiday XLSX original package relationship fail-closed regression (2026-10-22)

Audit-only branch `indexalert-krx-pit-source-audit-20261013`; original KRX private data and Railway production deployment **not modified**.

## Meaningful finding and code safeguards

The existing XLSX holiday-export reader validated ZIP bytes, pinned original file hash, workbook/package root target, date rows, and declared OPC content types, but a workbook package could still carry **two .rels relationships using the same `Id`** when those entries had different `Type` values. Old checks filtered for only the expected `officeDocument` or `worksheet` link, allowing an unrelated duplicate ID to go unnoticed. Other clients may resolve duplicated OPC IDs ambiguously, so this cannot safely attest the exact document/row graph an operator would see.

The parser now requires every `_rels/.rels` and `xl/_rels/workbook.xml.rels` record to have a unique, nonempty relationship ID and the correct Relationships root; external targets stay rejected. Regression tests construct raw synthetic XLSX ZIP/XML bytes with duplicates in **both** root and workbook relationships and a missing ID, checking refusal without source/PIT authorization.

An additional implementation improvement on this same branch validates that `xl/styles.xml` and any `xl/sharedStrings.xml` document being parsed are **reachable via the actual workbook relationships**, rather than allowing unused ZIP decoy metadata to influence holiday dates. Previously valid synthetic workbook fixtures needed the corresponding real `styles` relationship and were updated; no production document verification was relaxed.

The existing content-type protection also requires valid `[Content_Types].xml` workbook, worksheet and style declarations and refuses duplicated/contradictory central declarations. All these checks concern only the original file parser's safe identity, never its true KRX authorship.

## Verified GitHub action

- [GitHub Actions run 39714202742](https://github.com/kims34/openpilot-opkr/actions/runs/39714202742): **SUCCESS; Ran 162 offline synthetic tests — OK**.
- Final tested code at `82a15b9f824a3fa7b494019201c20441c1ec37a5`; relevant changes at `9ea0b27e8a6fc446653317a46d53f1f0f7090560`, `4ff157e8642de9c472cb079419ee979479282781`, `ad1c78523c18ea81e7f8f788c91f1dd688d2a91a`, and `82a15b9f824a3fa7b494019201c20441c1ec37a5`.
- Two intermediate tests failed while implementation and synthetic fixtures were being updated; the **final result is 162/162 passed**. Do not cite intermediate CI failures as outstanding.
- No authenticated KRX OpenAPI calls, live orders, worker deploys, permission changes, protected volume reads or funds movements were performed in this validation.

## Original-data PIT boundary remains unchanged

- Previously witnessed protected historical KRX original storage receipts: **3,071** weekday SHA-backed pairs over pinned 2015 through 2026-10-08.
- **184** provider-empty weekdays remain ambiguous, **27** historical securities remain quarantined. The stored pairs' hash consistency is **not** exact original exchange holiday-calendar equality.
- Public KRX holiday notice PDFs and dated media corroborate select calendar events only; a complete original annually versioned/KOSPI-cash-specific historical exchange calendar with independent exact source-document SHA and earliest published/revised-at timestamps **has not been acquired**. Legacy `.xls` archives remain unsupported without a separate deterministic original-byte adapter.
- The existing Railway worker deployment `16c93d7c-7cd0-4d84-a327-298d2805376c` was last confirmed unchanged in prior repository work. **The Railway connector is not available in the current turn**, so current runtime status was not independently reverified today.
- The private date-set comparator stays undeployed and unexecuted on original worker files; source/PIT gates C and D, 27-security status verification, M20 true profitability, frozen Champion, independent holdout and any real trading remain **blocked**. `ORDERING=false`.

**Critical unblock is still actual original licensed KRX cash-market complete-year calendar bytes, full date and revision provenance, and authorized read-only day-level comparison on the protected worker.** Additional parser regressions alone do not unblock a single ambiguous original provider date.
