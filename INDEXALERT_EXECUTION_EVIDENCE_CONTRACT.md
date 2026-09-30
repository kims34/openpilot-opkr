# IndexAlert Execution Evidence Contract

Updated: 2026-09-30 KST
Branch: `index-alert-research-v1`
Status: **FROZEN EVIDENCE-CLASSIFICATION CONTRACT — NOT PROMOTION EVIDENCE**

## 1. Purpose

This contract prevents Shadow decisions, paper-broker executions and real-account executions from being conflated. It governs evidence classification only; it does not activate live ordering and does not change Alpha/statistical promotion gates.

## 2. Evidence tiers

### A. `PROSPECTIVE_SHADOW_DECISION_LOG`

- Operating mode: `SHADOW`.
- No broker order is submitted.
- May record frozen decision output, intended order, abstention/NO_TRADE and later market outcome diagnostics.
- Must **not** contain or claim broker `filled_qty`, broker fill timestamp, broker average fill price or broker partial-fill evidence.
- Must not be written to the broker execution-fill ledger.
- Cannot satisfy empirical execution blockers.

### B. `PROSPECTIVE_PAPER_EXECUTION_LOG`

- Operating mode: supported broker paper/simulation environment only.
- Records the paper broker's actual API/order-state response, including full/partial/no fill, timestamps, price and reconciliation state where the paper environment supplies them.
- Validates adapter, state-machine, idempotency, reconciliation and data-pipeline behavior.
- Is **not evidence of real-market fill quality, slippage, partial-fill probability or live capacity**.
- Paper observations may pass structural schema checks but cannot by themselves close empirical live-execution blockers.

### C. `PROSPECTIVE_LIVE_EXECUTION_LOG`

- Operating modes: `TINY_LIVE`, `LIMITED_LIVE`, later `LIVE` after their independent gates.
- Represents actual real-account broker order/execution observations.
- Is the only tier eligible to contribute to empirical live fill ratio/time/price, partial/no-fill behavior, slippage, markout, latency/expiry and later capacity evidence.
- Presence of one or more structurally valid LIVE rows is **not** sufficient for promotion. Sample sufficiency, tail/risk behavior, capacity, operational reliability, sealed holdout and prospective confirmation remain separate gates.

## 3. Forbidden source substitution

The following must be rejected from empirical broker-fill evidence:
- backtest-generated fills;
- synthetic/modelled fills;
- market-open assumptions relabelled as fills;
- Shadow would-be orders/fills;
- undocumented source strings;
- paper observations relabelled as live observations.

No missing fill may be imputed merely to make an evidence table complete.

## 4. Required fill semantics

For PAPER or LIVE broker execution rows:
- requested quantity > 0;
- filled quantity is in `[0, requested_qty]`;
- zero fill is a valid preserved observation;
- zero-fill rows cannot fabricate fill timestamps, fill price or post-fill markouts;
- filled rows require first/final fill timestamps, average fill price and the required markouts;
- fill cannot precede order submission;
- final fill cannot precede first fill;
- ingestion timestamp cannot precede the recommendation;
- source tier must be explicit.

## 5. Immutability and identity

Broker execution observations are immutable once written. A retry with the same stable observation identity may be idempotent only if the normalized payload is identical.

New execution observation identity must include the source tier so that PAPER and LIVE observations for an otherwise identical decision do not overwrite or collide with one another.

Historical rows written under the former source label `PROSPECTIVE_SHADOW_EXECUTION_LOG` must not be rewritten or deleted to manufacture cleaner evidence. They remain quarantined as `legacy_shadow_fill` and are excluded from live empirical-evidence claims.

## 6. Promotion interpretation

- Shadow evidence = prospective decision behavior only.
- Paper evidence = operational/broker-pipeline behavior only.
- Live evidence = potentially eligible empirical execution behavior, subject to separate sufficiency and risk gates.

No evidence tier changes the frozen statistical contract. In particular:
- q25 / TopK / costs / horizon are not relaxed because execution evidence is sparse;
- no sealed holdout is consumed to compensate for missing live execution data;
- technical broker connectivity does not authorize real-account trading;
- `promotion_ready` remains false unless the full Master Spec promotion path independently passes.

## 7. Current implementation state

The research integrity schema and production execution ledger are being aligned to this contract. Real-account ordering remains disabled. No synthetic execution observations may be inserted to populate the ledger.
