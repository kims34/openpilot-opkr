# IndexAlert independent profitability/runtime audit — 2026-11-04 22:24 KST

Scope: read-only GitHub/Railway verification. No M20 run, no performance/model exploration, no orders, no deployment/merge. This is not source PIT approval.

## GitHub
- [PR #412](https://github.com/kims34/openpilot-opkr/pull/412), [#413](https://github.com/kims34/openpilot-opkr/pull/413), [#414](https://github.com/kims34/openpilot-opkr/pull/414), [#418](https://github.com/kims34/openpilot-opkr/pull/418), KRX [#420](https://github.com/kims34/openpilot-opkr/pull/420), [#422](https://github.com/kims34/openpilot-opkr/pull/422), [#423](https://github.com/kims34/openpilot-opkr/pull/423): issue API state OPEN; draft flag and current PR HEAD not independently returned by this API call (NOT VERIFIED). Prior recorded #414 HEAD 18c5418d9684d1717df58261ea27f28e514385b2, #413 f003ef6247e16fcc71bd3b1b20cd4904c4d984c0, #418 2f98401cc50a6c6a25808a98516efd5bf0c944ee: historical only, not current HEAD confirmation.
- Gate file at historical #414 SHA read successfully; prior blob SHA-1 984c933651f39f1ee9e26a1d7ac3893aaa5335be not independently recomputed this cycle.
- [Actions 38381997417](https://github.com/kims34/openpilot-opkr/actions/runs/38381997417), [38382214223](https://github.com/kims34/openpilot-opkr/actions/runs/38382214223), [38419111311](https://github.com/kims34/openpilot-opkr/actions/runs/38419111311): each 6/6 jobs success; [38419649711](https://github.com/kims34/openpilot-opkr/actions/runs/38419649711) 1/1 success; [OpenDART 38419439742](https://github.com/kims34/openpilot-opkr/actions/runs/38419439742) 2/2 success. [Chronology 41515392296](https://github.com/kims34/openpilot-opkr/actions/runs/41515392296): anchor FAIL, validation SKIPPED.
- Historical 34-case SHA-256 5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34, synthetic 28 and 13 adversarial mocks, regression phase serial 2.9656s vs concurrent 2.6209s (1.1315x) are prior evidence, not rehashed or rerun. Full CI/real backtest speed NOT VERIFIED.
- Research/development branches historical HEAD df474df348f22aa38b1dedaa59fcff66e548b406 / 1e6367d2863a86c3470da13d81a955d277eba485; current HEAD NOT VERIFIED this cycle.

## Railway live read-only evidence
Project IndexAlert d1c1a050-b7d6-41ce-b300-13c20f82a20a, production. KRX worker deployment 16c93d7c-7cd0-4d84-a327-298d2805376c SUCCESS, deployed 2026-10-12, commit 1e6367d2863a86c3470da13d81a955d277eba485. KRX worker 2026-11-04 20:00–22:30 KST log window: zero entries (not proof of successful market-source validation).
PIT rebuild deployment 8b354fc1-cfb2-4ef0-863e-67f7f5dda2b5 SUCCESS, but deploy status is not PIT admission. In 2026-11-04 20:00–22:30 KST window, prospective runtime repeated COMMON_OHLC_NONPOSITIVE / FAIL_CLOSED, last sampled at 21:31 KST; 803 common-stock rows, 27 nonpositive OHLC, 27 zero-volume/value; source failure session 2026-09-28, session_manifest_sha256 null, independent source/model/chronology admission false, ORDERING DISABLED, live orders false. Runtime service has quote/fallback logs; those do not validate PIT.
Previous 1565/1565 weekday raw-pair integrity PASS is storage-only, not official calendar/trading status approval; 90-day uncertainty and 12003 zero-activity blocks remain.

## Independent gate verdict
- Synthetic offline software CI: limited PASS (job status only). Exact frozen-case SHA parity and actual whole-run acceleration: NOT VERIFIED this cycle.
- OpenDART original-filing public available-at, 2021/2022 first three-month consolidated operating income period and correction lineage: NOT VERIFIED / FAIL-CLOSED. Candidate-row signatures do not establish period semantics.
- Historical corp/security mapping, KRX official calendars/status/corporate actions, execution feasibility and tax/cost ledger: NOT VERIFIED.
- Frozen H5 holdout consumed; cannot independently reuse. M20 horizon20/purge20 WF504/126/126 and all Frozen policies unchanged. M20 NetEV/PF/CAGR/MDD/ES95/99/concentration/time robustness: NOT EVALUABLE / NO-GO.
- Cache must bind approved original/data/code/Frozen/runtime/evidence SHA-256 fail-closed; only read-only independent postprocessing parallelizable. No dependent retraining/capital-transition parallelism.
- Next: independently validate original filing timestamps/period lineage and private KRX official status/calendar, then independent SHA manifest; only after separate approval consider M20. No user action requested in this cycle.
