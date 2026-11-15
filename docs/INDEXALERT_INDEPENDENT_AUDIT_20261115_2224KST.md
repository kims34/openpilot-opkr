# IndexAlert independent audit — 2026-11-15 22:24 KST

Scope: read-only evidence inspection; offline-only optimization verification. No market backtest, model search, deployment, merge, workflow edit, permission change, or orders.

## Exact PR heads (GitHub read 2026-11-15)
- #412 bf3d9514a87c53b1775e22ec9ba7711f6cecc49f
- #413 f003ef6247e16fcc71bd3b1b20cd4904c4d984c0
- #414 18c5418d9684d1717df58261ea27f28e514385b2
- #418 2f98401cc50a6c6a25808a98516efd5bf0c944ee
- #420 fab3cbbd63a951a4e081f9e7f08c1391ca308581
- #422 c14857620973531013799e44625d43080904fd5f
- #423 0e38004363cac9fc4475556b3a1c445de9af407f
All draft/open/unmerged. Research and development branch tip SHA: NOT VERIFIED this run.
#414 gate document Git blob SHA-1: 984c933651f39f1ee9e26a1d7ac3893aaa5335be.

## GitHub Actions direct job evidence
- 38381997417: 6/6 success; 38382214223: 6/6 success.
- 38419111311: 6/6 success.
- 38419439742: 2/2 success; candidate extraction only, not filing semantic/PIT approval.
- 38419649711: 1/1 success, synthetic offline only.
- 38486028854: 1/1 failure, immutable archived case parity; prior manifest Git blob SHA mismatch remains unresolved. Historical 34-case SHA-256 5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34 not independently recalculated this run. Whole-CI or official backtest acceleration NOT VERIFIED.

## Railway production, read 2026-11-15 13:25 UTC
Project d1c1a050-b7d6-41ce-b300-13c20f82a20a; environment 83d5840b-270e-4d3f-a941-a37fd4a55ff7.
PIT rebuild 1/1 running, runtime 1/1 running, KRX historical worker 0/1 running (deployment SUCCESS is not worker execution proof). Backend/push/db-query-readonly offline; db-query-readonly critical 1. Environment pending patch e113dacb-6705-4416-9997-dc694539d382 staged since 2026-10-29T06:20:53Z.
PIT logs 12:00–13:25 UTC: six consecutive FAIL_CLOSED, error COMMON_OHLC_NONPOSITIVE; common_stock_rows=803, nonpositive_ohlc_rows=27, zero_volume_value_rows=27, source_failure_session=2026-09-28, session_manifest_sha256=null, independent source/model/chronology admission=false, fresh_alpha_observation_admitted=false, ordering=DISABLED. KRX worker log entries 0 in window. Runtime: Investing USD/KRW HTTP errors with Yahoo fallback, not official source/PIT approval.

## Gate decisions
PASS: previously verified offline CI jobs; fail-closed block observed in current PIT logs.
FAIL: official prospective KRX OHLC quality gate (27/803); #418 integrated immutable archive CI.
NOT VERIFIED: original-filing public available-at/PIT; 2021/2022 first-quarter consolidated operating profit period/correction lineage; historic company-security mapping; official KRX calendar, corporate actions, execution feasibility and taxes/costs; H5 independent holdout, M20 horizon20/purge20 and WF504/126/126 economics; NetEV/PF/CAGR/MDD/ES95/ES99, concentration, temporal robustness; full CI acceleration; 34-case SHA independently reproduced.
M20 NO-GO. Preserve frozen policy, consumed H5 holdout exclusion, NO_TRADE and ORDERING=false. No new economics run before official PIT approval.

## Next safe steps
1. Independently reconcile the 27 nonpositive OHLC rows against official KRX status/corporate actions and immutable source receipt SHA, without changing production.
2. Verify DART original filing semantic row, exact publication timestamps and correction lineage against independent source artifacts.
3. Isolate #418 manifest expected vs actual Git blob hashes using offline synthetic tests only; no workflow edits.
4. Recheck precise research/dev HEAD and frozen 34-case SHA on independently approved artifacts.
