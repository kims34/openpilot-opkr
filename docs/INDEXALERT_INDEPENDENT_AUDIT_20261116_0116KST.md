# IndexAlert independent audit — 2026-11-16 01:16 KST

Scope: GitHub and Railway production read-only verification; sole write is this isolated audit note. No workflow edits, merge, deploy, order, capital, account, Champion, economic backtest, or policy change.

## GitHub / CI
- Read PR #412, #413, #414, #418, #420, #422, #423 via issue metadata: all OPEN at this observation; draft flags, current exact PR HEAD, and research/development exact branch HEAD NOT VERIFIED via this read path. Previous audit (2026-11-16 00:20 KST) reports heads #412 bf3d9514a87c53b1775e22ec9ba7711f6cecc49f; #413 f003ef6247e16fcc71bd3b1b20cd4904c4d984c0; #414 18c5418d9684d1717df58261ea27f28e514385b2; #418 2f98401cc50a6c6a25808a98516efd5bf0c944ee; #420 fab3cbbd63a951a4e081f9e7f08c1391ca308581; #422 c14857620973531013799e44625d43080904fd5f; #423 0e38004363cac9fc4475556b3a1c445de9af407f. These are historical, NOT current independent HEAD proof.
- PR #414 integration gate fetched from refs/pull/414/head, original-filing/PIT and official trading-source admission blocked.
- Actual GitHub jobs inspected: Actions 38381997417, 38382214223, 38419111311 all 6/6 SUCCESS; 38419439742 2/2 SUCCESS; 38419649711 1/1 SUCCESS; 38486028854 1/1 FAILURE, job 115599778959, step "Enforce original CI regression-source blob identities before any test" FAILURE; subsequent parity suites SKIPPED. Previously reported mismatch: research_v1_runtime_manifest.py expected blob SHA-1 108f66714602a1bd3ae42c34dcca7c16e38f460b vs observed e428789e2e97ca7be3a4482e0df23b483a1ad69d. This run's log fetched but mismatch string not independently extracted. Fail closed, not optimization PASS.
- Historical fixed 34-case SHA-256 5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34: NOT independently recomputed. Serial 2.9656 s vs concurrent 2.6209 s = 1.1315x regression-phase only; full CI and official backtest speed NOT VERIFIED.

## Railway production
- Project d1c1a050-b7d6-41ce-b300-13c20f82a20a, environment 83d5840b-270e-4d3f-a941-a37fd4a55ff7. Deployment list read-only: historical KRX worker successful deployment 16c93d7c-7cd0-4d84-a327-298d2805376c, commit 1e6367d2863a86c3470da13d81a955d277eba485; this is deployment commit, NOT independently current branch HEAD.
- PIT rebuild log window 2026-11-15 14:40–16:20 UTC: one observed record at 14:46:18 UTC, status FAIL_CLOSED, KRXProspectiveOpenAPISourceError COMMON_OHLC_NONPOSITIVE, common_stock_rows 803, nonpositive_ohlc_rows 27, zero_volume_value_rows 27, source_failure_session 2026-09-28; session_manifest_sha256 null; independent source/model/chronology admissions false; fresh alpha false; ordering DISABLED, live orders false, funds movement false. KRX source quality FAIL; safe veto observed PASS, PIT approval NOT VERIFIED.
- KRX historical worker same window: zero returned logs (absence of evidence, not success). Runtime same window: Investing USD/KRW HTTPError with Yahoo fallback, not official PIT evidence. Exact current service replicas and staged changes NOT VERIFIED this run.
- Historical KRX 2017–2022 private 1565/1565 weekday raw-pair integrity PASS as previously recorded, but official market calendar/trading statuses, actions, feasibility NOT VERIFIED.

## Profitability gate
- OpenDART original filing, exact public available-at/PIT, 2021/2022 first 3-month consolidated operating income and correction lineage, historical corp/security mapping: NOT VERIFIED.
- Official KRX calendar, status, corporate actions, fills, fees/taxes: NOT VERIFIED (prospective source OHLC quality FAIL).
- NetEV/PF/CAGR/MDD/ES95/99, concentration, time robustness and after-cost/tax annual risk-adjusted profitability: NOT VERIFIED, no economic run permitted. H5 exhausted holdout not reused; M20 NO-GO.
- Preserve Frozen H5, M20 horizon20/purge20, WF504/126/126, independent holdout, Champion/Top3/NO_TRADE, fixed risk/cost/tax gates and ORDERING=false. No dependent retraining or capital-transition parallelization; only independent read-only post-processing; SHA-bound fail-closed caching.

## Next safe steps
1. Independently dereference current research/development and PR HEADs and original SHA-bound artifacts before promotion.
2. KRX owner to reconcile 27 official OHLC failures against official status/corporate action/raw SHA without deleting veto rows.
3. DART owner to prove first-filed consolidated three-month period, corrections, and available-at; keep M20 blocked.
4. PR #418 owner to resolve original manifest blob mismatch on its own isolated branch, rerun synthetic offline checks only; do not change workflows through blocked security paths.
