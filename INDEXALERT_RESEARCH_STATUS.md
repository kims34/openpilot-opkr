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

Latest source-governance reference: KRX integrity Action `36817784717` at `bc5792640e0ba611f50f459f8c3b17c108cdd4bf` succeeded with structured authorization provenance through source-data admission.

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

Execution preregistration Action `36835013828` succeeded. Contract-drift semantics are additionally guarded in CI.

## External evidence still missing

Internal code cannot fabricate approved KRX source access/history/PIT/use rights, real complete affected-position status economics, genuine staged LIVE execution observations, or a later independent execution-sufficiency assessment against a properly preregistered protocol.

## Operational evidence state

Railway production `indexalert-runtime` previously ran server commit `65855916afd52d081453bc511b6b82df3ec948b1`; deployment `34e76729-ff9b-4fa5-8334-b8b591a336ba` had `/health` 200. This is operational evidence only and does not authorize trading. Real-account ordering remains disabled.

## Remaining blockers

1. **KRX authorization/data:** approved route/product, credentials/structured approval evidence, authenticated source proof and full official history.
2. **Security/status economics:** real complete affected-position fill/recovery economics must pass the exact audit; the internal auditor alone does not close the blocker.
3. **Investor flow:** real full official history must pass provenance, PIT, coverage, A-F and source-data admission; then separate preregistration before any feature-performance experiment.
4. **Execution:** genuine staged LIVE observations plus a separately frozen-before-LIVE sufficiency protocol and later assessment. Structurally valid LIVE rows alone do not close this blocker.
5. **Research governance:** no rejected-candidate revival; maintain Ledger/multiple-testing discipline.
6. **One-shot sealed holdout:** untouched until source/execution/code/protocol freeze; then Shadow S1 -> Fresh Confirmation S2.
7. **Physical notification E2E:** one current-build Android receipt still required.
8. **Live ordering:** disabled until all frozen promotion/safety gates and explicit user activation requirements are met.

## Promotion rule

Positive mean, PF or CAGR alone cannot promote a candidate. Promotion requires cost-adjusted OOS economics, PF > 1, positive date-cluster lower bound, best-day robustness, credible recent evidence, acceptable MDD/ES/tails, cost-stress survival, PIT correctness, official source/status integrity and execution realism. Final promotion additionally requires the one-shot sealed holdout and prospective confirmation sequence.
