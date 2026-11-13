# IndexAlert independent read-only gate — 2026-11-14 05:23 KST

Scope: evidence audit only; not a PIT approval, backtest authorization, production deployment, or strategy promotion. No confidential raw source data reproduced.

## GitHub pinned evidence
- research index-alert-research-v1 HEAD df474df348f22aa38b1dedaa59fcff66e548b406
- development index-alert-position-regen-fix-v1 HEAD 1e6367d2863a86c3470da13d81a955d277eba485
- Draft/open PR HEADs: #412 bf3d9514a87c53b1775e22ec9ba7711f6cecc49f; #413 f003ef6247e16fcc71bd3b1b20cd4904c4d984c0; #414 18c5418d9684d1717df58261ea27f28e514385b2; #418 2f98401cc50a6c6a25808a98516efd5bf0c944ee; #420 fab3cbbd63a951a4e081f9e7f08c1391ca308581; #422 c14857620973531013799e44625d43080904fd5f; #423 0e38004363cac9fc4475556b3a1c445de9af407f.
- PR #414 integration gate blob SHA-1 984c933651f39f1ee9e26a1d7ac3893aaa5335be.
- Actions jobs verified live: 38381997417 6/6 PASS; 38382214223 6/6 PASS; 38419111311 6/6 PASS; 38419649711 1/1 PASS; OpenDART 38419439742 2/2 PASS; 38486028854 1/1 FAIL. Latest failure job 115599778959; archived case mismatch remains unresolved, subsequent suite not admitted. Historical pinned 34-case SHA-256 5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34 was not independently recalculated this run.
- Optimization offline-only: synthetic software checks PASS at their historical SHA; full CI acceleration, official backtest acceleration and 34-case fresh parity NOT VERIFIED. Single-runner serial 2.9656s vs parallel suite 2.6209s is only historical regression-phase timing, not overall speedup.

## Railway production read-only
Project d1c1a050-b7d6-41ce-b300-13c20f82a20a, environment 83d5840b-270e-4d3f-a941-a37fd4a55ff7.
- PIT rebuild deployment 8b354fc1-cfb2-4ef0-863e-67f7f5dda2b5 SUCCESS, replica 1/1 running; Runtime eaaa9f67-b9f2-41d2-832c-7d6fad9b9b00 SUCCESS 1/1 running.
- KRX historical worker deployment 16c93d7c-7cd0-4d84-a327-298d2805376c SUCCESS, replica 0/1 running; Kiwoom real-readonly-run 6d3d5812-eb91-41b6-acba-9c62a68b3271 SUCCESS, replica 0/1 running. A SUCCESS deployment is not proof of active execution.
- Backend, push, db-query-readonly offline; separate kiwoom-real-readonly offline.
- pendingWork patch:e113dacb-6705-4416-9997-dc694539d382 remains staged since 2026-10-29T06:20:53Z, empty changes array in status response; DO NOT accept/deploy.
- 2026-11-13 19:00–20:25 UTC deploy logs: PIT 0, KRX 0 entries; Runtime returned 201 entries (query limit 200, possible service cap/pagination), with Investing USD/KRW HTTP errors and Yahoo fallback at 20:23:42Z. No new official PIT/KRX acceptance evidence. Prior 27/803 OHLC invalids and 12,003 zero-activity cases remain unresolved, not retested or cleared.

## Integration verdict
- Stored historical KRX weekday pair integrity 1565/1565: historical PASS for storage only; official session calendar, security status, corporate actions, fillability, fees/taxes: NOT VERIFIED / FAIL-CLOSED.
- OpenDART SGML candidate-row detection: historical software PASS; original-filing meaning, public available-at/PIT, 2021/2022 first three-month consolidated operating-profit period and correction lineage, historical issuer-security mapping: NOT VERIFIED.
- H5 consumed/failed holdout: NO-GO; no reuse as independent holdout. M20 horizon20/purge20, WF504/126/126, Frozen label/Purged/CPCV/Holdout/Champion/Top3/NO_TRADE gates unchanged. M20 economic RUN not authorized.
- After-fee/tax NetEV, PF, CAGR, MDD, ES95/99, return concentration and temporal robustness: NOT VERIFIED; no credible profitability conclusion.
- Optimization #413/#418: offline synthetic tests PASS at historical runs, integration job FAIL, full acceleration NOT VERIFIED. Cache only on all approved evidence SHA-256 matches; read-only postprocessing parallel only. No dependent retraining/capital transition parallelization.
- ORDERING=false and no trade, fund movement, credential/permission change, promotion, merge or deploy authorized.

Next safe actions: investigate archived case SHA mismatch without modifying protected workflows; independently reproduce fixed 34-case SHA offline in isolated code; obtain official first-filing public timestamp and corrected-period lineage; classify KRX 27 invalid OHLC rows with official status/calendar; verify Railway staged patch via read-only status before any proposed intervention. Never run M20 market economics before source PIT approval.
