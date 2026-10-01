# IndexAlert Continuity Snapshot — Canonical Cross-Chat Handoff

Updated: 2026-10-01 KST  
Branch of record: `index-alert-research-v1`

## 0. Authority and continuation rule

This file is a compact handoff. Authority order is:
1. `INDEXALERT_MASTER_SPEC.md` — frozen statistical/validation contract.
2. `INDEXALERT_RESEARCH_LEDGER.md` — experiments, outcomes, dispositions and negative evidence.
3. Current GitHub code + reproducible Actions artifacts/logs — implementation/execution evidence.
4. `INDEXALERT_RESEARCH_STATUS.md` — current research summary.
5. `INDEXALERT_KRX_SOURCE_ACCESS_CONTRACT.md`, `INDEXALERT_KRX_SOURCE_GATE_AUDIT.md`, `INDEXALERT_EXECUTION_EVIDENCE_CONTRACT.md` — source/evidence contracts and audit.
6. This snapshot — cross-chat handoff and unfinished-work registry.
7. Older chats/notes — historical context only.

If anything conflicts, current reproducible GitHub evidence wins. Always re-fetch branch HEAD and relevant Actions before editing.

## 1. Frozen research state

- H5 = Core development horizon.
- H10 = `REJECTED_CURRENT_CANDIDATE_DO_NOT_RETUNE`; no H6-H9 sweep or H10 retune from completed outcomes.
- H20 = out of the requested 5-10-session scope; archive only.
- Anchored walk-forward = train 504 / calibration 126 / test 126, with horizon-matched purge/embargo.
- Correct CPCV = 6 contiguous groups, all two-test-group combinations, each remaining group once as calibration, other three train = **60 cases/horizon**.
- Original decision-time Top3 is frozen. Vetoed/held/unfillable slots stay empty; **no rank-4+ backfill**.
- 0..3 trades and `NO_TRADE` are valid.
- Never relax q25, TopK, costs, recent-evidence, execution assumptions or horizon merely to manufacture trades.
- Sealed holdout remains one-shot and untouched. After a valid holdout require prospective trading-policy Shadow S1, then frozen Fresh Confirmation S2.

Current H5 developmental reference remains non-promotable: 278 entries / 137 trade days, mean NetReturn ~+1.150%, PF ~1.546, date-cluster lower bound below zero, 2x-cost mean ~+0.787% / PF ~1.344, MDD ~-24.39%, no admissions in 2022-2026/latest 504 OOS, and remove-best-5 turns economics negative.

Authoritative negative evidence remains unchanged:
- corrected 60-case CPCV Action `36637351334`: H5 median PF 0.381 / positive NetEV 43.3% / positive cluster LCB 11.7%; H10 0.745 / 50.0% / 33.3%; robust edge not established;
- Uncertainty Audit `36637333875`: **KEEP_ABSTENTION**;
- Policy Calibration `36643183157`: structural alignment only, no performance change;
- Rolling-160 and CA-safe path challengers rejected;
- H10 rejected current candidate; H20 archive only.

## 2. Frozen KRX source governance

Canonical A-F gates are:
- Gate A — `AUTHORIZED_OFFICIAL_ROUTE`
- Gate B — `EXACT_DATASET_SCHEMA_MAPPING`
- Gate C — `HISTORICAL_COVERAGE_SECURITY_MAPPING`
- Gate D — `PIT_AVAILABILITY_LINEAGE`
- Gate E — `REPRODUCIBLE_INTEGRITY_FAIL_CLOSED`
- Gate F — `INTENDED_USE_RIGHTS`

Only `PASS` closes a gate. Even all six PASS closes only the source contract for the declared scope and cannot by itself authorize Alpha/Final-Judge promotion, the sealed holdout, or live trading.

Current source states remain unchanged:
- **Security/status:** A BLOCKED, B PARTIAL, C BLOCKED, D BLOCKED, E PARTIAL, F PARTIAL; `judge_security_status_ready=false`.
- **Investor flow:** A BLOCKED, B PARTIAL, C BLOCKED, D PARTIAL, E PARTIAL, F PARTIAL; `feature_performance_testing_authorized=false`.

New validators/provenance/consent controls do not upgrade these states without real source evidence.

## 3. KRX public evidence, authorization and runtime consent

`research_v1_krx_public_evidence.py` freezes public evidence version `2026-10-01.v1`, fingerprint:
`349d310647c78412e45ac13078259bab2d002958db597b2f7dd26228f8b3ca7b`.

`research_v1_krx_auth_preflight.py` freezes:
- credentials are not authorization;
- authorization metadata is not runtime consent;
- Data Marketplace tiny probes require `KRX_ID` + `KRX_PW` + non-secret `KRX_AUTH_EVIDENCE_REF` + exact `KRX_EXPLICIT_PROBE_CONSENT=ALLOW_TINY_AUTHENTICATED_REQUEST`;
- generic consent strings such as `true`, `1`, `yes` are rejected;
- `KRX_OPENAPI_AUTH_KEY` is a separate route and cannot substitute for the Data Marketplace session;
- OpenAPI additionally requires an exact approved service mapping;
- purchased/distributed product access cannot be inferred from either online credential route;
- a successful tiny-request preflight may raise Gate A only to `PARTIAL`, never `PASS`, and never authorizes bulk history, performance testing, holdout, promotion or live trading.

Workflow defense-in-depth is now frozen:
- push events run dry-run only;
- push dry-run steps receive empty KRX credential/reference/consent environment values;
- authenticated steps are skipped on push;
- authenticated tiny requests are eligible only on `workflow_dispatch` with `allow_authenticated_request=true`;
- only that manual step receives Data Marketplace credentials, approval reference and exact consent sentinel;
- OpenAPI key is not injected into the Data Marketplace authenticated step.

Latest workflow evidence:
- **Status Action `36813950791`** — success; push-safe dry-run success; authenticated status step skipped.
- **Investor-flow Action `36813973236`** — success; push-safe dry-run success; authenticated investor step skipped.
- **Integrity Action `36814088731`** — success; full KRX fail-closed suite including exact-consent tests and Source Access Contract drift checks.

No authenticated KRX request has yet been demonstrated. Gate A remains BLOCKED.

## 4. KRX internal audit/provenance pipeline — implemented

Safe future real-data flow:

`explicit manual request consent -> authorization preflight -> authenticated acquisition -> immutable receipt -> consistent receipt batch -> PIT lineage -> exact expected-scope coverage -> A-F source audit -> source-data admission -> separate experiment-registry/preregistration review`

Implemented components:
- `research_v1_krx_investor_flow_lineage.py`: timezone-aware `event_time <= published_at <= available_at <= ingested_at`, investor final-result publication floor >= 20:00 KST, current public-evidence fingerprint, one source-contract fingerprint, decision-time availability;
- `research_v1_krx_investor_flow_coverage.py`: exact caller-attested `(event_date, symbol, isu_cd)` coverage; never invents calendar/universe or implicit zero-flow rows;
- `research_v1_krx_status_coverage.py`: exact caller-attested `(snapshot_date, symbol, isu_cd)` common-stock coverage; missing stable full issue identity fails closed;
- `research_v1_krx_status_event_integrity.py`: cleanup/delisting/delisted-price structural consistency; never invents fill price, recovery value or delisting return;
- `research_v1_krx_acquisition_receipt.py`: secret-free per-acquisition provenance binding request metadata hash, response schema/content hash, route, dataset, use scope, client revision, retrieval time, non-secret approval reference and public-contract fingerprint;
- `research_v1_krx_acquisition_batch.py`: verifies receipt fingerprints and rejects duplicate/tampered receipts or silent mixing of route, dataset, use scope, approval reference, client revision, schema or public-contract evidence;
- `research_v1_krx_source_data_admission.py`: requires closed A-F source contract + valid acquisition batch + current public evidence + valid PIT lineage + exact historical coverage + matching source family/use scope before `source_data_structurally_admissible=true`.

Even when source-data admission is structurally true, it grants only `eligible_for_experiment_registry_review=true`. It deliberately keeps `feature_performance_testing_authorized=false`, `sealed_holdout_authorized=false`, `alpha_or_final_judge_promotion_authorized=false`, and `live_trading_authorized=false`. Experiment ledger/preregistration and all statistical/execution gates remain separate.

Latest relevant integrity evidence:
- `36811118588` — status-event integrity: success;
- `36811648510` — acquisition receipt integrity: success;
- `36812299630` — acquisition batch integrity: success;
- `36812655201` — source-data admission integrity: success;
- `36813918295` — explicit-consent probe code/unit tests: success;
- `36814088731` — explicit-consent contract/full KRX integrity suite: success.

Transient implementation-test failures were fixed without changing any A-F gate, q25/TopK/horizon/cost rule or promotion threshold.

## 5. External KRX blockers — still hard blockers

Internal code cannot manufacture the remaining evidence. Required next external evidence is:
1. approved exact KRX historical route/product;
2. for the current Data Marketplace route, secure `KRX_ID` + `KRX_PW` and a real non-secret `KRX_AUTH_EVIDENCE_REF` describing the approval basis;
3. one explicitly consented manual tiny authenticated probe demonstrating the approved route without exposing credentials;
4. real complete historical status/investor-flow datasets;
5. independently attested full expected scope and stable security mapping;
6. real record-level PIT timestamps/availability evidence;
7. exact intended-use rights for the final route;
8. actual execution/recovery economics where halt/cleanup/delisting affects tradability/liquidation.

`KRX_OPENAPI_AUTH_KEY`, if later supplied, remains a separate route rather than a substitute for Data Marketplace credentials/approval.

Until real data passes the frozen pipeline, investor-flow performance research remains blocked and Final Judge status evidence remains incomplete.

## 6. Execution evidence and broker boundary

Canonical contracts: `INDEXALERT_EXECUTION_EVIDENCE_CONTRACT.md` and `INDEXALERT_BROKER_EXECUTION_CONTRACT.md`.

Evidence tiers remain:
1. `PROSPECTIVE_SHADOW_DECISION_LOG` — prospective decision/intention only, no broker fills;
2. `PROSPECTIVE_PAPER_EXECUTION_LOG` — paper/simulation plumbing/reconciliation evidence, not real-market fill quality;
3. `PROSPECTIVE_LIVE_EXECUTION_LOG` — actual real-account executions; only this tier may contribute empirical live fill/slippage/partial-fill/latency/markout/capacity evidence.

Research execution-evidence Action `36668905306` passed. Server full tests Action `36669071810` passed. Railway production service `indexalert-runtime` runs server commit `65855916afd52d081453bc511b6b82df3ec948b1`; deployment `34e76729-ff9b-4fa5-8334-b8b591a336ba` succeeded with `/health` 200. No synthetic execution rows were inserted.

Required automation progression remains:
`Research / Backtest -> Shadow -> Kiwoom Paper API -> Tiny Live -> Limited Live -> Production`.

Real-account ordering remains disabled. Default future UX remains automation ON/OFF plus `max_automation_capital_krw` ceiling; no valid opportunity means `NO_TRADE`/cash.

## 7. Server / Android notification state

Server execution-evidence semantics are production-active. The last directly verified push-health snapshot before subsequent environment changes had `ok=true`, `firebase=true`, `registered_devices=1`, `sent_deliveries=1`, `received_deliveries=0`, `unconfirmed_sent_deliveries=1`, `last_client_receipt_at=null`. A server `sent` row is not proof the handset received/presented the notification.

Last audited Android build branch head: `55d72dc576131d1f8c2f6f01b9f4951a2e088911` (`Fix WorkManager receipt result type`). Re-fetch before editing.

APK Action `36665289417`: success.
- debug artifact `IndexAlert-v4.4-debug`, ID `11076077796`, SHA256 `b195fa90e0e5d074bc1c0764918eb78e23537da693b9eb514547fb1fc48033be`;
- unsigned release artifact `IndexAlert-v4.4-unsigned-release`, ID `11075977955`, SHA256 `b5f0e090e167af076510eb831a83e38506793b796acdd9c9587878cb2e7afa70`.

Physical E2E gate remains open: one current-build handset receipt must produce `received_deliveries >= 1` and non-null `last_client_receipt_at`.

## 8. Explicit unfinished-work registry

1. **DONE:** corrected H5/H10 CPCV, Uncertainty Audit, Policy Calibration and frozen negative dispositions.
2. **DONE:** KRX A-F contract, Master Spec boundary, public-evidence manifest/fingerprint, source audit and doc-drift guards.
3. **DONE — INTERNAL:** authorization + explicit-consent preflight, push-safe source workflows, source-probe fingerprints, investor PIT lineage, investor/status exact coverage, status-event integrity, acquisition receipt, acquisition batch and source-data admission are fail-closed and CI-tested.
4. **EXTERNAL KRX AUTH BLOCKER:** secure approved route/product and route-specific credentials/approval reference, then explicitly dispatch one tiny authenticated probe. No authenticated KRX request has yet been demonstrated.
5. **EXTERNAL KRX DATA BLOCKER:** real full history + stable IDs + independently attested expected scope + record-level PIT lineage must pass the existing validators.
6. **EXACT STATUS ECONOMICS BLOCKER:** halt/cleanup/delisting execution/recovery economics remain required for Final Judge.
7. **EMPIRICAL EXECUTION BLOCKER:** genuine staged execution evidence remains required; never fabricate Shadow/Paper/Live evidence.
8. **SEALED HOLDOUT:** untouched; consume once only after source/execution/code/protocol freeze, then Shadow S1 -> Fresh Confirmation S2.
9. **PHYSICAL E2E:** current-build Android receipt still required.
10. **LIVE ORDERING:** disabled until all frozen promotion/safety gates and explicit user activation requirements are met.

## 9. Continuation rules

On every continuation:
- re-fetch current branch HEAD and relevant Actions first;
- re-read Master Spec, Ledger, Research Status, KRX source contract/audit, execution-evidence contract and this snapshot;
- skip completed/rejected experiments;
- never interpret green push probe execution as authenticated-source evidence: push is dry-run only;
- never allow an authenticated probe without exact per-run explicit consent;
- never treat credentials or approval metadata alone as runtime request consent;
- never substitute one KRX access route for another;
- never treat a receipt/batch alone as coverage, PIT or Alpha evidence;
- never run investor-flow performance research merely because source data is structurally admitted; first require separate experiment registry/preregistration authority;
- never revive rejected candidates by threshold/cost/horizon mining;
- never convert Shadow/Paper observations into live empirical evidence;
- never infer missing KRX rows as zeros or invent historical calendars/universes;
- if old chat conflicts with reproducible GitHub evidence, GitHub wins;
- commit material state changes to canonical GitHub docs so chat history remains nonessential.

## 10. Old-chat deletion gate

Older IndexAlert Chat/Work rooms are not project-state dependencies. Material continuity lives in GitHub code, Actions evidence and canonical docs.
