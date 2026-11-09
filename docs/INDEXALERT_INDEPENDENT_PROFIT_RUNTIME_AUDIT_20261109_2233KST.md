# IndexAlert independent audit — 2026-11-09 22:33 KST

Read-only evidence review; no economic run, trading, deployment, merge, workflow edits or promotion. Frozen H5, M20 horizon20/purge20, WF504/126/126, holdout/CPCV/Purged, NO_TRADE and cost/tax/risk policy unchanged.

## GitHub evidence
- Branch names `index-alert-research-v1`, `index-alert-position-regen-fix-v1`, and independent audit branch were discovered; this connector's branch search returns names, not current HEAD. **Current exact branch HEAD NOT VERIFIED**. Previous 21:17 audit reported research `df474df348f22aa38b1dedaa59fcff66e548b406` and development `1e6367d2863a86c3470da13d81a955d277eba485` (historical, not fresh).
- GitHub PR metadata search returned no results for open PRs; current #412/#413/#414/#418 and KRX #420/#422/#423 states/HEADs **NOT VERIFIED**. Gate file read from research branch returned 404; prior #414 gate blob `984c933651f39f1ee9e26a1d7ac3893aaa5335be` is historical only. No PR edits.
- Direct GitHub Actions jobs: 38381997417 **6/6 PASS**, 38382214223 **6/6 PASS**, 38419111311 **6/6 PASS**, 38419649711 **1/1 PASS**, OpenDART 38419439742 **2/2 PASS**. These are offline software/candidate checks, not source or economic approval. Previously reported immutable 34-case SHA-256 `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34` and serial 2.9656s / concurrent 2.6209s = 1.1315x are NOT recalculated this run; whole CI and official-backtest speed NOT VERIFIED.
- Chronology run 41515392296: auto-anchor FAILURE at public hash-only payload fetch; validation SKIPPED. Prior HTTP 404 detail not independently reread in this run.

## Railway production (project d1c1a050-b7d6-41ce-b300-13c20f82a20a)
- PIT rebuild deployment `8b354fc1-cfb2-4ef0-863e-67f7f5dda2b5` SUCCESS, replica running 1/1. Latest sampled log 2026-11-09 13:31:08Z = 22:31:08 KST: `FAIL_CLOSED`, `COMMON_OHLC_NONPOSITIVE`, original failure session 2026-09-28, common-stock 803 rows / nonpositive OHLC 27 / zero volume-and-value 27. `independent_source_admission_verified=false`, `fresh_alpha_observation_admitted=false`, `session_manifest_sha256=null`, `ordering=DISABLED`, `live_order_authorized=false`. **Safety guard PASS; source admission FAIL/BLOCKED**. Private rejected-source receipt reportedly saved; its bytes/SHA NOT VERIFIED.
- KRX historical worker deployment `16c93d7c-7cd0-4d84-a327-298d2805376c` SUCCESS, status online but replica running 0 / crashed 0 / total 1; no returned logs in checked period. Historical 1565/1565 weekday raw pairs remain a prior storage-integrity-only PASS, not official calendar/trading-status approval.
- Real-account read-only deployment `a77fb922-b679-4d88-92c4-03054ec579cd` SUCCESS but replica running 0 / crashed 1 / total 1: **runtime FAIL**. Runtime and PIT rebuild 1/1 running; backend and push offline; db-query-readonly offline with 1 critical.
- Environment describe reports staged=null while status reports empty staged patch `e113dacb-6705-4416-9997-dc694539d382`; discrepancy NOT VERIFIED, do not apply.

## Independent gates
- Original filing/public available-at, 2021/2022 first-three-month consolidated operating income period/correction lineage, historical corp/security map: **NOT VERIFIED**.
- Official KRX calendar/trading state/corporate actions/executability, transaction costs/tax: **NOT VERIFIED**.
- After-cost-and-tax risk-adjusted annual net profit, NetEV/PF/CAGR/MDD/ES95/ES99, concentration, time robustness: **NOT VERIFIED**. **M20 NO-GO**.
- PR #413/#418 optimization remains offline-only. Fail-closed cache requires independently approved source/data/code/Frozen/runtime/approval evidence SHA-256; only independent read-only postprocessing parallel; no dependent retraining/capital-transition parallelism. Consumed H5 holdout and Dynamic results cannot be retuned/reused.

## Next safe checks
Obtain exact live branch/PR HEAD and source SHA through authorized read-only GitHub endpoint; independently inspect original DART first-publication timestamps and 2021/2022 correction lineage; inspect official KRX original 27-row trading-state evidence without weakening filters; diagnose chronology anchor and crashed read-only replica without workflow edits or deployment; independently verify ORDERING environment configuration. No official-market economic test until PIT/source gate independently approved.
