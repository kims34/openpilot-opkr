# IndexAlert independent profitability and isolated runtime audit — 2026-11-05 22:21 KST

Read-only evidence snapshot. This branch forks prior independent audit commit `a816e92dd16de09cd351ffc3bce37adc40074334`; no other specialist branch, workflow, live service, strategy, holdout, or PR changed.

## GitHub evidence inspected in this run
- Branch search confirms `index-alert-research-v1` and `index-alert-position-regen-fix-v1` exist, but **current branch HEAD SHA not independently obtained this run**. Previous audited heads `df474df348f22aa38b1dedaa59fcff66e548b406` and `1e6367d2863a86c3470da13d81a955d277eba485` are historical only.
- PR search returned #412, #413, #418, #422, #423 and #424; #414 and #420 not conclusively returned in the scoped result, and no exact PR HEAD or Draft flag is independently verified. PR search body is historical author assertion, not current source authority.
- Fetch of `docs/INDEXALERT_PROFITABILITY_INTEGRATION_GATE_2026-10-13.md` on research ref returned 404; guessed integration ref also 404. **#414 document text NOT VERIFIED**; do not infer absence on its actual PR head.
- Direct GitHub Actions job reads: #38381997417 6/6 SUCCESS; #38382214223 6/6 SUCCESS; #38419111311 6/6 SUCCESS; #38419649711 1/1 SUCCESS; #38419439742 2/2 SUCCESS; chronology #41515392296 auto-anchor FAILURE / validation SKIPPED.
- PR #413 body describes additional offline source/cache TOCTOU repair #38466023642 6/6, later strict-cache receipt #38498552499 6/6 and incompatible #418 merged-context check #38486028854 FAIL due archived implementation SHA mismatch. **These later CI claims were read from PR body, not independently checked as jobs this run**. Do not silently re-pin or merge.
- Historical immutable 34-case outcome SHA-256 `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34`, synthetic 13/28, and 2.9656s vs 2.6209s (1.1315x regression phase) remain prior evidence, not freshly recomputed. Whole CI and real backtest acceleration NOT VERIFIED.

## Railway production directly read
Project `d1c1a050-b7d6-41ce-b300-13c20f82a20a`, environment `83d5840b-270e-4d3f-a941-a37fd4a55ff7`.
- PIT rebuild deployment `8b354fc1-cfb2-4ef0-863e-67f7f5dda2b5`: deployment SUCCESS, but **latest log 2026-11-05T13:16:14.270192838Z** reports `status=FAIL_CLOSED`, `error_reason_code=COMMON_OHLC_NONPOSITIVE`, 803 common-stock rows, 27 nonpositive OHLC, 27 zero volume/value, zero all-zero OHLC, `session_manifest_sha256=null`, `fresh_alpha_observation_admitted=false`, `ordering=DISABLED`. Repeated at 13:01Z and earlier. Source failure session 2026-09-28 per prior log; exact session not separately printed in this run's compact parse.
- KRX historical worker deployment `16c93d7c-7cd0-4d84-a327-298d2805376c` SUCCESS; zero deploy-log entries in queried period (since 12:00 UTC) is **not** official calendar, stock-state, PIT or execution verification.
- Runtime deployment `eaaa9f67-b9f2-41d2-832c-7d6fad9b9b00` SUCCESS. Runtime log at 13:20-13:21Z shows Yahoo USD/KRW fallback after Investing HTTP errors and QQQ/SPY premarket values. These are operational display observations, **not approved PIT source**.
- Deployment listing is not exhaustive for every service. Replica status, latest Backend/Push and independent KRX private source raw receipts were not verified in this run.

## Independent PASS/FAIL/NOT VERIFIED
| Gate | Verdict | Basis |
|---|---|---|
| Reject invalid prospective KRX input / preserve ordering denial | PASS | Direct 13:16Z fail-closed runtime evidence |
| Prospective 2026-09-28 source-session admission | FAIL | Repeated 27 nonpositive OHLC rows; manifest absent |
| KRX historical raw-pair integrity | HISTORICAL PASS ONLY | Previously reported 1565/1565; no fresh private rehash |
| Official KRX session/calendar/status/corporate action/fill feasibility | NOT VERIFIED | No independently authenticated row-level comparison |
| Original OpenDART filing, exact public available-at, 2021/2022 consolidated first-three-month operating-profit lineage | NOT VERIFIED | Candidate row matches do not prove meaning/time |
| Historical issuer/security mapping | NOT VERIFIED | No independently admitted point-in-time mapping |
| NetEV/PF/CAGR/MDD/ES95/99, after-tax annual risk-adjusted net return, concentration and temporal robustness | NOT VERIFIED | No admitted PIT or authorized M20 run |
| Offline test runner parity | PASS for job conclusions only | Exact historical SHA/parity artifact not freshly recomputed |
| Whole CI or actual market backtest acceleration | NOT VERIFIED | Regression-only timing not end-to-end |
| M20 | NOT EVALUABLE / NO-GO | Source and chronology gates unresolved |

## Immutable constraints and next steps
- Frozen H5, M20 horizon20/purge20, WF504/126/126, PIT/Purged/CPCV/independent Holdout/Champion/Top3/NO_TRADE, costs/taxes/execution/risk/promotion unchanged. H5 consumed holdout and Dynamic post-hoc findings never reused. ORDERING=false.
- Cache may be used only with independently admitted source, data, code, Frozen policy, runtime and approval evidence SHA-256 equality; mismatch fail-closed. Parallel only independent read-only postprocessing; never dependent retraining or capital transition.
- Next: authenticate exact 27 original KRX rows against official exchange session/status/corporate-action originals and preserved raw SHA; independently obtain #414 actual PR HEAD/file and verify OpenDART available-at/2021-22 correction lineage; recheck #413/#418 conflicting SHA-context CI with exact jobs and artifacts. Until admission: synthetic offline policy/software checks only.
- No workflow changes, bypass, production deployment, PR merge, model/performance search, official backtest, orders, funds, permissions or Champion promotion performed.
