# IndexAlert Broker Execution Contract — Future Live Trading Boundary

Updated: 2026-10-02 KST
Branch: `index-alert-research-v1`
Status: **ARCHITECTURE CONTRACT ONLY — LIVE ORDERING DISABLED**

This document defines the future broker/execution boundary without changing the current Alpha research priority. It is intentionally implementation-light until the prediction/selection engine has passed the required external validation sequence.

## 1. Priority and activation rule

Current KOSPI prediction/selection research and statistical validation remain the highest priority.

Broker automation must not delay, contaminate, weaken or restructure current research/backtest/validation work merely to make live trading possible.

Current phase requirements:
- keep prediction outputs and portfolio decisions broker-agnostic;
- keep data structures compatible with a future broker adapter;
- do not activate real-account ordering;
- do not implement Kiwoom-specific trading logic inside the Alpha model or selection engine;
- do not consume sealed holdout evidence to justify broker integration.

The required promotion sequence is:

`Research / Backtest -> Shadow -> Kiwoom Paper API -> Tiny Live -> Limited Live -> Production`

No stage may be skipped because an API connection is technically available.

## 2. Architectural separation

The system is split into independent layers:

1. **Prediction / Alpha Engine**
   - produces forecasts, uncertainty and candidate ranks;
   - has no broker credentials and sends no orders.

2. **Decision / Portfolio Policy**
   - produces broker-neutral intents: `BUY`, `HOLD`, `EXIT`, `REPLACE`, `NO_TRADE`;
   - applies frozen admission policy, abstention, portfolio/risk constraints and recommendation freshness.

3. **Pre-Trade Health Gate**
   - rechecks latest market/account/system state immediately before any executable intent;
   - requires prediction freshness, executable NetEV, liquidity/capacity, risk limits, market tradability and account/orderability.

4. **Broker Adapter Interface**
   - broker-neutral interface for authentication/session state, quotes/status, account/balance, order submission, order query, amend/cancel and executions;
   - Kiwoom will be one adapter implementation, not part of Core Alpha logic;
   - future brokers must be addable without changing the model/selection engine.

5. **Order State / Reconciliation Engine**
   - owns order lifecycle, idempotency, partial fills, cancel/replace races and reconciliation;
   - actual broker state is authoritative when internal state disagrees;
   - any unresolved mismatch forces new automated orders to fail closed.

6. **Execution Evidence / PnL Ledger**
   - records actual requested/filled quantities, timestamps, prices, fees/tax/slippage, markout and realised/unrealised PnL;
   - preserves empirical evidence separately from backtest assumptions.

## 3. Operating modes

The execution service must expose an explicit mode with deny-by-default semantics:

- `MASTER_OFF` — no automatic order submission of any kind.
- `SHADOW` — decisions and hypothetical order state are recorded; no broker order submission.
- `PAPER` — only supported paper/simulation broker environment may receive orders.
- `TINY_LIVE` — real account enabled only under deliberately tiny hard limits.
- `LIMITED_LIVE` — bounded real trading under explicit independent limits.
- `LIVE` — production mode, available only after all promotion gates and explicit user activation.

Default is `MASTER_OFF` unless explicitly configured otherwise. Restart, configuration failure, missing secret, unknown mode, stale state or reconciliation failure must not silently promote the mode.

## 4. Decision-to-order gate

A model `BUY` is never sufficient by itself to submit an order.

Immediately before submission, all of the following must pass:
- system and broker-session health;
- fresh prediction / recommendation TTL;
- current executable NetEV remains positive under current price/cost assumptions;
- liquidity and empirical/approved capacity limits;
- symbol security/status is tradable;
- market session, halt, VI/price-limit and holiday constraints;
- account buying power / orderable cash;
- actual broker holdings and open orders;
- position, portfolio and loss limits;
- no duplicate/idempotency collision;
- no unresolved reconciliation discrepancy;
- operating mode permits the requested class of order.

Failure of any required gate produces `NO_ORDER` / fail-closed behavior.

## 5. Order state model

Broker-neutral intents:
- `BUY`
- `HOLD`
- `EXIT`
- `REPLACE`
- `NO_TRADE`

Minimum order lifecycle states:
- `INTENT_CREATED`
- `PRETRADE_BLOCKED`
- `SUBMITTING`
- `SUBMITTED`
- `ACKNOWLEDGED`
- `PARTIALLY_FILLED`
- `FILLED`
- `UNFILLED`
- `REJECTED`
- `CANCEL_REQUESTED`
- `CANCEL_ACKNOWLEDGED`
- `CANCELLED`
- `AMEND_REQUESTED`
- `AMENDED`
- `RECONCILIATION_REQUIRED`
- `CLOSED`

Transitions must be event-driven and auditable. Broker responses/events, local request IDs, broker order IDs and timestamps must be retained so that retrying after timeout or reconnect cannot blindly duplicate an order.

## 6. Idempotency and race safety

Each executable intent must receive an immutable idempotency key derived from stable decision/order identity, not from a retry attempt.

Required safeguards:
- repeated submit calls with the same key must not create independent economic orders;
- timeout is treated as **unknown outcome**, not automatic failure; query broker state before retry;
- cancel and fill events may cross; final quantity derives from authoritative executions;
- remaining quantity after partial fill is explicit;
- amend/cancel commands require current order version/state;
- abnormal repeated-order patterns trip an independent circuit breaker;
- reconnect restores open-order and position state before allowing new automated orders.

## 7. Reconciliation authority

At startup, reconnect and periodically during an enabled session, reconcile:
- cash / buying power;
- positions and available quantity;
- open orders;
- executions/fills;
- fees/taxes where available;
- internal portfolio and realised PnL ledger.

If internal state conflicts with Kiwoom/broker state, the **actual broker/account state wins**. The discrepancy must be recorded, internal state repaired or quarantined, and new automatic orders blocked until reconciliation succeeds.

## 8. Independent safety limits

Risk controls must be independent of the model signal and independently configurable by mode.

At minimum:
- daily maximum realised/unrealised loss;
- maximum value per symbol;
- maximum total invested/gross exposure;
- maximum simultaneous positions;
- maximum value per order;
- abnormal repeated-order / retry limit;
- stale-model / stale-data cutoff;
- broker/API error threshold;
- reconciliation discrepancy breaker;
- emergency global Kill Switch.

A risk limit may veto an order but may not increase model conviction or manufacture Alpha.

## 9. Failure handling

Explicit handling is required for:
- API timeout / uncertain submit result;
- network interruption and reconnect;
- token/session expiration;
- API rate limiting;
- partial fill and residual quantity;
- rejection;
- market holiday / closed session;
- VI / trading halt / price-limit conditions;
- insufficient orderable funds;
- insufficient actual holdings for exit/cancel-replace;
- stale quote / stale prediction;
- duplicated event delivery;
- out-of-order broker events.

Unknown or contradictory state fails closed for new automatic orders.

## 10. Secrets and audit security

API Key, Secret, account authentication material, access/refresh tokens and equivalent credentials must never be committed to source control or stored in GitHub artifacts, logs or plaintext application/database fields.

Use environment/secret-manager injection appropriate to the deployment platform, minimum required scopes, key rotation and redacted structured logging. Audit logs may retain non-secret identifiers required to reconstruct order lifecycle.

## 11. Kiwoom REST implementation gate

Kiwoom integration must be implemented as a dedicated `BrokerAdapter` only when the research/promotion state reaches the appropriate stage.

Current safe preparation is governed by `INDEXALERT_KIWOOM_REST_READINESS_CONTRACT.md`. The 2026-10-02 review of the official `Kiwoom-Securities/Kiwoom-REST-API` schema permits only read-only/demo connectivity preparation, secret-safe configuration design, offline evidence mapping and fail-closed tests. It does **not** authorize real-account ordering or admit demo/paper observations as genuine LIVE evidence.

At the actual implementation start, re-read the **then-current official Kiwoom Securities REST API documentation** and validate at least:
- production vs paper/simulation environment support;
- authentication/token lifecycle;
- account and balance interfaces;
- order / amend / cancel schemas;
- order-status and execution events/query behavior;
- market/status endpoints needed for pre-trade checks;
- documented rate limits and retry expectations;
- error codes and uncertain-result semantics.

Do not implement endpoints, fields, limits or environment behavior from remembered or old API specifications.

## 12. Promotion gates

### Research / Backtest -> Shadow
Requires the Alpha/decision candidate to reach the research gate defined by the Master Spec and be frozen enough to observe prospectively without outcome-driven retuning.

### Shadow -> Kiwoom Paper
Requires prospective decision/execution logging, stable reconciliation/state-machine tests and no unresolved order-safety defects. Paper trading must not be presented as evidence of live fill quality.

### Paper -> Tiny Live
Requires explicit user activation plus validated official API behavior, secrets handling, idempotency, reconciliation, Kill Switch and hard tiny-notional risk limits. Statistical promotion requirements remain independent.

### Tiny Live -> Limited Live
Requires sufficient real execution evidence for fill ratio/time/price, partial fills, slippage/fees/tax, markout, latency/expiry, operational reliability and loss controls under tiny live exposure.

### Limited Live -> Production
Requires all Final Judge/statistical gates, live execution evidence, operational stability and explicit user activation. Technical connectivity alone can never authorize Production.

## 13. Current disposition

**Do not start real-order implementation now.**

Current work remains on the research/data/execution-evidence blockers defined by `INDEXALERT_MASTER_SPEC.md`, `INDEXALERT_RESEARCH_LEDGER.md` and `INDEXALERT_CONTINUITY_SNAPSHOT.md`.

Only maintain broker-neutral interfaces/data compatibility and the explicitly read-only/demo readiness work permitted by `INDEXALERT_KIWOOM_REST_READINESS_CONTRACT.md` until the promotion state makes broader Kiwoom integration appropriate.

## 14. Default user-control surface

The future consumer UX must follow `INDEXALERT_AUTOMATION_UX_CONTRACT.md`.

After broker connection, routine user controls are intentionally restricted to:
- automated operation enabled / disabled; and
- maximum automated-operation capital in KRW.

Stop-loss %, take-profit %, holdings count, per-symbol weights, holding period, entry threshold, replacement and re-entry rules are not routine user settings. They are engine-owned decisions governed by the validated Decision / Risk / Execution policies.

The user's capital input is a hard ceiling, not a target. The engine may retain any fraction of it as cash, including 100%. `NO_TRADE` must remain valid whenever expected-return/risk/execution requirements are not met.

Before any new exposure, conservative committed-capital accounting must include current automated positions, reserved open buy orders, partial-fill residual exposure, uncertain submissions and applicable cash buffers. A plan is forbidden if projected committed automated capital would exceed the user ceiling.

The user retains explicit authority to enable/disable automation, use the Kill Switch and set the capital ceiling. Internal safety limits remain mandatory and may be stricter than the user ceiling, but they are not intended to become expert configuration knobs in the default UX.
