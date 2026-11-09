# IndexAlert independent profitability / offline optimization audit — 2026-11-09 10:20 KST

Read-only evidence snapshot. No trading, deployment, merge, workflow edit, model search, official market backtest, or M20 economic run.

## GitHub current PR heads (verified via authenticated PR reads)
- #412 OPEN DRAFT unmerged: bf3d9514a87c53b1775e22ec9ba7711f6cecc49f
- #413 OPEN DRAFT unmerged: f003ef6247e16fcc71bd3b1b20cd4904c4d984c0
- #414 OPEN DRAFT unmerged: 18c5418d9684d1717df58261ea27f28e514385b2; integration gate blob 984c933651f39f1ee9e26a1d7ac3893aaa5335be
- #418 OPEN DRAFT unmerged: 2f98401cc50a6c6a25808a98516efd5bf0c944ee
- KRX #420 OPEN DRAFT: fab3cbbd63a951a4e081f9e7f08c1391ca308581
- KRX #422 OPEN DRAFT: c14857620973531013799e44625d43080904fd5f
- KRX #423 OPEN DRAFT: 0e38004363cac9fc4475556b3a1c445de9af407f
- Research branch index-alert-research-v1 and development index-alert-position-regen-fix-v1: latest branch tips NOT VERIFIED; README.md fetch on each ref returned 404 (absence of README is not proof branch is absent). Historical reported tips df474df348f22aa38b1dedaa59fcff66e548b406 and 1e6367d2863a86c3470da13d81a955d277eba485 are NOT current independently verified.

## GitHub Actions independently checked job conclusions
- 38381997417 6/6 success; 38382214223 6/6 success; 38419111311 6/6 success.
- 38419649711 1/1 success; 38419439742 2/2 success.
- 41515392296 auto-anchor FAILURE, validation SKIPPED: chronology anchor blocking.
- Historical fixed 34-case SHA-256 5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34 and serial 2.9656s vs concurrent 2.6209s (1.1315x regression-phase only) NOT independently recomputed this run. Entire CI/official backtest acceleration NOT VERIFIED.

## Railway IndexAlert production
Project d1c1a050-b7d6-41ce-b300-13c20f82a20a; environment 83d5840b-270e-4d3f-a941-a37fd4a55ff7.
- PIT rebuild running 1/1, runtime running 1/1.
- Kiwoom real readonly service shows online/SUCCESS deployment a77fb922-b679-4d88-92c4-03054ec579cd, but replica running 0/crashed 1: runtime health FAIL.
- db-query-readonly offline with one critical; backend and push offline with warnings.
- KRX historical worker shows SUCCESS deployment 16c93d7c-7cd0-4d84-a327-298d2805376c, replica 0 running/0 crashed (scheduled/idle state does not prove tradeability).
- Environment pending patch e113dacb-6705-4416-9997-dc694539d382 staged with empty changes; untouched.
- PIT/KRX/real-readonly deploy log queries 2026-11-09 00:00–01:25 UTC returned zero entries each. Zero logs do not prove service health.
- Actual ORDERING environment variable value NOT VERIFIED; policy ORDERING=false unchanged.

## Gate assessment
- Historical KRX 1565/1565 weekday original pairs storage integrity: PASS per prior verified record, NOT rehashed this run; official exchange calendar/status, actions, executable fills and costs: NOT VERIFIED.
- OpenDART original/amended SGML 15 candidate rows signature match: historical evidence only; original-filing semantics, public available-at and 2021/2022 initial 3-month consolidated operating profit correction lineage: NOT VERIFIED.
- Historical entity/security mappings, PIT labels, purge/CPCV/independent holdout, net costs/tax, NetEV/PF/CAGR/MDD/ES95/99, concentration and time robustness: NOT VERIFIED.
- Chronology anchor: FAIL. M20 PIT and profitability: NO-GO; H5 spent holdout never reusable.
- Offline CI job success: PASS for listed job conclusions only; no proof of economic profitability or whole-run speedup.

## Next safe steps
1. Obtain independent official first-publication timestamp, period semantics and amendment lineage; separately validate official KRX trading state, historical mapping and corporate actions with SHA-bound evidence.
2. Diagnose failed chronology anchor and crashed readonly replica via read-only logs; avoid modifying another owner's code or workflows.
3. In isolated offline-only area, validate cache key fail-closed on approved source/data/code/Frozen/runtime/approval SHA-256; permit only independent read-only postprocessing parallelism. Do not parallelize dependent training or capital transitions.
4. Keep Frozen H5, M20 horizon20/purge20, WF504/126/126, holdout, Top3/Champion/NO_TRADE and cost/risk thresholds fixed. No PR merges, deployment, orders, capital movements, credential changes or Champion promotion.
