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

Current Android build branch is `index-alert-build`, HEAD `5154ef7943353791f615622394523ecd52ef8b0f`. The audited build is `versionName=4.7`, `versionCode=47`, therefore `client_build=4.7-47`.

Latest APK Action `36856589300` succeeded:
- debug `IndexAlert-v4.7-debug`, artifact ID `11158994269`, SHA256 `0aec298a0d0276f8a5e40dc22429b595e8bb11636f22ceeea75cb018a4a7e411`;
- unsigned release `IndexAlert-v4.7-unsigned-release`, artifact ID `11159209190`, SHA256 `77f7ba0acb991ae48827dcac8658b917fe60edc0ec677ae4548d8e797c8f4780`.

The v4.7 Android client sends its privacy-safe `client_build` during registration and uses the build-specific self-test/receipt path. Provider send success is never treated as handset receipt; confirmation requires the actual client `/push-ack` for the exact server event.

Server branch `index-alert-server` currently has operational HEAD `b43b478bc624925b0fd58d5986f8fd293ae2d65f` (`Test fail-closed legacy registration ordering`). The shared build-registration overlay is installed by both v31 and v32 entrypoints, and production uses `production_v32:app`.

Frozen Physical-E2E contracts are:
- `registration_build_contract = "register-client-build-v1"`;
- `self_test_trigger_contract = "android-register-direct-v1"`;
- `physical_e2e_binding_contract = "registered-device-build-receipt-v1"`;
- `physical_e2e_blocker_contract = "physical-e2e-blocker-v1"`.

The server binds Physical E2E to the exact latest registered **device and build**. A same-build receipt from another device, an older-build receipt, or a newer legacy/unknown-build registration all fail closed. A legacy registration with no `client_build` is preserved as the latest unknown-build observation so it cannot resurrect an older build-aware device as the apparent latest candidate.

`/push-health` exposes privacy-safe diagnostics including `latest_registered_client_build`, `latest_self_test_build`, `latest_self_test_sent`, `latest_self_test_receipt_confirmed`, `registration_device_matches_self_test`, `registration_build_matches_self_test`, `physical_e2e_blocker`, and `current_build_physical_e2e_confirmed`. Raw token/event IDs remain server-private.

The blocker is exactly one of `NO_REGISTERED_BUILD`, `NO_SELF_TEST`, `DEVICE_MISMATCH`, `BUILD_MISMATCH`, `SELF_TEST_NOT_SENT`, `RECEIPT_PENDING`, `CONFIRMED`.

Read-only verifier `verify_push_physical_e2e.py` requires the exact expected registered build, same-device/same-build binding, all frozen contract markers, sent self-test, real receipt timestamp and `physical_e2e_blocker == "CONFIRMED"`; it cannot send FCM, register a device, or manufacture a receipt.

Server Tests Action `36868822598` succeeded at exact HEAD `b43b478b...`, with **159 tests** passing. v32 Build Contract Smoke Action `36868822607` initially timed out only because Railway completed the exact-source rollout just after the first run's 30-attempt window. Rerun job `110397147003` succeeded after production was on the exact revision.

### Current production observation — Physical E2E still OPEN

Railway production now runs deployment `10d09f6a-daec-45cb-b5fa-25b7e192d405`, built from exact server commit `b43b478bc624925b0fd58d5986f8fd293ae2d65f`. The service start command is `production_v32:app`, and the successful rerun smoke observed `runtime_revision = "b43b478bc624925b0fd58d5986f8fd293ae2d65f"`.

At the successful exact-revision smoke observation, production reported:
- `registration_build_contract = "register-client-build-v1"`;
- `self_test_trigger_contract = "android-register-direct-v1"`;
- `physical_e2e_binding_contract = "registered-device-build-receipt-v1"`;
- `physical_e2e_blocker_contract = "physical-e2e-blocker-v1"`;
- `physical_e2e_blocker = "NO_REGISTERED_BUILD"`;
- `latest_registered_client_build = null`;
- `latest_self_test_build = null`;
- `registration_device_matches_self_test = false`;
- `registration_build_matches_self_test = false`;
- `current_build_physical_e2e_confirmed = false`.

Therefore server deployment/configuration drift is CLOSED, but Physical E2E remains OPEN for one precise reason: production has not yet observed a current build-aware v4.7-47 handset registration. Older aggregate sent/received counters cannot be reclassified as current-build evidence.

Exact Physical E2E closure now requires one real handset running `4.7-47` to produce, on that same registered device:
- `latest_registered_client_build == "4.7-47"`;
- `latest_self_test_build == "4.7-47"`;
- `registration_device_matches_self_test == true`;
- `registration_build_matches_self_test == true`;
- `latest_self_test_sent == true`;
- `latest_self_test_receipt_confirmed == true`;
- `physical_e2e_blocker == "CONFIRMED"`;
- `current_build_physical_e2e_confirmed == true`;
- a non-null real client receipt timestamp/ledger row.

No physical receipt is fabricated or inferred from provider send success.

## U.S. mover production-data integrity — fail-closed and auditable

Constituent mover quotes now require Yahoo instrument type `EQUITY`; index/ETF/fund/currency contamination is rejected before ranking. Corporate-action discontinuities are not removed by an arbitrary percentage threshold. They are suppressed only on a source-backed event/date registered in `corporate_action_registry.py` when raw previous-close comparison is economically non-comparable.

`/laggards` exposes per-universe exclusion provenance through `excluded_non_equity_symbols` and `excluded_corporate_action_symbols`. Final exact-revision Production Smoke Action `36853857418` verified the live contract:
- S&P500 coverage `502/503`, `excluded_corporate_action_symbols=["CTVA"]` on the documented 2026-10-01 CTVA/Vylor separation date;
- NASDAQ100 coverage `100/100`, no deliberate exclusion;
- SCHD coverage `98/99`, `excluded_non_equity_symbols=["USD"]`, preventing ProShares Ultra Semiconductors from masquerading as a stock constituent.

Direction/sign checks remained valid for all three universes. This is an operational data-integrity safeguard, not Alpha/promotion evidence and not a change to the frozen research statistics or KRX A-F state.

## USD/KRW startup basis integrity — fail-closed and exact-revision audited

The public USD/KRW day-change contract is versioned as `ecos-1530-fail-closed-v1`. A live current quote may remain available during startup, but before the Bank of Korea ECOS prior 15:30 close is completely verified the public comparison fields are forced to:
- `previous_close = null`;
- `previous_close_date = null`;
- `day_change = null`;
- `day_change_percent = null`;
- `basis_provider = null`;
- `basis_verified = false`.

`fx_basis.public_basis_fields()` accepts a public daily basis only when the prior close is finite/positive, the date and day-change fields are complete, `basis_verified=true`, and the provider explicitly identifies ECOS. Unit tests reject a Yahoo/provider fallback even if an older layer marks the shape as otherwise plausible. `/status` and `/history/usdkrw` use the same fail-closed sanitizer and expose the non-secret `basis_contract` marker.

The original exact-revision production validation of this FX contract was Production Smoke `36853857418`: it passed only after `runtime_revision == a416d64c3bc444fc6126a85db94bdaa1d2b346c2` and verified the ECOS-ready state with `basis_contract="ecos-1530-fail-closed-v1"`, `basis_verified=true`, `previous_close=1352.8`, `previous_close_date="2026-09-30"`, and an ECOS basis provider. Later server revisions retained the same tested FX sanitizer; current operational runtime alignment is tracked separately below.

The timing-sensitive smoke did **not** itself capture a complete public response during the short pre-ECOS transition; unit tests enforce the null-field transition contract. Internal startup logs may still show an older-layer Yahoo fallback calculation before the outer v3.1 sanitizer completes; that internal calculation is not accepted as the public official day-change basis.

## Operational deployment evidence state

Railway `indexalert-runtime` is aligned to exact server commit `b43b478bc624925b0fd58d5986f8fd293ae2d65f` through deployment `10d09f6a-daec-45cb-b5fa-25b7e192d405` (SUCCESS). Server Tests Action `36868822598` and v32 Build Contract Smoke `36868822607` rerun job `110397147003` succeeded on the exact production revision. The smoke verifies the current privacy-safe build/device/blocker push-health contract and exact runtime revision while preserving the existing market/probability endpoint contracts.

This closes server deployment drift, stale-runtime ambiguity, the latest-registration ordering gap, the mover-provenance observability gap and the public startup FX-basis leakage path. It does not close the Physical E2E blocker, execution evidence blocker, KRX blockers, sealed holdout, promotion, or live-order authority. Real-account ordering remains disabled.

## External evidence still missing

Internal code cannot fabricate approved KRX source access/history/PIT/use rights, real complete affected-position status economics, genuine staged LIVE execution observations, a later independent execution-sufficiency assessment, or a real current-build handset receipt.

## Remaining blockers

1. **KRX authorization/data:** approved route/product, credentials/structured approval evidence, authenticated source proof and full official history.
2. **Security/status economics:** real complete affected-position fill/recovery economics must pass the exact audit; the internal auditor alone does not close the blocker.
3. **Investor flow:** real full official history must pass provenance, PIT, coverage, A-F and source-data admission; then separate preregistration before any feature-performance experiment.
4. **Execution:** genuine staged LIVE observations plus a separately frozen-before-LIVE sufficiency protocol and later assessment. Structurally valid LIVE rows alone do not close this blocker.
5. **Research governance:** no rejected-candidate revival; maintain Ledger/multiple-testing discipline.
6. **One-shot sealed holdout:** untouched until source/execution/code/protocol freeze; then Shadow S1 -> Fresh Confirmation S2.
7. **Physical notification E2E:** server-side exact revision, same-device/build binding and fail-closed blocker contract are DONE; current blocker is `NO_REGISTERED_BUILD`. A real v4.7-47 handset must register, create the exact build self-test, receive it and ACK it on that same device until `physical_e2e_blocker == "CONFIRMED"`.
8. **Live ordering:** disabled until all frozen promotion/safety gates and explicit user activation requirements are met.

## Promotion rule

Positive mean, PF or CAGR alone cannot promote a candidate. Promotion requires cost-adjusted OOS economics, PF > 1, positive date-cluster lower bound, best-day robustness, credible recent evidence, acceptable MDD/ES/tails, cost-stress survival, PIT correctness, official source/status integrity and execution realism. Final promotion additionally requires the one-shot sealed holdout and prospective confirmation sequence.
