# IndexAlert Research Status

Updated: 2026-10-01 KST  
Branch: `index-alert-research-v1`  
Master authority: `INDEXALERT_MASTER_SPEC.md`  
Experiment authority: `INDEXALERT_RESEARCH_LEDGER.md`  
Promotion authority: **none yet** — development evidence cannot promote a live strategy without sealed holdout + prospective Shadow.

## Current bottom line

The current price/volume/context stack is **not ready for live short-term investment recommendations**.

The research process is materially stronger than earlier versions — PIT discipline, corporate-action-safe returns, strict Top3/no-backfill, realistic costs, abstention, purged validation and reproducible CI are in place — but the current evidence does not establish a robust, recent, execution-ready edge.

Do **not** relax q25, TopK, costs, recent-evidence requirements, horizon or execution assumptions merely to create trades.

## Frozen policy / validation rules

- H5 is the Core development horizon.
- H10 is `REJECTED_CURRENT_CANDIDATE_DO_NOT_RETUNE`; do not sweep H6-H9 or retune H10 from completed outcomes.
- H20 is out-of-scope/archive evidence.
- Anchored walk-forward: train 504 / calibration 126 / test 126.
- Horizon-matched label-overlap purge and embargo.
- Original decision-time Top3 is frozen; vetoed/held/unfillable slots remain empty; **no rank-4+ backfill**.
- 0..3 trades and NO_TRADE are valid.
- Corporate-action-safe KRX base-price returns are mandatory.
- Primary evidence is executable, cost-adjusted NetReturn/NetEV with PF, date-cluster uncertainty, tail risk, drawdown, cost stress and execution/capacity realism.
- Sealed holdout is one-shot and stays sealed until data/execution blockers, code and protocol are frozen.
- After holdout: prospective Shadow S1 -> frozen Fresh Confirmation S2.

## Current H5 developmental reference

Selection-conditioned residual calibration with the preliminary post-rank normal-market fail-closed overlay remains a developmental reference, not a Champion.

Compact result:
- 278 executed entries / 137 trade days
- mean NetReturn **+1.150%**
- PF **1.546**
- cluster 95% lower bound remains below zero
- 2x-cost mean **+0.787%**, PF **1.344**
- portfolio total **+16.39%**
- CAGR **~1.83%**
- MDD **-24.39%**
- Sharpe **~0.23**
- average gross exposure **~5.20%**

Failure modes:
- positive admissions are concentrated in **2018-2021**
- no admissions in 2022-2026 / latest 504 OOS sessions
- remove-best-5 decision days turns mean NetReturn negative and PF below 1
- official historical security/status and execution/capacity blockers remain open

Classification: **DEVELOPMENTAL_NOT_CURRENTLY_PROMOTABLE**.

## Recent-gate and uncertainty audit

The recent gate diagnostic showed that q25 uncertainty width mechanically blocks almost all recent raw-positive Top3 rows. The preregistered realized-outcome audit then tested whether those blocked rows were actually valuable.

`EXP-2026-09-29-UNCERTAINTY-AUDIT-01`, Action `36637333875`: **COMPLETED**.

Key realized results:
- all-OOS q25-blocked: mean **-0.8432%**, PF **0.8425**, cluster 95% interval **[-1.4094%, -0.2782%]**
- 2022+ q25-blocked: mean **-1.2551%**, PF **0.8005**
- latest-504 q25-blocked: mean **-0.6263%**, PF **0.9012**; remove-best-5 **-1.2697%**, PF **0.8011**
- latest conservative-positive subset: only 4 rows, mean **-22.5669%**, PF **0.1381**

Decision: **KEEP_ABSTENTION**. The blocked pool is economically weak, so do not weaken q25 and do not launch a conditional-q25 rescue experiment from this result. Seek orthogonal PIT-valid information.

The audit artifact also reports `common_stock_identity_validated=false` and `judge_eligible=false`; official common-stock identity and exact halt/delisting economics remain hard blockers.

## Policy-aligned calibration

`EXP-2026-09-29-POLICY-CAL-01`, Action `36643183157`: **COMPLETED**.

The only change was to apply the same preliminary normal-market veto to calibration-day frozen Top3 before estimating residual q25/q50/q75, with no backfill and no change to model, features, q-level, windows, costs or admission threshold.

Result:
- reference and challenger selected the **same 278 compact decision-date/symbol records**
- direct comparison found 0 reference-only and 0 challenger-only records
- compact portfolio and cost-stress results are exactly identical
- selected CSV differences are only in the `model` identifier

Disposition: **ADOPT STRUCTURAL ALIGNMENT / NO PERFORMANCE CHANGE / NOT PROMOTION EVIDENCE**. This aligns calibration population with the decision policy without manufacturing performance. The underlying normal-market proxy is still preliminary pending official historical KRX status validation.

## Corrected Purged CPCV — authoritative result

Action `36637351334`: **COMPLETED SUCCESSFULLY**.

Frozen protocol: six contiguous groups; every pair of test groups; each remaining group once as calibration; remaining three groups train; horizon-matched purge/embargo; **60 cases per horizon**. CPCV is a secondary stability diagnostic only.

Authoritative results:
- **H5:** median PF **0.381**; positive NetEV cases **43.3%**; date-cluster LCB > 0 **11.7%**
- **H10:** median PF **0.745**; positive NetEV cases **50.0%**; date-cluster LCB > 0 **33.3%**

Verdict: **CPCV_DOES_NOT_ESTABLISH_ROBUST_EDGE** for either horizon.

The former H10 **15-combination** CPCV section and its numbers are **historical and superseded**. Conflicting old-chat recollections, including H10 median PF ~0.454, are not valid evidence. Earlier exit-137/143 failures were implementation memory/process failures; splitwise generate -> evaluate -> release fixed execution without changing the frozen protocol.

## Other completed negative evidence

### Rolling-160 recency challenger
- 85 trades
- mean -1.583%, PF 0.447
- cluster 95% interval -4.18% to -0.15%
- portfolio -17.64%, MDD -20.53%

Disposition: rejected; do not sweep nearby windows.

### CA-safe path family — Action `36549690847`
- 88 trades
- mean NetReturn +0.330%, PF 1.082
- cluster LCB -3.959%
- ES95 -26.41%
- portfolio -4.40%, MDD -20.44%
- latest-504 admissions 0
- remove-best-5 -2.668%, PF 0.449

Disposition: rejected; do not retune price-path definitions/subsets from this outcome.

## H10 / H20

### H10
Anchored developmental result was strong by point estimate (122 records / 58 days; mean +5.689%, PF 4.49, cluster LCB +1.752%, MDD -5.86%), but admissions occurred only in 2018-2021, recent admissions were zero, stability did not survive corrected CPCV, and hard blockers remain open.

Disposition: **REJECTED_CURRENT_CANDIDATE_DO_NOT_RETUNE**.

### H20
Out of the requested 5-10-session scope. Archive only; it cannot select a production horizon or motivate nearby-horizon tuning.

## Data-integrity state

Current research uses:
- KRX base-price-adjusted CA-safe daily returns for features and labels
- CA-safe economic price index for MTM
- fingerprinted fail-closed supervised caches
- exact-date KOSPI statutory sell tax + separate round-trip commission
- post-rank preliminary normal-market fail-closed veto; blocked slots remain empty

The >30.5% decision-day CA-safe return rule is a **market-state fail-closed proxy**, not alpha. It remains preliminary until historical official security/status data covers the Judge period.

## KRX source gates A-F — frozen 2026-10-01

The interrupted source-governance task is now complete in code and canonical documentation.

Canonical gates:
- Gate A — `AUTHORIZED_OFFICIAL_ROUTE`
- Gate B — `EXACT_DATASET_SCHEMA_MAPPING`
- Gate C — `HISTORICAL_COVERAGE_SECURITY_MAPPING`
- Gate D — `PIT_AVAILABILITY_LINEAGE`
- Gate E — `REPRODUCIBLE_INTEGRITY_FAIL_CLOSED`
- Gate F — `INTENDED_USE_RIGHTS`

Only `PASS` closes a gate; `PARTIAL` is not a pass. All six passing closes only the source contract for the declared scope and cannot by itself authorize Alpha/Final-Judge promotion, sealed-holdout consumption or live trading.

Canonical files:
- `INDEXALERT_KRX_SOURCE_ACCESS_CONTRACT.md`
- `INDEXALERT_KRX_SOURCE_GATE_AUDIT.md`
- `research_v1_krx_source_gates.py`
- `test_research_v1_krx_source_gates.py`

Master Spec section 16 freezes the same boundary. CI is configured to fail if the Master Spec, source contract or audit document drifts from the canonical A-F names or removes the non-promotion boundary.

Latest validating Action: `36807509480` on commit `9c1acf1a42f23b2b6eec6bfe19c38fa6e3296eb7` — **SUCCESS**.

Current audit remains fail-closed rather than declaring premature readiness:
- KRX security/status source contract: **OPEN**; Gates C/D remain `BLOCKED`, other source/licensing gates remain `PARTIAL` pending exact closure evidence.
- KRX investor-flow source contract: **OPEN**; Gate C remains `BLOCKED`, other gates remain `PARTIAL` pending exact historical access/mapping/PIT/licensing evidence.

Therefore no investor-flow performance experiment is authorized yet, and `judge_security_status_ready` remains false.

## Next independent information family

Do **not** continue price-only threshold/feature mining.

First candidate: **official KRX investor-flow data**. Before any performance test, establish an official reproducible historical source with:
- historical coverage and stable security mapping
- `event_time`
- `published_at`
- `available_at`
- `ingested_at`
- fail-closed handling when data is unavailable

Final day-D investor trading results are only eligible for a later decision after their publication time. Authentication/source-probe success alone is not feature evidence. Do not substitute undocumented same-day proxies if official reproducible history cannot be established.

## Final Judge blockers still open

1. Close KRX source Gates A-F for the exact security/status source used by Final Judge; specifically obtain and audit full historical common-stock/security-status coverage and PIT lineage.
2. Exact trading-halt, cleanup-trading and delisting economics/status joins.
3. Close KRX source Gates A-F for an official reproducible investor-flow historical route before any performance test.
4. Empirical fill ratio, fill time, fill price and partial-fill behavior.
5. Post-fill markout, recommendation latency/expiry and execution-delay stress.
6. Empirical capacity rather than only a square-root impact cost proxy.
7. Research-ledger/multiple-testing discipline across the full policy search.
8. One-shot sealed holdout only after blockers/code/protocol freeze, then Shadow S1 -> Fresh Confirmation S2.

## Promotion rule

Positive mean, PF or CAGR alone cannot promote a candidate. At minimum, evidence must show positive cost-adjusted OOS economics, PF > 1, positive date-cluster lower bound, robustness to best-day removal, credible recent evidence, acceptable MDD/ES/tail dependence, cost-stress survival, PIT correctness, official status integrity and execution realism. Final promotion additionally requires the sealed holdout and prospective confirmation sequence.
