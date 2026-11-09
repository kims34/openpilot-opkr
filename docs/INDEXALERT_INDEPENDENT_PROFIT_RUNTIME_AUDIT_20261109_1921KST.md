# IndexAlert independent profitability/runtime audit — 2026-11-09 19:21 KST

Read-only evidence review. No market-economic run, deployment, merge, order, permission change, or workflow edit. This document is not source/PIT approval.

## Exact refs checked
- research `index-alert-research-v1`: `df474df348f22aa38b1dedaa59fcff66e548b406`
- development `index-alert-position-regen-fix-v1`: `1e6367d2863a86c3470da13d81a955d277eba485`
- PR #412: `bf3d9514a87c53b1775e22ec9ba7711f6cecc49f`; #413: `f003ef6247e16fcc71bd3b1b20cd4904c4d984c0`; #414: `18c5418d9684d1717df58261ea27f28e514385b2`; #418: `2f98401cc50a6c6a25808a98516efd5bf0c944ee`; KRX #420: `fab3cbbd63a951a4e081f9e7f08c1391ca308581`, #422: `c14857620973531013799e44625d43080904fd5f`, #423: `0e38004363cac9fc4475556b3a1c445de9af407f`. All OPEN/Draft/unmerged at check.
- #414 gate file blob SHA `984c933651f39f1ee9e26a1d7ac3893aaa5335be`.
- Prior independent audit branch HEAD before write: `94ee08f875180d4021746c364e0b34e83068c027`.

## CI / software-only optimization
- Actions 38381997417, 38382214223, 38419111311: each 6/6 successful jobs. 38419649711: 1/1 success. OpenDART 38419439742: 2/2 success.
- Original 34-case SHA `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34`, 13 adversarial mocks, 28 synthetic cases, serial 2.9656s vs concurrent 2.6209s = 1.1315x regression-phase are **historical claims, not recomputed in this run**. Full CI / official backtest acceleration NOT VERIFIED.
- Chronology Action 41515392296 auto-anchor FAILURE, validation SKIPPED; retrieved job log shows HTTP 404. Root cause NOT VERIFIED.

## Railway production read-only
Project `d1c1a050-b7d6-41ce-b300-13c20f82a20a`, environment `83d5840b-270e-4d3f-a941-a37fd4a55ff7`.
- PIT rebuild replica running 1/1, runtime 1/1. Real readonly service `93074d5f-70b3-48e4-8671-a3c5b23daf7e` reports online/SUCCESS but running 0/crashed 1: runtime health FAIL. KRX worker running 0/crashed 0 of total 1: activity NOT VERIFIED. Backend/push offline; db-query-readonly offline with one critical.
- PIT deploy log timestamps 2026-11-09T09:30:20Z, 09:45:20Z, 10:00:31Z, 10:15:31Z: all `FAIL_CLOSED`, `COMMON_OHLC_NONPOSITIVE`; 803 common stock rows, 27 nonpositive OHLC rows and 27 zero-volume/value rows. `fresh_alpha_observation_admitted=false`, `live_order_authorized=false`. Rejected source admission FAIL, fail-closed safety PASS. Exact offending security rows and source reconciliation NOT VERIFIED.
- KRX worker and real readonly deploy logs returned 0 entries in 09:30–10:25Z window; absence of logs is not proof of health.
- `get_status.stagedChanges=null` while `environment_status.pendingWork` contains an empty staged patch `e113dacb-6705-4416-9997-dc694539d382`; left untouched.

## Gate decisions
- Original filing/public available-at PIT; 2021/2022 initial Q1 consolidated operating profit period and amendment lineage; historical entity/security mapping; official KRX calendar/status/corporate actions/execution feasibility; tax/fees; annual risk-adjusted net NetEV/PF/CAGR/MDD/ES95/ES99, concentration and temporal robustness: NOT VERIFIED. Historical 1565/1565 weekday pair integrity PASS only for storage, not tradability.
- H5 consumed/failed holdout and dynamic results must not be reused. M20 source PIT and profitability NO-GO. Frozen H5; M20 horizon20/purge20; WF504/126/126; holdout/champion/top3/NO_TRADE and costs/risk gates unchanged. ORDERING=false is required policy; **live variable not independently verified**.
- Only offline synthetic policy/software checks allowed. Cache only on matching independent approved original/data/code/frozen/runtime/evidence SHA-256, fail closed; only independent read-only postprocessing parallelizable.

## Next safe steps
1. Independently reconcile 27 rejected KRX rows against authoritative dated source receipts, without admitting observations.
2. Resolve chronology /anchor/latest 404 via read-only endpoint/manifest evidence, not workflow modification.
3. Restore verifiable original-filing chronology and mapping evidence; separately verify actual ORDERING setting via approved read-only access.
4. Keep M20 and economic runs blocked until independent approvals. No PR merge/deploy/real trading without explicit permission.
