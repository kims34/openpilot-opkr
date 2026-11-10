# IndexAlert independent read-only audit — 2026-11-10 21:25 KST

Scope: profitability integration gate and separately isolated offline-only runtime optimization. No strategy/model search, market backtest, PIT promotion, workflow change, merge, deployment, trading or account mutation.

## Exact source pins
- Research `index-alert-research-v1`: `df474df348f22aa38b1dedaa59fcff66e548b406` (GitHub compare base).
- Development `index-alert-position-regen-fix-v1`: previously pinned `1e6367d2863a86c3470da13d81a955d277eba485`; current HEAD not separately fetched in this run. GitHub compare diverged: development ahead 1148, behind 281, merge-base `c490974ff6619bb978dc6f83f9c24f2c46622f85`.
- OPEN/Draft/unmerged PR HEADs: #412 `bf3d9514a87c53b1775e22ec9ba7711f6cecc49f`; #413 `f003ef6247e16fcc71bd3b1b20cd4904c4d984c0`; #414 `18c5418d9684d1717df58261ea27f28e514385b2`; #418 `2f98401cc50a6c6a25808a98516efd5bf0c944ee`; KRX #420 `fab3cbbd63a951a4e081f9e7f08c1391ca308581`; #422 `c14857620973531013799e44625d43080904fd5f`; #423 `0e38004363cac9fc4475556b3a1c445de9af407f`.
- PR #414 gate file `docs/INDEXALERT_PROFITABILITY_INTEGRATION_GATE_2026-10-13.md` blob SHA `984c933651f39f1ee9e26a1d7ac3893aaa5335be` read at PR HEAD.

## CI evidence (read-only API jobs, latest attempts)
- 38381997417 6/6 success; 38382214223 6/6 success; 38419111311 6/6 success; 38419649711 1/1 success; 38419439742 2/2 success. Exact jobs enumerated through GitHub connector. This PASS applies only to offline CI job conclusions, not source PIT or financial performance.
- User-provided 34-case SHA256 `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34`, 13 adversarial mocks and 28 synthetic tests are historical claims, NOT independently recomputed this run.
- One-runner serial 2.9656s vs concurrent suite 2.6209s (historical 1.1315x regression-phase); total CI and official backtest acceleration NOT VERIFIED.

## Railway production, live status
Project `d1c1a050-b7d6-41ce-b300-13c20f82a20a`, environment `83d5840b-270e-4d3f-a941-a37fd4a55ff7`.
- PIT rebuild deployment `8b354fc1-cfb2-4ef0-863e-67f7f5dda2b5` SUCCESS, replica running 1/1.
- Runtime `eaaa9f67-b9f2-41d2-832c-7d6fad9b9b00` SUCCESS, replica running 1/1.
- KRX historical worker `16c93d7c-7cd0-4d84-a327-298d2805376c` SUCCESS, running 0/1 (not sufficient to conclude continuous runtime health).
- Kiwoom real read-only `a77fb922-b679-4d88-92c4-03054ec579cd` SUCCESS deployment but running 0/1 and crashed 1/1: runtime FAIL despite 'online' label.
- backend, push, db-query-readonly offline; db-query-readonly critical count 1.
- pending staged patch `e113dacb-6705-4416-9997-dc694539d382` changes=[]; untouched.
- PIT deploy logs 2026-11-10 11:00–12:16 UTC: six 15-minute events, `COMMON_OHLC_NONPOSITIVE`, common-stock rows 803, nonpositive 27, zero-volume/value 27, source_failure_session 2026-09-28, `FAIL_CLOSED`, `ordering=DISABLED`, all independent source/chronology/model approvals false, live orders/funds/permissions false. KRX and Kiwoom same-window logs 0 records (not proof of healthy operation).

## Independent admission verdict
- Original-filing OpenDART raw SGML 15 candidate rows and adjacent signature: historical limited extraction PASS; correct 2021/2022 first three-month consolidated operating profit, period/filing correction lineage, exact public available-at/PIT NOT VERIFIED.
- KRX private 2017–2022 weekday raw pairs 1565/1565: historical storage-integrity PASS only; official calendar, 90-day classification, 12003 zero-activity rows, historical security identity, status, corporate actions, tradeability, fill/cost/tax NOT VERIFIED and fail-closed.
- H5 consumed holdout and historical fragility: NO-GO, no retrospective tuning/reuse. M20 source/PIT and profitability RUN: NOT AUTHORIZED / NO-GO.
- After-cost and after-tax NetEV, PF, CAGR, MDD, ES95/99, concentration, date-cluster LCB, time robustness: NOT VERIFIED (no official economic experiment performed).
- Frozen H5, M20 horizon20/purge20, WF504/126/126, independent Holdout, Champion/Top3/NO_TRADE, costs/tax/execution/risk/promotion unchanged. Ordering disabled per observed PIT logs; do not infer global env variable independently verified.

## Safe next actions / blockers
1. Source owners must independently attest original-filing consolidated exact three-month operating profit and PIT/available-at/correction lineage for 2021 and 2022, with original SHA and official timing evidence.
2. KRX owner must independently resolve official market calendar/status, corporate actions, historical symbol mapping, 90-day classification, 27 OHLC veto and 12003 zero-activity entries; do not simply drop problematic rows.
3. Separately isolate synthetic offline-only optimizer tests, compare exact deterministic SHA, verify cache fail-closed binding to source/data/code/Frozen/runtime/approval evidence SHA-256, parallelize read-only postprocessing only. Do not parallelize dependent retraining/capital transitions.
4. Investigate Kiwoom read-only crashed replica and db-query-readonly critical via read-only diagnosis; no deployment or permission mutation.
5. Maintain M20 NO-GO until all source/PIT/market gates independently PASS; no official market return or economic experiments now. No merges of #413/#414/#418.

Sources: https://github.com/kims34/openpilot-opkr/pull/414 ; https://github.com/kims34/openpilot-opkr/pull/413 ; https://github.com/kims34/openpilot-opkr/pull/418 ; https://github.com/kims34/openpilot-opkr/actions/runs/38419649711 ; https://github.com/kims34/openpilot-opkr/actions/runs/38419439742 .
