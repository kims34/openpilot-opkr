# IndexAlert Empirical Execution Sufficiency Protocol v1

Frozen: 2026-10-01T23:52:00+09:00  
Branch authority: `index-alert-research-v1`  
Protocol ID: `INDEXALERT-EXEC-SUFFICIENCY-v1`  
Status: **FROZEN BEFORE ANY GENUINE LIVE OBSERVATION — NOT PROMOTION EVIDENCE**

## 1. Purpose

This protocol preregisters the minimum evidence and pass/fail rules for closing the empirical execution blocker. It is intentionally frozen before any genuine `PROSPECTIVE_LIVE_EXECUTION_LOG` observation is used for evaluation so the thresholds cannot be selected after seeing live outcomes.

Passing this protocol would close only the empirical execution-evidence blocker. It does **not** authorize sealed-holdout consumption, model promotion, broker stage advancement, or live trading. KRX source/status, PIT, statistical, holdout, Shadow S1, Fresh Confirmation S2 and explicit live-mode gates remain independent.

Unit-test or synthetic rows may exercise the evaluator but are never eligible evidence.

## 2. Evidence identity and scope

The evaluated evidence window must use one frozen decision policy and one frozen execution policy:

- `decision_policy_id = INDEXALERT-H5-FROZEN-DECISION-v1`
- `execution_policy_id = INDEXALERT-LIVE-EXECUTION-v1`
- accepted source = `PROSPECTIVE_LIVE_EXECUTION_LOG` only
- required markouts = `5m`, `30m`, `close`

Paper, Shadow, backtest, modelled, imputed or relabelled observations are excluded.

## 3. Minimum sample before assessment may pass

- minimum LIVE observations: **600**
- minimum distinct decision dates: **200**
- minimum filled observations: **400**
- minimum no-fill observations: **0**
- minimum partial-fill observations: **0**

The last two minima are deliberately zero: a genuinely low no-fill or partial-fill rate must not be forced to manufacture adverse events. Their rates are instead bounded with 95% Wilson upper confidence limits.

## 4. Capacity scope

The developmental cost model uses a fixed participation assumption of `0.0005` of 20-day ADV (0.05%). Empirical capacity evidence therefore cannot claim a larger scope.

- maximum permitted requested participation: **0.0005** of decision-time PIT ADV20
- near-capacity floor: **80%** of that ceiling = `0.0004`
- minimum near-capacity observations: **120**
- near-capacity mean fill-ratio 95% date-cluster LCB: **>= 0.85**
- near-capacity mean excess entry slippage 95% date-cluster UCB: **<= 0.0 bps** relative to the preregistered per-order entry-slippage budget

Any observation above `0.0005` is a capacity-scope breach for this protocol, not evidence supporting a larger capacity claim.

## 5. Fill-quality gates

Across all LIVE observations:

- mean fill-ratio 95% date-cluster LCB: **>= 0.90**
- no-fill-rate 95% Wilson UCB: **<= 0.10**
- partial-fill-rate 95% Wilson UCB: **<= 0.20**

Zero-fill rows remain in the denominator. No missing fill may be imputed.

## 6. Slippage and explicit-cost gates

Every filled order must carry the entry-slippage budget that was available before the recommendation/order and the modelled/actual fee-tax record.

- mean `(actual entry slippage - entry slippage budget)` 95% date-cluster UCB: **<= 0.0 bps**
- p95 of `max(actual entry slippage, 0) / entry slippage budget`: **<= 2.0x**
- p99 of that ratio: **<= 3.0x**
- mean `(actual fees/tax - modelled fees/tax)` 95% date-cluster UCB: **<= 1.0 bp**

These gates test whether the frozen execution allowance is conservative enough instead of choosing a new cost allowance after seeing LIVE results.

## 7. Latency, expiry, reconciliation and risk-integrity gates

- p95 submit latency / recommendation-TTL fraction: **<= 0.20**
- p95 first-fill latency / order-expiry-window fraction: **<= 0.80** for filled orders
- zero submissions after recommendation expiry
- zero first fills after order expiry
- zero requested-participation breaches
- zero unknown order outcomes
- zero unresolved reconciliation rows
- zero risk-limit-breach rows

Unknown or contradictory broker state fails closed.

## 8. Markout and adverse-selection gate

All filled observations require complete 5m, 30m and close markouts. The evaluator must report date-cluster means/95% intervals and adverse-tail ES95/ES99 for all three horizons.

The hard short-horizon adverse-selection gate is:

- 5m date-cluster 95% LCB of `(5m markout + entry slippage budget)` **>= 0.0 bps**.

The 30m and close markouts remain mandatory reported evidence but are not turned into an Alpha proxy. Their values do not override a failed 5m execution gate, and positive markouts cannot manufacture model promotion.

## 9. PIT and provenance requirements

Capacity ADV20 and cost-budget timestamps must be no later than the recommendation timestamp. Required live evidence metadata include stable observation identity, policy IDs, recommendation/order expiry timestamps, order-outcome timestamp, decision-time ADV20 and its availability timestamp, per-order entry-slippage budget and timestamp, modelled/actual fees/tax, reconciliation state, unknown-outcome flag and risk-limit-breach flag.

Duplicate observation IDs fail closed. A mixed policy window fails closed.

## 10. Statistical conventions

- Continuous mean gates use deterministic date-cluster bootstrap intervals, clustered by `decision_date`, so multiple symbols on one day are not treated as independent days.
- Event-rate gates use 95% Wilson intervals.
- Tail summaries use the worst-cost / most-adverse 5% and 1% empirical tails (`ES95`, `ES99`) without pretending that a small sample has high-resolution tail precision.
- Passing requires all gates simultaneously; no compensating score or weighted average is allowed.

## 11. Frozen interpretation

A valid preregistration plus a future passing genuine LIVE assessment may set `empirical_execution_blocker_closed=true` for this execution protocol only. It must still leave `promotion_ready=false`, `sealed_holdout_authorized=false` and `live_trading_authorized=false` until the independent Master Spec gates are satisfied.

Thresholds may not be weakened using outcomes from the evidence window they judge. Any future protocol revision must receive a new protocol ID, document fingerprint and evidence window beginning strictly after that revision was frozen.
