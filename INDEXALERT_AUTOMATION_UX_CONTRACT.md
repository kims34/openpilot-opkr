# IndexAlert Automated Operation UX Contract

Updated: 2026-09-30 KST
Status: **FROZEN PRODUCT/CONTROL CONTRACT — LIVE ORDERING STILL DISABLED**

This contract defines the intended end-user control surface for future IndexAlert automated operation. It does not authorize live trading and does not weaken any statistical, execution, broker, holdout or promotion gate in `INDEXALERT_MASTER_SPEC.md`.

## 1. Product goal

The default automated-trading UX must minimize user configuration. After the user connects an eligible Kiwoom account, the normal user-facing controls are limited to:

1. **Automated operation enabled / disabled**; and
2. **Maximum automated-operation capital (KRW)**.

The user must not be required to configure professional trading parameters such as stop-loss %, take-profit %, number of holdings, per-symbol allocation, entry threshold, holding period, replacement rules, re-entry rules, order type, model threshold or portfolio cash target.

Those decisions belong to the validated IndexAlert Decision / Risk / Execution Engine under frozen policies and safety gates.

## 2. Maximum capital is a hard ceiling, not an investment target

`max_automation_capital_krw` is an absolute upper bound on capital that the automated engine may place at risk or commit through open orders/positions under the product's accounting rules.

It is **not** a target allocation and must never create pressure to invest unused cash.

Therefore:
- invested capital may be anywhere from 0 KRW up to the permitted maximum;
- unused capital remains cash by default;
- if no candidate satisfies the frozen expected-return, uncertainty, tail-risk, liquidity, capacity, tradability and execution requirements, the correct decision is `NO_TRADE`;
- the engine must not lower admission standards, add lower-ranked symbols, increase position size or force replacement merely to use the available maximum capital.

## 3. Engine-owned decisions

Once automated operation is enabled, and only after all promotion and pre-trade gates are satisfied, the engine owns the following decisions without asking the user to set them manually:

- candidate selection;
- whether to enter at all;
- actual order quantity and allocation below the hard capital ceiling;
- how much cash to retain;
- simultaneous position count within internal risk limits;
- entry timing and execution policy;
- holding period;
- hold / exit / replace decisions;
- partial-fill handling;
- re-entry eligibility;
- whether to remain entirely in cash.

The engine may choose 0..N positions only within the currently validated portfolio policy. `NO_TRADE` and 100% cash are first-class valid states.

## 4. User authority that must remain explicit

The user retains final control over:

- connecting/disconnecting the broker account;
- enabling automated operation;
- disabling automated operation / Kill Switch;
- setting or lowering the maximum automated-operation capital;
- explicitly increasing the maximum capital when desired.

A user-requested disable must prevent creation of new automated orders. Existing orders/positions must then follow the separately specified safe-stop/reconciliation behavior; disabling automation must not silently create discretionary new exposure.

Any increase of the maximum capital is a user-authorized ceiling change only. It does not authorize immediate investment and does not change the engine's admission thresholds or risk standards.

## 5. Internal risk controls remain mandatory but are not routine UX knobs

Independent safety controls defined by the Broker Execution Contract remain mandatory, including daily-loss limits, per-symbol limits, total exposure limits, order limits, duplicate-order breakers, stale-data/model cutoffs, reconciliation blockers and emergency stop behavior.

These are engine/system safety constraints. The default consumer UX must not require the user to understand or manually tune them. Internal limits may be stricter than the user's maximum capital and therefore may reduce deployable capital further.

## 6. Fail-closed rules

The following must resolve to no new automated order:

- automation disabled;
- broker/account connection unavailable or unresolved;
- stale or invalid prediction/data;
- non-positive conservative executable NetEV;
- risk/tail/liquidity/capacity/tradability gate failure;
- unresolved holdings/open-order reconciliation;
- insufficient orderable cash;
- order would cause committed automated capital to exceed the user maximum;
- unknown or contradictory broker/order state.

No failure may be converted into a fallback trade merely to keep capital invested.

## 7. Capital accounting contract

Before any future live-capable implementation, a single broker-neutral definition of `committed_automation_capital_krw` must be frozen and tested. At minimum it must account for:

- current marked value or approved conservative value of automated positions;
- cash reserved for acknowledged/open automated buy orders;
- remaining quantity on partial fills;
- duplicate/idempotency-safe treatment of uncertain submissions;
- fees/tax/required cash buffers where economically applicable.

Pre-trade sizing must guarantee:

`projected_committed_automation_capital_krw <= max_automation_capital_krw`

under conservative order-state assumptions.

## 8. Account separation and scope

The engine may act only on positions/orders explicitly attributed to IndexAlert automated operation. Pre-existing/manual holdings must not be silently adopted, sold, resized or used to increase available automation capacity unless a future separately explicit product contract authorizes that behavior.

Broker state remains authoritative for reconciliation.

## 9. Promotion boundary

This UX contract is architecture preparation only. Current research blockers remain unchanged.

Required progression remains:

`Research / Backtest -> Shadow -> Kiwoom Paper API -> Tiny Live -> Limited Live -> Production`

Real-account ordering stays disabled until the relevant statistical, execution-evidence, broker/API, reconciliation, security and explicit user-activation gates are passed.
