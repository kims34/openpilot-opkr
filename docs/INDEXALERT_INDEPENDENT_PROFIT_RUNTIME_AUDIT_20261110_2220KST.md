# IndexAlert independent profitability/runtime audit — 2026-11-10 22:20 KST

Scope: read-only GitHub PR metadata, specified Actions job results, Railway production inventory/health/runtime logs. No production, model, workflow or trading changes. This audit branch was created from PR #414 HEAD 18c5418d9684d1717df58261ea27f28e514385b2; this is NOT proof that research/development HEADs are unchanged.

## GitHub immutable evidence
- PR #412 OPEN Draft unmerged HEAD bf3d9514a87c53b1775e22ec9ba7711f6cecc49f
- PR #413 OPEN Draft unmerged HEAD f003ef6247e16fcc71bd3b1b20cd4904c4d984c0
- PR #414 OPEN Draft unmerged HEAD 18c5418d9684d1717df58261ea27f28e514385b2
- PR #418 OPEN Draft unmerged HEAD 2f98401cc50a6c6a25808a98516efd5bf0c944ee
- KRX PR #420 HEAD fab3cbbd63a951a4e081f9e7f08c1391ca308581; #422 HEAD c14857620973531013799e44625d43080904fd5f; #423 HEAD 0e38004363cac9fc4475556b3a1c445de9af407f; all OPEN Draft unmerged.
- GitHub Actions run 38381997417, 38382214223, 38419111311: 6/6 jobs completed success each. 38419649711: 1/1 completed success. 38419439742: 2/2 completed success. Source: https://github.com/kims34/openpilot-opkr/actions/runs/38419649711
- 34-case SHA-256 claimed prior: 5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34; NOT independently recalculated this run. 13 adversarial mocks, 28 synthetic cases and 1.1315x regression-phase benchmark are prior claims, not new performance verification. Full CI and official backtest speed: NOT VERIFIED.
- Research branch index-alert-research-v1 and development branch index-alert-position-regen-fix-v1 current HEAD: NOT VERIFIED in this run; do not substitute prior reported SHAs for fresh observations. PR #414 document blob SHA prior claim 984c933651f39f1ee9e26a1d7ac3893aaa5335be: NOT independently checked this run.

## Railway production evidence
Project d1c1a050-b7d6-41ce-b300-13c20f82a20a, production environment 83d5840b-270e-4d3f-a941-a37fd4a55ff7. Inventory reports staged=null, while environment health reports empty staged patch e113dacb-6705-4416-9997-dc694539d382; no changes applied.
- PIT rebuild deployment 8b354fc1-cfb2-4ef0-863e-67f7f5dda2b5 SUCCESS; replica 1 running/1. Runtime eaaa9f67-b9f2-41d2-832c-7d6fad9b9b00 SUCCESS; replica 1/1.
- PIT deploy logs from 2026-11-10 11:00Z through 13:16Z: 10 records at approximately 15-minute intervals reporting KRXProspectiveOpenAPISourceError / COMMON_OHLC_NONPOSITIVE, independent source/chronology/model admission false, no fresh alpha admission. Repeated source error: FAIL for prospective data ingest. Prior observed 27/803 OHLC anomaly requires independent source-level resolution; latest log excerpts were truncated and do not independently recount the 27.
- KRX worker deployment 16c93d7c-7cd0-4d84-a327-298d2805376c SUCCESS but replica 0 running / 0 crashed / 1 total: execution health NOT VERIFIED; logs since 11:00Z: zero.
- Kiwoom real readonly deployment a77fb922-b679-4d88-92c4-03054ec579cd SUCCESS but replica 0 running / 1 crashed / 1 total: runtime FAIL; logs since 11:00Z: zero.
- Backend and Push offline; db-query-readonly offline with one critical issue. No deployment or restart performed.

## Gate assessment
PASS limited to specified historical GitHub Actions job success and previously documented 1565/1565 private weekday KRX raw-pair storage integrity (historical evidence only; not rehashed this run).
FAIL: current prospective OHLC source ingest (COMMON_OHLC_NONPOSITIVE), Kiwoom readonly replica crashed.
NOT VERIFIED: original-filing original/adjustment semantic and exact public available-at/PIT; 2021/2022 first three-month consolidated operating-profit period/correction lineage; historical issuer/ticker mapping; official KRX session/halts/corporate actions/tradability/execution and tax/cost evidence; independent post-cost-and-tax annual risk-adjusted NetEV, PF, CAGR, MDD, ES95/99, profit concentration, temporal robustness; 34-case fixed SHA reproduction; actual official end-to-end acceleration.
M20 NO-GO. H5 consumed/failed holdout and dynamic outputs cannot be reused as independent evidence. Frozen H5/M20 horizon20 purge20, WF504/126/126, PIT/labels/Purged/CPCV/independent Holdout/Champion/Top3/NO_TRADE and risk/cost/tax/promotion gates unchanged. ORDERING=false remains required; current live environment variable value NOT VERIFIED.

## Separate isolated optimisation track
PR #413 and #418 are read-only and unmerged. Allowed next work: independently reproduce fixed-case SHA in an isolated synthetic-only runner, fail-closed cache key verification against independently approved source/data/code/frozen policy/runtime/evidence hashes, parallelise only read-only post-processing. Never parallelise dependent retraining or capital transitions; no market returns/performance search or M20 economics until official source PIT approval.

## Next safe actions
1. Independent OpenDART original-filing/public-available-at and 2021/2022 period-lineage approval with original SHA evidence.
2. Official KRX calendar, trading status, corporate actions, fillability and cost/tax provenance; investigate repeated OHLC anomaly without admitting contaminated observations.
3. Diagnose crashed Kiwoom readonly replica without restarting, changing permissions or deploying.
4. Recompute fixed synthetic-case SHA and CI parity from immutable inputs only.
5. Only after all independent source PIT gates PASS, request explicit approval for any M20 economic run; never infer trading or Champion promotion permission.
