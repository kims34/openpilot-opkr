# IndexAlert independent profitability/runtime audit — 2026-11-04 18:24 KST

Read-only evidence refresh; NOT a PIT approval or economic backtest.

## Exact refs
- research `index-alert-research-v1`: `df474df348f22aa38b1dedaa59fcff66e548b406`
- development `index-alert-position-regen-fix-v1`: `1e6367d2863a86c3470da13d81a955d277eba485`
- PR #412 `bf3d9514a87c53b1775e22ec9ba7711f6cecc49f`; #413 `f003ef6247e16fcc71bd3b1b20cd4904c4d984c0`; #414 `18c5418d9684d1717df58261ea27f28e514385b2`; #418 `2f98401cc50a6c6a25808a98516efd5bf0c944ee`.
- KRX #420 `fab3cbbd63a951a4e081f9e7f08c1391ca308581`; #422 `c14857620973531013799e44625d43080904fd5f`; #423 `0e38004363cac9fc4475556b3a1c445de9af407f`. All seven PRs open/draft at this read.
- PR #414 gate `docs/INDEXALERT_PROFITABILITY_INTEGRATION_GATE_2026-10-13.md` blob SHA-1 `984c933651f39f1ee9e26a1d7ac3893aaa5335be`.
- Independent audit branch before this write: `501a8d4fb6a9cb3a0f137db39571b6c72bd79c9f`.

## Actions (job conclusions checked now)
- 38381997417: 6/6 success; 38382214223: 6/6 success; 38419111311: 6/6 success; 38419649711: 1/1 success; OpenDART 38419439742: 2/2 success.
- Chronology 41515392296: auto-anchor failure, validation skipped.
- Previously reported 34-case SHA `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34`, 13 adversarial mocks, 28 synthetic checks and 2.9656s/2.6209s (1.1315x regression-phase) are **historical claims, not independently recalculated this run**. Overall CI speedup NOT VERIFIED.

## Railway production read-only
- KRX worker latest deployment `16c93d7c-7cd0-4d84-a327-298d2805376c` SUCCESS, 2026-10-12 13:07 UTC, commit `1e6367d2863a86c3470da13d81a955d277eba485`.
- PIT rebuild latest deployment `8b354fc1-cfb2-4ef0-863e-67f7f5dda2b5` SUCCESS, 2026-10-10 10:28 UTC, commit `e57054ecdb3e734ced3c9a981b887d9b5fc60f97`.
- Runtime latest deployment `eaaa9f67-b9f2-41d2-832c-7d6fad9b9b00` SUCCESS, 2026-10-05 20:34 UTC, commit `8a68b01bca5d551d083ccda263df38d86fa54166`.
- 2026-11-04 08:00–09:25 UTC: KRX and PIT deploy log queries returned 0 entries; not evidence of source correctness. Runtime logs through 09:23:57 UTC show USDKRW Yahoo quote and `3.2_safe_fallback` probability path, unrelated to historical market PIT.

## Independent admission verdict
- KRX private 1565/1565 weekday raw pair storage integrity: historical PASS only. Official calendar, 90 uncertain sessions, 12003 zero-activity exclusions, corporate actions, symbol/entity mapping, trading states, realistic fills and taxes: NOT VERIFIED / FAIL-CLOSED.
- OpenDART first-filed original-filing, public available-at, 2021/2022 first-three-month consolidated operating-profit period and correction lineage: NOT VERIFIED / FAIL-CLOSED. SGML candidate rows do not prove meaning or timing.
- Frozen H5 failed/consumed holdout and dynamic result must not be reused; M20 horizon20/purge20, WF504/126/126 and all frozen policies unchanged.
- NetEV, PF, CAGR, MDD, ES95/99, return concentration, temporal robustness, annual risk-adjusted after-tax net profit: NOT EVALUABLE. M20 PIT/economics RUN: NO-GO.
- PR #413/#418 synthetic offline parity: limited CI PASS only. Cache must fail closed on independent approved input/data/code/frozen-policy/runtime/approval SHA-256; parallelise read-only postprocessing only. No dependent training or capital-transition parallelisation.
- ORDERING=false. No orders, account/credential changes, promotion, deployment, merges or workflow edits performed.

## Next safe work
Independently verify official filing timestamps and period/correction lineage, historical KRX official calendar/status/entity/action provenance and executable costs/taxes with source hashes; do not run M20 economic tests before source PIT admission. Keep any further audit writes isolated and avoid other workstreams' code.
