# IndexAlert KRX Status Economics Contract

Updated: 2026-10-01 KST  
Branch: `index-alert-research-v1`  
Status: **FROZEN FINAL-JUDGE INPUT CONTRACT — NO PROMOTION / HOLDOUT / LIVE AUTHORITY**

## 1. Purpose

Final Judge requires exact halt/delisting economics. Structural status-event consistency, daily OHLC, a cleanup-trading window, a delisting date or a delisted-security price series is not by itself exact economic evidence for an IndexAlert position.

This contract governs positions affected by `HALT`, `CLEANUP_TRADING` or `DELISTING` events and prevents the research pipeline from inventing fillability, fill prices, recovery values, fees/taxes or missing rows.

Executable semantics live in `research_v1_krx_status_economics.py`.

## 2. Independently attested affected-position scope

The complete set of candidate/position rows affected by official status events must be derived and independently audited before economic closure is evaluated.

The audit receives this as `expected_positions` and requires `expected_scope_attested=true`.

Rules:
- an empty affected-position set is acceptable only when that empty set is independently attested from complete candidate/position history plus complete official status-event coverage;
- absence of observed problem rows must never be interpreted as proof that the affected-position set is empty;
- missing or extra economic-evidence position IDs fail closed;
- duplicate position IDs fail closed;
- symbol, event type, affected quantity and source-contract identity must agree between expected scope and economics evidence.

## 3. Quantity conservation

For every affected position:

`affected_qty = verified_exit_fill_qty + verified_recovery_qty`

Any unresolved quantity or over-resolved quantity blocks `exact_status_economics_ready`.

No missing fill or recovery quantity may be imputed.

## 4. Exact fill evidence

Positive `verified_exit_fill_qty` requires:
- a positive verified average fill price;
- a non-empty immutable evidence reference;
- an accepted exact execution source.

Currently accepted exact fill evidence classes are:
- `PROSPECTIVE_LIVE_EXECUTION_LOG` — actual real-account broker execution evidence;
- `BROKER_HISTORICAL_EXECUTION_RECORD` — an actual broker historical execution record for the position.

The following are explicitly insufficient for exact fill economics:
- backtest-generated fills;
- synthetic/modelled fills;
- next-open or market-open assumptions;
- Shadow decisions;
- Paper execution observations;
- daily OHLC;
- MDCSTAT239 daily price rows by themselves.

Paper evidence may validate plumbing; it does not prove real-market fill quality. A quoted/traded market price is not proof that an IndexAlert order filled at that price.

## 5. Recovery evidence

Positive `verified_recovery_qty` requires a non-empty immutable evidence reference and an accepted recovery source.

Accepted recovery evidence classes are:
- `OFFICIAL_KRX_RECOVERY_RECORD`;
- `OFFICIAL_ISSUER_RECOVERY_RECORD`;
- `BROKER_CASH_DISTRIBUTION_RECORD`.

A verified zero recovery value is permitted only when supported by an accepted recovery record. Zero is never inferred from silence, delisting alone or missing price data.

## 6. Explicit costs and economic result

Fees/taxes must be supplied explicitly and must be non-negative. They are never silently set from an unrelated generic cost assumption inside this audit.

For structurally matched evidence the audit may compute:

`verified_fill_cash = verified_exit_fill_qty × verified_exit_avg_price`

`verified_recovery_cash = verified_recovery_qty × verified_recovery_cash_per_share`

`verified_net_exit_cash = verified_fill_cash + verified_recovery_cash - explicit_fees_taxes_total`

`exact_net_return = (verified_net_exit_cash - entry_cost_basis_total) / entry_cost_basis_total`

These values are evidence-derived diagnostics only. They do not promote a model and must not be used when the surrounding audit is invalid.

## 7. PIT and contract lineage

Every economic observation requires timezone-aware `economic_available_at` evidence and the same source-contract fingerprint as its independently expected affected-position record.

Naive/missing timestamps or source-contract mismatch block exact economics.

## 8. Closure semantics

`exact_status_economics_ready=true` requires all of:
- independently attested expected affected-position scope;
- exact expected/observed position coverage;
- quantity conservation for every affected position;
- no unresolved quantity;
- accepted exact fill evidence for every filled quantity;
- accepted recovery evidence for every recovery quantity;
- explicit cost accounting;
- valid PIT availability lineage;
- matching source-contract identity.

Even when true, this is only one Final-Judge input. It deliberately keeps:
- `judge_security_status_ready=false` by itself;
- `feature_performance_testing_authorized=false`;
- `sealed_holdout_authorized=false`;
- `alpha_or_final_judge_promotion_authorized=false`;
- `live_trading_authorized=false`.

All KRX A-F, longer-history, statistical, execution, tail-risk, sealed-holdout and prospective confirmation gates remain independent.

## 9. Current state

The fail-closed auditor and tests are implemented, but no real complete affected-position economics dataset has been supplied. Therefore the project-level exact halt/delisting economics blocker remains open.

The implementation must not be described as evidence that historical status economics are already complete.
