# IndexAlert independent audit — 2026-11-16 00:20 KST

Scope: read-only GitHub/Railway inspection; this document is the sole write. No market performance run, workflow change, merge, deployment, account permission change, order or capital transfer.

## GitHub observed
- PR #412 HEAD bf3d9514a87c53b1775e22ec9ba7711f6cecc49f; #413 f003ef6247e16fcc71bd3b1b20cd4904c4d984c0; #414 18c5418d9684d1717df58261ea27f28e514385b2; #418 2f98401cc50a6c6a25808a98516efd5bf0c944ee; #420 fab3cbbd63a951a4e081f9e7f08c1391ca308581; #422 c14857620973531013799e44625d43080904fd5f; #423 0e38004363cac9fc4475556b3a1c445de9af407f. All seven OPEN/DRAFT/UNMERGED.
- PR #414 gate document Git blob SHA-1 984c933651f39f1ee9e26a1d7ac3893aaa5335be (fetched from its head branch).
- Research and development branch exact current HEAD: NOT VERIFIED this run; branch names were discovered but not dereferenced to commits. Do not equate PR base SHAs with branch HEAD.
- Actions 38381997417, 38382214223, 38419111311: each 6/6 job PASS; 38419439742 2/2 PASS; 38419649711 1/1 PASS; 38486028854 1/1 FAIL. Failure job 115599778959: archived blob mismatch research_v1_runtime_manifest.py expected Git SHA-1 108f66714602a1bd3ae42c34dcca7c16e38f460b observed e428789e2e97ca7be3a4482e0df23b483a1ad69d.
- 34-case fixed test SHA-256 5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34 is a historical claim, NOT independently recomputed this run. Offline runner 2.9656 s serial / 2.6209 s concurrent = 1.1315x regression phase historical evidence only; full CI and official backtest acceleration NOT VERIFIED.

## Railway production observed
- Project d1c1a050-b7d6-41ce-b300-13c20f82a20a, environment 83d5840b-270e-4d3f-a941-a37fd4a55ff7.
- PIT rebuild deployment 8b354fc1-cfb2-4ef0-863e-67f7f5dda2b5 SUCCESS, 1/1 running; KRX historical worker 16c93d7c-7cd0-4d84-a327-298d2805376c SUCCESS but 0/1 running; Runtime eaaa9f67-b9f2-41d2-832c-7d6fad9b9b00 SUCCESS, 1/1 running. Deployment SUCCESS does not prove source quality.
- PIT log 2026-11-15 14:01, 14:16, 14:31, 14:46 UTC: four FAIL_CLOSED events, COMMON_OHLC_NONPOSITIVE; common_stock_rows=803, nonpositive_ohlc_rows=27, zero_volume_value_rows=27, session_manifest_sha256=null, fresh_alpha_observation_admitted=false, independent source/model/chronology admission=false, ordering=DISABLED. Source quality FAIL, fail-closed safety PASS. The 27 rows require original official KRX and market-state reconciliation, not automatic sanitisation.
- KRX historical worker: zero new deploy log entries in 14:00–15:25 UTC window (not proof of non-execution). Runtime logs: Investing USD/KRW HTTPError with Yahoo fallback; this is not an approved PIT input.
- Environment pending staged patch patch:e113dacb-6705-4416-9997-dc694539d382 since 2026-10-29 06:20:53 UTC; do not apply. Backend, push, db-query-readonly offline; db-query-readonly criticalCount=1.

## Gate adjudication
- Historical KRX private 1565/1565 weekday original pairs storage integrity: historical PASS only; official calendar, security state, corporate actions, fillability, cost/tax NOT VERIFIED.
- OpenDART original and amended SGML 15 candidate lines / adjacent number signature: historical extraction PASS only; 2021/2022 first three months consolidated operating profit period, original-filing semantics, amendment lineage, exact public available-at/PIT NOT VERIFIED.
- Historical issuer/security mapping NOT VERIFIED. NetEV, PF, CAGR, MDD, ES95/99, concentration, robustness, tax/cost-adjusted annual risk-adjusted net profitability NOT VERIFIED.
- M20 PIT and profitability RUN NO-GO. Frozen H5, M20 horizon20/purge20, WF504/126/126, PIT/labels/Purged/CPCV/independent holdout/Champion/Top3/NO_TRADE and economics gates unchanged. Consumed H5 holdout and dynamic results cannot be reused as independent evidence.
- Optimization: PR #413 and #418 synthetic/offline safety CI results PASS as specified above, but #418 integration manifest mismatch FAIL. Cache must fail closed unless independently approved source/data/calculation/Frozen policy/runtime/approval evidence SHA-256 all match. Parallelise only read-only postprocessing; no dependent retraining/capital transition concurrency.

## Next admissible steps
1. Isolated read-only official KRX 27-row raw receipts and official trading status, date/calendar, corporate actions and fillability reconciliation with source SHA.
2. Original-filing DART public available-at and 2021/2022 period/amendment lineage independent proof.
3. PR #418 archived blob drift diagnosis using pinned original and observed SHA, without workflow mutation; synthetic offline tests only.
4. Recompute fixed 34-case SHA independently; obtain current branch HEADs; no new economic experiment before PIT admission.

No production deployment, workflow edit, PR merge, model search, performance backtest, live order, funds movement, credential change or champion promotion performed.
