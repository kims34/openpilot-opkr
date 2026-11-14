# IndexAlert independent audit — 2026-11-14 23:24 KST

Read-only evidence snapshot. No strategy/backtest/profitability admission, deployment, merge, ordering, or live trading.

## Exact PR heads (GitHub fetch_pr)
- #412 bf3d9514a87c53b1775e22ec9ba7711f6cecc49f
- #413 f003ef6247e16fcc71bd3b1b20cd4904c4d984c0
- #414 18c5418d9684d1717df58261ea27f28e514385b2
- #418 2f98401cc50a6c6a25808a98516efd5bf0c944ee
- #420 fab3cbbd63a951a4e081f9e7f08c1391ca308581
- #422 c14857620973531013799e44625d43080904fd5f
- #423 0e38004363cac9fc4475556b3a1c445de9af407f
All seven open, Draft, unmerged. Research/development branch latest HEAD not independently fetched in this run; previously observed research df474df348f22aa38b1dedaa59fcff66e548b406 and development 1e6367d2863a86c3470da13d81a955d277eba485 are historical, not current-HEAD claims.

## GitHub Actions jobs (direct fetch_workflow_run_jobs)
- 38381997417: 6/6 SUCCESS; 38382214223: 6/6 SUCCESS.
- 38419111311: 6/6 SUCCESS; 38419649711: 1/1 SUCCESS.
- OpenDART 38419439742: 2/2 SUCCESS, but original-filing semantics/available-at not admitted.
- #418 38486028854: 1/1 FAILURE. Prior manifest expected Git blob SHA-1 108f66714602a1bd3ae42c34dcca7c16e38f460b versus observed e428789e2e97ca7be3a4482e0df23b483a1ad69d; this run did not independently fetch failure step logs. Exact 34-case SHA-256 5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34 not recalculated. Whole CI and official-backtest speedup NOT VERIFIED.

## Railway production evidence (direct environment_status / get_logs)
Project d1c1a050-b7d6-41ce-b300-13c20f82a20a; environment 83d5840b-270e-4d3f-a941-a37fd4a55ff7.
PIT rebuild 1/1 running; Runtime 1/1 running; KRX historical worker 0/1; Kiwoom real-readonly-run 0/1. indexalert-push, indexalert-backend, db-query-readonly offline. Pending staged patch e113dacb-6705-4416-9997-dc694539d382 since 2026-10-29T06:20:53Z remains unresolved.
2026-11-14T13:15Z–14:25Z PIT logs: five 15-minute prospective FAIL_CLOSED entries at 13:16,13:31,13:46,14:01,14:16Z; error_class KRXProspectiveOpenAPISourceError, reason COMMON_OHLC_NONPOSITIVE, common_stock_rows 803; independent source/model/chronology approvals false, fresh alpha false, live order/funds authorization false. Prior observed 27 bad OHLC rows, session manifest null, ORDERING=false remain unadmitted; full current log JSON not independently enumerated. KRX worker 0 logs in window. Runtime at 14:19Z Investing USD/KRW HTTPError with Yahoo fallback. Deployment SUCCESS does not establish official data admissibility.

## Gate classifications
PASS: historic isolated synthetic CI jobs as above; historical private 1565/1565 weekday pair storage integrity only (2026-10-14 supplied evidence, not rehashed today); prospective fail-closed observed.
FAIL: #418 integrated immutable-source gate CI (job failure; exact current step cause requires fresh step-log validation); prospective source OHLC validation, NOT an investment-performance failure.
NOT VERIFIED: original OpenDART original-filing/public available-at PIT; 2021/2022 first-quarter consolidated operating-profit period/correction lineage; historical issuer/security mapping; KRX official calendar/status/actions/executability; costs and taxes; NetEV, PF, CAGR, MDD, ES95/99, concentration, temporal robustness; archived 34-case SHA independently recomputed; production/whole-backtest acceleration.

## Non-admission and next steps
M20 NO-GO, H5 frozen/consumed holdout, horizon20/purge20, WF504/126/126, independent Holdout, Champion/Top3/NO_TRADE, cost/tax/risk thresholds unchanged. ORDERING=false. Only synthetic offline tests; no market economic replay, model search, merge, deploy, workflow edit, permissions, capital movement or live order. Next: independently obtain approved original-filing bytes/available-at and KRX official trading calendar and mapping; compare #418 original source byte lineage without rewriting expected SHA; investigate 27 OHLC anomalies and Railway pending patch read-only. Cache must fail closed unless approved source/data/code/frozen policy/runtime/evidence SHA-256 all match; parallelize read-only postprocessing only.
