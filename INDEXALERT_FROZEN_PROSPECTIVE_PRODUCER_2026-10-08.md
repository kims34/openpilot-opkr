# Frozen prospective H5 producer schedule — 2026-10-08

Status: STRUCTURAL PRODUCER BINDING ONLY — NO NEW PERFORMANCE TEST, NO HOLDOUT ACCESS, NO ALPHA ADMISSION, NO ORDER AUTHORITY.

The prospective protocol froze H5 / anchored WF 504-126-126 / purge5 / selection-conditioned q25 / strict Top3 / no backfill, but the later integration review correctly noted that a long-running producer also needs an explicit model/refit identity. Rather than inventing a new cadence, this change reads the actual freeze-anchor implementation at commit `5f19026e320ed8aec49f61b5273d03467d7437aa`.

At that anchor, `selected_calibration_walk_forward` already defined the schedule mechanically:

- first test block begins at ordinal `504 + 126 + 5 + 5 = 640`;
- training is anchored/expanding: `dates[:train_end]`;
- a five-session purge separates training from the 126-session calibration block;
- another five-session purge separates calibration from the test block;
- the fitted Ridge + selection-conditioned residual quantiles are held for one 126-session test block;
- the next 126-session block refits by the same arithmetic.

`research_v1_prospective_frozen_producer.py` makes that pre-existing schedule explicit and hash-bound. It uses only scheduled pre-test training/calibration rows, fits the exact Ridge pipeline, estimates calibration Top3 residual q25/q50/q75 with the existing function, and emits the previously introduced pickle-free model bundle plus a producer binding containing the block identity and data fingerprints.

The producer binding explicitly records that current/test features and outcomes were not consumed for fitting, the failed/consumed v1 holdout was not used, historical backfill is forbidden, and every source/model/Fresh-Alpha/promotion/live authority remains false.

This is not permission to execute a private-data fit yet. It is the deterministic contract needed so a future authorized run cannot choose a refit cadence after seeing outcomes. Synthetic tests alter test-block outcomes by extreme values and verify that the resulting model/binding fingerprints remain unchanged, while calibration-outcome changes alter the calibration fingerprint as expected.

No historical performance metrics are recomputed, no KRX network request is made, no consumed holdout is read, and no broker/account/funds action occurs.
