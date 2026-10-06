# IndexAlert Early-Live Readiness Gate v1

Status: IMPLEMENTATION GATE ONLY — NO REAL-ORDER AUTHORITY

This gate converts the existing capital-capped Early-Live preregistration into an executable fail-closed readiness checklist. It does not authorize a broker request, funds movement, account-permission change, or genuine-LIVE admission.

## Required state before user activation can even be requested

All items must be independently PASS:

- successor_alpha_admitted
- source_pit_status_economics_pass
- exact_policy_shadow_complete
- unresolved_reconciliation_count == 0
- risk_breach_count == 0
- durable_order_journal_pass
- broker_native_provenance_capture_pass
- account_snapshot_settlement_pass
- pretrade_risk_pass
- cancel_reconnect_kill_pass
- numeric_capital_limits_frozen
- broker_environment_real_account_attested
- user_activation_pending

Any missing/unknown value fails closed. The final user activation is deliberately not represented as a pre-authorized boolean: it must be obtained immediately before the first real-account order path is enabled.

## Invariants

- Parent execution-sufficiency v1 remains unchanged: >=600 genuine LIVE observations, >=200 distinct decision dates, >=400 fills, >=120 near-capacity observations plus all existing uncertainty/latency/reconciliation/risk/markout gates.
- Shadow/demo/paper evidence cannot be relabelled LIVE.
- Early-Live evidence may count only when independently eligible under the parent provenance/evidence contracts.
- Capital ceiling is an upper bound, never a utilization target.
- NO_TRADE remains valid.
- Restart, uncertain submission, unresolved reconciliation, stale account snapshot, Kill, or policy mismatch returns the path to OFF.
- No automatic real-order submission code is introduced by this gate.
