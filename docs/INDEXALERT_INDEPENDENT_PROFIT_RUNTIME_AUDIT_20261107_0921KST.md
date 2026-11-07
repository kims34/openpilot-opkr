# IndexAlert independent PIT and isolated runtime audit — 2026-11-07 09:21 KST

Read-only inspection only. Prior observations are not promoted to current evidence. This document is isolated from PR #412/#413/#414/#418 and other active work. No code, workflow, operational config, model, market backtest, order or merge modified.

## Exact identity (GitHub connector read)
- research `index-alert-research-v1` HEAD `df474df348f22aa38b1dedaa59fcff66e548b406` (self-compare identical).
- development `index-alert-position-regen-fix-v1` HEAD `1e6367d2863a86c3470da13d81a955d277eba485` (self-compare identical).
- Draft OPEN unmerged: PR #412 `bf3d9514a87c53b1775e22ec9ba7711f6cecc49f`; #413 `f003ef6247e16fcc71bd3b1b20cd4904c4d984c0`; #414 `18c5418d9684d1717df58261ea27f28e514385b2`; #418 `2f98401cc50a6c6a25808a98516efd5bf0c944ee`; KRX #420 `fab3cbbd63a951a4e081f9e7f08c1391ca308581`; #422 `c14857620973531013799e44625d43080904fd5f`; #423 `0e38004363cac9fc4475556b3a1c445de9af407f`.
- PR #414 gate `docs/INDEXALERT_PROFITABILITY_INTEGRATION_GATE_2026-10-13.md` directly read at PR HEAD; blob SHA `984c933651f39f1ee9e26a1d7ac3893aaa5335be`.
- GitHub Action jobs re-read: 38381997417 6/6 SUCCESS; 38382214223 6/6 SUCCESS; 38419111311 6/6 SUCCESS; 38498552499 6/6 SUCCESS; 38419649711 1/1 SUCCESS; 38419439742 2/2 SUCCESS. These establish offline software job success only. Fixed 34-case digest `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34` and 13 adversarial/28 synthetic counts are inherited claims, not independently recomputed from artifacts this run. Chronology Action 41515392296 auto-anchor FAILURE, validation SKIPPED. Previous HTTP 404 route root cause NOT VERIFIED.

## Railway production read-only (2026-11-07 ~09:21 KST)
- Project `d1c1a050-b7d6-41ce-b300-13c20f82a20a`, production `83d5840b-270e-4d3f-a941-a37fd4a55ff7`.
- PIT deployment `8b354fc1-cfb2-4ef0-863e-67f7f5dda2b5` SUCCESS, replica 1/1; KRX `16c93d7c-7cd0-4d84-a327-298d2805376c` SUCCESS, replica 0/1; Runtime `eaaa9f67-b9f2-41d2-832c-7d6fad9b9b00` SUCCESS, replica 1/1. Since 2026-11-06 23:00Z, PIT and KRX deploy log queries returned zero entries. No evidence that historic 27 bad OHLC or 90 uncertain sessions were resolved.
- **New discrepancy requiring isolation:** environment status currently reports pending staged patch `e113dacb-6705-4416-9997-dc694539d382` (started 2026-10-29 06:20:53Z), with empty changes array; prior 08:20 KST audit reported staged=null. No deploy or acceptance performed; determine API status semantics/patch provenance read-only.
- **New operational concern:** `indexalert-kiwoom-real-readonly` deployment `a77fb922-b679-4d88-92c4-03054ec579cd` SUCCESS yet replica status 0 running / 1 crashed; status surface says online and zero recent deployment failures. This mismatch must not be equated to healthy running read-only execution; investigate logs/health independently without changing authorization.
- `db-query-readonly` offline with one critical, `indexalert-push` offline with one warning, `indexalert-backend` offline with four warnings; not evidence of live trading.
- Runtime 2026-11-07 00:19Z logs show Investing.com USD/KRW HTTPError then Yahoo fallback; unrelated to original-filing PIT or M20 return verification.

## Evidence gates
- Historical KRX private 1565/1565 weekday raw pairs: prior storage integrity PASS ONLY; official calendar, 90 uncertain days, 12003 zero-activity, corporate actions, execution eligibility: NOT VERIFIED / FAIL-CLOSED.
- OpenDART original/corrected SGML 15 candidate signatures: prior extraction evidence only; 2021/2022 original consolidated first-three-month operating-profit semantics, correction lineage and exact public available-at: NOT VERIFIED.
- Historical issuer/security mapping, security state, timestamped corporate actions, cost/tax and execution feasibility: NOT VERIFIED.
- NetEV, PF, CAGR, MDD, ES95/99, concentration, temporal robustness, annual after-tax risk-adjusted profit: NOT VERIFIED; M20 PIT and profitability RUN NO-GO.
- Synthetic CI job outcomes: PASS for listed jobs; fixed digest and phase timing not freshly independently reproduced; 2.9656s serial vs 2.6209s concurrent = 1.1315x regression-phase historical evidence, whole CI and official backtest acceleration NOT VERIFIED.
- Frozen H5 and consumed holdout must not be reused. M20 horizon20/purge20, WF504/126/126, PIT/Purged/CPCV/Holdout/Champion/Top3/NO_TRADE, predeclared cost/tax/risk/upgrade criteria unchanged. ORDERING=false; no money movement, order, Champion promotion, deployment, PR merge or workflow modification.

## Next independent work
1. Read-only verify Railway pending patch status and crash/health discrepancy against deployment logs and source SHA, without applying staged changes.
2. Verify chronology Anchor Action 404 URL/route/commit contract; no workflow changes.
3. Obtain independent official filing timestamps/period/correction lineage and KRX original market status/issuer mapping SHA, then PIT admission review. No return or M20 run until fully approved.
4. Isolated optimization only: synthetic fail-closed cache key equality across independently approved source/data/calculation/Frozen/runtime/approval SHA-256, exact parity and safe read-only postprocessing parallelism; never dependent retraining or capital-transition parallelism.
