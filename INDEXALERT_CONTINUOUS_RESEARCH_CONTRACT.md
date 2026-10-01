# IndexAlert Continuous Research Governance Contract

Updated: 2026-10-02 KST
Branch: `index-alert-research-v1`

## Purpose

Keep research continuous after a Core version is frozen without allowing research outcomes to silently mutate the operating Core, sealed holdout, frozen execution protocol, costs, PIT rules, or promotion gates.

## Separation

- **CORE**: immutable released/frozen decision policy until a separately admitted successor is promoted.
- **RESEARCH_LAB**: may create challengers and diagnostics. It has no production write authority.
- **PROMOTION**: explicit gated state transition only. Research success never means deployment.

## Trial lifecycle

`IDEA -> PREREGISTERED -> RUNNING -> EVALUATED -> ACCEPTED_CHALLENGER | REJECTED | INVALIDATED`

An accepted challenger may proceed to separately required independent/prospective confirmation. It is not Core and cannot alter live execution.

## Fail-closed rules

1. Every evaluative trial is preregistered before outcomes are attached. The canonical JSON is SHA-256 fingerprinted.
2. Hypothesis, dataset window, PIT contract, target/horizon, primary metrics, acceptance criteria, cost assumptions and evaluation protocol are immutable for that trial after preregistration.
3. Changing any frozen field creates a **new trial_id**. Results from the old trial cannot validate the new protocol.
4. Sealed holdout data are forbidden from Research Lab discovery, tuning, threshold selection, feature selection and trial iteration.
5. Existing rejected candidates may not be revived by threshold, horizon, cost or subgroup mining. A materially new hypothesis requires a new preregistered trial and independent evidence.
6. Research Lab may automatically generate ideas, diagnostics and preregistrations, but may not automatically promote, deploy, enable live ordering, open the sealed holdout or weaken frozen gates.
7. Production/Core changes require an explicit successor version and all then-applicable source, execution, holdout, Shadow S1 and Fresh Confirmation S2 gates.
8. Missing/invalid protocol fields, fingerprint mismatch, results attached before preregistration, or forbidden holdout access invalidate the trial fail-closed.

## Continuous triggers

Permitted research triggers include drift, calibration deterioration, execution-cost/slippage drift, feature decay, missingness/freshness changes, regime changes, new independently sourced PIT-safe data families, and explicitly proposed new hypotheses. A trigger creates a research queue item only; it does not change Core.

## Current boundary

This contract does not alter any existing H5/H10 disposition, KRX blocker, execution-sufficiency threshold, sealed-holdout status or live-order authorization. Current Core and all frozen contracts remain authoritative until a separately validated successor is explicitly promoted.
