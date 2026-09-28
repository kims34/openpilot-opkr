# IndexAlert prospective shadow ledger

The served next-close model is the currently validated production model (`3.3-calibration-gated` at this release), protected by the prospective Brier serving gate.

Frozen challenger probabilities are recorded before the serving gate and before the target market open, stored separately from the public served value, and scored only after the target close becomes known. This prevents a fallback value from contaminating challenger evaluation and lets a raw candidate continue accumulating evidence even while the app is temporarily served the safer reference probability.

After at least 30 paired prospective outcomes for a serving stage, the candidate is served only when the 95% confidence interval for paired Brier gain is entirely above zero. Inconclusive or negative evidence falls back to that stage's reference probability while prospective recording continues, so a later recovery can be detected automatically.

The 60-session milestone report is informational only; it compares the current production model with frozen shadows and never auto-promotes a challenger.

The ledger uses `INDEXALERT_DB`; production persists it on the Railway `/data` volume.
