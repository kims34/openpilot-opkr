# IndexAlert Continuity Snapshot — Canonical Cross-Chat Handoff

Updated: 2026-10-01 KST  
Branch of record: `index-alert-research-v1`

## 0. Purpose and authority

This file keeps continuation independent of older Chat/Work rooms.

Authority order:
1. `INDEXALERT_MASTER_SPEC.md` — frozen statistical/validation contract.
2. `INDEXALERT_RESEARCH_LEDGER.md` — experiments, outcomes, dispositions and negative evidence.
3. Current GitHub code + reproducible Actions artifacts/logs — implementation/execution evidence.
4. `INDEXALERT_RESEARCH_STATUS.md` — current status summary.
5. `INDEXALERT_KRX_SOURCE_ACCESS_CONTRACT.md`, `INDEXALERT_KRX_SOURCE_GATE_AUDIT.md`, `INDEXALERT_EXECUTION_EVIDENCE_CONTRACT.md` — source/evidence contracts and audit.
6. This snapshot — cross-chat handoff and unfinished-work registry.
7. Older chats/notes — historical context only.

If sources conflict, current reproducible GitHub evidence wins. Always re-fetch branch HEAD before editing.

## 1. Frozen research contract

- H5 = Core development horizon.
- H10 = `REJECTED_CURRENT_CANDIDATE_DO_NOT_RETUNE`; no H6-H9 sweep or H10 retune from completed outcomes.
- H20 = out of requested 5-10-session scope; archive only.
- Anchored walk-forward = train 504 / calibration 126 / test 126.
- Horizon-matched label-overlap purge/embargo mandatory.
- Test/holdout outcomes must not choose thresholds, quantiles, TopK, costs or policy.
- Correct CPCV = 6 contiguous groups; all two-test-group combinations; each remaining group once as calibration; other three train = 60 cases/horizon. CPCV is stability evidence only.
- Original decision-time Top3 frozen; vetoed/held/unfillable slots remain empty; **no rank-4+ backfill**.
- 0..3 trades and `NO_TRADE` valid.
- Strict PIT/availability lineage and KRX CA-safe base-price returns mandatory.
- Primary evidence = executable cost-adjusted NetReturn/NetEV, PF, cluster uncertainty, MDD/ES tails, cost stress, coverage/abstention, execution/capacity and current-regime evidence.
- Never relax q25, TopK, costs, recent-evidence, execution assumptions or horizon merely to manufacture trades.
- Sealed holdout = one-shot, still unburned. After a valid holdout require prospective trading-policy Shadow S1 then frozen Fresh Confirmation S2.

## 2. Completed research state

### H5 developmental reference

- 278 executed entries / 137 trade days
- mean NetReturn ~+1.150%, PF ~1.546
- cluster 95% lower bound below zero
- 2x-cost mean ~+0.787%, PF ~1.344
- portfolio total ~+16.39%, CAGR ~1.83%, MDD ~-24.39%, Sharpe ~0.23
- admissions concentrated in 2018-2021; none in 2022-2026/latest 504 OOS
- remove-best-5 makes mean negative and PF < 1

Classification: `DEVELOPMENTAL_NOT_CURRENTLY_PROMOTABLE`.

### Authoritative negative/structural results

- Corrected 60-case CPCV Action `36637351334`: H5 median PF 0.381 / positive NetEV 43.3% / positive cluster LCB 11.7%; H10 median PF 0.745 / positive NetEV 50.0% / positive cluster LCB 33.3%. Verdict: robust edge not established.
- Uncertainty Audit `36637333875`: **KEEP_ABSTENTION**; q25-blocked pools are economically weak. Do not weaken q25.
- Policy-aligned calibration `36643183157`: same 278 selections/performance; structural alignment only, no new Alpha evidence.
- Rolling-160 rejected; do not sweep nearby windows.
- CA-safe path family rejected; do not retune.
- H10 rejected current candidate; no retune.
- H20 archive only.

## 3. KRX source-governance state

Canonical A-F gates:
- Gate A — `AUTHORIZED_OFFICIAL_ROUTE`
- Gate B — `EXACT_DATASET_SCHEMA_MAPPING`
- Gate C — `HISTORICAL_COVERAGE_SECURITY_MAPPING`
- Gate D — `PIT_AVAILABILITY_LINEAGE`
- Gate E — `REPRODUCIBLE_INTEGRITY_FAIL_CLOSED`
- Gate F — `INTENDED_USE_RIGHTS`

Statuses are `PASS`, `PARTIAL`, `BLOCKED`; only PASS closes a gate. Even all six PASS closes only the source contract for the declared scope and cannot by itself authorize Alpha/Final-Judge promotion, sealed holdout or live trading.

### Current gate state

**Security/status:** A BLOCKED, B PARTIAL, C BLOCKED, D BLOCKED, E PARTIAL, F PARTIAL. `judge_security_status_ready=false`.

**Investor flow:** A BLOCKED, B PARTIAL, C BLOCKED, D PARTIAL, E PARTIAL, F PARTIAL. `feature_performance_testing_authorized=false`.

No source gate changed merely because new validators were implemented.

### Authentication reality

Actions-log audit shows `KRX_ID`, `KRX_PW`, `KRX_OPENAPI_AUTH_KEY` are absent in the current source-probe runtime. Earlier green probes were `AUTH_NOT_CONFIGURED`; a green workflow means the diagnostic program ran, not that KRX authenticated access succeeded.

Latest public-evidence-bound probes:
- Status `36809182681`: success diagnostic, `authenticated_request_attempted=false`, source contract open, artifact `11139071717`, contract fp `b91b5ee6b2b64e11910dddcd6f0400c884d2add3cd12530771eb5fb824160eec`, result fp `65056341c19d0d70c7a8ae5e5bde3310cc54cfcc1eb2e4ed33645eb5152106e0`.
- Investor flow `36809196068`: success diagnostic, `authenticated_request_attempted=false`, source contract open, artifact `11138816495`, contract fp `28c9d28aab34d8ec8e55258dbc95d389c2096eaf687c635a8e6c1b8f76179291`, result fp `a227f4dcb34653cf89a9a6f462c01eabb45613c8c57212efa2e621039c53e097`.

### Public official evidence

`research_v1_krx_public_evidence.py` freezes version `2026-10-01.v1`, fingerprint:
`349d310647c78412e45ac13078259bab2d002958db597b2f7dd26228f8b3ca7b`.

It records the official OpenAPI key + per-service approval model, current non-commercial/no-third-party-distribution restrictions, public status-screen semantics, investor final-result after-20:00 rule, and unknown exact mappings as unknown. It grants no promotion authority.

## 4. KRX Gate C/D validation infrastructure — implemented, evidence still missing

### Investor flow PIT lineage

`research_v1_krx_investor_flow_lineage.py` enforces:
- timezone-aware times;
- `event_time <= published_at <= available_at <= ingested_at`;
- day-D final publication floor >= 20:00 KST;
- current public-evidence fingerprint;
- one source-contract fingerprint per historical dataset;
- decision eligibility only when decision timestamp >= `available_at`.

Action `36809680268`: success. Structural validity still cannot authorize performance testing or holdout use.

### Investor flow exact historical coverage

`research_v1_krx_investor_flow_coverage.py` compares only independently attested expected `(event_date, symbol, isu_cd)` keys against validated observed lineage. It never invents business days/securities or converts a missing row into zero. Missing/extra/duplicate/mapping-conflict keys keep coverage incomplete.

Action `36809948775`: success.

### Security/status common-stock coverage

`research_v1_krx_status_coverage.py` compares an independently attested expected `(snapshot_date, symbol, isu_cd)` scope to official common-stock identity evidence. Current normalized identity evidence without a stable full issue ID cannot close Gate C. Exact identity coverage alone still cannot set Final-Judge ready.

Action `36810205800` initially failed on an empty-common-stock DataFrame schema bug; protocol/policy were unchanged. Empty key schema was preserved, and Action `36810309522` passed the same protocol.

### Latest integrity state

- Public-evidence binding Action `36809165505`: success.
- Investor PIT lineage Action `36809680268`: success.
- Investor exact coverage Action `36809948775`: success.
- Status coverage corrected Action `36810309522`: success.
- Source-audit doc Action `36810464265`: success.
- Research-status Action `36810572547`: success.

## 5. Execution evidence / broker boundary

Canonical: `INDEXALERT_EXECUTION_EVIDENCE_CONTRACT.md` and `INDEXALERT_BROKER_EXECUTION_CONTRACT.md`.

Frozen evidence tiers:
1. `PROSPECTIVE_SHADOW_DECISION_LOG` — prospective decision/intention only, no broker fills.
2. `PROSPECTIVE_PAPER_EXECUTION_LOG` — paper/simulation broker plumbing/reconciliation evidence, not real-market fill quality.
3. `PROSPECTIVE_LIVE_EXECUTION_LOG` — actual real-account executions; only tier eligible to contribute empirical live fill/slippage/partial-fill/latency/markout/capacity evidence.

Research execution-evidence Action `36668905306` passed. Server full tests Action `36669071810` passed. Railway production service `indexalert-runtime` runs server commit `65855916afd52d081453bc511b6b82df3ec948b1`, deployment `34e76729-ff9b-4fa5-8334-b8b591a336ba` SUCCESS with `/health` 200. Operational success does not authorize trading and no synthetic execution rows were inserted.

Required automation progression remains:
`Research / Backtest -> Shadow -> Kiwoom Paper API -> Tiny Live -> Limited Live -> Production`.

Real-account ordering remains disabled. Default future UX remains automation ON/OFF + `max_automation_capital_krw` ceiling; no valid opportunity means `NO_TRADE`/cash.

## 6. Server / Android notification state

### Server

Corrected execution evidence semantics are production-active. Persistent `/data` volume remains part of the deployment. Protected execution logging token is configured; no secret value belongs in GitHub docs.

Last directly verified push-health snapshot before subsequent environment changes had:
- `ok=true`, `firebase=true`, `registered_devices=1`
- `sent_deliveries=1`
- `received_deliveries=0`
- `unconfirmed_sent_deliveries=1`
- `last_client_receipt_at=null`

A server `sent` row is not proof a handset received/presented the notification.

### Android

Last audited build branch head: `55d72dc576131d1f8c2f6f01b9f4951a2e088911` (`Fix WorkManager receipt result type`). Re-fetch before edits.

APK Action `36665289417`: success.
- debug artifact `IndexAlert-v4.4-debug`, ID `11076077796`, SHA256 `b195fa90e0e5d074bc1c0764918eb78e23537da693b9eb514547fb1fc48033be`
- unsigned release artifact `IndexAlert-v4.4-unsigned-release`, ID `11075977955`, SHA256 `b5f0e090e167af076510eb831a83e38506793b796acdd9c9587878cb2e7afa70`

Physical E2E gate remains open: one current-build handset receipt must produce `received_deliveries >= 1` and non-null `last_client_receipt_at`.

## 7. Explicit unfinished-work registry

Continue from the first actionable unresolved item supported by current GitHub evidence:

1. **DONE:** corrected H5/H10 CPCV, Uncertainty Audit, Policy Calibration and frozen negative dispositions.
2. **DONE:** KRX A-F contract, Master Spec section, source audit, code semantics, document-drift tests and public-evidence manifest/fingerprint.
3. **DONE — INTERNAL INFRASTRUCTURE:** source probes emit machine-readable gate audits/fingerprints; investor Gate D lineage validator, investor Gate C exact-coverage auditor and status Gate C exact-coverage auditor are CI-tested.
4. **EXTERNAL DATA/AUTH BLOCKER:** obtain/configure an approved exact KRX historical route/product using secure secret management. Current audited CI has no KRX credentials; Gate A stays BLOCKED. Do not place credentials in code/logs/docs.
5. **EXTERNAL DATA/COVERAGE BLOCKER:** supply real full historical status + investor-flow data, independently attested expected scope/stable security mapping and record-level PIT lineage. Until real data passes validators, status C/D and investor C remain blocked and investor D remains partial.
6. **EXACT STATUS ECONOMICS BLOCKER:** full halt/cleanup/delisting joins and exact economic outcomes remain required for Final Judge.
7. **EMPIRICAL EXECUTION BLOCKER:** collect genuine staged execution evidence; Shadow decisions, Paper plumbing, Tiny Live+ real empirical fills. Never fabricate evidence.
8. **SEALED HOLDOUT:** still untouched. Burn once only after source/execution/code/protocol freeze; then Shadow S1 -> Fresh Confirmation S2.
9. **PHYSICAL E2E:** current-build Android receipt still required.
10. **LIVE ORDERING:** disabled until all frozen promotion/safety gates and explicit user activation requirements are met.

## 8. Continuation rule

On every continuation:
- re-fetch current branch HEAD and relevant Actions first;
- re-read Master Spec, Ledger, Research Status, KRX source contract/audit, execution-evidence contract and this snapshot;
- skip completed/rejected experiments;
- never interpret a green KRX source-probe workflow as authenticated success without its internal `authenticated_request_attempted`/gate state;
- never revive rejected candidates by threshold/cost/horizon mining;
- never convert Shadow/Paper observations into live empirical evidence;
- never infer missing KRX rows as zeros or invent historical calendars/universes to make coverage pass;
- if old chat conflicts with reproducible GitHub evidence, GitHub wins;
- commit material state changes to canonical GitHub docs so chat history remains nonessential.

## 9. Old-chat deletion gate

Older IndexAlert Chat/Work rooms are not project-state dependencies. Material continuity lives in GitHub code, Actions evidence and canonical docs.
