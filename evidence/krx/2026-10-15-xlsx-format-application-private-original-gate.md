# KRX cash equity holiday XLSX display-style hardening

Reviewed 2026-10-15 KST. Isolated audit branch `indexalert-krx-pit-source-audit-20261013`.

## Practical parser bug fixed

The original-byte-bound XLSX validator checked a numeric Excel serial cell's `numFmtId` but did not inspect an explicitly disabled `applyNumberFormat` attribute. An XLSX with `xf numFmtId="14" applyNumberFormat="0"` could therefore be treated as an operator-visible full calendar date even though the number format was explicitly disabled. Another ambiguity was a custom `numFmt` trying to redefine reserved Excel built-in IDs. Both cases are now rejected, rather than treating the date serial as verified visually displayed holiday dates.

Updated [reader](../../research_v1_krx_calendar_xlsx_source_validator.py) refuses `applyNumberFormat="0"` / `"false"` on accepted date styles and rejects custom numbering formats with IDs below 164 or duplicate custom numbering IDs. [Regression tests](../../test_indexalert_krx_calendar_xlsx_source_validator.py) exercise false/zero/uppercase disabled flags, explicitly applied good date styles, and reserved built-in format overrides. Existing regular CSV and plain date cell validation remains unchanged.

[GitHub Actions run #38705795464](https://github.com/kims34/openpilot-opkr/actions/runs/38705795464): **SUCCESS, 149 / 149 synthetic and offline tests**, code commit `4f5dbdc1ab63f8dda9f4ded41989a1274f59e7d3`. No KRX protected provider calls, Railway shell execution or deployed service changes in this work.

## What this does not resolve

KRX Data Marketplace publicly describes CSV / Excel / PDF downloads, but the official KRX holiday schedule export path cannot be read as full original date rows via the current public text tooling; access to the two historical KRX holiday page URLs returned HTTP 403 in this inspection. [Official KRX Data Marketplace help](https://data.krx.co.kr/contents/MDC/INFO/informationController/MDCINFO002.cmd) confirms general download capabilities, not that a 2015–2026 PIT-appropriate, versioned calendar archive was actually retrieved. Do not synthesize missing official files from those help pages or from the secondary XKRX calendar.

No 2015–2026 date-complete original public KOSPI cash-equity trading schedule has been acquired or version/first-publication-time authenticated. The Railway worker `indexalert-krx-historical-worker` retains its 2026-10-12 successful deployment `16c93d7c-7cd0-4d84-a327-298d2805376c` on development branch, with restricted volume `/data`. The audit code on this separate branch has **not** been deployed or executed against the original worker.

As a result the **184 ambiguous source-empty days remain unverified** and **27 historical securities remain quarantined**; previous original-storage hashes are not PIT market session proof. M20 performance, independent holdout, source contracts C/D, Champion promotion and real orders remain unauthorized. `ORDERING=false`; no funds or accounts changed.

**Critical unblock:** obtain a permitted, original, full-year KOSPI cash-equity market calendar for each required historical period, with exact original document hash and historical availability/version evidence, stage it only in the protected environment and run the already implemented **read-only private full-date original receipt comparison**. Log only non-sensitive aggregate comparison/sha results; no provider re-download or orders.
