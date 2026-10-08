# Frozen prospective calendar reference correction — 2026-10-08

Status: P0 FAIL-CLOSED CORRECTION BEFORE ANY REAL PROSPECTIVE FIT.

The adopted policy-aligned calibration run (GitHub Actions run 36643183157) used a raw long-history panel beginning 2015-06-15, but the walk-forward function schedules folds from the supervised frame `z["decision_date"]`. Feature warm-up makes that supervised calendar begin on 2015-07-10. Its emitted anchored-WF test-block starts are part of the structural producer identity: supervised ordinal 640 = 2018-02-19, then every 126 supervised sessions through ordinal 2656 = 2026-05-11.

The existing Railway PIT volume is a different historical artifact. Its verified build summary begins 2018-01-02 and ends 2026-09-28. If that shorter calendar were passed directly to the prospective producer, ordinal 640 would be rebased around 2020 and every later train/calibration/test boundary would drift even though the numerical 504/126/126 parameters appeared unchanged.

This change prevents that silent rebase. The producer now requires the frozen long-history origin 2015-06-15 and validates every applicable historical test-block ordinal/date milestone emitted by the adopted policy-alignment run. The target-session calendar prefix is SHA-256 bound into the producer record. Producer validation also independently recomputes the block ordinal from the block index, the target ordinal from its in-block offset, and the expanding training span from the refit index.

The fit path now additionally requires every scheduled training and calibration session to be present in the supplied supervised frame, and every such session to retain label-available rows before fitting/calibration. A 2018-only panel therefore cannot silently create a structurally valid current model for the frozen 2015-origin policy.

This is a schedule/integrity correction only. It does not acquire missing 2015-2017 data, recompute historical performance, access the consumed v1 holdout, change H5/504-126-126/q25/Top3/cost rules, admit a model/source/Fresh-Alpha observation, or authorize any broker/order/funds action.

Remaining consequence: the automatic future runner must locate or independently rebuild the exact 2015-origin supervised history before a genuine prospective model bundle can be produced. The existing 2018-origin PIT volume alone is insufficient for that purpose.
