# IndexAlert 독립 수익성·오프라인 최적화 감사 — 2026-11-07 03:20 KST

## Evidence scope
- Repository: kims34/openpilot-opkr. Branch names index-alert-research-v1 and index-alert-position-regen-fix-v1 independently located via branch search; **exact current branch HEAD NOT VERIFIED** (branch-search response does not return SHA). Previous known research df474df348f22aa38b1dedaa59fcff66e548b406, development 1e6367d2863a86c3470da13d81a955d277eba485 are historical, not current assertions.
- Integration document at pinned PR #414 commit 18c5418d9684d1717df58261ea27f28e514385b2 fetched directly; historical blob 984c933651f39f1ee9e26a1d7ac3893aaa5335be. **Current PR HEAD and merge status NOT VERIFIED in this run**. PR #412/#413/#418 and KRX #420/#422/#423 current status likewise NOT VERIFIED.
- GitHub Actions 41515392296: auto-anchor FAILURE at step 5 'Fetch today's public hash-only prospective payload'; validation SKIPPED. Job log inspected; precise root cause not yet independently isolated. Chronology/PIT FAIL-CLOSED.
- GitHub Actions 38419649711: one-runner-offline-comparison SUCCESS 1/1. This is offline-only parity, not official end-to-end acceleration.
- GitHub Actions 38419439742: offline-row-security-tests and official-safe-candidate-row-diff SUCCESS 2/2. Row signature does not establish original filing meaning, 2021/2022 consolidated three-month period or available-at.
- Historical Actions 38381997417/38382214223 6/6 each, 38419111311 6/6, pinned 34-case SHA 5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34 and synthetic 28 / regression phase 1.1315x are historical reported evidence; not re-executed this run.
- Railway project d1c1a050-b7d6-41ce-b300-13c20f82a20a, production 83d5840b-270e-4d3f-a941-a37fd4a55ff7. PIT rebuild deployment 8b354fc1-cfb2-4ef0-863e-67f7f5dda2b5 SUCCESS; KRX historical worker 16c93d7c-7cd0-4d84-a327-298d2805376c SUCCESS; runtime eaaa9f67-b9f2-41d2-832c-7d6fad9b9b00 SUCCESS. PIT and KRX worker had zero returned deploy entries for 2026-11-06 16:00Z onward: latest quality improvement NOT VERIFIED. Runtime logs through 2026-11-06 18:20Z show Investing USD/KRW HTTPError and Yahoo fallback; unrelated to M20 economic approval.
- Prior observed PIT common-stock 803, invalid OHLC 27 and FAIL_CLOSED are historical evidence only, not freshly reproduced.

## Gate decisions
- Raw KRX 2017–2022 1565/1565 weekday-pair storage hash integrity: historical PASS (does not imply official market-calendar/market-status verification).
- Latest source quality: NOT VERIFIED (historical OHLC FAIL). Fail-closed safety: historical PASS, current state NOT VERIFIED.
- Original OpenDART filing/public available-at, 2021/2022 consolidated 3-month operating-profit period/correction lineage, historical corp/security mapping: NOT VERIFIED.
- Official KRX calendar/status/corporate actions/executability, fees/taxes: NOT VERIFIED.
- NetEV/PF/CAGR/MDD/ES95/ES99, concentration, temporal robustness, independent Holdout: NOT VERIFIED; M20 economic RUN **NO-GO**.
- Offline CI isolated runner: historical PASS; actual whole-CI/official backtest speedup NOT VERIFIED.
- H5 failed/consumed holdout and Dynamic remain disqualified for independent reuse; Frozen H5, M20 horizon20/purge20, WF504/126/126, CPCV, NO_TRADE and ORDERING=false unchanged.

## Next safe actions
1. Read-only inspect chronology anchor step-5 error tail and source authority; do not change workflow or bypass security blocks.
2. Independently bind exact current branch/PR HEAD and raw source SHA before comparing evidence; distinguish historical pinned evidence from live state.
3. Obtain original-filing chronology and official KRX calendar/trading/corporate action evidence from designated owners; no M20 run until independent source gate PASS.
4. In isolated offline-only track, compare fixed 34-case SHA and synthetic controls with policy-preserving fail-closed cache evidence; no model search, no performance tests, no deployment/merge/order.
