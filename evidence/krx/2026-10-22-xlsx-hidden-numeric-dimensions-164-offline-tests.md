# KRX holiday XLSX: numeric invisible dimensions must fail closed

**Reviewed** 2026-10-22 KST on isolated branch `indexalert-krx-pit-source-audit-20261013`.

## Concrete issue and remedy

The XLSX date-row parser was hardened previously to reject explicitly hidden rows and columns (`hidden="true"`, `ht="0"`, `ht="0.0"` and `zeroHeight`), but it still permitted Excel-authored dimensions with equivalent numeric zero values:

- `<col min="1" max="1" width="0.00" customWidth="1"/>` masks the date column despite `hidden` not being set;
- `<row r="2" ht="0.000">` can mask one holiday date, bypassing literal `"0"`/`"0.0"` comparison;
- `<sheetFormatPr defaultRowHeight="0.000"/>` and `<sheetFormatPr defaultColWidth="0.00"/>` can make dates invisible by default without explicit `hidden`.

This matters because a sidecar SHA or row XML can match a private claimed holiday set while what an operator sees in the exported original XLSX omits some dates. A file-level hash alone only pins **the provided file**, not its actual readability or origin.

The [offline XLSX reader](../../research_v1_krx_calendar_xlsx_source_validator.py) now fails closed for **nonpositive, nonfinite, and malformed** explicitly declared numeric widths/heights, including sheet-format defaults, while leaving absent (normal workbook default) and positive dimensions supported. Numeric parsing does not perform external I/O, and the original rows/source SHA remain strictly bound. No lenient coercion, formula evaluation or source admission was added.

[New regression tests](../../test_indexalert_krx_calendar_xlsx_source_validator.py) cover decimal-zero column width, decimal-zero row height, default-zero row height, default-zero column width, and a good example with positive explicitly declared row/column dimensions. The synthetic fixture remains byte-level ZIP/OPC/XML, not private source data.

## Verified result

- Parser commit `5b296bfd1824f87ee7570f00532c3ae94735de86`.
- Tests commit `1611b250738a17b04a1e8e06fbbcae7dbf3a4f87`.
- [GitHub Actions **#39721289545**](https://github.com/kims34/openpilot-opkr/actions/runs/39721289545): **SUCCESS; Ran 164 offline tests, OK**.

## Source and trading gates unchanged

This proves **a parser safety regression has been fixed**, not that an authentic KRX versioned 2015–2026 annual cash-market holiday export was retrieved, a historically published/available-at calendar was established, or the private Railway original date receipts were compared day-by-day.

Prior verified storage-only scope remains **3,071** weekday SHA-backed pairs and **184** ambiguous original provider-empty weekdays; **27** historical names stay quarantined. KRX source/PIT contracts C/D, M20 net profitability and holdout, Frozen Champion promotion and real Tiny Live remain blocked; `ORDERING=false`. No additional authenticated KRX OpenAPI calls, original private `/data` reads, railway deploys/restarts, orders, broker/account permission changes or fund movement occurred in this review. Railway integration is not exposed to this turn, so current online worker status is **not independently re-checked today**.

**True next required evidence:** permitted original KRX yearly calendar bytes and version/first-publication history, independently pinned source-document SHA, authorized private execution of the exact historical day-set comparator against original SHA-backed receipts. Count equality or a successful XLSX parser is not an original session/PIT pass.
