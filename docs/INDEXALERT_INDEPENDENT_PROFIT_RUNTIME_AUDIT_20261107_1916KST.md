# IndexAlert independent profit / isolated optimizer audit — 2026-11-07 19:16 KST

Scope: read-only evidence inspection; no production, model, strategy, workflow, broker, account or trading writes. This document is a separate isolated audit and is not a gate approval.

## Source refs verified this run
- Research `index-alert-research-v1` HEAD `df474df348f22aa38b1dedaa59fcff66e548b406`.
- Development `index-alert-position-regen-fix-v1` HEAD `1e6367d2863a86c3470da13d81a955d277eba485`.
- Draft OPEN, unmerged PRs #412/#413/#414/#418/#420/#422/#423; #414 HEAD `18c5418d9684d1717df58261ea27f28e514385b2`. #414 gate blob `984c933651f39f1ee9e26a1d7ac3893aaa5335be`.
- GitHub Actions job results directly queried: #38381997417 6/6 PASS; #38382214223 6/6 PASS; #38419111311 6/6 PASS; #38419439742 2/2 PASS; #38419649711 1/1 PASS; #38498552499 6/6 PASS. These are CI job conclusions, **not** source PIT or economic admission. #41515392296 auto-anchor FAIL, validation SKIPPED.
- Historical 34-case reference SHA `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34` and synthetic 28/13 cases are previously reported; test-content digest was not independently recalculated this run.

## New independently observed Railway evidence
Production project `d1c1a050-b7d6-41ce-b300-13c20f82a20a`, environment `83d5840b-270e-4d3f-a941-a37fd4a55ff7`. `get_status` reports stagedChanges=null yet pendingWork has empty-change patch `e113dacb-6705-4416-9997-dc694539d382`; `describe_environment` reports staged=null. Do not commit patch.

`indexalert-pit-rebuild` service `225f2279-d728-4e1a-a3f3-2447ff0f9dc1`, deployment `8b354fc1-cfb2-4ef0-863e-67f7f5dda2b5` (deployment SUCCESS), logged 2026-11-07 09:30:30, 09:45:29, 10:00:36, 10:15:34 UTC: `status=FAIL_CLOSED`, `error_class=KRXProspectiveOpenAPISourceError`, `error_reason_code=COMMON_OHLC_NONPOSITIVE`, `common_stock_rows=803`, `nonpositive_ohlc_rows=27`, `zero_volume_value_rows=27`, `source_failure_session=2026-09-28`, `session_manifest_sha256=null`, `independent_source_admission_verified=false`, `independent_chronology_admission_verified=false`, `independent_model_admission_verified=false`, `fresh_alpha_observation_admitted=false`, `ordering=DISABLED`, `live_order_authorized=false`. This is **positive evidence of an active fail-closed source blocker**, not merely absence of verification. The 27 count is a source rejection count; no market-value interpretation permitted.
- KRX historical worker and Kiwoom real-readonly had zero deploy log entries within 2026-11-07 08:00 UTC onward; absence is not proof of service health. Runtime returned logs including Yahoo USDKRW fallback and extended-session unavailable; these quotes are not approved backtest inputs.
- Railway latest deployment SUCCESS for PIT/KRX/Runtime/real-readonly is not equivalent to live replica health. Replica state was not independently queried this run.

## Admission decisions
- Official original filing/public available-at, 2021/2022 initial consolidated Q1 operating income and correction lineage: NOT VERIFIED.
- Historical issuer/security mapping, official KRX calendar/status/corporate actions/executability and costs/taxes: NOT VERIFIED. Previously reported 1565/1565 private weekday-pair integrity PASS is limited to storage, not trading admission.
- PIT source gate: FAIL/CLOSED on current prospective source receipt (27 OHLC failures); economic M20 admission: NO-GO.
- NetEV, PF, CAGR, MDD, ES95/99, concentration, time robustness: NOT VERIFIED; do not run M20 or reuse consumed H5 Holdout.
- Optimizer isolated synthetic regression jobs: PASS as CI only; whole-CI speedup and real official-backtest speedup NOT VERIFIED. Existing single-runner 2.9656s versus 2.6209s concurrent suite implies 1.1315x regression-phase ratio, not proven speedup.
- Frozen H5, M20 horizon20/purge20, WF504/126/126, PIT/labels/Purged/CPCV/Holdout/Champion/Top3/NO_TRADE unchanged. Cache requires exact independent approved source/data/code/Frozen/runtime/evidence SHA-256 match and fail-closed behavior. Only read-only postprocessing parallelizable.
- ORDERING=false, no deployment/merge/order/funds/credential/Champion changes.

## Next read-only actions
1. Compare the four current FAIL_CLOSED receipts with immutable official KRX source rows and independent chronology evidence; do not alter data or admission.
2. Investigate chronology-anchor #41515392296 failure routing and validation skipped from original logs, without workflow edits.
3. Inspect real-readonly replica health and any critical alert with read-only health endpoints; no restarts.
4. Confirm actual runner test digest and cache invalidation with synthetic offline-only checks; no new performance search or official market economics.
