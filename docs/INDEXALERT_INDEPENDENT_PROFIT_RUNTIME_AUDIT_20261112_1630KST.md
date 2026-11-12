# IndexAlert independent gate audit — 2026-11-12 16:30 KST

Scope: read-only GitHub/Railway source verification, no strategy/model/performance run, no deployment or merge. This document is not approval.

## Source identities
- PR #412 OPEN draft head bf3d9514a87c53b1775e22ec9ba7711f6cecc49f
- PR #413 OPEN draft head f003ef6247e16fcc71bd3b1b20cd4904c4d984c0
- PR #414 OPEN draft head 18c5418d9684d1717df58261ea27f28e514385b2
- PR #418 OPEN draft head 2f98401cc50a6c6a25808a98516efd5bf0c944ee
- KRX PR #420 OPEN draft fab3cbbd63a951a4e081f9e7f08c1391ca308581; #422 OPEN draft c14857620973531013799e44625d43080904fd5f; #423 OPEN draft 0e38004363cac9fc4475556b3a1c445de9af407f.
- PR #414 gate file read on PR branch; source explicitly keeps M20 performance_run_authorized=false, H5/0-N NO-GO, source PIT fail-closed. Current research and development branch HEAD SHA independently NOT VERIFIED this cycle; earlier reported research df474df348f22aa38b1dedaa59fcff66e548b406 and development 1e6367d2863a86c3470da13d81a955d277eba485 are historical, not current confirmations.

## Actions
Direct read-only job fetch on 2026-11-12: 38381997417 6/6 SUCCESS; 38382214223 6/6 SUCCESS; 38419111311 6/6 SUCCESS; 38419649711 1/1 SUCCESS; 38419439742 2/2 SUCCESS. This proves CI job outcomes, not actual original-filing PIT, full SHA parity recomputation, or production backtest speed. Prior fixed 34-case SHA 5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34 is a reference only; independent recomputation NOT VERIFIED. Prior single runner 2.9656s vs concurrent 2.6209s implies 1.1315x regression-phase ratio only; overall CI and official backtest acceleration NOT VERIFIED.

## Railway production live evidence
Project d1c1a050-b7d6-41ce-b300-13c20f82a20a; production environment 83d5840b-270e-4d3f-a941-a37fd4a55ff7.
- PIT rebuild SUCCESS deployment 8b354fc1-cfb2-4ef0-863e-67f7f5dda2b5; replica 1/1 running.
- Runtime SUCCESS deployment eaaa9f67-b9f2-41d2-832c-7d6fad9b9b00; replica 1/1 running.
- KRX historical worker SUCCESS deployment 16c93d7c-7cd0-4d84-a327-298d2805376c; replica 0/1 running, 0 crashed: live execution NOT VERIFIED, not a claim of a running worker.
- Kiwoom real-readonly SUCCESS deployment a77fb922-b679-4d88-92c4-03054ec579cd; replica 0/1 running, 1/1 crashed: runtime FAIL despite online service display.
- Backend, Push, db-query-readonly offline; db-query-readonly critical notification 1. Empty staged environment patch e113dacb-6705-4416-9997-dc694539d382 left untouched.
- Deploy logs in 2026-11-12 06:20–07:31 UTC: PIT, KRX, Kiwoom 0 entries; Runtime displays ETF_CLOSED_PROXY futures-linked estimates and Naver KOSPI quote. Neither constitutes approved KRX historical trading evidence. Production ORDERING flag independently NOT VERIFIED; preserve ORDERING=false policy.

## Independent admission decisions
- Prior 2017–2022 1565/1565 private weekday original-pair storage SHA: PASS within historical storage-only evidence; official calendar, session states, corporate actions, fills, taxes: NOT VERIFIED.
- OpenDART SGML original/correction candidate-row shape and 15 nearby numeric signatures: historical limited evidence; original consolidated first 3-month operating profit for 2021/2022, exact public available-at, correction lineage and historic corp/security mapping: NOT VERIFIED.
- H5 archived robustness: NO-GO, consumed/failed holdout not reusable. M20 horizon20/purge20 WF504/126/126: NO-GO; economic run NOT AUTHORIZED.
- NetEV/PF/CAGR/MDD/ES95/99, concentration, temporal robustness, after-tax risk-adjusted annual net return: NOT VERIFIED; no market performance experiment performed.
- Offline software CI PASS in tested scope; cache requires independently approved original/data/code/Frozen/runtime/approval SHA-256 exact match fail-closed. Only independent read-only postprocessing eligible for parallelization; no dependent retraining or capital transitions.
- No change to Frozen H5, M20, Top3/NO_TRADE, risk/cost/tax/approval thresholds; no orders, transfers, credential changes, Champion promotion, merge, workflow change, or production deployment.

## Next gate
Independent original filing / precise available-at and CFS 3-month lineage from DART owner; official KRX session/availability/corporate-action and fill-cost evidence from KRX owner; then independent SHA-bound source gate review. No M20 profitability run before both pass. Investigate crashed Kiwoom read-only replica separately without changing account permissions or deployment.
