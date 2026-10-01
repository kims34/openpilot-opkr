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

## 6. Android / push Physical E2E — current build identified, server audit hardened, physical receipt still OPEN

### Android current audited build

Current build branch: `index-alert-build`.  
Current branch HEAD: `396501f9df3bdf4fd7cea4a2c97116a02f8961d5` (`Name APK artifacts for v4.6`).  
This is a direct descendant of the older audited `55d72dc...` WorkManager receipt fix.

`index-alert/app/build.gradle.kts` freezes:
- `versionName = "4.6"`
- `versionCode = 46`
- self-test `client_build` therefore resolves to **`4.6-46`**.

Latest APK Action `36815959241`: SUCCESS.
- debug artifact `IndexAlert-v4.6-debug`, artifact ID `11141577031`, SHA256 `d32c468bb3f719dcdafe99f3614358723cceeb566239bbedbbb3927c6f740dbf`;
- unsigned release artifact `IndexAlert-v4.6-unsigned-release`, artifact ID `11141532240`, SHA256 `b95c8f28417c1b3f901ad2c0768970ae2942f2167ed49e9373f3666a4edf19a6`.

Current Android `Push.kt` schedules privacy-safe `/push-ack` for the server-issued event ID on Firebase receipt and polls the same build self-test until `receipt_confirmed=true`. A provider `sent` result is never treated as handset receipt.

### Server current audited code

Current server branch: `index-alert-server`.

The server self-test contract already reuses the same `token + client_build` event after it has been sent, so polling never generates a fresh event merely because receipt is pending. `/push-ack` accepts only SHA256(token) for a registered device plus an already-sent matching event, and duplicate ACKs are idempotent.

Physical-E2E health was further hardened on 2026-10-01:
- `push_self_test.latest_self_test_status()` binds health to the most recently created build self-test and omits raw token/event IDs;
- `/push-health` now exposes `latest_self_test_build`, `latest_self_test_sent`, `latest_self_test_receipt_confirmed`, and `current_build_physical_e2e_confirmed`;
- tests explicitly prove that an ACK from an older build cannot confirm a newer build;
- server unit test Action `36836572820` at server commit `36b7250b31afcf2ca775cb59987c0c6c305cfc17` succeeded.

Server smoke was then strengthened at server commit `12f6676287db487199a8b0644a7d568c11de77a1` to require the new build-specific `/push-health` fields in production. This prevents a stale production deployment from passing merely because old aggregate receipts exist.

### Railway production deployment state

Railway service `indexalert-runtime` is sourced from `index-alert-server`, but the latest confirmed production deployment is still deployment `5b5fc540-2925-4c83-aa83-0688eef31159`, commit `65855916afd52d081453bc511b6b82df3ec948b1` (`Test paper live execution evidence ledger tiers`). It predates the new build-specific E2E health contract.

Therefore current GitHub/server code and production are intentionally treated as **deployment-drifted** until production is updated. A smoke green on the old aggregate contract is no longer sufficient; the strengthened smoke requires the new fields.

### Exact Physical E2E closure condition

For the current audited Android build, Physical E2E remains OPEN until a real handset running build `4.6-46` causes server evidence at the test point showing at least:
- `latest_self_test_build == "4.6-46"`;
- `latest_self_test_sent == true`;
- `latest_self_test_receipt_confirmed == true`;
- `current_build_physical_e2e_confirmed == true`;
- a non-null client receipt timestamp / receipt ledger entry from the real handset path.

Aggregate `received_deliveries >= 1` by itself is no longer sufficient because it may refer to an older build.

No physical receipt is fabricated or inferred from Firebase provider send success.

## 7. Broker / live-order boundary

Execution progression remains:
`Research / Backtest -> Shadow -> Kiwoom Paper API -> Tiny Live -> Limited Live -> Production`.

Real-account ordering remains disabled. Structurally valid LIVE rows, broker connectivity, Android push receipt, or server deployment success cannot skip any research/promotion stage.

## 8. Explicit unfinished-work registry

1. DONE — H5/H10 CPCV, Uncertainty Audit, Policy Calibration, negative dispositions.
2. DONE — internal KRX A-F/source authorization/readiness/provenance/PIT/coverage/admission infrastructure.
3. EXTERNAL KRX AUTH/DATA BLOCKER — approved route, real credentials/approval, authenticated proof, full history/stable IDs/PIT/use rights.
4. DONE — internal exact status-economics auditor; EXTERNAL EVIDENCE BLOCKER remains for real fill/recovery data.
5. DONE — execution schema hardening: LIVE structural presence is no longer mislabeled as empirical sufficiency.
6. DONE — execution-sufficiency preregistration validator; FUTURE PROTOCOL BLOCKER remains because actual project criteria have not been frozen.
7. EMPIRICAL EXECUTION BLOCKER — genuine staged LIVE observations plus later independent sufficiency assessment.
8. SEALED HOLDOUT — untouched; use once only after source/execution/code/protocol freeze, then Shadow S1 -> Fresh Confirmation S2.
9. SERVER DEPLOYMENT DRIFT — current production still runs server commit `65855916...`; build-specific E2E health exists only on newer `index-alert-server` code until deployed.
10. PHYSICAL E2E — current v4.6-46 handset receipt meeting the build-specific conditions above is still required.
11. LIVE ORDERING — disabled until every frozen promotion/safety gate and explicit activation requirement passes.

## 9. Continuation rules

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
- never treat Firebase provider send success or an old-build receipt as current-build Physical E2E;
- never revive rejected candidates through threshold/cost/horizon mining;
- never convert Shadow/Paper observations into live empirical evidence;
- if chat conflicts with reproducible GitHub evidence, GitHub wins;
- commit material state changes to canonical GitHub docs.

## 10. Old-chat deletion gate

Older IndexAlert chat/work rooms are not project-state dependencies. Material continuity lives in GitHub code, Actions evidence and canonical documents.
