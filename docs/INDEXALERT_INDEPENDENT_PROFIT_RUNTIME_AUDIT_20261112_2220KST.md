# IndexAlert independent audit — 2026-11-12 22:20 KST

Scope: read-only GitHub/Railway verification and offline-only optimization evidence. No financial backtest, market return, deployment, merge, workflow, trading or secrets change.

## Fresh immutable source references
- Research `index-alert-research-v1`: compare to `df474df348f22aa38b1dedaa59fcff66e548b406` identical, ahead/behind 0/0.
- Development `index-alert-position-regen-fix-v1`: compare to `1e6367d2863a86c3470da13d81a955d277eba485` identical, 0/0.
- PR head compares (all identical 0/0 vs previously pinned): #412 `bf3d9514a87c53b1775e22ec9ba7711f6cecc49f`; #413 `f003ef6247e16fcc71bd3b1b20cd4904c4d984c0`; #414 `18c5418d9684d1717df58261ea27f28e514385b2`; #418 `2f98401cc50a6c6a25808a98516efd5bf0c944ee`; KRX #420 `fab3cbbd63a951a4e081f9e7f08c1391ca308581`, #422 `c14857620973531013799e44625d43080904fd5f`, #423 `0e38004363cac9fc4475556b3a1c445de9af407f`. HEAD identity confirmed, PR Draft/open state not independently fetched in this run.
- #414 gate source blob `984c933651f39f1ee9e26a1d7ac3893aaa5335be` fetched from refs/pull/414/head. Historical policy unchanged.
- Actions directly fetched jobs: 38381997417 6/6 success; 38382214223 6/6 success; 38419111311 6/6 success; 38419649711 1/1 success; 38419439742 2/2 success; 38498552499 6/6 success. GitHub URLs: https://github.com/kims34/openpilot-opkr/actions/runs/38498552499 and https://github.com/kims34/openpilot-opkr/actions/runs/38419439742.
- Offline 34-case pinned SHA-256 `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34`: historical CI-reported only; independent byte recomputation NOT VERIFIED. #413 13 adversarial and #418 28 synthetic historically reported; PR #413/#418 implementation parity NOT VERIFIED. Single runner serial 2.9656s vs concurrent suite 2.6209s = 1.1315x regression-phase only; whole-CI/official backtest speed NOT VERIFIED.

## Railway production read-only
- Project `d1c1a050-b7d6-41ce-b300-13c20f82a20a`, environment `83d5840b-270e-4d3f-a941-a37fd4a55ff7`.
- Latest deployment metadata still lists KRX worker `16c93d7c-7cd0-4d84-a327-298d2805376c` SUCCESS (2026-10-12); Kiwoom read-only `a77fb922-b679-4d88-92c4-03054ec579cd` SUCCESS (2026-10-29). SUCCESS deployment metadata is not live replica-health proof.
- PIT service `225f2279-d728-4e1a-a3f3-2447ff0f9dc1` deploy logs 2026-11-12 12:15–13:25 UTC: five FAIL_CLOSED entries at 12:16:09, 12:31:06, 12:46:13, 13:01:11, 13:16:19. All `KRXProspectiveOpenAPISourceError / COMMON_OHLC_NONPOSITIVE`, source session 2026-09-28, 803 common rows, 27 nonpositive OHLC, 27 zero volume/value. `session_manifest_sha256=null`, `private_rejected_source_receipt_saved=true` self-reported but private bytes not independently rehashed. **Official source quality FAIL; observed fail-closed PASS**: `ordering=DISABLED`, `fresh_alpha_observation_admitted=false`, `independent_source_admission_verified=false`, `real_orders_authorized=false`, `funds_movement_authorized=false`, `permission_change_authorized=false`.
- KRX worker and Kiwoom read-only logs in same window: zero entries, NOT proof of healthy replica. Runtime logs include Investing USD/KRW HTTPError and Yahoo fallback; not approved PIT.
- Live replica count/health not independently checked this run: NOT VERIFIED. No staged patch accepted.

## Evidence gates
- 2017–2022 KRX 1565/1565 private weekday pairs: prior stored-pair integrity PASS only; official calendar, historical trade status, corporate actions, executable fills, fees/taxes NOT VERIFIED.
- OpenDART original/correction SGML 15 operating-income candidate rows: candidate signature evidence only; 2021/2022 original consolidated 3-month operating income period, amendment lineage, public available-at and historical issuer/security mapping NOT VERIFIED.
- Post-fee/post-tax NetEV/PF/CAGR/MDD/ES95/99, return concentration, temporal robustness NOT VERIFIED. **M20 NO-GO**. H5 failed/consumed holdout and Dynamic results cannot be independently reused.
- Frozen H5 and M20 horizon20/purge20, WF504/126/126, PIT/label/Purged/CPCV/holdout/Champion/Top3/NO_TRADE, fixed costs/taxes/risk unchanged. ORDERING=false requirement maintained; observed logs DISABLED.
- Cache fail-closed unless independently approved source/data/code/Frozen/runtime/evidence SHA-256 all match; parallelize read-only postprocessing only, never dependent retraining or capital transitions.

## Next authorized verification
1. KRX owner rehash private rejected 27 rows and establish official vintage/trading state without treating 27 exclusions as approval.
2. DART owner independently prove original first-filing period, public timestamp and amendment lineage with original byte SHA.
3. Offline optimization owner compare #413/#418 implementation and pinned artifact identities without market-return experiments.
4. Coordinator require independent source PIT approvals before any separately authorized M20 economics. No deployment/merge/order/funds/permission change/Champion promotion.
