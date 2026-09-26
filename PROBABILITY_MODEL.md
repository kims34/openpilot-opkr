# Next-close probability contract (model 3.1)

- Target: next US regular-session closing price is strictly greater than the latest completed closing price. Equal closes count as not rising. Uses Yahoo `quote.close`, excluding cash dividends; it does not silently substitute total-return `adjclose`.
- Universe: SPY, QQQ, SCHD only. Existing alert rules, KOSPI and FX displays are separate.
- Calendar: XNYS trading sessions, holidays and early closes. Daily bars need a 15-minute closing grace. Missing/duplicate/out-of-order dates, stale histories and obvious split/unit discontinuities suppress output.
- Baseline: each ETF's past rise frequency is time-weighted with a 1,260-session half-life and a small 50/50 beta prior. Only outcomes known before the forecast are used.
- Adaptive challengers: (1) a half-life selected from 126/252/504/756/1,260/2,520 sessions, (2) previous-session direction conditioning, and (3) next-session weekday conditioning. Conditional estimates are strongly shrunk toward the baseline.
- Policy: on each forecast date, a challenger is allowed only when it beat the fixed baseline on Brier loss in both chronological halves of the prior 504 known forecasts. Otherwise the baseline is used. The live weekday candidate uses the actual next XNYS session date, so holidays do not turn it into a generic calendar-weekday guess.
- Evaluation: the latest 1,008 daily predictions apply the same past-only selection policy. Report Brier loss, baseline Brier, log loss, fixed-bin calibration and negative as well as positive skill. The current day's unknown outcome is excluded from model selection.
- Research gate: a higher-dimensional ridge model using momentum, volatility, drawdown, VIX, TLT, HYG and IWM was rejected because its final held-out Brier loss was worse than baseline. The simpler adaptive policy was promoted only after lower Brier loss was observed for SPY, QQQ and SCHD, including positive improvement in both chronological halves of the 1,008-day audit. The improvement is small and is not evidence of a guaranteed edge.
- Uncertainty: a 20-session moving-block resample (400 repetitions) describes historical skill and historical calibration-bin frequencies. These are approximate historical sampling ranges, not a confidence interval for tomorrow's individual probability or a guarantee under regime change.
- Prospective ledger: save the first prediction before the target session opens; never overwrite it. Score it only after the target session closes. A model-version change starts a separate prospective score series so 3.0 and 3.1 outcomes are not mixed.
- Android: accept only the validated, unexpired model payload. Retain a valid prior response during an outage and label it as cached. Otherwise show unavailable; do not silently replace audited results with a different local heuristic. Show origin and target dates.

## Verification

`python -m unittest discover -p test_probability.py -v`

The automated research workflow also runs real SPY/QQQ/SCHD smoke inference and the rejected cross-asset challenger side-by-side with the promoted adaptive policy.

Tests cover future/outcome leakage, causal selection, truthful negative skill, incomplete/early-close bars, holidays, corrupt and stale data, immutable forecasts, and stale-response suppression.

Deployment source trigger: model 3.1 validated on 2026-09-26.

## References

- https://scikit-learn.org/stable/modules/calibration.html
- https://otexts.com/fpp3/tscv.html
- https://github.com/gerrymanoim/exchange_calendars
