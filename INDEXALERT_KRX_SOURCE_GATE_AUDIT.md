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
| Gate A — `AUTHORIZED_OFFICIAL_ROUTE` | `BLOCKED` | The routes are explicitly separated, but audited Actions show `KRX_ID`, `KRX_PW` and `KRX_OPENAPI_AUTH_KEY` absent in the active probe runtime. No authenticated KRX source request has therefore been demonstrated, and the exact authorized historical product/access contract remains open. |
| Gate B — `EXACT_DATASET_SCHEMA_MAPPING` | `PARTIAL` | Official screen contracts MDCSTAT213/237/238/239 are identified. The public re-audit confirms schema semantics for cleanup trading, delisting status and delisted regular-session price history. KRX also publicly lists KOSPI/KOSDAQ/KONEX basic-info OpenAPI services, but the exact approved historical transport/schema equivalence and stable full issue-ID field contract used by Final Judge are not yet frozen. |
| Gate C — `HISTORICAL_COVERAGE_SECURITY_MAPPING` | `BLOCKED` | `research_v1_krx_status_coverage.py` now fail-closed audits an independently attested `(snapshot_date, symbol, isu_cd)` scope against observed official common-stock identity. It never generates missing snapshots or IDs. Current normalized identity evidence lacks the stable full issue identifier required to close this gate, and no full-period expected scope/data has been supplied. |
| Gate D — `PIT_AVAILABILITY_LINEAGE` | `BLOCKED` | `available_at` remains mandatory in status adapters, but complete historical event/publication/availability/ingestion lineage across all status families has not been supplied. Public screen semantics clarify event economics but do not establish historical availability timestamps. |
| Gate E — `REPRODUCIBLE_INTEGRITY_FAIL_CLOSED` | `PARTIAL` | Pinned probes, source labels, A-F audit, public-evidence manifest/fingerprint, status coverage tests and fail-closed adapters exist. Authenticated end-to-end historical acquisition/schema/coverage reproducibility remains open. |
| Gate F — `INTENDED_USE_RIGHTS` | `PARTIAL` | Current OpenAPI terms are audited as effective 2025-12-26 and restrict OpenAPI use to non-commercial purposes, prohibit charging third parties for API results and prohibit providing KRX-received information to third parties. Exact rights for the final selected historical route/product remain unverified. |

Current verdict: `judge_security_status_ready=false`. No source-gate result here is permission to burn the sealed holdout.

## 4. Investor-flow family audit

Declared source family: `KRX_INVESTOR_FLOW`  
Declared use scope: `INTERNAL_RESEARCH_CANDIDATE_FEATURE_PREPARATION`  
Overall source contract: **OPEN — PERFORMANCE TESTING REMAINS BLOCKED**

| Gate | Status | Current evidence / blocker |
|---|---|---|
| Gate A — `AUTHORIZED_OFFICIAL_ROUTE` | `BLOCKED` | Audited Actions show all configured KRX credential variables absent in the active investor-flow probe runtime. No authenticated KRX request is exercised and the authorized reproducible historical route remains unfrozen. |
| Gate B — `EXACT_DATASET_SCHEMA_MAPPING` | `PARTIAL` | KRX publicly lists stock `투자자별 거래실적` and `투자자별 거래실적(개별종목)`; the exploratory client maps the intended per-security family to MDCSTAT02303. Exact approved historical transport/OpenAPI service/schema equivalence remains unestablished. |
| Gate C — `HISTORICAL_COVERAGE_SECURITY_MAPPING` | `BLOCKED` | `research_v1_krx_investor_flow_coverage.py` now compares only caller-supplied attested `(event_date, symbol, isu_cd)` keys against validated observed lineage. It never invents business days, securities or zero-flow rows; missing or extra keys keep coverage incomplete. No authorized full-period expected scope/history has yet been supplied. |
| Gate D — `PIT_AVAILABILITY_LINEAGE` | `PARTIAL` | `research_v1_krx_investor_flow_lineage.py` now enforces timezone-aware `event_time <= published_at <= available_at <= ingested_at`, the official day-D publication floor of 20:00 KST, current public-contract fingerprint, a single source-contract fingerprint and decision-time eligibility only after `available_at`. This is validated infrastructure, but no real full historical dataset has yet passed it. |
| Gate E — `REPRODUCIBLE_INTEGRITY_FAIL_CLOSED` | `PARTIAL` | The source probe is metadata-only/fingerprinted; public contract evidence is versioned; PIT lineage and exact-coverage validators fail closed. Bulk authenticated historical retrieval and reproducible coverage evidence remain unavailable. |
| Gate F — `INTENDED_USE_RIGHTS` | `PARTIAL` | Current OpenAPI non-commercial/no-third-party-distribution restrictions are frozen in the public-evidence manifest. Rights for the ultimately selected investor-flow route/use scope remain to be explicitly verified. |

Current verdict: investor-flow feature-performance experiments remain blocked. Validating synthetic/unit-test lineage or coverage structures does not turn them into source evidence.

## 5. Current official public evidence re-audit

The 2026-10-01 official KRX public re-audit established the following without private credentials:

1. **OpenAPI access model:** authentication-key application/administrator approval is followed by selection of an individual API service, a separate utilization application and service approval. `AUTH_KEY` alone is not dataset authorization.
2. **Service specificity/history:** KRX's public service list states a general OpenAPI data target period of 2010 onward and separately lists KOSPI/KOSDAQ/KONEX stock basic-information APIs. This does not establish the exact stable-identifier schema or historical snapshot semantics needed by Final Judge.
3. **OpenAPI missing-data notice:** the current homepage lists a June 2026 notice `KRX Open API 미제공 데이터에 대한 안내`. The retrievable page did not reliably expose a dataset list, so no specific IndexAlert dataset is classified available/unavailable from that notice alone.
4. **Status screen schemas:** MDCSTAT237/238/239 expose the status/economic fields described in the source contract. MDCSTAT238 is based on the last trading day before delisting; MDCSTAT239 price data are regular-session 09:00-15:30 data.
5. **Investor publication timing:** same-day final investor trading details are provided after 20:00.
6. **OpenAPI terms:** Korean terms effective 2025-12-26 restrict use to non-commercial purposes, prohibit charging third parties/providing received KRX information to third parties, impose up to 10,000 requests/day per key, require KRX-statistics attribution on screens, and prohibit continued use after the contract ends.

Machine-readable public evidence is frozen in `research_v1_krx_public_evidence.py` as version `2026-10-01.v1`, fingerprint `349d310647c78412e45ac13078259bab2d002958db597b2f7dd26228f8b3ca7b`.

None of these facts closes Gate A/C/D/E. They improve Gate B/F evidence while those gates remain `PARTIAL` at the whole-source-family level.

## 6. Audited workflow evidence

A green source-probe workflow must be interpreted by its internal result, not by the green check alone.

Earlier diagnostics `36668563968` and `36668579581` were green but internally `AUTH_NOT_CONFIGURED`; no authenticated source requests occurred.

Latest public-evidence-bound source probes:
- **Status Action `36809182681`** — success as diagnostic; `authenticated_request_attempted=false`; A `BLOCKED`, B `PARTIAL`, C `BLOCKED`, D `BLOCKED`, E/F `PARTIAL`; contract fingerprint `b91b5ee6b2b64e11910dddcd6f0400c884d2add3cd12530771eb5fb824160eec`; result fingerprint `65056341c19d0d70c7a8ae5e5bde3310cc54cfcc1eb2e4ed33645eb5152106e0`; artifact `11139071717`.
- **Investor-flow Action `36809196068`** — success as diagnostic; `authenticated_request_attempted=false`; A `BLOCKED`, B `PARTIAL`, C `BLOCKED`, D/E/F `PARTIAL`; `feature_performance_testing_authorized=false`; contract fingerprint `28c9d28aab34d8ec8e55258dbc95d389c2096eaf687c635a8e6c1b8f76179291`; result fingerprint `a227f4dcb34653cf89a9a6f462c01eabb45613c8c57212efa2e621039c53e097`; artifact `11138816495`.

Integrity CI:
- `36809165505` — public-evidence manifest/probe binding: **success**.
- `36809680268` — investor PIT-lineage tests: **success**.
- `36809948775` — investor exact-coverage tests: **success**.
- `36810205800` — initial status-coverage CI: **failed** on an empty-common-stock DataFrame schema bug; no policy/gate threshold changed.
- `36810309522` — same status-coverage protocol after preserving empty key schema: **success**.

## 7. Internal validation infrastructure now complete vs external evidence still missing

Implemented and CI-tested internally:
- canonical A-F source-gate semantics and documentation drift checks;
- public KRX contract/schema evidence manifest and fingerprint;
- source-probe contract/result fingerprints;
- investor-flow PIT lineage validator;
- investor-flow exact expected-scope coverage auditor;
- status/common-stock exact expected-scope coverage auditor;
- fail-closed prohibition on implicit zero-flow, invented dates/universe, stale public-evidence fingerprint, mixed source contracts and unstable/missing security identity.

Still missing external evidence:
- an approved/authenticated exact historical KRX route/product;
- real complete historical status/investor-flow data;
- independently attested full expected scope/security mapping;
- record-level historical PIT timestamps/availability evidence;
- exact intended-use rights for the final selected route.

Therefore the presence of validators does not change any A-F status by itself.

## 8. Evidence required to close the gates

- **Gate A:** approved exact route/product + demonstrated authorized access without exposing credentials.
- **Gate B:** exact service/screen/feed identifiers, schema/field mapping, version/transport assumptions and equivalence boundaries for the route actually used.
- **Gate C:** full-period independently attested expected scope and exact observed coverage, including stable security identity; no implicit zeros or generated history.
- **Gate D:** real record-level `event_time`/`published_at`/`available_at`/`ingested_at` lineage and decision eligibility for every historical observation.
- **Gate E:** reproducible authenticated acquisition/normalization/audit artifacts with immutable metadata/fingerprints.
- **Gate F:** permitted-use scope for the exact selected route before the corresponding activation stage.

## 9. Non-negotiable separation from model promotion

Even if all A-F gates later become `PASS`, PIT/time consistency, anchored Walk-Forward, Purged/CPCV diagnostics, realistic transaction/execution costs, fill/markout realism, distributional NetEV/tail risk, recency/current evidence, empirical capacity, one-shot sealed holdout, prospective Shadow S1 and frozen Fresh Confirmation S2 remain separate mandatory gates.

No A-F result may weaken q25/abstention, alter TopK/backfill, retune rejected H10/H20 work, reduce costs, mine horizons or otherwise manufacture a promotable result.
