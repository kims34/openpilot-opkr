# Prospective model bundle boundary — 2026-10-07

Status: STRUCTURAL MODEL IDENTITY ONLY — NOT A SIGNAL, NOT ALPHA ADMISSION, NOT LIVE AUTHORITY.

The critical-path review found that prospective inputs existed without a durable identity for the fitted Ridge state and selection-conditioned calibration state that would later produce a real future decision. `research_v1_prospective_model_bundle.py` closes only that engineering gap.

The bundle is pickle-free and records the frozen feature order, median-imputer statistics, StandardScaler mean/scale, Ridge coefficients/intercept, calibration residual quantiles, exact training/calibration input fingerprints, fit-code commit/path, training/calibration cutoff dates, and an explicit caller-supplied refit-policy identifier. The entire canonical body is SHA-256 bound. A later scorer can reproduce the linear prediction without loading an opaque serialized estimator.

This module deliberately does **not** choose a refit cadence, fit the project model, authenticate the training/calibration data, admit KRX source evidence, generate a signal, record a decision, access the consumed v1 holdout, or submit an order. `independent_model_admission_verified`, `signal_generation_complete`, `decision_recorded`, `promotion_authority`, and `live_order_authorized` remain exact false.

The fixed identifiers bind this structural state to the current frozen H5 prospective diagnostic identity: `IA-FRESH-ALPHA-H5-TOP3-20261007`, `INDEXALERT-H5-FROZEN-DECISION-v1`, and the strict 0-to-3 selection-conditioned q25 / normal-market / no-backfill policy. These identifiers are identity constraints, not evidence that the underlying data or model is independently approved.

Next consequential step after this boundary is to connect one exact bundle plus one genuine current-session input snapshot to an append-only prospective scoring/decision-capture record while preserving separate source/model admission status and keeping MASTER_OFF.
