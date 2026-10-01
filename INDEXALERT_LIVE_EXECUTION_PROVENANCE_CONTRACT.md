# IndexAlert Genuine LIVE Execution Provenance Contract

Updated: 2026-10-02 KST  
Branch: `index-alert-research-v1`  
Status: **FAIL-CLOSED PROVENANCE CONTRACT — REAL-ACCOUNT ORDERING REMAINS DISABLED**

## 1. Purpose

This contract prevents a self-authored or synthetic CSV from being converted into project-level empirical execution evidence merely by setting `source=PROSPECTIVE_LIVE_EXECUTION_LOG` and satisfying the frozen numerical thresholds.

The execution-sufficiency metric evaluator and genuine-LIVE provenance admission are separate controls:

1. **metric assessment** asks whether the supplied rows satisfy the frozen v1 fill/slippage/latency/capacity/tail criteria;
2. **provenance admission** asks whether those rows have independently verified broker-native origin and row-level traceability proving that they are genuine real-account observations.

Both are necessary. A metric pass without provenance admission is not project evidence and cannot close the empirical execution blocker.

## 2. Self-declaration is never provenance

None of the following can establish genuine LIVE provenance by itself:

- the literal source label `PROSPECTIVE_LIVE_EXECUTION_LOG`;
- a CSV file name or directory name containing `live`;
- a SHA-256 hash of a self-authored CSV;
- a unit-test fixture or synthetic generator;
- a manually typed summary of broker fills;
- Shadow or paper-broker rows relabelled as LIVE;
- a self-authored manifest that merely repeats the same values already present in the CSV.

A file hash proves byte identity only. It does not prove that the observations came from a real broker account.

## 3. Minimum independent provenance needed for later project admission

Before project-level execution evidence may be admitted, a separate provenance review must bind the exact assessment CSV to broker-native source material. The accepted source material must be external to the evaluator and independently auditable, for example:

- broker-native order/execution API captures produced by the real-account environment; or
- broker-issued order/execution export or statement material containing the corresponding real orders/executions.

The review must establish, without exposing account secrets:

- exact evidence CSV SHA-256 and row count;
- evidence window start/end;
- broker/environment identity sufficient to distinguish real account from paper/simulation;
- a privacy-safe account fingerprint, never plaintext account credentials;
- stable broker order/execution identifiers or an equivalent broker-native identity;
- row-level mapping from each admitted `observation_id` to broker-native order/execution evidence;
- requested quantity, fill quantity, fill timestamps and fill price consistency;
- no-fill / partial-fill outcomes where applicable;
- fees/tax evidence where the broker supplies it;
- reconciliation status and any unresolved broker/internal mismatch;
- hashes of the broker-native source artifacts used by the review;
- reviewer identity or review artifact identity and review timestamp.

The provenance review must preserve negative/adverse observations. Missing broker-native evidence must fail closed rather than be imputed.

## 4. Current automated boundary

`research_v1_execution_sufficiency_assessment.py` is a **metric evaluator**. It may report that the frozen numerical execution gates passed for the supplied rows, but it must not by itself claim that the rows are genuine broker evidence.

Therefore, until an independent broker-native provenance admission exists and passes for the exact evidence bundle, the evaluator/CLI must keep:

- `genuine_live_provenance_verified=false`;
- `execution_metric_sufficiency_assessed=true` may describe only the numerical evaluation that was run;
- `empirical_execution_sufficiency_assessed=false`;
- `live_empirical_execution_evidence_ready=false`;
- `empirical_execution_blocker_closed=false`;
- `promotion_ready=false`;
- `sealed_holdout_authorized=false`;
- `live_trading_authorized=false`.

A numerical pass should instead be exposed separately as `execution_metric_gates_passed=true`.

This is stricter evidence admission; it does not alter or weaken any frozen v1 numerical threshold.

## 5. Future provenance verifier

A future broker-specific verifier may combine the metric result with independently obtained broker-native artifacts. It must be implemented only from then-current official broker documentation and real evidence formats. It must not accept a caller-supplied boolean or a renamed CSV as proof of genuineness.

Until such a verifier/review path is implemented and actually used on genuine evidence, project-level provenance remains unverified.

## 6. Trading and holdout guardrails

This contract does not activate or implement real-account ordering. Current automated real-account ordering remains disabled.

It also does not authorize:

- sealed holdout consumption;
- model promotion;
- Shadow S1 completion;
- Fresh Confirmation S2;
- Tiny Live / Limited Live / Production stage advancement.

Those remain governed by the Master Spec and their independent gates.
