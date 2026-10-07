# Frozen supervised-cache rehydration — 2026-10-08

Status: EXACT FROZEN FEATURE/LABEL CACHE RECONSTRUCTION ONLY — NO PERFORMANCE RERUN, NO MODEL FIT, NO ALPHA/LIVE AUTHORITY.

The exact 2015-origin long-history source has already been reconstructed on the Railway PIT volume and matched Action 36643183157 byte-semantically at the source-fingerprint boundary: 2,512,128 rows, 1,089 symbols, 2015-06-15 through 2026-09-23, with the exact recovered pandas hash XOR/sum.

The same Action artifact also retained the complete `supervised_cache` metadata object. This change vendors the exact five-module dependency closure from Action head `4df26b6f5d2d9e645cd2c0242c9ac8cefb747a9d` and will rebuild only the expensive feature/label/DecisionRecord cache. Four of those files are still unchanged in current development; the cache wrapper itself later changed, so the exact frozen version is intentionally isolated under `pit_rebuild/frozen_supervised_v1`.

Publication requires exact equality to the recovered Action values, not tolerance:

- cache version: `pit-supervised-cache-v3-ca-safe-source-fingerprint`;
- supervised rows: 2,486,909;
- DecisionRecord rows: 2,484,241;
- same-bar ambiguity: 55,604;
- entry no-fill retained in decision universe: 2,668;
- post-entry missing-future-bar conservative stop: 7,274;
- insufficient global future horizon: 4,561;
- all statutory sell-tax + commission count buckets;
- the complete corporate-action return-gap diagnostics;
- exact source fingerprint and all frozen H5 label/cost parameters.

The one-shot builder reads only the already verified long-history panel, writes into a separate attempt directory, and atomically publishes `/pit/supervised_frozen_verified_36643183157` only after the entire recovered metadata/diagnostics object matches exactly. A logical whole-frame fingerprint and parquet/meta SHA-256 values are then recorded for prospective model identity.

This step does not read the consumed holdout artifact, calculate any performance metric, fit any model, create retrospective decisions, admit Fresh Alpha evidence, promote anything, or authorize a live order.
