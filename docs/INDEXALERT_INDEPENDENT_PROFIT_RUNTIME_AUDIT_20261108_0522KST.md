# IndexAlert independent audit — 2026-11-08 05:22 KST

Scope: read-only GitHub/Railway source verification; isolated documentation only. No live orders, deployment, merge, workflow change, M20 run, market backtest, or model exploration.

## Exact PR HEADs (direct GitHub fetch)
- #412 OpenDART: bf3d9514a87c53b1775e22ec9ba7711f6cecc49f — OPEN/Draft
- #413 offline optimization: f003ef6247e16fcc71bd3b1b20cd4904c4d984c0 — OPEN/Draft
- #414 integration: 18c5418d9684d1717df58261ea27f28e514385b2 — OPEN/Draft
- #418 one-runner: 2f98401cc50a6c6a25808a98516efd5bf0c944ee — OPEN/Draft
- #420 KRX: fab3cbbd63a951a4e081f9e7f08c1391ca308581 — OPEN/Draft
- #422 KRX: c14857620973531013799e44625d43080904fd5f — OPEN/Draft
- #423 KRX: 0e38004363cac9fc4475556b3a1c445de9af407f — OPEN/Draft
Research and development branches exist (search_branches), but their exact current HEADs were not independently resolved in this run. Prior observed research df474df348f22aa38b1dedaa59fcff66e548b406 and development 1e6367d2863a86c3470da13d81a955d277eba485 are historical, not freshly certified.

## GitHub Actions direct job evidence
- #38381997417 and #38382214223: each 6/6 success.
- #38419111311: 6/6 success.
- #38419649711: 1/1 success (one-runner synthetic offline).
- #38419439742: 2/2 success (OpenDART offline candidate diff).
- #41515392296: auto-anchor FAILURE in 'Fetch today's public hash-only prospective payload'; validation SKIPPED.
The 34-case SHA-256 5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34, synthetic 28, adversarial 13 and 2.9656s/2.6209s measurements are prior evidence, NOT independently recomputed from artifacts in this run. Full CI and official backtest speedup NOT VERIFIED.

## Railway production direct evidence
Project d1c1a050-b7d6-41ce-b300-13c20f82a20a; production 83d5840b-270e-4d3f-a941-a37fd4a55ff7.
- PIT rebuild deployment 8b354fc1-cfb2-4ef0-863e-67f7f5dda2b5 SUCCESS, replica 1 running.
- Runtime deployment eaaa9f67-b9f2-41d2-832c-7d6fad9b9b00 SUCCESS, replica 1 running.
- Kiwoom real-readonly deployment a77fb922-b679-4d88-92c4-03054ec579cd SUCCESS, replica running 0, crashed 1: service health FAIL despite deployment SUCCESS.
- db-query-readonly: offline, one critical notification.
- Pending staged patch e113dacb-6705-4416-9997-dc694539d382 contains empty changes[]; do not apply.
- PIT/KRX/real-readonly deploy log query since 2026-11-07 19:00Z returned zero records; this cannot establish recovery or absence of faults. Previous 803 rows / 27 invalid OHLC / 27 zero activity and missing manifest remain unresolved historical evidence.

## Independent admission gates
- Offline software CI: PASS for the specific historical runs, not profitability approval.
- Original-filing + public available-at PIT: NOT VERIFIED.
- 2021/2022 first-three-month consolidated operating-profit period/correction lineage: NOT VERIFIED.
- Historical corporate/security mapping: NOT VERIFIED.
- KRX official calendar, trade state, corporate actions, fill feasibility, tax/cost: NOT VERIFIED.
- NetEV, PF, CAGR, MDD, ES95/99, concentration and time-slice robustness: NOT VERIFIED.
- Chronology anchor run: FAIL.
- M20 profitability admission: NO-GO; ORDERING=false; H5 frozen holdout consumed, not reusable.
- Optimization: synthetic offline-only, no real acceleration approval. Cache fail-closed on all source/data/code/policy/runtime/evidence SHA-256, parallelize read-only postprocessing only.

Next: independently validate official filing-time/period lineage, KRX original calendar/status and tradeability; repair chronology anchor via responsible owner (do not edit blocked workflows), independently compare SHA-bound immutable artifacts, then consider approval. No gate relaxation or experiment before evidence.
