# Frozen block16 model rehydration — 2026-10-08

Status: STRUCTURAL / PLATFORM-EQUIVALENT MODEL RECONSTRUCTION ONLY — NOT INDEPENDENTLY ADMITTED, NO TEST PERFORMANCE, NO CURRENT-SESSION SCORE, NO ALPHA/LIVE AUTHORITY.

The source and feature/label prerequisites were independently reconstructed twice and exact-matched to adopted Action 36643183157:

- long-history source: 2,512,128 rows / 1,089 symbols / exact XOR+sum fingerprint / raw origin 2015-06-15;
- frozen supervised cache: 2,486,909 rows / 2,484,241 DecisionRecords / exact logical fingerprint / supervised-session origin 2015-07-10;
- the walk-forward schedule uses the supervised-session calendar, matching the Action implementation, while the source identity remains bound to the 2015-06-15 raw panel.

The frozen block is fixed:

- block index 16, supervised ordinal 2656 = 2026-05-11;
- expanding training ends 2025-10-17;
- five-session purge;
- calibration 2025-10-27 through 2026-04-29, 126 sessions;
- five-session purge before the test block;
- original calibration Top3 is frozen by predicted mean, the normal-market veto is applied afterwards, and blocked slots are never backfilled;
- exactly 378 frozen calibration rows, 371 retained, 7 vetoed across 6 dates / 5 symbols.

A Railway reconstruction under the same pinned Python/numpy/pandas/scikit-learn/SciPy versions reproduced every discrete calibration fact exactly, but the floating residual quantiles differed from the GitHub Actions artifact only at machine scale: maximum 43 IEEE-754 float64 ULP and maximum absolute difference 1.491862189340054e-16. The source fingerprints, supervised fingerprints, row counts, dates, selection counts, veto counts, bucket counts and policy diagnostics were exact.

This is treated as a platform-numeric reproduction boundary, not a research tolerance. The verifier requires:

- exact mapping/list structure, keys, strings, booleans and integer counts;
- exact frozen pre-veto selection-conditioned Top3 calibration structure;
- exact frozen post-veto policy-aligned calibration structure;
- for floating leaves only, both <= 64 float64 ULP and <= 2e-15 absolute difference;
- exact calibration-policy diagnostics;
- any violation fails closed.

Both the pre-veto selection-conditioned quantiles and the post-veto policy-aligned quantiles are bound to the recovered Action artifact. After the current-platform computation proves the strict machine-scale equivalence, the model bundle stores the **canonical quantile values from the Action artifact**, rather than silently replacing the frozen calibration thresholds with host-specific last-bit results.

The mean Ridge state is still recomputed on the current host. The artifact did not preserve the exact fitted coefficients, so the output explicitly records `model_state_exact_action_coefficients_verified=false` and remains `independent_model_admission_verified=false`. Platform equivalence therefore does **not** manufacture independent model admission.

No block16 test rows or outcomes are consumed for fitting/calibration. No present-day features are consumed. The consumed v1 holdout artifact is not opened. No performance metric is recomputed. `fresh_alpha_observation_admitted=false`, `promotion_authority=false`, and `live_order_authorized=false` remain mandatory.

The model is published into a new immutable PIT-volume directory only after all structural, source, supervised, calibration and machine-scale checks succeed. Future prospective sessions still require official current-session source evidence, input snapshot, producer binding, append-only decision capture and independent chronology/source/model admission before any later stage may rely on them.
