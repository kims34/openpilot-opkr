# IndexAlert independent read-only audit — 2026-11-10 00:22 KST

Scope: profitability integration gate and isolated offline-only optimisation evidence. This is NOT source approval, economic backtest approval, live deployment or order authorisation. No secrets, raw market rows, account data or proprietary payloads included.

## GitHub refs (direct connector read)
- research index-alert-research-v1 HEAD df474df348f22aa38b1dedaa59fcff66e548b406
- development index-alert-position-regen-fix-v1 HEAD 1e6367d2863a86c3470da13d81a955d277eba485
- compare development...research: DIVERGED, ahead 281 / behind 1148; merge base c490974ff6619bb978dc6f83f9c24f2c46622f85. Identical SHA from earlier report was incorrect interpretation; these branches are NOT identical.
- PR #412 OPEN DRAFT bf3d9514a87c53b1775e22ec9ba7711f6cecc49f
- PR #413 OPEN DRAFT f003ef6247e16fcc71bd3b1b20cd4904c4d984c0
- PR #414 OPEN DRAFT 18c5418d9684d1717df58261ea27f28e514385b2; docs/INDEXALERT_PROFITABILITY_INTEGRATION_GATE_2026-10-13.md blob 984c933651f39f1ee9e26a1d7ac3893aaa5335be
- PR #418 OPEN DRAFT 2f98401cc50a6c6a25808a98516efd5bf0c944ee
- KRX PR #420 OPEN DRAFT fab3cbbd63a951a4e081f9e7f08c1391ca308581; #422 OPEN DRAFT c14857620973531013799e44625d43080904fd5f; #423 OPEN DRAFT 0e38004363cac9fc4475556b3a1c445de9af407f
- Existing isolated audit branch HEAD before this write: 251d028c0503e0f0058778ff2d5e7082723830d6.

## Actions jobs (direct read)
- 38381997417: 6/6 success; 38382214223: 6/6 success; 38419111311: 6/6 success.
- 38419649711: 1/1 success; 38419439742: 2/2 success.
- Chronology Anchor 41515392296: auto-anchor FAILURE; validation SKIPPED. HTTP 404 is historical reported symptom, not freshly re-derived from job logs in this run.
- Fixed 34-case SHA-256 5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34 and 13 adversarial / 28 synthetic cases are historical attestations, not rehashed in this run.
- serial 2.9656s vs concurrent 2.6209s, regression phase 1.1315x historical observation only; end-to-end CI/official backtest speedup NOT VERIFIED.

## Railway production (direct read)
Project d1c1a050-b7d6-41ce-b300-13c20f82a20a, environment 83d5840b-270e-4d3f-a941-a37fd4a55ff7.
- PIT rebuild deployment 8b354fc1-cfb2-4ef0-863e-67f7f5dda2b5 SUCCESS, actual replicas running 1/total 1. Runtime eaaa9f67-b9f2-41d2-832c-7d6fad9b9b00 SUCCESS, running 1/1.
- Kiwoom real readonly a77fb922-b679-4d88-92c4-03054ec579cd deployment SUCCESS but running 0, crashed 1/1: runtime FAIL.
- KRX historical worker 16c93d7c-7cd0-4d84-a327-298d2805376c SUCCESS but running 0/crashed 0/total 1; runtime execution NOT VERIFIED.
- Backend and push latest FAILED/offline; db-query-readonly offline with 1 critical.
- describe_environment staged=null but environment_status returned empty-changes staged patch e113dacb-6705-4416-9997-dc694539d382: inconsistent reporting; DO NOT accept/deploy.
- PIT deploy logs at 2026-11-09 23:31 and 23:46 KST: COMMON_OHLC_NONPOSITIVE, 803 common-stock rows, 27 nonpositive OHLC, 27 zero volume/value; fresh_alpha_observation_admitted=false, independent source/model/chronology admission verified=false, live_order_authorized=false, ordering=DISABLED. Safe FAIL_CLOSED PASS, source admission FAIL/BLOCKED. KRX worker and real readonly yielded zero logs in sampled 23:30-00:25 KST window; zero logs do not prove health.

## Independent gates
- Official first original filing, public available-at/PIT, 2021/2022 first 3-month consolidated operating profit period and correction lineage: NOT VERIFIED.
- Historical issuer/security mappings, KRX calendar/status/corporate actions/executable fills/costs/taxes: NOT VERIFIED.
- Historical private raw 1565/1565 weekday pair integrity: prior PASS only, not a market admission. 90-day classification and zero-activity 12003 external exclusion remain prior boundaries.
- NetEV, PF, CAGR, MDD, ES95/99, concentration, temporal robustness, post-cost/post-tax annual risk-adjusted net profitability: NOT VERIFIED.
- H5 consumed/failed holdout and Dynamic results must not be retrofitted or reused as independent holdout. M20 PIT and economic RUN: NO-GO.
- Frozen H5; M20 horizon20/purge20; WF504/126/126; PIT, purged/CPCV, independent holdout, Champion/Top3/NO_TRADE and risk/cost/tax/execution promotion policy unchanged.
- ORDERING=false required and log reports DISABLED; actual environment variable value NOT independently inspected.

## Optimisation boundaries / next evidence
- PR #413 and #418 software-only CI PASS for recorded jobs, but performance and official backtest speedup NOT VERIFIED.
- Fail-closed cache only on independently approved source/data/code/Frozen policy/runtime/approval evidence SHA-256 match. Only independent read-only postprocessing may parallelise; no dependent retraining or capital transition parallelism.
- Next: source owner must independently reconcile 27 KRX OHLC exceptions with official status/transaction/corporate-action lineage; original DART filing time/period/correction mapping; chronology 404 root cause and isolated readonly runtime crash. Obtain immutable source SHA, logs and independent sign-off before any M20 economic test.
- No code/workflow writes, merges, deployment, ordering, funds movement, permission changes or Champion promotion authorised.
