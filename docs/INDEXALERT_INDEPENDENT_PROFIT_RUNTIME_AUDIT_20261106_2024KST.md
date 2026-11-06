# IndexAlert independent profit/runtime audit — 2026-11-06 20:24 KST

Scope: read-only inspection; this document is not source/PIT approval, not a backtest result, not authorization to trade, merge or deploy. All referenced private source contents remain private.

## Exact GitHub references
- research `index-alert-research-v1`: `df474df348f22aa38b1dedaa59fcff66e548b406`
- development `index-alert-position-regen-fix-v1`: `1e6367d2863a86c3470da13d81a955d277eba485`
- OPEN/Draft PRs: #412 `bf3d9514a87c53b1775e22ec9ba7711f6cecc49f`, #413 `f003ef6247e16fcc71bd3b1b20cd4904c4d984c0`, #414 `18c5418d9684d1717df58261ea27f28e514385b2`, #418 `2f98401cc50a6c6a25808a98516efd5bf0c944ee`, #420 `fab3cbbd63a951a4e081f9e7f08c1391ca308581`, #422 `c14857620973531013799e44625d43080904fd5f`, #423 `0e38004363cac9fc4475556b3a1c445de9af407f` (PR status inspected via REST).
- PR #414 gate file read from PR HEAD: `docs/INDEXALERT_PROFITABILITY_INTEGRATION_GATE_2026-10-13.md`. Existing gate explicitly forbids M20 performance until DART/KRX PIT approval.
- GitHub Actions jobs independently read: 38381997417 6/6 success; 38382214223 6/6 success; 38419111311 6/6 success; 38419649711 1/1 success; 41515392296 auto-anchor FAILURE, validation SKIPPED. OpenDART 38419439742 run SUCCESS; original semantics and available-at remain unapproved.
- Historical 34-case fingerprint `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34` and 2.9656s/2.6209s (1.1315x regression-phase) are previously reported evidence, **not independently rehashed or rebenchmarked in this run**. No whole-CI/real-backtest speedup established.

## Railway production observed
Project `d1c1a050-b7d6-41ce-b300-13c20f82a20a`, environment `83d5840b-270e-4d3f-a941-a37fd4a55ff7`.
- PIT rebuild deployment `8b354fc1-cfb2-4ef0-863e-67f7f5dda2b5` SUCCESS, 1/1 running. Six actual deploy log entries at 2026-11-06 10:00:55, 10:16:01, 10:30:59, 10:46:08, 11:01:04, 11:16:13 UTC show `KRXProspectiveOpenAPISourceError / COMMON_OHLC_NONPOSITIVE`, `common_stock_rows=803`, `nonpositive_ohlc_rows=27`, `zero_volume_value_rows=27`, `status=FAIL_CLOSED`, `fresh_alpha_observation_admitted=false`, `live_order_authorized=false`. **Data-quality FAIL, safety veto PASS.** Current actual ordering config was not independently read; no changes applied.
- KRX worker deployment `16c93d7c-7cd0-4d84-a327-298d2805376c` SUCCESS, 0 running replicas; no fresh log entries in inspected period. Historical 1565/1565 weekday source-pair storage SHA integrity PASS per prior evidence, but official exchange calendar/status and executable trades NOT VERIFIED.
- Runtime deployment `eaaa9f67-b9f2-41d2-832c-7d6fad9b9b00` SUCCESS 1/1, logs show Investing.com USD/KRW HTTP failures with Yahoo fallback; not source admission evidence.
- Backend, push, db-query-readonly OFFLINE; db-query-readonly 1 critical. Kiwoom real-readonly reports online while replicas running 0/crashed 1. Staged patch `e113dacb-6705-4416-9997-dc694539d382` persists as staged (not deployed).

## Gate verdict
- OpenDART original-filing exact 2021/2022 3-month consolidated operating profit, original/correction lineage, public available-at: NOT VERIFIED / FAIL-CLOSED.
- Historical corp/security mapping, KRX official session/state/corporate actions/fillability, fees/taxes: NOT VERIFIED / FAIL-CLOSED.
- 27 prospective OHLC defects: FAIL (source quality); fail-closed guard: PASS.
- Chronology Anchor: FAIL; downstream validation SKIPPED.
- NetEV/PF/CAGR/MDD/ES95/ES99, concentration, temporal robustness, net annual risk-adjusted profitability: NOT VERIFIED, no authorized official M20 run.
- Optimization: offline CI job success PASS, synthetic parity fingerprint not independently recomputed this run; whole-pipeline speedup NOT VERIFIED.

## Safe next steps
KRX owner to independently reconcile the 27 invalid OHLC rows against official source and session/security status, without bypassing veto. Chronology owner to investigate failed auto-anchor job using read-only logs and independent temporal proof. DART owner to establish original filing, exact 3-month consolidated line and available-at without correction backfill. Optimization owner may run synthetic offline parity/safety tests only, with cache keyed to approved source/data/code/Frozen/runtime/evidence SHA-256, fail-closed; parallelize read-only postprocessing only. Preserve Frozen H5/M20 horizon20/purge20, WF504/126/126, independent Holdout, NO_TRADE and ORDERING=false policy. No economic backtest, strategy search, PR merge, deployment, live order, funds move, permission change or Champion promotion.
