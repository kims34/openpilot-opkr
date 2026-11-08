# IndexAlert independent profitability / runtime audit — 2026-11-09 05:18 KST

Read-only evidence inspection; no market backtest, no model selection, no operational change. This document is independent of PR #413/#414/#418 and does not approve them.

## GitHub exact PR heads (fresh connector reads)
- #412 OPEN Draft bf3d9514a87c53b1775e22ec9ba7711f6cecc49f
- #413 OPEN Draft f003ef6247e16fcc71bd3b1b20cd4904c4d984c0
- #414 OPEN Draft 18c5418d9684d1717df58261ea27f28e514385b2
- #418 OPEN Draft 2f98401cc50a6c6a25808a98516efd5bf0c944ee
- #420 OPEN Draft fab3cbbd63a951a4e081f9e7f08c1391ca308581
- #422 OPEN Draft c14857620973531013799e44625d43080904fd5f
- #423 OPEN Draft 0e38004363cac9fc4475556b3a1c445de9af407f
- #414 integration gate document blob SHA 984c933651f39f1ee9e26a1d7ac3893aaa5335be.
- Research/development latest branch HEAD not independently resolved in this run. Prior observed research df474df348f22aa38b1dedaa59fcff66e548b406; development 1e6367d2863a86c3470da13d81a955d277eba485. These are historical anchors, not fresh HEAD assertions.

## CI evidence (fresh jobs reads)
- Actions 38381997417, 38382214223, 38419111311: each six jobs completed SUCCESS.
- Action 38419649711: one job SUCCESS.
- Action 38419439742: two jobs SUCCESS.
- Chronology Anchor 41515392296: auto-anchor FAILURE; validation SKIPPED. **FAIL** for chronology acceptance.
- Prior immutable 34-case test SHA 5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34, synthetic 28, adversarial 13, and 2.9656s/2.6209s ratio 1.1315x are historical evidence, not recalculated in this run. Whole-CI and actual market backtest acceleration NOT VERIFIED.

## Railway production (fresh describe-environment / environment-status / deploy log reads)
Project d1c1a050-b7d6-41ce-b300-13c20f82a20a; environment 83d5840b-270e-4d3f-a941-a37fd4a55ff7.
- PIT rebuild and runtime: each running replica 1/1, latest deployment SUCCESS.
- Real-account read-only: UI online but replica running 0 / crashed 1 / total 1. **FAIL** runtime replica health; deployment SUCCESS is not runtime health.
- db-query-readonly offline, critical 1. Backend offline (4 warnings), Push offline (1 warning).
- KRX historical worker latest deployment SUCCESS, current replicas running 0/total 1; cron/idle semantics need separate validation.
- Environment inventory staged=null, but environment-status pendingWork includes empty staged patch e113dacb-6705-4416-9997-dc694539d382, changes=[]; **NOT VERIFIED** consistency, do not apply.
- PIT, KRX worker, real-readonly service deploy logs: zero entries in 2026-11-08 18:00Z–20:30Z query. Absence of log entries is not proof of successful PIT.
- No deployment, variable, authorization or account changes performed.

## Independent gate decisions
- Official original-filing/public available-at PIT, 2021/2022 initial 3-month consolidated operating-profit period/correction lineage: NOT VERIFIED.
- Historical issuer-security mapping, KRX official trading sessions/status/corporate actions, executable fill/cost/tax: NOT VERIFIED. Historical 1565/1565 weekday raw pairs are storage-integrity PASS only, not tradability PASS. Quarantine zero-activity 12003 and suspicious 2026-09-28 27 cases.
- Annual post-cost/post-tax risk-adjusted NetEV, PF, CAGR, MDD, ES95/99, concentration and temporal robustness: NOT VERIFIED (no authorized run).
- M20 PIT/profitability: NO-GO. H5 consumed holdout/Dynamic cannot be retroactively optimized or reused as independent holdout. ORDERING=false; no trading.
- Frozen H5; M20 horizon20/purge20, WF504/126/126, PIT/Purged/CPCV/independent Holdout/Champion/Top3/NO_TRADE; cost/tax/fill/risk/promotion policy unchanged.
- Optimization: only offline synthetic tests; cache must fail closed on independently approved source/data/code/Frozen/runtime/approval SHA-256 mismatch; only independent read-only postprocessing parallel; dependent retraining/capital transitions serial.

## Next safe steps
1. Independent official original-filing and precise public-available-at evidence plus 2021/2022 lineage/issuer mapping; preserve SHA and earliest publication timestamp.
2. Official KRX session/trading-state/corporate-action and executable cost/tax proofs; classify all source gaps.
3. Repair chronology anchor evidence upstream without bypassing blocked workflow permissions; request separate explicit authorization for any protected workflow edits.
4. Investigate read-only replica crash and db-query outage in a separate authorized operations track, read-only until approved.
5. Revalidate optimization SHA parity and end-to-end timing only using permitted offline synthetic fixtures; no M20 economics.
