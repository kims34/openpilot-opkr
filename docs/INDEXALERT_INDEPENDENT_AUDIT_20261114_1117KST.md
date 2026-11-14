# IndexAlert independent read-only audit — 2026-11-14 11:17 KST

Scope: profitability integration gate and separately isolated offline execution optimisation. No production/strategy modifications or economic experiments.

## Verified GitHub references (read-only)
- research HEAD `df474df348f22aa38b1dedaa59fcff66e548b406`
- development HEAD `1e6367d2863a86c3470da13d81a955d277eba485`
- audit branch before this report `bef44d0ab228a5d8dd0ec55cac9bcde12ba5a970`
- PRs all draft/open/unmerged: #412 `bf3d9514a87c53b1775e22ec9ba7711f6cecc49f`; #413 `f003ef6247e16fcc71bd3b1b20cd4904c4d984c0`; #414 `18c5418d9684d1717df58261ea27f28e514385b2`; #418 `2f98401cc50a6c6a25808a98516efd5bf0c944ee`; #420 `fab3cbbd63a951a4e081f9e7f08c1391ca308581`; #422 `c14857620973531013799e44625d43080904fd5f`; #423 `0e38004363cac9fc4475556b3a1c445de9af407f`.
- PR #414 integration gate blob Git SHA-1 `984c933651f39f1ee9e26a1d7ac3893aaa5335be` (NOT a SHA-256).
- Actions 38381997417, 38382214223, 38419111311, 38419439742, 38419649711 all completed success; 38486028854 completed failure, job `immutable-archived-case-parallel-regressions`, failing step `Enforce original CI regression-source blob identities before any test`. Job outcomes are NOT independent 34-case SHA-256 reproduction.
- Frozen 34-case expected SHA-256 `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34`: current independent recomputation NOT VERIFIED.
- Offline single-runner serial 2.9656s vs concurrent 2.6209s (1.1315x regression-phase only); full CI/official backtest speedup NOT VERIFIED.

## Railway production
Project `d1c1a050-b7d6-41ce-b300-13c20f82a20a`, environment `83d5840b-270e-4d3f-a941-a37fd4a55ff7`.
- PIT rebuild and runtime each SUCCESS with running 1/1; KRX historical worker and Kiwoom real-readonly-run each SUCCESS but running 0/1; backend, push, db-query-readonly offline. A successful deployment is not proof of currently running worker.
- Pending staged patch `e113dacb-6705-4416-9997-dc694539d382` since 2026-10-29 remains; no deploy/apply.
- 2026-11-14 01:20–02:20 UTC requested deploy-log window: PIT 0 entries, KRX 0, runtime 201 returned (query cap 200; do not infer exhaustive total). Runtime 02:16:42 UTC: Investing USD/KRW HTTPError and Yahoo fallback. This is operational source fallback, NOT PIT/market profitability evidence.

## Evidence gates
- Official original-filing public available-at/PIT, 2021/2022 first three months consolidated operating profit period/correction lineage, historical issuer/security mapping: NOT VERIFIED / FAIL-CLOSED.
- KRX 2017–2022 stored weekday raw pairs 1565/1565: historical storage-integrity PASS per 2026-10-14 evidence, not independently rehashed this run. Official trading calendar/status, corporate actions, fills, execution costs/taxes: NOT VERIFIED / FAIL-CLOSED. 90-day classification and 12003 zero-activity records remain excluded.
- NetEV/PF/CAGR/MDD/ES95/99/concentration/temporal robustness net of costs/taxes: NOT VERIFIED, no approved M20 run.
- OpenDART original/correction SGML 15 adjacent-signature candidates: software evidence only; official semantic period/available-at approval NOT VERIFIED.
- PR #418 integration CI: FAIL; offline historic Actions PASS but cannot promote cache/parallel optimisation or claim whole-system acceleration.
- Frozen H5, M20 horizon20/purge20, WF504/126/126, Purged/CPCV/independent holdout, Champion/Top3/NO_TRADE, costs/taxes and promotion rules unchanged. H5 consumed holdout cannot be reused. ORDERING=false. M20 NO-GO.

## Next permitted work
1. Independently inspect original filing timestamp and consolidated quarterly operating-income period/correction chain from official immutable originals, with SHA-256 and approval provenance; do not substitute corrected later values.
2. Independently reconcile official KRX session/status/corporate-action/point-in-time mappings and fill feasibility; preserve exclusion rules.
3. Resolve archived blob mismatch in the owning isolated PR and independently reproduce immutable 34-case SHA-256 with safe offline synthetic tests only; no workflow edits or concurrent owner-code changes.
4. Only after source PIT approval consider pre-approved independent cost/tax risk-adjusted economic gate; no new M20 economics now.

No merge, deploy, trade, credential/account permission change, Champion promotion, or forbidden workflow edit attempted.
