# IndexAlert M20 2022 Q3 — verified source-only replay capsule

**Date:** 2026-10-18. **Verdict:** Four read-only original-viewer diagnostic artifacts still agree, but original 2022/2021 Q3 CFS profit accounting/PIT remains **NO-GO**.

## Why this task was needed

The four independently successful original-DART viewer source diagnostics for fixed cohort slot 5 (2022 Q3) were retained as individual GitHub Actions artifacts for seven days. Their expiration must not silently erase source proof, trigger repeated live provider requests, or turn a missing downloadable artifact into a newly verified financial fact. The source-only diagnostic reconciler previously established four stable aggregate outputs. This additional step preserves **only the already validated source-count JSONs**, their exact pinned provenance manifest, a NO-PIT verdict and file checksums.

## Verified run and artifact

- Code change: commit `faa68ad257fff1eff697e78653e1e369db3453f3`, workflow `.github/workflows/indexalert-m20-original-source-evidence-gate.yml`. No change to M20/H5 Frozen code, pre-registered experiment, historical source data, broker accounts or authorization.
- [GitHub Actions #39132675511](https://github.com/kims34/openpilot-opkr/actions/runs/39132675511): **offline manifest-security SUCCESS** and **pinned-source historical evidence reconciliation SUCCESS**, with no new OpenDART, DART viewer, KRX or broker requests.
- **New source-count replay capsule**: artifact ID `12138239045`, exact name `m20-first-original-four-pinned-counts-replay-capsule-no-pit`, archive digest `sha256:c9465d204b6a5c0b109807b06c352e46e12a50d8d717e953bd06ab3e9176036b`; created `2026-10-18T13:42:08Z`; provider-reported expiry **`2026-11-17T13:42:08Z`** (30-day retention).
- Independently retained normal **NO-PIT verdict**: artifact ID `12138398409`, digest `sha256:040d84d82dd83a4eef1194463766774131c4ea7891f6e5223f9a48c79b547f3a`; expires `2026-10-25T13:42:09Z` (seven days).

The replay capsule contains:
1. The four **previously validated** count/status-only `counts.json` files in their separate diagnostic namespaces.
2. Exact `INDEXALERT_M20_2022_Q3_VERIFIED_SOURCE_ARTIFACT_MANIFEST.json`, retaining original run/head SHA/artifact SHA pins.
3. The independently cross-reconciled `verdict.json` from `research_v1_m20_original_source_evidence_gate.py`.
4. A `checksums.json` file holding SHA256 fingerprints of the manifest, four raw input count JSONs and the gate verdict, with explicit negative financial/PIT/trading bits.

The runner permitted creation **only after** successful original artifact metadata verification, four report schema/identity/source-count consistency checks, and strict denial of any unsafe financial/PIT/holdout/Champion/order flags. The capsule is **not** an original financial statement or audit substitute. Once original seven-day source artifacts expire, replay is merely a verification of *this sealed historical snapshot*; the previous GitHub run IDs, commit pins, artifact digests, and original archive digest remain the upstream provenance, and no new official source success is implied.

## Exact evidence outcome (unchanged)

- Original first-receipt 2022 Q3 viewer finance sections: **four**, containing **329** table tags and **two** exact-label operating-income candidate tables.
- Of these two candidates, **zero** were bound to both quarter terms in *preceding explicit header rows*, **zero** had complete 2022 July–September Q3 period text in the same table, and **zero** complete 2021 comparative Q3 period text in the same table.
- No first-submitted authoritative **CFS statement → operating-income accounting line → three-month numeric column → monetary unit → 2022/2021 original-edition values → historical publication instant** chain was proved. Earlier first-edition standardized XBRL `014`, historical issuer/traded-security PIT and original-versus-amended financial-cell lineage remain separate blockers.

**Decision:** keep `m20_feature_pit_admitted=false`, `m20_performance_run_authorized=false`, `independent_holdout_authorized=false`, `champion_change_authorized=false`, `real_orders_authorized=false`, `funds_movement_authorized=false`, `permissions_change_authorized=false`, **`ORDERING=DISABLED`**. Frozen H5/M20 rules and Holdout unchanged. Research PR #412 must remain Draft/unmerged. No scheduled task was added; avoid repeated unsuccessful old API calls simply to refresh a retention timer.

Next genuinely independent data acquisition requires a validated archived first-vintage CFS statement/period original or authoritative first-edition structured XBRL; broad DART viewer source-text matching cannot resolve this accounting/PIT issue.


## Independent 30-day capsule offline replay — 2026-10-18 actual SUCCESS

- Added `research_v1_m20_source_capsule_replay.py`, `test_research_v1_m20_source_capsule_replay.py` and `.github/workflows/indexalert-m20-original-source-capsule-replay.yml` at commit `69e417f3f75bcf4880ee23d6ecb153973e69dd75`. Replay downloads **only** the previously sealed 30-day capsule from GitHub Actions #39132675511; first verifies that runner's exact completed/successful commit, sealed artifact ID, digest and unexpired state. It then checks the capsule's *four individual JSON byte hashes*, pinned manifest identity, sealed verdict hash and exact original source-shape consistency. No original seven-day artifacts, OpenDART/DART source, KRX, market, Holdout or broker data are requested.
- **[Actions #39133051052](https://github.com/kims34/openpilot-opkr/actions/runs/39133051052) completed SUCCESS in both offline tamper/PIT-security job and actual isolated capsule replay job**. Official GitHub-proven prior source snapshot remains four reports / 329 table tags / two earning-row text candidates. Replay output intentionally has `source_replay_is_new_official_dart_result=false`, `original_2022_q3_cfs_fact_verified=false`, `original_2021_q3_cfs_fact_verified=false`, and *all* feature/performance/Holdout/Champion/order/funds/permissions bits false; `ORDERING=DISABLED`.
- Seven-day replay-verdict artifact ID `12138334301`, digest `sha256:4aad6c9bc6ab9a7e232ffcadb13f8503cd1e7a931ebdadf143b7462fc2a46b47`, expiry `2026-10-25T13:47:14Z`. The **sealed source-count archive itself** remains artifact ID `12138239045`, digest `sha256:c9465d204b6a5c0b109807b06c352e46e12a50d8d717e953bd06ab3e9176036b`, expiry `2026-11-17T13:42:08Z`. The previous original run/artifact hashes are retained in the manifest, **but archived replay is not a fresh independently signed original DART financial statement**.
- Historical original standalone Q3 CFS profit values, monetary units, first-publication timestamp, full corrected financial-cell vintage and historical issuer/security PIT remain missing. Do not start profit tests or live trading from this archival work. Retain Draft PR #412 unmerged.
