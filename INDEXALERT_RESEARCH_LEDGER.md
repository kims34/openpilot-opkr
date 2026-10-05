# IndexAlert Research Ledger

## Current authoritative correction — 2026-10-05T19:56:04.948Z

**CONSUMED_FAILED_INVALID_V1_HOLDOUT — NO PROMOTION OR REUSE AUTHORITY.** This supersedes older “untouched/unopened” statements below. It records existing evidence; no private outcome was opened or reevaluated for this synchronization.

Development record: `index-alert-position-regen-fix-v1@ced2f2190ee70f4ba853d21aaabbd365b7912747`, last implementation `ed3e0f2cbb2a30830aed452e01c7426545dfad05`. Failed result was already created at **2026-10-05T08:05:25.795261Z**, passed=false, frozen cutoff **2026-09-25**, consumed window **2026-09-28..2026-10-01**. The original evaluator had future-label leakage and ignored the rolling1260 requirement; this is invalid independent promotion evidence, not a passing candidate.

Preserve these SHA-256 identities and the historical manifest/result discrepancy:
- Result: `30c15bb283e4de6e048d33c06734b86ab29a36c342536942e768c6b4d45f5a82`.
- Manifest: `ff5e60c816c6e45b0c9aee100af4e884385b14cc5cf602b16919f27560769907`.
- Receipt: `3f0b86dcd9bdbabc6a14021b7f7a895f9a321aa53d3fc4ad23dd614a29a81a63`.
- Manifest outcomes_unsealed=false despite the existing failed result is retained as historical discrepancy, not corrected by rewriting private artifacts.

**Do not delete/reset/reseal/rerun/relabel/retune or use a new window to rescue v1.** Retirement merge `03140e9f9c5327bb79b1b0621dafa6e6908ca700`, repair `b1d5bb3bfd8f15ee74076a8e67b84d8fb7d1c3dc`; nine synthetic boundary tests and Actions37292632806/37292636269 passed. These are engineering boundary evidence only. No independent successor or promotion authority has been admitted.

Actual PIT service225f2279-d728-4e1a-a3f3-2447ff0f9dc1 is pinned at `26f56e63c3f30a6f8e02695ce9a4eb7b4ac3fe15`, completed deployment7021473a-d9a6-4711-b496-a359fd9bb0c8, read-only retired-validation audit, restartNEVER, /pit5000MB volume03f389e5-5030-46a9-bfa5-dd8aa3dc24fa. Its prior safe audit reported three matching frozen hashes and four stages blocked, without opening outcomes or authorizing model evaluation. Do not restart the retired evaluator.

All Master Spec criteria remain frozen: PIT/label/CA returns, H5 504/126/126, rolling1260, horizon purge/embargo,60-case CPCV,Top3/no-backfill,0..3/NO_TRADE,q25,cost/slippage/partial-fill,NetEV/Precision@Selected/PF/MDD/ES95/99/recent evidence and promotion/rejection rules. H10 remains rejected/no-retune; H20 archive. Final execution requires600 genuine LIVE observations/200 distinct decision dates/400fills/120near-capacity fills >=80% frozen cap ADV0.0005 plus every existing noncompensating gate. No loosening or current live-order authority. Any future independent successor must be preregistered and admitted through existing contracts before its own untouched holdout; this consumed v1 window is unavailable.

Current independent engineering evidence: dev PR31-34,231 offline tests; PR33 integrated synthetic capital fault replay88 tests; DEMO kt00018 read-only holdings report2026-10-05T19:26:51.265407712Z at isolated pin`c2d497c76cc43a1b59a17f04c5ffd1d67a88c02a`, deploymentcd47a5f0-709c-46cc-9b8f-ea0969ce2ba9 SUCCESS/0running0crashed, one page/zero observed rows. Account-origin/completeness/freshness/ownership/cash/fee-settlement/capital-release/genuineLIVE/holdout/trading flags remain false. This is DEMO plumbing only; zero observed rows do not establish account-wide zero exposure or genuine execution evidence.

Public runtime still pins server`b5d01da4bb1c3185de7959bd480fe71f46c8a4fc`, deploymenta824af66-f8d0-4006-a7a1-49d4cd79e4f9 SUCCESS/1running0crashed, /data500MB volumef96f985a-8aba-41ef-88df-f76999c4ff0c. PR35`62f7060727a0e27df2b99bbbd277ea1e9e7e183a` is OPEN/unmerged/undeployed: read-only unavailable-automation diagnostics only,199 local tests passed. CI37364545547 attempt1 was interrupted/cancelled before steps; job111946502765 retry requested. Never represent local tests or a queued retry as remote CI success.

KRX service003812ee-102b-42b6-bda4-36925885b428 pin`ef95e7857f692fda3855390e918e165487624881`, deploymente56cf101-15c5-478e-ae67-228585013ef0 SUCCESS/0running0crashed, /data5000MB volume61610fae-dc0c-493e-9920-eb3cef4cea86: storage-integrity audit only; source/PIT/status-economics gates are not closed by acquisition or storage hashes.

Research main before this documentation correction: `c490974ff6619bb978dc6f83f9c24f2c46622f85`; economics audit`5aefb98988f7b4ccf7c95e7cdf2a671a7bdfee7e`; early-LIVE draft`1d81eb526f59b87c528d63be9e3883e0f76fedf6`. No REJECT/INCONCLUSIVE/idea or future draft has been applied to the Champion. No code, Master Spec, model, threshold, immutable execution history or private holdout artifact is changed by this synchronization.

Research follow-up: independently resolve the canonical committed-capital/user-control contract before integrating the currently separate server and development structural interfaces. Their capital-ceiling domains/action vocabularies differ; no silent mapping or numerical criterion change is authorized. Complete account/day/side/whole-account scope, stable cross-day ownership, native fee/sale settlement, source/PIT/affected-position economics, genuine LIVE evidence and frozen reconnect/Kill/pretrade admission remain unresolved. Caller flags, synthetic replay, estimated valuation fees and DEMO snapshots cannot satisfy these gates.

Exact resume: re-fetch actual dev/server/research heads and PR35 run/job detail; merge/deploy only after exact-head CI199 success. Preserve public source pin/startup audits/volume and DEMO isolation root. Continue admissible independent engineering and research contract work, recording new issues in the ledger; do not reopen v1 or activate broker orders. Actual stock orders/funds/broker permission changes require separate explicit authority after frozen readiness. The project is not complete.

---

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

## 2026-10-02 — Kiwoom demo/read-only connectivity evidence synchronized

Canonical `INDEXALERT_KIWOOM_DEMO_CONNECTIVITY_EVIDENCE.md` records a user-operated mock-host smoke result of `TOKEN_OK / ACCOUNT_OK / BALANCE_OK / FILLS_OK`. Disposition: **DEMO READ-ONLY PLUMBING OBSERVED; NO PROMOTION CREDIT**. This evidence must not be counted as genuine LIVE provenance, empirical fill/slippage/capacity evidence, exact status-event economics, KRX authorization/data evidence, sealed-holdout authorization, or live-order authorization.

## 2026-10-02 — Internal completeness audit

Disposition: **INTERNAL AUTHORITY BOUNDARY HARDENED; NO EXTERNAL BLOCKER CREDIT**. Whole-boundary review of continuous research, successor staging, automation controls, Kiwoom offline normalization and execution evidence found one internal authority ambiguity and fixed it fail-closed. Promotion eligibility is now explicitly distinct from Core mutation authority. No sealed holdout or genuine LIVE evidence was consumed.

## 2026-10-05 — Research governance malformed-input correction

Engineering fault reproduction on canonical research code: all_preregistered_acceptance_criteria_passed="false" incorrectly classified a trial ACCEPTED_CHALLENGER; scalar data_roles="sealed_holdout" also bypassed role exclusion. Disposition: **INPUT VALIDATION DEFECT; NO RESEARCH OR PROMOTION CREDIT**. Fix exact-boolean acceptance and result/authority flags, require an explicit nonempty role list, and retain normalized forbidden-role matching. Existing accepted synthetic fixtures remain staging only; no empirical trial was evaluated or adopted. The same audit reproduced calibration_drift="false" plus a null reference creating an IDEA with evidence_ref="None". Extend exact-boolean diagnostic checks and require genuine nonempty reference strings; malformed diagnostic/reference-map types fail closed with no queue. Ten governance tests,9 orchestrator tests and6 successor tests (25 combined) pass locally. Remote exact-head CI must pass before merge. No Core/model/threshold/holdout/private artifact/order change. This safety code correction is to be synchronized into development separately; it is not a strategy Challenger.
