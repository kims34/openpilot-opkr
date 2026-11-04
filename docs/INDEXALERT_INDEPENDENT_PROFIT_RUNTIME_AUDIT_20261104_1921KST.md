# IndexAlert independent profitability/runtime audit — 2026-11-04 19:21 KST

Read-only connector evidence, no source admission or economic backtest.

## GitHub heads
- PR #412: open, draft=true, HEAD=bf3d9514a87c53b1775e22ec9ba7711f6cecc49f
- PR #413: open, draft=true, HEAD=f003ef6247e16fcc71bd3b1b20cd4904c4d984c0
- PR #414: open, draft=true, HEAD=18c5418d9684d1717df58261ea27f28e514385b2
- PR #418: open, draft=true, HEAD=2f98401cc50a6c6a25808a98516efd5bf0c944ee
- PR #420: open, draft=true, HEAD=fab3cbbd63a951a4e081f9e7f08c1391ca308581
- PR #422: open, draft=true, HEAD=c14857620973531013799e44625d43080904fd5f
- PR #423: open, draft=true, HEAD=0e38004363cac9fc4475556b3a1c445de9af407f
- Research branch `index-alert-research-v1`: exists; exact HEAD not independently resolved this run (NOT VERIFIED). Previous observed df474df348f22aa38b1dedaa59fcff66e548b406 is historical only.
- Development branch `index-alert-position-regen-fix-v1`: exists; exact HEAD not independently resolved this run (NOT VERIFIED). Previous observed 1e6367d2863a86c3470da13d81a955d277eba485 is historical only.
- Integration gate docs blob SHA-1: 984c933651f39f1ee9e26a1d7ac3893aaa5335be (direct fetch).

## Actions independently read (job conclusions)
- 38381997417 6/6 SUCCESS; 38382214223 6/6 SUCCESS; 38419111311 6/6 SUCCESS; 38419649711 1/1 SUCCESS; OpenDART 38419439742 2/2 SUCCESS.
- Chronology 41515392296 auto-anchor FAILURE, validation SKIPPED.
- Historical 34-case SHA256 5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34 and 2.9656s/2.6209s=1.1315x are reported prior evidence, NOT independently recalculated now. No whole-CI or admitted-data speedup claim.

## Railway (production, direct read 2026-11-04 19:21 KST)
- KRX worker deployment 16c93d7c-7cd0-4d84-a327-298d2805376c SUCCESS (2026-10-12), commit 1e6367d2863a86c3470da13d81a955d277eba485. 09:00-10:25 UTC deploy logs: 0.
- PIT service deployment 8b354fc1-cfb2-4ef0-863e-67f7f5dda2b5 SUCCESS (2026-10-10), commit e57054ecdb3e734ced3c9a981b887d9b5fc60f97. **NEW directly observed** 2026-11-04 09:30, 09:45, 10:00 UTC and later: INDEXALERT_PROSPECTIVE_RUNTIME status FAIL_CLOSED, error COMMON_OHLC_NONPOSITIVE; common_stock_rows=803, nonpositive_ohlc_rows=27, zero_volume_value_rows=27, independent_source/model/chronology_admission_verified=false, session_manifest_sha256=null, ordering=DISABLED, live_order_authorized=false, private_rejected_source_receipt_saved=true. The underlying source_failure_session remains 2026-09-28; these logs are repeated prospective rejections, NOT new independent source admission.
- IndexAlert runtime deployment eaaa9f67-b9f2-41d2-832c-7d6fad9b9b00 SUCCESS (2026-10-05), commit 8a68b01bca5d551d083ccda263df38d86fa54166; current runtime price checks do not establish historical PIT or tradability.

## Gate verdict
- Official OpenDART original filing, exact public available-at, 2021/2022 first 3-month consolidated operating-profit period/correction lineage: NOT VERIFIED / FAIL CLOSED.
- Historical entity-security mapping, KRX official calendar/trading status/corporate actions, actual fillability and cost/tax assumptions: NOT VERIFIED / FAIL CLOSED. Historical 1565/1565 private SHA receipts PASS only for storage integrity, 90-day classification unresolved; 12003 zero-activity observations quarantined.
- M20 PIT and after-tax risk-adjusted annual NetEV/PF/CAGR/MDD/ES95/99/concentration/WF robustness: NOT EVALUABLE, NO-GO; no economic run authorized.
- Offline isolated runtime synthetic software regression: limited PASS for cited CI job conclusions; speedup on full CI or actual official backtest NOT VERIFIED.

## Next safe steps
Obtain independently auditable original-filing chronology/period lineage and official KRX exact calendar/status/adjustment receipts before any M20 economic run. Continue only synthetic offline fail-closed checks on isolated code. Frozen H5, M20 horizon20/purge20, WF504/126/126, holdout/CPCV/Champion gates unchanged. No holdout reuse, parameter search, orders, permission changes, merges, deployment, or workflow edits. ORDERING=false.
