# IndexAlert independent profit and offline optimization audit — 2026-11-09 23:28 KST

Read-only verification. No trading, deployment, merge, workflow modification, official-market backtest, model search, or promotion. This audit is independent of PR #413/#414/#418. ORDERING=false is a required policy; the actual environment variable was not independently read.

## Current GitHub PR heads (direct API)
- OpenDART #412 OPEN Draft: bf3d9514a87c53b1775e22ec9ba7711f6cecc49f
- Offline optimization #413 OPEN Draft: f003ef6247e16fcc71bd3b1b20cd4904c4d984c0
- Profitability gate #414 OPEN Draft: 18c5418d9684d1717df58261ea27f28e514385b2
- Single runner #418 OPEN Draft: 2f98401cc50a6c6a25808a98516efd5bf0c944ee
- KRX #420 OPEN Draft: fab3cbbd63a951a4e081f9e7f08c1391ca308581
- KRX #422 OPEN Draft: c14857620973531013799e44625d43080904fd5f
- KRX #423 OPEN Draft: 0e38004363cac9fc4475556b3a1c445de9af407f
- Exact research branch index-alert-research-v1 and development branch index-alert-position-regen-fix-v1 tips NOT VERIFIED in this pass. Direct fetch of integration-gate document from these branches returned 404, which is not evidence the document is missing from #414.

## Actions (direct job API, historical run IDs)
- 38381997417 6/6 SUCCESS; 38382214223 6/6 SUCCESS; 38419111311 6/6 SUCCESS.
- 38419649711 1/1 SUCCESS; 38419439742 2/2 SUCCESS.
- 41515392296 auto-anchor FAILURE, validation SKIPPED. Earlier HTTP 404 root-cause remains NOT VERIFIED.
- Prior fixed 34-case SHA-256 5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34 and synthetic 28-case claims were not independently recomputed this pass. Reported 2.9656/2.6209=1.1315x applies only to regression phase; end-to-end acceleration NOT VERIFIED.

## Railway production (direct get_status/get_logs)
- Project d1c1a050-b7d6-41ce-b300-13c20f82a20a, environment 83d5840b-270e-4d3f-a941-a37fd4a55ff7.
- PIT rebuild latest deployment SUCCESS (2026-10-10), KRX worker SUCCESS (2026-10-12), runtime SUCCESS (2026-10-05), real-readonly SUCCESS (2026-10-29). Backend and push latest deployment FAILED. All replica counts returned null: runtime health NOT VERIFIED, and successful deployment does not establish running replicas.
- stagedChanges=null but pendingWork contains staged patch e113dacb-6705-4416-9997-dc694539d382 with empty changes; untouched.
- PIT logs at 22:01, 22:16, 22:31, 22:46, 23:01, 23:16 KST report KRXProspectiveOpenAPISourceError / COMMON_OHLC_NONPOSITIVE: common-stock 803 rows, nonpositive OHLC 27, zero volume/value 27; fresh observation not admitted, live order and funds movement unauthorized, ordering DISABLED. Fail-closed safety PASS, KRX source admission FAIL/BLOCKED.
- KRX worker and real-readonly service returned no deploy logs for 22:00–23:28 KST; this does not prove healthy runtime.

## Economic evidence verdict
- Official original-filing and public available-at/PIT: NOT VERIFIED.
- 2021/2022 initial three-month consolidated operating profit, correction lineage and issuer/security historical mappings: NOT VERIFIED.
- Historical private weekday pairs 1565/1565 integrity: previously reported PASS, not revalidated here. Official trading calendar/status, corporate actions, executability and tax/cost realism: NOT VERIFIED.
- Chronology Anchor: FAIL on historical Action; current root cause NOT VERIFIED.
- NetEV/PF/CAGR/MDD/ES95/99, concentration, regime/time robustness, after-cost and tax annual risk-adjusted net return: NOT VERIFIED. M20 NO-GO.
- Frozen H5 and M20 horizon20/purge20, WF504/126/126, PIT/label/Purged/CPCV/independent Holdout/Champion/Top3/NO_TRADE remain unchanged. Consumed H5 holdout and Dynamic results must not be reused or tuned post hoc.
- Cache fail-closed on independently approved source/data/code/Frozen/runtime/evidence SHA-256. Only read-only independent postprocessing parallelizable; no dependent retraining or capital transition parallelism.

## Next independent evidence needed
1. Obtain official original-filing/available-at and 2021/2022 initial-quarter consolidated operating-profit correction lineage with immutable SHA.
2. Resolve 27 KRX source rows against official session/state/corporate-action records, without admitting observations until independent approval.
3. Resolve Chronology Anchor 404 and independently verify execution/market mapping; no M20 profitability execution until PIT and source gates PASS.
4. Confirm research/development exact HEAD via direct branch ref, plus isolated runner CI hash/whole-pipeline benchmarks only under allowed synthetic offline safety scope.
