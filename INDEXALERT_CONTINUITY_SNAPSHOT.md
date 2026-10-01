# IndexAlert Continuity Snapshot — Canonical Cross-Chat Handoff

Updated: 2026-10-01 KST  
Branch of record: `index-alert-research-v1`

## 0. Authority and continuation rule

This is a compact handoff, not a substitute for the canonical authorities. Authority order:
1. `INDEXALERT_MASTER_SPEC.md` — frozen statistical/validation contract.
2. `INDEXALERT_RESEARCH_LEDGER.md` — experiments, outcomes, dispositions and negative evidence.
3. Current GitHub code + reproducible Actions/logs — implementation/execution evidence.
4. `INDEXALERT_RESEARCH_STATUS.md` — current research summary.
5. Source/execution contracts and audits.
6. This snapshot — continuation registry only.
7. Older chats/notes — historical context only.

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
- Sealed holdout remains one-shot and untouched. After a valid holdout require trading-policy Shadow S1 then frozen Fresh Confirmation S2.

Current H5 developmental reference remains non-promotable: 278 entries / 137 trade days, mean NetReturn ~+1.150%, PF ~1.546, date-cluster lower bound below zero, 2x-cost mean ~+0.787% / PF ~1.344, MDD ~-24.39%, no admissions in 2022-2026/latest 504 OOS, remove-best-5 economics negative.

Authoritative negative evidence remains unchanged:
- corrected 60-case CPCV Action `36637351334`: H5 median PF 0.381 / positive NetEV 43.3% / positive cluster LCB 11.7%; H10 0.745 / 50.0% / 33.3%; robust edge not established;
- Uncertainty Audit `36637333875`: `KEEP_ABSTENTION`;
- Policy Calibration `36643183157`: structural alignment only, no performance change;
- Rolling-160 and CA-safe path challengers rejected;
- H10 do-not-retune; H20 archive only.

## 2. KRX source governance — internally hardened, externally blocked

Frozen A-F gates:
- A `AUTHORIZED_OFFICIAL_ROUTE`
- B `EXACT_DATASET_SCHEMA_MAPPING`
- C `HISTORICAL_COVERAGE_SECURITY_MAPPING`
- D `PIT_AVAILABILITY_LINEAGE`
- E `REPRODUCIBLE_INTEGRITY_FAIL_CLOSED`
- F `INTENDED_USE_RIGHTS`

Current states remain:
- Security/status: A BLOCKED, B PARTIAL, C BLOCKED, D BLOCKED, E PARTIAL, F PARTIAL; `judge_security_status_ready=false`.
- Investor flow: A BLOCKED, B PARTIAL, C BLOCKED, D PARTIAL, E PARTIAL, F PARTIAL; feature-performance testing blocked.

Even all six PASS closes only the declared source contract; it never by itself authorizes Alpha/Final-Judge promotion, sealed holdout or live trading.

Public-evidence manifest remains version `2026-10-01.v1`, fingerprint `349d310647c78412e45ac13078259bab2d002958db597b2f7dd26228f8b3ca7b`.

Authorization boundary is frozen as:
`route credentials -> validated structured non-secret authorization evidence -> exact per-run tiny-request consent`.

An opaque approval reference alone is not validated evidence. Push probe workflows are dry-run only. Network-free readiness forcibly disables request consent. No authenticated KRX request has yet been demonstrated; Gate A remains BLOCKED.

Latest broad KRX integrity reference before the status-economics work: Action `36817784717` at `bc5792640e0ba611f50f459f8c3b17c108cdd4bf` succeeded with structured authorization provenance through source-data admission.

## 3. KRX source-data pipeline — DONE internally

Safe future sequence:
`structured authorization evidence -> network-free readiness -> explicit manual consent -> auth preflight -> tiny authenticated acquisition -> immutable receipt -> consistent batch -> PIT lineage -> exact expected-scope coverage -> A-F audit -> source-data admission -> separate experiment-registry/preregistration review`.

Canonical implementations include:
- `research_v1_krx_authorization_evidence.py`
- `research_v1_krx_auth_readiness.py`
- `research_v1_krx_auth_preflight.py`
- status/investor probes and workflow-safety tests
- `research_v1_krx_acquisition_receipt.py`
- `research_v1_krx_acquisition_batch.py`
- `research_v1_krx_investor_flow_lineage.py`
- investor/status exact-coverage auditors
- `research_v1_krx_status_event_integrity.py`
- `research_v1_krx_source_data_admission.py`

Source-data admission only permits experiment-registry review; performance testing, holdout, promotion and live authority remain false.

External source blockers remain: approved exact route/product, secure credentials and genuine approval evidence, authenticated access proof, complete full history/stable IDs, attested expected scope, record-level PIT lineage and exact intended-use rights.

## 4. Exact KRX halt/cleanup/delisting economics — auditor DONE, evidence BLOCKED

Canonical contract: `INDEXALERT_KRX_STATUS_ECONOMICS_CONTRACT.md`.  
Executable audit: `research_v1_krx_status_economics.py`.

Final Judge exact economics now requires an independently attested complete affected-position scope and exact quantity conservation:
`affected_qty = verified_exit_fill_qty + verified_recovery_qty`.

Exact filled quantity must be backed by accepted actual execution evidence; exact recovery quantity must be backed by accepted official/issuer/broker cash-distribution evidence. Missing/over-resolved quantity, unsupported source, naive/missing availability timestamp, source-contract mismatch or implicit zero recovery fails closed.

Daily OHLC, MDCSTAT239 daily prices, backtest/synthetic/modelled fills, market-open assumptions, Shadow or Paper fills cannot prove exact realized economics.

Internal tests passed Action `36834108231`. Contract drift run `36834285722` exposed a documentation identifier mismatch only; canonical identifiers were added without relaxing policy. Action `36834718544` then succeeded.

**Project-level exact status economics remains OPEN** because no real complete affected-position economics dataset has been supplied. The auditor itself is not evidence that historical economics are complete.

## 5. Execution evidence — LIVE structure separated from empirical sufficiency

Canonical contract: `INDEXALERT_EXECUTION_EVIDENCE_CONTRACT.md`.

Evidence tiers:
- `PROSPECTIVE_SHADOW_DECISION_LOG`: decision intent only, no fills.
- `PROSPECTIVE_PAPER_EXECUTION_LOG`: paper/simulation plumbing evidence, not real fill quality.
- `PROSPECTIVE_LIVE_EXECUTION_LOG`: real-account observations; the only tier eligible to contribute raw live empirical execution evidence.

`research_v1_execution_evidence.py` now separates `live_structural_execution_evidence_present` from empirical sufficiency. One or several structurally valid LIVE rows do not close the empirical blocker.

Until a separately frozen protocol is evaluated:
- `live_empirical_execution_evidence_ready=false`
- `empirical_execution_sufficiency_assessed=false`
- `empirical_execution_blocker_closed=false`
- `promotion_ready=false`

Execution evidence Action `36834616144` succeeded with this boundary.

## 6. Execution-sufficiency preregistration — validator DONE, project criteria NOT YET FROZEN

`research_v1_execution_sufficiency_protocol.py` is the preregistration structural validator.

It does not choose IndexAlert thresholds. It requires any future protocol to explicitly state its counts/evidence dimensions, fingerprint the governing document and freeze `frozen_at` strictly before the first LIVE recommendation that protocol will judge. A same-time or later freeze is rejected as post-hoc.

Required dimensions include live observation count, distinct dates, filled/no-fill/partial-fill observations, 5m/30m/close markouts, slippage, latency, capacity and tail evidence. Numeric values used in unit tests are illustrative fixtures only, not promotion thresholds.

Protocol validity itself keeps sufficiency unassessed and blocker/promotion/holdout/live authority false. A later independent evaluator must assess genuine staged LIVE evidence against a properly preregistered protocol.

Execution preregistration Action `36835013828` succeeded. Contract-drift semantics are guarded in CI.

## 7. Broker/server/Android boundary

Required execution progression remains:
`Research / Backtest -> Shadow -> Kiwoom Paper API -> Tiny Live -> Limited Live -> Production`.

Real-account ordering remains disabled. Broker connectivity or structurally valid LIVE rows cannot skip stages.

Railway production service `indexalert-runtime` previously ran server commit `65855916afd52d081453bc511b6b82df3ec948b1`; deployment `34e76729-ff9b-4fa5-8334-b8b591a336ba` succeeded with `/health` 200. Operational evidence only.

Last audited Android build branch head: `55d72dc576131d1f8c2f6f01b9f4951a2e088911` (`Fix WorkManager receipt result type`). APK Action `36665289417` succeeded. Physical E2E remains open: a current-build handset receipt must yield `received_deliveries >= 1` and non-null `last_client_receipt_at`.

## 8. Explicit unfinished-work registry

1. **DONE — research protocol:** corrected H5/H10 CPCV, Uncertainty Audit, Policy Calibration and negative dispositions.
2. **DONE — internal KRX source governance:** A-F contracts, structured auth evidence, readiness/preflight, probes, provenance, PIT, coverage, status-event integrity, source-data admission.
3. **EXTERNAL KRX AUTH/DATA BLOCKER:** approved route/product, secure credentials/genuine approval evidence, authenticated access, full official history/stable IDs/PIT/use rights.
4. **DONE — internal exact status-economics audit; EXTERNAL EVIDENCE BLOCKER remains:** real complete affected-position fill/recovery economics must pass `research_v1_krx_status_economics.py`.
5. **DONE — execution schema hardening:** LIVE structural presence is no longer mislabeled as empirical sufficiency.
6. **DONE — preregistration validator; FUTURE PROTOCOL BLOCKER remains:** actual IndexAlert execution-sufficiency criteria must be separately chosen and frozen before the LIVE evidence they judge; no post-hoc threshold selection.
7. **EMPIRICAL EXECUTION BLOCKER:** genuine staged LIVE observations and later independent sufficiency assessment remain required.
8. **SEALED HOLDOUT:** untouched; consume once only after source/execution/code/protocol freeze, then Shadow S1 -> Fresh Confirmation S2.
9. **PHYSICAL E2E:** current-build Android receipt still required.
10. **LIVE ORDERING:** disabled until all frozen promotion/safety gates and explicit activation requirements pass.

## 9. Continuation rules

On every continuation:
- re-fetch branch HEAD and relevant Actions first;
- read Master Spec, Ledger, Research Status, current contracts/audits and this snapshot;
- skip completed/rejected work;
- never treat green diagnostic/probe workflows as authenticated KRX evidence without internal state;
- never treat credentials/reference alone as authorization;
- never infer missing KRX rows as zeros or invent historical scope;
- never treat status-event structure or daily prices as exact realized status economics;
- never treat one/few LIVE rows as empirical execution sufficiency;
- never freeze execution-sufficiency thresholds after seeing the LIVE outcomes they will judge;
- never revive rejected model candidates through threshold/cost/horizon mining;
- never convert Shadow/Paper observations into live empirical evidence;
- if old chat conflicts with reproducible GitHub evidence, GitHub wins;
- commit material continuity changes to canonical GitHub docs.

## 10. Old-chat deletion gate

Older IndexAlert chat/work rooms are not project-state dependencies. Material continuity lives in GitHub code, Actions evidence and canonical documents.
