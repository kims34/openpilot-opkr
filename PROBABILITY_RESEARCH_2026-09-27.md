# IndexAlert probability research — 2026-09-27

The pre-open / next-session production probability remains the guarded `3.3-calibration-gated` model, which currently falls back to the validated 3.2 probability when its calibration gate fails. Do not loosen gates merely to force a different probability.

A separate after-open nowcast (`3.9-open-nowcast`) passed research and integrity gates. It has different timing semantics and must never replace or be shown as the pre-open forecast.

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

## v3.7 — macro / risk-appetite residual model
Added genuinely different information: VIX, TLT, HYG, IWM, UUP and GLD, including credit appetite (HYG vs TLT), small-cap appetite (IWM vs SPY), duration/rates proxy, dollar and gold context.

Development / holdout result:
- SPY: no stable development winner.
- QQQ: no stable development winner.
- SCHD: development winner `(window=756, ridge=1000, cap=0.02)` but failed untouched holdout.
  - development gain overall: +0.00042043
  - development first half: +0.00060348
  - development second half: +0.00023739
  - previous holdout Brier: 0.24960983
  - candidate holdout Brier: 0.25016233
  - total holdout gain: -0.00055250
  - first-half gain: +0.00233369
  - second-half gain: -0.00343869

Result: rejected.

## v3.8 — calendar / seasonality model
Used only ex-ante calendar information: weekday and month cycles, first/last three sessions of month, first/last session, quarter/year-end and known gap to the next trading session.

Results:
- SPY selected `(window=756, ridge=30, cap=0.02)` in development but failed holdout.
  - previous holdout Brier: 0.24952487
  - candidate holdout Brier: 0.25039655
  - total holdout gain: -0.00087168
  - first-half gain: +0.00213699
  - second-half gain: -0.00388036
- QQQ selected `(window=756, ridge=30, cap=0.03)` in development but failed holdout.
  - previous holdout Brier: 0.24770245
  - candidate holdout Brier: 0.24943959
  - total holdout gain: -0.00173714
  - first-half gain: +0.00194247
  - second-half gain: -0.00541674
- SCHD: no stable development winner.

Result: rejected.

## v3.9 — after-open nowcast
This is a different forecast timing, not a replacement for the pre-open probability. Once the target U.S. session has opened, the official session opening price is known. The model uses that opening gap versus the prior completed close plus prior-close information to estimate whether the target close will finish above the prior close.

Features: target-session opening gap, absolute gap, positive-gap flag, prior 1d return, prior 5d momentum and gap × prior-return interaction. Rolling ridge residual correction is applied to the already-served guarded pre-open forecast.

Development selection and untouched final-252-session holdout:
- SPY selected `(window=504, ridge=100, cap=0.15)`.
  - development gain overall / halves: +0.02780775 / +0.02843348 / +0.02718202
  - previous holdout Brier: 0.24952487
  - after-open holdout Brier: 0.21332140
  - holdout gain overall / halves: +0.03620346 / +0.02157320 / +0.05083373
- QQQ selected `(window=756, ridge=100, cap=0.15)`.
  - development gain overall / halves: +0.03094747 / +0.02888071 / +0.03301424
  - previous holdout Brier: 0.24770245
  - after-open holdout Brier: 0.21481614
  - holdout gain overall / halves: +0.03288631 / +0.02565636 / +0.04011625
- SCHD selected `(window=252, ridge=100, cap=0.15)`.
  - development gain overall / halves: +0.03083538 / +0.03236626 / +0.02930449
  - previous holdout Brier: 0.24960983
  - after-open holdout Brier: 0.22383007
  - holdout gain overall / halves: +0.02577976 / +0.01827598 / +0.03328355

All three passed the untouched holdout gate overall and in both chronological halves.

Integrity workflow on 2,514 aligned sessions:
- validated close vs OHLC close basis error: 0 for SPY, QQQ and SCHD.
- overnight gaps above 15%: 0 for all three.
- maximum absolute observed gap: SPY 10.45%, QQQ 9.46%, SCHD 10.66%.
- timing-safety runtime tests: 4/4 passed (not available before open+5m, not available after close, target-day close ignored, live gap calculation verified).

Promotion rule:
- Keep the existing pre-open probability unchanged.
- Expose v3.9 only as a clearly separate `after_open` probability after target-session open + 5 minutes.
- Freeze the first live after-open forecast in a separate prospective ledger and score it after the target close. Prospective evidence must accumulate before treating the historical gain as durable live evidence.

## Current conclusion
More model complexity did not improve the pre-open forecast under strict chronology. The first robust improvement came from genuinely new information that becomes available after the market opens. Therefore the safe architecture is two-timing: retain the guarded 3.3/3.2 next-session probability before the open, and add v3.9 only as a separately labeled after-open nowcast once timing and data-quality gates are satisfied.
