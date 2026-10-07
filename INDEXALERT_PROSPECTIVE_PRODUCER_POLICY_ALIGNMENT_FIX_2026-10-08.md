# Frozen prospective producer policy-alignment correction — 2026-10-08

Status: P0 CORRECTION BEFORE ANY REAL PROSPECTIVE MODEL FIT.

The first structural producer implementation correctly recovered the freeze-anchor 504/126/126 anchored expanding-WF block arithmetic, but it imported the older pre-alignment calibration helper from `research_v1_selected_calibration.py`.

That helper ranks each calibration day by predicted mean and estimates residual q25/q50/q75 from the frozen Top3 directly. The final H5 structural reference adopted before the Fresh Alpha freeze is the later policy-aligned calibration from `research_v1_policy_aligned_calibration.py`: freeze calibration Top3 by predicted mean, apply the same normal-market hard veto with no backfill, then estimate q25/q50/q75 from the surviving frozen rows.

The original policy-alignment Action 36643183157 confirms this identity and reports the calibration source string `calibration_daily_top3_by_pred_mean_then_same_normal_market_veto_no_backfill`. It also confirms the long-history origin 2015-06-15 and the latest frozen block boundaries used by the H5 reference.

This correction changes no threshold, feature, horizon, TopK, cost, result or promotion rule. It replaces the prospective producer's stale calibration helper with the adopted policy-aligned helper, changes the producer fit-code identity/refit-policy ID accordingly, and makes producer validation reject any model bundle whose global calibration source is not the adopted policy-aligned source.

No real/private model is fit in this change. No historical performance is recomputed, no consumed holdout is read, no KRX request is made and no trading authority changes.
