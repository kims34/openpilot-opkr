# IndexAlert independent profitability and runtime audit — 2026-11-10 03:18 KST

Scope: read-only GitHub/Railway verification. No PIT admission, financial return computation, M20 run, strategy/model search, workflow edit, deployment, merge or orders. Existing frozen H5/M20 WF504/126/126, horizon20/purge20, Holdout, Top3/NO_TRADE, costs and ordering-disabled policy remain unchanged. This document is NOT authority to trade.

## Exact GitHub evidence
- Research branch index-alert-research-v1 HEAD: df474df348f22aa38b1dedaa59fcff66e548b406; development branch index-alert-position-regen-fix-v1 HEAD: 1e6367d2863a86c3470da13d81a955d277eba485, per fresh compare API. DIVERGED: development 1148 ahead / 281 behind research, merge base c490974ff6619bb978dc6f83f9c24f2c46622f85. Do not merge or interpret these as identical.
- OPEN / Draft / unmerged PR HEADs: #412 bf3d9514a87c53b1775e22ec9ba7711f6cecc49f; #413 f003ef6247e16fcc71bd3b1b20cd4904c4d984c0; #414 18c5418d9684d1717df58261ea27f28e514385b2; #418 2f98401cc50a6c6a25808a98516efd5bf0c944ee; KRX #420 fab3cbbd63a951a4e081f9e7f08c1391ca308581; #422 c14857620973531013799e44625d43080904fd5f; #423 0e38004363cac9fc4475556b3a1c445de9af407f.
- #414 integration gate document blob SHA 984c933651f39f1ee9e26a1d7ac3893aaa5335be; fetched from PR branch.
- Actions jobs checked directly: 38381997417 6/6 success; 38382214223 6/6 success; 38419111311 6/6 success; 38419649711 1/1 success; OpenDART 38419439742 2/2 success; chronology anchor 41515392296 auto-anchor FAILURE, validation SKIPPED.
- Historical 34-case identity SHA 5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34 and 2.9656s vs 2.6209s regression-only 1.1315x are prior reported evidence, not independently recalculated in this audit. Whole-CI and official market backtest acceleration NOT VERIFIED.

## Railway production — fresh read-only
- Project d1c1a050-b7d6-41ce-b300-13c20f82a20a, environment 83d5840b-270e-4d3f-a941-a37fd4a55ff7. PIT rebuild deployment 8b354fc1-cfb2-4ef0-863e-67f7f5dda2b5 SUCCESS, running 1/1; Runtime eaaa9f67-b9f2-41d2-832c-7d6fad9b9b00 SUCCESS, running 1/1. KRX worker 16c93d7c-7cd0-4d84-a327-298d2805376c SUCCESS, running 0/1, crashed 0. Real-readonly a77fb922-b679-4d88-92c4-03054ec579cd deployment SUCCESS but running 0/1, crashed 1/1: runtime health FAIL despite 'online' label. Backend and Push offline, db-query-readonly offline/critical 1.
- Describe-environment reports staged=null, whereas environment-status reports pending patch e113dacb-6705-4416-9997-dc694539d382 with empty changes. Inconsistent read-only endpoints; NOT VERIFIED as to actual staged state. No staged change applied.
- PIT and KRX logs queried from 2026-11-10 00:00 KST through current run, each returned zero entries. This does not prove resolution of previously observed 2026-09-28 27/803 invalid OHLC and zero-activity failures. Prior 23:46 KST log was last cited by earlier audit. Current fresh error persistence NOT VERIFIED; historical fail-closed evidence retained.

## Independent gates
- Official original-filing SGML 15 candidate rows / adjacent numeric signature: previous offline-source integrity PASS only. Exact original 2021/2022 Q3 standalone three-month consolidated operating profit, period/filing correction lineage, first public available-at and PIT: NOT VERIFIED / BLOCKED.
- Historical corp/security mapping, official KRX trading calendar, suspension/delisting, corporate actions, executable price/size, taxes/fees/slippage: NOT VERIFIED / BLOCKED. 1565/1565 2017-22 private weekday source pairs previously integrity PASS, NOT market admission.
- NetEV, PF, CAGR, MDD, ES95/99, profit concentration, date-cluster LCB, best-five-day robustness, yearly and instrument sensitivity: NOT VERIFIED; no M20 run authorized. Historical H5 failed/consumed holdout cannot be reused.
- Optimisation: offline synthetic regression CI PASS, economic/real-backtest speed NOT VERIFIED. Cache requires approved source/data/code/Frozen/runtime/evidence SHA-256 identity and fail-closed; parallelise independent read-only postprocessing only. No dependent retraining or capital transition parallelism.
- ORDERING=false policy; actual environment variable independently NOT VERIFIED (no secrets read). No trades, transfers, privilege changes or Champion promotion.

## Next independent steps
1. OpenDART source owner: produce original-filing 2021/22 Q3 consolidated three-month line and correction/public available-at lineage, evidence SHA and official source timestamps; no corrected-value backfill.
2. KRX owner: reconcile 27/803 invalid OHLC and official calendar/status/actions/execution feasibility with private source SHA, without quietly dropping securities.
3. Chronology owner: diagnose anchor HTTP 404 and skipped validation in independent read-only evidence; avoid workflow modifications barred by policy.
4. Runtime owner: diagnose real-readonly crashed replica and stale/empty PIT logs without deployment or order authority.
5. Optimisation owner: maintain offline-only synthetic safety parity, independently bound full CI and real market backtest speed only after source/PIT approval.
6. Integration gate remains M20 NO-GO; independent source approval is prerequisite to any economic run.
