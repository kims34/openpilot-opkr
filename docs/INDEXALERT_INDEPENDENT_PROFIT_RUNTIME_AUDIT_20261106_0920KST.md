# IndexAlert independent audit — 2026-11-06 09:20 KST

Scope: read-only GitHub/Railway evidence; no PIT approval, performance experiment, merge, deployment, or order.

## Current PR heads (GitHub get_pr_info)
- #412 OPEN Draft bf3d9514a87c53b1775e22ec9ba7711f6cecc49f
- #413 OPEN Draft f003ef6247e16fcc71bd3b1b20cd4904c4d984c0
- #414 OPEN Draft 18c5418d9684d1717df58261ea27f28e514385b2
- #418 OPEN Draft 2f98401cc50a6c6a25808a98516efd5bf0c944ee
- KRX #420 OPEN Draft fab3cbbd63a951a4e081f9e7f08c1391ca308581
- KRX #422 OPEN Draft c14857620973531013799e44625d43080904fd5f
- KRX #423 OPEN Draft 0e38004363cac9fc4475556b3a1c445de9af407f
- Research and development branch names exist; exact current HEAD NOT VERIFIED in this pass.

## Actions (direct job reads)
- 38381997417, 38382214223, 38419111311: 6/6 jobs success each.
- 38419649711: 1/1 success; 38419439742: 2/2 success.
- 41515392296: auto-anchor FAILURE; validation SKIPPED. Chronology approval blocked.
- Prior 34-case SHA 5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34, 13 mocks, 28 synthetic and 1.1315x regression-phase are historical evidence, NOT independently recalculated this pass. Full CI/backtest acceleration NOT VERIFIED.

## Railway production
- Project d1c1a050-b7d6-41ce-b300-13c20f82a20a; environment 83d5840b-270e-4d3f-a941-a37fd4a55ff7.
- PIT rebuild deployment 8b354fc1-cfb2-4ef0-863e-67f7f5dda2b5 SUCCESS; KRX worker 16c93d7c-7cd0-4d84-a327-298d2805376c SUCCESS. Neither produced deploy log entries in query since 2026-11-05T23:00Z. Historical OHLC 27/803 resolution NOT VERIFIED.
- Runtime deployment eaaa9f67-b9f2-41d2-832c-7d6fad9b9b00 SUCCESS; 2026-11-06T00:20:46Z logs show Investing USD/KRW HTTPError then Yahoo fallback; this is not official PIT evidence.
- Backend and push latest deployment FAILED; db-query-readonly has no latest deployment. Staged pending patch e113dacb-6705-4416-9997-dc694539d382 left untouched.

## Independent gates
- Historical KRX private 1565/1565 weekday-pair storage integrity: historical PASS only; official calendar/trading status, corporate actions, fillability, fees/tax NOT VERIFIED.
- Original filing, public available-at/PIT, 2021/2022 first-three-month consolidated operating income period/correction lineage, historical issuer/security mapping: NOT VERIFIED.
- NetEV/PF/CAGR/MDD/ES95/ES99/concentration/time robustness after costs and tax: NOT VERIFIED.
- M20 PIT/economics: NO-GO; Frozen H5, horizon20/purge20, WF504/126/126 and holdout restrictions unchanged. ORDERING=false policy; runtime variable value not independently inspected.
- Optimization: synthetic offline CI PASS within job-conclusion scope only; full speed-up NOT VERIFIED. Fail-closed cache evidence SHA requirements and read-only postprocessing parallelism unchanged.

Next safe steps: independent chronology original hash/provenance and original-filing timestamps; official KRX calendar/status lineage; check new worker logs; recompute fixed offline test manifest hashes only after isolated evidence capture. No economic run until separate PIT gate approval.
