# IndexAlert independent profitability/runtime audit — 2026-11-06 19:22 KST

Read-only verification, not a source/PIT/economics approval. No market performance run, no trading, no deploy, no merge, no workflow edit.

## Exact repository anchors
- research `index-alert-research-v1`: `df474df348f22aa38b1dedaa59fcff66e548b406`
- development `index-alert-position-regen-fix-v1`: `1e6367d2863a86c3470da13d81a955d277eba485`
- PR #412: OPEN/Draft, `bf3d9514a87c53b1775e22ec9ba7711f6cecc49f`
- PR #413: OPEN/Draft, `f003ef6247e16fcc71bd3b1b20cd4904c4d984c0`
- PR #414: OPEN/Draft, `18c5418d9684d1717df58261ea27f28e514385b2`
- PR #418, #420, #422, #423: OPEN/Draft (metadata verified; exact HEAD SHA not independently established this run).
- #414 gate document fetched at #414 HEAD; original gate remains NO-GO, no source admission.

## GitHub Actions independently read
- [38381997417](https://github.com/kims34/openpilot-opkr/actions/runs/38381997417): 6/6 jobs success.
- [38382214223](https://github.com/kims34/openpilot-opkr/actions/runs/38382214223): 6/6 success.
- [38419111311](https://github.com/kims34/openpilot-opkr/actions/runs/38419111311): 6/6 success.
- [38419649711](https://github.com/kims34/openpilot-opkr/actions/runs/38419649711): 1/1 success.
- [38419439742](https://github.com/kims34/openpilot-opkr/actions/runs/38419439742): 2/2 success.
- [41515392296](https://github.com/kims34/openpilot-opkr/actions/runs/41515392296): auto-anchor FAIL, validation SKIPPED.
- Prior fixed 34-case digest `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34`, 13 adversarial mocks, 28 synthetic cases and 2.9656/2.6209=1.1315x regression-phase are historical claims, not independently recomputed today. Whole-CI/official-backtest speedup NOT VERIFIED.

## NEW production runtime evidence (read-only)
Railway IndexAlert project `d1c1a050-b7d6-41ce-b300-13c20f82a20a`, production `83d5840b-270e-4d3f-a941-a37fd4a55ff7`, PIT rebuild service `225f2279-d728-4e1a-a3f3-2447ff0f9dc1`, settled deployment `8b354fc1-cfb2-4ef0-863e-67f7f5dda2b5` SUCCESS.
At **2026-11-06 18:30:47, 18:45:45, 19:00:55, 19:16:01 KST** (09:30,09:45,10:00,10:16 UTC), four actual deploy logs reported `INDEXALERT_PROSPECTIVE_RUNTIME` `status=FAIL_CLOSED`, `error_class=KRXProspectiveOpenAPISourceError`, `error_reason_code=COMMON_OHLC_NONPOSITIVE`, `source_failure_session=2026-09-28`, `common_stock_rows=803`, `nonpositive_ohlc_rows=27`, `zero_volume_value_rows=27`, `session_manifest_sha256=null`. Explicit `fresh_alpha_observation_admitted=false`, `independent_source_admission_verified=false`, `independent_chronology_admission_verified=false`, `independent_model_admission_verified=false`, `live_order_authorized=false`, `real_orders_authorized=false`, `funds_movement_authorized=false`, `ordering=DISABLED`. `private_rejected_source_receipt_saved=true`. Thus current runtime safety rejection PASS (observed fail-closed), source quality FAIL for prospective admission, chronology and model admission NOT VERIFIED, M20 NO-GO. The 27/803 issue is **not resolved**; do not interpret a SUCCESS deployment as source approval. `chronology_anchor_pending=false` is only a runtime flag, not independent chronology approval; GitHub anchor Action remains failed.

KRX historical worker `003812ee-102b-42b6-bda4-36925885b428`: SUCCESS deployment `16c93d7c-7cd0-4d84-a327-298d2805376c`, no new logs in 17:00–19:22 KST window, running 0. Historical private 1565/1565 weekday-pair SHA storage PASS (previous evidence), official calendar/tradability NOT VERIFIED. Runtime `37902fde-ca05-43e0-bc76-278992bf7732`: SUCCESS running 1. Backend/push/db-query-readonly offline, latter critical=1; Kiwoom real-readonly shows online but replica running=0/crashed=1. Pending staged patch `e113dacb-6705-4416-9997-dc694539d382` remains, unchanged.

## Gate verdict and safe next work
- Original filing/public available-at/PIT, 2021/2022 first three-month consolidated operating profit period and correction lineage: NOT VERIFIED.
- Historical issuer/security mappings, official KRX session/state/corporate actions/fills, taxes and costs: NOT VERIFIED.
- Annual after-cost/tax risk-adjusted NetEV/PF/CAGR/MDD/ES95/99, concentration and temporal robustness: NOT VERIFIED; no economic run.
- Runtime rejection of invalid OHLC: PASS (four independent timestamped observations), source admission: FAIL-CLOSED; M20: NO-GO.
- Frozen H5, M20 horizon20/purge20, WF504/126/126, Purged/CPCV/Holdout/Champion/Top3/NO_TRADE unchanged. Holdout consumed H5/Dynamic cannot be reused as independent. ORDERING disabled.
- Optimisation: only offline synthetic policy/parity work; cache only if approved source/data/code/Frozen/runtime/approval SHA-256 all match, otherwise fail-closed; only independent read-only postprocessing parallel; no dependent retraining/capital-transition parallelisation.
- Next: investigate `COMMON_OHLC_NONPOSITIVE` private rejected receipt and official KRX 2026-09-28 status via authorised independent read-only provenance; resolve failed chronology anchor; independently bind source SHA and exact public timestamp; rerun synthetic offline guard checks only. No source-PIT approval or M20 run until independent gates pass.
