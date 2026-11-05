# IndexAlert independent profitability and runtime audit — 2026-11-06 02:19 KST

Scope: read-only verification of GitHub and Railway; no economic backtest, model exploration, operational changes or orders. This is an evidence ledger, NOT a source/PIT admission.

## GitHub
- PR heads (all OPEN/DRAFT, directly fetched): #412 `bf3d9514a87c53b1775e22ec9ba7711f6cecc49f`; #413 `f003ef6247e16fcc71bd3b1b20cd4904c4d984c0`; #414 `18c5418d9684d1717df58261ea27f28e514385b2`; #418 `2f98401cc50a6c6a25808a98516efd5bf0c944ee`; #420 `fab3cbbd63a951a4e081f9e7f08c1391ca308581`; #422 `c14857620973531013799e44625d43080904fd5f`; #423 `0e38004363cac9fc4475556b3a1c445de9af407f`.
- PR #414 gate file blob SHA `984c933651f39f1ee9e26a1d7ac3893aaa5335be` read at PR head; explicitly states M20 NO-GO and ORDERING disabled.
- Branch names index-alert-research-v1 and index-alert-position-regen-fix-v1 exist, but exact latest branch HEAD not independently resolved in this run: NOT VERIFIED.
- Actions job conclusions independently queried: 38381997417 6/6 success; 38382214223 6/6 success; 38419111311 6/6 success; 38419649711 1/1 success; 38419439742 2/2 success; 41515392296 auto-anchor FAILURE and validation SKIPPED. These are CI status, not independent source-PIT approval.
- Historical frozen 34-case SHA `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34` and regression-phase 1.1315x: historical evidence only, not independently recalculated. Full CI / official backtest speed NOT VERIFIED.

## Railway production (read-only)
- Project `d1c1a050-b7d6-41ce-b300-13c20f82a20a`, environment `83d5840b-270e-4d3f-a941-a37fd4a55ff7`.
- PIT rebuild deployment `8b354fc1-cfb2-4ef0-863e-67f7f5dda2b5` SUCCESS; replicas 1/1; no entries returned since 2026-11-05 15:00 UTC (absence of log evidence is not a PASS).
- KRX historical worker deployment `16c93d7c-7cd0-4d84-a327-298d2805376c` SUCCESS; replicas 0/1; no entries returned in same window.
- Runtime deployment `eaaa9f67-b9f2-41d2-832c-7d6fad9b9b00` SUCCESS; replicas 1/1. Logs 2026-11-05 17:19 UTC show Investing.com USDKRW failure and Yahoo fallback; operational market data are not official PIT proof.
- Backend, Push, db-query-readonly offline (critical on db-query-readonly); Kiwoom real-readonly running 0/crashed 1. Staged environment patch `e113dacb-6705-4416-9997-dc694539d382` untouched.
- Prior 2026-09-28 803-row/27 nonpositive OHLC and FAIL_CLOSED evidence remains historical; no new PIT log entry this run to independently reconfirm current occurrence.

## Verdict and dependencies
- Historical KRX 1565/1565 stored raw pair integrity: prior PASS evidence; no independent rehash this run.
- Official trading sessions, corporate actions, executable fills, historical entity/security mapping: NOT VERIFIED.
- Original-filing exact public available-at, 2021/2022 first 3-month consolidated operating profit period/amendment lineage: NOT VERIFIED.
- Cost/tax-adjusted NetEV, PF, CAGR, MDD, ES95/99, concentration, time robustness: NOT VERIFIED; M20 NOT EVALUABLE / NO-GO.
- Synthetic offline CI jobs: PASS at job status level only. Cache identity/evidence SHA and full acceleration: NOT VERIFIED.
- Maintain frozen H5, M20 horizon20/purge20, WF504/126/126, independent holdout, NO_TRADE and ORDERING=false. No model search, market profitability run, deployment, merges or trading.

Next safe actions: obtain immutable official KRX per-security state/corporate-action proof and exact original-filing timestamps/lineage; independently verify source hashes, chronology anchor failure, cache identity and frozen policy in isolated offline-only scope. Do not admit M20 or change any gate until independent evidence passes.
