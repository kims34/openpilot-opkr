# IndexAlert independent read-only audit — 2026-11-09 14:16 KST

## Scope and provenance
Read-only GitHub connector PR metadata and Actions job conclusions, Railway production service descriptions/deployments/logs queried in this run. This is NOT a source-PIT approval, trading authorization, performance run, or full code review. Research branch `index-alert-research-v1` and development branch `index-alert-position-regen-fix-v1` existence checked; exact current branch tips NOT VERIFIED (historical reference research df474df348f22aa38b1dedaa59fcff66e548b406, development 1e6367d2863a86c3470da13d81a955d277eba485 are not promoted to fresh HEAD).

## PR metadata (OPEN, Draft, unmerged)
- #412 bf3d9514a87c53b1775e22ec9ba7711f6cecc49f
- #413 f003ef6247e16fcc71bd3b1b20cd4904c4d984c0
- #414 18c5418d9684d1717df58261ea27f28e514385b2
- #418 2f98401cc50a6c6a25808a98516efd5bf0c944ee
- KRX #420 fab3cbbd63a951a4e081f9e7f08c1391ca308581
- KRX #422 c14857620973531013799e44625d43080904fd5f
- KRX #423 0e38004363cac9fc4475556b3a1c445de9af407f

## Actual Actions job check
- 38381997417: 6/6 success
- 38382214223: 6/6 success
- 38419111311: 6/6 success
- 38419649711: 1/1 success
- 38419439742: 2/2 success
- 41515392296: auto-anchor FAILURE, validation SKIPPED.
Previous 34-case digest 5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34 and serial 2.9656s / parallel 2.6209s (1.1315x regression-phase) are historical claims, not independently recomputed this run. Whole-CI speedup and official backtest speedup NOT VERIFIED.

## Railway production
Project d1c1a050-b7d6-41ce-b300-13c20f82a20a; environment 83d5840b-270e-4d3f-a941-a37fd4a55ff7.
- PIT rebuild latest SUCCESS deploy 8b354fc1-cfb2-4ef0-863e-67f7f5dda2b5 (2026-10-10).
- KRX historical worker latest SUCCESS deploy 16c93d7c-7cd0-4d84-a327-298d2805376c (2026-10-12).
- Real readonly latest SUCCESS deploy a77fb922-b679-4d88-92c4-03054ec579cd (2026-10-29), runtime replica health NOT VERIFIED this run.
- Runtime latest SUCCESS deploy eaaa9f67-b9f2-41d2-832c-7d6fad9b9b00 (2026-10-05).
- db-query-readonly latest deployment NULL.
- 2026-11-09 12:20–14:20 KST window: PIT/KRX/real-readonly/db deploy logs 0 returned; runtime deploy logs returned 51, mostly ETF/index display and proxy readings, not official M20 evidence. Empty logs are not proof of inactivity.
- These service descriptions reported staged=null and zero stagedChanges. No configuration writes or deploys made. Actual ORDERING variable value NOT VERIFIED.

## Independent gates
- OpenDART original filing semantics, public available-at/PIT and 2021/2022 initial 3-month consolidated operating profit correction lineage: NOT VERIFIED. Historical 15 SGML candidate row matches alone do not pass.
- Historical corporate/security mapping: NOT VERIFIED.
- KRX 2017–2022 private weekday pair storage 1565/1565 integrity: historical PASS limited to storage/hash; official session calendar, status, corporate actions, executable fills: NOT VERIFIED.
- Chronology Anchor: FAIL (Action 41515392296).
- Costs, tax, NetEV, PF, CAGR, MDD, ES95/99, concentration, temporal robustness: NOT VERIFIED. M20 PIT/economic RUN: NO-GO.
- Optimization: offline synthetic CI PASS on inspected jobs only. Production/offline full wall-time speedup NOT VERIFIED.

## Non-negotiable controls and next safe work
Keep Frozen H5; M20 horizon20/purge20, WF504/126/126, PIT, labels, Purged/CPCV, independent holdout, Champion/Top3/NO_TRADE and fixed cost/tax/risk/promotion rules. H5 failed/consumed holdout cannot be reused. ORDERING=false policy; live variable not independently verified. Only offline synthetic safety tests; fail-closed cache requires independently approved original data/code/policy/runtime/evidence SHA-256; parallelize only independent read-only postprocessing, never dependent retraining/capital transitions. No live orders, money, auth changes, promotion, deployment, auto-merge, or PR merges. Next: independently anchor original-filing available-at and 2021/2022 lineages, reconcile KRX official calendar/tradability, repair chronology anchor through authorized owner workflow (do not bypass blocked workflow edits), then independently verify source SHA and frozen gates before any M20 run. Avoid touching other teams' code.
