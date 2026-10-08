# Frozen block16 model rehydration — 2026-10-08

Status: STRUCTURAL MODEL RECONSTRUCTION ONLY — NO TEST PERFORMANCE, NO CURRENT-SESSION SCORE, NO ALPHA/LIVE AUTHORITY.

The source and feature/label prerequisites are now independently reconstructed and exact-matched to adopted Action 36643183157:

- long-history source: 2,512,128 rows / 1,089 symbols / exact XOR+sum fingerprint;
- frozen supervised cache: 2,486,909 rows / 2,484,241 DecisionRecords / complete exact metadata and diagnostics match.

The next frozen H5 state is therefore reconstructed only from the training and calibration windows preceding the already-adopted block beginning 2026-05-11. The Action artifact fixes the structural dates and policy-aligned calibration result:

- block index 16, test start ordinal 2656 = 2026-05-11;
- anchored expanding training ends 2025-10-17;
- five-session purge;
- calibration 2025-10-27 through 2026-04-29, 126 sessions;
- five-session purge before the test block;
- calibration freezes each day's original Top3 by predicted mean, applies the same normal-market veto, and never backfills;
- exactly 378 frozen calibration rows, 371 retained, 7 vetoed across 6 dates / 5 symbols;
- exact global q25/q50/q75 = -0.10747415305238285 / -0.04253637350115687 / 0.03058802127529393.

`pit_rebuild/rehydrate_frozen_block16_model.py` reads only the verified long-history and verified supervised cache, rebuilds the corporate-action-safe D+5 target for the train/calibration sessions, fits the unchanged median-imputer → StandardScaler → Ridge(alpha=1.0) pipeline under the exact Action runtime, and requires the complete block16 policy-aligned quantile/diagnostic object to equal the recovered artifact exactly.

No block16 test rows or outcomes are consumed for fitting/calibration. No present-day features are consumed. The consumed v1 holdout artifact is not opened. No performance metric is recomputed. The output is a pickle-free canonical model bundle compatible with the main prospective model validator and remains `independent_model_admission_verified=false`, `fresh_alpha_observation_admitted=false`, and `live_order_authorized=false`.

The model is published into a new immutable PIT-volume directory only after all reference checks succeed. It is the fixed model/calibration state that prospective sessions in this still-active 126-session block may later bind to; each future session still requires its own official current-session source, input snapshot, producer binding, append-only decision capture, and independent chronology/source/model admission.
