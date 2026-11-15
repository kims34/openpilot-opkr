# IndexAlert independent evidence audit — 2026-11-15 11:17 KST

Scope: read-only GitHub/Railway evidence; no official market replay, no M20 economics, no deployment, merge, order, promotion or credentials change. Parent isolated audit commit: `5cf59f3e200b77917173906f180dfc7493bd7780`.

## GitHub PR exact heads (direct connector read)
- #412 OpenDART: `bf3d9514a87c53b1775e22ec9ba7711f6cecc49f`; draft open.
- #413 offline optimization: `f003ef6247e16fcc71bd3b1b20cd4904c4d984c0`; draft open.
- #414 orchestration gate: `18c5418d9684d1717df58261ea27f28e514385b2`; draft open.
- #418 independent runner: `2f98401cc50a6c6a25808a98516efd5bf0c944ee`; draft open.
- #420 KRX uncertainty: `fab3cbbd63a951a4e081f9e7f08c1391ca308581`; draft open.
- #422 KRX 2021: `c14857620973531013799e44625d43080904fd5f`; draft open.
- #423 KRX 2022: `0e38004363cac9fc4475556b3a1c445de9af407f`; draft open.
- Research `index-alert-research-v1` and development `index-alert-position-regen-fix-v1`: branches exist; exact live HEAD not independently retrieved this run — NOT VERIFIED. Historical reported research `df474df...` and development `1e6367d...` are not promoted to current HEAD.
- Read PR #414 gate at its exact HEAD: source PIT and official trading eligibility remain blocked, H5 holdout spent, M20 unauthorized.

## GitHub Actions — latest direct job checks
- 38381997417: 6/6 success; 38382214223: 6/6 success.
- 38419111311: 6/6 success; 38419439742: 2/2 success (OpenDART offline/official-safe candidate only); 38419649711: 1/1 success (synthetic runner).
- 38486028854: 1/1 failure. Job 115599778959 actual log: `SourceDriftError: archived blob mismatch: research_v1_runtime_manifest.py expected=108f66714602a1bd3ae42c34dcca7c16e38f460b observed=e428789e2e97ca7be3a4482e0df23b483a1ad69d`; no regression artifact uploaded. FAIL; do not change pinned manifest to mask source drift.
- Historical 34-case SHA-256 `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34`: user-supplied prior evidence; not independently recalculated this run — NOT VERIFIED.
- Historical 2.9656s serial vs 2.6209s concurrent: regression-only 1.1315x, not total CI or official backtest acceleration.

## Railway production read-only (2026-11-15)
Project `d1c1a050-b7d6-41ce-b300-13c20f82a20a`; environment `83d5840b-270e-4d3f-a941-a37fd4a55ff7`.
- PIT rebuild deployment `8b354fc1-cfb2-4ef0-863e-67f7f5dda2b5` SUCCESS, replicas 1/1.
- KRX worker `16c93d7c-7cd0-4d84-a327-298d2805376c` SUCCESS, replicas 0/1.
- Runtime `eaaa9f67-b9f2-41d2-832c-7d6fad9b9b00` SUCCESS, replicas 1/1.
- PIT/KRX deploy logs for 2026-11-15 01:15–02:25 UTC: 0 each. Runtime returned logs including 02:17:42 UTC Investing USD/KRW HTTP error and Yahoo fallback; not official PIT.
- Backend and push offline; db-query-readonly offline with one critical notification. Staged environment patch `e113dacb-6705-4416-9997-dc694539d382` since 2026-10-29 06:20:53 UTC, unchanged; do not deploy.
- Historical KRX 1565/1565 weekday stored pairs: prior storage-integrity PASS only; official calendar, trading status, corporate actions, fillability and costs NOT VERIFIED.

## Independent admission verdict
- Original filing 2021/2022 connected first-three-month operating income, period and correction lineage, exact public available-at, historical corp/security mapping: NOT VERIFIED.
- Official KRX session/trading-state, corporate actions, fillability, fees and tax: NOT VERIFIED.
- Post-cost/post-tax NetEV, PF, CAGR, MDD, ES95/99, concentration, temporal robustness: NOT VERIFIED; M20 NO-GO. H5 spent holdout cannot be reused.
- Offline historical CI jobs PASS as above; #418 later integrated CI FAIL; total-CI and official-backtest speedup NOT VERIFIED.

## Frozen constraints and next permitted steps
Maintain H5 frozen, M20 horizon20/purge20, WF504/126/126, PIT/label/Purged/CPCV/independent holdout/Champion/Top3/NO_TRADE and fixed cost/tax/execution/risk/promotion gates; ORDERING=false. Cache fail-closed on independent approved source/data/code/frozen/runtime/approval evidence SHA-256; parallelize only independent read-only postprocessing, never dependent retraining or capital transitions. No new official returns/model search or M20 run before source PIT approval. Independent owners should supply original-filing temporal/lineage proof and KRX official eligibility; #418 owner should resolve SHA source drift in isolated offline tests without modifying frozen source or workflow through a blocked permission path. No other Work code touched.
