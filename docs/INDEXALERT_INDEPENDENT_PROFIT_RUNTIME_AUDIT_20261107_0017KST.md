# IndexAlert independent profitability/runtime audit — 2026-11-07 00:17 KST

Scope: read-only inspection; offline-only optimization evidence; no market return computation, no economic M20 run, no merges/deployment/order/authority changes.

## Current directly queried evidence
- GitHub branch discovery: `index-alert-research-v1` and `index-alert-position-regen-fix-v1` exist. **Exact current branch HEAD SHA NOT VERIFIED** by branch search; do not substitute historical SHA.
- PR #414 integration gate was read at explicitly pinned commit `18c5418d9684d1717df58261ea27f28e514385b2` (not independently established as current PR HEAD). It explicitly states M20 no-run, KRX stored SHA integrity != tradability, original DART PIT unresolved, H5 no-go.
- GitHub Actions jobs independently fetched: #38381997417 6/6 success; #38382214223 6/6 success; #38419111311 6/6 success; #38419649711 1/1 success; OpenDART #38419439742 2/2 success; chronology anchor #41515392296 auto-anchor **failure**, validation **skipped**. These CI successes only certify their own offline/synthetic jobs, not official source PIT or full backtest acceleration.
- Historical fixed 34-case SHA256 `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34` and 2.9656s serial vs 2.6209s concurrent are **prior recorded evidence**, not re-hashed/rebenchmarked this run.
- Railway project IndexAlert `d1c1a050-b7d6-41ce-b300-13c20f82a20a`, production `83d5840b-270e-4d3f-a941-a37fd4a55ff7`: PIT rebuild deployment `8b354fc1-cfb2-4ef0-863e-67f7f5dda2b5` SUCCESS, code commit `e57054ecdb3e734ced3c9a981b887d9b5fc60f97`; KRX historical worker deployment `16c93d7c-7cd0-4d84-a327-298d2805376c` SUCCESS, commit `1e6367d2863a86c3470da13d81a955d277eba485`. Deployment success is not proof of PIT.
- PIT deploy logs 2026-11-06 23:01–23:46 KST: repeated `COMMON_OHLC_NONPOSITIVE`, `common_stock_rows=803`, `nonpositive_ohlc_rows=27`, `zero_volume_value_rows=27`, `source_failure_session=2026-09-28`; `FAIL_CLOSED`, `fresh_alpha_observation_admitted=false`, `live_order_authorized=false`, `ordering=DISABLED`, `session_manifest_sha256=null`. **Data-quality FAIL; fail-closed safety PASS.** Note timestamps are UTC in provider logs; this report translates +09:00.
- KRX worker latest selected time-window logs: no entries, therefore recent official state/tradability improvement NOT VERIFIED.
- Railway runtime logs include USDKRW Investing HTTP errors with Yahoo fallback. Not evidence of M20 source admission.

## Gate disposition
- OpenDART original filing, exact public available-at, 2021/2022 first 3-month consolidated operating profit period/correction lineage: **NOT VERIFIED**. Historical 15 candidate rows/adjacent signatures do not establish original semantic PIT.
- Historical corp/security mapping, official KRX calendar/trading status/corporate actions/fillability, fees/tax: **NOT VERIFIED**. 1565/1565 historical weekday raw-pair SHA integrity remains prior PASS only for storage, not tradability.
- Frozen H5 holdout: prior failure/consumed, no independent reuse. M20 horizon20/purge20, WF504/126/126 and Champion/Top3/NO_TRADE policy unchanged.
- NetEV, PF, CAGR, MDD, ES95/99, return concentration, temporal robustness, annual risk-adjusted net profitability: **NOT VERIFIED; M20 NO-GO**.
- PR #413/#418 offline regression job success: **PASS for queried job conclusions**; total CI and official PIT backtest speedup **NOT VERIFIED**.
- Cache remains fail-closed unless approved independent source/data/code/Frozen/runtime/approval evidence SHA256 all match; only independent read-only post-processing parallelizable; dependent retraining/capital transition serial.
- ORDERING=false policy preserved; production variable value not modified or independently read.

## Next independent checks
1. Retrieve full current branch/PR HEAD and exact blob SHA using authoritative ref resolution; do not label historical pinned SHAs as latest.
2. Investigate failed chronology anchor job using original job logs; compare public filing available-at and original SGML period/correction lineage with exact official receipt evidence.
3. Compare the 27 rejected OHLC source records with official KRX status and corporate actions privately, without whitelist-by-exclusion.
4. Continue synthetic offline policy/cache/parity tests only; do not run M20 returns or new model search until all source PIT gates pass.

No existing Work-owned code, workflows, PRs, Railway variables/deployments, orders or accounts were changed.
