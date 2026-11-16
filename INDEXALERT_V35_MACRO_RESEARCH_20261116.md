# IndexAlert 3.5 — Macro overlay accuracy research (2026-11-16)

## Status
**RESEARCH ONLY / NO PRODUCTION ADMISSION / NO ORDERS**

The existing Android app, Railway backend and deployed v3.3 probability
pipeline are not modified. Railway points to an immutable, separate
`indexalert-app-restore-20261116` commit; this repository branch is isolated.
All real trading and account permissions remain disabled.

## Goal
Improve SPY and QQQ **next completed regular-session close direction** probability
relative to the **exact as-issued reference** (not merely 50/50 accuracy).
This is not a return or intraday-price forecast.

Prespecified candidate feature families, in order:
1. Prior completed session VIX (fear / volatility regime).
2. VIX plus as-of available US 10-year Treasury yield.
3. VIX, yield and contemporaneous market breadth (from a verified
   contemporaneous universe and as-published constituents).

A signal is used only if its own source session and published-at time are
not later than the forecast timestamp. Missing or later data cannot be
silently filled by tomorrow's revised close.

## What was actually implemented
- `research_v35_macro_overlay.py`: standalone walk-forward ridge-residual
  challenger, reference probability input, fixed research families,
  training labels filtered by outcome-known time, development-only selection,
  reserved last 252 rows with two-part comparison. Explicit bounds and
  future-timestamp rejection.
- `test_research_v35_macro_overlay.py`: synthetic causality, data source
  checks and no-future-outcome tests (NOT historical market accuracy).
- `.github/workflows/indexalert-v35-macro-research.yml`: offline tests.
- `research_v35_public_data_pilot.py`: *exploratory* Yahoo historical
  backfill trial for VIX and 10-year yields. The baseline in this trial
  is the causal fixed-rate research baseline, **not actual v3.3 as-issued**.
  Only eligible aligned samples are scored. Any signal's reconstructed
  17:15 NY timestamp is an **analysis convention**, not evidence of when
  a historical provider originally published it.
- `.github/workflows/indexalert-v35-public-pilot.yml`: separate optional
  external-public-data job with metadata-only stdout. It may be blocked by
  Yahoo access, missing historical bars or provider changes.

All reported numerical metrics from synthetic regression tests are only
software-test evidence. No claim of real-world skill improvement.

## Necessary prerequisites for any future production decision
1. Preserve *as-issued* daily reference predictions (model version,
   issuance timestamp, target trading session) without retrospective changes.
2. Acquire authoritative source snapshots with verifiable as-published
   observation times, immutable checksums, trading calendar and revision
   lineage for VIX, US10Y and breadth. A public history downloaded today is
   **not proof of a historical point-in-time vintage**. Breadth requires
   a historical constituent universe rather than present-day survivors.
3. Keep feature selection strictly before the reserved OOS period.
   Once this holdout is inspected, do not call it untouched in another
   optimization round; use new chronological prospective data.
4. Compare on matching dates against the **actually served** 3.3 reference
   using Brier skill, calibration, coverage and both chronological halves.
   Accuracy alone is an incomplete score for probabilities.
5. Accumulate *new independent prospective* predictions after deployment,
   check performance across bull/bear/sideways regimes, and require
   meaningful uncertainty-aware improvement before considering a user-approved
   application update. Even a positive historical exploratory result does not
   authorize live changes.

## Operation
```bash
python -m unittest -v test_research_v35_macro_overlay
python research_v35_macro_overlay.py --input VERIFIED_CANDIDATES.json
# Or optional public-history diagnostic only:
python research_v35_public_data_pilot.py
```

The input JSON has a top-level `records` array; each item needs
`as_of`, `prediction_at`, `baseline_probability`,
`baseline_issued_at`, `target_date`, `target_close_at`,
`outcome_known_at`, binary `outcome`, and
`features` entries keyed by `vix`, `us10y`, `breadth`. Each feature
entry requires `value`, `session`, `published_at`, and
`source_quality` (`archived_asof` or `public_backfill`).
The code never treats these self-declared fields as independently verified
original vintage; even archive declarations remain blocked for admission.

## Non-negotiable safeguards
- No Railway deploy, changing production branches, API key usage or secrets.
- No live order placement, brokerage authentication, holdout/Champion change,
  permissions, or funds movement.
- No invented profitability, accuracy gains or source lineage.
- Do not resume deleted KRX worker or private volumes.


## First real-history *exploratory* run (2026-11-16)

[GitHub Actions #43814976893](https://github.com/kims34/openpilot-opkr/actions/runs/43814976893) completed successfully.

- Data: retrospective public Yahoo ETF/VIX/TNX daily bars, 1,008 aligned
  observations per SPY and QQQ; neither the as-published release timestamps
  nor the as-issued deployed v3.3 prediction series are authenticated.
- Comparison: *causal fixed-rate research baseline*; 504 development
  observations, final 252 reserved and not scored because no contender
  passed development selection.
- SPY development Brier: reference 0.244045; VIX-only 0.244611;
  VIX+10Y 0.244955.
- QQQ development Brier: reference 0.243596; VIX-only 0.244772;
  VIX+10Y 0.245023.
- Both added-feature configurations were worse over the full development
  period for both ETFs. Neither passed the prespecified positive-gain gate
  in both chronological halves. **Decision: NO_STABLE_DEVELOPMENT_WINNER**.
- Breadth was not evaluated: its historical constituent universe and
  genuine as-of data are not yet established. It must NOT be represented
  by current survivors or mislabeled as real breadth.
- No claim about production v3.3 relative performance, profitability, or
  future skill is supported. No production changes, secrets or live orders.

[Offline safety CI #43814544851](https://github.com/kims34/openpilot-opkr/actions/runs/43814544851):
**12/12 synthetic adversarial tests passed**, independent of the historical
performance experiment.
