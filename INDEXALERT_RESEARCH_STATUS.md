# IndexAlert Research Status

Updated: 2026-10-01 KST  
Branch: `index-alert-research-v1`  
Master authority: `INDEXALERT_MASTER_SPEC.md`  
Experiment authority: `INDEXALERT_RESEARCH_LEDGER.md`  
Promotion authority: **none yet**.

## Current bottom line

The current price/volume/context stack is **not ready for live short-term investment recommendations**. The process has strict PIT discipline, CA-safe returns, frozen Top3/no-backfill, realistic costs, abstention, anchored purged walk-forward, corrected CPCV and reproducible CI, but the evidence still does not establish a robust, recent, execution-ready edge.

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

Older 15-combination CPCV and conflicting old-chat recollections are superseded.

Other dispositions remain frozen: Rolling-160 rejected; CA-safe path family rejected; H10 current candidate rejected/do-not-retune; H20 archive only. Stop price-only threshold/feature mining.

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

## KRX authorization and runtime-consent reality

`research_v1_krx_auth_preflight.py` freezes **credentials are not authorization, and authorization metadata is not runtime consent**.

For the current Data Marketplace probe path, one tiny authenticated request requires all of:
- `KRX_ID` secret;
- `KRX_PW` secret;
- non-secret `KRX_AUTH_EVIDENCE_REF` identifying the approval basis;
- exact per-run sentinel `KRX_EXPLICIT_PROBE_CONSENT=ALLOW_TINY_AUTHENTICATED_REQUEST`.

Generic values such as `true`, `1` or `yes` are rejected. OpenAPI `KRX_OPENAPI_AUTH_KEY` is a separate route and additionally requires exact approved service mapping; it cannot substitute for Data Marketplace credentials.

Workflow defense-in-depth is also frozen:
- push runs are dry-run only;
- push dry-run steps receive empty KRX credential/reference/consent environment values;
- authenticated steps are skipped on push;
- authenticated tiny probes are eligible only on explicit `workflow_dispatch` with `allow_authenticated_request=true`;
- the Data Marketplace probe workflow does not inject `KRX_OPENAPI_AUTH_KEY` into the authenticated step.

Latest workflow evidence:
- **Status `36813950791`** — success; push-safe dry-run step success; explicitly consented authenticated step skipped.
- **Investor `36813973236`** — success; push-safe dry-run step success; explicitly consented authenticated step skipped.
- **Integrity `36814088731`** — full KRX fail-closed suite including exact consent-sentinel tests and Source Access Contract drift checks: success.

No authenticated KRX request has yet been demonstrated; Gate A therefore remains BLOCKED.

## KRX internal source-evidence pipeline — implemented

Canonical files include:
- `INDEXALERT_KRX_SOURCE_ACCESS_CONTRACT.md`
- `INDEXALERT_KRX_SOURCE_GATE_AUDIT.md`
- `research_v1_krx_source_gates.py`
- `research_v1_krx_public_evidence.py`
- `research_v1_krx_auth_preflight.py`
- `research_v1_krx_status_source_probe.py`
- `research_v1_krx_investor_flow_probe.py`
- `research_v1_krx_investor_flow_lineage.py`
- `research_v1_krx_investor_flow_coverage.py`
- `research_v1_krx_status_coverage.py`
- `research_v1_krx_status_event_integrity.py`
- `research_v1_krx_acquisition_receipt.py`
- `research_v1_krx_acquisition_batch.py`
- `research_v1_krx_source_data_admission.py`
- corresponding fail-closed tests in CI.

Frozen future flow:
`explicit manual request consent -> authorization preflight -> authenticated acquisition -> immutable receipt -> consistent batch -> PIT lineage -> exact expected-scope coverage -> A-F audit -> source-data admission -> separate experiment-registry/preregistration review`.

Key properties:
- investor lineage requires timezone-aware `event_time <= published_at <= available_at <= ingested_at`, final day-D publication >=20:00 KST and decision-time eligibility only after availability;
- investor/status coverage compares only independently attested expected keys and never invents calendar/universe/implicit zero rows;
- status-event integrity rejects impossible cleanup/delisting/delisted-price chronology and never invents fill/recovery returns;
- acquisition receipts bind request/schema/content/route/dataset/client/approval/public-contract fingerprints without storing credential values;
- batch provenance rejects tampered/duplicate receipts and silent route/dataset/use-scope/approval/client/schema drift;
- source-data admission requires closed A-F + valid batch + current public evidence + valid PIT + exact coverage + matching family/use scope.

Even if source-data admission becomes structurally true, it sets only `eligible_for_experiment_registry_review=true`; it deliberately keeps performance testing, sealed holdout, promotion and live-trading authority false. A separate Ledger/preregistration decision is mandatory.

Latest integrity milestones include:
- `36811118588` status-event integrity — success;
- `36811648510` acquisition receipt — success;
- `36812299630` acquisition batch — success;
- `36812655201` source-data admission — success;
- `36813918295` explicit-consent probe code/unit tests — success;
- `36814088731` explicit-consent Source Access Contract + full KRX integrity suite — success.

## External source evidence still missing

Internal code cannot fabricate:
1. approved exact KRX historical route/product;
2. route-specific credentials plus real non-secret authorization-evidence reference;
3. one explicitly consented tiny authenticated probe proving the approved route without exposing credentials;
4. complete historical status/investor-flow data;
5. independently attested expected scope and stable issue mapping;
6. real record-level PIT publication/availability timestamps;
7. exact intended-use rights for the selected route;
8. exact halt/cleanup/delisting execution/recovery economics.

Until real data passes the pipeline, no investor-flow performance experiment is authorized and Final Judge status remains incomplete.

## Execution evidence state

Evidence tiers remain frozen:
1. `PROSPECTIVE_SHADOW_DECISION_LOG` — decisions only, no broker fills.
2. `PROSPECTIVE_PAPER_EXECUTION_LOG` — paper/simulation plumbing evidence, not real fill quality.
3. `PROSPECTIVE_LIVE_EXECUTION_LOG` — real-account executions; only tier eligible for empirical live fill/slippage/partial-fill/latency/markout/capacity evidence.

Research execution-evidence Action `36668905306` passed. Server tests `36669071810` passed. Railway production runs server commit `65855916afd52d081453bc511b6b82df3ec948b1`; deployment `34e76729-ff9b-4fa5-8334-b8b591a336ba` succeeded with `/health` 200. This is operational evidence only and does not authorize trading.

## Remaining blockers

1. **KRX authorization/data:** approved route/product, credentials/reference, explicit manual probe and real history remain external requirements.
2. **Security/status economics:** full stable identity/status history and exact halt/cleanup/delisting economic joins.
3. **Investor flow:** full real official history passing provenance, PIT, coverage, A-F and source-data admission, then separate preregistration before any performance test.
4. **Execution:** empirical fill ratio/time/price, partial fills, markouts, latency/expiry and real capacity.
5. **Research governance:** no rejected-candidate revival; maintain Ledger/multiple-testing discipline.
6. **One-shot sealed holdout:** untouched until source/execution/code/protocol freeze; then Shadow S1 -> Fresh Confirmation S2.
7. **Physical notification E2E:** one current-build Android receipt still required.
8. **Live ordering:** disabled until frozen promotion/safety gates and explicit user activation are satisfied.

## Promotion rule

Positive mean, PF or CAGR alone cannot promote a candidate. Promotion requires cost-adjusted OOS economics, PF > 1, positive date-cluster lower bound, best-day robustness, credible recent evidence, acceptable MDD/ES/tails, cost-stress survival, PIT correctness, official source/status integrity and execution realism. Final promotion additionally requires the one-shot sealed holdout and prospective confirmation sequence.
