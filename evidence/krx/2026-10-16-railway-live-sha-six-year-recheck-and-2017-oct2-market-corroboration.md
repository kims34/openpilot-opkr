# KRX PIT original storage live recheck and 2017-10-02 independent calendar corroboration

Reviewed **2026-10-16 KST**. Isolated evidence branch `indexalert-krx-pit-source-audit-20261013`. This is a read-only inspection of existing Railway deploy logs and public contemporaneous materials. **No Railway private volume shell, new authenticated KRX OpenAPI call or actual protected source-date row access.**

## Live worker historical SHA metadata versus pinned GitHub receipts

Read the latest available deploy log events for protected service `003812ee-102b-42b6-bda4-36925885b428` (deployment `16c93d7c-7cd0-4d84-a327-298d2805376c`, successful). Compared the actual `INDEXALERT_MISSING_2017_2022_INTEGRITY_YEAR=` log event's `verified_weekday_pairs`, `unknown_calendar_or_source_gap_days` and `metadata_snapshot_sha256` **exactly** against each 2017–2022 year's `verified_weekday_pairs`, `unverified_exchange_calendar_or_source_gap_days` and `reported_metadata_snapshot_sha256` in [the frozen provenance boundary manifest](./2026-10-13-krx-market-source-pit-boundaries.json).

| Year | Original SHA-backed weekday pairs | Ambiguous source-empty weekdays | Count, empty and original snapshot SHA all match LIVE log? | Original PIT source admission |
| --- | ---: | ---: | --- | --- |
| 2017 | 260 | 17 | Yes | No |
| 2018 | 261 | 17 | Yes | No |
| 2019 | 261 | 15 | Yes | No |
| 2020 | 262 | 14 | Yes | No |
| 2021 | 261 | 13 | Yes | No |
| 2022 | 260 | 14 | Yes | No |
| **Six-year total** | **1,565** | **90** | **6/6 years** | **Blocked** |

All six original deployed reports carry `historical_pit_source_admitted=false`, and the final persisted integrity report says `invalid_pair_count=0`, `missing_weekday_pairs=0`, `full_universe_source_admitted=false`, `ordering=DISABLED`. These logs were originally generated Oct12; this turn **re-queried the logs** and re-computed equality, not a new data collection or 2026-Oct16 run of the private integrity auditor.

## 2017 October extraordinary closure: dated original-market attribution and one issuer corroboration

1. [Yonhap 2017-09-17 08:01 original contemporaneous article](https://www.yna.co.kr/view/AKR20170915179300008), quoting data credited to **Korea Exchange**: 2017-09-30 through 2017-10-09 was a ten-consecutive-day period without stock market trading, explicitly attributed to the separately designated **2017-10-02** temporary public holiday. This is evidence of what contemporaneous *public news* reported **before** the closure. It is **not** an independently SHA-verified KRX original holiday schedule or authenticated original exchange press notice publication instant.
2. [KRX KIND hosted 2017-10-31 issuer-authored offering document — Jooyon Tech](https://kind.krx.co.kr/external/2017/10/31/000512/20171031001090/10601.htm), original HTML content visibly reviewed in the public text source. Its daily issuer price/volume/consideration table displays `2017-10-02(월)` as dash/no values across fields, with 2017-09-29 and 2017-10-10 carrying actual trading amounts. This **retrospective, per-security** row independently corroborates the trading interruption pattern. It is **NOT an exchange-market original daily calendar**, cannot rule out an issuer-specific halt as a general inference, and was published after the Oct2 event, so it **MUST NOT** be treated as a source available at an earlier investment decision.
3. [2017 July third-party mirror of KRX holiday export](./2026-10-14-krx-2017-holiday-temporal-source-reconciliation.json) listed 16 weekday closures and excluded Oct2; Sept exchange-attributed news permits a **17-date source-candidate** only after original public secondary publication. This candidate count equals the live worker's **17 ambiguous empty days**, but exact source-empty original dates **were not retrieved**; count equality cannot prove exact date-set agreement.

The 2017 private original `metadata_snapshot_sha256` was independently compared against the previously pinned original evidence, **but we did not inspect the actual private October 2 receipt**. Do not remove October 2 from the 17 unknown-day set by inference. An authoritative KOSPI cash-market original archived calendar and its version/publication lineage are still needed, along with a protected read-only per-day comparison.

## Unchanged safety boundaries

Across 2015–2026 the historical manifest still records **3,071** SHA-backed weekday receipt pairs and **184** unverified source-empty date pairs. All **27** problematic historical securities remain quarantined. Frozen H5/Champion, PIT and historical halt/delist/corporate-action provenance, M20 Net EV, independent holdout, costs/true fills and Tiny Live remain blocked pending their separate original evidence gates. No source contract C/D admission, no orders, no account or permission changes, no funds movement. The original worker deployment/branch/start command and restricted `/data` volume remain unchanged. `ORDERING=false`.

**Next dependency:** original year/date-complete KRX cash market holiday/session history with publication/version/source SHA, followed by read-only snapshot-pinned per-day crosscheck on the already protected worker. The repository's 152/152 [offline CI suite](https://github.com/kims34/openpilot-opkr/actions/runs/38821504163) is still the latest tested code baseline; this evidence-only addition does not introduce executable code or claim a new CI suite.
