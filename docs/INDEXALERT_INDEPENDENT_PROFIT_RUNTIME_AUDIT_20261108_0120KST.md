# IndexAlert independent read-only gate and isolated runtime audit — 2026-11-08 01:20 KST

Scope: independent evidence only; no source, workflow, model, trading, deployment, PR merge or economic backtest changes. All statuses are scoped to observed original GitHub/Railway evidence. This audit branch was based on PR #414 base commit 3b8b7830612a6284d7c7a60628cb527cb741627a; it is not a claim that this is the latest research branch HEAD.

## GitHub pinned source evidence
- PR #414 OPEN/Draft HEAD 18c5418d9684d1717df58261ea27f28e514385b2; base SHA 3b8b7830612a6284d7c7a60628cb527cb741627a; integration gate blob SHA 984c933651f39f1ee9e26a1d7ac3893aaa5335be (fetched directly from PR branch).
- PR #413 OPEN/Draft HEAD f003ef6247e16fcc71bd3b1b20cd4904c4d984c0; #418 OPEN/Draft HEAD 2f98401cc50a6c6a25808a98516efd5bf0c944ee; #412 OPEN/Draft HEAD bf3d9514a87c53b1775e22ec9ba7711f6cecc49f.
- KRX #420 HEAD fab3cbbd63a951a4e081f9e7f08c1391ca308581, #422 HEAD c14857620973531013799e44625d43080904fd5f, #423 HEAD 0e38004363cac9fc4475556b3a1c445de9af407f; all OPEN/Draft.
- Research and development branch names were found in GitHub branch search. Exact current branch HEADs NOT VERIFIED in this run; PR base SHA is not proof of branch HEAD.
- Actions #38419439742: 2/2 jobs success; #38419649711: 1/1 success; #38498552499: 6/6 success; chronology #41515392296: auto-anchor failure, validation skipped. Older fixed-test SHA 5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34 and earlier run IDs are historical supplied evidence, not independently re-hashed this run. CI success is offline synthetic only, not official PIT or measured whole-backtest acceleration.

## Railway original operational evidence
- Project IndexAlert d1c1a050-b7d6-41ce-b300-13c20f82a20a, production 83d5840b-270e-4d3f-a941-a37fd4a55ff7.
- PIT rebuild deployment 8b354fc1-cfb2-4ef0-863e-67f7f5dda2b5 SUCCESS, running 1/1. Direct log entries 2026-11-07 13:00:56–14:46:14 UTC show FAIL_CLOSED, KRXProspectiveOpenAPISourceError, COMMON_OHLC_NONPOSITIVE, 803 common stock rows, 27 nonpositive OHLC, 27 zero volume/value, source failure session 2026-09-28, session_manifest_sha256 null, independent source/chronology/model admission false, fresh alpha false, ORDERING DISABLED. Query from 15:00 UTC returned no newer PIT logs; no inference of recovery.
- KRX worker deployment 16c93d7c-7cd0-4d84-a327-298d2805376c SUCCESS, replicas running 0 crashed 0; query from 15:00 UTC no logs. Official calendar/status/tradeability still NOT VERIFIED.
- Real readonly deployment a77fb922-b679-4d88-92c4-03054ec579cd SUCCESS, replica running 0 crashed 1 (inconsistent with displayed online status); query from 15:00 UTC no logs. Treat as unresolved operational blocker, not successful runtime health.
- Runtime deployment eaaa9f67-b9f2-41d2-832c-7d6fad9b9b00 SUCCESS, running 1/1. Logs at 16:20 UTC include Investing USD/KRW unavailable and Yahoo fallback, not evidence for source PIT admission.
- db-query-readonly critical alert 1. Pending staged empty patch e113dacb-6705-4416-9997-dc694539d382, changes [], not deployed or touched.

## Gate decisions
- OpenDART candidate-row numerical signature CI: PASS only within synthetic/candidate scope; original 2021/2022 first 3-month consolidated operating profit, corrected vintage lineage and exact public available-at/PIT: NOT VERIFIED.
- Historical issuer/ticker mapping, KRX official holiday/trading status/corporate actions/executability and complete transaction costs/taxes: NOT VERIFIED. Prior 1565/1565 private weekday storage integrity is historical PASS only, not official market admission.
- Prospective PIT source: FAIL_CLOSED on current directly observed logs; chronology anchor job: FAIL; M20 admission: NO-GO.
- NetEV/PF/CAGR/MDD/ES95/99, concentration, temporal robustness and annual post-cost/post-tax risk-adjusted profitability: NOT VERIFIED; no economic run authorized.
- Isolated optimization PR #413/#418: offline CI scoped PASS; actual end-to-end speedup and official backtest parity NOT VERIFIED. Historical serial 2.9656s vs concurrent 2.6209s (regression phase 1.1315x) is not whole-run evidence.

## Safe next steps
1. Obtain independently signed official first-original DART bytes, CFS 3-month cell meaning, corrections and exact public availability time with hashes, then independently verify issuer history.
2. Resolve 27 KRX OHLC failures, official calendar/status/corporate action/execution and chronology anchor, with original receipts and CI logs. Preserve fail-closed and zero-activity external exclusion.
3. Only offline synthetic regression/security checks in separate optimization scope; cache only exact approved data/code/Frozen policy/runtime/evidence SHA-256 matches; read-only postprocessing parallelism only. No dependent training or capital transition parallelism.
4. Maintain Frozen H5, M20 horizon20/purge20, WF504/126/126, holdout isolation, Champion/Top3/NO_TRADE, costs/taxes/risk thresholds unchanged; ORDERING=false. No M20, market economic replay, Champion promotion, real orders, permissions, money movement, deploy or merges without separate authorization.
