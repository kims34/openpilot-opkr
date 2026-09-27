# IndexAlert probability research — 2026-09-27

Production remains on `3.3-calibration-gated` (`production_v20`).
No experiment below met promotion criteria. Do not loosen gates merely to force a different probability.

## v3.4 — causal categorical market-state challengers
Signals: prior-day return strength, two-day sign pattern, 20-session trend, distance from 60-session high, 20-session volatility regime.

Integrity tests: 3/3 passed, including future-data invariance.

Live 1,008-session audit versus actually-served 3.3/3.2 safety forecast:
- SPY: candidate Brier 0.24796554 vs previous 0.24767193 — reject.
- QQQ: candidate Brier 0.24722443 vs previous 0.24666747 — reject.
- SCHD: candidate Brier 0.25079493 vs previous 0.25076421 — reject.

Result: all gates rejected; served probabilities unchanged.

## v3.5 — price-only ridge residual model
Features: 1d return, 5d momentum, 20d momentum, 20d volatility, 60d drawdown.
36 configurations tested with development-only selection and an untouched final 252-session holdout.

Development result:
- SPY: no stable development winner.
- QQQ: no stable development winner.
- SCHD: no stable development winner.

Result: rejected before holdout evaluation.

## v3.6 — VIX + cross-asset residual model
Features: log VIX level, VIX 1d move, SPY/QQQ/SCHD breadth, target 1d/5d/20d momentum, target 20d volatility, target 20d relative momentum vs SPY.
Aligned history: 2,514 common sessions, 2016-09-26 through 2026-09-25.
Final 252 sessions were untouched until final scoring.

Development / holdout result:
- SPY: no stable development winner.
- SCHD: no stable development winner.
- QQQ: development winner `(window=756, ridge=100, cap=0.02)` but failed untouched holdout.
  - previous holdout Brier: 0.24770245
  - candidate holdout Brier: 0.24895912
  - total holdout gain: -0.00125667
  - first-half gain: -0.00180163
  - second-half gain: -0.00071171

Result: rejected.

## Current conclusion
The simple validated 3.3/3.2 safety forecast remains stronger than the tested price-state, ridge-price, and VIX/cross-asset challengers under strict chronological validation. Future work should prioritize genuinely new information and prospective evidence rather than adding model complexity.
