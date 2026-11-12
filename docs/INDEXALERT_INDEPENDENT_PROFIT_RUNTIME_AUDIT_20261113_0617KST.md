# IndexAlert independent profitability / runtime audit — 2026-11-13 06:17 KST

Scope: read-only verification of GitHub and Railway, plus this isolated audit document. No economic run, merge, deployment, order, permission change or workflow modification.

## Immutable GitHub refs (freshly read)
- Research `index-alert-research-v1`: `df474df348f22aa38b1dedaa59fcff66e548b406`, compare identical (ahead/behind 0/0).
- Development `index-alert-position-regen-fix-v1`: `1e6367d2863a86c3470da13d81a955d277eba485`, compare identical (0/0).
- Draft OPEN/unmerged PR HEADs: #412 `bf3d9514a87c53b1775e22ec9ba7711f6cecc49f`; #413 `f003ef6247e16fcc71bd3b1b20cd4904c4d984c0`; #414 `18c5418d9684d1717df58261ea27f28e514385b2`; #418 `2f98401cc50a6c6a25808a98516efd5bf0c944ee`; KRX #420 `fab3cbbd63a951a4e081f9e7f08c1391ca308581`, #422 `c14857620973531013799e44625d43080904fd5f`, #423 `0e38004363cac9fc4475556b3a1c445de9af407f`.
- #414 gate document blob SHA `984c933651f39f1ee9e26a1d7ac3893aaa5335be`; explicitly prohibits M20 profitability and market-PIT approval.
- Action jobs (fresh metadata): 38381997417 6/6 success; 38382214223 6/6; 38419111311 6/6; 38419649711 1/1; OpenDART 38419439742 2/2. Job success is CI PASS only, not independent evidence of original PIT or economic merit.
- Fixed 34-case SHA-256 `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34` is historical claim, independent recomputation NOT VERIFIED. 13 adversarial mocks and 28 synthetic cases historically reported, independent artifact comparison NOT VERIFIED. Serial 2.9656s vs concurrent 2.6209s, regression phase ratio 1.1315x only; end-to-end acceleration NOT VERIFIED.

## Railway production (fresh environment_status and get_logs)
- Project `d1c1a050-b7d6-41ce-b300-13c20f82a20a`, environment `83d5840b-270e-4d3f-a941-a37fd4a55ff7`.
- PIT rebuild deployment `8b354fc1-cfb2-4ef0-863e-67f7f5dda2b5`: 1/1 running. Runtime `eaaa9f67-b9f2-41d2-832c-7d6fad9b9b00`: 1/1 running. Kiwoom real-readonly deployment `a77fb922-b679-4d88-92c4-03054ec579cd`: 0/1 running, 1 crashed despite SUCCESS/online metadata; runtime health FAIL. KRX historical worker `16c93d7c-7cd0-4d84-a327-298d2805376c`: 0/1 running (cron/idle semantics not independently resolved). Backend, push and db-query-readonly offline; db-query-readonly 1 critical.
- Window 2026-11-12 20:00–21:20 UTC: PIT 0 logs, KRX 0, Kiwoom 0; runtime 151 returned entries (limit 150 requested; provider returned 151), including USD/KRW Yahoo and KOSPI data at 21:06–21:16 UTC. Absence of PIT logs does NOT prove 2026-09-28 27 invalid OHLC originals repaired.
- Staged empty environment patch `e113dacb-6705-4416-9997-dc694539d382` still present; not applied. Live ORDERING flag not read in this run: NOT VERIFIED (required false).

## Evidence gate / decision
- KRX 2017–2022 private 1565/1565 weekday raw pair storage integrity: historical PASS only, not rehashed here. Official session/status, corporate actions, executable fills and costs/taxes: NOT VERIFIED. Known 2026-09-28 27 invalid OHLC and zero-activity 12003 remain excluded; resolution NOT VERIFIED.
- Original-filing, public available-at/PIT, 2021/2022 first consolidated three-month operating-profit period and correction lineage, historical corp/security mappings: NOT VERIFIED. OpenDART 15 candidate-row signature success is not semantic/timestamp approval.
- NetEV, PF, CAGR, MDD, ES95/99, concentration and temporal robustness after taxes/costs: NOT VERIFIED, M20 NO-GO. No economic RUN performed.
- H5 failed/consumed Holdout and Dynamic results not recyclable; Frozen H5, M20 horizon20/purge20, WF504/126/126, Purged/CPCV, independent Holdout, Champion/Top3/NO_TRADE, risk/cost/tax gates unchanged.
- Cache only when independently approved source/data/code/Frozen/runtime/approval evidence SHA-256 all match, otherwise fail-closed. Only independent read-only postprocessing parallelism. No dependent retraining or capital transition parallelism.

## Next admissible work
1. KRX owner independently rehash 27 private originals and prove official session/tradability/corporate-action lineage without leaking private rows.
2. DART owner prove exact original-filing public timestamps, 2021/2022 first consolidated three-month operating-profit and corrections, with source SHA.
3. Independently compare offline synthetic fixed cases/artifacts and PR #413/#418 implementation parity, without official-market economic tests.
4. Confirm ORDERING=false via approved read-only runtime config/log evidence. Keep M20 NO-GO, no order/deploy/merge/promotion.


## 2026-11-13 08:22 KST — independent read-only check
- Research branch index-alert-research-v1 identical to df474df348f22aa38b1dedaa59fcff66e548b406 (compare ahead=0, behind=0). Development index-alert-position-regen-fix-v1 identical to 1e6367d2863a86c3470da13d81a955d277eba485 (compare ahead=0, behind=0).
- PR HEADs, all OPEN/Draft/unmerged: #412 bf3d9514a87c53b1775e22ec9ba7711f6cecc49f; #413 f003ef6247e16fcc71bd3b1b20cd4904c4d984c0; #414 18c5418d9684d1717df58261ea27f28e514385b2; #418 2f98401cc50a6c6a25808a98516efd5bf0c944ee; #420 fab3cbbd63a951a4e081f9e7f08c1391ca308581; #422 c14857620973531013799e44625d43080904fd5f; #423 0e38004363cac9fc4475556b3a1c445de9af407f.
- GitHub Actions jobs directly checked: 38381997417 6/6 success; 38382214223 6/6 success; 38419111311 6/6 success; 38419649711 1/1 success; 38419439742 2/2 success. These prove job conclusions, NOT independently reproduced fixed 34-case SHA, 13/28 mocks, economic performance or full CI speedup. Frozen fixed-case expected SHA 5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34 remains NOT VERIFIED independently.
- Railway IndexAlert production environment 83d5840b-270e-4d3f-a941-a37fd4a55ff7: PIT rebuild 1/1 running; runtime 1/1 running; Kiwoom real readonly 0/1 running, 1/1 crashed despite SUCCESS/online label = operational FAIL; KRX historical worker 0/1 running; backend/push/db-query-readonly offline, db-query-readonly critical=1. Pending staged patch e113dacb-6705-4416-9997-dc694539d382 has empty reported changes; do not apply. Latest observed Kiwoom deployment a77fb922-b679-4d88-92c4-03054ec579cd dated 2026-10-29; KRX deployment 16c93d7c-7cd0-4d84-a327-298d2805376c dated 2026-10-12.
- Railway logs read-only queried 2026-11-12 22:00–23:25 UTC: PIT 0 entries, KRX 0 entries; Kiwoom service log query returned 'Service not found in this project' (NOT VERIFIED, no fallback or inference). Runtime 121 returned records including 23:22:39 UTC Investing USD/KRW HTTP error and Yahoo fallback. No PIT/KRX source approval or OHLC remediation proven. ORDERING actual runtime value NOT VERIFIED; required false remains unchanged by this audit.
- Gate judgments: prior private 2017–2022 1565/1565 raw-pair integrity historical PASS only; 2026-09-28 27/803 OHLC anomaly unresolved FAIL; original-filing public available-at/PIT, 2021/2022 consolidated 3-month operating-profit lineage, entity historical mapping, official KRX calendar/status/corporate actions/executability, costs/tax, NetEV/PF/CAGR/MDD/ES95/99/concentration/temporal robustness all NOT VERIFIED. M20 NO-GO; no economic RUN, trading, deployment, merge, promotion or credential change.
- Optimisation PR #413/#418: CI-only synthetic test job success PASS; independently calculated fixed-case SHA, implementation parity, overall CI and official backtest speedup NOT VERIFIED. Serial 2.9656s vs concurrent 2.6209s (reported 1.1315x regression-phase only) is not a full-run acceleration claim. Cache requires approved source/data/code/Frozen/runtime/evidence SHA-256 exact match, otherwise fail closed. Parallelise read-only independent postprocessing only.
- Next: independent source SHA and official calendar/27-row KRX adjudication; DART original-filing timestamp/period/correction evidence; offline fixed-case hash and implementation comparison; authorised read-only ORDERING config evidence. No modifications to other teams' branches/workflows.
