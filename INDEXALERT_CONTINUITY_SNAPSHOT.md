# IndexAlert Continuity Snapshot — Canonical Cross-Chat Handoff

Updated: 2026-09-30 KST
Branch of record: `index-alert-research-v1`

## 0. Purpose and authority

This file keeps IndexAlert continuation independent of older Chat/Work rooms.

Authority order:
1. `INDEXALERT_MASTER_SPEC.md` — frozen statistical/validation contract.
2. `INDEXALERT_RESEARCH_LEDGER.md` — experiments, outcomes, dispositions, negative evidence.
3. Current GitHub code + reproducible Actions artifacts/logs — implementation/execution evidence.
4. `INDEXALERT_RESEARCH_STATUS.md` — current status summary.
5. This snapshot — cross-chat/cross-branch handoff and legacy evidence.
6. Older chats/notes — historical context only.

When sources conflict, current reproducible GitHub evidence wins.

## 1. Frozen contract that must survive chat deletion

- H5 = Core development horizon.
- H10 = `REJECTED_CURRENT_CANDIDATE_DO_NOT_RETUNE`; do not sweep H6-H9 or retune H10 from completed outcomes.
- H20 = outside requested 5-10-session scope; archive only.
- Anchored walk-forward: train 504 / calibration 126 / test 126.
- H5/H10 common fold endpoints; horizon-matched purge/embargo and label-overlap protection.
- Calibration is disjoint and may use only information/outcomes available before test prediction.
- Test/holdout outcomes must not choose thresholds, quantiles, TopK, costs or policy.
- Correct CPCV: 6 contiguous groups; all two-test-group combinations; each remaining group once as calibration; other three train; **60 cases per horizon**.
- CPCV is stability evidence only, not forward OOS, holdout or promotion authority.
- Original decision-time Top3 frozen; vetoed/held/unfillable slots remain empty; **no rank-4+ backfill**.
- 0..3 trades and NO_TRADE valid.
- Strict PIT/availability lineage and KRX corporate-action-safe base-price returns mandatory.
- Primary evidence: executable cost-adjusted NetReturn/NetEV, PF, cluster uncertainty, MDD, ES95/ES99, cost stress, coverage/abstention, execution/capacity and tail dependence.
- Current square-root impact is a cost proxy, not empirical capacity-aware NetEV.
- Official historical security/status, exact halt/delisting economics, partial fills, fill time/price, markout, latency/expiry and empirical capacity are hard blockers.
- Sealed holdout stays one-shot and unburned until blockers/code/protocol are frozen; after it, require Shadow S1 then frozen Fresh Confirmation S2.
- Never relax q25, TopK, costs, recent-evidence or execution assumptions merely to manufacture trades.

## 2. Current research state

### H5 developmental reference

Strongest compact selection-conditioned result:
- 278 executed entries / 137 trade days
- mean NetReturn ~+1.150%, PF ~1.546
- cluster lower bound below zero
- 2x-cost mean ~+0.787%, PF ~1.344
- portfolio total ~+16.39%, CAGR ~1.83%, MDD ~-24.39%, Sharpe ~0.23
- admissions concentrated in 2018-2021; none in 2022-2026 / latest 504 OOS
- remove-best-5 turns mean economics negative and PF below 1

Classification: `DEVELOPMENTAL_NOT_CURRENTLY_PROMOTABLE`.

### Corrected 60-case CPCV — completed

Action `36637351334` completed successfully under the frozen 60-case protocol.

Authoritative values:
- H5 median PF **0.381**; positive NetEV **43.3%**; positive date-cluster LCB **11.7%**.
- H10 median PF **0.745**; positive NetEV **50.0%**; positive date-cluster LCB **33.3%**.

Verdict: CPCV does not establish robust edge.

The older H10 15-combination result is **HISTORICAL / SUPERSEDED**. Old-chat recollections including H10 PF ~0.454 are invalid for decisions. Earlier exit-137/143 runs failed from memory/process accumulation; splitwise generate -> evaluate -> release fixed execution without altering the statistical contract.

### Uncertainty Audit — completed

`EXP-2026-09-29-UNCERTAINTY-AUDIT-01`, Action `36637333875`.

Key conclusion: **KEEP_ABSTENTION**.
- all-OOS q25-blocked mean -0.8432%, PF 0.8425, cluster interval entirely below zero
- 2022+ q25-blocked mean -1.2551%, PF 0.8005
- latest-504 blocked mean -0.6263%, PF 0.9012; remove-best-5 -1.2697%, PF 0.8011
- latest conservative-positive subset only 4 rows, mean -22.5669%, PF 0.1381

Do not weaken q25 and do not launch conditional-q25 rescue from this result. Seek orthogonal PIT-valid information.

Audit artifact also states `common_stock_identity_validated=false`, `judge_eligible=false`.

### Policy-aligned calibration — completed

`EXP-2026-09-29-POLICY-CAL-01`, Action `36643183157`, artifact `11067383547`.

The calibration population was aligned to the same preliminary post-Top3 normal-market veto without changing q-level/model/features/windows/costs/admission or allowing backfill.

Result:
- reference and challenger have the **same 278 compact decision-date/symbol selections**
- no reference-only or challenger-only selected rows
- compact portfolio and cost-stress results exactly identical
- exported row differences are only model naming

Disposition: **ADOPT STRUCTURAL ALIGNMENT / NO PERFORMANCE CHANGE / NOT PROMOTION EVIDENCE**. The preliminary normal-market proxy still requires official historical status validation.

## 3. Other material dispositions

- Rolling-160 recency challenger: rejected; do not sweep nearby windows.
- CA-safe daily path family: rejected/do not retune.
- H10 anchored challenger: `REJECTED_CURRENT_CANDIDATE_DO_NOT_RETUNE` despite strong historical point estimates because admissions are old, recent evidence is absent, corrected CPCV is weak, and blockers remain.
- H20: out of scope/archive.
- Price-only threshold/feature mining should stop; next information must be genuinely independent and PIT-valid.

## 4. KRX official status / investor-flow source state

Official KRX issue-statistics screens required by the status blocker are confirmed to exist, including trading-halt history (MDCSTAT213), cleanup-trading status (MDCSTAT237), delisting status (MDCSTAT238) and delisted-security price history (MDCSTAT239). Source availability is distinct from authenticated reproducible historical ingestion.

### Official status adapter and source probe

- `research_v1_krx_official_status.py` normalises official identity, halt, delisting and delisted-price evidence and fails closed on missing source/availability lineage.
- `research_v1_krx_cleanup_status.py` now normalises official MDCSTAT237 cleanup-trading intervals, treats cleanup status as inclusive `[start,end]`, validates planned delisting occurs after cleanup end, and deliberately **does not invent execution returns/fills**.
- Official KRX status integrity Action `36646910657` completed **successfully**, including cleanup-status fail-closed tests.
- Metadata-only source probe `research_v1_krx_status_source_probe.py` was added; Action `36646695064` completed successfully at the infrastructure level.
- Probe artifact `11068429448`, SHA256 `a58991a9f34384a84b32db4b988e0a842a8cbb7de6fa77efa77b3ac29461acc1` reports:
  - `credentials_present=false`
  - `status=AUTH_NOT_CONFIGURED`
  - `judge_security_status_ready=false`
  - no numeric market data persisted

Therefore official historical security/status ingestion is **externally blocked on KRX authenticated source credentials**, not on adapter/test readiness. Candidate low-level BLDs for MDCSTAT213/237 remain unpromoted until a live authenticated response validates them.

### Investor flow

- `research_v1_krx_investor_flow_probe.py` is source-feasibility only; it is not a feature test.
- Action `36550623671`, artifact `11024238450`, SHA256 `e24ec0b86b22eaea6c54941cbaced3eb3f5333b81cde1f0fbcb483356db1eac8` also reports `credentials_present=false`, `AUTH_NOT_CONFIGURED`.
- Day-D final investor flow remains ineligible until official access, historical coverage, stable mapping and `event_time/published_at/available_at/ingested_at` lineage are established. It must not be substituted with an undocumented same-day proxy.

## 5. Execution realism infrastructure

Current H5 fixed-horizon learning target assumes economic entry at the next regular-session open and exit at D+5 close, with modeled costs. That is **not empirical fill evidence**.

New fail-closed module `research_v1_execution_evidence.py` requires prospective Shadow/live-style observations to preserve:
- requested and filled quantity
- full / partial / zero fill
- recommendation timestamp and order-submission latency
- first/final fill time
- average fill price and reference open
- 5-minute / 30-minute / close post-fill markouts
- explicit empirical source attestation and ingestion timestamp

Backtest/simulated fills cannot be relabeled empirical; zero-fill rows cannot carry fabricated fill price/timestamps; filled rows require markouts. Structural CI Action `36647064858` completed **successfully**. This closes the **schema/integrity preparation**, not the empirical evidence blocker. Actual prospective observations and empirical capacity remain missing.

The current production server also has `execution_evidence_ledger.py` and broker-neutral `/execution-evidence` interfaces, but the verified production `/push-health` snapshot reports `execution_logging_configured=false`. Therefore production collection readiness must not be confused with schema readiness; prospective execution evidence is not yet being collected through the protected write path.

## 6. Current explicit unfinished-work registry

Continue from the first unresolved/actionable item supported by latest GitHub state:
1. **DONE:** corrected 60-case H5/H10 CPCV read and archived.
2. **DONE:** `UNCERTAINTY-AUDIT-01` read; decision KEEP_ABSTENTION.
3. **DONE:** `POLICY-CAL-01` read; structural population alignment only, no performance claim.
4. **INFRA DONE / EXTERNAL BLOCKER:** official KRX status adapters + cleanup status + metadata probe are ready, but authenticated KRX historical source access is not configured. Do not claim Judge status readiness until real data + PIT lineage pass coverage audit.
5. **EXTERNAL BLOCKER:** official KRX investor-flow probe is also `AUTH_NOT_CONFIGURED`; no performance test permitted.
6. **SCHEMA DONE / DATA NEXT:** empirical execution evidence schema and CI are ready. Production ledger interfaces exist, but `execution_logging_configured=false`; protected collection configuration and then prospective Shadow observations for fill ratio/time/price, partial/no fills, latency and markout remain next. Add empirical capacity evidence rather than relying only on square-root impact.
7. Keep sealed holdout untouched until data/execution blockers, code and protocol are frozen; then Shadow S1 -> Fresh Confirmation S2.
8. **SERVER/ANDROID CODE+DEPLOY VERIFIED / PHYSICAL E2E PENDING:** latest server production and Android build are verified as described in section 7. The remaining notification transport gate is one current-build physical handset receipt that changes the server aggregate from `received_deliveries=0` to at least one acknowledged receipt. Do not call FCM end-to-end fully verified before that happens.
9. **PRODUCT CONTRACT DONE / LIVE STILL DISABLED:** minimal-control automated-operation UX is frozen in `INDEXALERT_AUTOMATION_UX_CONTRACT.md` and enforced by broker-neutral `indexalert_automation_control.py`. User-facing routine controls are automation ON/OFF and maximum automation capital only; the maximum is a hard ceiling, never an investment target; `NO_TRADE`/cash retention remain valid. Action `36664662044` passed the contract tests. Future broker/live implementation must preserve this contract without bypassing promotion gates.

## 7. Realtime / server / Android operational verification

### Current server branch / production

- `index-alert-server` verified head: `b4b619edc12bf946e95b1a62c22037a08db367f7` (`Install full server requirements in smoke CI`).
- Previous smoke failure was a CI dependency defect (`fastapi` / `apscheduler` absent from the smoke environment), not an application-logic failure. Workflow now installs full `requirements.txt`.
- Server Smoke Action `36665043317` completed **successfully**. The local syntax/regression phase passed **23 tests**.
- Railway production deployment `bcdbe39d-840f-4df5-b72c-6114ffe9f53f` completed **SUCCESS** from the same `b4b619ed...` source commit. This is a fresh source build, not a redeploy of the prior snapshot.
- Production smoke subsequently validated `/health`, `/push-health`, `/openapi.json`, `/status`, `/laggards` and `/next-day-probabilities`, including `/push-ack` API presence, basis checks and probability payload checks.

Verified production push-health snapshot after deployment:
- `ok=true`
- `firebase=true`
- `registered_devices=1`
- `pending_deliveries=0`
- `sent_deliveries=1`
- `received_deliveries=0`
- `unconfirmed_sent_deliveries=1`
- `last_client_receipt_at=null`
- `client_receipts_supported=true`
- `execution_logging_configured=false`
- `tokens_exposed=false`

Interpretation: server/Firebase transport, registration accounting and receipt endpoint are operational, but **there is no current-build handset receipt yet**. A server `sent` record is not proof that the phone received/presented the message.

### Current Android build

- `index-alert-build` verified head: `55d72dc576131d1f8c2f6f01b9f4951a2e088911` (`Fix WorkManager receipt result type`).
- Prior build failure was a Kotlin type ambiguity between standard `Result` and WorkManager `Result`; the fix explicitly returns `ListenableWorker.Result` without changing notification/trading semantics.
- APK Action `36665289417` completed **successfully**; Gradle built debug and unsigned release variants and uploaded all artifacts.
- Debug artifact: `IndexAlert-v4.4-debug`, artifact ID `11076077796`, SHA256 `b195fa90e0e5d074bc1c0764918eb78e23537da693b9eb514547fb1fc48033be`, expires 2026-12-29.
- Unsigned release artifact: `IndexAlert-v4.4-unsigned-release`, artifact ID `11075977955`, SHA256 `b5f0e090e167af076510eb831a83e38506793b796acdd9c9587878cb2e7afa70`, expires 2026-12-29.
- Current `Push.kt` registers only when notification permission is available, stores only a SHA256 token hash for acknowledgements, receives FCM data messages, records/schedules an `event_id` receipt and POSTs `/push-ack` through WorkManager with bounded retries.

### Physical E2E gate

The next current-version notification gate is deliberately simple and operational, not statistical:
1. install/run the current debug build on the target Android handset and allow notifications;
2. let the app register its current FCM token with production;
3. send/receive one benign IndexAlert test notification carrying an `event_id` through the normal server/FCM path;
4. confirm the phone receives it and production `/push-health` reports `received_deliveries >= 1`, `unconfirmed_sent_deliveries` correspondingly reduced and non-null `last_client_receipt_at`.

Until this gate passes, classify current notification health as **CODE/BUILD/SERVER VERIFIED; PHYSICAL CLIENT RECEIPT PENDING**.

Historical audit anchors only:
- probability/realtime lineage `index-alert-v41-research` previously @ `85bfd892ef8cc8e36b434983945cf45ce9d7e070`
- old server anchor `ccde47271fd85c3d5a880d7e18531131d625c309`
- old Android/build anchor `d8f61cf2712eb91651b0ce25810aef0209697e00`

Older chat operational evidence (old APK install/token registration/test push) remains `LEGACY_CHAT_EVIDENCE`; it does not substitute for the current physical E2E gate above.

## 8. Continuation rule

On every continuation:
- re-read current Master Spec, Ledger, this snapshot and relevant branch HEAD/Actions
- skip completed/rejected experiments
- never revive rejected candidates by threshold/cost/horizon mining
- if old chat conflicts with reproducible GitHub evidence, GitHub wins
- commit each material result to Ledger/Status/Snapshot so chat history remains nonessential

## 9. Old-chat deletion gate

Older IndexAlert Chat/Work rooms remain unnecessary as a project-state dependency. Their material continuity information is preserved in GitHub. Deleting old chats does not delete GitHub code, Actions artifacts, Master Spec, Ledger or this snapshot.

## 10. Frozen automated-operation product UX

The long-term default UX is intentionally simple:
- connect an eligible broker account;
- choose whether automated operation is enabled;
- set `max_automation_capital_krw`.

The user is not required to tune stop-loss, take-profit, number of holdings, position weights, holding period, replacement or re-entry parameters. The validated Decision / Risk / Execution Engine owns those decisions beneath the user's hard capital ceiling and all internal safety/promotion gates.

The ceiling may remain partly or entirely unused. No candidate passing the frozen economic/risk/execution standard means `NO_TRADE` and cash. Increasing the ceiling never changes admission standards. Disabling automation blocks new automated exposure; broker reconciliation and safe-stop handling still govern existing orders/positions.
