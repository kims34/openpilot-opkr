# IndexAlert Continuity Snapshot — Canonical Cross-Chat Handoff

Updated: 2026-10-01 KST
Branch of record: `index-alert-research-v1`

## 0. Purpose and authority

This file keeps IndexAlert continuation independent of older Chat/Work rooms.

Authority order:
1. `INDEXALERT_MASTER_SPEC.md` — frozen statistical/validation contract.
2. `INDEXALERT_RESEARCH_LEDGER.md` — experiments, outcomes, dispositions, negative evidence.
3. Current GitHub code + reproducible Actions artifacts/logs — implementation/execution evidence.
4. `INDEXALERT_RESEARCH_STATUS.md` — status summary; older passages may be superseded.
5. `INDEXALERT_KRX_SOURCE_ACCESS_CONTRACT.md`, `INDEXALERT_KRX_SOURCE_GATE_AUDIT.md` and `INDEXALERT_EXECUTION_EVIDENCE_CONTRACT.md` — source/evidence boundary contracts and current source audit.
6. This snapshot — cross-chat/cross-branch handoff and unfinished-work registry.
7. Older chats/notes — historical context only.

When sources conflict, current reproducible GitHub evidence wins.

## 1. Frozen research contract

- H5 = Core development horizon.
- H10 = `REJECTED_CURRENT_CANDIDATE_DO_NOT_RETUNE`; do not sweep H6-H9 or retune H10 from completed outcomes.
- H20 = outside requested 5-10-session scope; archive only.
- Anchored walk-forward: train 504 / calibration 126 / test 126.
- H5/H10 share fold endpoints; horizon-matched purge/embargo and label-overlap protection are mandatory.
- Calibration is disjoint and may use only information/outcomes available before test prediction.
- Test/holdout outcomes must not choose thresholds, quantiles, TopK, costs or policy.
- Correct CPCV = 6 contiguous groups, all two-test-group combinations, each remaining group once as calibration, other three train = **60 cases per horizon**.
- CPCV is stability evidence only, not forward OOS, sealed holdout or promotion authority.
- Original decision-time Top3 is frozen. Vetoed/held/unfillable slots remain empty; **no rank-4+ backfill**.
- 0..3 trades and `NO_TRADE` are valid.
- Strict PIT/availability lineage and KRX corporate-action-safe base-price returns are mandatory.
- Primary evidence includes executable cost-adjusted NetReturn/NetEV, PF, cluster uncertainty, MDD, ES95/ES99, cost stress, coverage/abstention, execution/capacity and tail dependence.
- Current square-root impact estimate is a cost proxy, not empirical capacity-aware NetEV.
- Official historical security/status, exact halt/cleanup/delisting economics, partial/no fills, fill time/price, markout, latency/expiry and empirical capacity remain hard blockers.
- Sealed holdout stays one-shot and unburned until blockers/code/protocol are frozen. After a valid holdout, require prospective Shadow S1 then frozen Fresh Confirmation S2.
- Never relax q25, TopK, costs, recent-evidence or execution assumptions merely to manufacture trades.

## 2. Completed research state

### H5 developmental reference

Strongest compact selection-conditioned result:
- 278 executed entries / 137 trade days
- mean NetReturn ~+1.150%, PF ~1.546
- cluster lower bound below zero
- 2x-cost mean ~+0.787%, PF ~1.344
- portfolio total ~+16.39%, CAGR ~1.83%, MDD ~-24.39%, Sharpe ~0.23
- admissions concentrated in 2018-2021; none in 2022-2026 / latest 504 OOS
- remove-best-5 makes mean economics negative and PF < 1

Classification: `DEVELOPMENTAL_NOT_CURRENTLY_PROMOTABLE`.

### Corrected 60-case CPCV

Action `36637351334` completed successfully under the frozen 60-case protocol.
- H5 median PF **0.381**; positive NetEV **43.3%**; positive date-cluster LCB **11.7%**.
- H10 median PF **0.745**; positive NetEV **50.0%**; positive date-cluster LCB **33.3%**.

Verdict: CPCV does not establish robust edge. Older 15-combination CPCV and old-chat H10 PF recollections such as ~0.454 are superseded and invalid for decisions.

### Uncertainty Audit

`EXP-2026-09-29-UNCERTAINTY-AUDIT-01`, Action `36637333875`.
Decision: **KEEP_ABSTENTION**.
- all-OOS q25-blocked mean -0.8432%, PF 0.8425, cluster interval entirely below zero
- 2022+ q25-blocked mean -1.2551%, PF 0.8005
- latest-504 blocked mean -0.6263%, PF 0.9012; remove-best-5 -1.2697%, PF 0.8011
- latest conservative-positive subset only 4 rows, mean -22.5669%, PF 0.1381

Do not weaken q25 or launch conditional-q25 rescue from this result.

### Policy-aligned calibration

`EXP-2026-09-29-POLICY-CAL-01`, Action `36643183157`, artifact `11067383547`.
- reference and challenger have the same 278 compact decision-date/symbol selections
- no selection differences
- compact portfolio and cost-stress results identical

Disposition: **ADOPT STRUCTURAL ALIGNMENT / NO PERFORMANCE CHANGE / NOT PROMOTION EVIDENCE**.

### Other dispositions

- Rolling-160 recency challenger: rejected; do not sweep nearby windows.
- CA-safe daily path family: rejected/do not retune.
- H10 anchored challenger: `REJECTED_CURRENT_CANDIDATE_DO_NOT_RETUNE`.
- H20: out of scope/archive.
- Stop price-only threshold/feature mining; future information must be genuinely independent and PIT-valid.

## 3. KRX official source/access state — audited 2026-10-01

Canonical source boundary: `INDEXALERT_KRX_SOURCE_ACCESS_CONTRACT.md`.  
Current source audit: `INDEXALERT_KRX_SOURCE_GATE_AUDIT.md`.

Three access routes must remain distinct:
1. KRX OpenAPI — separate `AUTH_KEY`, administrator approval and per-API service approval.
2. KRX Data Marketplace authenticated web session — exploratory probes use `KRX_ID` / `KRX_PW` only for this route when configured.
3. KRX purchased/distributed data products — separate access/licensing route.

Do not substitute one authentication/access route for another. Do not assume an OpenAPI key supplies a dataset until the exact official service mapping, schema, history and approval are established.

### Frozen A-F source gates

- A `AUTHORIZED_OFFICIAL_ROUTE`
- B `EXACT_DATASET_SCHEMA_MAPPING`
- C `HISTORICAL_COVERAGE_SECURITY_MAPPING`
- D `PIT_AVAILABILITY_LINEAGE`
- E `REPRODUCIBLE_INTEGRITY_FAIL_CLOSED`
- F `INTENDED_USE_RIGHTS`

Only `PASS` closes a gate; `PARTIAL` is not a pass. Even A-F all PASS is source-governance evidence only and cannot by itself authorize Alpha/Final-Judge promotion, sealed holdout or live trading.

Required Final Judge status families include common-stock identity/mapping, trading halt, cleanup trading, delisting and delisted-price/economic history. Known official Data Marketplace screens include MDCSTAT213/237/238/239. Candidate low-level BLDs for MDCSTAT213/237 remain provisional until an authorized response and exact contract validate them.

Current adapters and gate infrastructure:
- `research_v1_krx_official_status.py`
- `research_v1_krx_cleanup_status.py`
- `research_v1_krx_source_gates.py`
- `research_v1_krx_status_source_probe.py`
- `research_v1_krx_investor_flow_probe.py`
- `test_research_v1_krx_source_gates.py`
- `test_research_v1_krx_source_probes.py`

### Important correction: prior green source-probe Actions were not authenticated-source successes

Direct audit of Actions logs established that the source-probe runtimes had no KRX credentials configured:
- status source Action `36668563968`: `KRX_ID`, `KRX_PW`, `KRX_OPENAPI_AUTH_KEY` all absent; internal result `AUTH_NOT_CONFIGURED`.
- investor-flow Action `36668579581`: same; internal result `AUTH_NOT_CONFIGURED`.

Therefore neither run made an authenticated KRX request. The green workflow result means the diagnostic program executed successfully; it is **not** authenticated source evidence.

The probe code now emits `authenticated_request_attempted`, machine-readable `source_gate_audit`, and contract/result SHA256 fingerprints. Missing session credentials force Gate A to `BLOCKED`; merely supplying credentials may raise A only to `PARTIAL`, never directly to `PASS`.

Latest machine-audited source runs:

**Security/status — Action `36808057709`**
- workflow conclusion: success as diagnostic
- `authenticated_request_attempted=false`
- A `BLOCKED`, B `PARTIAL`, C `BLOCKED`, D `BLOCKED`, E `PARTIAL`, F `PARTIAL`
- `source_contract_closed_for_declared_scope=false`
- `judge_security_status_ready=false`
- contract fingerprint `1a78f35d3f207d97a168efa594962358de63f7686e993d2af5539d2b0d3d582a`
- result fingerprint `21764684b02ec8c572d63171ed44bfa3393e39c02e2b1c4990a2b616efd0e2b5`
- artifact ID `11138570329`

**Investor flow — Action `36808077021`**
- workflow conclusion: success as diagnostic
- `authenticated_request_attempted=false`
- A `BLOCKED`, B `PARTIAL`, C `BLOCKED`, D `PARTIAL`, E `PARTIAL`, F `PARTIAL`
- `source_contract_closed_for_declared_scope=false`
- `feature_performance_testing_authorized=false`
- contract fingerprint `b00669f4c82102a2feaca436ba83f309bf6cfd5f33ab2fccd9bce024a2cbf8d8`
- result fingerprint `31015fb1e623f5eaf204753a0b5e61b4438405cf9f8ec8818f2eced4e9f4283a`
- artifact ID `11137504925`

Official KRX integrity including source-gate/probe tests passed in Actions `36808122270` and `36808133821`.

Investor-flow rule remains frozen: final day-D KRX investor trading results are not eligible before official publication; the audited Data Marketplace page states final day-D results are supplied after 20:00. Therefore final D flow may enter only the next eligible decision after publication. No same-day undocumented proxy substitution.

Current product/licensing rule: free/public OpenAPI permissions must not be assumed to permit a future external/commercial IndexAlert service. Data-use rights are a product activation gate independent of Alpha promotion.

## 4. Execution evidence — corrected tier contract

Canonical boundary: `INDEXALERT_EXECUTION_EVIDENCE_CONTRACT.md`.

A prior design mistake classified `PROSPECTIVE_SHADOW_EXECUTION_LOG` as if Shadow could contain empirical broker fills. This is now corrected.

Frozen tiers:
1. **`PROSPECTIVE_SHADOW_DECISION_LOG`** — decision/intention observation only; SHADOW submits no broker order and cannot carry/claim broker fills.
2. **`PROSPECTIVE_PAPER_EXECUTION_LOG`** — actual supported paper/simulation broker responses; validates adapter/state/reconciliation plumbing but **not real-market fill quality**.
3. **`PROSPECTIVE_LIVE_EXECUTION_LOG`** — actual real-account broker executions; the only tier eligible to contribute to empirical live fill/slippage/partial-fill/capacity evidence.

Backtest/synthetic/would-be Shadow fills are forbidden as empirical evidence. Zero-fill observations remain valid; filled observations require actual fill timestamps/price and required markouts. No minimum sample threshold has been invented merely to declare readiness.

Research implementation:
- `research_v1_execution_evidence.py` rejects Shadow fill records and distinguishes PAPER vs LIVE.
- PAPER-only evidence may be structurally valid but cannot set `live_empirical_execution_evidence_ready=true`.
- `promotion_ready` remains false by construction because statistical/capacity/holdout/prospective gates are separate.
- Execution Evidence Integrity Action `36668905306` on commit `0d6b97e988ff1fdeb54e9aa545303e101759f6cf` completed **successfully**.

Server implementation:
- `execution_evidence_ledger.py` on `index-alert-server` accepts only explicit PAPER or LIVE sources for new fill records.
- Shadow decision source and former `PROSPECTIVE_SHADOW_EXECUTION_LOG` are rejected for new writes.
- new observation identity includes source so PAPER and LIVE evidence for the same decision cannot collide.
- historical legacy Shadow-labelled rows, if any, are not deleted or rewritten; summary quarantines them as `legacy_shadow_fill` and excludes them from live-evidence claims.
- Server Tests Action `36669071810` on server commit `65855916afd52d081453bc511b6b82df3ec948b1` completed **successfully**, including the full unittest suite.

Production deployment:
- Railway production service `indexalert-runtime` runs server commit `65855916afd52d081453bc511b6b82df3ec948b1`.
- deployment `34e76729-ff9b-4fa5-8334-b8b591a336ba` completed **SUCCESS** on 2026-09-30 KST.
- the corrected PAPER/LIVE ledger semantics are production-active.
- persistent `/data` volume remained mounted and `production_v31:app` reached application startup successfully.
- Railway healthcheck `GET /health` returned **200 OK** during deployment.
- protected `INDEXALERT_EXECUTION_LOG_TOKEN` remains configured; no secret value is stored in this snapshot.
- no synthetic execution rows were inserted.
- deployment/health success is operational evidence only. The empirical blocker remains open until genuine prospective LIVE observations exist and later pass sufficiency/capacity/risk gates.

## 5. Broker / automation product boundary

`INDEXALERT_BROKER_EXECUTION_CONTRACT.md` remains architecture-only; live ordering is disabled.

Required sequence:
`Research / Backtest -> Shadow -> Kiwoom Paper API -> Tiny Live -> Limited Live -> Production`

No stage may be skipped because technical connectivity exists.

Frozen default UX from `INDEXALERT_AUTOMATION_UX_CONTRACT.md`:
- connect an eligible broker account;
- user controls automated operation ON/OFF;
- user sets `max_automation_capital_krw` only.

The maximum is a hard ceiling, never an investment target. Decision/Risk/Execution Engine owns selection, entry/no-entry, quantity, cash retention, holding period, exits, replacement and re-entry under validated policy. No valid opportunity means `NO_TRADE` and cash. Stop-loss %, take-profit %, holdings count and weights are not routine user settings. User retains final control over activation/stop and capital ceiling.

Action `36664662044` passed the product-contract tests. Real-account Kiwoom ordering must not be implemented/activated merely to populate evidence while the research/promotion gates are still unmet.

## 6. Realtime / server / Android operational state

### Server / Railway

- latest server production commit: `65855916afd52d081453bc511b6b82df3ec948b1`.
- latest server full test run `36669071810` = success.
- Railway deployment `34e76729-ff9b-4fa5-8334-b8b591a336ba` = **SUCCESS** on the same commit.
- startup completed under `production_v31:app`; persistent `/data` volume mounted; Railway `/health` = **200 OK**.
- protected execution evidence collection and corrected evidence-tier semantics are production-active.

Last directly verified production push-health snapshot before the execution-logging environment update:
- `ok=true`
- `firebase=true`
- `registered_devices=1`
- `pending_deliveries=0`
- `sent_deliveries=1`
- `received_deliveries=0`
- `unconfirmed_sent_deliveries=1`
- `last_client_receipt_at=null`
- `client_receipts_supported=true`
- old `execution_logging_configured=false` was superseded by verified Railway configuration and successful deployment, but a fresh external `/push-health` read has not been independently obtained from the current tool environment.

A server `sent` record is not proof the handset received/presented the notification.

### Android

Last audited build branch head: `55d72dc576131d1f8c2f6f01b9f4951a2e088911` (`Fix WorkManager receipt result type`). Re-fetch before editing.

APK Action `36665289417` = success.
- debug artifact `IndexAlert-v4.4-debug`, ID `11076077796`, SHA256 `b195fa90e0e5d074bc1c0764918eb78e23537da693b9eb514547fb1fc48033be`
- unsigned release artifact `IndexAlert-v4.4-unsigned-release`, ID `11075977955`, SHA256 `b5f0e090e167af076510eb831a83e38506793b796acdd9c9587878cb2e7afa70`

Physical E2E gate remains open: current-build handset must receive the isolated self-test and production must show `received_deliveries >= 1` with non-null `last_client_receipt_at`. Until then: **CODE/BUILD/SERVER VERIFIED; PHYSICAL CLIENT RECEIPT PENDING**.

## 7. Explicit unfinished-work registry

Continue from the first actionable unresolved item supported by latest GitHub state:
1. **DONE:** corrected 60-case H5/H10 CPCV archived.
2. **DONE:** Uncertainty Audit -> KEEP_ABSTENTION.
3. **DONE:** Policy Calibration -> structural alignment only.
4. **DONE:** KRX A-F source-governance contract, machine audit, probe fingerprints and CI enforcement are implemented and tested.
5. **EXTERNAL DATA-AUTH BLOCKER:** Gate A for both KRX status and investor-flow is `BLOCKED` because the audited GitHub Actions runtime has no KRX credentials/authorized source configured. Do not place secrets in source code/logs; configure an approved route through secure secret management before an authenticated diagnostic can occur.
6. **EXTERNAL DATA/COVERAGE BLOCKER:** status Gates C/D remain blocked until full historical common-stock/security-status coverage and PIT lineage are reconstructed/audited; investor Gate C remains blocked and D partial until historical availability lineage is complete.
7. **DONE:** Shadow/Paper/Live execution evidence semantics corrected; research CI and server full tests pass.
8. **DONE:** corrected execution ledger deployed to Railway production as deployment `34e76729-ff9b-4fa5-8334-b8b591a336ba`; `/health` 200 OK. Deployment does not authorize trading.
9. **EMPIRICAL DATA BLOCKER:** collect genuine execution evidence only at the appropriate staged mode. Shadow supplies decisions, Paper supplies plumbing evidence, Tiny Live+ supplies real empirical fill evidence. Do not fabricate rows.
10. Keep sealed holdout untouched until official data/execution blockers, code and protocol are frozen; then follow the frozen holdout -> Shadow S1 -> Fresh Confirmation S2 sequence.
11. **PHYSICAL E2E PENDING:** one current Android-build handset receipt is still required for full notification end-to-end verification.
12. **LIVE ORDERING DISABLED:** minimal-control UX is frozen, but real Kiwoom ordering remains gated by research/promotion, official API verification, safety controls and explicit user activation.

## 8. Continuation rule

On every continuation:
- re-read current Master Spec, Ledger, source/evidence contracts, source-gate audit, this snapshot and relevant branch HEAD/Actions;
- skip completed/rejected experiments;
- never revive rejected candidates by threshold/cost/horizon mining;
- never convert Shadow or Paper observations into live empirical evidence;
- never interpret a green source-probe workflow as authenticated-source success without checking its internal result and `authenticated_request_attempted` flag;
- if old chat conflicts with reproducible GitHub evidence, GitHub wins;
- commit each material result/contract correction to canonical GitHub docs so chat history remains nonessential.

## 9. Old-chat deletion gate

Older IndexAlert Chat/Work rooms remain unnecessary as a project-state dependency. Their material continuity information is preserved in GitHub. Deleting old chats does not delete GitHub code, Actions artifacts, Master Spec, Ledger, source/evidence contracts or this snapshot.
