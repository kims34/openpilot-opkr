# IndexAlert independent profitability and isolated runtime audit — 2026-11-10 13:24 KST

Scope: independent read-only evidence review. No official return calculation, M20 execution, trading, merge, deployment, workflow changes or Champion promotion.

## Exact GitHub refs
- Research `index-alert-research-v1` HEAD: `df474df348f22aa38b1dedaa59fcff66e548b406` (compare base commit).
- Development `index-alert-position-regen-fix-v1`: prior deployment commit `1e6367d2863a86c3470da13d81a955d277eba485`; exact latest HEAD not independently extracted by this compare response. Diverged versus research: development ahead 1148, behind 281.
- PR #412 `bf3d9514a87c53b1775e22ec9ba7711f6cecc49f`; #413 `f003ef6247e16fcc71bd3b1b20cd4904c4d984c0`; #414 `18c5418d9684d1717df58261ea27f28e514385b2`; #418 `2f98401cc50a6c6a25808a98516efd5bf0c944ee`.
- KRX #420 `fab3cbbd63a951a4e081f9e7f08c1391ca308581`; #422 `c14857620973531013799e44625d43080904fd5f`; #423 `0e38004363cac9fc4475556b3a1c445de9af407f`. All seven OPEN, Draft, unmerged as queried.
- Integration gate path `docs/INDEXALERT_PROFITABILITY_INTEGRATION_GATE_2026-10-13.md`: direct research-branch fetch failed this run; PR #414 body/diff accessible, no independent blob SHA approval.

## Actions and isolated optimization
- Actions 38381997417, 38382214223, 38419111311: 6/6 jobs SUCCESS each; 38419649711: 1/1 SUCCESS; 38419439742: 2/2 SUCCESS (jobs endpoint checked this run).
- Original 34-case SHA `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34`, 13 adversarial mocks and 28 synthetic cases are historical assertions, not independently rehashed this run.
- Prior serial 2.9656 s vs concurrent 2.6209 s = 1.1315x regression-phase only. End-to-end CI and official backtest speed NOT VERIFIED. Cache fail-closed on all independent approved source/data/code/Frozen/runtime/approval SHA-256; parallelize read-only postprocessing only; dependent training and capital transition remain serial.

## Railway production
- Project `d1c1a050-b7d6-41ce-b300-13c20f82a20a`, environment `83d5840b-270e-4d3f-a941-a37fd4a55ff7`.
- PIT rebuild deployment `8b354fc1-cfb2-4ef0-863e-67f7f5dda2b5` SUCCESS, replicas running 1/1; runtime `eaaa9f67-b9f2-41d2-832c-7d6fad9b9b00` SUCCESS, running 1/1.
- KRX worker deployment `16c93d7c-7cd0-4d84-a327-298d2805376c` SUCCESS, replicas running 0/1 (not sufficient for runtime PASS).
- Kiwoom real-readonly `a77fb922-b679-4d88-92c4-03054ec579cd` deployment SUCCESS but running 0/crashed 1/total 1: runtime FAIL despite Online label.
- Backend, push and db-query-readonly offline. Staged patch `e113dacb-6705-4416-9997-dc694539d382` has zero changes; not applied.
- PIT/KRX/Kiwoom deploy logs since 2026-11-10 00:00 UTC each returned 0 records. This is NOT VERIFIED, not a success attestation. Existing OHLC 27/803 unresolved.

## Independent gates
- OpenDART original filing, exact public available-at/PIT, 2021/2022 first 3-month consolidated operating-profit period and correction lineage: NOT VERIFIED. Historic 15 candidate SGML rows are not semantic/PIT approval.
- Historical entity/security mappings, official KRX calendar/trading status, corporate actions, executable prices, transaction costs/taxes: NOT VERIFIED. Historic 1565/1565 private weekday-pair integrity PASS limited to storage integrity, not official tradability.
- NetEV/PF/CAGR/MDD/ES95/ES99, return concentration and temporal robustness after taxes/costs: NOT VERIFIED. M20 admission NO-GO.
- H5 failed/consumed holdout and Dynamic results must not be reused. Frozen H5, M20 horizon20/purge20, WF504/126/126, PIT/labels/Purged/CPCV/independent Holdout/Champion/Top3/NO_TRADE and cost/risk/promotion gates unchanged. ORDERING=false.
- Next: independently verify original first-filed semantics/available-at and correction lineage, official KRX session/state/corporate-action mapping, evidence-bound executable cost/tax assumptions; then independent approval before any M20 economic test. No automatic merge, deploy, trading, credential changes, or promotion.
