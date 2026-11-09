# IndexAlert independent profitability and offline optimization audit — 2026-11-09 21:17 KST

Scope: read-only GitHub/Railway evidence; no new economic run, no order, no deployment, no merge. Source truth is scoped to observed tool results. Frozen H5, M20 horizon20/purge20, WF504/126/126, independent holdout, CPCV/Purged, NO_TRADE, cost/tax/risk and promotion policy unchanged.

## Repository evidence
- Research `index-alert-research-v1`: compare to df474df348f22aa38b1dedaa59fcff66e548b406 => identical, ahead 0 behind 0. Thus HEAD df474df348f22aa38b1dedaa59fcff66e548b406.
- Development `index-alert-position-regen-fix-v1`: compare to 1e6367d2863a86c3470da13d81a955d277eba485 => identical, ahead 0 behind 0. Thus HEAD 1e6367d2863a86c3470da13d81a955d277eba485.
- PR #414 integration gate file at commit 18c5418d9684d1717df58261ea27f28e514385b2: Git blob 984c933651f39f1ee9e26a1d7ac3893aaa5335be. This establishes file content only, not current PR HEAD or Draft status.
- PR #412/#413/#414/#418 and KRX #420/#422/#423 live PR metadata: NOT VERIFIED this run (GitHub issue search returned empty; no unsupported state inference).
- GitHub Actions jobs directly checked: 38381997417 6/6 success; 38382214223 6/6 success; 38419111311 6/6 success; 38419649711 1/1 success; OpenDART 38419439742 2/2 success. Chronology 41515392296 auto-anchor failure, validation skipped. Prior 34-case SHA 5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34 and 1.1315x regression-phase ratio are prior observations, NOT independently recalculated now. Whole-CI and official-backtest acceleration NOT VERIFIED.

## Railway production
Project d1c1a050-b7d6-41ce-b300-13c20f82a20a.
- PIT rebuild deployment 8b354fc1-cfb2-4ef0-863e-67f7f5dda2b5 SUCCESS, 1/1 running; latest sampled log 2026-11-09 12:16:00Z (21:16 KST) reports KRXProspectiveOpenAPISourceError COMMON_OHLC_NONPOSITIVE, 27 nonpositive OHLC of 803 common-stock rows and 27 zero volume/value rows. independent_source_admission_verified=false, fresh_alpha_observation_admitted=false, live_order_authorized=false, ordering=DISABLED. Fail-closed guard PASS; source admission FAIL/BLOCKED. Do not equate this sample with all KRX history.
- KRX worker deployment 16c93d7c-7cd0-4d84-a327-298d2805376c SUCCESS; runtime status online but running=0 crashed=0 total=1 (cron/idle ambiguity; actual execution NOT VERIFIED); no logs in 20:00–21:17 KST window.
- Kiwoom real read-only deployment a77fb922-b679-4d88-92c4-03054ec579cd SUCCESS but running=0 crashed=1 total=1: runtime FAIL. No logs in window.
- Runtime 1/1 running. Backend and push offline; db-query-readonly offline with one critical.
- Environment describe staged=null but status reports staged empty patch e113dacb-6705-4416-9997-dc694539d382, no changes; no apply.
- Latest deployment timestamps are older than this run; deployment SUCCESS does not prove live health.

## Independent profitability gates
- Official original-filing / exact public available-at / 2021–2022 first 3-month consolidated operating income period and correction lineage: NOT VERIFIED; candidate SGML rows are not semantic/PIT approval.
- Historical corp/security mapping, KRX calendar/trading status/corporate actions/executability/cost and tax: NOT VERIFIED; earlier 1565/1565 private weekday raw-pair integrity is prior limited PASS only.
- After-tax NetEV, PF, CAGR, MDD, ES95/99, return concentration and time-robustness: NOT VERIFIED, no approved official economic run.
- Chronology anchor CI FAIL; M20 NO-GO. Consumed H5 holdout and Dynamic output must not be retuned/reused.
- Optimization isolated PR #413/#418 software CI success only. Cache only on matching independently approved source/data/code/Frozen/runtime/approval SHA-256, otherwise fail closed; only independent read-only postprocessing parallel. No dependent retraining/capital-transition parallelism.

## Next independent checks
1. Obtain authoritative original filing and publication-time lineage, Q3 period/consolidation and corp/security mapping without backfilling corrections.
2. Diagnose KRX 27 invalid rows against official trading-state/corporate-action data and original SHA; do not relax filters.
3. Investigate chronology anchor HTTP 404 / failed job without changing workflow protections; independently verify live PR states and original test SHA.
4. Diagnose crashed read-only replica without restart or deploy. Confirm live ORDERING configuration separately if permitted; runtime logs show DISABLED, not necessarily config value.
5. Only after independently approved PIT, market execution and cost/tax evidence, request separate authorization before any M20 economic run or promotion.
