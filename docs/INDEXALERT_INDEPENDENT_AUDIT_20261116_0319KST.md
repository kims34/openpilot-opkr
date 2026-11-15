# IndexAlert independent audit — 2026-11-16 03:19 KST

Scope: read-only GitHub/Railway inspection, no strategy/economic backtest, no deployment/merge/order. This document is an evidence ledger, NOT PIT or profitability approval.

## Git refs verified in this run
- research `index-alert-research-v1`: `df474df348f22aa38b1dedaa59fcff66e548b406` (GitHub fetch_commit ref)
- development `index-alert-position-regen-fix-v1`: `1e6367d2863a86c3470da13d81a955d277eba485`
- Draft/open/unmerged PRs (head SHA): #412 `bf3d9514a87c53b1775e22ec9ba7711f6cecc49f`; #413 `f003ef6247e16fcc71bd3b1b20cd4904c4d984c0`; #414 `18c5418d9684d1717df58261ea27f28e514385b2`; #418 `2f98401cc50a6c6a25808a98516efd5bf0c944ee`; #420 `fab3cbbd63a951a4e081f9e7f08c1391ca308581`; #422 `c14857620973531013799e44625d43080904fd5f`; #423 `0e38004363cac9fc4475556b3a1c445de9af407f`.
- #414 integration gate document Git blob SHA-1: `984c933651f39f1ee9e26a1d7ac3893aaa5335be` (fetched).
- This audit is branched from previous isolated audit commit `453d017dde45555e84cfa78bf7d034930ad198be`, without modifying any active work branch.

## CI observed
- Actions [38381997417](https://github.com/kims34/openpilot-opkr/actions/runs/38381997417) 6/6 PASS; [38382214223](https://github.com/kims34/openpilot-opkr/actions/runs/38382214223) 6/6 PASS; [38419111311](https://github.com/kims34/openpilot-opkr/actions/runs/38419111311) 6/6 PASS; OpenDART [38419439742](https://github.com/kims34/openpilot-opkr/actions/runs/38419439742) 2/2 PASS (software/row matching, NOT PIT); single-runner [38419649711](https://github.com/kims34/openpilot-opkr/actions/runs/38419649711) 1/1 PASS (synthetic only).
- [38486028854](https://github.com/kims34/openpilot-opkr/actions/runs/38486028854) 1/1 FAIL, job `115599778959`; job log has no pinned-parallel artifacts. Previously reported expected blob `108f66714602a1bd3ae42c34dcca7c16e38f460b` vs observed `e428789e2e97ca7be3a4482e0df23b483a1ad69d`; independent exact SHA recomputation NOT VERIFIED. Archived 34-case SHA-256 `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34` is historical evidence only, not recalculated this run. 2.9656/2.6209=1.1315x regression phase only, no full-CI or market-backtest acceleration approval.

## Railway production read-only
Project `d1c1a050-b7d6-41ce-b300-13c20f82a20a`, environment `83d5840b-270e-4d3f-a941-a37fd4a55ff7`. Runtime latest deployment SUCCESS `eaaa9f67-b9f2-41d2-832c-7d6fad9b9b00`, PIT rebuild SUCCESS `8b354fc1-cfb2-4ef0-863e-67f7f5dda2b5`, KRX historical worker SUCCESS `16c93d7c-7cd0-4d84-a327-298d2805376c` (deployment status is not live health). `stagedChanges=null` conflicts with pendingWork patch `e113dacb-6705-4416-9997-dc694539d382` status staged since 2026-10-29: unresolved. Runtime logs 2026-11-15 17:30–18:25 UTC: Investing USD/KRW HTTP errors with Yahoo fallback; PIT rebuild and KRX worker logs 0 in same queried window. Zero new entries is not proof of recovery. Prior 27/803 invalid common-stock OHLC remains unresolved, no fresh independent source confirmation this run.

## Gate verdicts
- Historical KRX 1565/1565 weekday raw pairs: historical storage integrity PASS (2026-10-14 evidence), official calendar/tradability NOT VERIFIED.
- KRX prospective 27/803 OHLC: prior quality FAIL, latest source repair NOT VERIFIED; fail-closed guard remains required.
- OpenDART first original filing, exact public available-at, 2021/2022 initial three-month consolidated operating profit and correction lineage: NOT VERIFIED.
- Historical entity/security mapping, official KRX statuses/actions/fillability, execution costs and taxes: NOT VERIFIED.
- NetEV, PF, CAGR, MDD, ES95/99, concentration and time robustness after costs/tax: NOT VERIFIED. M20 NO-GO, no economic run.
- Optimisation offline CI subset PASS, immutable-manifest integration FAIL, full wall-clock acceleration NOT VERIFIED.
- Holdout H5 consumed; cannot be reused independently or tuned after the fact.

## Constraints / next steps
Preserve Frozen H5, M20 horizon20/purge20, WF504/126/126, PIT/label/Purged/CPCV/independent holdout/Champion/Top3/NO_TRADE, fixed costs/taxes/risk and promotion rules, ORDERING=false. Cache only if all independently approved source/data/code/frozen-policy/runtime/approval SHA-256 match fail-closed. Parallelise only independent read-only postprocessing, never dependent retraining or capital transition. Before PIT approval: synthetic offline safety tests only; no strategy search or market return/performance experiment. No live orders, account/auth changes, promotion, deployment, or PR merge. Next: independently reconcile 27 KRX OHLC originals and official status, DART original-filing PIT, PR418 immutable manifest mismatch; verify staged patch discrepancy. No external approvals inferred.
