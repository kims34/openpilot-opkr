# Prospective decision capture boundary — 2026-10-07

Status: APPEND-ONLY STRUCTURAL FUTURE DECISION CAPTURE — NOT YET ADMITTED FRESH ALPHA EVIDENCE.

The critical path now has three separate artifacts: a label-free current-session input snapshot, a deterministic model/calibration bundle, and this decision capture. `build_decision_capture` reproduces the frozen Ridge prediction from explicit coefficients/scaler state, applies the frozen selection-conditioned residual quantiles, freezes the original positive-lower-bound Top3, and then applies the existing normal-market veto with no backfill. The complete ranking, original Top3, vetoed rows, selected 0..3 candidates and candidate NO_TRADE state are captured before outcomes.

Every record binds the exact input-snapshot SHA-256 and model-bundle SHA-256. Private storage is one immutable file per session with mode 0600, atomic no-overwrite publication and fsync. Identical retry is idempotent; a different later record for the same session cannot replace the first capture.

This closes only the engineering chronology/capture gap. File timestamps and caller-supplied source/model metadata are not independent proof of chronology or provenance. Therefore `independent_source_admission_verified`, `independent_model_admission_verified`, `independent_chronology_admission_verified`, `fresh_alpha_observation_admitted`, `formal_shadow_s1`, `fresh_confirmation_s2`, `promotion_authority`, `outcome_attached` and `live_order_authorized` all remain false. A captured candidate NO_TRADE is not counted as an admitted Fresh Alpha NO_TRADE until the exact capture receives independent source/model/chronology admission.

No historical replay, v1 holdout access, KRX network acquisition, broker action, permission change or funds movement is performed here. MASTER_OFF remains unchanged.

Next consequential work is the external-facing admission/capture connector: bind an official current-session source receipt and one approved exact model-bundle identity to this path, then schedule genuine future production-time capture. Until that connector exists and actually runs, no new prospective observation count is claimed.
