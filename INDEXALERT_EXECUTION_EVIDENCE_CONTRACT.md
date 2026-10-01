# IndexAlert Execution Evidence Contract

Updated: 2026-10-01 KST
Branch: `index-alert-research-v1`
Status: **FROZEN EVIDENCE-CLASSIFICATION CONTRACT — NOT PROMOTION EVIDENCE**

## 1. Purpose

This contract prevents Shadow decisions, paper-broker executions and real-account executions from being conflated. It governs evidence classification only; it does not activate live ordering and does not change Alpha/statistical promotion gates.

A second boundary is equally important: **structurally valid LIVE rows are not the same thing as sufficient empirical execution evidence.** One or a few real-account fills may demonstrate that the execution ledger works, but cannot by themselves close the empirical execution blocker.

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
- Presence of one or more structurally valid LIVE rows is **not** sufficient for promotion and does **not** close the empirical execution blocker. Sample sufficiency, tails, capacity, operational reliability, sealed holdout and prospective confirmation remain separate gates.

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

## 5. Structural LIVE evidence vs empirical sufficiency

`research_v1_execution_evidence.py` must distinguish these concepts explicitly.

A structurally valid LIVE filled row with required markouts may set:
- `contains_live_execution_evidence=true`;
- `live_structural_execution_evidence_present=true`.

It must **not** merely from that fact set:
- `live_empirical_execution_evidence_ready=true`;
- `empirical_execution_blocker_closed=true`;
- `promotion_ready=true`.

Until a separate preregistered execution-sufficiency protocol is frozen and evaluated, the implementation must keep:
- `live_empirical_execution_evidence_ready=false`;
- `empirical_execution_sufficiency_assessed=false`;
- `empirical_execution_blocker_closed=false`.

No numeric sample threshold may be invented after observing the live outcomes merely to obtain a pass. Any future sufficiency protocol must be separately frozen before it is used as a promotion input and must cover the relevant dimensions in the Master Spec, including live fill/no-fill/partial-fill behavior, fill time/price, slippage, markouts, latency/expiry, capacity and adverse/tail conditions.

## 6. Immutability and identity

Broker execution observations are immutable once written. A retry with the same stable observation identity may be idempotent only if the normalized payload is identical.

New execution observation identity must include the source tier so that PAPER and LIVE observations for an otherwise identical decision do not overwrite or collide with one another.

Historical rows written under the former source label `PROSPECTIVE_SHADOW_EXECUTION_LOG` must not be rewritten or deleted to manufacture cleaner evidence. They remain quarantined as `legacy_shadow_fill` and are excluded from live empirical-evidence claims.

## 7. Promotion interpretation

- Shadow evidence = prospective decision behavior only.
- Paper evidence = operational/broker-pipeline behavior only.
- Structurally valid Live evidence = eligible raw empirical observations, not sufficiency by itself.
- Empirical execution sufficiency = a separate future preregistered assessment that is currently **not assessed / not closed**.

No evidence tier changes the frozen statistical contract. In particular:
- q25 / TopK / costs / horizon are not relaxed because execution evidence is sparse;
- no sealed holdout is consumed to compensate for missing live execution data;
- technical broker connectivity does not authorize real-account trading;
- `promotion_ready` remains false unless the full Master Spec promotion path independently passes.

## 8. Current implementation state

The research integrity schema separates PAPER from LIVE and now separates LIVE structural presence from empirical sufficiency. Real-account ordering remains disabled. No synthetic execution observations may be inserted to populate the ledger.

The empirical execution blocker remains open. A future preregistered sufficiency protocol and genuine staged live evidence are still required.
