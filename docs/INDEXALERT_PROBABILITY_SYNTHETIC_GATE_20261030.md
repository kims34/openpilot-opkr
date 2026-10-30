# IndexAlert probability calibration: isolated synthetic-only gate (2026-10-30)

Status: SPECIFICATION ONLY / NO MARKET RUN / NOT VERIFIED.
Branch: indexalert-probability-synthetic-isolation-20261030 (separate from Frozen research, runtime optimization, and production).
Reference PR heads read on 2026-10-30: #412 bf3d9514a87c53b1775e22ec9ba7711f6cecc49f; #413 f003ef6247e16fcc71bd3b1b20cd4904c4d984c0; #414 0ee3dcf917942cfed05a093fc75e42e1f0dbb011; #418 2f98401cc50a6c6a25808a98516efd5bf0c944ee.
These are reference snapshots, not approvals or proof of CI/PIT.

## Immutable isolation
- Never alter Frozen H5, M20 horizon20/purge20, WF504/126/126, Champion/Top3/NO_TRADE, transaction cost/tax/risk/holdout gates.
- ORDERING=false. No deployment, merge, live orders, account changes, or market backtest.
- Existing consumed H5 holdout and Dynamic outputs may not be reused for tuning or independent claims.
- This branch is documentation-only until independently authorized synthetic-only implementation.

## Prediction contracts
- Instruments: QQQ (Nasdaq-100 proxy), SPY (S&P 500 proxy), SCHD. Adjusted prices, corporate-action lineage and instrument identity must be independently approved before market testing.
- Direction: P(next trading day adjusted close > current adjusted close), and separately P(5 trading day close > current close).
- Drawdown events: for horizon h in {5,20,60} trading days and thresholds d in {0.05,0.10,0.20,0.30}, P(min future adjusted close / reference close - 1 <= -d). Explicitly distinguish close-based event from intraday low and from ATH drawdown.
- If an ATH alert is needed, define separately P(future close <= trailing confirmed ATH*(1-d)); never silently substitute one label for another.
- Prediction issued at a pinned available-at timestamp; no same-bar finalized close/volume or future information in features.

## Calibration and quality gates (pre-registered, no numerical claims)
- Compare fixed baseline (historical prevalence) with candidate under identical forward-only splits; report Brier score, log loss, reliability by bins, sample size, confidence intervals and event prevalence. Direction additionally balanced accuracy/AUC; drawdown additionally precision-recall AUC.
- Nested chronological train/calibration/evaluation partitions; no evaluation labels in feature selection, calibration, threshold selection, or stopping rules.
- Enforce horizon-aware purge and embargo and issuer/event overlap checks. Uncertainty bounds via block bootstrap (not iid sampling).
- Rare event probabilities must show low effective sample counts and may be suppressed rather than presented as precise percentages.
- No model promotion from synthetic success; any eventual official data test requires separate PIT/source approval and new independent untouched evaluation design.

## Synthetic-only adversarial tests (proposed, NOT EXECUTED)
1. A feature timestamp later than prediction available-at must fail closed.
2. Label horizon crossing evaluation split must be purged.
3. Synthetic split with no positives must suppress unsupported calibration claims.
4. Monotonic event nesting: for identical horizon P(-30%) <= P(-20%) <= P(-10%) <= P(-5%), and horizon nesting P(event within 5d) <= P(within 20d) <= P(within 60d).
5. Missing/duplicate bars, stale timestamps, timezone/DST boundary, splits and symbol remapping must block or be explicitly classified.
6. Calibrator trained on evaluation labels must be rejected.
7. Fixed seed and SHA-pinned synthetic fixtures must reproduce deterministic results.
8. Missing SHA-256 for source, code, frozen policy, runtime and approval evidence must reject cache reuse.
9. Alert notifications must never imply order execution; ORDERING=false enforced.

## Exit criteria
Only synthetic software safety tests can pass now. Market directional skill, crash probability accuracy, trading economics, and real-data speedup remain NOT VERIFIED. PIT original-filing, public available-at, KRX official tradability and corporate actions must be independently verified before any market-based evaluation.
