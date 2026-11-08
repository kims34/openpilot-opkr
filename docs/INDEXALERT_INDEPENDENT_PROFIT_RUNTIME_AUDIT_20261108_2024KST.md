# IndexAlert independent read-only audit — 2026-11-08 20:24 KST

Scope: independent profitability evidence gate and isolated offline-only optimisation review. This is NOT a PIT approval, economic run, merge, deployment, or order authority.

## Verified in this run
- Research branch `index-alert-research-v1` compare to `df474df348f22aa38b1dedaa59fcff66e548b406`: identical (ahead=0, behind=0). Development `index-alert-position-regen-fix-v1` compare to `1e6367d2863a86c3470da13d81a955d277eba485`: identical.
- PR #414 integration document read at historical PR HEAD `18c5418d9684d1717df58261ea27f28e514385b2`; blob SHA `984c933651f39f1ee9e26a1d7ac3893aaa5335be`. Current PR heads/draft state not independently established in this run (GitHub issue search returned no matches); do not infer from prior reports.
- Actions job endpoints: #38381997417 6/6 success; #38382214223 6/6 success; #38419111311 6/6 success; #38419649711 1/1 success; #38419439742 2/2 success. Job result success is offline software evidence only, not economic/PIT approval. Existing 34-case SHA `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34`, 28 synthetic cases and timings 2.9656/2.6209s are PRIOR evidence, not recomputed this run.
- Chronology Action #41515392296: auto-anchor FAIL at 'Fetch today's public hash-only prospective payload'; validation SKIPPED.
- Railway IndexAlert production inventory: no staged patch; PIT rebuild deployment `8b354fc1-cfb2-4ef0-863e-67f7f5dda2b5` SUCCESS; KRX worker `16c93d7c-7cd0-4d84-a327-298d2805376c` SUCCESS; real readonly `a77fb922-b679-4d88-92c4-03054ec579cd` SUCCESS (deployment status is not replica health). Backend/push latest FAILED. KRX and real readonly service deploy logs empty in queried 2026-11-08 10:00Z onward interval.
- PIT deploy logs at 10:00, 10:15, 10:30, 10:45, 11:00, 11:15 UTC: `FAIL_CLOSED`, `ordering=DISABLED`, `KRXProspectiveOpenAPISourceError/COMMON_OHLC_NONPOSITIVE`; common-stock 803, nonpositive OHLC 27, zero-volume/value 27, source failure session 2026-09-28. No fresh alpha admitted, no source/chronology/model admission; session manifest SHA null. Repeated receipts of historical source failure, not new distinct market incidents.

## Decision table
- Prior KRX 1565/1565 weekday private pair storage integrity: PASS **historical evidence only**; official trading calendar, trading states, corporate actions, fills and tax/cost: NOT VERIFIED.
- Original filing, exact public available-at, 2021/2022 initial 3-month consolidated operating profit, period/correction lineage, historic corp/security mapping: NOT VERIFIED / FAIL-CLOSED.
- Chronology anchor latest inspected run: FAIL; downstream validation SKIPPED.
- NetEV, PF, CAGR, MDD, ES95/99, return concentration, temporal robustness after fees/tax: NOT VERIFIED; M20 RUN NO-GO.
- Optimisation offline job execution: PASS for inspected jobs only. Independent SHA artifact recalculation and end-to-end official backtest speed: NOT VERIFIED.
- Frozen H5; M20 horizon20/purge20, WF504/126/126, independent Holdout, Champion/Top3/NO_TRADE and policy thresholds unchanged. ORDERING=false.

## Next evidence gates
1. DART Work: exact original SGML period/consolidation/available-at and correction lineage with immutable hashes.
2. KRX Work: official calendar, security status, corporate actions and execution/cost/tax validation, preserving all vetoes.
3. Chronology Work: resolve failed public hash-only payload and obtain independent immutable anchor evidence; do not bypass failure.
4. Optimisation Work: only isolated synthetic offline fail-closed and immutable regression parity; no official market performance run, parameter search, dependent retraining parallelism, or capital-transition parallelism.
5. Re-read current PR heads/status with a working GitHub PR endpoint; search_issues yielded empty and is not proof of absence.

No code/workflow modification, PR merge, deployment, credential/permission change, live order, funds movement or Champion promotion authorised.
