# IndexAlert independent audit — 2026-11-14 19:17 KST

Read-only evidence snapshot, no economic backtest or deployment. Frozen H5, M20 horizon20/purge20, WF504/126/126, PIT/Purged/CPCV/independent holdout, Champion/Top3/NO_TRADE, costs/taxes/risk unchanged; ORDERING=false; M20 NO-GO.

## GitHub verified
Draft open PR heads (Git SHA): #412 bf3d9514a87c53b1775e22ec9ba7711f6cecc49f; #413 f003ef6247e16fcc71bd3b1b20cd4904c4d984c0; #414 18c5418d9684d1717df58261ea27f28e514385b2; #418 2f98401cc50a6c6a25808a98516efd5bf0c944ee; KRX #420 fab3cbbd63a951a4e081f9e7f08c1391ca308581, #422 c14857620973531013799e44625d43080904fd5f, #423 0e38004363cac9fc4475556b3a1c445de9af407f. PR #414 gate blob Git SHA-1 984c933651f39f1ee9e26a1d7ac3893aaa5335be. Research/development branch exact current HEAD NOT VERIFIED.

Actions: 38381997417, 38382214223, 38419111311 each 6/6 PASS; 38419439742 2/2 PASS; 38419649711 1/1 PASS. Action 38486028854 1/1 FAIL: archived research_v1_runtime_manifest.py blob expected 108f66714602a1bd3ae42c34dcca7c16e38f460b vs observed e428789e2e97ca7be3a4482e0df23b483a1ad69d (Git SHA-1). Independent SHA-256 recomputation of archived 34-case fixture NOT VERIFIED; 5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34 remains historical reported fingerprint only. Regression-phase serial 2.9656s vs concurrent 2.6209s = 1.1315x reported, not total CI or official backtest speedup.

## Railway production
Project d1c1a050-b7d6-41ce-b300-13c20f82a20a; environment 83d5840b-270e-4d3f-a941-a37fd4a55ff7. Last deployments PIT 8b354fc1-cfb2-4ef0-863e-67f7f5dda2b5 SUCCESS; KRX 16c93d7c-7cd0-4d84-a327-298d2805376c SUCCESS; Runtime eaaa9f67-b9f2-41d2-832c-7d6fad9b9b00 SUCCESS; Kiwoom real-readonly 028c7110-5cbf-457b-b1a6-539c818280b0 FAILED. Replica counts returned null (NOT VERIFIED). Environment stagedChanges=null yet pendingWork patch e113dacb-6705-4416-9997-dc694539d382 status staged since 2026-10-29, unresolved discrepancy.

NEW: 2026-11-14 09:15–10:25 UTC service log query found PIT service 4 prospective runtime records (09:30,09:45,10:00,10:15 UTC), all status FAIL_CLOSED, error_class KRXProspectiveOpenAPISourceError, error_reason_code COMMON_OHLC_NONPOSITIVE, 27 nonpositive/803 common stock rows, 27 zero-volume/value, session_manifest_sha256=null, independent_source/model/chronology_admission_verified=false, fresh_alpha_observation_admitted=false, ordering=DISABLED, real_orders_authorized=false. These are prospective runtime logs, NOT PIT rebuild success evidence; service identity alone does not prove pipeline ownership. KRX worker 0 records in interval. Runtime service returned 101 records (limit 100 requested; partial); 10:17 UTC Yahoo USD/KRW quote present; no inference of market data admissibility.

## Gate decisions
KRX 1565/1565 weekday private raw pairs integrity PASS only as previously evidenced; official calendar, 90-session classification, 12003 zero-activity rows, corporate actions, executable trades, fees/taxes NOT VERIFIED. OpenDART SGML candidate row signature 15 matches is historical candidate extraction PASS only, original-filing meaning, public available-at/PIT, 2021/2022 first three months consolidated operating-profit correction lineage NOT VERIFIED. Historic issuer/security mapping NOT VERIFIED. NetEV, PF, CAGR, MDD, ES95/99, concentration, temporal robustness after fees/taxes NOT VERIFIED. H5 holdout consumed; no reuse or tuning. M20 PIT/economic RUN blocked; no new official-market or model-search tests.

## Next allowed work
1. Read-only independently compare approved original manifest bytes and exact PR #418 blob lineage, do not alter expected hash.
2. Independently establish official filing publication time/period/correction lineage and KRX session/status/corporate action/executability evidence before any PIT gate.
3. Clarify Railway pending patch versus stagedChanges and prospect runtime source-error receipts, with read-only evidence only.
4. Cache only when all independent approved source/data/code/Frozen/runtime/approval SHA-256 match; parallelize read-only postprocessing only. No dependent retraining or capital transitions.
No merges, workflow bypass, production deployment, trading, permission changes, or Champion promotion.
