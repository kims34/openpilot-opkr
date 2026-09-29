# IndexAlert Research Ledger

Purpose: prevent research-memory bias and repeated policy mining. This ledger records material experiments, their fixed question, outcome and disposition. It is not a performance marketing document.

## Governance

- Production promotion is impossible from development results alone.
- Primary economics: executable, cost-adjusted OOS NetReturn / NetEV.
- Freeze original decision-time Top3; blocked/held/vetoed slots stay empty; no rank-4+ backfill.
- 0..3 and NO_TRADE are valid.
- Five-session purge around outcome boundaries for the 5-session target.
- Corporate-action-safe KRX base-price returns are mandatory for feature/label/MTM research.
- Candidate changes must be identified before reading the candidate's test outcome. Do not relax q25, TopK, costs, recent-evidence requirements or execution assumptions to manufacture trades.
- Keep negative experiments in the ledger.
- A development candidate can only justify further falsification. Sealed holdout + prospective Shadow are required for actual promotion.

## Material completed experiments

### Legacy simple momentum / probability baselines
Status: **REJECTED as current champion**.

Reason: after realistic costs and corrected execution accounting, simple momentum/probability baselines did not establish positive robust OOS economic edge. Earlier optimistic outputs affected by execution-set mismatches or later-superseded data assumptions are not promotion evidence.

### Purge / embargo correction
Status: **ADOPTED as mandatory validation policy**.

Finding: 5-session targets require a five-session boundary purge. Pre-purge ML results are superseded for promotion purposes.

### Rolling 160-session recency training
Status: **REJECTED**.

Prespecified challenger result: roughly 85 trades, mean NetReturn -1.58%, PF 0.45, negative cluster lower bound and materially worse drawdown than the expanding reference. Do not sweep nearby recency windows from this failure.

### Corporate-action-safe return axis
Status: **ADOPTED as mandatory data policy**.

Finding: raw close ratios can create false momentum, labels and MTM around splits/rights/capital actions. Current research uses KRX base-price-adjusted daily returns and fingerprinted fail-closed supervised caches. All raw-close promotion conclusions are superseded.

### Long-history marginal Distributional NetEV
Status: **REJECTED as robust edge**.

2015-06-15 onward CA-safe long-history testing falsified the short-window optimism. Without a normal-market status layer, catastrophic non-standard-price observations dominated tail risk. With the preliminary fail-closed market-state overlay, point estimates improved but cluster lower bounds remained non-positive.

### Selection-conditioned residual calibration
Status: **KEEP AS DEVELOPMENTAL / NOT PROMOTABLE**.

Fixed change: estimate residual q25/q50/q75 from calibration-day Top3 by predicted mean, while keeping model, quantile levels, Top3, costs and test threshold unchanged.

Strongest developmental all-context result after the preliminary normal-market fail-closed overlay: about 278 trades, mean NetReturn +1.15%, PF 1.55, but cluster 95% lower bound remains below zero; best-five-decision-day removal turns the edge negative; no admissions in the latest 504 OOS test sessions. Positive history is concentrated in 2018-2021.

Important chronology: the normal-market >30.5% decision-day return veto was added after the selection-conditioned challenger was first developed. It is structurally justified as a data/market-state fail-closed rule, but its development-sample performance lift is not independent evidence. Freeze and validate it only on fresh evidence.

### EXP-2026-09-29-CA-PATH-01 — CA-safe daily path feature family
Status: **REJECTED / DO NOT RETUNE**. GitHub Actions run `36549690847`.

Question: does one additional decision-close path-information family restore current, robust economic edge without changing model or thresholds?

Only change tested:
- CA-safe opening gap relative to reconstructed KRX base price
- same-session open-to-close return
- same-session high-low range
- close location in range
- trading-value surprise vs prior 20 sessions
- cross-sectional ranks of those path variables

Frozen protocol: modern +/-30% price-limit regime from 2015-06-15; Ridge mean NetReturn; selection-conditioned q25/q50/q75 calibration; train 504 / calibration 126 / test 126 / purge 5; costs unchanged; `netev_low > 0`; original Top3 frozen; preliminary normal-market fail-closed overlay after rank freeze; no backfill.

Result after normal-market fail-closed overlay:
- 88 trades
- mean gross +0.716%
- mean cost 0.386%
- mean NetReturn **+0.330%**
- PF **1.082**
- date-cluster 95% lower bound **-3.959%**
- ES95 **-26.41%**
- portfolio total return **-4.40%**
- CAGR **-0.54%**
- MDD **-20.44%**
- latest 504 OOS test sessions: **0 admissions**
- remove best 1 decision day: mean NetReturn **-0.642%**, PF **0.846**
- remove best 5 decision days: mean NetReturn **-2.668%**, PF **0.449**

Disposition: failed the preregistered cluster-LCB, extreme-day-independence, current-evidence and portfolio-economics criteria. It also underperformed the existing selection-conditioned reference on mean NetReturn, PF, cluster lower bound and tail loss. Do not tune alternate gap definitions, path thresholds or path-family subsets from this result.

### EXP-2026-09-29-RECENT-GATE-01 — recent-regime gate waterfall
Status: **COMPLETED DIAGNOSTIC / NO POLICY CHANGE**. GitHub Actions run `36555181788`.

Question: why does the strongest developmental selection-conditioned candidate produce no admissions in the recent regime?

Frozen protocol: same all-context mean model, selection-conditioned residual q25, train 504 / calibration 126 / test 126 / purge 5, same costs, original Top3, normal-market fail-closed veto, no backfill. No thresholds or quantile levels were changed.

Latest 504 OOS sessions (2024-08-20 through 2026-09-16):
- original Top3 rows: **1,512**
- raw `pred_mean > 0`: **1,464**
- raw-positive rows blocked by `netev_low <= 0`: **1,460**
- conservative `netev_low > 0`: **4** rows on 3 dates
- all four conservative-positive rows were removed by the preliminary non-standard-market veto
- final admissions: **0**
- original-Top3 mean `pred_mean`: **+1.410%**
- original-Top3 mean calibration penalty (`netev_low - pred_mean`): **-9.934%**
- original-Top3 mean `netev_low`: **-8.523%**

2024 and 2025 each had zero conservative-positive Top3 rows; 2026 had four, all vetoed. The dominant recent bottleneck is therefore **uncertainty/calibration width**, with the market-status veto only affecting the tiny set that survives q25. Do not loosen q25 merely to manufacture trades.

A realized-outcome audit of the q25-blocked rows was preregistered before reading its result. It will decide whether abstention is correctly protective or whether a conditional-q25 estimator is worth testing.

## Preregistered / running experiments

### EXP-2026-09-29-UNCERTAINTY-AUDIT-01 — realized outcomes behind q25 veto
Status: **RUNNING**.

No model or policy change. Measure realised 5-session NetReturn, PF, date-cluster CI, ES5 and remove-best-1/3/5-day robustness for original Top3, raw-positive Top3, q25-blocked raw-positive Top3 and conservative-positive Top3 in all OOS / 2022+ / 2024+ / latest-504 windows.

Decision fixed before outcome:
- if q25-blocked rows are economically weak or jackpot-dependent: keep abstention and seek orthogonal information;
- if blocked rows have positive economics but wide conditional tails: test a conditional q25 estimator at the **same 25th-percentile target**;
- do not change TopK, q-level, costs or admission threshold from this audit.

### EXP-2026-09-29-POLICY-CAL-01 — policy-aligned calibration population
Status: **PREREGISTERED, NOT YET READ**.

Structural issue found before running the challenger: current selection-conditioned calibration freezes calibration-day Top3 by `pred_mean`, but does **not** apply the decision-time non-standard-market fail-closed veto before estimating residual quantiles, whereas the test/trade policy applies that veto after Top3 freeze.

Prespecified challenger:
1. calibration-day Top3 is frozen by `pred_mean` exactly as before;
2. apply the same decision-time normal-market veto to those frozen calibration rows;
3. vetoed slots stay empty; rank 4+ is never promoted;
4. estimate q25/q50/q75 residuals only from policy-eligible calibration Top3;
5. mean model, features, q-levels, train/cal/test windows, costs, test Top3 and admission `netev_low > 0` remain unchanged.

This is a **population-alignment test, not a q25 relaxation**. It is kept only if calibration coverage and economic/tail robustness do not deteriorate. Any apparent performance gain remains development evidence and cannot promote without fresh sealed evidence.

## Next information family after CA-path failure

Do **not** continue price-only feature/threshold mining. Prefer one genuinely independent PIT-valid information family.

Current first candidate: **KRX investor-flow data**. Official KRX Data Marketplace states that final investor trading results for the day are provided after 20:00, so a day-D final-flow feature may only be used for the next eligible decision after publication. Before any performance test, establish official source/access, historical coverage, security mapping and `event_time/published_at/available_at/ingested_at` lineage. If a reproducible official historical feed cannot be obtained, do not substitute an undocumented same-day proxy merely to run a backtest.
