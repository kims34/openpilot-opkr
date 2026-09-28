# IndexAlert prospective shadow ledger

The served next-close model is the currently validated production model (`3.3-calibration-gated` at this release), protected by the prospective Brier serving gate.

Frozen challenger probabilities are recorded before the serving gate and before the target market open, stored separately from the public served value, and scored only after the target close becomes known. This prevents a fallback value from contaminating challenger evaluation and lets a raw candidate continue accumulating evidence even while the app is temporarily served the safer reference probability.

After at least 30 paired prospective outcomes for a serving stage, the candidate is served only when the 95% confidence interval for paired Brier gain is entirely above zero. Inconclusive or negative evidence falls back to that stage's reference probability while prospective recording continues, so a later recovery can be detected automatically.

The 60-session milestone report is informational only; it compares the current production model with frozen shadows and never auto-promotes a challenger.

The ledger uses `INDEXALERT_DB`; production persists it on the Railway `/data` volume.

## v4.0 delivery hardening (2026-09-28)

- The probability pipeline refreshes every 60 seconds on the server, independently of phone requests. Existing first-forecast immutability and the 60-session Firebase milestone remain active.
- HTTP reads return current daily probabilities immediately; one coalesced background worker updates timing-specific layers. Overlay caches expire after 120 seconds and are invalidated immediately at target, base-probability, and market-session boundaries.
- Forecast ledger model identity comes from each forecast payload, so concurrent KOSPI and US work never temporarily changes a shared global model identifier.
- A pre-open forecast first computed after its target open is excluded from prospective scoring.
- Smoke validation now checks the actually served 3.3 model instead of the obsolete 3.2 identifier.
