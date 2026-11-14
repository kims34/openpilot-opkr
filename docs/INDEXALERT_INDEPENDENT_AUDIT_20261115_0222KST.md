# IndexAlert independent evidence audit — 2026-11-15 02:22 KST

Scope: read-only GitHub/Railway checks; no PIT approval, no official market performance run, no trading, deployment, workflow edit or merge. Historical user-supplied evidence is not independently reapproved.

## Exact current refs
- research index-alert-research-v1: df474df348f22aa38b1dedaa59fcff66e548b406 (compare ref to itself)
- development index-alert-position-regen-fix-v1: 1e6367d2863a86c3470da13d81a955d277eba485
- Draft/open/unmerged PR HEADs: #412 bf3d9514a87c53b1775e22ec9ba7711f6cecc49f; #413 f003ef6247e16fcc71bd3b1b20cd4904c4d984c0; #414 18c5418d9684d1717df58261ea27f28e514385b2; #418 2f98401cc50a6c6a25808a98516efd5bf0c944ee; #420 fab3cbbd63a951a4e081f9e7f08c1391ca308581; #422 c14857620973531013799e44625d43080904fd5f; #423 0e38004363cac9fc4475556b3a1c445de9af407f.
- #414 integration gate blob SHA-1 984c933651f39f1ee9e26a1d7ac3893aaa5335be.

## Actions and optimization
- 38381997417 6/6 PASS; 38382214223 6/6 PASS; 38419111311 6/6 PASS; 38419649711 1/1 PASS; OpenDART 38419439742 2/2 PASS. These are software CI results, not PIT or market profitability approvals.
- #418 integration run 38486028854 job 115599778959 FAIL: SourceDriftError research_v1_runtime_manifest.py archived Git blob expected 108f66714602a1bd3ae42c34dcca7c16e38f460b observed e428789e2e97ca7be3a4482e0df23b483a1ad69d. No hash bypass or baseline replacement permitted. Original archived 34-case SHA-256 5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34 is historical evidence, NOT independently recomputed this run. Whole-CI/official-backtest acceleration NOT VERIFIED. Historical regression-phase 1.1315x is not acceleration.

## Railway production (read-only)
- project d1c1a050-b7d6-41ce-b300-13c20f82a20a; environment 83d5840b-270e-4d3f-a941-a37fd4a55ff7.
- PIT rebuild deployment 8b354fc1-cfb2-4ef0-863e-67f7f5dda2b5 SUCCESS 1/1; Runtime eaaa9f67-b9f2-41d2-832c-7d6fad9b9b00 SUCCESS 1/1; KRX worker 16c93d7c-7cd0-4d84-a327-298d2805376c SUCCESS 0/1; Kiwoom real-readonly-run 6d3d5812-eb91-41b6-acba-9c62a68b3271 SUCCESS 0/1. Offline: push, backend, db-query-readonly. These deployment labels do not prove service PIT fitness.
- pending staged patch e113dacb-6705-4416-9997-dc694539d382 (since 2026-10-29 06:20:53Z) remains; no commit/deploy attempted.
- 2026-11-14 16:20–17:25 UTC: PIT and KRX queried deploy logs returned zero entries; this is not proof of zero processing. Runtime logs showed market quote polling, including 17:22:39Z USD/KRW Investing quote and 17:22:42Z Yahoo/ECOS close alignment; not official PIT evidence.

## Gate decisions
- Official original-filing and exact public available-at/PIT: NOT VERIFIED. 2021/2022 first three months consolidated operating profit period/amendment lineage: NOT VERIFIED. Historical company/security mapping: NOT VERIFIED. Official KRX calendar, halts, corporate actions, fillability and taxes/costs: NOT VERIFIED. 1565/1565 weekday original pair storage integrity: historical PASS only; 90-day uncertain and 12003 zero-activity rows excluded, not admitted.
- Independent post-cost/tax annual risk-adjusted NetEV, PF, CAGR, MDD, ES95/99, concentration, temporal robustness: NOT VERIFIED. H5 failed/consumed holdout cannot be reused; M20 PIT and profitability RUN NO-GO.
- Frozen H5; M20 horizon20/purge20, WF504/126/126, Purged/CPCV, independent holdout, Champion/Top3/NO_TRADE and risk/cost/upgrade policy unchanged. ORDERING=false. No live order, money movement, permissions change, champion promotion, PR merge or production deployment.
- Optimization: offline synthetic policy checks only; cache fail-closed on independently approved original/data/code/Frozen/runtime/evidence SHA-256 equality; parallelize read-only postprocessing only, not dependent retraining or capital transition.

## Next evidence-only actions
1. Independently trace archived manifest bytes/commit provenance in #418 without altering frozen expectation; keep CI FAIL until genuine source lineage is resolved.
2. Acquire authoritative DART first-filed original and public timestamp + correction lineage and official KRX calendar/status/corporate-action/fillability lineage with immutable SHA/evidence; until then do not run M20 economic tests.
3. Resolve Railway pending patch discrepancy via read-only status inspection; no deployment.
