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
| Gate A — `AUTHORIZED_OFFICIAL_ROUTE` | `BLOCKED` | The source routes are explicitly separated, but audited GitHub Actions logs show `KRX_ID`, `KRX_PW` and `KRX_OPENAPI_AUTH_KEY` are absent in the active source-probe runtime. The authenticated Data Marketplace route is therefore not exercised, and the exact authorized historical product/access contract is not closed. |
| Gate B — `EXACT_DATASET_SCHEMA_MAPPING` | `PARTIAL` | Official screen contracts MDCSTAT213/237/238/239 are identified. The 2026-10-01 official public re-audit directly confirms schema semantics for MDCSTAT237 cleanup-trading status, MDCSTAT238 delisting status/stock type/listing and delisting dates/reason, and MDCSTAT239 regular-session delisted-security OHLC/volume/value/capitalization history. Some low-level BLD mappings remain provisional and exact approved historical transport/OpenAPI equivalence for the complete required family has not been established. |
| Gate C — `HISTORICAL_COVERAGE_SECURITY_MAPPING` | `BLOCKED` | Full requested-period common-stock identity/status history and complete relevant-security coverage have not been reconstructed and independently audited. The current coverage audit deliberately keeps `judge_security_status_ready=false`. |
| Gate D — `PIT_AVAILABILITY_LINEAGE` | `BLOCKED` | `available_at` is mandatory in adapters, but complete historical `event_time`/publication/availability/ingestion lineage for all status families across the Judge period is not yet established. The MDCSTAT238 public page's “last trading day before delisting” note and MDCSTAT239 regular-session semantics clarify event economics but do not establish historical publication/availability timestamps. |
| Gate E — `REPRODUCIBLE_INTEGRITY_FAIL_CLOSED` | `PARTIAL` | Pinned metadata-only diagnostics, strict official-source labels, fail-closed adapter tests and probe contract/result fingerprints exist. End-to-end authenticated historical acquisition/schema/coverage reproducibility is not yet closed. |
| Gate F — `INTENDED_USE_RIGHTS` | `PARTIAL` | Current KRX OpenAPI terms are audited as effective 2025-12-26 and explicitly restrict OpenAPI use to non-commercial purposes, prohibit charging third parties for API results, and prohibit providing KRX-received information to third parties. This clearly blocks assuming free OpenAPI terms cover an external/paid product, but exact rights for the final chosen historical route/product remain to be verified. |

Current verdict: `judge_security_status_ready=false`. No source gate result in this table is permission to burn the sealed holdout.

## 4. Investor-flow family audit

Declared source family: `KRX_INVESTOR_FLOW`  
Declared use scope: `INTERNAL_RESEARCH_CANDIDATE_FEATURE_PREPARATION`  
Overall source contract: **OPEN — PERFORMANCE TESTING REMAINS BLOCKED**

| Gate | Status | Current evidence / blocker |
|---|---|---|
| Gate A — `AUTHORIZED_OFFICIAL_ROUTE` | `BLOCKED` | Audited GitHub Actions logs show `KRX_ID`, `KRX_PW` and `KRX_OPENAPI_AUTH_KEY` are absent in the active investor-flow source-probe runtime. No authenticated KRX request is exercised and the official reproducible historical access contract remains unfrozen. |
| Gate B — `EXACT_DATASET_SCHEMA_MAPPING` | `PARTIAL` | KRX Data Marketplace publicly lists stock `투자자별 거래실적` and `투자자별 거래실적(개별종목)`; the exploratory client maps the intended per-security family to MDCSTAT02303. The exact approved historical transport/OpenAPI service/schema equivalence is not established and must not be inferred. |
| Gate C — `HISTORICAL_COVERAGE_SECURITY_MAPPING` | `BLOCKED` | Full historical coverage and stable security mapping have not been audited for the research period. A tiny probe window cannot close this gate. |
| Gate D — `PIT_AVAILABILITY_LINEAGE` | `PARTIAL` | The official publication rule is directly re-verified: final day-D investor trading results are supplied after 20:00, so they may only enter a later eligible decision. Complete record-level `event_time`/`published_at`/`available_at`/`ingested_at` lineage is not yet implemented for historical research data. |
| Gate E — `REPRODUCIBLE_INTEGRITY_FAIL_CLOSED` | `PARTIAL` | The diagnostic is metadata-only, fail-closed, fingerprints its contract/result and does not persist numeric market data; credentials are not exposed. Bulk authenticated historical reproducibility/coverage integrity remains unverified. |
| Gate F — `INTENDED_USE_RIGHTS` | `PARTIAL` | The current OpenAPI non-commercial/no-third-party-distribution restrictions are explicitly documented. Internal research and future external/commercial use remain separated, but rights for the ultimately selected investor-flow route/use scope remain to be explicitly verified. |

Current verdict: investor-flow feature-performance experiments remain blocked. A workflow run that exits successfully while reporting `AUTH_NOT_CONFIGURED` is diagnostic execution evidence only, not authenticated source evidence.

## 5. Current official public evidence re-audit

The 2026-10-01 official KRX public re-audit established the following without requiring private credentials:

1. **OpenAPI access model:** the official service-use guide requires login/authentication-key application and administrator approval, then selection of an individual API service, a separate utilization application, and service approval before use. An `AUTH_KEY` alone is not dataset authorization.
2. **OpenAPI service specificity:** individual service pages expose service names/descriptions/history start dates and require service-specific utilization applications. This supports the rule that a similarly named API cannot be assumed equivalent to a Data Marketplace screen.
3. **OpenAPI missing-data notice:** the current OpenAPI homepage lists a June 2026 notice titled `KRX Open API 미제공 데이터에 대한 안내`. The publicly retrievable notice body did not reliably expose the dataset list, so this is evidence only that some Data Marketplace data are not necessarily OpenAPI data. It is **not** evidence that a specific IndexAlert-required dataset is available or unavailable.
4. **Status screen schemas:** MDCSTAT237, MDCSTAT238 and MDCSTAT239 public pages expose the status/economic fields described in the source contract. MDCSTAT238 explicitly states its information is based on the last trading day before delisting; MDCSTAT239 states price data are regular-session 09:00-15:30 data.
5. **Investor publication timing:** the KRX investor-trading page states that same-day final trading details are provided after 20:00.
6. **OpenAPI terms:** the Korean terms effective 2025-12-26 restrict use to non-commercial purposes, prohibit charging third parties for API results, prohibit providing KRX-received information to third parties, impose up to 10,000 requests/day per key, require KRX-statistics attribution on screens built from results, and prohibit continued use after the contract ends.

None of these facts closes Gate A/C/D/E for either source family. They improve the evidence quality behind Gate B/F while those gates remain `PARTIAL` at the whole-source-family level.

## 6. Audited workflow evidence

The source-probe logs must be interpreted by their internal result rather than by the green workflow check alone.

Earlier diagnostic runs:
- KRX status source probe Action `36668563968` — workflow success, internal `AUTH_NOT_CONFIGURED`; all three KRX secret environment values empty; no authenticated source request.
- KRX investor-flow source probe Action `36668579581` — workflow success, internal `AUTH_NOT_CONFIGURED`; all three KRX secret environment values empty; no authenticated source request.

Current machine-audited runs:
- status Action `36808057709` — diagnostic success; `authenticated_request_attempted=false`; A `BLOCKED`, B `PARTIAL`, C `BLOCKED`, D `BLOCKED`, E/F `PARTIAL`; source contract open; artifact `11138570329`.
- investor-flow Action `36808077021` — diagnostic success; `authenticated_request_attempted=false`; A `BLOCKED`, B `PARTIAL`, C `BLOCKED`, D/E/F `PARTIAL`; `feature_performance_testing_authorized=false`; artifact `11137504925`.
- Official KRX Status Integrity Actions `36808122270`, `36808133821` and subsequent status-document Action `36808367257` — success.

The source probe code emits a machine-readable `source_gate_audit`, `authenticated_request_attempted`, `probe_contract_fingerprint_sha256` and `probe_result_fingerprint_sha256`. Missing session credentials force Gate A to `BLOCKED`; merely supplying credentials can raise it only to `PARTIAL`, never directly to `PASS`.

## 7. Evidence required to close the gates

- **Gate A:** configure/obtain an approved exact official historical route/product and demonstrate the relevant authorized source access without exposing credentials; a green diagnostic Action with `AUTH_NOT_CONFIGURED` does not count.
- **Gate B:** freeze service/screen/feed identifiers, schema/field mapping, version/transport assumptions and equivalence boundaries. Public-screen schema confirmation alone is insufficient if the actual acquisition route differs.
- **Gate C:** produce a reproducible coverage audit across the full requested period and relevant security universe, including stable security identity mapping.
- **Gate D:** preserve auditable PIT lineage and decision-time eligibility for every historical observation; no retrospective availability assumptions.
- **Gate E:** demonstrate reproducible acquisition/normalisation/audit outputs with fail-closed tests and immutable source metadata/fingerprints sufficient to detect drift or substitution.
- **Gate F:** record the permitted-use scope for the exact selected route before the corresponding internal/product activation stage. Free OpenAPI terms must not be extended by inference to paid/external distribution.

## 8. Non-negotiable separation from model promotion

Even if all A-F gates later become `PASS`, the following remain separate mandatory gates under the Master Spec: PIT/time consistency, anchored Walk-Forward, Purged/CPCV diagnostics, realistic transaction/execution costs, fill and markout realism, distributional NetEV and tail risk, recency/current evidence, empirical capacity, one-shot sealed holdout, prospective trading-policy Shadow S1 and frozen Fresh Confirmation S2.

No A-F source result may be used to weaken q25/abstention, alter TopK/backfill, retune rejected H10/H20 work, reduce costs, mine a horizon, or otherwise manufacture a promotable result.
