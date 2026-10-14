# KRX 2017 market holiday announcement: earlier public availability, six-year live source fingerprint recheck

Date: 2026-10-14 KST. Independent branch: `indexalert-krx-pit-source-audit-20261013`.
**No original KRX holiday export bytes, raw private price data, execution/trading authorization, or source PIT admission.**

## Evidence-based corrected *secondary news* as-of

The prior isolated 2017 calendar candidate implementation withheld the 2017-10-02 exchange closure until the day after a quoted 2017-09-18 exchange announcement. That is conservative but **not the earliest identified public report**.

- [FinanceData article dated **2017-07-16 15:45 KST**](https://financedata.github.io/posts/pandas-market-days-krx.html) describes then-current KRX holiday spreadsheet data and visibly lists **16 weekday closures** for 2017; its historical table does **not** include 2017-10-02. Its displayed old table uses `일자 및 요일` and `요일구분` columns, **different from today's `일자 / 요일 / 비고` holiday grid**. The linked archive of `hdays-2017-KRX.xls` was inaccessible in this review. A public blog table is not the original KRX source XLS nor independent proof of the XLS's upload/publication time.
- The September 5 government holiday decision preceded the KRX-attributed news.
- [Yonhap article **2017-09-17 08:01 KST**](https://www.yna.co.kr/view/AKR20170915179300008) expressly reports that KRX says the cash stock market is closed September 30–October 9 and identifies the October 2 extraordinary government holiday. Its article timestamp is an as-of bound for the **publicly published secondary report**, **not the exchange's original notice**.
- [Electronic Times article **2017-09-18 13:21 KST**](https://www.etnews.com/20170918000164) separately attributes the closure to KRX. This is a later corroboration and cannot invalidate the earlier public 9/17 report. The previously quoted 9/18 KRX notice listing date likewise does not authenticate a first-published-at instant.
- The [2017 source-evolution manifest](./2026-10-14-krx-2017-holiday-temporal-source-reconciliation.json) now distinguishes both articles and leaves `original_KRX_notice_bytes_or_first_publication_instant_authenticated=false`.
- The [2017 as-of validator](../../research_v1_krx_2017_temporal_calendar_reconciliation.py) makes its 17-day **secondary candidate** date set available at/after the **Yonhap 2017-09-17 08:01 KST article timestamp** only; immediately before that minute, the candidate remains the 16-day July third-party snapshot. No KRX-original-PIT claim was added.

## Practical impact on potential 2017 backtests

The existing 2017 private source manifest counts **260 weekdays**. Simple calendar arithmetic, **not an original exchange session proof**:

| Snapshot candidate | Excluded weekdays | Computed open weekday candidates |
| --- | ---: | ---: |
| July 16 public archived holiday table | 16 | 244 |
| At/after September 17 public KRX-attributed 10/02 news | 17 | 243 |

The difference is one **potential false trading session** (Oct 2) if a future October or full-year backtest reused the stale July calendar without an as-of update. Do not add the October update retroactively to decision times before it became publicly known.

## Direct live Railway log vs sanitized repo source fingerprint check

Read-only original worker deployment `16c93d7c-7cd0-4d84-a327-298d2805376c` (SUCCESS, started 2026-10-12) exposes six existing `INDEXALERT_MISSING_2017_2022_INTEGRITY_YEAR` receipt records and a final non-PIT summary. Recompared each of the **2017, 2018, 2019, 2020, 2021, 2022** records against the frozen [sanitized year manifest](./2026-10-13-krx-market-source-pit-boundaries.json):

- **6/6 checkpoint counts matched**.
- **6/6 uncertain-empty-day counts matched**.
- **6/6 `metadata_snapshot_sha256` vs `reported_metadata_snapshot_sha256` matched**.
- Every year remained `historical_pit_source_admitted=false`, `real_orders_authorized=false`.
- Final Railway receipt explicitly: `network_request_attempted=false`, `ordering=DISABLED`, `live_orders_authorized=false`, `m20_performance_testing_authorized=false`, `raw_security_rows_emitted=false`.
- This was comparison of previously logged SHA receipts and sanitized aggregate manifest; **no private per-day original data bytes or 2017's 17 actual source-empty date identities were available or compared**.

## CI and unfinished blockers

[GitHub Actions run **38508162819**](https://github.com/kims34/openpilot-opkr/actions/runs/38508162819) completed **SUCCESS, 126/126 offline tests**, commit `29e9187ac2a5796f6bf41170df0f802638f72e66`. Tests cover time-bound as-of guard, differing year-level candidate session counts, pinned receipt metadata and unchanged admission flags.

**Critical source-format blocker:** the archived 2017 KRX export is linked as legacy `.xls` and the published table uses an older **two-column** schema; current [safe private source reader](../../research_v1_krx_private_calendar_year_runner.py) supports narrow CSV or strict XLSX `일자,요일,비고` formats and refuses opaque legacy XLS. It would **correctly fail closed** even if the 2017 archive bytes were now provided. Do **not** re-label/conflate the third-party tabulation with the KRX original file or silently convert legacy XLS to a different format and claim original provenance. The historical original must first be fetched under permitted rights, recorded with SHA/version, and then an independently tested read-only legacy parsing adapter developed for its exact actual format.

**Protected work blocked:** all **184** unresolved KRX original weekday source gaps still require date-level original/reference comparison; **27** historical securities remain quarantined. Source contracts C/D, original available-at PIT, M20 profitability run and sealed holdout are **NOT authorized**. Frozen H5/Champion unchanged, `ORDERING=false`, no live orders, no fund movement, no new KRX authenticated source requests, no Railway deployment/restart.
