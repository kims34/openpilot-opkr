# IndexAlert independent profitability/runtime audit — 2026-11-07 10:24 KST

Scope: read-only independent evidence audit. No market performance runs, live orders, deployment, merge, workflow edits, or policy changes.

## Exact refs verified this run
- Research `index-alert-research-v1`: `df474df348f22aa38b1dedaa59fcff66e548b406` (compare to pinned SHA: identical, ahead=0, behind=0).
- Development `index-alert-position-regen-fix-v1`: `1e6367d2863a86c3470da13d81a955d277eba485` (identical).
- Draft OPEN, unmerged: #412 `bf3d9514a87c53b1775e22ec9ba7711f6cecc49f`; #413 `f003ef6247e16fcc71bd3b1b20cd4904c4d984c0`; #414 `18c5418d9684d1717df58261ea27f28e514385b2`; #418 `2f98401cc50a6c6a25808a98516efd5bf0c944ee`; #420 `fab3cbbd63a951a4e081f9e7f08c1391ca308581`; #422 `c14857620973531013799e44625d43080904fd5f`; #423 `0e38004363cac9fc4475556b3a1c445de9af407f`.
- PR #414 gate document blob `984c933651f39f1ee9e26a1d7ac3893aaa5335be` at `docs/INDEXALERT_PROFITABILITY_INTEGRATION_GATE_2026-10-13.md`.
- Actions jobs inspected: #41515392296 auto-anchor FAILURE / validation SKIPPED; #38498552499 6/6 SUCCESS offline parity; #38419649711 1/1 SUCCESS synthetic single runner; #38419439742 2/2 SUCCESS OpenDART row-diff, **not PIT approval**. Historical regression 34-case SHA `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34` remains historical evidence, not independently rehashed this run.

## Railway production (read-only)
Project `d1c1a050-b7d6-41ce-b300-13c20f82a20a`, environment `83d5840b-270e-4d3f-a941-a37fd4a55ff7`. `describe_environment`: staged=null, 0 staged changes per service. Latest deployments PIT `8b354fc1-cfb2-4ef0-863e-67f7f5dda2b5` SUCCESS; KRX `16c93d7c-7cd0-4d84-a327-298d2805376c` SUCCESS; real-readonly `a77fb922-b679-4d88-92c4-03054ec579cd` SUCCESS; runtime `eaaa9f67-b9f2-41d2-832c-7d6fad9b9b00` SUCCESS. Deployment SUCCESS and configured replicas=1 do not prove healthy runtime replicas. No PIT/KRX/real-readonly deploy logs since 2026-11-06 20:00 UTC in this query; absence does not prove defect fixed. Runtime at 2026-11-07 01:24 UTC: Investing.com USD/KRW HTTPError, Yahoo fallback, unavailable extended-session quotes, market CLOSED. No trading permission inferred.

## Gate decisions
- Historical KRX 1565/1565 weekday original-pair storage: **PASS (historical integrity only)**; official calendar, 90 uncertain dates, zero-activity 12003, corporate actions, orderability, execution costs/taxes: **NOT VERIFIED / fail-closed**.
- 2021/2022 original-filing consolidated first three-month operating income period, amendment lineage, available-at timestamp, corp/security history: **NOT VERIFIED / fail-closed**. OpenDART 15 candidate rows do not establish semantics or PIT.
- PIT rebuild prior 27 invalid common-stock OHLC: **FAIL (historical evidence)**; remediation **NOT VERIFIED** due no new PIT logs.
- Chronology anchor proof: **FAIL** (#41515392296); root cause of prior /anchor/latest HTTP 404 **NOT VERIFIED**.
- Offline CI parity: **PASS for tested synthetic/offline scope only**. Single-runner regression-phase serial 2.9656s versus concurrent 2.6209s = 1.1315x historical measurement; end-to-end official backtest speed **NOT VERIFIED**.
- NetEV/PF/CAGR/MDD/ES95/99, annual after-cost-and-tax risk-adjusted net profit, return concentration, temporal robustness: **NOT VERIFIED; no authorized M20 run**.
- M20 **NO-GO**, ORDERING=false, NO_TRADE. H5 consumed/failed Holdout and Dynamic results cannot be reused or tuned ex post.

## Next allowed independent checks
1. Read-only verify chronology anchor route/contract against deployed source SHA, then validate original timestamp evidence without changing workflows.
2. Source owners separately establish original-filing and KRX official historical tradeability provenance, with original SHA and timestamp.
3. Keep optimization work limited to isolated synthetic offline tests and independent read-only postprocessing; cache only with all approved source/data/code/Frozen/runtime/evidence SHA-256 matching, fail closed.
4. No merge, production deployment, capital movement, live orders, Champion promotion, frozen parameter changes, or official economic experiments without distinct explicit approval.
