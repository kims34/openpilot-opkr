# IndexAlert independent profitability/runtime audit — 2026-11-10 18:17 KST

Scope: read-only independent gate, no market backtest, no deployment, no merges, no workflow edits, no strategy modification. Prior evidence is not automatically re-approved.

## GitHub observed
Research branch index-alert-research-v1 base SHA from live compare: df474df348f22aa38b1dedaa59fcff66e548b406. Development branch index-alert-position-regen-fix-v1 compare status DIVERGED: development ahead 1148, behind 281. Development exact latest SHA not independently resolved by compare output (historical 1e6367d2863a86c3470da13d81a955d277eba485, not re-certified as current).
PRs (all OPEN Draft, unmerged), exact head SHA:
- #412 bf3d9514a87c53b1775e22ec9ba7711f6cecc49f
- #413 f003ef6247e16fcc71bd3b1b20cd4904c4d984c0
- #414 18c5418d9684d1717df58261ea27f28e514385b2
- #418 2f98401cc50a6c6a25808a98516efd5bf0c944ee
- #420 fab3cbbd63a951a4e081f9e7f08c1391ca308581
- #422 c14857620973531013799e44625d43080904fd5f
- #423 0e38004363cac9fc4475556b3a1c445de9af407f
PR #414 gate document docs/INDEXALERT_PROFITABILITY_INTEGRATION_GATE_2026-10-13.md blob SHA 984c933651f39f1ee9e26a1d7ac3893aaa5335be (fetched on PR branch).

Actions checked directly: 38381997417 6/6 SUCCESS, 38382214223 6/6 SUCCESS, 38419111311 6/6 SUCCESS; 38419649711 1/1 SUCCESS; 38419439742 2/2 SUCCESS. Fixed 34-case SHA 5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34 is historical reported evidence, NOT independently recalculated today. 13 adversarial mocks / 28 synthetic tests are historical claims; job completion alone does not certify their payloads. Serial 2.9656s / concurrent 2.6209s = 1.1315x regression phase historical only; end-to-end CI and real official backtest acceleration NOT VERIFIED.

## Railway production (read-only)
Project d1c1a050-b7d6-41ce-b300-13c20f82a20a, environment 83d5840b-270e-4d3f-a941-a37fd4a55ff7.
- PIT rebuild deployment 8b354fc1-cfb2-4ef0-863e-67f7f5dda2b5 SUCCESS, replica 1/1 running.
- Runtime eaaa9f67-b9f2-41d2-832c-7d6fad9b9b00 SUCCESS, replica 1/1 running.
- KRX worker 16c93d7c-7cd0-4d84-a327-298d2805376c SUCCESS, 0 running / 0 crashed / total 1; runtime execution NOT VERIFIED.
- Kiwoom real read-only a77fb922-b679-4d88-92c4-03054ec579cd deployment SUCCESS, 0 running / 1 crashed / total 1: runtime FAIL despite service UI online.
- backend, push, db-query-readonly offline; db-query-readonly 1 critical issue.
- PIT/KRX/Kiwoom service deploy logs since 2026-11-10 00:00 UTC: 0 entries each. Absence of logs is not health evidence.
- Staged pending patch e113dacb-6705-4416-9997-dc694539d382 has zero changes; DO NOT APPLY.

## Gate assessment
PASS (limited): historic 1565/1565 weekday raw KRX pairs storage integrity; Actions job completion above.
FAIL: Kiwoom real-readonly running replica health (0 running, 1 crashed); historical H5/consumed holdout disqualified from independent reuse.
NOT VERIFIED: official first-filed original-filing public available-at/PIT, 2021/2022 first three-month consolidated operating profit period/correction lineage, historical entity-security mapping, official KRX calendar/trading state/corporate actions/fill feasibility, cost/tax modelling, independent after-cost/tax annual risk-adjusted NetEV/PF/CAGR/MDD/ES95/99/concentration/time robustness, fixed-test SHA independent replay, full CI and real backtest speed, live ORDERING setting.
OpenDART original/correction SGML 15 candidate rows with numeric adjacency from Action 38419439742 do NOT prove semantic PIT. Historical 90-session classification and 12003 zero-activity quarantine remain blocked, not trade approval; 27/803 suspicious OHLC unresolved.

## Frozen guardrails / next safe steps
M20 NO-GO: horizon20/purge20, WF504/126/126, PIT/label/Purged/CPCV/independent Holdout/Champion/Top3/NO_TRADE, cost/tax/NetEV/execution/risk/promotion policy unchanged. H5 consumed holdout cannot be recycled. ORDERING=false required, actual deployment value not read. No M20 economic run, market return experiments, parameter search, real orders, money transfer, credential changes, champion promotion, deployment or merge. Only synthetic offline policy checks and independent provenance verification allowed. Cache fail-closed on independent approved source/data/code/Frozen policy/runtime/approval SHA-256; parallelize only independent read-only postprocessing, never dependent retraining or capital transition.
Next: obtain original-filing/publication timestamp and corrected-lineage proof, authoritative KRX session/tradability proof and independently signed SHA manifests; review Kiwoom crashed replica via logs without restarting; then independently audit official after-tax returns only after explicit source PIT approval. Do not edit other workstreams.
