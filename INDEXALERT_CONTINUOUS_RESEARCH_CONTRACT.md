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
9. Caller-supplied booleans, labels, filenames, hashes, self-authored manifests or status strings are never promotion authority. A promotion-capable consumer must verify immutable outputs from the independent canonical gate auditors it relies on.

## Continuous triggers

Permitted research triggers include drift, calibration deterioration, execution-cost/slippage drift, feature decay, missingness/freshness changes, regime changes, new independently sourced PIT-safe data families, and explicitly proposed new hypotheses. A trigger creates a research queue item only; it does not change Core.

## Current boundary

This contract does not alter any existing H5/H10 disposition, KRX blocker, execution-sufficiency threshold, sealed-holdout status or live-order authorization. Current Core and all frozen contracts remain authoritative until a separately validated successor is explicitly promoted.

## Automated research orchestrator

`research_v1_research_orchestrator.py` may translate explicit, evidence-referenced diagnostic flags into deterministic `IDEA` queue items for calibration drift, execution-cost drift, feature freshness drift, regime drift and data-quality drift. Unknown/free-form flags and signals without an evidence reference are not queued. No signal means no research churn. Any sealed-holdout input fails closed. The orchestrator has no authority to execute a challenger, alter Core, change frozen thresholds, promote, open holdout, or authorize live orders.

## Successor Core auto-staging boundary

`research_v1_successor_core.py` permits deterministic automatic creation of a versioned `SHADOW_CANDIDATE` successor artifact only after an `ACCEPTED_CHALLENGER` also passes explicit independent OOS, cost-stress, tail-risk, recent-stability, PIT-integrity, no-leakage and frozen-protocol-match gates. Post-hoc criteria changes or sealed-holdout use at this stage block successor creation.

The resulting artifact is staging material only:
- `production_active=false`;
- `promotion_authority_granted=false`;
- `automatic_code_update_allowed=false`;
- `sealed_holdout_authorized=false`;
- `live_order_authorized=false`.

## Promotion-condition assessment is not promotion authority

`assess_shadow_promotion()` may receive caller-declared flags describing Shadow S1, Fresh Confirmation S2, sealed-holdout contract, external blockers and execution blocker state. Those flags are useful only for deterministic structural diagnostics. Even when every caller flag is `true`, the function must not infer that the underlying independent canonical auditors actually admitted the evidence.

Therefore, until a separate trusted promotion-authority adapter is implemented and bound to immutable outputs from the relevant canonical gate auditors:
- all caller conditions may at most yield `promotion_conditions_structurally_satisfied=true`;
- `promotion_eligible=false` remains mandatory;
- `independent_gate_admission_verified=false` remains mandatory;
- `promotion_authority_granted=false` remains mandatory;
- `automatic_code_update_allowed=false` remains mandatory;
- `automatic_live_order_activation_allowed=false` and `live_order_authorized=false` remain mandatory;
- `INDEPENDENT_GATE_ADMISSION_NOT_IMPLEMENTED` remains an explicit blocker.

A future promotion-authority adapter must be separately reviewed. It may not trust a caller-supplied `all_external_blockers_closed`, `execution_blocker_closed`, `sealed_holdout_contract_passed`, `shadow_s1_passed` or `fresh_confirmation_s2_passed` boolean as evidence. It must verify immutable, provenance-bound outputs produced by the authoritative source/execution/holdout/confirmation auditors. Until then, no automatic Core mutation is authorized by this contract.
