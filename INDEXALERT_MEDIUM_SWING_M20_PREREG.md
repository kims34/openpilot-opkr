# IndexAlert Medium-Swing Fundamental Drift Preregistration — M20 v1

Status: **PREREGISTERED / DATA-GATED / NEW EVIDENCE REQUIRED**

## Research question

Can a materially different, PIT-safe fundamental-information-drift strategy held for one trading month improve sustainable annual post-cost risk-adjusted net return relative to the frozen H5 short reference, without rescuing or retuning the rejected price/context H10 candidate?

## Economic hypothesis

The candidate tests **gradual incorporation of newly disclosed quarterly operating-performance information** rather than extending the existing short-horizon price model.

For each officially available quarterly disclosure, define a seasonal operating-profit shock from the newly disclosed quarter versus the comparable quarter one year earlier, scaled by the decision-time PIT market capitalization. A simple fixed Ridge distributional model may combine that fundamental shock with the already-frozen contemporaneous market/context fields solely to estimate D+20 cost-adjusted return. The hypothesis is that sufficiently strong positive fundamental shocks can retain positive executable NetEV over approximately one trading month because public information is not always incorporated immediately.

This is a distinct mechanism from the rejected H10 price/context Swing. H10 remains rejected and is not a comparator to tune against.

## Primary horizon and anti-sweep rule

- Primary holding horizon: **20 KRX sessions**.
- Entry: next eligible regular-session executable open after the first decision close at which the disclosure is admissibly known.
- Primary research exit: **D+20 close**.
- No H5/H7/H10/H15/H20 horizon tournament is permitted.
- D+5/D+10/D+15 markouts, if later retained for diagnostics, are path/risk diagnostics only and may not select a different horizon within this trial.
- No stop-loss/take-profit threshold is introduced in the first alpha-existence trial. This intentionally separates alpha existence from exit-rule mining. Path MDD/ES/adverse excursion must still be reported; a later dynamic-exit Challenger requires a separate preregistration.

The choice of 20 sessions is an ex-ante economic one-trading-month horizon for the fundamental-information-drift mechanism. It is not a rescue of the archived price-only H20 evidence.

## Required new PIT evidence before any performance run

Empirical execution is forbidden until all required source fields are independently admitted for the tested history:

1. Official OpenDART disclosure identity and stable corporation-to-KRX-security mapping.
2. PIT-safe disclosure availability. If exact historical publication time is unavailable, the filing is shifted conservatively to the next eligible decision session; receipt date alone never grants same-day availability.
3. Quarterly operating-profit values and comparable prior-year-quarter values with reproducible document/field lineage and restatement handling.
4. Decision-time market capitalization and all existing KRX security/status/tradability inputs under their applicable source gates.
5. Corporate-action-safe entry/exit return path and exact affected-position status economics under existing fail-closed rules.

Current metadata-only OpenDART reachability/probe code is not sufficient evidence for items 1–3.

## Frozen signal and model family

The fundamental shock is:

`operating_profit_shock_to_mcap = (operating_profit_q - operating_profit_q_minus_4) / decision_time_market_cap`

Rules:
- use only values that were officially available before the decision timestamp;
- no forward-filled future/restated value may rewrite an earlier decision;
- non-comparable/missing quarters are ineligible, not imputed;
- no analyst-consensus, news sentiment, investor-flow or alternative earnings metric is added in this v1 trial;
- no feature-family sweep.

Primary model:
- Ridge regression with the repository's existing fixed alpha=1.0 preprocessing/model convention;
- inputs limited to the preregistered fundamental shock plus the already-frozen contemporaneous market/context fields;
- target = corporate-action-safe next-open to D+20-close net return after the preregistered cost model;
- selection-conditional residual calibration uses the existing q25/q50/q75 framework;
- admit only conservative `NetEV_low > 0`;
- freeze original decision-time Top3; vetoed/unfillable slots remain empty; no rank-4+ backfill;
- `NO_TRADE` is valid.

No alternative model, threshold, q-level, TopK or signal definition may replace a poor result inside this trial.

## Validation design

Primary developmental evidence:
- anchored walk-forward train 504 / calibration 126 / test 126 sessions;
- purge and embargo = 20 sessions;
- test outcomes never tune features, thresholds, costs or horizon;
- current project-v1 consumed failed-invalid holdout is forbidden.

Secondary stability diagnostic, only after the primary run is structurally valid:
- the existing six-group Purged CPCV construction;
- every two-group test combination;
- one remaining group as calibration and three as train;
- horizon-matched purge/embargo;
- repeated test identities are not pooled as independent observations.

Insufficient PIT history or event count yields **NEW EVIDENCE REQUIRED**, not relaxed windows or a different horizon.

## Cost, capital and risk accounting

The v1 medium strategy must include:
- date-aware statutory sell tax;
- commission allowance;
- spread/impact allowance and the same fixed participation reference used for comparable research until empirical capacity evidence exists;
- entry and exit feasibility/status rules;
- 20-session capital occupation in the portfolio simulation;
- overlapping-position and duplicate-symbol accounting;
- turnover and explicit cost drag.

Required risk/economic reporting:
- post-cost mean NetReturn / NetEV and date-cluster 95% LCB;
- PF;
- annualized geometric net return/CAGR on the common portfolio path;
- annualized daily volatility;
- MDD;
- daily and trade ES95/ES99;
- maximum underwater/loss duration;
- turnover and cost drag;
- coverage / NO_TRADE rate;
- maximum/average capital occupation;
- concentration by date/name;
- remove-best-1/3/5-decision-day sensitivity;
- 2x-cost stress;
- capacity/execution limitations.

A high CAGR cannot compensate for failed tail, concentration, cost, capacity or LCB evidence.

## Strategy comparison

A. Existing frozen H5 short reference — unchanged.

B. This M20 fundamental-drift Challenger — independent.

C. H5 + M20 blend — **not evaluated unless B first establishes an independently credible positive edge**.

For B versus A on their common eligible daily portfolio span:
- include cash/NO_TRADE days as zero;
- primary incremental-return evidence is a preregistered moving-block-bootstrap 95% LCB of M20-minus-H5 mean daily post-cost return > 0;
- B must also independently have positive mean NetReturn, PF > 1, positive date-cluster LCB, survive 2x cost, and preserve positive mean/PF/LCB after removing the best five decision days;
- B must not worsen the applicable MDD, daily ES95/99 or maximum underwater duration versus A;
- capacity/execution feasibility must not be inferior in a way that invalidates practical use.

A later blend trial must use a separate preregistration with a fixed capital-allocation rule and must demonstrate incremental portfolio benefit after cross-strategy correlation, overlapping names, capital occupation and joint-tail risk.

## Stop / reject conditions

This v1 trial is rejected or stopped without rescue-tuning if any of the following applies:
- required PIT source admission cannot be established;
- the primary developmental run has non-positive cost-adjusted mean, PF <= 1, or non-positive date-cluster LCB;
- latest/recent evidence is absent or materially unstable under the then-applicable frozen recency rule;
- best-five-day sensitivity destroys positive mean/PF/LCB;
- 2x-cost mean/PF fails;
- tail/drawdown/loss-duration evidence is worse than the H5 reference without independently stronger incremental-return evidence;
- results depend on invalid status/economics rows or unavailable future information.

No rejected result may be rescued by trying H15, H10, alternate earnings definitions, threshold sweeps or post-hoc subgroups under this trial ID.

## Promotion boundary

A successful developmental result is at most an **ADOPT CANDIDATE** for further independent validation. It does not change Champion/Core, Tiny Live, Android, server or broker operation.

Any actual promotion still requires the applicable OOS/CPCV, frozen Challenger, independent source admission, untouched successor evidence, Shadow, Fresh Confirmation, execution/capacity and later live-stage gates.

Existing Tiny Live work for the frozen strategy proceeds independently and must not wait for this research.
