# IndexAlert independent profitability/runtime audit — 2026-11-06 00:25 KST

## Scope and immutable boundaries
Read-only source/CI/production inspection. No M20 run, market-return generation, optimization search, H5/Holdout reuse, model promotion, order, merge, deployment, workflow change or staged patch application. ORDERING remains disabled by policy; runtime observation noted below.

## Verified GitHub refs at inspection
- Research `index-alert-research-v1`: `df474df348f22aa38b1dedaa59fcff66e548b406` (self-compare ref resolution).
- Development `index-alert-position-regen-fix-v1`: `1e6367d2863a86c3470da13d81a955d277eba485`.
- Draft OPEN #412: `bf3d9514a87c53b1775e22ec9ba7711f6cecc49f`.
- Draft OPEN #413: `f003ef6247e16fcc71bd3b1b20cd4904c4d984c0`.
- Draft OPEN #414: `18c5418d9684d1717df58261ea27f28e514385b2`.
- Draft OPEN #418: `2f98401cc50a6c6a25808a98516efd5bf0c944ee`.
- Draft OPEN KRX #420: `fab3cbbd63a951a4e081f9e7f08c1391ca308581`; #422: `c14857620973531013799e44625d43080904fd5f`; #423: `0e38004363cac9fc4475556b3a1c445de9af407f`.
- #414 gate file blob `984c933651f39f1ee9e26a1d7ac3893aaa5335be`, read directly at its PR branch. Confirms M20 source PIT NO-GO.

## CI jobs (read-only, current API response)
- Actions 38381997417, 38382214223, 38419111311: 6/6 jobs success each.
- Action 38419649711: 1/1 success; Action 38419439742: 2/2 success.
- Chronology 41515392296: auto-anchor FAILURE; validation SKIPPED.
- Historic 34-case digest `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34` and 1.1315x regression-only measurement are *prior supplied evidence*, not independently recomputed this run. Overall CI speedup and official backtest speedup NOT VERIFIED.

## Railway production (read-only)
Project `d1c1a050-b7d6-41ce-b300-13c20f82a20a`, environment `83d5840b-270e-4d3f-a941-a37fd4a55ff7`.
- PIT rebuild deployment `8b354fc1-cfb2-4ef0-863e-67f7f5dda2b5` SUCCESS, running 1/1. Latest retrieved event 2026-11-05 14:46:31 UTC: `KRXProspectiveOpenAPISourceError`, `COMMON_OHLC_NONPOSITIVE`, `fresh_alpha_observation_admitted=false`, `live_order_authorized=false`; prior 27/803 nonpositive rows remain unresolved, not independently re-counted here. Source veto PASS, source admission FAIL.
- KRX historical worker `16c93d7c-7cd0-4d84-a327-298d2805376c` SUCCESS but running 0/1; no logs in query since 14:00 UTC.
- Runtime `eaaa9f67-b9f2-41d2-832c-7d6fad9b9b00` SUCCESS, running 1/1.
- Kiwoom real read-only `a77fb922-b679-4d88-92c4-03054ec579cd` SUCCESS but running 0, crashed 1; backend/push offline and db-query-readonly critical. Staged environment patch `e113dacb-6705-4416-9997-dc694539d382` untouched.

## Independent verdict and next safe work
- KRX 2017–2022 1565/1565 weekday private storage SHA integrity: historical PASS only. Official session calendar, 90-day classification, 12003 zero-activity observations, security history, corporate actions, 2026-09-28 veto row resolution and tradability: NOT VERIFIED / fail-closed.
- OpenDART SGML candidate signatures 15 rows: historical structural evidence only; original filing, public available-at, exact 2021/2022 CFS first three-month operating income, corrections and security mapping NOT VERIFIED.
- NetEV/PF/CAGR/MDD/ES95/99, taxes, execution, concentration, temporal robustness: NOT EVALUABLE. M20 NO-GO.
- Optimization #413/#418 synthetic regression CI PASS only; SHA-gated fail-closed cache and read-only independent postprocessing only. No dependent training/capital-transition parallelization.
- Next: independent official source-level KRX row/status lineage and DART timestamp/period lineage, then immutable evidence SHA review; synthetic offline safety checks only until source PIT admission. No approval to run M20.
