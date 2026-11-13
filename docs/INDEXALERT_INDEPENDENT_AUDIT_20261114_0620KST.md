# IndexAlert independent audit — 2026-11-14 06:20 KST

Read-only evidence refreshed during this run. This document does not authorize source approval, economics, deployment, trading, or PR merge.

## GitHub source identity
- Research branch `index-alert-research-v1`: compare against df474df348f22aa38b1dedaa59fcff66e548b406 returns identical, ahead=0, behind=0; HEAD thus df474df348f22aa38b1dedaa59fcff66e548b406.
- Development branch `index-alert-position-regen-fix-v1`: compare against 1e6367d2863a86c3470da13d81a955d277eba485 returns identical, ahead=0, behind=0; HEAD thus 1e6367d2863a86c3470da13d81a955d277eba485.
- PR #414 gate read directly at refs/pull/414/head: docs/INDEXALERT_PROFITABILITY_INTEGRATION_GATE_2026-10-13.md blob SHA-1 984c933651f39f1ee9e26a1d7ac3893aaa5335be. Gate says M20 source PIT/economics NO-GO. Individual PR #412/#413/#418 and KRX PR HEAD/status were not freshly obtained; historical evidence is not a fresh PR status.
- Previous isolated audit read: docs/INDEXALERT_INDEPENDENT_AUDIT_20261114_0523KST.md blob SHA-1 6ca592d4b60e887d4e34e6c223ff4f524707eff1.

## GitHub Actions freshly checked (latest attempt jobs, historical run IDs)
- https://github.com/kims34/openpilot-opkr/actions/runs/38381997417: 6/6 SUCCESS.
- https://github.com/kims34/openpilot-opkr/actions/runs/38382214223: 6/6 SUCCESS.
- https://github.com/kims34/openpilot-opkr/actions/runs/38419111311: 6/6 SUCCESS.
- https://github.com/kims34/openpilot-opkr/actions/runs/38419649711: 1/1 SUCCESS.
- https://github.com/kims34/openpilot-opkr/actions/runs/38419439742: 2/2 SUCCESS.
- https://github.com/kims34/openpilot-opkr/actions/runs/38486028854: 1/1 FAILURE, job immutable-archived-case-parallel-regressions. Historical archived manifest expected/observed blob mismatch remains unresolved; current log cause not re-fetched. Historical 34-case SHA-256 5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34 not independently recomputed. Offline-only test success is not whole-CI or market backtest acceleration. Historical serial 2.9656s / parallel 2.6209s = 1.1315x regression-phase ratio only.

## Railway production
Project d1c1a050-b7d6-41ce-b300-13c20f82a20a, environment 83d5840b-270e-4d3f-a941-a37fd4a55ff7. Fresh environment status:
- PIT rebuild deployment 8b354fc1-cfb2-4ef0-863e-67f7f5dda2b5 SUCCESS, replicas 1/1 running; Runtime eaaa9f67-b9f2-41d2-832c-7d6fad9b9b00 SUCCESS, replicas 1/1 running.
- KRX historical worker 16c93d7c-7cd0-4d84-a327-298d2805376c SUCCESS, replicas 0/1; Kiwoom real-readonly-run 6d3d5812-eb91-41b6-acba-9c62a68b3271 SUCCESS, replicas 0/1. Deployment success != running process. Backend, push, db-query-readonly offline.
- pendingWork patch:e113dacb-6705-4416-9997-dc694539d382 status staged since 2026-10-29T06:20:53.202Z, changes=[]; do not apply.
- Deploy logs 2026-11-13 20:20–21:25 UTC: PIT 0, KRX 0, Runtime 151 entries. Runtime at 21:20:42Z reports Investing USD/KRW HTTPError -> Yahoo fallback. No fresh official source PIT/KRX acceptance. Prior 27/803 OHLC invalid and 12003 zero-activity remain unapproved; no claim they persist at identical counts in new data.

## Evidence verdict and boundaries
- KRX 2017–2022 1565/1565 weekday pair storage SHA integrity: historical PASS for storage only. Official session calendar, trading status, corporate actions, historical issuer/security mapping, fillability, fees/taxes: NOT VERIFIED, FAIL-CLOSED.
- OpenDART SGML 15 candidate rows/numeric adjacency: historical software PASS; original-filing meaning, public available-at/PIT, 2021/2022 first three-month consolidated operating profit period/correction lineage: NOT VERIFIED.
- H5 consumed holdout: NO-GO for independent reuse. M20 horizon20/purge20, WF504/126/126, PIT/Purged/CPCV/Holdout/Champion/Top3/NO_TRADE remain frozen. M20 market economics: NOT AUTHORIZED.
- After-cost/tax NetEV, PF, CAGR, MDD, ES95/99, return concentration, temporal robustness: NOT VERIFIED; profitability gate NO-GO.
- Optimization: historical offline synthetic tests PASS; PR #418 integrated CI FAIL; independent 34-case parity and overall acceleration NOT VERIFIED. Fail-closed cache requires matching independent approved source/data/code/Frozen/runtime/approval SHA-256. Parallelize read-only postprocessing only, not dependent retraining or capital transitions.
- ORDERING=false; no deployment, merge, live order, fund movement, credential/permission change or Champion promotion.

Next safe work: inspect immutable archived case mismatch without protected workflow changes; reproduce pinned 34-case SHA offline; verify first-filing timestamp and correction lineage; classify 27 historical OHLC anomalies with official KRX state/calendar; investigate staged patch read-only. No new strategy/model or M20 economic run before source PIT approval.
