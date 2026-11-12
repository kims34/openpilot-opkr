# IndexAlert independent evidence audit — 2026-11-12 12:23 KST

Read-only cross-check; this document alone is the authorized isolated write. No economic replay, new market experiment, workflow edit, merge, deployment, order, credential change or Champion promotion.

## Fresh GitHub references
- Branch names independently found: `index-alert-research-v1`, `index-alert-position-regen-fix-v1`, `indexalert-independent-audit-20261111-2323kst`. Branch tip SHA **NOT VERIFIED this run** (branch-search returned names only); prior pinned research `df474df348f22aa38b1dedaa59fcff66e548b406`, development `1e6367d2863a86c3470da13d81a955d277eba485`, not asserted fresh.
- PRs OPEN/Draft/unmerged, HEAD verified via GitHub PR metadata: #412 `bf3d9514a87c53b1775e22ec9ba7711f6cecc49f`; #413 `f003ef6247e16fcc71bd3b1b20cd4904c4d984c0`; #414 `18c5418d9684d1717df58261ea27f28e514385b2`; #418 `2f98401cc50a6c6a25808a98516efd5bf0c944ee`; KRX #420 `fab3cbbd63a951a4e081f9e7f08c1391ca308581`, #422 `c14857620973531013799e44625d43080904fd5f`, #423 `0e38004363cac9fc4475556b3a1c445de9af407f`.
- PR #414 gate `docs/INDEXALERT_PROFITABILITY_INTEGRATION_GATE_2026-10-13.md` blob `984c933651f39f1ee9e26a1d7ac3893aaa5335be` fetched from its head branch.
- Actions jobs freshly queried: 38381997417 6/6 success; 38382214223 6/6 success; 38419111311 6/6 success; 38419649711 1/1 success; OpenDART 38419439742 2/2 success. Job success is **not** source-semantic/PIT admission. Frozen 34-case SHA-256 `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34`, 13 adversarial mocks and 28 synthetic cases **NOT independently recomputed**. Reported serial 2.9656s vs parallel 2.6209s (1.1315x regression phase) remains historical only; full CI and real backtest acceleration NOT VERIFIED.

## Fresh Railway production
Project `d1c1a050-b7d6-41ce-b300-13c20f82a20a`, environment `83d5840b-270e-4d3f-a941-a37fd4a55ff7`.
- Latest deployment records: PIT rebuild SUCCESS `8b354fc1-cfb2-4ef0-863e-67f7f5dda2b5`, runtime SUCCESS `eaaa9f67-b9f2-41d2-832c-7d6fad9b9b00`, KRX worker SUCCESS `16c93d7c-7cd0-4d84-a327-298d2805376c`, Kiwoom real-readonly SUCCESS `a77fb922-b679-4d88-92c4-03054ec579cd`. Deploy success does not prove running.
- Live replica status: PIT 1 running/1 total PASS (availability only), runtime 1/1 PASS (availability only); KRX worker 0 running/1 total **NOT VERIFIED operational readiness**; Kiwoom real-readonly 0 running/1 crashed **FAIL** despite UI service state online. Backend and Push offline; db-query-readonly offline, 1 critical. No automatic remediation.
- Deploy logs requested 2026-11-12 02:20–03:25 UTC: PIT 0, KRX 0, Kiwoom 0; runtime 101 entries returned (provider response limit), including 03:16 UTC ETF closed-market futures-proxy pricing; these are display/market quote logs, not source PIT evidence.
- `describe_environment.staged=null` while `environment_status.pendingWork` includes empty staged patch `e113dacb-6705-4416-9997-dc694539d382`; left untouched, reconciliation NOT VERIFIED.

## Admission and separation
- KRX weekday private raw-pair storage 1565/1565: **PASS only under historical 2026-10-14 pinned storage-integrity evidence**, no fresh private SHA audit. Official trading calendar, 90 uncertain days, 12003 zero-activity rows, 27 suspect OHLC, halts, delistings, corporate actions, executable fills and cost/tax: **NOT VERIFIED / fail closed**.
- OpenDART original and amended SGML candidate rows (15) and numeric-adjacent signatures: **historical extraction PASS only**. 2021/2022 original first 3-month consolidated operating income, exact period, corrections lineage, public available-at/PIT and historical corporation/security mappings: **NOT VERIFIED / fail closed**. Do not backfill first-filing from amended reports.
- Frozen H5 consumed/failed Holdout: **NO-GO**, no independent reuse or post-hoc tuning. M20 horizon20/purge20, WF504/126/126 and frozen PIT/labels/Purged/CPCV/Holdout/Champion/Top3/NO_TRADE unchanged. M20 performance run: **NOT AUTHORIZED**.
- Post-cost/post-tax risk-adjusted annual profitability: NetEV, PF, CAGR, MDD, ES95/99, profit concentration, temporal robustness: **NOT VERIFIED**. No PASS inferred from synthetic CI.
- Optimization: offline-only software parity **CI PASS**, full end-to-end runtime/real official backtest speed **NOT VERIFIED**. Cache only if independently approved source/data/code/Frozen/runtime/evidence SHA-256 match; fail closed; parallelize read-only independent postprocessing only, never dependent retraining or capital transition.
- ORDERING=false required; **actual deployed value NOT VERIFIED**. No trading, funds, credentials, Champion promotion, merges or deploys.

## Next permitted work
1. Source owners independently attest official first-filing period, available-at, correction lineage and historical entity/security mapping with raw SHA; KRX owner separately attests official session/trading status, corporate actions, executable fill and cost/tax evidence.
2. Independently recompute offline frozen test SHA and inspect relevant CI artifacts/logs without changing frozen policies.
3. Diagnose crashed Kiwoom replica and KRX 0-running mismatch read-only; no restart or deployment without separate authorization.
4. Keep M20 NO-GO until all source gates independently pass; document any true new evidence rather than promoting archived results.
