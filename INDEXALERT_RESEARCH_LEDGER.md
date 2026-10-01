# IndexAlert Research Ledger

Purpose: prevent research-memory bias and repeated policy mining. This ledger records material experiments, their fixed question, outcome and disposition. It is not a performance marketing document.

Updated: 2026-10-02 KST

## Governance

- Production promotion is impossible from development results alone.
- Primary economics: executable, cost-adjusted OOS NetReturn / NetEV.
- Freeze original decision-time Top3; blocked/held/vetoed slots stay empty; no rank-4+ backfill.
- 0..3 and NO_TRADE are valid.
- Five-session purge around outcome boundaries for the H5 target; horizon-matched purge/embargo for other frozen horizons.
- Corporate-action-safe KRX base-price returns are mandatory for feature/label/MTM research.
- Candidate changes must be identified before reading the candidate's test outcome. Do not relax q25, TopK, costs, recent-evidence requirements or execution assumptions to manufacture trades.
- Keep negative experiments in the ledger.
- A development candidate can only justify further falsification. Sealed holdout + prospective Shadow are required for actual promotion.
- H5 is the Core development horizon. H10 is `REJECTED_CURRENT_CANDIDATE_DO_NOT_RETUNE`; do not sweep H6-H9 or retune H10 from completed outcomes. H20 is out of scope/archive evidence.

## Material completed experiments

### Legacy simple momentum / probability baselines
Status: **REJECTED as current champion**.

After realistic costs and corrected execution accounting, simple momentum/probability baselines did not establish positive robust OOS economic edge. Earlier optimistic outputs affected by execution-set mismatches or superseded data assumptions are not promotion evidence.

### Purge / embargo correction
Status: **ADOPTED as mandatory validation policy**.

Five-session targets require a five-session boundary purge. Pre-purge ML results are superseded for promotion purposes.

### Rolling 160-session recency training
Status: **REJECTED / DO NOT SWEEP NEARBY WINDOWS**.

Prespecified challenger: 85 trades, mean NetReturn -1.583%, PF 0.447, cluster 95% interval -4.18% to -0.15%, portfolio total -17.64%, MDD -20.53%.

### Corporate-action-safe return axis
Status: **ADOPTED as mandatory data policy**.

Raw close ratios can create false momentum, labels and MTM around splits/rights/capital actions. Current research uses KRX base-price-adjusted daily returns and fingerprinted fail-closed supervised caches. Raw-close promotion conclusions are superseded.

### Long-history marginal Distributional NetEV
Status: **REJECTED as robust edge**.

2015-06-15 onward CA-safe long-history testing falsified short-window optimism. Without a normal-market status layer, catastrophic non-standard-price observations dominated tail risk. With the preliminary fail-closed market-state overlay, point estimates improved but cluster lower bounds remained non-positive.

### Selection-conditioned residual calibration
Status: **KEEP AS DEVELOPMENTAL / NOT PROMOTABLE**.

Fixed change: estimate residual q25/q50/q75 from calibration-day Top3 by predicted mean while keeping model, quantile levels, Top3, costs and test threshold unchanged.

Strongest compact all-context developmental result after the preliminary normal-market fail-closed overlay:
- 278 executed entries / 137 trade days
- mean NetReturn +1.150%
- PF 1.546
- cluster 95% lower bound remains below zero
- 2x-cost mean +0.787%, PF 1.344
- portfolio total +16.39%, CAGR ~1.83%, MDD -24.39%, Sharpe ~0.23
- admissions concentrated in 2018-2021; none in 2022-2026 / latest 504 OOS sessions
- remove-best-1 day: +0.694%, PF 1.326
- remove-best-3: +0.053%, PF 1.025
- remove-best-5: -0.362%, PF 0.836

The normal-market >30.5% decision-day return veto was added after the selection-conditioned challenger was first developed. It is structurally justified as a fail-closed market-state rule but remains preliminary until official historical security/status lineage is validated. Its development-sample performance lift is not independent evidence.

### EXP-2026-09-29-CA-PATH-01 — CA-safe daily path feature family
Status: **REJECTED / DO NOT RETUNE**. Action `36549690847`.

Frozen protocol: 2015-06-15 onward; Ridge mean NetReturn; selection-conditioned q25/q50/q75; train 504 / calibration 126 / test 126 / purge 5; costs unchanged; `netev_low > 0`; original Top3 frozen; preliminary normal-market fail-closed overlay after rank freeze; no backfill.

Result:
- 88 trades
- mean gross +0.716%, cost 0.386%, NetReturn +0.330%
- PF 1.082
- date-cluster 95% LCB -3.959%
- ES95 -26.41%
- portfolio total -4.40%, CAGR -0.54%, MDD -20.44%
- latest 504 OOS admissions 0
- remove-best-1: -0.642%, PF 0.846
- remove-best-5: -2.668%, PF 0.449

Failed cluster-LCB, extreme-day-independence, current-evidence and portfolio-economics criteria. Do not tune alternate gap definitions, path thresholds or path subsets from this result.

### EXP-2026-09-29-RECENT-GATE-01 — recent-regime gate waterfall
Status: **COMPLETED DIAGNOSTIC / NO POLICY CHANGE**. Action `36555181788`.

Latest 504 OOS sessions, 2024-08-20 through 2026-09-16:
- original Top3 1,512
- raw `pred_mean > 0` 1,464
- raw-positive blocked by `netev_low <= 0`: 1,460
- conservative `netev_low > 0`: 4 rows on 3 dates
- all 4 removed by the preliminary non-standard-market veto
- final admissions 0
- mean Top3 `pred_mean` +1.410%
- mean calibration penalty -9.934%
- mean `netev_low` -8.523%

Diagnostic conclusion at that stage: uncertainty/calibration width was the dominant mechanical gate. This did **not** justify loosening q25; the preregistered realized-outcome audit below determined whether the blocked population actually had missed economic value.

### EXP-2026-09-29-UNCERTAINTY-AUDIT-01 — realized outcomes behind q25 veto
Status: **COMPLETED / KEEP_ABSTENTION / DO NOT TEST CONDITIONAL-q25 FROM THIS RESULT**. Action `36637333875`.

No model or policy change. Realized 5-session economics were audited for original Top3, raw-positive Top3, q25-blocked raw-positive Top3 and conservative-positive Top3 across all OOS / 2022+ / 2024+ / latest-504 windows.

Authoritative findings:
- all-OOS q25-blocked: mean **-0.8432%**, PF **0.8425**, date-cluster 95% interval **[-1.4094%, -0.2782%]**; remove-best-5 mean -1.0534%, PF 0.8036.
- 2022+ q25-blocked: mean **-1.2551%**, PF **0.8005**, cluster LCB -1.9933%.
- 2024+ q25-blocked: mean **-0.7182%**, PF **0.8822**; interval includes zero but remove-best-5 falls to -1.2039%, PF 0.8035.
- latest-504 q25-blocked: 1,460 rows / 1,374 realized, mean **-0.6263%**, PF **0.9012**, cluster interval **[-1.7606%, +0.5840%]**; remove-best-5 -1.2697%, PF 0.8011.
- latest conservative-positive set: only 4 rows, mean **-22.5669%**, PF **0.1381**.
- artifact states `common_stock_identity_validated=false`, `judge_eligible=false`; official common-stock identity and exact halt/delisting economics remain blockers.

Preregistered decision: the q25-blocked pool is economically weak rather than a clearly positive population hidden by over-wide uncertainty. **Keep abstention. Do not weaken q25 and do not launch a conditional-q25 rescue experiment from this audit. Seek orthogonal PIT-valid information instead.**

### EXP-2026-09-29-POLICY-CAL-01 — policy-aligned calibration population
Status: **COMPLETED / ADOPT STRUCTURAL ALIGNMENT / NO PERFORMANCE CHANGE / NOT PROMOTION EVIDENCE**. Action `36643183157`, artifact `11067383547`, SHA256 `c8dd6a016103cf33d9219622f416fda25715c1cac19b371714d9308f2cb2c26f`.

Prespecified only change:
1. freeze calibration-day Top3 by `pred_mean` exactly as before;
2. apply the same decision-time preliminary normal-market veto to those frozen calibration rows;
3. vetoed slots stay empty; no rank-4+ backfill;
4. estimate q25/q50/q75 residuals only from policy-eligible calibration Top3;
5. keep mean model, features, q-levels, train/cal/test windows, costs, test Top3 and `netev_low > 0` unchanged.

Result from the reproducible artifact:
- reference and challenger each selected the **same 278 compact decision-date/symbol records**; direct row-key comparison found 0 reference-only and 0 challenger-only records.
- compact portfolio results are exactly identical: total return +16.3863%, CAGR 1.8341%, MDD -24.3899%, Sharpe 0.2300, average gross exposure 5.2008%, 278 executed entries / 137 trade days.
- compact cost stress is identical: 1x mean +1.1501%, PF 1.5461; 1.5x +0.9687%, PF 1.4413; 2x +0.7873%, PF 1.3440.
- the exported selected CSVs differ only in the `model` identifier for the common selected rows; the selected decision-date/symbol/prediction/outcome set is unchanged.
- the challenger changes calibration eligibility as intended but does not manufacture additional realized performance.

Disposition: keep the population alignment as a **developmental structural-consistency correction**, not as new alpha or promotion evidence. The underlying normal-market proxy remains preliminary pending official historical KRX security/status validation.

### EXP-2026-09-29-SWING-H10 — 10-session Swing Challenger
Status: **REJECTED AS CURRENT CANDIDATE / DO NOT RETUNE**. Action `36568357047`.

Anchored developmental result: 122 records / 58 trade days; mean NetReturn +5.689%, PF 4.49, cluster 95% LCB +1.752%, MDD -5.86%, ES95/ES99 -10.44%/-12.77%, 2x-cost mean +5.325%.

Not current/general evidence: admissions only 2018-2021, recent admissions zero, best-day robustness insufficient under cluster uncertainty, official status/execution/capacity blockers open, and no sealed holdout/Shadow. Do not search H6-H9, loosen q25, alter costs or retune H10.

### EXP-2026-09-29-SWING-H20 — 20-session exploratory run
Status: **OUT OF SCOPE / ARCHIVED**.

H20 is outside the requested 5-10-session challenger range. It cannot select a production horizon or motivate nearby-horizon tuning.

### Corrected 60-case Purged CPCV — H5/H10 stability diagnostic
Status: **COMPLETED / DOES NOT ESTABLISH ROBUST EDGE**. Action `36637351334`.

Frozen protocol: six contiguous groups; every pair of test groups; each remaining group serves once as calibration; remaining three groups train; horizon-matched label-overlap purge + embargo; **60 cases per horizon**. CPCV is a stability diagnostic only; repeated test rows are not independent and CPCV cannot replace anchored walk-forward, sealed holdout or Shadow.

Authoritative reproducible results:
- **H5:** median PF **0.381**; fraction positive NetEV **43.3%**; fraction date-cluster LCB > 0 **11.7%**.
- **H10:** median PF **0.745**; fraction positive NetEV **50.0%**; fraction date-cluster LCB > 0 **33.3%**.

The older 15-combination H10 CPCV result is historical/superseded. Conflicting old-chat recollections, including an H10 median PF near 0.454, are invalid for decisions; the completed 60-case artifact is authoritative.

Earlier exit-137/143 CPCV failures were engineering memory/process failures caused by accumulating prediction DataFrames. Splitwise generate -> evaluate -> release fixed execution without changing the statistical protocol.

### Execution-sufficiency project protocol v1 — preregistration freeze
Status: **FROZEN BEFORE GENUINE LIVE / EVALUATOR IMPLEMENTED / NOT PROMOTION EVIDENCE**. Action `36881327868`.

The project criteria are frozen in `INDEXALERT_EXECUTION_SUFFICIENCY_PROTOCOL.md` and SHA-256-bound `.json` before any genuine LIVE execution evidence is used. The independent evaluator accepts only the real-account `PROSPECTIVE_LIVE_EXECUTION_LOG` tier with frozen decision/execution policy identity and PIT provenance.

Minimum scope is 600 LIVE observations across at least 200 distinct decision dates and at least 400 fills; empirical capacity is bounded to the existing `0.0005` decision-time ADV participation assumption with at least 120 near-capacity observations. Prespecified non-compensating gates cover fill quality, Wilson no-fill/partial-fill bounds, slippage versus the pre-order budget, fee/tax excess, TTL/expiry latency, complete 5m/30m/close markouts with ES95/ES99, near-capacity behavior, and zero unknown/reconciliation/capacity/risk-integrity breaches.

Disposition: no genuine LIVE evidence window exists yet, so the empirical execution blocker remains open and unassessed. Synthetic/unit-test rows cannot close it. The numerical evaluator now reports metric success separately as `execution_metric_gates_passed`; a source label or hash-bound CSV cannot set project readiness or close the blocker without independent broker-native provenance admission under `INDEXALERT_LIVE_EXECUTION_PROVENANCE_CONTRACT.md`. Even a later fully admitted execution-evidence pass cannot by itself authorize the sealed holdout, model promotion or live trading.

## Next independent information family

Do **not** continue price-only feature/threshold mining. The next research family must be genuinely independent and PIT-valid.

First candidate: **official KRX investor-flow data**. Final day-D investor trading results are published after the trading session, so day-D final flow may only be used at the next eligible decision after publication. Before any performance test, establish:
- official reproducible source/access;
- historical coverage;
- security mapping;
- `event_time`, `published_at`, `available_at`, `ingested_at` lineage;
- fail-closed behavior when publication/access is unavailable.

A source/auth probe alone is not feature-promotion evidence. If reproducible official history cannot be obtained, do not substitute an undocumented same-day proxy merely to run a backtest.

## Open Final Judge blockers / next work

1. Obtain and validate real official historical KRX common-stock/security-status raw data with PIT availability lineage.
2. Model exact halt, cleanup-trading and delisting economics/status rather than proxy inference.
3. Establish official reproducible KRX investor-flow historical access/lineage before any performance test.
4. Collect genuine LIVE execution evidence against the already-frozen project v1 protocol, retain broker-native order/execution provenance for row-level independent admission, then run the frozen metric assessment: fill ratio, fill time/price, partial/no fills, post-fill markout, latency/expiry, fees/tax, reconciliation and capacity.
5. Do **not** burn the sealed holdout while external KRX/status-economics and empirical execution blockers remain open; the execution protocol itself is now frozen.
6. After a valid holdout, require prospective Shadow S1 then frozen Fresh Confirmation S2.
