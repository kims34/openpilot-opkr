# IndexAlert independent profitability and runtime audit — 2026-11-11 10:24 KST

Scope: read-only GitHub Actions, branch comparison, Railway production inventory/status/logs. No market backtest, model search, order, deploy, merge, workflow change or champion promotion.

## GitHub evidence
- Development `index-alert-position-regen-fix-v1` HEAD: `1e6367d2863a86c3470da13d81a955d277eba485` (compare API base_commit).
- Research `index-alert-research-v1`: compare API says DIVERGED, research ahead 281 / behind 1148 relative to development; research HEAD SHA not returned in this call, hence NOT VERIFIED this run (previous audit recorded `df474df348f22aa38b1dedaa59fcff66e548b406`, not independently refreshed).
- PR #412/#413/#414/#418/#420/#422/#423: repository issue search returned empty, thus latest PR HEAD, draft state, and integration-gate blob SHA NOT VERIFIED this run. Do not interpret empty search as closure. The guessed integration branch was absent; no edits to PR-owned branches.
- Direct workflow jobs API: 38381997417 6/6 SUCCESS; 38382214223 6/6 SUCCESS; 38419111311 6/6 SUCCESS; 38419649711 1/1 SUCCESS; 38419439742 2/2 SUCCESS; 38498552499 6/6 SUCCESS. Historical 34-case SHA `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34`, 13 adversarial mocks, 28 synthetic cases and 21 follow-up synthetic cases NOT independently recomputed. CI PASS is limited to jobs' reported success.
- Offline regression-phase measurement as previously reported: single-runner 2.9656s / concurrent 2.6209s = 1.1315x (slower); follow-up serial 1.7114s / parallel 2.5776s (parallel slower). Overall CI and official backtest acceleration NOT VERIFIED.

## Railway production evidence
- Project `d1c1a050-b7d6-41ce-b300-13c20f82a20a`, environment `83d5840b-270e-4d3f-a941-a37fd4a55ff7`; inventory reports no staged patch, status reports pending patch `e113dacb-6705-4416-9997-dc694539d382` with zero changes: discrepancy, no apply.
- PIT rebuild: latest deployment SUCCESS, running 1/1; runtime: SUCCESS, running 1/1. KRX worker: deployment SUCCESS but running 0/1 (runtime NOT VERIFIED). Kiwoom real readonly: deployment SUCCESS but running 0/1, crashed 1/1 (runtime FAIL). Backend and Push: offline with FAILED latest deployments; db-query-readonly offline, critical issue 1.
- Deploy logs since 2026-11-11 00:00 UTC: PIT 0, KRX 0, Kiwoom 0, Runtime 41 records. Runtime USD/KRW Investing HTTP errors with Yahoo fallback around 01:24 UTC; this is not PIT or profitability validation.
- 2017–2022 KRX 1565/1565 weekday original-pair storage integrity is historical PASS only; official exchange calendar, status, corporate actions, executable fills and taxes remain NOT VERIFIED.

## Profitability approval matrix
| Gate | Status | Rationale |
|---|---|---|
| OpenDART original-filing / public available-at PIT | NOT VERIFIED | Candidate rows and signature do not establish original semantic meaning or disclosure timing |
| 2021/2022 first consolidated three-month operating profit, amendment lineage | NOT VERIFIED | No independently approved period/lineage |
| Historical company/security mapping | NOT VERIFIED | No approved PIT mapping |
| KRX official trading state/corporate actions/fills/costs/taxes | NOT VERIFIED | Pair storage is not exchange admissibility |
| NetEV, PF, CAGR, MDD, ES95/99, concentration, temporal robustness after tax | NOT VERIFIED | No approved official economic run |
| Offline CI job execution | PASS (limited) | 6 recorded workflow runs have successful job conclusions |
| End-to-end speedup | NOT VERIFIED | Synthetic regression timings do not show improvement |

## Hard gates and next steps
- M20 NO-GO; H5 consumed holdout and Dynamic outputs cannot be tuned or reused as independent holdout.
- Preserve Frozen H5; M20 horizon20/purge20; WF504/126/126; PIT, Purged/CPCV, independent holdout, Champion/Top3/NO_TRADE, costs/taxes/NetEV/execution/risk/promotion gates unchanged.
- ORDERING=false required; live environment variable value not independently inspected. No trading, funds, credential changes, promotion, merge or deployment.
- Fail-closed cache only when independent approved source/data/calculation/Frozen policy/runtime/evidence SHA-256 all match; parallelise only independent read-only postprocessing, never dependent retraining or capital transitions.
- Next: read-only independently resolve PR metadata and original filing available-at lineage, KRX official status/corporate actions and runtime crash evidence; then repeat exact SHA checks. Until PIT approval, only synthetic offline software and policy safety checks.
