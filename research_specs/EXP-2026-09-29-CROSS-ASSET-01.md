# EXP-2026-09-29-CROSS-ASSET-01

Status at registration: **PRESPECIFIED / NOT YET RUN**

## Question

Can one small independent cross-asset regime family restore current OOS admissions and robust economic edge without changing the Korean stock model, calibration quantiles, costs, Top3 policy or admission threshold?

## Source family

Historical carrier: FRED daily-close series.

- `NASDAQCOM` — NASDAQ Composite daily close
- `VIXCLS` — CBOE VIX daily close

This is developmental source evidence, not Final-Judge market-data lineage. FRED history may be revised and the ultimate live system must use a timestamped market feed whose availability is independently validated.

## Conservative availability rule

To avoid assuming FRED has published an observation at the instant the underlying U.S. market closes, an observation dated U.S. day `t` is eligible only for Korean decisions on or after calendar date `t + 2 days`.

This deliberately sacrifices freshness to prevent same-day publication-time leakage. No forward fill across the availability boundary is allowed; after eligibility, the latest available observation may be carried through non-U.S. trading days.

## Added features only

1. `nasdaq_ret1_available`
2. `nasdaq_ret5_available`
3. `vix_log_available`
4. `vix_change5_available`

No feature subset search, threshold search, interaction search or lag search is allowed from this experiment.

## Frozen Korean protocol

- CA-safe KRX feature/label/MTM axis
- history: 2015-06-15 onward
- ADV20 rank >= 20th percentile
- Ridge mean executable D+5 NetReturn
- selection-conditioned residual q25/q50/q75 calibration
- train 504 / calibration 126 / test 126
- purge 5 sessions
- date-aware tax + commission + spread/impact unchanged
- admission `netev_low > 0`
- freeze original Top3
- preliminary normal-market fail-closed veto after rank freeze
- no rank-4+ backfill
- 0..3 / NO_TRADE valid

## Predeclared continuation criteria

For the normal-market fail-closed candidate:

1. mean cost-adjusted OOS NetReturn > 0;
2. PF > 1;
3. date-cluster 95% lower bound > 0;
4. after removing best 5 decision days, mean NetReturn > 0 and PF > 1;
5. at least one admission in latest 504 OOS test sessions;
6. latest-504 mean NetReturn > 0 and PF > 1 (cluster LCB remains diagnostic if sample is small);
7. no material worsening in ES95 or MDD relative to reference;
8. source/date-alignment integrity tests pass.

Even a full pass only justifies freezing the family for further falsification because this development history is not sealed.

## Failure disposition

If the family fails the recent-evidence and robustness criteria, do not tune FRED lags, feature windows or VIX/NASDAQ thresholds from the observed result. Record the failure and move to a genuinely different information family or data-quality blocker.
