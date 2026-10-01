# IndexAlert Continuity Snapshot — Canonical Cross-Chat Handoff

Updated: 2026-10-01 KST  
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
- Security/status: A BLOCKED, B PARTIAL, C BLOCKED, D BLOCKED, E PARTIAL, F PARTIAL; `judge_security_status_ready=false`.
- Investor flow: A BLOCKED, B PARTIAL, C BLOCKED, D PARTIAL, E PARTIAL, F PARTIAL; feature-performance testing blocked.

Even all six PASS closes only the declared source contract; it does not authorize promotion, sealed holdout or live trading.

Public-evidence fingerprint remains `349d310647c78412e45ac13078259bab2d002958db597b2f7dd26228f8b3ca7b` (`2026-10-01.v1`).

Authorization boundary:
`route credentials -> validated structured non-secret authorization evidence -> exact per-run tiny-request consent`.

Canonical validator: `research_v1_krx_authorization_evidence.py`. Canonical structured-evidence variable is `KRX_AUTH_EVIDENCE_JSON`; canonical explicit-consent variable is `KRX_EXPLICIT_PROBE_CONSENT`. The approval reference alone is not validated evidence. Network-free readiness always clears consent and performs no KRX request. Push probe workflows are dry-run only. **Gate A remains BLOCKED** because no authenticated KRX request has yet been demonstrated.

Internal safe source sequence:
`structured authorization evidence -> network-free readiness -> explicit manual consent -> auth preflight -> tiny authenticated acquisition -> receipt -> batch -> PIT lineage -> exact scope coverage -> A-F audit -> source-data admission -> separate experiment-registry/preregistration review`.

Source-data admission only permits experiment-registry review; performance testing, holdout, promotion and live authority stay false.

Latest broad KRX source-governance reference: Action `36817784717` at `bc5792640e0ba611f50f459f8c3b17c108cdd4bf` succeeded with structured authorization provenance through source-data admission. Final documentation-drift repair Action `36835918274` succeeded at research branch state before the later Android/server handoff update.

External KRX blockers remain: approved exact route/product, credentials and genuine approval evidence, authenticated route proof, full official history/stable IDs, independently attested expected scope, record-level PIT lineage and exact use rights.

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

## 5. Execution-sufficiency preregistration — validator DONE, project criteria NOT FROZEN

`research_v1_execution_sufficiency_protocol.py` validates future criteria without choosing them. It requires explicit observation/date/fill/no-fill/partial-fill criteria, 5m/30m/close markouts, slippage, latency, capacity and tail evidence, a governing-document SHA256, and a timezone-aware freeze time.

If the protocol will judge existing LIVE observations, `frozen_at` must be strictly earlier than the first LIVE recommendation; same-time or later is rejected as post-hoc. Unit-test threshold values are fixtures only, not IndexAlert policy.

Protocol validity alone keeps sufficiency unassessed and blocker/promotion/holdout/live authority false. A later independent evaluator must judge genuine staged LIVE evidence against a properly frozen protocol.

Execution preregistration Action `36835013828` succeeded; strengthened contract-drift Action `36835231533` also succeeded.

## 6. Android / push Physical E2E — server/prod same-device contract DONE, handset v4.7 evidence still OPEN

### Android current audited build

Current build branch: `index-alert-build`.  
Current branch HEAD: `5154ef7943353791f615622394523ecd52ef8b0f` (`Label Android v4.7 build artifacts`).  
Current Android build identifies itself to the server as **`client_build = "4.7-47"`**.

Latest APK Action `36856589300`: SUCCESS.
- debug artifact `IndexAlert-v4.7-debug`, artifact ID `11158994269`, digest `sha256:0aec298a0d0276f8a5e40dc22429b595e8bb11636f22ceeea75cb018a4a7e411`;
- unsigned release artifact `IndexAlert-v4.7-unsigned-release`, artifact ID `11159209190`, digest `sha256:77f7ba0acb991ae48827dcac8658b917fe60edc0ec677ae4548d8e797c8f4780`.

The v4.7 client sends the privacy-safe build identifier during registration and uses the established self-test/receipt path; provider send success alone is never treated as handset receipt. The server-issued event is acknowledged through privacy-safe `/push-ack` only after the handset actually receives it.

### Server current audited code

Current server branch: `index-alert-server`.  
Operational server HEAD: `3ce5b96502e496e676d61a46deb655c56f0ff01f` (`Re-export Physical E2E binding contract from v32 runtime`).

The build-registration overlay is shared by v31 and v32 entrypoints, so start-command drift cannot silently remove the build-bound registration/health contract. Production v32 re-exports the frozen contract markers for compatibility and auditability.

Frozen contracts:
- `registration_build_contract = "register-client-build-v1"`
- `self_test_trigger_contract = "android-register-direct-v1"`
- `physical_e2e_binding_contract = "registered-device-build-receipt-v1"`

Physical-E2E is now bound to the exact latest registered **device and build**, not merely a matching build string. Server-internal token/event identifiers are used only for binding and are never exposed in the public health payload.

Public health evidence includes:
- `latest_registered_client_build`
- `latest_self_test_build`
- `latest_self_test_sent`
- `latest_self_test_receipt_confirmed`
- `registration_device_matches_self_test`
- `registration_build_matches_self_test`
- `current_build_physical_e2e_confirmed`

A same-build receipt from a different device must fail closed. An older-build receipt must also fail closed. `verify_push_physical_e2e.py` is read-only and requires the exact registered build, same-device binding, same-build binding, frozen contract markers, sent self-test and real client receipt before returning confirmed.

Server Tests Action `36866475663` succeeded with all 154 tests passing. v32 Build Contract Smoke Action `36866475674`, job `110383083332`, also succeeded against the exact production revision and the same-device/same-build contract.

### Railway production — exact source SHA and runtime SHA aligned

Railway `indexalert-runtime` deployment `0b426b06-a4ec-4782-b1d5-21fa86d839bb` is SUCCESS from exact server commit `3ce5b96502e496e676d61a46deb655c56f0ff01f`.

Railway service start command is explicitly `production_v32:app`. The production runtime marker is also `3ce5b96502e496e676d61a46deb655c56f0ff01f`; the successful v32 smoke waited through the older runtime and passed only after the exact source commit and runtime revision matched.

Therefore the server deployment, API schema and all three Physical-E2E contract markers are production-audited. This does **not** by itself prove a physical handset receipt.

### Current Physical E2E evidence — still OPEN

The final successful exact-revision production smoke observed:
- `runtime_revision = "3ce5b96502e496e676d61a46deb655c56f0ff01f"`
- `registration_build_contract = "register-client-build-v1"`
- `self_test_trigger_contract = "android-register-direct-v1"`
- `physical_e2e_binding_contract = "registered-device-build-receipt-v1"`
- `latest_registered_client_build = null`
- `latest_self_test_build = null`
- `registration_device_matches_self_test = false`
- `registration_build_matches_self_test = false`
- `current_build_physical_e2e_confirmed = false`

This is a clean server-side fail-closed state: the new production has **not yet observed a v4.7 handset registration/self-test**, so there is no build/device-specific physical evidence to confirm. Null/false values must not be reinterpreted from older aggregate delivery counters.

Exact Physical E2E closure requires a real handset running build `4.7-47` to produce all of the following on the same registered device:
- `latest_registered_client_build == "4.7-47"`
- `latest_self_test_build == "4.7-47"`
- `registration_device_matches_self_test == true`
- `registration_build_matches_self_test == true`
- `latest_self_test_sent == true`
- `latest_self_test_receipt_confirmed == true`
- `current_build_physical_e2e_confirmed == true`
- a non-null real client receipt timestamp / receipt ledger entry.

No physical receipt is fabricated or inferred from Firebase provider send success, a prior build, or a same-build event received by another device.

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
2. DONE — internal KRX A-F/source authorization/readiness/provenance/PIT/coverage/admission infrastructure.
3. EXTERNAL KRX AUTH/DATA BLOCKER — approved route, real credentials/approval, authenticated proof, full history/stable IDs/PIT/use rights.
4. DONE — internal exact status-economics auditor; EXTERNAL EVIDENCE BLOCKER remains for real fill/recovery data.
5. DONE — execution schema hardening: LIVE structural presence is no longer mislabeled as empirical sufficiency.
6. DONE — execution-sufficiency preregistration validator; FUTURE PROTOCOL BLOCKER remains because actual project criteria have not been frozen.
7. EMPIRICAL EXECUTION BLOCKER — genuine staged LIVE observations plus later independent sufficiency assessment.
8. SEALED HOLDOUT — untouched; use once only after source/execution/code/protocol freeze, then Shadow S1 -> Fresh Confirmation S2.
9. DONE — server deployment drift and stale-runtime ambiguity; Railway production source and runtime revision are aligned to exact server commit `3ce5b965...`, v32 start command is explicit, and exact-revision same-device contract smoke succeeds.
10. DONE — mover production-integrity provenance; non-equity and registered corporate-action exclusions are fail-closed and visible in `/laggards`.
11. DONE — USD/KRW public startup basis is fail-closed until ECOS prior-15:30 verification and carries contract marker `ecos-1530-fail-closed-v1`.
12. PHYSICAL E2E — server-side exact device/build binding is DONE, but production currently has `latest_registered_client_build=null` and `latest_self_test_build=null`; a real v4.7-47 handset must register, receive the build-specific self-test and ACK it on that same device.
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
- never freeze execution thresholds after seeing the LIVE outcomes they will judge;
- never treat Firebase provider send success, an old-build receipt, or a same-build receipt from a different device as current-build Physical E2E;
- never infer a current-build self-test from aggregate sent/received counters when `latest_registered_client_build` or `latest_self_test_build` is null/mismatched;
- never claim current-build Physical E2E unless same-device, same-build, sent and real-receipt fields all pass the frozen `registered-device-build-receipt-v1` contract;
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