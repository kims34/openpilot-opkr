# IndexAlert independent profit/runtime audit — 2026-11-05 21:23 KST

Read-only evidence snapshot; independent isolated documentation only. No model, backtest, workflow, trading, deployment or PR merge action.

## Exact refs
- research branch `index-alert-research-v1`: `df474df348f22aa38b1dedaa59fcff66e548b406` (GitHub compare self-ref)
- development branch `index-alert-position-regen-fix-v1`: `1e6367d2863a86c3470da13d81a955d277eba485`
- default `HKG_community`: `f17283d9a5f0427c3d5b8a865d39455f92ee2f1d`
- PR #412/#413/#414/#418 and KRX #420/#422/#423 exact HEAD/state: NOT VERIFIED in this run; prior historical reports not treated as fresh verification.
- Integration gate file fetch on research branch returned GitHub 404: document content NOT VERIFIED (not evidence of absence across PR refs).

## GitHub Actions read-only jobs (verified this run)
- 38381997417: 6/6 success
- 38382214223: 6/6 success
- 38419111311: 6/6 success
- 38419649711: 1/1 success
- 38419439742: 2/2 success
- 41515392296: auto-anchor failure, validation skipped.
- Historical 34-case fixed SHA `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34`, 13 adversarial mocks, 28 synthetic tests, and 2.9656s/2.6209s=1.1315x are prior reported evidence, not independently recomputed now. Overall CI and official backtest acceleration: NOT VERIFIED.

## Railway production (read-only, 2026-11-05)
Project `d1c1a050-b7d6-41ce-b300-13c20f82a20a`, environment `83d5840b-270e-4d3f-a941-a37fd4a55ff7`.
- PIT rebuild deployment `8b354fc1-cfb2-4ef0-863e-67f7f5dda2b5`: SUCCESS; KRX historical worker `16c93d7c-7cd0-4d84-a327-298d2805376c`: SUCCESS. Deployment SUCCESS is not data admission.
- Latest PIT log at `2026-11-05T12:16:08.368021848Z`: `status=FAIL_CLOSED`, `error_reason_code=COMMON_OHLC_NONPOSITIVE`, source_failure_session `2026-09-28`, 803 common stock rows, 27 nonpositive OHLC rows, 27 zero volume/value rows, all_zero_ohlc_rows=0; `session_manifest_sha256=null`, `fresh_alpha_observation_admitted=false`, `independent_source_admission_verified=false`, `ordering=DISABLED`, `private_rejected_source_receipt_saved=true`. Earlier logs 10:00–12:16 UTC repeat the same error.
- KRX worker deploy logs since 10:00 UTC: 0 entries, not proof of no activity.
- Runtime latest sampled 12:23 UTC: Yahoo USD/KRW fallback after Investing HTTP errors, QQQ/SPY premarket; not an approved PIT source.
- Backend and push latest deployments FAILED; production pendingWork contains staged patch `e113dacb-6705-4416-9997-dc694539d382`, untouched. numReplicas null in status response, so live instance count NOT VERIFIED.

## Independent gate verdict
- Rejection/fail-closed of invalid KRX source: PASS (observed).
- 2026-09-28 source session admissibility: FAIL (observed); official KRX calendar, trade status, corporate actions, economic execution feasibility: NOT VERIFIED.
- Original-filing/public available-at, 2021/2022 consolidated 3-month operating-profit lineage, historical issuer/security mapping: NOT VERIFIED.
- Cost/tax-aware NetEV, PF, CAGR, MDD, ES95/99, concentration, walk-forward robustness, independent Holdout and risk-adjusted annual net profit: NOT VERIFIED.
- M20: NOT EVALUABLE / NO-GO; no PIT profitability run authorised. H5 consumed/failed holdout cannot be recycled.
- Frozen H5; M20 horizon20/purge20; WF504/126/126; Purged/CPCV/Holdout/Champion/Top3/NO_TRADE, costs, taxes, execution and promotion rules unchanged. ORDERING=false.
- Cache requires independent source/data/code/Frozen/runtime/approval SHA-256 parity and fail-closed; parallelise only read-only independent postprocessing. No dependent retraining or capital transition parallelisation.

## Next safe work
Independently obtain official KRX 2026-09-28 session/trading-status/corporate-action source and match all 27 rejected rows to original identifiers and raw SHA before considering source admission. Verify PR HEADs, #414 gate text and source PIT lineage read-only. Recheck CI artefacts and immutable SHA; only offline synthetic safety tests until PIT admission. No production changes, workflow edits, merging, trading, permissions or Champion promotion.
