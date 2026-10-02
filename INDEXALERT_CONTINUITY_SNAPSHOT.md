# IndexAlert Continuity Snapshot — Canonical Cross-Chat Handoff

Updated: 2026-10-02 KST  
Branch of record: `index-alert-research-v1`

## 0. Authority and continuation rule

Authority order:
1. `INDEXALERT_MASTER_SPEC.md`
2. `INDEXALERT_RESEARCH_LEDGER.md`
3. Current GitHub code + reproducible Actions/logs
4. `INDEXALERT_RESEARCH_STATUS.md`
5. Current source/execution contracts and audits
6. This snapshot
7. Older chats/notes

If anything conflicts, current reproducible GitHub evidence wins. Re-fetch branch HEAD and relevant Actions before every continuation.

## 1. Frozen research state — unchanged

- H5 = Core development horizon.
- H10 = `REJECTED_CURRENT_CANDIDATE_DO_NOT_RETUNE`; no H6-H9 sweep or H10 retune from completed outcomes.
- H20 = out of requested 5-10-session scope; archive only.
- Anchored walk-forward = train 504 / calibration 126 / test 126 with horizon-matched purge/embargo.
- Correct CPCV = six contiguous groups, all two-test-group combinations, each remaining group once as calibration, other three train = 60 cases/horizon.
- Original decision-time Top3 frozen; no rank-4+ backfill.
- 0..3 trades and `NO_TRADE` valid.
- Never relax q25, TopK, costs, recency, execution assumptions or horizon merely to manufacture trades.
- Sealed holdout remains one-shot and untouched. After a valid holdout require Shadow S1 then frozen Fresh Confirmation S2.

H5 remains developmental/non-promotable: 278 entries / 137 trade days, mean NetReturn ~+1.150%, PF ~1.546, cluster lower bound below zero, 2x-cost mean ~+0.787% / PF ~1.344, MDD ~-24.39%, no admissions in 2022-2026/latest 504 OOS, remove-best-5 economics negative.

Negative evidence remains frozen: corrected CPCV Action `36637351334`, Uncertainty Audit `36637333875` = `KEEP_ABSTENTION`, Policy Calibration `36643183157` = structural alignment only; Rolling-160/CA-safe challengers rejected; H10 do-not-retune; H20 archive.

## 2. KRX source governance — internal pipeline DONE, external evidence BLOCKED

A-F gates remain:
- A `AUTHORIZED_OFFICIAL_ROUTE`
- B `EXACT_DATASET_SCHEMA_MAPPING`
- C `HISTORICAL_COVERAGE_SECURITY_MAPPING`
- D `PIT_AVAILABILITY_LINEAGE`
- E `REPRODUCIBLE_INTEGRITY_FAIL_CLOSED`
- F `INTENDED_USE_RIGHTS`

Current states:
- Security/status: A PARTIAL, B PARTIAL, C BLOCKED, D BLOCKED, E PARTIAL, F PARTIAL; `judge_security_status_ready=false`. Authenticated status tiny probe Action `36976085781` succeeded and live-validated `MDCSTAT21301` and `MDCSTAT23701` metadata reachability. Exact production OpenAPI connectivity/schema is now proven only for `유가증권 종목기본정보` and `유가증권 일별매매정보`; that evidence does not map the unresolved halt/cleanup/delisting route.
- Investor flow: A BLOCKED, B PARTIAL, C BLOCKED, D PARTIAL, E PARTIAL, F PARTIAL; feature-performance testing blocked.

Even all six PASS closes only the declared source contract; it does not authorize promotion, sealed holdout or live trading.

Public-evidence fingerprint remains `39f357fda6eec5bb994f1dcba1ba44ed913714df256ec6b542b5aeadf14a0380` (`2026-10-02.v2`).

Authorization boundary:
`route credentials -> validated structured non-secret authorization evidence -> explicit KRX automation permission where Data Marketplace web-session automation is used -> exact per-run tiny-request consent`.

Canonical validator: `research_v1_krx_authorization_evidence.py`. Canonical structured-evidence variable is `KRX_AUTH_EVIDENCE_JSON`; canonical explicit-consent variable is `KRX_EXPLICIT_PROBE_CONSENT`. The approval reference alone is not validated evidence. Network-free readiness always clears consent and performs no KRX request. Push research-probe workflows are dry-run only. Production OpenAPI now has authenticated proof for the two separately enabled basic-info/daily-trade services (`20261001`, 942 rows each, exact schema plus response fingerprints; Action `36956234911`), but no authenticated exact status-event or investor-flow route has been demonstrated. **Gate A remains BLOCKED for those declared source families**.

Internal safe source sequence:
`structured authorization evidence -> network-free readiness -> explicit manual consent -> auth preflight -> tiny authenticated acquisition -> receipt -> batch -> PIT lineage -> exact scope coverage -> A-F audit -> source-data admission -> separate experiment-registry/preregistration review`.

Source-data admission only permits experiment-registry review; performance testing, holdout, promotion and live authority stay false.

Latest broad KRX source-governance reference: Action `36817784717` at `bc5792640e0ba611f50f459f8c3b17c108cdd4bf` succeeded with structured authorization provenance through source-data admission. Final documentation-drift repair Action `36835918274` succeeded at research branch state before the later Android/server handoff update.

External KRX blockers remain: authenticated exact status-event/investor-flow route proof, exact schema/equivalence, full official history/stable IDs, independently attested expected scope, record-level PIT lineage and broader/bulk rights. The user-provided KRX email metadata + body now explicitly support low-frequency programmatic/automated querying for personal non-commercial/internal research without a separate approval procedure. Structured evidence validates for both source families, and network-free Action `36973737546` leaves only `EXPLICIT_TINY_REQUEST_CONSENT` before a metadata-only authenticated probe. The basic-info/daily-trade OpenAPI proof is recorded in `INDEXALERT_KRX_OPENAPI_CONNECTIVITY_EVIDENCE.md/.json`; candidate Data Marketplace BLDs are frozen in `INDEXALERT_KRX_DATA_MARKETPLACE_ROUTE_MAP.md/.json`; the automation restriction is frozen in `INDEXALERT_KRX_DATA_MARKETPLACE_TERMS_AUDIT.md/.json`. All are fail-closed validated and none grants source closure.

## 3. Exact KRX status economics — internal auditor DONE, real evidence BLOCKED

Contract: `INDEXALERT_KRX_STATUS_ECONOMICS_CONTRACT.md`.  
Audit: `research_v1_krx_status_economics.py`.

Required for every independently attested affected position:
`affected_qty = verified_exit_fill_qty + verified_recovery_qty`.

Exact filled quantity needs accepted actual execution evidence; exact recovery quantity needs accepted official/issuer/broker cash-distribution evidence. Missing/over-resolved quantity, unsupported evidence, naive/missing economic availability or contract mismatch fails closed.

Backtest/synthetic/modelled fills, market-open assumptions, Shadow/Paper fills, daily OHLC and MDCSTAT239 daily prices cannot prove an IndexAlert fill.

Action `36834108231` passed implementation tests. Documentation drift run `36834285722` failed only on a canonical identifier omission; no policy changed. After naming canonical forbidden identifiers, Action `36834718544` succeeded.

The project-level exact halt/cleanup/delisting economics blocker remains OPEN because no real complete affected-position economics dataset exists yet.

## 4. Execution evidence — LIVE structure != empirical sufficiency

Contract: `INDEXALERT_EXECUTION_EVIDENCE_CONTRACT.md`.

Tiers:
- `PROSPECTIVE_SHADOW_DECISION_LOG`: decisions/intents only.
- `PROSPECTIVE_PAPER_EXECUTION_LOG`: paper/simulation plumbing, not real fill quality.
- `PROSPECTIVE_LIVE_EXECUTION_LOG`: real-account observations; only tier eligible to contribute raw live execution evidence.

`research_v1_execution_evidence.py` separates `live_structural_execution_evidence_present` from empirical sufficiency. One/few LIVE rows never close the blocker.

Until a separately frozen protocol is evaluated:
- `live_empirical_execution_evidence_ready=false`
- `empirical_execution_sufficiency_assessed=false`
- `empirical_execution_blocker_closed=false`
- `promotion_ready=false`

Execution integrity Action `36834616144` succeeded with this boundary.

## 5. Execution-sufficiency preregistration — project v1 FROZEN, genuine LIVE not yet observed

Canonical files:
- `INDEXALERT_EXECUTION_SUFFICIENCY_PROTOCOL.md`;
- `INDEXALERT_EXECUTION_SUFFICIENCY_PROTOCOL.json`;
- `research_v1_execution_sufficiency_protocol.py`;
- `research_v1_execution_sufficiency_assessment.py`.

Project v1 was frozen before any genuine LIVE observation. Minimum sample is 600 LIVE observations across at least 200 distinct decision dates with at least 400 fills. Capacity scope is capped at decision-time PIT ADV participation `0.0005`; at least 120 observations must be near capacity (>=80% of the ceiling). Fill, no-fill/partial-fill, slippage, fee/tax, latency/expiry, 5m/30m/close markout, ES95/ES99, reconciliation, unknown-outcome, capacity and risk-integrity gates are all preregistered and non-compensating.

The metric evaluator accepts only LIVE-labelled rows with the frozen decision/execution policy IDs and PIT timestamps, but a source label or CSV hash does not authenticate real-account origin. `INDEXALERT_LIVE_EXECUTION_PROVENANCE_CONTRACT.md` requires separate independent broker-native provenance admission for the exact evidence bundle. Unit-test fixtures are never project evidence.

Current state remains `genuine_live_provenance_verified=false`, `live_empirical_execution_evidence_ready=false`, `empirical_execution_sufficiency_assessed=false`, `empirical_execution_blocker_closed=false`, `promotion_ready=false`, `sealed_holdout_authorized=false`, `live_trading_authorized=false` because no genuine staged LIVE evidence window or broker-native provenance admission exists yet.

Frozen project protocol/evaluator Action `36881327868` succeeded. The protocol cannot be weakened from outcomes it judges; any revision requires a new protocol ID/fingerprint and only later observations.

## 6. Android / push Physical E2E — DONE for audited v4.7-47

Canonical audit: `INDEXALERT_PHYSICAL_E2E_AUDIT.md`.

### Android audited build

Build branch: `index-alert-build`.  
Audited branch HEAD: `5154ef7943353791f615622394523ecd52ef8b0f` (`Label Android v4.7 build artifacts`).  
Android identifies itself to the server as **`client_build = "4.7-47"`**.

APK Action `36856589300`: SUCCESS.
- debug artifact `IndexAlert-v4.7-debug`, artifact ID `11158994269`, digest `sha256:0aec298a0d0276f8a5e40dc22429b595e8bb11636f22ceeea75cb018a4a7e411`;
- unsigned release artifact `IndexAlert-v4.7-unsigned-release`, artifact ID `11159209190`, digest `sha256:77f7ba0acb991ae48827dcac8658b917fe60edc0ec677ae4548d8e797c8f4780`.

The v4.7 client sends its privacy-safe build identifier during registration and uses the established self-test/receipt path; provider send success alone is never treated as handset receipt. The server-issued event is acknowledged through privacy-safe `/push-ack` only after the handset actually receives it.

### Real registration incompatibility found and fixed

The first physical v4.7 installation could read `/status`, `/laggards` and history successfully, but repeated `POST /register` requests returned HTTP 400.

Root cause: the established base registration validator requires an exact `enabled_levels` key set matching server `monitor.RULES`. Production contains display-only rules with empty alert levels, including `usdkrw`, while the Android registration payload carries the configurable alert rules plus the legacy KOSPI display key. This otherwise valid payload therefore failed exact-key validation.

Fix in `push_build_registration.py`: add only missing server rules whose alert `levels` are empty before calling the established validator. Alert-bearing rules are never synthesized; missing/unknown alert rules continue to fail closed. `test_push_build_registration.py` freezes this compatibility boundary.

Validated server revision: `d8523810b1c2c092a9ffc8f6245586e3bb719645` (`Test v4.7 registration with display-only server rules`). Server Tests Action `36874615526` succeeded.

### Frozen server contracts

- `registration_build_contract = "register-client-build-v1"`
- `self_test_trigger_contract = "android-register-direct-v1"`
- `physical_e2e_binding_contract = "registered-device-build-receipt-v1"`
- `physical_e2e_blocker_contract = "physical-e2e-blocker-v1"`

Physical E2E is bound to the exact latest registered **device and build**, not merely a matching build string. Server-internal token/event identifiers are used only for binding and are never exposed in the public health payload. A latest registration that omits `client_build` is preserved as a latest unknown-build observation and fails closed as `NO_REGISTERED_BUILD`; it cannot cause an older build-aware device to resurface as if it were the latest registration.

Public health evidence includes:
- `latest_registered_client_build`
- `latest_self_test_build`
- `latest_self_test_sent`
- `latest_self_test_receipt_confirmed`
- `registration_device_matches_self_test`
- `registration_build_matches_self_test`
- `physical_e2e_blocker`
- `current_build_physical_e2e_confirmed`

The blocker code is exactly one of:
`NO_REGISTERED_BUILD`, `NO_SELF_TEST`, `DEVICE_MISMATCH`, `BUILD_MISMATCH`, `SELF_TEST_NOT_SENT`, `RECEIPT_PENDING`, `CONFIRMED`.

A same-build receipt from a different device fails closed. An older-build receipt fails closed. A newer legacy/unknown-build registration also fails closed and cannot resurrect older evidence. `verify_push_physical_e2e.py` is read-only and requires the exact registered build, same-device binding, same-build binding, all frozen contract markers, `physical_e2e_blocker == "CONFIRMED"`, sent self-test and real client receipt before returning confirmed.

### Railway production and real handset evidence — CONFIRMED

Railway `indexalert-runtime` deployment `4cde730b-2aca-49c2-9950-f895897fe642` completed SUCCESS from exact server commit `d8523810b1c2c092a9ffc8f6245586e3bb719645`. Production uses `production_v32:app`.

After the fixed revision became live, the real Android handset generated the actual production path:
- `POST /register` — HTTP 200;
- `POST /push-self-test` — HTTP 200;
- real handset `POST /push-ack` — HTTP 200.

A fresh rerun of v32 Build Contract Smoke Action `36874615527` then succeeded on the exact production revision and observed:
- `runtime_revision = "d8523810b1c2c092a9ffc8f6245586e3bb719645"`
- `registration_build_contract = "register-client-build-v1"`
- `self_test_trigger_contract = "android-register-direct-v1"`
- `physical_e2e_binding_contract = "registered-device-build-receipt-v1"`
- `physical_e2e_blocker_contract = "physical-e2e-blocker-v1"`
- `physical_e2e_blocker = "CONFIRMED"`
- `latest_registered_client_build = "4.7-47"`
- `latest_self_test_build = "4.7-47"`
- `registration_device_matches_self_test = true`
- `registration_build_matches_self_test = true`
- `current_build_physical_e2e_confirmed = true`

Therefore **Physical E2E is CLOSED/DONE for audited Android v4.7-47 and production revision `d8523810…`**. This proves notification plumbing only and cannot be used as Alpha, execution-sufficiency, KRX, holdout, promotion or live-order evidence.

## 7. U.S. mover operational integrity — DONE and auditable

Stock-constituent quote admission is fail-closed to Yahoo instrument type `EQUITY`. ETF/fund/index/currency contamination cannot enter the company mover ranking. Corporate-action price discontinuities are not filtered by an arbitrary return threshold; omission requires a source-backed event/date in `corporate_action_registry.py` for which raw previous-close comparison is non-comparable.

The live `/laggards` contract exposes:
- `excluded_non_equity_symbols`
- `excluded_corporate_action_symbols`
for each universe.

Final exact-revision Production Smoke Action `36853857418` verified:
- S&P500 `502/503`, with `excluded_corporate_action_symbols=["CTVA"]` on 2026-10-01;
- NASDAQ100 `100/100`, no deliberate exclusions;
- SCHD `98/99`, with `excluded_non_equity_symbols=["USD"]`.

This explains coverage loss directly in the API and prevents the earlier `USD` ETF contamination and CTVA spin-off discontinuity from being presented as ordinary stock movers. Direction/sign checks remained valid. This operational integrity work does not alter frozen research results or KRX gate status.

## 7A. USD/KRW startup basis integrity — DONE and exact-revision audited

The public day-change basis is versioned as `ecos-1530-fail-closed-v1`. A live current quote may remain available during startup, but until Bank of Korea ECOS prior 15:30 basis verification is complete, public `previous_close`, `previous_close_date`, `day_change`, `day_change_percent` and `basis_provider` must all be null and `basis_verified=false`.

`fx_basis.public_basis_fields()` accepts a public basis only when the prior close is finite/positive, date and change fields are complete, `basis_verified=true`, and `basis_provider` explicitly contains `ECOS`. Unit tests reject older-layer Yahoo/provider fallback shapes, including a false `basis_verified=true` shape with a non-ECOS provider. `/status` and `/history/usdkrw` use this fail-closed sanitizer.

The timing-sensitive production smoke did not happen to capture a full response during the short pre-ECOS transition; unit tests enforce the transition shape. The final exact-revision smoke verified the live ready state with `basis_contract="ecos-1530-fail-closed-v1"`, `basis_verified=true`, `previous_close=1352.8`, `previous_close_date="2026-09-30"`, and an ECOS basis provider. Internal startup logs can still show an older-layer Yahoo fallback calculation before the outer v3.1 sanitizer completes, but that calculation is not accepted as the public official day-change basis.

## 8. Broker / live-order boundary

Execution progression remains:
`Research / Backtest -> Shadow -> Kiwoom Paper API -> Tiny Live -> Limited Live -> Production`.

Real-account ordering remains disabled. Structurally valid LIVE rows, broker connectivity, Android push receipt, or server deployment success cannot skip any research/promotion stage.

## 9. Explicit unfinished-work registry

1. DONE — H5/H10 CPCV, Uncertainty Audit, Policy Calibration, negative dispositions.
2. DONE — internal KRX A-F/source authorization/readiness/provenance/PIT/coverage/admission infrastructure. Legacy `research_v1_krx.py` is now explicitly staging-only: `judge_eligible=false`, source-governance admission required, sealed-holdout/live authority false.
3. EXTERNAL KRX AUTH/DATA BLOCKER — basic-info/daily-trade OpenAPI authentication is proven; status/investor BLD candidates are pinned; Data Marketplace ID/PW and explicit low-frequency automation permission are validated. Network-free readiness is complete. Status tiny probe is complete; investor-flow still needs its explicit-consent tiny authenticated probe. After that, exact route/schema, full-history/stable-ID, PIT and rights verification remain.
4. DONE — internal exact status-economics auditor; EXTERNAL EVIDENCE BLOCKER remains for real fill/recovery data.
5. DONE — execution schema hardening: LIVE structural presence is no longer mislabeled as empirical sufficiency.
6. DONE — frozen project execution-sufficiency protocol v1, SHA-256-bound machine-readable criteria, metric evaluator, provenance fail-closed hardening and Actions coverage; EMPIRICAL EXECUTION BLOCKER remains because genuine staged LIVE evidence and broker-native provenance admission do not exist.
7. EMPIRICAL EXECUTION BLOCKER — genuine staged LIVE observations + independent broker-native provenance admission + frozen numerical sufficiency assessment.
8. SEALED HOLDOUT — untouched; use once only after source/execution/code/protocol freeze, then Shadow S1 -> Fresh Confirmation S2.
9. DONE — server deployment drift/stale-runtime safeguards remain in place; Railway production is currently aligned to exact server commit `4714f8e2d47881b7ccc42d7add0bfebb67ce3bf5` via deployment `2ae60f51-720c-463f-96cb-c9ef98fc449b`, and Production Smoke `36956234911` succeeds. The original physical handset event remains separately bound to the audited v4.7-47 event evidence and must not be re-dated to this later deployment.
10. DONE — mover production-integrity provenance; non-equity and registered corporate-action exclusions are fail-closed and visible in `/laggards`.
11. DONE — USD/KRW public startup basis is fail-closed until ECOS prior-15:30 verification and carries contract marker `ecos-1530-fail-closed-v1`.
12. DONE — PHYSICAL E2E for audited Android v4.7-47: real production `/register` -> `/push-self-test` -> handset `/push-ack` succeeded on the exact registered device/build and production now reports `physical_e2e_blocker=CONFIRMED`.
13. LIVE ORDERING — disabled until every frozen promotion/safety gate and explicit activation requirement passes.

## 10. Continuation rules

On every continuation:
- re-fetch branch HEADs and relevant Actions first;
- read Master Spec, Ledger, Research Status, contracts/audits and this snapshot;
- skip completed/rejected work;
- never treat green source workflows as authenticated KRX evidence without internal state;
- never treat credentials/reference alone as authorization;
- never infer missing KRX rows as zeros or invent scope;
- never treat daily prices/status chronology as exact realized status economics;
- never treat one/few LIVE rows as empirical execution sufficiency;
- never treat a `PROSPECTIVE_LIVE_EXECUTION_LOG` label, CSV file name/hash or self-authored manifest as proof of genuine broker provenance;
- never freeze execution thresholds after seeing the LIVE outcomes they will judge;
- never treat Firebase provider send success, an old-build receipt, or a same-build receipt from a different device as current-build Physical E2E;
- never let a later legacy/unknown-build registration resurrect an older build-aware device as the latest Physical E2E candidate;
- never infer a current-build self-test from aggregate sent/received counters when `latest_registered_client_build` or `latest_self_test_build` is null/mismatched;
- never claim current-build Physical E2E unless same-device, same-build, sent, real-receipt and `physical_e2e_blocker == "CONFIRMED"` all pass the frozen contracts;
- never admit a non-equity symbol into a stock-constituent mover universe;
- never treat a registered corporate-action discontinuity as an ordinary one-day return; use source-backed, date-scoped fail-closed handling rather than arbitrary percentage clipping;
- never expose a provider-fallback USD/KRW previous close/day change as official while ECOS basis verification is incomplete;
- never accept a production smoke as proof of a newer revision unless `runtime_revision` matches the exact expected GitHub SHA;
- never revive rejected candidates through threshold/cost/horizon mining;
- never convert Shadow/Paper observations into live empirical evidence;
- if chat conflicts with reproducible GitHub evidence, GitHub wins;
- commit material state changes to canonical GitHub docs.

## 11. Old-chat deletion gate

Older IndexAlert chat/work rooms are not project-state dependencies. Material continuity lives in GitHub code, Actions evidence and canonical documents.

## 12. Kiwoom demo/read-only connectivity continuity note

`INDEXALERT_KIWOOM_DEMO_CONNECTIVITY_EVIDENCE.md` is canonical on `index-alert-research-v1` and records `TOKEN_OK / ACCOUNT_OK / BALANCE_OK / FILLS_OK` from the Kiwoom mock/demo host only. Treat this as completed demo/read-only plumbing evidence, never as genuine LIVE provenance or execution-sufficiency evidence. It changes no external blocker, does not authorize the sealed holdout, and does not enable real-account ordering.

## 13. Continuous Research governance

Continuous post-Core research is enabled as an isolated Research Lab. Every evaluative trial requires pre-outcome protocol fingerprinting; protocol mutation/post-hoc criteria changes or sealed-holdout use invalidate the trial. `ACCEPTED_CHALLENGER` is not production promotion. The Research Lab has no production-write, sealed-holdout, or live-order authority.

## 14. Internal completeness audit

Internal audit hardened successor promotion: represented confirmation conditions cannot self-grant `promotion_eligible`; `automatic_code_update_eligible=false`, `automatic_code_update_allowed=false` and `promotion_authority_verified=false` remain fail-closed until a future independent canonical promotion-authority mechanism exists. The same audit now also hardens legacy KRX daily-panel staging so retrieval cannot self-grant Judge eligibility. No real-order or sealed-holdout authority was introduced.
