# IndexAlert independent profitability and offline runtime audit — 2026-11-12 21:20 KST

Read-only GitHub/Railway audit. No market-performance replay, strategy search, deployment, merge, workflow change, secrets or order.

## Source heads and ownership
- Research branch previously independently confirmed HEAD df474df348f22aa38b1dedaa59fcff66e548b406; development branch previously confirmed HEAD 1e6367d2863a86c3470da13d81a955d277eba485. **Current HEAD freshness NOT VERIFIED this run** (branch search returned names only).
- Previously pinned Draft PR heads (current freshness NOT VERIFIED): #412 bf3d9514a87c53b1775e22ec9ba7711f6cecc49f; #413 f003ef6247e16fcc71bd3b1b20cd4904c4d984c0; #414 18c5418d9684d1717df58261ea27f28e514385b2; #418 2f98401cc50a6c6a25808a98516efd5bf0c944ee; KRX #420 fab3cbbd63a951a4e081f9e7f08c1391ca308581, #422 c14857620973531013799e44625d43080904fd5f, #423 0e38004363cac9fc4475556b3a1c445de9af407f.
- #414 gate document previously pinned blob 984c933651f39f1ee9e26a1d7ac3893aaa5335be; fresh fetch at audit branch returned no content (NOT VERIFIED this run). Prior audit document blob a697169ffc0028291613a6615fb95841712c7e80.

## Actual CI read 2026-11-12
- GitHub Actions jobs directly checked: 38381997417 6/6 SUCCESS, 38382214223 6/6 SUCCESS, 38419111311 6/6 SUCCESS, 38419649711 1/1 SUCCESS, 38419439742 2/2 SUCCESS, 38498552499 6/6 SUCCESS.
- Offline-only tests. Prior 34-case SHA-256 5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34 **not independently recalculated**; PR #418 synthetic 28 and PR #413 13 adversarial are historical reported scope, not independent current execution. Serial 2.9656s vs concurrent 2.6209s = 1.1315x regression phase only, not whole-CI or official backtest acceleration. PR #413/#418 implementation parity/integration remains NOT VERIFIED.

## Actual Railway production evidence
- Project d1c1a050-b7d6-41ce-b300-13c20f82a20a, environment 83d5840b-270e-4d3f-a941-a37fd4a55ff7.
- Latest deployment metadata: PIT rebuild 8b354fc1-cfb2-4ef0-863e-67f7f5dda2b5 SUCCESS; KRX worker 16c93d7c-7cd0-4d84-a327-298d2805376c SUCCESS; Runtime eaaa9f67-b9f2-41d2-832c-7d6fad9b9b00 SUCCESS; Kiwoom REAL read-only a77fb922-b679-4d88-92c4-03054ec579cd SUCCESS; backend cce12a43-592a-4910-9b75-89c6b7cdd159 FAILED; push 3ad3102d-ced6-416b-a6da-85c390c9a606 FAILED. All replica counts returned null: **live replica health NOT VERIFIED**, not proof of running.
- get_status stagedChanges=null, but pendingWork lists empty staged patch e113dacb-6705-4416-9997-dc694539d382 with zero changes; no accept/deploy.
- PIT logs queried 2026-11-12 11:15–12:20 UTC: **5/5 FAIL_CLOSED** at 11:15:50, 11:30:56, 11:46:03, 12:01:00, 12:16:09 UTC. Exact error KRXProspectiveOpenAPISourceError / COMMON_OHLC_NONPOSITIVE; source_failure_session=2026-09-28; 803 common-stock rows, 27 nonpositive OHLC and 27 zero-volume/value rows. session_manifest_sha256=null. private_rejected_source_receipt_saved=true is a runtime self-report, not independently rehashed bytes.
- Each PIT record: ordering=DISABLED, fresh_alpha_observation_admitted=false, independent_source_admission_verified=false, live_order_authorized=false, real_orders_authorized=false, funds_movement_authorized=false, permission_change_authorized=false. **Observed fail-closed safety PASS; official source quality FAIL.**
- KRX and Kiwoom read-only service logs 0 records within queried interval (not evidence of absence of failures). Runtime 151 entries returned (limit 150 per stream), repeated Investing USD/KRW HTTP errors with Yahoo fallback. This is an operational source-quality concern, not an approved price PIT source.

## Gate classifications
- Historical private 2017–2022 1565/1565 weekday KRX raw pairs: **historical stored-pair integrity PASS only on earlier evidence**; official session calendar, halt/trade-state, corporate actions, executable price/volume, taxes and costs **NOT VERIFIED**.
- OpenDART #38419439742 original/correction SGML candidate rows 15 numeric adjacency signatures: historical offline candidate PASS, original-filing meaning, exact public available-at, 2021/2022 first 3-month consolidated operating-income period/correction lineage **NOT VERIFIED**.
- Historical issuer/security episode mapping **NOT VERIFIED**.
- NetEV/PF/CAGR/MDD/ES95/ES99/concentration/time robustness after all costs and taxes **NOT VERIFIED**; M20 **NO-GO**. H5 failed/consumed holdout and Dynamic cannot be repurposed.
- Frozen H5, M20 horizon20/purge20, WF504/126/126, PIT/labels/Purged/CPCV/independent Holdout/Champion/Top3/NO_TRADE and cost/tax/risk/promotion gates unchanged. ORDERING=false required, and observed prospective PIT logs show DISABLED.
- Cache only on independently approved original/data/code/Frozen/runtime/evidence SHA-256 exact identity, fail closed. Only read-only postprocessing parallel; never dependent retraining or capital transitions.

## Next safe actions
1. KRX owner, in its existing authorized private environment, independently rehash 2026-09-28 rejected raw OHLC 27 rows, identify official status/corporate-action/zero-activity semantics and source-vintage; no re-fetch or approval inferred.
2. DART owner independently verify first-filing document period and public timestamp/correction lineage against original bytes and explicit source SHAs.
3. Optimization owner compare PR #413/#418 code/runner identity and offline CI artifact hashes without changing policy or running market profitability.
4. Coordinator refresh branch/PR HEAD and original source SHA; only after independent source PIT approval consider explicitly separately authorized economics gate. No automatic merge, production deployment, trading or Champion promotion.
