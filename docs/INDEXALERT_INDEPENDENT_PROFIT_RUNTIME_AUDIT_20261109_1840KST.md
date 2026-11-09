# IndexAlert independent profitability and isolated optimisation audit — 2026-11-09 18:40 KST

## NEW independent production evidence — FAIL-CLOSED
- Railway IndexAlert production PIT rebuild service 225f2279-d728-4e1a-a3f3-2447ff0f9dc1, deployment 8b354fc1-cfb2-4ef0-863e-67f7f5dda2b5, direct deploy log timestamp **2026-11-09T09:30:20.344233001Z** (18:30:20 KST).
- Structured `INDEXALERT_PROSPECTIVE_RUNTIME` receipt: `status=FAIL_CLOSED`, `error_class=KRXProspectiveOpenAPISourceError`, `error_reason_code=COMMON_OHLC_NONPOSITIVE`, `source_failure_session=2026-09-28`, `session=2026-11-09`, `common_stock_rows=803`, `nonpositive_ohlc_rows=27`, `zero_volume_value_rows=27`, `all_zero_ohlc_rows=0`, `session_manifest_sha256=null`, `private_rejected_source_receipt_saved=true`.
- The same live log reports `ordering=DISABLED`, `live_order_authorized=false`, `real_orders_authorized=false`, `funds_movement_authorized=false`, `permission_change_authorized=false`, `fresh_alpha_observation_admitted=false`, `independent_chronology_admission_verified=false`, `independent_model_admission_verified=false`, `independent_source_admission_verified=false`. **PASS for observed fail-closed safety response only**; NOT a proof of environment variable `ORDERING=false` or a general security guarantee. **FAIL** for source admission / chronology anchor; do not silently filter 27 observations, reclassify official sessions or alter Frozen gates.
- Read-only KRX worker and Kiwoom REAL readonly deploy logs 08:30–09:45 UTC returned 0 entries; this does not establish inactivity. Runtime logs returned 201 quote/display entries, not official PIT/economics proof.

## Chronology anchor root-cause evidence
- GitHub Actions https://github.com/kims34/openpilot-opkr/actions/runs/41515392296 auto-anchor job 125517531544 direct decoded log: `ANCHOR_URL=https://indexalert-pit-rebuild-production.up.railway.app/anchor/latest`; after retries the job terminates at 2026-11-02T20:40:58Z with `urllib.error.HTTPError: HTTP Error 404: Not Found`, exit 1. Validation job 125517534895 SKIPPED.
- This is **PASS** for identifying the HTTP 404 observed failure mode, **NOT VERIFIED** for whether endpoint routing, published artifact, session freshness, or another upstream issue is the underlying cause. No workflow or endpoint modification attempted. Treat chronology anchor FAIL, not an approved PIT timestamp.

## GitHub and optimisation CI
- Exact branch-name search found `index-alert-research-v1` and `index-alert-position-regen-fix-v1`; branch-tip HEAD SHAs not independently returned by that API. Earlier tip SHAs are historical only.
- GitHub PR search returned no matches on this run; current PR #412/#413/#414/#418 and KRX #420/#422/#423 state, Draft and exact HEAD **NOT VERIFIED this run**. Do not infer closure from an empty search response. Historical PR references retained only as historical.
- Direct job-list verification: https://github.com/kims34/openpilot-opkr/actions/runs/38381997417 6/6 SUCCESS; https://github.com/kims34/openpilot-opkr/actions/runs/38382214223 6/6 SUCCESS; https://github.com/kims34/openpilot-opkr/actions/runs/38419111311 6/6 SUCCESS; https://github.com/kims34/openpilot-opkr/actions/runs/38419649711 1/1 SUCCESS; https://github.com/kims34/openpilot-opkr/actions/runs/38419439742 2/2 SUCCESS.
- Prior fixed 34-case SHA-256 `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34`, 13 adversarial mocks, 28 synthetic cases, serial 2.9656s vs concurrent 2.6209s = 1.1315x regression phase: **historical evidence, not recomputed**. Full CI and official backtest acceleration NOT VERIFIED. Only offline synthetic software/policy tests permitted.

## Railway runtime and controls
- Production project `d1c1a050-b7d6-41ce-b300-13c20f82a20a`, environment `83d5840b-270e-4d3f-a941-a37fd4a55ff7`. PIT rebuild and Runtime 1 running / 0 crashed each. KRX worker 0 running / 0 crashed of 1. Kiwoom REAL readonly UI online, deploy SUCCESS but 0 running / 1 crashed of 1: runtime-health **FAIL**. db-query-readonly offline with 1 critical; backend offline 4 warnings; push offline 1 warning.
- `describe_environment.staged=null` conflicts with `environment_status.pendingWork` empty staged patch `e113dacb-6705-4416-9997-dc694539d382`; **NOT VERIFIED** reconciliation. Do not apply patch.
- No deploy, merge, credential change, account permission change, live order or funding action performed.

## Profitability evidence gate — NO-GO
- Historical OpenDART SGML 15 original/amended candidate rows and numeric adjacency: narrow historical PASS, but original-filing semantic interpretation, exact public available-at/PIT, 2021/2022 first-three-month consolidated operating-profit period and amendment lineage NOT VERIFIED.
- Historical private KRX 2017–2022 1565/1565 weekday pair storage integrity: narrow historical PASS, but official calendar, stock state, corporate actions, mapping, feasible fills, fees and tax NOT VERIFIED. Exclude 90 unresolved sessions and 12003 zero-activity records.
- After-tax NetEV, PF, CAGR, MDD, ES95/99, concentration, temporal robustness NOT VERIFIED; M20 PIT/economic RUN NO-GO. H5 failed/consumed holdout and Dynamic outcomes not reused.
- Frozen H5, M20 horizon20/purge20, WF504/126/126, PIT/labels/Purged/CPCV/independent Holdout/Champion/Top3/NO_TRADE and cost/tax/risk/promotion criteria unchanged. Cache only fail-closed with independently approved source/data/code/Frozen/runtime/approval SHA-256 identity. Only read-only postprocessing may parallelise; never dependent retraining or capital transitions.

## Next permitted steps
1. DART owner: independent original filing and amendment public-availability timestamps plus exact content SHA and 2021/2022 period lineage.
2. KRX owner: independent official calendar/status/corporate-action/feasible fill source receipts; investigate 2026-09-28 27 common-stock nonpositive OHLC rows without modifying exclusions.
3. PIT runtime owner: read-only inspection of /anchor/latest 404 cause and current session manifest; do not alter workflow or claim anchor admission.
4. Railway owner: investigate crashed Kiwoom REAL readonly replica and staged-state discrepancy in read-only mode.
5. Verify current PR/branch HEAD through a trustworthy API before making SHA provenance claims. No official economic or model experiment before source PIT approval.
