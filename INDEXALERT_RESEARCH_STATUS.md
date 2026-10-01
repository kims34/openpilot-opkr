# IndexAlert Research Status

Updated: 2026-10-01 KST  
Branch: `index-alert-research-v1`  
Master authority: `INDEXALERT_MASTER_SPEC.md`  
Experiment authority: `INDEXALERT_RESEARCH_LEDGER.md`  
Promotion authority: **none yet**.

## Current bottom line

The current price/volume/context stack is **not ready for live short-term investment recommendations**. PIT discipline, CA-safe returns, frozen Top3/no-backfill, realistic costs, abstention, anchored purged walk-forward, corrected CPCV and reproducible CI are implemented, but robust recent execution-ready edge is not established.

Do **not** relax q25, TopK, costs, recent-evidence requirements, horizon, fill/capacity assumptions or holdout rules merely to create trades.

## Frozen research policy

- H5 = Core development horizon.
- H10 = `REJECTED_CURRENT_CANDIDATE_DO_NOT_RETUNE`; no H6-H9 sweep or H10 retune from completed outcomes.
- H20 = outside requested 5-10-session scope; archive only.
- Anchored walk-forward = train 504 / calibration 126 / test 126 with horizon-matched purge/embargo.
- Correct CPCV = six contiguous groups, all two-test-group combinations, each remaining group once as calibration, other three train = **60 cases per horizon**.
- Original decision-time Top3 frozen; vetoed/held/unfillable slots remain empty; **no rank-4+ backfill**.
- 0..3 trades and `NO_TRADE` valid.
- Corporate-action-safe KRX base-price returns mandatory.
- Primary evidence = executable cost-adjusted NetReturn/NetEV, PF, date-cluster uncertainty, MDD/ES/tails, cost stress, coverage/abstention, execution/capacity realism and recent evidence.
- One-shot sealed holdout remains untouched until source/execution/code/protocol blockers are frozen. After a valid holdout: prospective trading-policy Shadow S1 -> frozen Fresh Confirmation S2.

## Current empirical reference and frozen negative evidence

### H5 developmental reference — not promotable

- 278 executed entries / 137 trade days
- mean NetReturn **+1.150%**, PF **1.546**
- date-cluster 95% lower bound below zero
- 2x-cost mean **+0.787%**, PF **1.344**
- portfolio total **+16.39%**, CAGR ~1.83%, MDD **-24.39%**, Sharpe ~0.23
- admissions concentrated in 2018-2021
- no admissions in 2022-2026/latest 504 OOS sessions
- remove-best-5 turns mean negative and PF below 1

Classification: `DEVELOPMENTAL_NOT_CURRENTLY_PROMOTABLE`.

### Uncertainty Audit

`EXP-2026-09-29-UNCERTAINTY-AUDIT-01`, Action `36637333875`: **KEEP_ABSTENTION**.
- all-OOS q25-blocked mean -0.8432%, PF 0.8425;
- 2022+ q25-blocked mean -1.2551%, PF 0.8005;
- latest-504 blocked mean -0.6263%, PF 0.9012; remove-best-5 -1.2697%, PF 0.8011;
- latest conservative-positive subset: 4 rows, mean -22.5669%, PF 0.1381.

Do not weaken q25 or launch a conditional-q25 rescue from this result.

### Policy-aligned calibration

`EXP-2026-09-29-POLICY-CAL-01`, Action `36643183157`: **ADOPT STRUCTURAL ALIGNMENT / NO PERFORMANCE CHANGE / NOT PROMOTION EVIDENCE**. Reference and challenger selected the same 278 records with identical compact economics.

### Corrected 60-case CPCV

Action `36637351334`: **CPCV_DOES_NOT_ESTABLISH_ROBUST_EDGE**.
- H5 median PF 0.381; positive NetEV 43.3%; positive date-cluster LCB 11.7%.
- H10 median PF 0.745; positive NetEV 50.0%; positive date-cluster LCB 33.3%.

Older 15-combination CPCV and conflicting old-chat recollections are superseded. Rolling-160 and CA-safe path challengers remain rejected; H10 remains do-not-retune; H20 archive only. Stop price-only threshold/feature mining.

## KRX source gates A-F — frozen and machine-audited

Canonical gates:
- Gate A — `AUTHORIZED_OFFICIAL_ROUTE`
- Gate B — `EXACT_DATASET_SCHEMA_MAPPING`
- Gate C — `HISTORICAL_COVERAGE_SECURITY_MAPPING`
- Gate D — `PIT_AVAILABILITY_LINEAGE`
- Gate E — `REPRODUCIBLE_INTEGRITY_FAIL_CLOSED`
- Gate F — `INTENDED_USE_RIGHTS`

Only `PASS` closes a gate. All six passing closes only the source contract for the declared scope; it does not authorize Alpha/Final-Judge promotion, sealed holdout or live trading.

Current states remain:
- **Security/status:** A BLOCKED, B PARTIAL, C BLOCKED, D BLOCKED, E PARTIAL, F PARTIAL; `judge_security_status_ready=false`.
- **Investor flow:** A BLOCKED, B PARTIAL, C BLOCKED, D PARTIAL, E PARTIAL, F PARTIAL; `feature_performance_testing_authorized=false`.

Machine-readable public evidence remains version `2026-10-01.v1`, fingerprint:
`349d310647c78412e45ac13078259bab2d002958db597b2f7dd26228f8b3ca7b`.

## KRX authorization and source-data pipeline

The authorization boundary remains three separate layers:
1. route-specific credentials;
2. matching validated non-secret structured authorization evidence;
3. exact per-run consent for one tiny authenticated request.

Canonical runtime/configuration names are `KRX_AUTH_EVIDENCE_JSON` for the structured non-secret authorization record and `KRX_EXPLICIT_PROBE_CONSENT` for the exact per-run request-consent sentinel. An opaque approval reference alone is not validated evidence.

Canonical components include:
- `research_v1_krx_authorization_evidence.py`
- `research_v1_krx_auth_readiness.py`
- `research_v1_krx_auth_preflight.py`
- `research_v1_krx_status_source_probe.py`
- `research_v1_krx_investor_flow_probe.py`
- `research_v1_krx_acquisition_receipt.py`
- `research_v1_krx_acquisition_batch.py`
- `research_v1_krx_investor_flow_lineage.py`
- `research_v1_krx_investor_flow_coverage.py`
- `research_v1_krx_status_coverage.py`
- `research_v1_krx_status_event_integrity.py`
- `research_v1_krx_source_data_admission.py`

Frozen future source flow:
`structured authorization-evidence validation -> network-free auth readiness -> explicit manual request consent -> authorization preflight -> tiny authenticated probe/acquisition -> immutable receipt -> consistent batch -> PIT lineage -> exact expected-scope coverage -> A-F audit -> source-data admission -> separate experiment-registry/preregistration review`.

Push workflows remain dry-run only. No authenticated KRX request has yet been demonstrated; **Gate A remains BLOCKED**. Real route credentials, genuine approval evidence, full history, stable IDs, record-level PIT evidence and exact use rights remain external blockers.

Latest source-governance reference: KRX integrity Action `36817784717` at `bc5792640e0ba611f50f459f8c3b17c108cdd4bf` succeeded with structured authorization provenance through source-data admission. Documentation/handoff drift repairs later passed Action `36835918274`.

## Exact KRX status economics — internal audit implemented, real evidence missing

Final Judge requires exact halt/delisting economics. Structural status-event consistency or daily price history is not sufficient.

Canonical contract: `INDEXALERT_KRX_STATUS_ECONOMICS_CONTRACT.md`.  
Executable audit: `research_v1_krx_status_economics.py`.

The audit requires independently attested complete affected-position scope, exact position-ID coverage, quantity conservation, accepted actual execution/recovery evidence, explicit fees/taxes, timezone-aware economic availability and matching source-contract lineage. It rejects backtest/synthetic/modelled fills, market-open assumptions, Shadow/Paper fill substitution, daily OHLC and MDCSTAT239 daily price rows as proof that an IndexAlert order filled.

Even `exact_status_economics_ready=true` is only one Final-Judge input and does not itself set Judge readiness, promotion, holdout or live authority.

Implementation tests passed Action `36834108231`. Contract drift initially failed in `36834285722` only because human-readable wording omitted a canonical forbidden-source identifier; the document was corrected without changing policy. Action `36834718544` then succeeded.

**Project-level exact halt/cleanup/delisting economics remains OPEN** because no real complete affected-position economics dataset has been supplied.

## Execution evidence — structural LIVE evidence is not empirical sufficiency

Canonical contract: `INDEXALERT_EXECUTION_EVIDENCE_CONTRACT.md`.

Evidence tiers remain:
1. `PROSPECTIVE_SHADOW_DECISION_LOG` — decisions only, no broker fills.
2. `PROSPECTIVE_PAPER_EXECUTION_LOG` — paper/simulation plumbing evidence, not real fill quality.
3. `PROSPECTIVE_LIVE_EXECUTION_LOG` — real-account executions; the only tier eligible to contribute raw empirical live fill/slippage/partial-fill/latency/markout/capacity evidence.

`research_v1_execution_evidence.py` separates `live_structural_execution_evidence_present` from empirical execution sufficiency. One or several LIVE rows can never automatically close the empirical blocker. Until a separately frozen protocol is evaluated:
- `live_empirical_execution_evidence_ready=false`;
- `empirical_execution_sufficiency_assessed=false`;
- `empirical_execution_blocker_closed=false`;
- `promotion_ready=false`.

Execution integrity Action `36834616144` succeeded after freezing this separation.

## Execution-sufficiency preregistration — validator implemented, project thresholds not yet frozen

`research_v1_execution_sufficiency_protocol.py` prevents post-hoc execution-threshold selection. It validates a future protocol's explicit criteria, document fingerprint and required dimensions, and requires `frozen_at` to be **strictly earlier** than the first LIVE recommendation that protocol will judge.

It requires future criteria to explicitly cover live observation count, distinct dates, filled/no-fill/partial-fill evidence, 5m/30m/close markouts, slippage, latency, capacity and tail evidence. Unit-test threshold numbers are test fixtures only and are **not IndexAlert promotion thresholds**.

A structurally valid protocol still keeps sufficiency unassessed and blocker/promotion/holdout/live authority false. The actual project sufficiency criteria must be separately decided and frozen before the LIVE observations they will evaluate.

Execution preregistration Action `36835013828` succeeded. Strengthened contract-drift Action `36835231533` also succeeded.

## Android / push Physical E2E state

Current Android build branch is `index-alert-build`, HEAD `396501f9df3bdf4fd7cea4a2c97116a02f8961d5`. The audited build is `versionName=4.6`, `versionCode=46`, therefore self-test `client_build=4.6-46`.

Latest APK Action `36815959241` succeeded:
- debug `IndexAlert-v4.6-debug`, artifact ID `11141577031`, SHA256 `d32c468bb3f719dcdafe99f3614358723cceeb566239bbedbbb3927c6f740dbf`;
- unsigned release `IndexAlert-v4.6-unsigned-release`, artifact ID `11141532240`, SHA256 `b95c8f28417c1b3f901ad2c0768970ae2942f2167ed49e9373f3666a4edf19a6`.

The Android receipt path schedules privacy-safe `/push-ack` for the exact server event and only marks the build self-test complete after `receipt_confirmed=true`. Provider send success is never treated as handset receipt.

Server branch `index-alert-server` now has audited HEAD `b592e04802fc4f9f015ac1f9881ba9ad9da0fa07` (`Run Physical E2E verifier in server CI`). The server self-test reuses one event per token/build and never re-sends a successful provider send merely because handset receipt is pending. `/push-ack` is bound to a registered token hash plus an already-sent exact event and is idempotent.

`/push-health` binds confirmation to the latest created Android build self-test instead of aggregate receipt history. Its build-specific fields are `latest_self_test_build`, `latest_self_test_sent`, `latest_self_test_receipt_confirmed`, `latest_self_test_created_at`, and `current_build_physical_e2e_confirmed`. Tests explicitly prove an older-build ACK cannot confirm the newer build. Read-only verifier `verify_push_physical_e2e.py` requires the exact expected build and cannot send FCM, register a device, or write a receipt.

Latest server CI Action `36837589631` at `b592e048...` succeeded. It compile/tests the Physical-E2E verifier and the server push/receipt contract.

Exact Physical E2E closure for the current audited app requires a real handset path showing at the test point:
- `latest_self_test_build == "4.6-46"`;
- `latest_self_test_sent == true`;
- `latest_self_test_receipt_confirmed == true`;
- `current_build_physical_e2e_confirmed == true`;
- a non-null real client receipt timestamp/ledger row.

Aggregate `received_deliveries >= 1` alone is insufficient because it may belong to an older build. Firebase provider send success is not handset receipt evidence.

### Current production observation — Physical E2E still OPEN

Railway production now runs deployment `3b1df2eb-df74-42fd-b7cb-5e50edb23c59`, built from server commit `b592e04802fc4f9f015ac1f9881ba9ad9da0fa07`. The deployment completed successfully. The strengthened production-smoke rerun, Action `36836821948` job `110321079146`, also succeeded, proving the new build-specific `/push-health` contract is actually live in production.

At that smoke observation, production reported:
- `registered_devices = 1`;
- `sent_deliveries = 1`;
- `received_deliveries = 0`;
- `unconfirmed_sent_deliveries = 1`;
- `last_client_receipt_at = null`;
- `latest_self_test_build = null`;
- `latest_self_test_sent = false`;
- `latest_self_test_receipt_confirmed = false`;
- `current_build_physical_e2e_confirmed = false`.

Therefore deployment drift is CLOSED, but Physical E2E remains OPEN. More specifically, production has **no current latest Android self-test row at all** yet; this is stronger than merely having a sent `4.6-46` self-test with a missing ACK. The existing aggregate sent delivery cannot be reclassified as a current-build self-test.

No physical receipt is fabricated or inferred from provider send success.

## Operational deployment evidence state

Railway `indexalert-runtime` is now aligned to server commit `b592e04802fc4f9f015ac1f9881ba9ad9da0fa07` through deployment `3b1df2eb-df74-42fd-b7cb-5e50edb23c59` (SUCCESS). Production-smoke rerun job `110321079146` in Action `36836821948` succeeded after the deployment and verified the new health schema in the live service.

This closes the prior server deployment-drift blocker only. It does not close the Physical E2E blocker, execution evidence blocker, KRX blockers, sealed holdout, promotion, or live-order authority. Real-account ordering remains disabled.

## External evidence still missing

Internal code cannot fabricate approved KRX source access/history/PIT/use rights, real complete affected-position status economics, genuine staged LIVE execution observations, a later independent execution-sufficiency assessment, or a real current-build handset receipt.

## Remaining blockers

1. **KRX authorization/data:** approved route/product, credentials/structured approval evidence, authenticated source proof and full official history.
2. **Security/status economics:** real complete affected-position fill/recovery economics must pass the exact audit; the internal auditor alone does not close the blocker.
3. **Investor flow:** real full official history must pass provenance, PIT, coverage, A-F and source-data admission; then separate preregistration before any feature-performance experiment.
4. **Execution:** genuine staged LIVE observations plus a separately frozen-before-LIVE sufficiency protocol and later assessment. Structurally valid LIVE rows alone do not close this blocker.
5. **Research governance:** no rejected-candidate revival; maintain Ledger/multiple-testing discipline.
6. **One-shot sealed holdout:** untouched until source/execution/code/protocol freeze; then Shadow S1 -> Fresh Confirmation S2.
7. **Physical notification E2E:** deployment drift is closed, but production currently has `latest_self_test_build=null`; a real v4.6-46 handset must create the exact self-test and ACK path satisfying the build-specific criteria above.
8. **Live ordering:** disabled until all frozen promotion/safety gates and explicit user activation requirements are met.

## Promotion rule

Positive mean, PF or CAGR alone cannot promote a candidate. Promotion requires cost-adjusted OOS economics, PF > 1, positive date-cluster lower bound, best-day robustness, credible recent evidence, acceptable MDD/ES/tails, cost-stress survival, PIT correctness, official source/status integrity and execution realism. Final promotion additionally requires the one-shot sealed holdout and prospective confirmation sequence.
