# IndexAlert independent audit — 2026-11-16 02:23 KST

Scope: read-only GitHub/Railway evidence and a single isolated audit-document write. No workflow, source, strategy, live deployment, orders, funding, credentials, champion, merges or economic backtests modified.

## GitHub exact PR HEADs (fresh get_pr_info)
| PR | HEAD | status |
|---|---|---|
| #412 OpenDART | bf3d9514a87c53b1775e22ec9ba7711f6cecc49f | OPEN DRAFT |
| #413 isolated optimizer | f003ef6247e16fcc71bd3b1b20cd4904c4d984c0 | OPEN DRAFT |
| #414 integration | 18c5418d9684d1717df58261ea27f28e514385b2 | OPEN DRAFT |
| #418 single runner | 2f98401cc50a6c6a25808a98516efd5bf0c944ee | OPEN DRAFT |
| #420 KRX | fab3cbbd63a951a4e081f9e7f08c1391ca308581 | OPEN DRAFT |
| #422 KRX | c14857620973531013799e44625d43080904fd5f | OPEN DRAFT |
| #423 KRX | 0e38004363cac9fc4475556b3a1c445de9af407f | OPEN DRAFT |

Research branch index-alert-research-v1 and development index-alert-position-regen-fix-v1 names confirmed to exist; exact *current* branch tips NOT VERIFIED by this connector. Historical research df474df348f22aa38b1dedaa59fcff66e548b406 and deployed development 1e6367d2863a86c3470da13d81a955d277eba485 are NOT treated as current HEADs.

## Actual GitHub Actions evidence
- 38381997417 6/6 PASS, 38382214223 6/6 PASS, 38419111311 6/6 PASS, 38419439742 2/2 PASS, 38419649711 1/1 PASS.
- 38486028854 1/1 FAIL; job 115599778959 original regression-source blob identity step FAIL; archived-case and four-suite parity tests SKIPPED. Previously reported research_v1_runtime_manifest.py expected Git blob SHA-1 108f66714602a1bd3ae42c34dcca7c16e38f460b vs observed e428789e2e97ca7be3a4482e0df23b483a1ad69d (not freshly extracted from full raw log this run).
- Fixed 34-case SHA-256 5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34 independently recomputed this run: NOT VERIFIED. Prior synthetic serial 2.9656s / parallel 2.6209s = 1.1315x regression-phase only; whole CI and official backtest acceleration NOT VERIFIED.
- Integration gate document fetched at PR #414 branch, blob SHA-1 984c933651f39f1ee9e26a1d7ac3893aaa5335be.

## Railway production fresh read-only
Project d1c1a050-b7d6-41ce-b300-13c20f82a20a, environment 83d5840b-270e-4d3f-a941-a37fd4a55ff7. PIT rebuild 1/1 and runtime 1/1 running; KRX historical worker 0/1 running despite deployment SUCCESS (do not conflate deployment with active worker). Backend and push offline; db-query-readonly offline with one critical notification. Environment-status pendingWork contains STAGED patch e113dacb-6705-4416-9997-dc694539d382 begun 2026-10-29T06:20:53Z, while describe_environment staged=null: discrepancy NOT resolved.
- Logs window 2026-11-15 16:15–17:25 UTC: PIT rebuild 0 entries; KRX historical worker 0 entries. Zero logs is not success and does not overturn previously observed prospective KRX FAIL_CLOSED COMMON_OHLC_NONPOSITIVE (27/803, 2026-09-28 first failure session).
- Runtime at 17:19 UTC: Investing USD/KRW HTTPError, Yahoo fallback. Not authoritative market PIT or tradability evidence.
- Historical private 1565/1565 weekday raw-pair storage integrity PASS (prior evidence only), official session calendar/trading status/corporate actions/fills NOT VERIFIED.

## Independent admission verdict
- OpenDART original filing, public available-at/PIT, 2021/2022 initial consolidated three-month operating income period and correction lineage: NOT VERIFIED. Action 38419439742 software candidate rows PASS does NOT approve semantics or timestamp.
- Historical corp/security mapping: NOT VERIFIED.
- Prospective KRX OHLC source-quality: FAIL based on prior observed 27/803 invalid rows; fail-closed safety veto previously observed PASS, fresh recurrence this window NOT VERIFIED.
- KRX official calendar, status, corporate actions, fills, fees and taxes: NOT VERIFIED.
- NetEV/PF/CAGR/MDD/ES95/99, concentration, temporal robustness and annual risk-adjusted net profitability after costs/tax: NOT VERIFIED; M20 economic run NOT AUTHORIZED, H5 consumed holdout not reused.
- Optimizer synthetic offline job PASS only for original five runs, integrated #418 FAIL; official speed NOT VERIFIED.

## Fixed guardrails / next safe steps
Frozen H5, M20 horizon20/purge20, WF504/126/126, PIT/labels/Purged/CPCV/independent holdout/Champion/Top3/NO_TRADE, costs/taxes/risk gates unchanged. ORDERING=false. Cache requires independently approved raw/data/code/policy/runtime/authorization SHA-256 identity and fails closed. Only independent read-only postprocessing may parallelize; no dependent retraining/capital transition parallelization.
1. KRX owner: independently reconcile 27 nonpositive OHLC rows with official original SHA, official sessions/status/actions, preserve veto.
2. DART owner: prove first-filed period and public available-at/correction lineage, never backfill initial with amended.
3. PR #418 owner: isolate immutable manifest mismatch, synthetic offline-only retest, no workflow security bypass.
4. Independently retrieve research/development current branch tips and recompute original case fingerprint before approval.
