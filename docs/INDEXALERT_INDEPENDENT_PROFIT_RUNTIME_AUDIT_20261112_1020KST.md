# IndexAlert independent audit — 2026-11-12 10:20 KST

Scope: read-only evidence review; no trading, promotion, deployment, merge, workflow edits, market backtest or model search. This document is an independent snapshot, not approval.

## Source heads (queried this run)
- research index-alert-research-v1: df474df348f22aa38b1dedaa59fcff66e548b406
- development index-alert-position-regen-fix-v1: 1e6367d2863a86c3470da13d81a955d277eba485
- prior isolated audit: 26e5ca59ddb7d43a237d80c4e929dc204124062f
- PR refs/pull/head: #412 bf3d9514a87c53b1775e22ec9ba7711f6cecc49f; #413 f003ef6247e16fcc71bd3b1b20cd4904c4d984c0; #414 18c5418d9684d1717df58261ea27f28e514385b2; #418 2f98401cc50a6c6a25808a98516efd5bf0c944ee; #420 fab3cbbd63a951a4e081f9e7f08c1391ca308581; #422 c14857620973531013799e44625d43080904fd5f; #423 0e38004363cac9fc4475556b3a1c445de9af407f. PR open/draft status was NOT VERIFIED this run (issue search returned no matches).
- #414 gate document blob SHA 984c933651f39f1ee9e26a1d7ac3893aaa5335be, fetched from refs/pull/414/head.

## Actions independently checked (jobs conclusion success)
- 38381997417: 6/6; 38382214223: 6/6; 38419111311: 6/6; 38419649711: 1/1; OpenDART 38419439742: 2/2.
- Reported fixed 34-case SHA 5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34 NOT VERIFIED independently (no artifact rehash). Synthetic 13/28 case counts are historical reports, not freshly reproduced.
- Serial 2.9656s vs concurrent 2.6209s: 1.1315x regression-phase ratio only; end-to-end CI and official backtest speed NOT VERIFIED.

## Railway production 2026-11-12 00:00–01:25 UTC
- PIT rebuild and Runtime: running 1/1 each. KRX historical worker: running 0/1 (not proof of failure for scheduled jobs). Kiwoom real-readonly: UI online but running 0/1, crashed 1/1: operational FAIL. Backend, Push, db-query-readonly offline; latter critical issue 1.
- PIT, KRX, Kiwoom service deploy log entries: 0 in queried window (not evidence of healthy ingestion). Runtime returned market quote logs and USD/KRW Investing HTTPError followed by Yahoo fallback.
- environment_status returned staged patch e113dacb-6705-4416-9997-dc694539d382 with zero changes; describe_environment returned staged=null. Do not apply; inconsistency NOT VERIFIED.

## Profitability / PIT gate
- Historical KRX 1565/1565 raw weekday pair storage integrity: historical PASS only; official holiday/calendar, suspension, delisting, corporate actions, tradability, execution, costs/tax: NOT VERIFIED.
- OpenDART original-vs-amended SGML candidate row signatures: historical evidence only. 2021/2022 first three-month consolidated operating-profit period semantics, amendment lineage, public available-at and original filing timestamp: NOT VERIFIED.
- Historical issuer/security mapping: NOT VERIFIED.
- Post-cost/post-tax annual risk-adjusted net profit, NetEV, PF, CAGR, MDD, ES95/99, return concentration, temporal robustness: NOT VERIFIED.
- H5 failed/consumed holdout cannot be independently reused; M20 horizon20/purge20, WF504/126/126 and Frozen policy unchanged. M20 economic RUN NO-GO; Champion/Top3 promotion NO-GO; ORDERING=false required, actual production value NOT VERIFIED.
- Cache must fail closed unless approved input/data/code/Frozen policy/runtime/evidence SHA-256 all match. Parallelism limited to read-only independent postprocessing; no dependent retraining or capital-transition parallelism.

## Next allowed steps
1. Obtain independently auditable original filing/available-at, exact consolidated 3-month 2021/2022 lineage and issuer/security mapping.
2. Obtain official KRX historical calendar, state, corporate-action and execution evidence; reconcile invalid/zero-activity records without backfilling.
3. Rehash fixed CI artifact and inspect job evidence; perform synthetic offline safety-only checks. Do not launch economic or new performance experiments until source PIT gate is approved.
4. Diagnose Railway Kiwoom replica and read-only db critical issue without changing production.
