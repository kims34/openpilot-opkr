# IndexAlert independent profitability / offline runtime audit — 2026-11-11 11:22 KST

## Scope and immutable authority
Read-only verification only, separate from research/development and all specialist workspaces. No trading, model search, M20 economics, holdout replay, merge, deployment, workflow modification, secrets, or capital movement. ORDERING=false required; actual environment value not independently read. Frozen H5 and M20 horizon20/purge20, WF504/126/126, PIT/labels/Purged/CPCV/independent holdout/Champion/Top3/NO_TRADE and costs/tax/NetEV/fill/risk/promotion thresholds unchanged. Consumed H5 holdout and Dynamic results cannot be retrospectively retuned or reused as independent holdout.

## Exact GitHub heads and provenance
- Research `index-alert-research-v1` HEAD **df474df348f22aa38b1dedaa59fcff66e548b406**: independently verified via compare to branch (identical, ahead 0, behind 0).
- Development `index-alert-position-regen-fix-v1` HEAD **1e6367d2863a86c3470da13d81a955d277eba485**: independently verified as compare base commit. Research relative to development is diverged, ahead 281, behind 1148.
- Draft OPEN unmerged PRs: #412 bf3d9514a87c53b1775e22ec9ba7711f6cecc49f; #413 f003ef6247e16fcc71bd3b1b20cd4904c4d984c0; #414 18c5418d9684d1717df58261ea27f28e514385b2; #418 2f98401cc50a6c6a25808a98516efd5bf0c944ee; KRX #420 fab3cbbd63a951a4e081f9e7f08c1391ca308581, #422 c14857620973531013799e44625d43080904fd5f, #423 0e38004363cac9fc4475556b3a1c445de9af407f. #418 is based on isolated #413 context and must not merge.
- PR #414 integration document `docs/INDEXALERT_PROFITABILITY_INTEGRATION_GATE_2026-10-13.md` was fetched at `refs/pull/414/head`. Its historical statements are not independent PIT approvals. Document blob SHA not recorded in this audit; no claim of recomputation.

## Direct CI observations (jobs conclusion only)
- https://github.com/kims34/openpilot-opkr/actions/runs/38381997417 6/6 SUCCESS
- https://github.com/kims34/openpilot-opkr/actions/runs/38382214223 6/6 SUCCESS
- https://github.com/kims34/openpilot-opkr/actions/runs/38419111311 6/6 SUCCESS
- https://github.com/kims34/openpilot-opkr/actions/runs/38419649711 1/1 SUCCESS
- https://github.com/kims34/openpilot-opkr/actions/runs/38419439742 2/2 SUCCESS
- https://github.com/kims34/openpilot-opkr/actions/runs/38498552499 6/6 SUCCESS
The historical 34-case regression SHA `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34`, 13 adversarial mocks, 28 synthetic additions and 21 later synthetic tests are reported historical evidence, **not recomputed from current artifacts**. PASS only for observed CI job completion. Historical single-runner serial 2.9656s vs concurrent 2.6209s = regression phase 1.1315x; later #413 serial 1.7114s vs parallel 2.5776s (parallel slower). Whole CI and official backtest acceleration NOT VERIFIED. Cache fail-closed unless independently approved source/data/code/Frozen policy/runtime/approval SHA-256 all match; parallelise read-only postprocessing only, not dependent retraining or capital transitions.

## Railway production read-only observations
Project d1c1a050-b7d6-41ce-b300-13c20f82a20a, environment 83d5840b-270e-4d3f-a941-a37fd4a55ff7. Latest deployment: PIT rebuild SUCCESS (8b354fc1-cfb2-4ef0-863e-67f7f5dda2b5), Runtime SUCCESS (eaaa9f67-b9f2-41d2-832c-7d6fad9b9b00), KRX worker SUCCESS (16c93d7c-7cd0-4d84-a327-298d2805376c, deployed commit 1e6367d...), Kiwoom real readonly SUCCESS (a77fb922-b679-4d88-92c4-03054ec579cd, commit 85bb6fd...), Backend FAILED, Push FAILED.
Runtime replicas 1/1, PIT replicas 1/1; KRX worker 0/1; Kiwoom real readonly 0 running, 1 crashed / 1 total (**runtime FAIL** notwithstanding latest deployment SUCCESS). Backend, Push, db-query-readonly offline; db-query-readonly has 1 critical. One staged Railway patch exists with **zero changes** (e113dacb-6705-4416-9997-dc694539d382); not applied. KRX/PIT/Kiwoom logs in 2026-11-11 00:00–02:25 UTC 0 entries. Runtime 81 returned log entries including Investing USDKRW HTTP failure and Yahoo fallback at 02:22 UTC, not PIT approval. Deployment SUCCESS != live healthy replica or official source lineage PASS.

## Independent gate matrix
| Gate | Verdict | Why |
|---|---|---|
| Historical 2017–2022 KRX 1565/1565 weekday source pair SHA storage | historical PASS only | Prior 2026-10-14 private evidence; not re-hashed in this run |
| KRX 90 source-empty days, 12003 zero-activity, invalid OHLC, official calendar/status, corporate actions, delistings, actual fills | NOT VERIFIED / FAIL-CLOSED | No independently approved exact official tradability mapping |
| OpenDART original filing vs corrections SGML 15 candidate rows | CI PASS for jobs, semantic/PIT NOT VERIFIED | 2021/2022 original 3-month consolidated operating income, reporting period, amendment lineage and exact public available-at not independently certified |
| Historical corporation/security identifier mapping | NOT VERIFIED | Missing independently approved point-in-time mapping |
| M20 PIT, official economic backtest, after-cost-and-tax NetEV/PF/CAGR/MDD/ES95/99, concentration, temporal robustness | NOT VERIFIED, NO-GO | Source gates unmet; no approved official run |
| Offline optimizer suite CI | PASS for job completion only | No current independent fixed-case digest recomputation |
| Full CI or real backtest speedup | NOT VERIFIED | Phase-only synthetic timings cannot support broader claim |
| Railway Kiwoom real readonly runtime | FAIL | 0 running / 1 crashed |
| ORDERING=false actual runtime config | NOT VERIFIED | Required policy retained; no secret/config read |

## Next permitted actions
1. Specialist source owners independently establish official original-filing exact period, public available-at and correction lineage for 2021 and 2022, and historic corp/security PIT mapping; immutable hashes and source provenance only, no private raw source publication.
2. KRX specialist validates official exact session set, halt/delist/corporate-action/tradability and fill-cost/tax evidence, keeps 90 unknown days and zero-activity excluded.
3. Optimization isolated owner may reverify 34-case SHA from immutable CI artifacts and synthetic safety checks; no new market returns or model exploration.
4. Re-evaluate M20 authorization **only after** independent source and fill gates PASS. No automatic Champion promotion, deployment, PR merges, or orders. Every high-impact action requires separate explicit approval.
