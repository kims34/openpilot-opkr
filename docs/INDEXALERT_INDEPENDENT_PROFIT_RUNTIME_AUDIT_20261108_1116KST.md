# IndexAlert independent profitability and runtime audit — 2026-11-08 11:16 KST

Read-only evidence snapshot. This is NOT authorization for market backtests, deployment, merge, trading, or Champion promotion.

## GitHub PR HEADs (direct connector reads)
- #412 OpenDART: bf3d9514a87c53b1775e22ec9ba7711f6cecc49f
- #413 offline optimization: f003ef6247e16fcc71bd3b1b20cd4904c4d984c0
- #414 integration gate: 18c5418d9684d1717df58261ea27f28e514385b2
- #418 one-runner: 2f98401cc50a6c6a25808a98516efd5bf0c944ee
- KRX #420: fab3cbbd63a951a4e081f9e7f08c1391ca308581
- KRX #422: c14857620973531013799e44625d43080904fd5f
- KRX #423: 0e38004363cac9fc4475556b3a1c445de9af407f
All seven OPEN, draft. Research index-alert-research-v1 and development index-alert-position-regen-fix-v1 current HEAD were not independently resolved in this pass; earlier observed df474df348f22aa38b1dedaa59fcff66e548b406 and 1e6367d2863a86c3470da13d81a955d277eba485 are historical, NOT current attestations.
#414 integration gate file blob SHA: 984c933651f39f1ee9e26a1d7ac3893aaa5335be, fetched at #414 HEAD.

## GitHub Actions (direct job reads)
- 38381997417: 6/6 SUCCESS
- 38382214223: 6/6 SUCCESS
- 38419111311: 6/6 SUCCESS
- 38419649711: 1/1 SUCCESS
- 38419439742: 2/2 SUCCESS
- Chronology Anchor 41515392296: auto-anchor FAILURE, validation SKIPPED (FAIL).
- Historic fixed 34-case digest 5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34, 13 adversarial mocks, 28 synthetic cases, and serial 2.9656s vs concurrent 2.6209s were NOT recomputed here. No claim of real end-to-end speedup.

## Railway production (direct environment health and logs)
Project d1c1a050-b7d6-41ce-b300-13c20f82a20a; environment 83d5840b-270e-4d3f-a941-a37fd4a55ff7.
- PIT rebuild: deployment SUCCESS, running replicas 1/1; new deploy logs since 2026-11-08 00:00Z: 0.
- KRX historical worker: SUCCESS, replica 0 running/0 crashed of 1 (likely one-shot/idle; not proof of live processing); new logs: 0.
- Kiwoom real read-only: deployment SUCCESS but running replicas 0, crashed 1 of 1; inconsistent UI 'online'; actual healthy service FAIL/needs diagnosis. New logs: 0.
- Runtime: SUCCESS, running 1/1; deploy logs show Investing USD/KRW HTTPError and Yahoo fallback at 2026-11-08 02:16Z. This is a fallback observation, NOT source PIT approval.
- indexalert-backend offline (4 warnings), indexalert-push offline (1 warning), db-query-readonly offline (1 critical).
- Staged patch e113dacb-6705-4416-9997-dc694539d382 has zero listed changes; no deploy or patch acceptance authorized.

## Evidence gate
- Historical 2017–2022 1565/1565 private weekday original pairs: archival integrity PASS **historical evidence only**; official calendar, market states, corporate actions, actual fillability NOT VERIFIED.
- OpenDART original/modified SGML 15 candidate rows and adjacency signature: offline candidate check PASS **historical evidence only**; original-filing semantics, precise public available-at/PIT, 2021/2022 first three-month consolidated operating profit period/correction lineage NOT VERIFIED.
- Historical entity/security mapping, source-time model approval, executable prices, tax/fees, cost-adjusted NetEV/PF/CAGR/MDD/ES95/99, return concentration and temporal robustness: NOT VERIFIED.
- Chronology Anchor: FAIL; source PIT admission NOT VERIFIED; M20 profitability RUN remains NO-GO.
- Optimization: offline synthetic parity jobs PASS; full CI and official market backtest acceleration NOT VERIFIED.
- Prior H5 consumed/failed holdout and dynamic results must not be retuned or reused as independent.
- Frozen H5, M20 horizon20/purge20, WF504/126/126, PIT/label/purged/CPCV/holdout/champion/Top3/NO_TRADE, fees/taxes/risk/promotion unchanged. ORDERING=false. Fail-closed cache only on exact approved evidence SHA-256 across source/data/code/policy/runtime. Only read-only independent postprocessing may parallelize; dependent retraining and capital transitions remain serial.

## Next safe steps
1. Independently resolve exact research/development branch HEADs and capture PR #413/#418 test artifacts with SHA and phase-vs-whole-CI timing.
2. Diagnose Chronology Anchor failure without workflow changes, obtain official first-filed publication-time and correction lineage evidence before any M20 gate reopening.
3. Obtain official KRX trading-status/corporate-action/calendar provenance and independent fill/cost/tax evidence.
4. Investigate Railway read-only crashed replica and offline services in read-only mode; do not treat SUCCESS deployment as healthy runtime.
5. No production deploy, workflow changes, merge, real orders, funding, credential changes or Champion promotion.
