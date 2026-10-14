# KRX official holiday export -> private historical source date-set comparison

Scope date: 2026-10-14 KST
Status: **IMPLEMENTED AND OFFLINE TESTED; PROTECTED ORIGINAL YEARLY INPUT NOT ACQUIRED, NOT RUN ON PRIVATE WORKER, NOT PIT ADMITTED**.

## Source route, rights and quality

- **Primary public lookup:** [KRX holiday schedule](https://open.krx.co.kr/contents/MKD/01/0110/01100305/MKD01100305.jsp). Select **KRX** rather than CME/EUREX, select the historical year, use the KRX site's query/download action. KRX describes the page's query and download controls. This page itself provides a route, **not** already acquired original source rows.
- **Market-specific rule:** [KRX KOSPI cash equity holiday regulation](https://global.krx.co.kr/contents/GLB/06/0602/0602010201/GLB0602010201T1.jsp). Holidays include national elections, May 1, last year-end session and exchange-designated closures. Derivatives, KOSDAQ-only, overnight and simulated-market calendars are not substitutes.
- **Important 2026 exceptions:** a KRX May 20 notice [reported by NewsPim](https://www.newspim.com/news/view/20260520000433) says June 3 and July 17 were market-wide closures. The secondary XKRX package omitted these two in a previous *count-only* comparison; no direct original KRX source receipt/date-set match for them has occurred.
- The website may provide spreadsheets through a dynamic, stateful server route. The historical record's original downloaded document, metadata, applicable market, licence and display/version date must be recorded. **Do not invent an undocumented HTTP endpoint, reuse stale session tokens/OTP, or broaden the already approved six-GET OpenAPI authorization.** Human-exported input must be licensed and kept within the designated private data store.

## Code shipped on independent GitHub audit branch

- [Source-byte/market/year preflight](../../research_v1_krx_official_calendar_input_preflight.py): checks local original export SHA-256, KOSPI cash-equities market claim, source page identity, weekday/date/year shape, duplicates and valid UTC download record. **It cannot independently read Excel table cells or prove that an operator normalized the original source correctly**; human or separate independent verification of actual rows is still required.
- [Year-specific private runner](../../research_v1_krx_private_calendar_year_runner.py): requires dedicated `indexalert-krx-historical-worker`, existing private `/data` volume, original source file and normalized sidecar, independent expected original-document SHA, existing per-year source receipt SHA from frozen [sanitized manifest](./2026-10-13-krx-market-source-pit-boundaries.json). By default it is DRY-RUN and reads no provider data; with `--audit` it calls the existing SHA-backed private `_check_one` via [date-set comparator](../../research_v1_krx_private_date_set_comparator.py).
- [CI denial/integration tests](../../test_indexalert_krx_private_calendar_year_runner.py), [CSV row parser](../../research_v1_krx_calendar_csv_source_validator.py), [XLSX row parser](../../research_v1_krx_calendar_xlsx_source_validator.py), [source preflight tests](../../test_indexalert_krx_official_calendar_input_preflight.py). No brokerage/key/network access.

Sample *documentation only*, NOT executed:

```bash
python -B research_v1_krx_private_calendar_year_runner.py \
  --year 2025 \
  --document /data/krx-calendar/2025-original-export.xlsx \
  --claim /data/krx-calendar/2025-normalized-claim.json \
  --expected-document-sha256 <SHA256_FROM_INDEPENDENTLY_VERIFIED_ORIGINAL_DOWNLOAD> \
  --audit
```

**Important file-format constraint:** this CLI accepts narrowly validated original CSV (`일자,요일,비고`) or XLSX with visible sheet/row/relationship and actual date-value verification. Legacy binary `.xls`, HTML, unsupported worksheet schema, or manually converted CSV passed off as an original download are **rejected**. The actual downloaded KRX file is **not** available for format inspection in this session. Do not run the above example using a fabricated extension; an actual supported licensed original and independently pinned SHA are prerequisites.

**CLI exit codes:** Without `--audit` this is read-free dry run. With `--audit`, only `EXACT_DATE_SET_AGREES_REFERENCE_ONLY_NOT_PIT` returns exit 0; a genuine date-set mismatch, snapshot drift, malformed record or absent original is **exit 1** (never silently counted as a validated calendar). Even an exit 0 proves **only** exact source/reference set consistency and cannot override PIT/safety gates. The runner also checks the original worker's per-year weekday count, original SHA snapshot, calendar overlap arithmetic and explicit non-admission flags. The default trusted base is `KRX_PRIVATE_RAW_DIR` or `/data`, consistent with the original live worker. Relative, off-volume, symlink and `/data/../` traversals are refused.

The input sidecar needs source kind `KRX_HUMAN_EXPORTED_HOLIDAY_SCHEDULE`, `market=KOSPI_CASH_EQUITIES`, exact official lookup URL, year, original-document SHA, actual UTC download time, and **exact source-derived closed weekdays**. Keep year/source files **private**, outside GitHub and public logs.

2026 source comparison is intentionally limited to the original observed weekday snapshot through **2026-10-08**; 2015–2025 are full years. Years are checked against already pinned original SHA receipts. An independently validated source/normalization attestation is still mandatory before any genuine holiday reclassification. A matching date set is evidence only of private source/reference consistency, not historical per-security tradability or PIT original availability.

## Current operational access limitation

The connected Railway tooling exposes service/deployment descriptions and logs but does not provide an interactive shell for files on the mounted KRX private volume. The audit branch code **is not deployed to the worker**; the worker still points to development commit `1e6367d2863a86c3470da13d81a955d277eba485`, currently successful, with no new post-2026-10-12 logs. We therefore **cannot assert an actual year comparison** was executed in the worker. Running this later requires an explicitly permissioned private export and a controlled read-only runner execution with the original SHA and local files; changes to the live worker are not silently authorized by this handoff.

Current source summary: 3,071 SHA-backed original weekday checkpoint pairs, 184 ambiguous days, 27 quarantined securities, source gates C/D **BLOCKED**. No newly PIT-admitted KRX data, profitability run or real order. Frozen/H5, Champion, Holdout and `ORDERING=false` unchanged.

## CI evidence (2026-10-14 KST)

[GitHub Actions run 38466345880](https://github.com/kims34/openpilot-opkr/actions/runs/38466345880), built from commit `000841000bded74c46a64be5d23da7552efebe49`, completed SUCCESS: **71 of 71 offline tests passed**, covering historical-status temporal guard, year-level counts, SHA-pinned source inputs, exact private date-set comparator, private-volume denial and frozen safety flags. This proves code behavior on synthetic/manifest evidence only; **no official original holiday XLS or private Railway day-set comparison was executed in the test runner**.

## Hardened runner update and real deployment boundary (2026-10-15 KST)

Audit-only branch code now shares the private root resolver between the yearly command and the private date-set comparator. The original live integrity auditor uses `Path(os.getenv("KRX_PRIVATE_RAW_DIR") or "/data") / "openapi_kospi_history_v1"`. Previously the audit-only runner rejected absent `KRX_PRIVATE_RAW_DIR` even if the worker's trusted `/data` mount existed. The resolver now matches the deployed auditor's fallback, rejecting off-volume, relative, symlink and dot-dot traversal paths.

The yearly runner now fails closed if any annual source manifest count or SHA-256 pin is invalid; if source-reconciliation outputs are inconsistent with the expected weekday scope, original empty count, closure count or exact original source snapshot; or if the claimed exact match has any missed original-empty/reference-open days. For a mismatch, CLI exits with nonzero status instead of reporting successful verification. **This does not validate that the human-supplied calendar source is genuinely issued by KRX or available as of a historical trading decision.**

[GitHub Actions run 38598147207](https://github.com/kims34/openpilot-opkr/actions/runs/38598147207): **140/140 offline tests passed**, based on commit `5e4fbd6c3f9a9a420a5fda999cd6a8d0faf52589`. Tests use synthetic CSV/XLSX bytes and mocked private receipt metadata; they do NOT access Railway's mounted raw records or permit performance/holdout/orders. The live worker branch, deployment command, and source data remain unchanged. All 184 ambiguous provider-empty days and 27 quarantined securities remain unresolved.
