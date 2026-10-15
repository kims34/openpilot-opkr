# KRX holiday export XLSX: hidden/filtered date-row fail-closed check

Reviewed on 2026-10-15 KST. Isolated research branch `indexalert-krx-pit-source-audit-20261013`.

## Concrete issue fixed

The prior XLSX reader verified raw file SHA, the displayed workbook sheet relationship, date cells, weekdays and the normalized sidecar claimed days. But it did **not** reject an XLSX worksheet with explicitly hidden calendar rows, hidden columns, zero-height rows/default, an auto-filter, or merged header cells. In those files, the underlying XML date list can be different from what a human inspecting the holiday spreadsheet sees. A sidecar matching those invisible date rows could misleadingly pass source-row equality.

[read_holiday_source_xlsx](../../research_v1_krx_calendar_xlsx_source_validator.py) now **fails closed** when it sees:
- row-level `hidden` flags or zero-height `ht=0` rows;
- worksheet `sheetFormatPr.zeroHeight=true` or any explicitly hidden column;
- worksheet `autoFilter` or `mergeCells`.

[Dedicated regression tests](../../test_indexalert_krx_calendar_xlsx_source_validator.py) build synthetic original XLSX ZIP/XML bytes with each of these six cases, verifying refusal before a source-row match, while the ordinary fully visible XLSX still passes the narrowly scoped row comparison.

## Verified execution

[GitHub Actions run #38690312700](https://github.com/kims34/openpilot-opkr/actions/runs/38690312700): **SUCCESS — 144/144 offline synthetic regression tests**, commit `608d2d926d155bd2238eb1f35a0b575fb43d8d18`. Code change committed as `24dc8e01560745062d95b1bd1616e6ddc2bb0535`.

No original KRX XLS/XLSX source bytes were acquired or licensed in this run. The 2017 third-party mirrored legacy `.xls` link remains unavailable through the public retrieval channel. This is a tested **parser safety/visibility invariant**, **not** authentication of an official KRX annual cash-equity calendar or source publication as-of.

Read-only Railway verification shows the original KRX worker is still running successful 2026-10-12 deployment `16c93d7c-7cd0-4d84-a327-298d2805376c`, attached volume `/data`, with no staged environment/service changes. Audit branch code **is not deployed**. The source's 3,071 hashed weekday checkpoints are storage-integrity proof only; **184** ambiguous provider-empty dates remain unverified date-by-date and **27** securities remain quarantined. Frozen H5/Champion, PIT, holdout, M20 profitability gates and `ORDERING=false` remain unchanged. No authenticated provider API calls, data export, trading orders, funds movement or permission changes.

Next meaningful prerequisite remains a legitimately obtained **original full-year official cash-equities trading calendar** with independently pinned source document bytes/timestamps, then authorized **read-only** day-level comparison inside the protected worker.
