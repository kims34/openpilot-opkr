# Independent profitability and runtime audit — 2026-11-06 16:25 KST

## Scope and source evidence
Read-only GitHub checks: branches `index-alert-research-v1` and `index-alert-position-regen-fix-v1` exist (branch search does not return HEAD SHA). Issue endpoint confirms open PRs #412, #413, #414, #418, #420, #422, #423; draft state and HEAD SHA were not returned by this endpoint and are NOT VERIFIED this run. The #414 gate file fetch failed with 404 on attempted refs, so no current blob SHA is asserted.

GitHub Actions job evidence (all conclusions directly retrieved):
- 38381997417: 6/6 success
- 38382214223: 6/6 success
- 38419111311: 6/6 success
- 38419649711: 1/1 success
- 38419439742: 2/2 success
- 41515392296: auto-anchor failure, validation skipped.

The historical 34-case SHA `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34`, 13 adversarial mocks, 28 synthetic cases and 2.9656s/2.6209s = 1.1315x regression-phase measurement are carried forward, NOT independently recomputed. No whole-CI or official-backtest speedup approval.

Railway IndexAlert production environment `83d5840b-270e-4d3f-a941-a37fd4a55ff7`: PIT rebuild latest deployment SUCCESS, running 1/1; KRX worker latest deployment SUCCESS, running 0/0 (no active replica); Runtime SUCCESS running 1/1. PIT and KRX worker deploy logs empty since 2026-11-06 05:00Z; historical 27/803 OHLC fix NOT VERIFIED. Backend, Push, db-query-readonly offline; db-query-readonly critical 1. Kiwoom real readonly reports online but replica running 0/crashed 1. Runtime log at 2026-11-06 07:22Z shows Investing.com USDKRW HTTP errors and Yahoo fallback.

**New consistency blocker:** Railway `describe_environment` reports `staged:null`, while `environment_status` simultaneously reports pending staged patch `e113dacb-6705-4416-9997-dc694539d382` (started 2026-10-29T06:20:53Z). Treat staged state as INCONSISTENT/NOT VERIFIED, do not accept, deploy or alter patch. Independently reconcile via read-only pending-work/staged-change APIs before any action.

## Admission decisions
- OpenDART original-filing semantics, public available-at and 2021/2022 first 3-month consolidated operating profit correction lineage: NOT VERIFIED. The historical 15 matching candidate signatures do not approve PIT.
- Historical issuer/security mapping, official KRX trading calendar/status/corporate actions, executable fills and cost/tax: NOT VERIFIED. Historical 1565/1565 weekday private storage integrity alone does not establish trading admissibility.
- NetEV, PF, CAGR, MDD, ES95/99, concentration, chronological robustness, annual risk-adjusted after-tax net profitability: NOT VERIFIED.
- Chronology anchor: FAIL (GitHub Action 41515392296); downstream validation SKIPPED.
- M20 PIT/economic run: NO-GO. H5 holdout consumed; no post-hoc retuning or independent reuse. ORDERING=false policy unchanged, live config not directly verified.

## Optimization isolation
Only offline synthetic and policy-safety tests permitted. Cache fail-closed on independently approved source/data/code/Frozen policy/runtime/approval evidence SHA-256. Parallelize read-only independent post-processing only; no dependent retraining or capital-transition parallelism. Keep H5/M20 horizon20 purge20 WF504/126/126, CPCV, holdout, Champion/Top3/NO_TRADE and frozen economics unchanged.

## Next read-only verification
Retrieve exact research/development and PR HEAD SHAs via authoritative refs; fetch #414 document at actual PR HEAD; inspect chronology-anchor failed job logs; reconcile Railway staged state discrepancy and KRX OHLC evidence. No workflow modification, PR merge, deployment, ordering, model search, real trade or account change authorized.
