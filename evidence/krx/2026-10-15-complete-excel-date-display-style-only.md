# KRX holiday XLSX original-row preflight: full date displayed or fail closed

Reviewed 2026-10-15 KST, audit-only branch `indexalert-krx-pit-source-audit-20261013`.

## Concrete correctness defect

The prior strict XLSX parser allowed Excel numeric date styles 16 (`d-mmm`) and 17 (`mmm-yy`) as evidence that an operator would see **year, month and day** in the displayed holiday cell. Both styles conceal a required field, even though the internally stored Excel serial is a complete date. This is insufficient when independently comparing an external claim against the human-visible original file.

It also decided an arbitrary custom numeric format was a full date if the formatCode contained the substrings `yyyy`, `mm` and `dd`, enabling a numeric cell formatted as `0"yyyy-mm-dd"` to be incorrectly recognized. The quoted suffix renders as literal words alongside the numeric value, not as a full date.

**Source:** [Microsoft Open XML numbering format specification](https://learn.microsoft.com/en-us/dotnet/api/documentformat.openxml.spreadsheet.numberingformat) documents built-in styles 14, 15, 16, 17 and 22. [Microsoft Office Open XML number format details](https://learn.microsoft.com/en-us/openspecs/office_standards/ms-oi29500/17d11129-219b-4e2c-88db-45844d21e528) documents Korea-specific built-in 55 (`yyyy-mm-dd` / `yyyy/mm/dd`).

## Remediation

- [XLSX original-row reader](../../research_v1_krx_calendar_xlsx_source_validator.py): permitted full-calendar built-in date formats now `14,15,22,55`. **16 and 17 rejected**.
- Accept custom styles only from an explicit small set of full date patterns (such as `yyyy-mm-dd`, `yyyy/mm/dd`, `dd/mm/yyyy`) rather than substring heuristics.
- [Regression tests](../../test_indexalert_krx_calendar_xlsx_source_validator.py): 3 new tests with synthetic ZIP/XML bytes for both incomplete built-in dates, 6 deceptive custom styles, and accepted full-date built-ins including Korean 55, plus valid custom styles.
- [GitHub Actions #38690744114](https://github.com/kims34/openpilot-opkr/actions/runs/38690744114): **SUCCESS, 147/147 offline tests** on commit `82d37bf53e514e086ae3070c1e435ce208f1c43b`. Parser change commit `8a6928bbf378c7e075ddfdb44bed9d31db6ba7c7`.

## Source and trading boundary

This fixes a **parsing correctness defect only**. The actual full-year KRX original exports, independent source SHA/provenance, and historical publication as-of remain unavailable in this run. The original private Railway KRX worker still runs the 2026-10-12 successful deployment `16c93d7c-7cd0-4d84-a327-298d2805376c` from development branch with its protected `/data` mount; no volume reading, restart or deployment was performed.

**184** private source-empty dates remain ambiguous; **27** historical securities are still quarantined. Source contracts C/D, independent M20 profitability/holdout, Champion promotion and live orders remain **blocked**; `ORDERING=false`. No extra authenticated KRX requests, funds transfer, or broker action.
