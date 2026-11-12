# IndexAlert independent audit — 2026-11-12 20:22 KST

Read-only evidence review. No production deployment, trade, promotion, workflow edit, PR merge, strategy exploration, M20 economics run or Holdout reuse.

## Immutable references
- Research branch index-alert-research-v1 HEAD **df474df348f22aa38b1dedaa59fcff66e548b406** (compare identical, 0 ahead/behind).
- Development index-alert-position-regen-fix-v1 HEAD **1e6367d2863a86c3470da13d81a955d277eba485** (compare identical).
- Draft open PR HEADs: #412 bf3d9514a87c53b1775e22ec9ba7711f6cecc49f; #413 f003ef6247e16fcc71bd3b1b20cd4904c4d984c0; #414 18c5418d9684d1717df58261ea27f28e514385b2; #418 2f98401cc50a6c6a25808a98516efd5bf0c944ee; KRX #420 fab3cbbd63a951a4e081f9e7f08c1391ca308581, #422 c14857620973531013799e44625d43080904fd5f, #423 0e38004363cac9fc4475556b3a1c445de9af407f.
- #414 gate document blob SHA **984c933651f39f1ee9e26a1d7ac3893aaa5335be**.
- GitHub Actions run IDs 38381997417, 38382214223, 38419111311, 38419649711, 38419439742, 38498552499: respectively 6/6, 6/6, 6/6, 1/1, 2/2, 6/6 successful jobs (read-only API). Historical 34-case SHA **5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34** not independently recomputed here. #418 single-runner 2.9656s serial vs 2.6209s concurrent = 1.1315x regression phase only; whole CI and official backtest acceleration NOT VERIFIED. #413 later parity/performance conflict remains unapproved.

## Production Railway (project d1c1a050-b7d6-41ce-b300-13c20f82a20a, production 83d5840b-270e-4d3f-a941-a37fd4a55ff7)
- 20:22 KST read-only environment status: PIT rebuild 1/1 running, Runtime 1/1 running; KRX historical worker 0/1 running; Kiwoom real read-only 0/1 running, 1/1 crashed (**operational FAIL** despite API top-level online); Backend/Push/db-query-readonly offline, latter critical 1. Empty staged patch changes [] (do not apply).
- 2026-11-12 09:20–11:23 UTC PIT deploy logs **8 repeated errors** (09:30, 09:45, 10:00, 10:15, 10:30, 10:45, 11:00, 11:15): KRXProspectiveOpenAPISourceError / COMMON_OHLC_NONPOSITIVE, 803 common-stock rows, 27 nonpositive OHLC, 27 zero-volume/value, all-zero OHLC 0. **Source admission FAIL**; logs report fresh_alpha_observation_admitted=false, live_order_authorized=false, ordering=DISABLED (**fail-closed PASS for observed executions**). This is continuation of prior issue, not eight distinct independently validated source failures. KRX and Kiwoom deploy logs 0 entries in same interval; Runtime active with KOSPI/USDKRW lookup, Investing HTTP failure and Yahoo fallback. None of these runtime quotes constitute official KRX source PIT.
- Historical 2017–2022 1,565/1,565 weekday private original-pair integrity: **PASS only within previously recorded storage/hash scope**; official session calendar, trade status, corporate actions and execution availability **NOT VERIFIED**; 90 uncertain days and 12,003 zero-activity records blocked.

## Gate adjudication
- OpenDART first original SGML candidate signatures 15 rows: previous read-only Action 38419439742 CI success, **semantic original first-quarter operating-profit amount, correction lineage, exact public available-at NOT VERIFIED**. 2021/2022 consolidated first three-month period, issuer/security historical mapping NOT VERIFIED.
- Cost/tax/tradability, PIT, independent holdout, annual risk-adjusted net profitability and NetEV/PF/CAGR/MDD/ES95/99/concentration/time robustness: **NOT VERIFIED**; H5 archived failure and consumed holdout cannot be reused; M20 NO-GO.
- Frozen H5, M20 horizon20/purge20, WF504/126/126, PIT/labels/Purged/CPCV/independent Holdout/Champion/Top3/NO_TRADE and cost/risk/promotion criteria unchanged. Only isolated synthetic offline safety checks allowed. Cache must fail closed unless all approved original/data/code/Frozen/runtime/approval evidence SHA-256 match; only independent read-only postprocessing parallelizable; dependent retraining/capital transitions serial. No economic experiments before source/PIT signoff.

## Next independent evidence
1. KRX source owner: reconcile 2026-09-28 27 OHLC failures against official original status/corporate-action/market calendar with signed immutable raw and classification lineage; do not treat zero activity as tradeable.
2. OpenDART source owner: prove original filing, public timestamp, period/consolidation, 2021/2022 first-three-month operating-profit lineage and historical issuer mapping with immutable original SHA.
3. Investigate Railway Kiwoom read-only crashed replica and KRX worker 0/1 without restarting, deploying or changing permissions; capture diagnostics only.
4. Optimization owners: resolve #413/#418 implementation SHA and compare full CI wall clock under frozen synthetic test inputs, without touching existing specialist branches.
5. Only after independently approved source/PIT and execution/cost gates, request explicit authorization for any separate M20 economic run. No orders, capital movement, permission changes or Champion promotion without per-action approval.
