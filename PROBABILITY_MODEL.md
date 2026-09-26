# Next-close probability contract (model 3.0)

- Target: next US regular-session closing price is strictly greater than the latest completed closing price. Equal closes count as not rising. Uses Yahoo `quote.close`, excluding cash dividends; it does not silently substitute total-return `adjclose`.
- Universe: SPY, QQQ, SCHD only. Existing alert rules, KOSPI and FX displays are separate.
- Calendar: XNYS trading sessions, holidays and early closes. Daily bars need a 15-minute closing grace. Missing/duplicate/out-of-order dates, stale histories and obvious split/unit discontinuities suppress output.
- Features retained: 1/5/20-session momentum, 20-session volatility, distance from the 60-session closing high. Scaling, neighbors and outcomes use only data known at each forecast origin.
- The neighbor estimate is shrunk toward the ETF's own time-weighted historical rise rate. A prior strength of 80 affects the point estimate only, never an uncertainty interval or an observed sample count.
- Policy: on each forecast date, the prior 504 known daily predictions choose a shrinkage alpha from {0, .25, .5, .75, 1}. The older two-thirds fit alpha; the newer third must show improvement beyond a fixed conservative HAC-error margin. Otherwise alpha is zero (baseline). These settings are declared in code, not optimized on the reported audit.
- Evaluation: up to 1,008 later daily predictions apply the entire past-only policy. The current day's unknown outcome is excluded from model selection. Report Brier loss, baseline Brier, log loss, fixed-bin calibration and negative as well as positive skill. The benchmark is the same causal historical rise-rate estimator, not a trading strategy.
- Uncertainty: removed the previous pseudo-sample-based "80% probability range". A 20-session moving-block resample (400 repetitions) describes historical skill and historical calibration-bin frequencies. These are approximate historical sampling ranges, not a confidence interval for tomorrow's individual probability or a guarantee under regime change.
- Prospective ledger: save the first prediction before the target session opens; never overwrite it. Score it only after the target session closes. Keep prospective counts separate from reconstructed backtests; updated vendor history and design choices still limit backtest interpretation.
- Android: accept only this model's validated, unexpired payload. Retain a valid prior response during an outage and label it as cached. Otherwise show unavailable; do not silently replace audited results with a different local heuristic. Show origin and target dates.

## Verification

`python -m unittest discover -p test_probability.py -v`

Tests cover future/outcome leakage, selection detecting real signal, truthful negative skill, incomplete/early-close bars, holidays, corrupt and stale data, immutable forecasts, and stale-response suppression.

## References

- https://scikit-learn.org/stable/modules/calibration.html
- https://otexts.com/fpp3/tscv.html
- https://github.com/gerrymanoim/exchange_calendars
