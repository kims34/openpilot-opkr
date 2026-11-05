# IndexAlert independent profitability and offline optimisation audit — 2026-11-06 06:21 KST

Scope: read-only GitHub/Railway checks; no official market performance experiment, M20 run, deployment, merge or order.

## Direct evidence
- GitHub branches `index-alert-research-v1` and `index-alert-position-regen-fix-v1` exist (branch search). Exact current HEAD SHA: **NOT VERIFIED** (branch search returns names only).
- PR #412/#413/#414/#418 and KRX #420/#422/#423: current PR HEAD/draft state **NOT VERIFIED** in this run (repository issue search returned no results); do not infer unchanged status from previous runs. Integration gate document fetch on research branch returned 404; alternative guessed ref also 404. No policy approval inferred.
- GitHub Actions run 38381997417: 6/6 success; 38382214223: 6/6 success; 38419111311: 6/6 success; 38419649711: 1/1 success; OpenDART 38419439742: 2/2 success. Direct jobs API. Run 41515392296 auto-anchor failure and validation skipped. Job success does not establish economic validity or original filing semantics.
- Historical fixed 34-case SHA `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34`, 13 adversarial mocks, 28 synthetic cases, and regression-only 1.1315x are **previous evidence, not independently recomputed this run**.
- Railway project `d1c1a050-b7d6-41ce-b300-13c20f82a20a`, production `83d5840b-270e-4d3f-a941-a37fd4a55ff7`: PIT rebuild deployment `8b354fc1-cfb2-4ef0-863e-67f7f5dda2b5` SUCCESS, running 1/1; KRX historical worker deployment `16c93d7c-7cd0-4d84-a327-298d2805376c` SUCCESS, running 0/1; runtime running 1/1. Backend, push and db-query-readonly offline; db-query-readonly one critical. Kiwoom real readonly shows 0 running/1 crashed despite service state online. One staged patch remains, untouched.
- Railway PIT and KRX worker logs queried from 2026-11-05 20:00 UTC: both returned zero deploy log entries. Current 27/803 OHLC failure recurrence **NOT VERIFIED**; prior observed invalid rows remain unapproved.

## Independent gates
- Historical 1565/1565 weekday pair storage integrity: **PASS only for previously recorded storage-pair evidence**; official KRX calendar, trade status, corporate actions, fills, taxes, instrument history mapping: **NOT VERIFIED**.
- Original-filing, public available-at PIT, 2021/2022 first-three-month consolidated operating profit period and correction lineage: **NOT VERIFIED**. Candidate row matching is not semantic/time approval.
- Chronology anchor: **FAIL**; validation **SKIPPED**.
- Synthetic offline regression CI: **PASS (specified runs only)**; full CI/official backtest acceleration: **NOT VERIFIED**.
- NetEV/PF/CAGR/MDD/ES95/ES99, concentration and temporal robustness after costs/tax: **NOT VERIFIED**. M20: **NO-GO**.
- ORDERING=false, fail-closed, no champion promotion or live orders remain mandatory. No independent evidence authorising relaxation.

## Next safe steps
Read exact branch/PR HEAD and file blob hashes using an authoritative ref-aware endpoint; inspect chronology anchor failed job logs; obtain official original-filing and KRX source lineage with independent SHA before reconsidering PIT. Keep cache keyed on approved source/data/code/Frozen/runtime/evidence SHA256, parallelise only independent read-only postprocessing; no dependent retraining or capital transition parallelisation. Do not alter Frozen H5, M20 horizon20/purge20, WF504/126/126, holdout or promotion gates. Avoid other Work-owned code and workflow writes.
