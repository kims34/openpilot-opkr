# Frozen source vs supervised calendar correction — 2026-10-08

Status: P0 SCHEDULE IDENTITY CORRECTION — NO PERFORMANCE RERUN OR LIVE AUTHORITY.

The failed first block16 reconstruction exposed a calendar-layer mistake rather than a source-data mismatch. The long-history source was correctly verified from 2015-06-15, but the block16 reconstruction derived ordinal 2656 from raw OHLC dates. The adopted Action 36643183157 did not do that: `selected_calibration_walk_forward(z)` defines `dates` from `z["decision_date"].drop_duplicates()`.

The verified supervised cache starts on 2015-07-10 after feature warm-up. On that exact supervised calendar, the Action's emitted milestones are internally consistent: ordinal 640 = 2018-02-19 and ordinal 2656 = 2026-05-11, with block16 train end 2025-10-17 and calibration 2025-10-27 through 2026-04-29.

The code now keeps both identities separate:
- raw source identity/origin: exact 2015-06-15 long-history fingerprint;
- walk-forward schedule identity/origin: exact supervised `decision_date` calendar beginning 2015-07-10.

The block16 rehydrator obtains its schedule from the verified supervised parquet, while independently rechecking the raw-source fingerprint. The main prospective producer uses the same supervised-calendar origin and the already frozen Action milestones.

No thresholds, H5 horizon, 504/126/126 blocks, purge, q25, Top3, normal-market veto, cost rule, holdout state, Alpha admission, order authority or funds authority change.
