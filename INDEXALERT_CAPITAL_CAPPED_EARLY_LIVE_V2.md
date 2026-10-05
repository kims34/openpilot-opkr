# IndexAlert Capital-Capped Early-Live Protocol v2 — PREREGISTRATION DRAFT

Status: FROZEN-FOR-FUTURE-EVIDENCE ONLY; NOT CURRENT TRADING AUTHORITY
Protocol ID: INDEXALERT-CAPITAL-CAPPED-EARLY-LIVE-v2
Parent execution protocol: INDEXALERT-EXEC-SUFFICIENCY-v1

## Purpose
Define a future, separately governed capital-capped real-account validation stage so genuine execution evidence may be accumulated before the 200-distinct-date final execution-sufficiency window completes. This protocol does not weaken, replace, satisfy, or reinterpret any v1 promotion criterion.

## Non-retroactivity
This protocol cannot be applied to the consumed/invalid v1 sealed-holdout window, any already-observed outcome, or any evidence collected before this protocol is independently admitted. No cutoff, model, threshold, pass rule, or failed disposition may be changed because of this protocol.

## Preconditions before any real order
All must be independently true:
1. a separately admitted successor Alpha candidate has passed its preregistered statistical/PIT/OOS requirements;
2. required source/PIT/status-economics gates for that candidate are PASS;
3. Shadow validation for the exact decision/execution policy is complete and has no unresolved reconciliation/risk breach;
4. broker-native provenance capture, durable order journal, account snapshot/settlement, pretrade risk, cancel/reconnect and Kill enforcement are independently tested and fail-closed;
5. explicit user authorization is obtained immediately before enabling real-account ordering.

Until every precondition passes: EARLY_LIVE_AUTHORIZED=false.

## Capital/risk boundary
Early Live is a validation stage, not production promotion. A future activation must use a separately frozen hard KRW capital ceiling and loss/risk limits chosen before the first eligible real order. The ceiling is an upper bound, never a deployment target. NO_TRADE remains valid. Increasing the ceiling cannot relax any strategy, NetEV, liquidity, capacity, provenance, reconciliation or safety gate.

The exact numeric capital/loss/order limits are intentionally NOT selected in this draft. They must be frozen by an independent admission revision before any eligible observation, without using Early-Live outcomes.

## Evidence handling
Every eligible observation must retain broker-native order/execution identity, privacy-safe account fingerprint, timestamps, requested/fill quantities, unit fill prices, fees/tax evidence when available, reconciliation state, PIT decision inputs, policy IDs, capacity inputs and markouts required by the parent protocol. Missing/ambiguous evidence fails closed.

Early-Live observations may contribute to the future parent execution-sufficiency evidence window only if they independently satisfy the unchanged v1 provenance and eligibility contract. No synthetic, demo, paper or Shadow row may be relabelled LIVE.

## Relationship to frozen v1
The parent final criteria remain unchanged: >=600 genuine LIVE observations, >=200 distinct decision dates, >=400 fills, >=120 near-capacity observations and every existing fill/slippage/fee-tax/latency/reconciliation/risk/markout gate. Passing Early Live does not set empirical_execution_blocker_closed, promotion_ready, sealed_holdout_authorized or production_live_authorized.

## Current authority
capital_capped_early_live_authorized=false
real_orders_authorized=false
funds_movement_authorized=false
broker_permission_change_authorized=false
consumed_holdout_reuse_authorized=false

No code path may infer authority from the existence of this document.
