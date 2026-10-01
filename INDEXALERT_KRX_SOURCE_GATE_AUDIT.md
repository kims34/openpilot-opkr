# IndexAlert KRX Source Gate Audit — A-F

Updated: 2026-10-01 KST  
Branch: `index-alert-research-v1`  
Status: **SOURCE-GOVERNANCE AUDIT — NO ALPHA / HOLDOUT / LIVE AUTHORITY**

## 1. Authority and purpose

This audit applies the frozen A-F source-gate contract in `INDEXALERT_KRX_SOURCE_ACCESS_CONTRACT.md`. Executable gate semantics live in `research_v1_krx_source_gates.py`.

This document records only current source readiness. It does not modify or relax `INDEXALERT_MASTER_SPEC.md`, does not constitute feature-performance evidence, does not consume the sealed holdout, and cannot authorize Shadow/Paper/Live promotion or live trading.

Allowed gate states are exactly `PASS`, `PARTIAL`, `BLOCKED`. Only `PASS` closes a gate. `PARTIAL` is not a pass.

## 2. Frozen gate definitions

- **Gate A — `AUTHORIZED_OFFICIAL_ROUTE`**: exact official KRX access route/product and appropriate authorization are identified; OpenAPI, Data Marketplace web session and purchased/distributed products are not interchangeable.
- **Gate B — `EXACT_DATASET_SCHEMA_MAPPING`**: exact API service/screen/feed and required fields/schema are verified; similar names or provisional transports are insufficient.
- **Gate C — `HISTORICAL_COVERAGE_SECURITY_MAPPING`**: requested historical period/relevant securities, stable mapping and required common-stock identity are covered; a current snapshot or tiny probe is insufficient.
- **Gate D — `PIT_AVAILABILITY_LINEAGE`**: `event_time`, `published_at` where applicable, `available_at`, `ingested_at` and decision eligibility are explicit and PIT-safe.
- **Gate E — `REPRODUCIBLE_INTEGRITY_FAIL_CLOSED`**: retrieval/source metadata are reproducible and auditable, ambiguity fails closed, and undocumented proxy/synthetic substitution is forbidden.
- **Gate F — `INTENDED_USE_RIGHTS`**: data-use/licensing rights are verified for the declared use scope; internal research and external/commercial product use are separate scopes.

## 3. Security/status family audit

Declared source family: `KRX_SECURITY_STATUS`  
Declared use scope: `INTERNAL_RESEARCH_AND_FINAL_JUDGE_INPUT_PREPARATION`  
Overall source contract: **OPEN — NOT ALL A-F PASS**

| Gate | Status | Current evidence / blocker |
|---|---|---|
| Gate A — `AUTHORIZED_OFFICIAL_ROUTE` | `BLOCKED` | The source routes are explicitly separated, but audited GitHub Actions logs for status probe Action `36668563968` show `KRX_ID`, `KRX_PW` and `KRX_OPENAPI_AUTH_KEY` were all absent. The authenticated Data Marketplace route was therefore not exercised, and the exact authorized historical product/access contract is not closed. |
| Gate B — `EXACT_DATASET_SCHEMA_MAPPING` | `PARTIAL` | Official screen contracts MDCSTAT213/237/238/239 are identified; the current adapters have strict source/schema checks. Some low-level BLD mappings remain provisional and exact approved historical service/schema equivalence for all required histories has not been established. |
| Gate C — `HISTORICAL_COVERAGE_SECURITY_MAPPING` | `BLOCKED` | Full requested-period common-stock identity/status history and complete relevant-security coverage have not been reconstructed and independently audited. The current coverage audit deliberately keeps `judge_security_status_ready=false`. |
| Gate D — `PIT_AVAILABILITY_LINEAGE` | `BLOCKED` | `available_at` is mandatory in adapters, but complete historical `event_time`/publication/availability/ingestion lineage for all status families across the Judge period is not yet established. |
| Gate E — `REPRODUCIBLE_INTEGRITY_FAIL_CLOSED` | `PARTIAL` | Pinned metadata-only diagnostics, strict official-source labels, fail-closed adapter tests and probe contract/result fingerprints exist. End-to-end authenticated historical acquisition/schema/coverage reproducibility is not yet closed. |
| Gate F — `INTENDED_USE_RIGHTS` | `PARTIAL` | Project rules distinguish internal research from future external/commercial use and forbid assuming free OpenAPI rights cover a product. Exact rights for the final chosen historical route and any future distribution scope remain to be verified. |

Current verdict: `judge_security_status_ready=false`. No source gate result in this table is permission to burn the sealed holdout.

## 4. Investor-flow family audit

Declared source family: `KRX_INVESTOR_FLOW`  
Declared use scope: `INTERNAL_RESEARCH_CANDIDATE_FEATURE_PREPARATION`  
Overall source contract: **OPEN — PERFORMANCE TESTING REMAINS BLOCKED**

| Gate | Status | Current evidence / blocker |
|---|---|---|
| Gate A — `AUTHORIZED_OFFICIAL_ROUTE` | `BLOCKED` | Audited GitHub Actions logs for investor-flow probe Action `36668579581` show `KRX_ID`, `KRX_PW` and `KRX_OPENAPI_AUTH_KEY` were all absent. No authenticated KRX request was exercised in that run, and the official reproducible historical access contract remains unfrozen. |
| Gate B — `EXACT_DATASET_SCHEMA_MAPPING` | `PARTIAL` | The MDCSTAT02303 individual-investor daily source family is identified, but exact approved historical service/schema equivalence is not established and must not be inferred. |
| Gate C — `HISTORICAL_COVERAGE_SECURITY_MAPPING` | `BLOCKED` | Full historical coverage and stable security mapping have not been audited for the research period. A tiny probe window cannot close this gate. |
| Gate D — `PIT_AVAILABILITY_LINEAGE` | `PARTIAL` | The official publication rule is frozen: final day-D investor trading results are eligible only for the next decision after publication (the audited page states after 20:00). Complete record-level `event_time`/`published_at`/`available_at`/`ingested_at` lineage is not yet implemented for historical research data. |
| Gate E — `REPRODUCIBLE_INTEGRITY_FAIL_CLOSED` | `PARTIAL` | The diagnostic is metadata-only, fail-closed, fingerprints its contract/result and does not persist numeric market data; credentials are not exposed. Bulk authenticated historical reproducibility/coverage integrity remains unverified. |
| Gate F — `INTENDED_USE_RIGHTS` | `PARTIAL` | Internal research and future external/commercial use are separated by contract, but rights for the ultimately selected investor-flow route/use scope remain to be explicitly verified. |

Current verdict: investor-flow feature-performance experiments remain blocked. A workflow run that exits successfully while reporting `AUTH_NOT_CONFIGURED` is diagnostic execution evidence only, not authenticated source evidence.

## 5. Audited workflow evidence

The following Actions completed successfully as workflows, but the source-probe logs must be interpreted by their internal result rather than by the green workflow check alone:

- Official KRX status integrity: Action `36646910657` — success; adapter/test infrastructure evidence.
- KRX status source probe: Action `36668563968` — workflow success, but report/log state `AUTH_NOT_CONFIGURED`; all three configured KRX secret environment values were empty, so no authenticated source request was exercised.
- KRX investor-flow source probe: Action `36668579581` — workflow success, but report/log state `AUTH_NOT_CONFIGURED`; all three configured KRX secret environment values were empty, so no authenticated source request was exercised.

The source probe code now emits a machine-readable `source_gate_audit`, `authenticated_request_attempted`, `probe_contract_fingerprint_sha256` and `probe_result_fingerprint_sha256`. Missing session credentials force Gate A to `BLOCKED`; merely supplying credentials can raise it only to `PARTIAL`, never directly to `PASS`.

## 6. Evidence required to close the gates

- **Gate A:** configure/obtain an approved exact official historical route/product and demonstrate the relevant authorized source access without exposing credentials; a green diagnostic Action with `AUTH_NOT_CONFIGURED` does not count.
- **Gate B:** freeze service/screen/feed identifiers, schema/field mapping, version/transport assumptions and equivalence boundaries.
- **Gate C:** produce a reproducible coverage audit across the full requested period and relevant security universe, including stable security identity mapping.
- **Gate D:** preserve auditable PIT lineage and decision-time eligibility for every historical observation; no retrospective availability assumptions.
- **Gate E:** demonstrate reproducible acquisition/normalisation/audit outputs with fail-closed tests and immutable source metadata/fingerprints sufficient to detect drift or substitution.
- **Gate F:** record the permitted-use scope for the exact selected route before the corresponding internal/product activation stage.

## 7. Non-negotiable separation from model promotion

Even if all A-F gates later become `PASS`, the following remain separate mandatory gates under the Master Spec: PIT/time consistency, anchored Walk-Forward, Purged/CPCV diagnostics, realistic transaction/execution costs, fill and markout realism, distributional NetEV and tail risk, recency/current evidence, empirical capacity, one-shot sealed holdout, prospective trading-policy Shadow S1 and frozen Fresh Confirmation S2.

No A-F source result may be used to weaken q25/abstention, alter TopK/backfill, retune rejected H10/H20 work, reduce costs, mine a horizon, or otherwise manufacture a promotable result.
