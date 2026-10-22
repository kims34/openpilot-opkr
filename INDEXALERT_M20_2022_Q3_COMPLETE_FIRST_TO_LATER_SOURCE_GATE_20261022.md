# IndexAlert M20 — 2022 Q3 first-to-correction contiguous official index proof

**Created October 22, 2026 KST. First-edition CFS financial PIT: NO-GO; no performance/holdout/trading permissions.**

## What was established before this task

- Original 2022 Q3 first-submitted OpenDART indexed receipt had independently been resolved for frozen issuer slot **5**. Original-to-amended SGML archives were separately obtained; original source archive was SHA-pinned. Exact candidate rows did not constitute verified 2022 or 2021 standalone July–September CFS operating-profit cells. Original 2022 standardized XBRL returned `014`, and current normalized 2022 CFS source did not supply an acceptable first-vintage quarter.
- An earlier issuer periodic-report index covering **2023-03-01 to 2026-10-13** found **31** periodic rows, exactly **one** corrected 2022 Q3 report and **zero** matching attachment additions.
- [Separate official incremental window #39715224915](https://github.com/kims34/openpilot-opkr/actions/runs/39715224915) covered **2026-10-14 to 2026-10-21**; OpenDART reported status **`013` (no queried periodic records)** with the result accepted only for the exact read-only issuer/time scope, not as an all-time archive or original CFS financial fact.

## New single-run continuity proof to eliminate cross-run gaps

Created three files on isolated unmerged research branch `indexalert-m20-opendart-original-proof-20261013`:

- `research_v1_m20_2022_q3_full_edition_index_20261021.py`
- `test_research_v1_m20_2022_q3_full_edition_index_20261021.py`
- `.github/workflows/indexalert-m20-full-contiguous-2022-index.yml`

One read-only workflow checks **the earliest-original report index `2022-10-01..2023-02-28` and entire later index `2023-03-01..2026-10-21`** for the *same* current registry issuer in one execution, using at most **three authenticated official OpenDART calls** (`corpCode.xml`, first-window `list.json`, later-window `list.json`).

The gate requires complete **one-page** response pagination (max 100), exact issuer for every row, bounded receipt/day identity, unique earliest first-edition report, no withdrawal, source `rm=정` correction hint, no initial-window correction, exactly **31** later periodic rows (previously pinned count), exactly **one** same-period correction confined to the previously proven pre-October 14 window, **zero** attachment additions, no new 2022 Q3 editions after October 13, and no receipts duplicated across windows. Any official status `013` for the longer expected populated index, unknown report variant, unverified provider outcome, drift or paging ambiguity fails closed.

**[GitHub Actions #39721626218](https://github.com/kims34/openpilot-opkr/actions/runs/39721626218)**:
- The **offline synthetic fail-closed/unit/security job succeeded (16 tests)**.
- The **actual three-call official source validation was still running at the last verified observation**. Do not claim single-run original-to-2026-10-21 continuity or an official artifact until the source job has finished and logs have been checked.

Source commits: `187cb42968fd982edacfa0fffc7e36ac98f0af76` (source), `735c2fbe1a8d8e76eddead0fccfab174a5ad00fa` (offline tests), `511acdb76809b8a2173a637effb04dc5fb621df1` (workflow).

## Hard provenance boundary

A completed official index chronology, if achieved, establishes only that the **query returned a bounded as-of sequence of filing identifiers/metadata** for the fixed current issuer. It does not authenticate 2022 originally public financial CFS accounting cells, monetary scale, the first-disclosure clock, future/earlier amendments outside scope, historical issuer/security PIT or whether current DART rendering reflects historical data. The date-only edition candidate gate still needs separately verified historical KRX sessions and original-vintage release timing. The query does not access trading endpoints, KRX, Railway, broker tokens or account funds. Original four-document source-count capsule ID `12138239045` remains unchanged and is not a signed original financial snapshot.

**All hard stops remain:** `m20_feature_pit_admitted=false`, `m20_performance_run_authorized=false`, `independent_holdout_authorized=false`, `champion_change_authorized=false`, `real_orders_authorized=false`, no funds/permissions; `ORDERING=DISABLED`. Frozen H5 and M20, preregistered cohort, taxes/costs, Walk-Forward and separate holdout unchanged. [Draft PR #412](https://github.com/kims34/openpilot-opkr/pull/412) **unmerged**. No extra hourly automation created.


## Final independently verified source — completed official GitHub Actions

[Actions #39721626218](https://github.com/kims34/openpilot-opkr/actions/runs/39721626218) **COMPLETED SUCCESS** after the provisional entry above. Both `offline-complete-edition-chain-security` and `official-complete-edition-chronology` succeeded. The offline job ran **16** complete-input, tamper, identity, chronology and no-network/no-order synthetic tests. The official job used the three-call limit and emitted:

- `source_status=FULL_CONTIGUOUS_OFFICIAL_INDEX_RANGE_VERIFIED_SOURCE_ONLY`, fixed cohort slot 5, observed index end **2026-10-21**.
- Original 2022-Q3 first-submitted receipt unique; original listing page completely checked, corresponding correction hint present, and no original-window corrected rows.
- Later 2023-03-01..2026-10-21 index one-page metadata and every row checked; **31** periodic records for the same currently registered issuer, **one** correction of the 2022 Q3 report and **zero** attachment additions.
- The one correction remains inside the previously pinned prior window ending Oct13; **zero** new 2022 Q3 correction/attachment editions for Oct14..21; contiguous initial/later windows verified for this **queried and returned official index**.
- `current_day_20261022_index_complete=false`, `all_time_revision_history_verified=false`, `index_is_historically_immutable_archive_verified=false`. A current registry identity is **not** independently historically PIT validated.

**Official safe source-count artifact:** ID `12401173549`, sha256 `8deb40bd1fa9714277346d052f346dd570894bc5a356d63fcdd5580ef4d8b4d2`, expires `2026-10-29T04:22:35Z`. This archive holds **counts and authorization flags only**. It is not a source document or extracted monetary data and does not replace the separate 30-day first-viewer count capsule.

### Interpretation

For the fixed issuer, the *official indexed periodic-filing inventory* observed in this precise three-call run is now internally consistent across the **original-window, subsequent-window and previously observed Oct14–21 extension**. This is a stronger bounded-index source-provenance result than simply combining two earlier independent runs. It neither proves source immortality or a historical time-of-day publication clock, nor binds a single original CFS 2022/2021 standalone Q3 profit number to the first edition. As-of availability, full historical issuer/security PIT, financial amount/period/unit semantics, actual correction-to-financial-cell linkage and OpenDART XBRL 014 gap remain **NO-GO**.

**Safety verified:** `m20_feature_pit_admitted=false`, `m20_performance_run_authorized=false`, `independent_holdout_authorized=false`, `champion_change_authorized=false`, `real_orders_authorized=false`, `ORDERING=DISABLED`. No broker, Railway, trading rights or funds changed. Draft PR #412 unmerged.
