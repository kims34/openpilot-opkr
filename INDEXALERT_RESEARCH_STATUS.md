# IndexAlert Research Status

Updated: 2026-10-02 KST  
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
- **Security/status:** A PARTIAL, B PARTIAL, C BLOCKED, D BLOCKED, E PARTIAL, F PASS (personal/internal research scope only); `judge_security_status_ready=false`.
- **Investor flow:** A PARTIAL, B PARTIAL, C BLOCKED, D PARTIAL, E PARTIAL, F PASS (personal/internal research scope only); `feature_performance_testing_authorized=false`.

Machine-readable public evidence remains version `2026-10-02.v2`, fingerprint:
`39f357fda6eec5bb994f1dcba1ba44ed913714df256ec6b542b5aeadf14a0380`.

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

Push research-probe workflows remain dry-run only. Separately, production OpenAPI evidence now demonstrates authenticated GET access for the approved `유가증권 종목기본정보` and `유가증권 일별매매정보` services on basis date `20261001` (942 rows each, exact expected schemas; server revision `4714f8e2d47881b7ccc42d7add0bfebb67ce3bf5`, Smoke Action `36956234911`). Canonical evidence is `INDEXALERT_KRX_OPENAPI_CONNECTIVITY_EVIDENCE.md/.json`; `research_v1_krx_openapi_connectivity_evidence.py` fail-closed validates the committed evidence and forbids authority escalation. This OpenAPI evidence is separate from the later authenticated Data Marketplace tiny probes. Those probes move Gate A to `PARTIAL` for both declared source families; they still do not close full-history/PIT/source contracts. KRX permission evidence v3 now closes Gate F for the declared personal/internal-research scope. Remaining source blockers are actual full-history technical coverage, stable IDs across the required period, exact all-period route/schema equivalence, record-level PIT lineage and immutable acquisition provenance.

Latest authenticated OpenAPI plumbing/schema reference: production Smoke Action `36956234911` at server revision `4714f8e2d47881b7ccc42d7add0bfebb67ce3bf5` succeeded and recorded sanitized KRX response metadata plus per-service schema/payload SHA-256 fingerprints. Existing broad source-governance integrity reference remains Action `36817784717` at `bc5792640e0ba611f50f459f8c3b17c108cdd4bf`; documentation/handoff drift repairs later passed Action `36835918274`.

## KRX low-frequency internal-research reply evidence

The latest KRX permission evidence v3 states that personal research may use complete full-historical-period download/query plus programmatic/automated low- and high-frequency collection without a separate approval procedure, while external leakage, sale and third-party distribution are prohibited. Canonical evidence is `INDEXALERT_KRX_PERMISSION_REPLY_EVIDENCE.md/.json`; latest reply provenance is bound by redacted normalized SHA-256 `7361065e06599f947216233fc84e97126b1675de5af41068114cf6ef9577e304`. The exact timestamp of the latest v3 reply was not re-provided and is intentionally left unknown. Gate F is now PASS for the declared personal/internal-research scope.

## Data Marketplace automation-permission boundary

The Data Marketplace terms boundary remains frozen in `INDEXALERT_KRX_DATA_MARKETPLACE_TERMS_AUDIT.md/.json`: credentials alone never authorize automation. KRX permission v3 now establishes full-history/high-frequency rights for personal research. Network-free Action `36973737546` established tiny-probe readiness; the separately consented status Action `36976085781` and investor-flow Action `36976873119` subsequently completed successfully. A new, broader full-history network job is governed by the separate historical-acquisition plan/consent gate.

`research_v1_krx_authorization_evidence.py` now treats a Data Marketplace record without `automated_collection_authorized=true` as insufficient, and `research_v1_krx_auth_preflight.py` independently enforces the same requirement.

### Pinned Data Marketplace route map

`INDEXALERT_KRX_DATA_MARKETPLACE_ROUTE_MAP.md/.json` now records authenticated tiny-probe reachability for `MDCSTAT21301`, `MDCSTAT23701` and `MDCSTAT02303`. `MDCSTAT23701` remains provisional for the full historical contract. The route-map validator still rejects any attempt to self-grant Gate A/B PASS, holdout or live authority.

## Authenticated KRX status tiny probe

Action `36976085781` completed successfully under explicit one-run consent. The authenticated status route returned current security identity plus new-listing, delisted-history, trading-halt `MDCSTAT21301` and cleanup-trading `MDCSTAT23701` metadata. Gate A for `KRX_SECURITY_STATUS` is now `PARTIAL` rather than BLOCKED. Gate B remains `PARTIAL`; C/D remain BLOCKED; `judge_security_status_ready=false`. Canonical evidence is `INDEXALERT_KRX_STATUS_TINY_PROBE_EVIDENCE.md/.json`.

## Authenticated KRX investor-flow tiny probe

Action `36976873119` completed successfully under explicit one-run consent. `MDCSTAT02303` returned 3 rows for `005930` over `2026-09-21..2026-09-23` with the observed investor-category schema. Investor-flow Gate A is now `PARTIAL`; Gate B remains `PARTIAL`; Gate C remains `BLOCKED`; Gate D remains `PARTIAL`. Feature-performance testing remains unauthorized. Canonical evidence is `INDEXALERT_KRX_INVESTOR_FLOW_TINY_PROBE_EVIDENCE.md/.json`.

## Frozen KRX historical acquisition plan

`INDEXALERT_KRX_HISTORICAL_ACQUISITION_PLAN.md/.json` freezes the primary required source window `2015-06-15..2026-10-01` for KOSPI, preserving the existing long-history research protocol rather than silently expanding model evaluation. The plan defines identity reconstruction, 730-day halt chunks, calendar-year investor-flow chunks, PIT lineage, receipts/batches, private raw-data handling and bounded concurrency. KRX rights are confirmed, but actual bulk network execution remains separately gated by `research_v1_krx_historical_acquisition_preflight.py` and an exact user execution-consent sentinel.

## KRX historical worker implementation readiness

Internal implementation for the future private full-history job is now materially complete through the first executable stage:

- acquisition plan: `INDEXALERT-KRX-HIST-ACQ-v3`;
- execution contract: `INDEXALERT-KRX-HIST-EXEC-v3`;
- exact historical identity/standard-code reconstruction and request planner;
- raw-preserving Data Marketplace/OpenAPI fetch adapters;
- content-addressed private raw store, receipt/manifest/checkpoint and verified resume;
- canonical one-request executor;
- staged batch orchestrator;
- fail-closed private phase state;
- preflight-first one-shot worker entrypoint;
- dedicated worker Dockerfile and deployment contract `INDEXALERT-KRX-HIST-WORKER-DEPLOY-v1`.

Latest integrated KRX integrity reference for the worker deployment boundary: Action `36997637052` at research revision `190d914e14190077d55b14de6f2637bf1abf5d90` succeeded.

Since that reference, the expected-scope acquisition path has also been implemented and fail-closed hardened behind its own execution boundary: separate consent-gated worker entrypoint, content-addressed immutable per-date scope/receipt records, checkpointed resume, and explicit rejection of scope-path drift or tampered raw/receipt reconciliation. Expected-scope hardening revision `090271828fe0915e8bc9004c623eb848419ea62e` passed Official KRX Status Integrity Action `37009561566` with **397 passed, 1 warning**. The immediately preceding failures at `f2c9ead`, `db9dc8c`, and `ccaf6cd` were superseded by the green HEAD after fixing the content-addressed checkpoint test/verification path; no KRX bulk network acquisition was performed by these CI tests.

Railway provisioning and worker-secret setup are complete for the dedicated `indexalert-krx-historical-worker`: isolated service/volume, `Dockerfile.krx-historical-worker`, restart `NEVER`, no cron and no public domain. A Railway builder conflict was found and fixed by pinning the research-branch root `railway.json` to the worker Dockerfile; fresh preflight deployment `83be77ba-ccb1-4dcf-a40d-dd67a49fa9fb` at exact revision `6343f01b493404d59736e06eb6968e9820d0e595` then passed with all three credential-presence flags true and zero network requests.

The user separately authorized only the first 27-request `IDENTITY_SEED`. Fresh deployment `d268e5b0-b7c2-46be-b9ae-ca41d27cdb02` executed that stage on the exact pinned worker image and completed **27/27**, with zero resumes, 27 network requests, phase `COMPLETE`, task-set fingerprint `fb69ed44c2944911417dc26f088f0c5876942530a7c17abdd1fc38ee3f197aa1`, private-batch metadata fingerprint `054a9689adac7f57fa5a797f10ff9a69d3a7abd34a8697b624464588c6f0502f`, and `raw_rows_emitted=false`. Canonical sanitized evidence is `INDEXALERT_KRX_HISTORICAL_IDENTITY_SEED_EXECUTION_EVIDENCE.md/.json`.

Immediately after completion, the exact execution sentinel was disabled again and the worker start command was restored to preflight-only. `IDENTITY_STANDARD_CODE_BINDING`, expected-scope execution, per-security history, status economics, feature-performance testing, sealed holdout and live trading remain unauthorized. Gates C/D/E remain open.

Canonical Railway readiness evidence is `INDEXALERT_KRX_HISTORICAL_RAILWAY_READINESS_EVIDENCE.md/.json`. Provisioning authority remains separated by `INDEXALERT_KRX_WORKER_PROVISIONING_CONSENT_CONTRACT.md/.json`; completed preflight infrastructure setup cannot authorize historical bulk acquisition or expected-scope network execution.

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

## Execution-sufficiency preregistration — project v1 frozen, genuine LIVE not yet observed

Canonical preregistration/evaluator stack is now:
- `INDEXALERT_EXECUTION_SUFFICIENCY_PROTOCOL.md` — human-readable frozen protocol;
- `INDEXALERT_EXECUTION_SUFFICIENCY_PROTOCOL.json` — SHA-256-bound machine-readable schema v2 criteria;
- `research_v1_execution_sufficiency_protocol.py` — fail-closed preregistration validator with legacy schema-v1 compatibility;
- `research_v1_execution_sufficiency_assessment.py` — frozen numerical execution-gate evaluator;
- `INDEXALERT_LIVE_EXECUTION_PROVENANCE_CONTRACT.md` — separate fail-closed genuine-LIVE provenance admission contract.

The project protocol was frozen before any genuine LIVE observation. Core criteria include at least 600 LIVE observations across at least 200 distinct decision dates, at least 400 filled observations, decision-time PIT ADV participation capped at the existing research assumption `0.0005` (0.05%), 120 near-capacity observations at >=80% of that ceiling, date-cluster fill/slippage gates, Wilson no-fill/partial-fill bounds, 5m/30m/close markouts with ES95/ES99 reporting, latency/expiry controls, fee/tax comparison, and zero unknown/reconciliation/risk/capacity-integrity breaches. Thresholds are bound to the protocol document fingerprint and may not be weakened using outcomes from the evidence window they judge.

The metric evaluator requires LIVE-labelled rows, the frozen decision/execution policy IDs and PIT provenance timestamps, but it cannot authenticate real-account origin from a caller-supplied CSV. A source label or CSV SHA-256 is identity/structure evidence only. Numerical success is exposed separately as `execution_metric_gates_passed`, while the fact that the metric calculation was run is `execution_metric_sufficiency_assessed=true`. Project-level readiness additionally requires independent broker-native provenance admission for the exact evidence bundle. The metric evaluator by itself keeps `genuine_live_provenance_verified=false`, `empirical_execution_sufficiency_assessed=false`, `live_empirical_execution_evidence_ready=false`, `empirical_execution_blocker_closed=false`, `promotion_ready=false`, `sealed_holdout_authorized=false` and `live_trading_authorized=false`.

No genuine staged LIVE execution observations or broker-native provenance admission exist yet, so current project state remains:
- `genuine_live_provenance_verified=false`;
- `live_empirical_execution_evidence_ready=false`;
- `empirical_execution_sufficiency_assessed=false`;
- `empirical_execution_blocker_closed=false`;
- `promotion_ready=false`.

Historical preregistration Actions `36835013828` and `36835231533` succeeded. The frozen project protocol/evaluator Action `36881327868` also succeeded. Unit-test fixtures may exercise numerical pass/fail paths only and are not project evidence; a synthetic fixture may never close the project execution blocker.

## Android / push Physical E2E state — CONFIRMED

Canonical audit: `INDEXALERT_PHYSICAL_E2E_AUDIT.md`.

Current Android build branch is `index-alert-build`, HEAD `5154ef7943353791f615622394523ecd52ef8b0f`. The audited build is `versionName=4.7`, `versionCode=47`, therefore `client_build=4.7-47`.

Latest APK Action `36856589300` succeeded:
- debug `IndexAlert-v4.7-debug`, artifact ID `11158994269`, SHA256 `0aec298a0d0276f8a5e40dc22429b595e8bb11636f22ceeea75cb018a4a7e411`;
- unsigned release `IndexAlert-v4.7-unsigned-release`, artifact ID `11159209190`, SHA256 `77f7ba0acb991ae48827dcac8658b917fe60edc0ec677ae4548d8e797c8f4780`.

The v4.7 Android client sends its privacy-safe `client_build` during registration and uses the build-specific self-test/receipt path. Provider send success is never treated as handset receipt; confirmation requires the actual client `/push-ack` for the exact server event.

During the real handset audit, the first v4.7 registration attempts reached production but returned HTTP 400. Root cause was an exact-key mismatch between the Android `enabled_levels` payload and server-side display-only rules such as `usdkrw` whose alert `levels` are empty. The server overlay was fixed to synthesize only missing **display-only** empty-level keys; alert-bearing keys are never synthesized and continue to fail closed when missing or invalid.

The validated server branch `index-alert-server` production revision is now `d8523810b1c2c092a9ffc8f6245586e3bb719645` (`Test v4.7 registration with display-only server rules`). Server Tests Action `36874615526` succeeded, including regression coverage for the v4.7 payload/display-only compatibility boundary.

Frozen Physical-E2E contracts remain:
- `registration_build_contract = "register-client-build-v1"`;
- `self_test_trigger_contract = "android-register-direct-v1"`;
- `physical_e2e_binding_contract = "registered-device-build-receipt-v1"`;
- `physical_e2e_blocker_contract = "physical-e2e-blocker-v1"`.

The server binds Physical E2E to the exact latest registered **device and build**. A same-build receipt from another device, an older-build receipt, or a newer legacy/unknown-build registration all fail closed. A legacy registration with no `client_build` is preserved as the latest unknown-build observation so it cannot resurrect an older build-aware device as the apparent latest candidate.

`/push-health` exposes privacy-safe diagnostics including `latest_registered_client_build`, `latest_self_test_build`, `latest_self_test_sent`, `latest_self_test_receipt_confirmed`, `registration_device_matches_self_test`, `registration_build_matches_self_test`, `physical_e2e_blocker`, and `current_build_physical_e2e_confirmed`. Raw token/event IDs remain server-private.

Read-only verifier `verify_push_physical_e2e.py` requires the exact expected registered build, same-device/same-build binding, all frozen contract markers, sent self-test, real receipt timestamp and `physical_e2e_blocker == "CONFIRMED"`; it cannot send FCM, register a device, or manufacture a receipt.

### Real production Physical E2E evidence — DONE

Railway production deployment `4cde730b-2aca-49c2-9950-f895897fe642` is built from exact server revision `d8523810b1c2c092a9ffc8f6245586e3bb719645` and completed SUCCESS.

After that revision became live, the real Android handset performed the physical path in production:
- `POST /register` — HTTP 200;
- `POST /push-self-test` — HTTP 200;
- real handset `POST /push-ack` — HTTP 200.

The v32 Build Contract Smoke Action `36874615527` was rerun after the real handset ACK and completed SUCCESS. Its exact-revision `/push-health` observation reported:
- `runtime_revision = "d8523810b1c2c092a9ffc8f6245586e3bb719645"`;
- `physical_e2e_blocker = "CONFIRMED"`;
- `latest_registered_client_build = "4.7-47"`;
- `latest_self_test_build = "4.7-47"`;
- `registration_device_matches_self_test = true`;
- `registration_build_matches_self_test = true`;
- `current_build_physical_e2e_confirmed = true`.

Therefore the Android notification Physical E2E blocker is **CLOSED for the audited v4.7-47 build and exact production revision above**. This is plumbing/safety evidence only. It is not model-promotion evidence, execution sufficiency, KRX evidence, sealed-holdout evidence or live-order authority.

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

Railway `indexalert-runtime` is now aligned to server revision `4714f8e2d47881b7ccc42d7add0bfebb67ce3bf5` through deployment `2ae60f51-720c-463f-96cb-c9ef98fc449b` (SUCCESS). Production Smoke Action `36956234911` succeeded on that exact runtime revision and included the sanitized KRX connectivity/schema proof. The original physical handset event remains the earlier v4.7-47 `/register -> /push-self-test -> /push-ack` evidence; the newer deployment must not be misdescribed as a new handset event.

This closes server deployment drift, stale-runtime ambiguity, the latest-registration ordering gap, the v4.7 display-only registration compatibility gap, the Physical E2E blocker, the mover-provenance observability gap and the public startup FX-basis leakage path. It does not close the execution evidence blocker, KRX blockers, sealed holdout, promotion, or live-order authority. Real-account ordering remains disabled.

## External evidence still missing

Internal code cannot fabricate the still-missing actual full-history KRX coverage/PIT/provenance evidence, real complete affected-position status economics, genuine staged LIVE execution observations or a later independent execution-sufficiency assessment. Personal-research acquisition rights themselves are now evidenced by KRX permission v3.

## Remaining blockers

1. **KRX authorization/data:** basic-info/daily-trade OpenAPI connectivity, both Data Marketplace tiny probes, personal-research full-history/high-frequency rights, and the internal private historical-acquisition implementation are complete through a preflight-only dedicated-worker image. Gate F is PASS for the declared scope; Gate A remains PARTIAL. The dedicated private Railway worker/volume and worker secrets are complete, and the 27-request `IDENTITY_SEED` is complete with canonical metadata-only evidence. `IDENTITY_STANDARD_CODE_BINDING` has now also been prepared **network-free** from the private seed: exactly 145 `security_master` tasks were frozen with task-set SHA-256 `b3e9c845d74b0b479af0fd95d9015de92697fbd82b7bf07f9765378dfafd11d9`, private-manifest metadata SHA-256 `940f446caec81dd1a4a7b3a01053ae3f6a6ef6c79654e23bf2b971dca3622a6c`, and zero network requests. Canonical evidence is `INDEXALERT_KRX_IDENTITY_BINDING_PREPARATION_EVIDENCE.md/.json`. The separate identity-binding approval was supplied and consumed. Railway deployment `3501cbb8-a6a6-4972-bf82-4fb8e3fb36f6` at exact revision `6c152d8f29354d843b16c35be27a86a8a8058908` completed the frozen `IDENTITY_STANDARD_CODE_BINDING` stage **145/145**, zero resumes, exactly 145 network requests, phase `COMPLETE`, task-set SHA-256 `b3e9c845d74b0b479af0fd95d9015de92697fbd82b7bf07f9765378dfafd11d9`, and private execution-batch metadata SHA-256 `d5ca4e7ea45033f6bd6d45e301f1d3041b2e7257836e60d71c442fa73d8013be`; raw rows/identifiers were not emitted publicly. Both consent values were disabled again and the worker was restored to preflight-only. Canonical evidence is `INDEXALERT_KRX_IDENTITY_BINDING_EXECUTION_EVIDENCE.md/.json`. `PER_SECURITY_HISTORY` network-free preparation is now complete on Railway deployment `f683b1a2-5db6-4e95-81a7-6ec5889a2c59` from exact revision `ffe0e2c05e2a705c4b4cf06922600d07daa464cc`: **14,296** requests were frozen (**9,485** `investor_trading_individual_daily` + **4,811** `trading_halt`), task-set SHA-256 `fb5b883c6fe0e9c15e88aea9bdf874ddd7a11ae8a009c2ddf91c4e4249a8ba38`, private-manifest metadata SHA-256 `0d98f45168cedeecc013e95c71abe661ca1fac9df0403ba477d2f5653572c116`, and zero KRX network requests during preparation. Before freezing, PIT-safe identity reconciliation preserved official six-character alphanumeric short codes and excluded only issues proven non-common by same-day/start-date official master evidence; missing/ambiguous mappings remain fail-closed. Canonical evidence is `INDEXALERT_KRX_PER_SECURITY_HISTORY_PREPARATION_EVIDENCE.md/.json`. The exact prepared scope is now code-pinned and execution-contract-pinned. The separate exact approval `I_AUTHORIZE_INDEXALERT_KRX_PER_SECURITY_HISTORY_v1` has now been supplied and consumed only for the frozen one-shot scope. The original Railway execution deployment `bc79d1b5-5fb8-46c7-8067-682e61947014` at source revision `9009c48a00394063c813d29219507ee2190ce09e` **CRASHED** at 2026-10-03T00:45:16Z because that executor revision incorrectly required `isuCd2` to be decimal-only even though the already-frozen PIT-safe planner correctly preserves official six-character ASCII alphanumeric short codes. The executor is now patched and regression-tested to the same six-character ASCII alphanumeric domain. A network-free aggregate status deployment `92439b24-644a-4d3d-a888-9e0ba568bfac` verified the private checkpoint at **11,750 / 14,296 complete**, **2,546 remaining**, **0 failed**, phase `IN_PROGRESS`, frozen fingerprint `fb5b883c6fe0e9c15e88aea9bdf874ddd7a11ae8a009c2ddf91c4e4249a8ba38`, with `network_request_attempted=false`. Canonical interruption evidence is `INDEXALERT_KRX_PER_SECURITY_HISTORY_INTERRUPTION_EVIDENCE.md/.json`. The original one-shot authority is consumed and both consent values are disabled again; configured worker start is preflight-only with restart `NEVER`. The alphanumeric short-code fix is now verified at exact revision `585d763542b2fbbdc3f928621f679fb14c8c3bbf`: Official KRX Status Integrity Action `37087007640` is SUCCESS, and fresh preflight-only Railway deployment `c1f875b2-4164-491a-9aaf-e6c5b2a387db` used `Dockerfile.krx-historical-worker` with `network_request_attempted=false` and no execution consent. Frozen source branch `index-alert-krx-per-security-resume-v1` points exactly to that revision. The resume consent contract is therefore `FIX_VERIFIED_WAITING_FOR_EXPLICIT_USER_AUTHORIZATION`; no resume execution deployment exists and resume network authority remains false. Resume is **not authorized** and requires a new explicit user authorization while preserving the exact frozen scope and checkpoint semantics. Exact phrase: `I_AUTHORIZE_INDEXALERT_KRX_PER_SECURITY_HISTORY_RESUME_v1`; runtime resume consent must match it. This authority is one-shot and does not authorize `STATUS_ECONOMICS`, expected-scope network execution, feature-performance testing, sealed holdout, genuine LIVE or live trading. `STATUS_ECONOMICS` is additionally fail-closed at the code layer: its expected task count, task-set SHA-256 and private-manifest metadata SHA-256 constants remain intentionally unset until network-free preparation completes; actual execution stays blocked until those exact values are code-pinned and the full Official KRX CI passes. A network-free/read-only `--finalize-status-economics-metadata` path and metadata-only execution-evidence validator are also present for any future authorized run; they require exact COMPLETE state, the frozen manifest/task fingerprints and post-run relock, and explicitly keep `exact_status_economics_ready=false`, realized fill economics unproven and recovery cash flows unproven. After exact completion or failure, both consent values must be disabled again and the worker restored to preflight-only. Full-history coverage, exact all-period schema/equivalence, PIT lineage and immutable real acquisition receipts/batches remain open until the phase reaches exact COMPLETE and final evidence is admitted.
2. **Security/status economics:** real complete affected-position fill/recovery economics must pass the exact audit; the internal auditor alone does not close the blocker.
3. **Investor flow:** real full official history must pass provenance, PIT, coverage, A-F and source-data admission; then separate preregistration before any feature-performance experiment.
4. **Execution:** genuine staged LIVE observations, frozen numerical sufficiency assessment and independent broker-native provenance admission for the exact evidence bundle. Structurally valid or self-labelled LIVE rows alone do not close this blocker.
5. **Research governance:** no rejected-candidate revival; maintain Ledger/multiple-testing discipline.
6. **One-shot sealed holdout:** untouched until source/execution/code/protocol freeze; then Shadow S1 -> Fresh Confirmation S2.
7. **Physical notification E2E:** **DONE for audited Android v4.7-47 and production revision `d8523810…`**; do not reinterpret this plumbing success as Alpha/execution/promotion evidence.
8. **Live ordering:** disabled until all frozen promotion/safety gates and explicit user activation requirements are met.

## Promotion rule

Positive mean, PF or CAGR alone cannot promote a candidate. Promotion requires cost-adjusted OOS economics, PF > 1, positive date-cluster lower bound, best-day robustness, credible recent evidence, acceptable MDD/ES/tails, cost-stress survival, PIT correctness, official source/status integrity and execution realism. Final promotion additionally requires the one-shot sealed holdout and prospective confirmation sequence.

## Kiwoom demo/read-only connectivity — observed, non-promotional

Canonical demo evidence records `TOKEN_OK`, `ACCOUNT_OK`, `BALANCE_OK`, and `FILLS_OK` against the Kiwoom mock/demo host in a user-operated read-only smoke test. This is plumbing/readiness evidence only. Genuine LIVE broker-native provenance, empirical execution sufficiency, real status-event economics, KRX external evidence, sealed holdout and live ordering remain blocked/unauthorized as previously frozen.

## Continuous Research Lab — ENABLED, isolated from Core

Continuous research governance is now implemented by `research_v1_continuous_research.py` under `INDEXALERT_CONTINUOUS_RESEARCH_CONTRACT.md`. Automated research may queue ideas and evaluate preregistered challengers, but cannot mutate Core, open the sealed holdout, authorize live ordering, or auto-promote a candidate. Existing frozen blockers and criteria are unchanged.

## Internal completeness audit — authority boundary hardened

`INDEXALERT_INTERNAL_COMPLETENESS_AUDIT.md` records the internal audit. Successor research may satisfy represented promotion conditions but remains `promotion_eligible=false` until independent canonical gate admission exists; caller booleans cannot grant that authority. The audit also fixed a legacy KRX staging ambiguity: `research_v1_krx.py` now hard-codes `judge_eligible=false`, requires source-governance admission, and cannot label pykrx transport success as authenticated Final-Judge evidence. Real-order and sealed-holdout authorization remain false. Remaining material blockers are external/evidence-bound.
