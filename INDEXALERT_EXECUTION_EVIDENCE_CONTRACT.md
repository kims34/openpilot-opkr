# IndexAlert Execution Evidence Contract

Updated: 2026-10-02 KST
Branch: `index-alert-research-v1`
Status: **FROZEN EVIDENCE-CLASSIFICATION CONTRACT — NOT PROMOTION EVIDENCE**

## 1. Purpose

This contract prevents Shadow decisions, paper-broker executions and real-account executions from being conflated. It governs evidence classification only; it does not activate live ordering and does not change Alpha/statistical promotion gates.

A second boundary is equally important: **structurally valid LIVE rows are not the same thing as sufficient empirical execution evidence.** One or a few real-account fills may demonstrate that the execution ledger works, but cannot by themselves close the empirical execution blocker.

A third boundary is now explicit: **a row self-labelled `PROSPECTIVE_LIVE_EXECUTION_LOG` is not proof of genuine real-account provenance.** Numerical sufficiency and broker-native provenance admission are separate requirements.

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
- The literal source label is a classification field, not an authenticity credential. Project admission additionally requires independently verified broker-native provenance for the exact evidence bundle.

## 3. Forbidden source substitution

The following must be rejected from empirical broker-fill evidence:
- backtest-generated fills;
- synthetic/modelled fills;
- market-open assumptions relabelled as fills;
- Shadow would-be orders/fills;
- undocumented source strings;
- paper observations relabelled as live observations;
- self-authored or unit-test rows relabelled as `PROSPECTIVE_LIVE_EXECUTION_LOG`;
- a CSV hash, file name or manifest used as a substitute for broker-native source proof.

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

The frozen project numerical protocol is evaluated separately by `research_v1_execution_sufficiency_assessment.py`. The evaluator may set `execution_metric_gates_passed=true` only when every frozen numerical gate passes. That result still does not prove that the input is genuine real-account evidence.

## 6. Preregistered execution-sufficiency protocol

`research_v1_execution_sufficiency_protocol.py` is the canonical structural validator for execution-sufficiency preregistration.

A valid protocol record must include at least:
- unique protocol ID and schema version;
- timezone-aware `frozen_at`;
- protocol-document SHA-256;
- minimum LIVE observation count;
- minimum distinct decision dates;
- minimum filled/no-fill/partial-fill observation counts;
- required markout horizons including 5m, 30m and close;
- mandatory slippage, latency, capacity and tail evidence requirements;
- rationale.

If LIVE evidence already exists, `frozen_at` must be **strictly earlier** than the first LIVE recommendation being evaluated. A protocol frozen at or after that first LIVE observation is rejected as post-hoc.

Unit-test fixture values remain non-evidence. The canonical IndexAlert project thresholds are frozen in `INDEXALERT_EXECUTION_SUFFICIENCY_PROTOCOL.md` and its SHA-256-bound `INDEXALERT_EXECUTION_SUFFICIENCY_PROTOCOL.json`; they were fixed before any genuine LIVE observation.

Even a structurally valid preregistered protocol sets only protocol validity. It deliberately keeps:
- `empirical_execution_sufficiency_assessed=false`;
- `empirical_execution_blocker_closed=false`;
- `promotion_ready=false`;
- `sealed_holdout_authorized=false`;
- `live_trading_authorized=false`.

## 6A. Genuine LIVE provenance admission

Canonical contract: `INDEXALERT_LIVE_EXECUTION_PROVENANCE_CONTRACT.md`.

`research_v1_execution_sufficiency_assessment.py` is a numerical metric evaluator. It cannot authenticate broker provenance from a caller-supplied CSV. Therefore a metric pass by itself must keep all project-level empirical state fail-closed:
- `genuine_live_provenance_verified=false`;
- `empirical_execution_sufficiency_assessed=false`;
- `live_empirical_execution_evidence_ready=false`;
- `empirical_execution_blocker_closed=false`.

Later project admission requires an independent review/verifier that binds the exact CSV to broker-native real-account order/execution material with row-level traceability. A source label, CSV SHA-256, unit-test fixture or self-authored manifest is insufficient.

The provenance requirement is an evidence-integrity hardening layer. It does not change or weaken any frozen v1 numerical threshold.

## 7. Immutability and identity

Broker execution observations are immutable once written. A retry with the same stable observation identity may be idempotent only if the normalized payload is identical.

New execution observation identity must include the source tier so that PAPER and LIVE observations for an otherwise identical decision do not overwrite or collide with one another.

Historical rows written under the former source label `PROSPECTIVE_SHADOW_EXECUTION_LOG` must not be rewritten or deleted to manufacture cleaner evidence. They remain quarantined as `legacy_shadow_fill` and are excluded from live empirical-evidence claims.

## 8. Promotion interpretation

- Shadow evidence = prospective decision behavior only.
- Paper evidence = operational/broker-pipeline behavior only.
- Structurally valid LIVE-labelled rows = eligible input shape, not proof of genuine broker provenance and not sufficiency by themselves.
- Valid execution-sufficiency protocol = preregistered numerical criteria only.
- `execution_metric_gates_passed=true` = the supplied rows satisfy the frozen numerical gates, not a project-level evidence admission.
- Genuine LIVE provenance = separate independent broker-native evidence admission for the exact assessment bundle.
- Empirical execution blocker closure requires both numerical sufficiency and genuine provenance, and is currently **not closed**.

No evidence tier changes the frozen statistical contract. In particular:
- q25 / TopK / costs / horizon are not relaxed because execution evidence is sparse;
- no sealed holdout is consumed to compensate for missing live execution data;
- technical broker connectivity does not authorize real-account trading;
- `promotion_ready` remains false unless the full Master Spec promotion path independently passes.

## 9. Current implementation state

The research integrity schema separates PAPER from LIVE and LIVE structural presence from numerical sufficiency. The project protocol is frozen in `INDEXALERT_EXECUTION_SUFFICIENCY_PROTOCOL.md` / `.json` and the metric evaluator is Actions-tested.

As of 2026-10-02 the metric evaluator also fails closed on authenticity: a source-labelled/hash-bound CSV cannot by itself set `live_empirical_execution_evidence_ready` or `empirical_execution_blocker_closed` true. Broker-native provenance admission is a separate still-open requirement.

Real-account ordering remains disabled. No synthetic execution observations may be inserted to populate the ledger or presented as project evidence.

The empirical execution blocker remains open because no genuine staged LIVE evidence window and no independent broker-native provenance admission exist yet. Numerical metric pass, when eventually run on evidence, will remain only one necessary component. Passing it still does not independently authorize sealed holdout, promotion or live trading.
