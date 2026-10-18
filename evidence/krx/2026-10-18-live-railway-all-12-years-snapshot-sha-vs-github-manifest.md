# KRX 2015–2026 complete pinned-year SHA consistency recheck

**Observed:** 2026-10-18 KST. **Branch:** `indexalert-krx-pit-source-audit-20261013`. Original private Railway worker has **not been rerun**: this is an independently recalculated comparison of existing October 12 live deploy log entries against frozen GitHub metadata.

## Scope and method

Using the connected Railway read-only **deploy log stream** for service `003812ee-102b-42b6-bda4-36925885b428` (latest successful deployment `16c93d7c-7cd0-4d84-a327-298d2805376c`), parsed three families of log entries:
- **2015–2016:** `INDEXALERT_PRIVATE_KRX_OPENAPI_INTEGRITY=` (`verified_date_pairs`, `empty_daily_unverified_calendar_or_source_gap_days`, `snapshot_fingerprint_sha256`).
- **2017–2022:** `INDEXALERT_MISSING_2017_2022_INTEGRITY_YEAR=` (`verified_weekday_pairs`, `unknown_calendar_or_source_gap_days`, `metadata_snapshot_sha256`).
- **2023–2026:** `INDEXALERT_RECENT_INTEGRITY_YEAR=` (same fields as 2017–2022).

For every year, compared the logged exact SHA digest and both integer counts to `offline_verification.per_year` in the pinned [source/PIT boundary manifest](./2026-10-13-krx-market-source-pit-boundaries.json). **All 12 / 12 exact three-field comparisons passed**; every logged year carries `source_admitted=false` or `historical_pit_source_admitted=false`. No original daily rows or pair IDs were exported. Original 2026 scope ends **2026-10-08**, not 2026-12-31. These logs originated 2026-10-12; no new market-data download or SHA hashing occurred in this work.

| Year | Matched original weekday source pairs | Ambiguous source-empty weekday responses | SHA vs pinned manifest |
| --- | ---: | ---: | --- |
| 2015 | 261 | 13 | EXACT |
| 2016 | 261 | 15 | EXACT |
| 2017 | 260 | 17 | EXACT |
| 2018 | 261 | 17 | EXACT |
| 2019 | 261 | 15 | EXACT |
| 2020 | 262 | 14 | EXACT |
| 2021 | 261 | 13 | EXACT |
| 2022 | 260 | 14 | EXACT |
| 2023 | 260 | 15 | EXACT |
| 2024 | 262 | 18 | EXACT |
| 2025 | 261 | 19 | EXACT |
| 2026 (through Oct 8) | 201 | 14 | EXACT |
| **Total** | **3,071** | **184** | **12/12** |

## Original scanner and private comparator API compatibility

Inspected original `research_v1_krx_openapi_private_integrity_audit.py` in the audit GitHub branch: production `_check_one` revalidates source byte SHA, checkpoint identity, timestamp and source quality, and returns `day`, `pair_sha256`, `daily_rows`, `common_rows`, `source_day_class`. It computes `snapshot_fingerprint_sha256` over the serialized ascending-day list of `{day,pair_sha256}` using sorted JSON keys and compact separators, matching the intended digest construction in `research_v1_krx_private_date_set_comparator.py`. This is a **static code contract inspection only**; neither reader nor annual comparator was invoked against live volume `/data` in this review.

Current protected Railway service still tracks **development** branch `index-alert-position-regen-fix-v1` and only runs the existing integrity scanner. GitHub **research audit branch is not deployed**. The holiday annual source `CSV/XLSX`, sidecar date claim and source-document independent checksum have **not** been staged in that worker; therefore there is no actual private original-vs-official-day-set comparison to report.

## Strict conclusion

**Verified:** existing saved original source acquisition / SHA audit metadata agrees across all recorded years.

**Unverified and BLOCKED:** which of the 184 source-empty weekdays are authentic KOSPI holidays versus provider gaps; contemporaneous official *versioned* holiday source and first-published-at; original historical security halt/delist/corporate-action handling; **27 quarantined securities**; PIT gates C/D; independent sealed holdout; M20 Net EV and live ordering.

All Frozen H5/Champion policy, costs/true execution limits and `ORDERING=false` remain intact. **No production deployment, restart, private volume file read/write, extra protected KRX OpenAPI request, trading order, or financial operation occurred.**

Next true unblock: obtain independently authenticated, approved market-specific first-party **historical annual holiday date rows and amendments** with original raw SHA and source availability timestamp; stage them inside the authorized private worker; then perform strictly read-only exact date-set reconciliation after separate review. Passing an aggregate count, source SHA or offline unit test alone **does not** clear PIT.
