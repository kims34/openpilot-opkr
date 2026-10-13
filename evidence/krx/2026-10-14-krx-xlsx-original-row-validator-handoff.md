# KRX historical holiday XLSX original-row checks — 2026-10-14

## Current independent audit status

**New code/CI verified. No real KRX original historical holiday file was retrieved and no private Railway weekday pair was compared. No source/PIT admission.**

- GitHub audit branch: `indexalert-krx-pit-source-audit-20261013`; only audit-branch code/tests/this report changed.
- [Successful CI run 38485800413](https://github.com/kims34/openpilot-opkr/actions/runs/38485800413) for code commit `be6a33d3ed66ae28631baae7826b90072ccc22c2`: **96 of 96 offline synthetic tests passed**. Prior transient CI failure between implementation and updating the test fixture was corrected.
- Railway historical worker still uses development branch `index-alert-position-regen-fix-v1`, last observed deployment `16c93d7c-7cd0-4d84-a327-298d2805376c` SUCCESS; no newer relevant logs. Protected raw market data remains on the service's private `/data` volume.
- Private source manifest remains **3,071 hash-bound weekday checkpoint pairs**, **184 provider-empty/source-versus-calendar unknown dates**, **27 historically uncertain securities quarantined**; exact-date source reconciliation and source PIT gate C/D remain **BLOCKED**.

## Important practical change from last turn

The previous offline [CSV row validator](../../research_v1_krx_calendar_csv_source_validator.py) matched `일자/요일/비고` source rows against a claimed closure-date list. But the actual KRX site's [holiday grid and download](https://open.krx.co.kr/contents/MKD/01/0110/01100305/MKD01100305.jsp) do not expose downloadable historical source-file bytes to this chat's web-readable view; the human-operated download can yield an Excel format, not necessarily CSV.

The new dependency-free [original XLSX row validator](../../research_v1_krx_calendar_xlsx_source_validator.py) accepts already-obtained private XLSX bytes, validates their pinned original document SHA against the metadata claim, safely opens **a narrow supported subset of XLSX using Python standard library**, extracts the actual visible first sheet's `일자/요일/비고` rows, and checks equality between parsed weekday dates and the sidecar claimed dates. It detects a workbook-to-sheet relationship redirect, an externally linked workbook, unexpected/hidden/multiple sheets, unsafe ZIP paths, formulas, duplicate dates, bad weekdays, unknown data types and unstyled numeric dates. It supports exact ISO date text and Excel serial date cells only where an explicit date style is declared. Any unsupported or ambiguous XLSX structure fails closed; legacy OLE `.xls` remains unsupported. Actual file type, contents and licence still need to be checked before running on a KRX export.

The existing [private year runner](../../research_v1_krx_private_calendar_year_runner.py) now automatically routes original ZIP/XLSX documents to the strict XLSX parser, other supported CSV to the CSV row parser, and refuses legacy XLS/HTML or any unparsed sidecar before invoking the SHA-bound private source date-set comparator. Tests include an attempted forged sidecar that differs from original XLSX rows, and verify no private audit is invoked for it.

## Security and evidentiary limits

The SHA comparison proves *only that supplied bytes match their pinned digest*. Neither manually asserted `source_page_url` nor the standardized XLSX file's presence independently authenticates the file as coming from the exchange. The first published 2015–2026 cash-equity holiday schedules, source revision/correction history, as-of public timestamp, rights to store/reuse, and all original member-security halt/resume/cleanup/delist/corporate-action histories are not supplied by this code.

KRX official site has a historical holiday [lookup/download UI](https://open.krx.co.kr/contents/MKD/01/0110/01100305/MKD01100305.jsp), but no actual dated spreadsheet bytes were available to the tools used here. No unsupported download endpoint, token replay, or unapproved KRX OpenAPI call was attempted. The Railway connector has **no private-volume shell/file-read action**; the comparator was not deployed or executed on the historical worker. Changing or redeploying the worker just to claim a comparison is not justified before an authenticated official holiday original is staged.

## Safe next original-data step

1. Obtain the historical KOSPI equities holiday spreadsheet through the exchange's permitted page/download mechanism, ensuring exact 2015–2026 annual market scope and source publication/version metadata.
2. Retain the **unmodified original bytes** privately and independently pin SHA-256; do not post originals or private stock data into GitHub public evidence.
3. Use the CSV/XLSX reader only if the source format is actually supported and each extracted date has been independently matched to the original official document. If the source is old XLS/OLE or encrypted/HTML, create an independently tested parser or keep the source unadmitted; no conversion accepted as original.
4. Run the existing private worker `_check_one` and exact date-set comparator **read-only**, with each year's original source snapshot hash and aggregate empty-count pin; export only aggregate counts/digest.
5. Regardless of date-set match, the 27 securities remain blocked; no M20 profit performance or live trading until other pre-registered gates pass.

**Trading and research invariants**: Frozen/H5, Champion, Holdout unchanged; `ORDERING=false`; no real orders, money movements or broker permissions change.
