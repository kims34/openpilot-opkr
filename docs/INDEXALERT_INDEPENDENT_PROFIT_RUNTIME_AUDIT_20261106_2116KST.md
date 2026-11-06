# IndexAlert independent profit/runtime audit — 2026-11-06 21:16 KST

Scope: read-only GitHub/Railway evidence and this isolated documentation write only. No workflows, trading, deployment, code, model, or frozen policy changed.

## Source refs
Research PR #414 base SHA `3b8b7830612a6284d7c7a60628cb527cb741627a` (branch latest HEAD independently NOT VERIFIED); development PR #420 base SHA `1e6367d2863a86c3470da13d81a955d277eba485` (branch latest HEAD independently NOT VERIFIED).
PR #412 `bf3d9514a87c53b1775e22ec9ba7711f6cecc49f`; #413 `f003ef6247e16fcc71bd3b1b20cd4904c4d984c0`; #414 `18c5418d9684d1717df58261ea27f28e514385b2`; #418 `2f98401cc50a6c6a25808a98516efd5bf0c944ee`; KRX #420 `fab3cbbd63a951a4e081f9e7f08c1391ca308581`, #422 `c14857620973531013799e44625d43080904fd5f`, #423 `0e38004363cac9fc4475556b3a1c445de9af407f`. All OPEN/DRAFT/unmerged at read time. #414 gate document blob SHA `984c933651f39f1ee9e26a1d7ac3893aaa5335be`.

## Original CI verification
GitHub Actions 38381997417 6/6 success, 38382214223 6/6 success, 38419111311 6/6 success; 38419649711 1/1 success; OpenDART 38419439742 2/2 success. Chronology anchor 41515392296 auto-anchor FAIL, validation SKIPPED. Historical 34-case SHA `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34`, 13 adversarial mocks and 28 synthetic checks, serial 2.9656s vs parallel 2.6209s = 1.1315x regression-phase only are previous reported evidence, not independently rehashed in this run. Full CI and real backtest speedup NOT VERIFIED.

## Railway production evidence
Project `d1c1a050-b7d6-41ce-b300-13c20f82a20a`. PIT rebuild service `225f2279-d728-4e1a-a3f3-2447ff0f9dc1` status SUCCESS, logs at 20:01,20:16,20:31,20:46,21:01,21:16 KST (UTC 11:01 through 12:16) each `KRXProspectiveOpenAPISourceError`, `COMMON_OHLC_NONPOSITIVE`, 27/803 common-stock rows invalid and 27 zero-volume/value rows; `fresh_alpha_observation_admitted=false`, `live_order_authorized=false`, `ordering=DISABLED`. Source data quality FAIL; fail-closed admission/order safety PASS. KRX historical worker service `003812ee-102b-42b6-bda4-36925885b428` SUCCESS deployment with no logs in queried 20:00–21:16 KST interval; its deployment source SHA `1e6367d2863a86c3470da13d81a955d277eba485`. Deployment SUCCESS does not prove live replica or market data correctness.

## Gate decisions
Official first-filing original meaning, precise public available-at/PIT, 2021/2022 first 3-month consolidated operating profit period/correction lineage, historical entity-security mapping, KRX official trading calendar/status/corporate actions/executability, actual taxes/costs and NetEV/PF/CAGR/MDD/ES95/99, concentration and temporal robustness: NOT VERIFIED. Historical private 1565/1565 weekday pairs storage-integrity PASS is prior evidence only; official tradability NOT VERIFIED. H5 failed/consumed holdout cannot be recycled. M20 horizon20/purge20, WF504/126/126, frozen H5, CPCV, independent Holdout, Champion/Top3/NO_TRADE unchanged. M20 PIT/economic run NO-GO; no new market performance tests. Cache requires approved original/data/code/frozen policy/runtime/evidence SHA-256 equality and fail-closed; parallelize read-only postprocessing only; no dependent retraining/capital transitions.

## Next permitted steps
1. Independent original-filing public timestamp and 2021/2022 corrected-lineage attestation; 2. Official KRX status/zero-activity/27 invalid OHLC reconciliation without promoting observations; 3. Chronology anchor failure root-cause read-only review; 4. Offline synthetic parity and complete CI wall-time verification on isolated runner only after approved provenance. No merge/deploy/ORDERING enable/trading/Champion promotion.
