# M20 2022 Q3 source-readiness audit: four pinned official artifacts reconciled

**2026-10-17 KST. Verdict: OFFICIAL EVIDENCE CONSISTENT; ORIGINAL FINANCIAL PIT / M20 PERFORMANCE NO-GO.**

## Actual independently checked official workflow evidence

This research branch now pins exactly four *completed, successful*, historical first-receipt DART viewer source-only workflows. It neither refetched OpenDART/DART nor accessed market/broker/holdout data for this source-consistency gate.

| Source stage | Verified GitHub Actions run | Artifact ID | Source-only finding |
| --- | --- | --- | --- |
| First-receipt viewer financial subsections | [#38706084440](https://github.com/kims34/openpilot-opkr/actions/runs/38706084440) | `11958577751` | 4 financial subsections, 329 tables, 2 earnings row candidates |
| Same subsection text hints | [#38708786002](https://github.com/kims34/openpilot-opkr/actions/runs/38708786002) | `11958909398` | One subsection earnings+CFS wording, one earnings+3-month wording; no full July–September 2022 or 2021 window |
| Same parsed table structure | [#38731230183](https://github.com/kims34/openpilot-opkr/actions/runs/38731230183) | `11971011193` | Two earnings candidate tables with four numeric peers; one table has `당분기` and `전분기` text; zero exact quarterly date spans |
| Preceding TH/TD header rows | [#38822004271](https://github.com/kims34/openpilot-opkr/actions/runs/38822004271) | `12013358036` | Two preceding TH header contexts; zero earnings rows preceded by **both** quarter terms, zero preceding literal 3-month label |

**New audit workflow [#39001867286](https://github.com/kims34/openpilot-opkr/actions/runs/39001867286) PASSED BOTH JOBS.** Offline unit/security tests passed and the runner re-downloaded the four *same immutable status-only JSON evidence artifacts*, verified each original GitHub run's ID, head commit SHA and successful conclusion plus artifact ID/name/sha256 digest and unexpired status, and reconciled mandatory source-status/count/PIT/trading checks. The new audit made **no additional official OpenDART/DART source requests**.

Current exact M20 first-original source gate:
- `source_status=FOUR_OFFICIAL_SOURCE_DIAGNOSTICS_AGREE_NO_PIT`
- `verified_pinned_source_artifact_count=4`
- `first_original_financial_viewer_subdocuments=4`, `financial_viewer_table_tags=329`, `first_original_operating_label_table_candidates=2`
- `candidates_with_both_quarter_words_in_preceding_header_rows=0`
- `candidates_with_full_2022_q3_window_in_same_table=0`
- `candidates_with_full_2021_q3_window_in_same_table=0`
- `actual_original_cfs_operating_profit_cell_period_lineage_verified=false`
- All feature, backtest/performance, independent Holdout, Champion, real order, funds and permissions admission false, `ORDERING=DISABLED`.

New gate code:
- `INDEXALERT_M20_2022_Q3_VERIFIED_SOURCE_ARTIFACT_MANIFEST.json` — exact four immutable source run HEADs, artifact IDs/names and SHA-256 digests
- `research_v1_m20_original_source_evidence_gate.py` — deny missing/mixed or newly promoted source reports; permit no raw account values, receipts or financial cells
- `test_research_v1_m20_original_source_evidence_gate.py` — forging run SHA, artifact digest, evidence/status or PIT flags fails closed
- `.github/workflows/indexalert-m20-original-source-evidence-gate.yml` — read-only GitHub artifact metadata download and official evidence consistency check
- New immutable seven-day **counts-only audit artifact** `12088933161`, `sha256:0c6e175b48473b9e8067b9e88691b49c6bc1a577dfcf3228a296b7b07aab065e`. This artifact's expiry is **2026-10-24**. The four upstream source artifacts expire on their original retention schedules; future re-download failures must remain fail-closed, not be interpreted as source records newly missing.

The first workflow attempt [#39001839731](https://github.com/kims34/openpilot-opkr/actions/runs/39001839731) passed offline tests but failed on its metadata shell loop syntax; commit `1dbe692f0e3b38f42d4a5f5d64e7cbc363fce6ae` fixed that runner-only error and full official GitHub source-artifact evidence verification then succeeded. Do not mislabel this runner error as a DART accounting failure.

## What is NOT proven / approval gate

Four consistent source-shape probes do **not** establish the *actual first-edition standalone three-month consolidated operating-income numeric column* for Q3 2022 and comparative Q3 2021, the corresponding original financial unit, independently versioned company statement, exact first publication instant or historical issuer-to-security PIT. Source text cooccurrence and DART viewer rendering cannot substitute for original first-edition structured XBRL/independent archived material. The earlier original 2022 XBRL endpoint returned `014`, and the current normalized 2022 CFS API was unavailable (`013/014`); repeating weaker source word-count scans is not the next missing proof.

Do not use this counts-only audit as a profitability dataset; no returns, costs, taxes or market economics were computed and it contains no original earnings values. Frozen H5/M20, pre-registered source universe, CPCV/Walk-Forward, independent Holdout, all Champion criteria and real broker account settings stay unchanged. **Keep Draft PR #412 unmerged.** `ORDERING=DISABLED`.
