# IndexAlert Research Status

Updated: 2026-10-01 KST  
Branch: `index-alert-research-v1`  
Master authority: `INDEXALERT_MASTER_SPEC.md`  
Experiment authority: `INDEXALERT_RESEARCH_LEDGER.md`  
Promotion authority: **none yet** — development evidence cannot promote a live strategy without the frozen source/execution/statistical gates, one-shot sealed holdout and prospective confirmation sequence.

## Current bottom line

The current price/volume/context stack is **not ready for live short-term investment recommendations**.

The research process has strict PIT discipline, corporate-action-safe returns, original decision-time Top3/no-backfill, realistic cost treatment, abstention, anchored purged walk-forward, corrected CPCV and reproducible CI. The evidence still does not establish a robust, recent, execution-ready edge.

Do **not** relax q25, TopK, costs, recent-evidence requirements, horizon, fill/capacity assumptions or holdout rules merely to create trades.

## Frozen policy / validation rules

- H5 = Core development horizon.
- H10 = `REJECTED_CURRENT_CANDIDATE_DO_NOT_RETUNE`; do not sweep H6-H9 or retune H10 from completed outcomes.
- H20 = outside the requested 5-10-session scope; archive only.
- Anchored walk-forward: train 504 / calibration 126 / test 126.
- Horizon-matched label-overlap purge and embargo.
- Original decision-time Top3 frozen; vetoed/held/unfillable slots stay empty; **no rank-4+ backfill**.
- 0..3 trades and `NO_TRADE` are valid.
- Corporate-action-safe KRX base-price returns are mandatory.
- Primary evidence = executable cost-adjusted NetReturn/NetEV, PF, date-cluster uncertainty, MDD, ES/tails, cost stress, coverage/abstention, execution/capacity realism and recent evidence.
- Sealed holdout is one-shot and remains untouched until blockers/code/protocol are frozen.
- After a valid holdout: prospective trading-policy Shadow S1 -> frozen Fresh Confirmation S2.

## Current empirical reference and negative evidence

### H5 developmental reference — not promotable

Selection-conditioned residual calibration with the preliminary post-rank normal-market fail-closed overlay remains a developmental reference, not a Champion:
- 278 executed entries / 137 trade days
- mean NetReturn **+1.150%**
- PF **1.546**
- date-cluster 95% lower bound remains below zero
- 2x-cost mean **+0.787%**, PF **1.344**
- portfolio total **+16.39%**, CAGR ~1.83%, MDD **-24.39%**, Sharpe ~0.23
- admissions concentrated in 2018-2021
- no admissions in 2022-2026 / latest 504 OOS sessions
- remove-best-5 turns mean negative and PF below 1

Classification: `DEVELOPMENTAL_NOT_CURRENTLY_PROMOTABLE`.

### Uncertainty audit

`EXP-2026-09-29-UNCERTAINTY-AUDIT-01`, Action `36637333875`: **KEEP_ABSTENTION**.
- all-OOS q25-blocked mean -0.8432%, PF 0.8425, cluster interval entirely below zero
- 2022+ q25-blocked mean -1.2551%, PF 0.8005
- latest-504 blocked mean -0.6263%, PF 0.9012; remove-best-5 -1.2697%, PF 0.8011
- latest conservative-positive subset only 4 rows, mean -22.5669%, PF 0.1381

Do not weaken q25 or launch a conditional-q25 rescue from this result.

### Policy-aligned calibration

`EXP-2026-09-29-POLICY-CAL-01`, Action `36643183157`: **ADOPT STRUCTURAL ALIGNMENT / NO PERFORMANCE CHANGE / NOT PROMOTION EVIDENCE**.
Reference and challenger selected the same 278 compact decision-date/symbol records and produced identical compact portfolio/cost-stress results.

### Corrected 60-case CPCV

Action `36637351334`: **CPCV_DOES_NOT_ESTABLISH_ROBUST_EDGE**.
- H5 median PF 0.381; positive NetEV 43.3%; positive date-cluster LCB 11.7%.
- H10 median PF 0.745; positive NetEV 50.0%; positive date-cluster LCB 33.3%.

Older 15-combination CPCV and conflicting old-chat recollections are superseded.

### Other frozen dispositions

- Rolling-160 recency challenger: rejected; do not sweep nearby windows.
- CA-safe path feature family: rejected; do not retune path definitions/subsets.
- H10 anchored challenger: `REJECTED_CURRENT_CANDIDATE_DO_NOT_RETUNE` despite strong old point estimates because evidence is old-regime concentrated, recent admissions are zero and corrected CPCV does not establish stability.
- H20: out of scope/archive.
- Stop price-only threshold/feature mining; the next information family must be genuinely independent and PIT-valid.

## Data-integrity state

Current research uses:
- KRX base-price-adjusted CA-safe daily returns for features/labels;
- CA-safe economic price index for MTM;
- fingerprinted fail-closed supervised caches;
- exact-date KOSPI statutory sell tax + separate round-trip commission;
- post-rank preliminary normal-market fail-closed veto; blocked slots remain empty.

The >30.5% decision-day CA-safe return rule is a **market-state fail-closed proxy, not alpha**, and remains preliminary until official historical security/status evidence covers the Judge period.

## KRX source gates A-F — frozen and machine-audited

Canonical gates:
- A `AUTHORIZED_OFFICIAL_ROUTE`
- B `EXACT_DATASET_SCHEMA_MAPPING`
- C `HISTORICAL_COVERAGE_SECURITY_MAPPING`
- D `PIT_AVAILABILITY_LINEAGE`
- E `REPRODUCIBLE_INTEGRITY_FAIL_CLOSED`
- F `INTENDED_USE_RIGHTS`

Only `PASS` closes a gate; `PARTIAL` is not a pass. All six passing closes only the source contract for the declared scope. It does not authorize Alpha/Final-Judge promotion, sealed holdout or live trading.

Canonical source/readiness files now include:
- `INDEXALERT_KRX_SOURCE_ACCESS_CONTRACT.md`
- `INDEXALERT_KRX_SOURCE_GATE_AUDIT.md`
- `research_v1_krx_source_gates.py`
- `research_v1_krx_public_evidence.py`
- `research_v1_krx_status_source_probe.py`
- `research_v1_krx_investor_flow_probe.py`
- `research_v1_krx_investor_flow_lineage.py`
- `research_v1_krx_investor_flow_coverage.py`
- `research_v1_krx_status_coverage.py`
- corresponding fail-closed tests in CI.

### Public contract evidence

Machine-readable official-public evidence is frozen as version `2026-10-01.v1`, fingerprint:

`349d310647c78412e45ac13078259bab2d002958db597b2f7dd26228f8b3ca7b`

Current public audit confirms:
- OpenAPI authentication-key approval and separate per-service utilization approval are distinct requirements;
- the public service list targets 2010+ data generally and separately lists KOSPI/KOSDAQ/KONEX stock basic-information APIs;
- the June 2026 “KRX Open API 미제공 데이터에 대한 안내” notice exists, but its specific dataset list was not reliably retrieved, so no required dataset is inferred available/unavailable from it;
- MDCSTAT237/238/239 public screen semantics support cleanup/delisting/delisted-price schema evidence;
- final day-D investor results are supplied after 20:00;
- current Korean OpenAPI terms effective 2025-12-26 are non-commercial, prohibit charging third parties for API results/providing KRX-received information to third parties, impose up to 10,000 calls/day/key and contain attribution/contract-end restrictions.

These facts improve Gate B/F evidence but do not close A/C/D/E.

### Authenticated-source reality

Direct Actions-log audit established that `KRX_ID`, `KRX_PW` and `KRX_OPENAPI_AUTH_KEY` are not configured in the current source-probe runtime. Therefore green source-probe workflows are diagnostics only and have not made authenticated KRX requests.

Latest public-evidence-bound probes:

**Status Action `36809182681`**
- success as diagnostic
- `authenticated_request_attempted=false`
- A `BLOCKED`, B `PARTIAL`, C `BLOCKED`, D `BLOCKED`, E/F `PARTIAL`
- source contract open; `judge_security_status_ready=false`
- public evidence version `2026-10-01.v1`, fingerprint `349d310647c78412e45ac13078259bab2d002958db597b2f7dd26228f8b3ca7b`
- probe contract fp `b91b5ee6b2b64e11910dddcd6f0400c884d2add3cd12530771eb5fb824160eec`
- result fp `65056341c19d0d70c7a8ae5e5bde3310cc54cfcc1eb2e4ed33645eb5152106e0`
- artifact `11139071717`

**Investor-flow Action `36809196068`**
- success as diagnostic
- `authenticated_request_attempted=false`
- A `BLOCKED`, B `PARTIAL`, C `BLOCKED`, D/E/F `PARTIAL`
- source contract open; `feature_performance_testing_authorized=false`
- public evidence version/fingerprint same as above
- probe contract fp `28c9d28aab34d8ec8e55258dbc95d389c2096eaf687c635a8e6c1b8f76179291`
- result fp `a227f4dcb34653cf89a9a6f462c01eabb45613c8c57212efa2e621039c53e097`
- artifact `11138816495`

## KRX Gate C/D internal validation readiness — 2026-10-01

The missing external data cannot be fabricated, but the internal validators required to audit it are now implemented and CI-tested.

### Investor-flow PIT lineage — Gate D infrastructure

`research_v1_krx_investor_flow_lineage.py` enforces:
- timezone-aware timestamps only;
- `event_time <= published_at <= available_at <= ingested_at`;
- final day-D publication not before 20:00 Asia/Seoul;
- current public-contract evidence fingerprint;
- one source-contract fingerprint per validated historical dataset;
- decision-time eligibility only when `decision_time >= available_at`.

Structurally valid lineage still returns `feature_performance_testing_authorized=false` and `sealed_holdout_authorized=false`. Integrity Action `36809680268` passed.

### Investor-flow historical coverage — Gate C infrastructure

`research_v1_krx_investor_flow_coverage.py` requires an independently attested expected `(event_date, symbol, isu_cd)` scope and exact observed key coverage. It never generates trading dates/universe or treats missing rows as zero. Missing, extra, duplicate or mapping-conflict keys keep coverage incomplete. Integrity Action `36809948775` passed.

### Security/status common-stock coverage — Gate C infrastructure

`research_v1_krx_status_coverage.py` requires an independently attested expected `(snapshot_date, symbol, isu_cd)` scope. Current normalized identity evidence without an official stable full issue identifier cannot close Gate C. Even exact identity coverage cannot set `judge_security_status_ready=true` by itself.

Initial Action `36810205800` exposed an empty-common-stock DataFrame schema bug (1 failed / 65 passed). The policy/protocol was unchanged; the implementation was corrected to preserve an empty key schema. Action `36810309522` then passed the same protocol.

### Current meaning

Internal audit machinery is ready; **actual evidence is not**. No real full historical KRX status/investor-flow dataset has yet passed these validators. Gate statuses therefore remain unchanged and no investor-flow performance backtest is authorized.

## Execution evidence state

Execution evidence tiers remain frozen:
1. `PROSPECTIVE_SHADOW_DECISION_LOG` — prospective decisions only, no broker fills.
2. `PROSPECTIVE_PAPER_EXECUTION_LOG` — paper/simulation broker plumbing/reconciliation evidence, not real-market fill quality.
3. `PROSPECTIVE_LIVE_EXECUTION_LOG` — real-account observations; only this tier can contribute empirical live fill/slippage/partial-fill/latency/markout/capacity evidence.

Research execution-evidence CI passed at Action `36668905306`. Server full tests passed at `36669071810`; corrected PAPER/LIVE semantics are deployed to Railway production commit `65855916afd52d081453bc511b6b82df3ec948b1`, deployment `34e76729-ff9b-4fa5-8334-b8b591a336ba`. This is operational evidence only and does not authorize trading.

## Next independent information family

First candidate remains **official KRX investor-flow data**, but no performance experiment may run until the applicable source contract is closed with real evidence:
- approved exact route/product;
- historical coverage + stable security mapping;
- real `event_time`, `published_at`, `available_at`, `ingested_at` lineage;
- reproducible fail-closed acquisition;
- intended-use rights.

Same-day undocumented proxy substitution is forbidden.

## Final Judge blockers still open

1. **External data/auth:** approved exact KRX historical route/product; current audited CI has no KRX credentials and Gate A is blocked.
2. **Security/status evidence:** full common-stock/security-status history with stable issue mapping and PIT lineage; exact halt/cleanup/delisting economics joins.
3. **Investor-flow evidence:** full official historical data passing the new Gate C/D validators; performance testing remains blocked.
4. **Execution evidence:** empirical fill ratio, fill time/price, partial fills, post-fill markout, latency/expiry and real capacity.
5. **Research governance:** full multiple-testing/ledger discipline continues; no rejected-candidate revival.
6. **One-shot sealed holdout:** untouched until source/execution/code/protocol blockers are frozen, then Shadow S1 -> Fresh Confirmation S2.
7. **Physical notification E2E:** separate operational gate remains pending from the current Android build.
8. **Live ordering:** disabled; broker automation remains downstream of Alpha/source/execution promotion and explicit user activation.

## Promotion rule

Positive mean, PF or CAGR alone cannot promote a candidate. At minimum, evidence must show positive cost-adjusted OOS economics, PF > 1, positive date-cluster lower bound, robustness to best-day removal, credible recent evidence, acceptable MDD/ES/tail dependence, cost-stress survival, PIT correctness, official source/status integrity and execution realism. Final promotion additionally requires the one-shot sealed holdout and prospective confirmation sequence.
