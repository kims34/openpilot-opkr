# IndexAlert KRX Source Gate Audit — A-F

Updated: 2026-10-01 KST  
Branch: `index-alert-research-v1`  
Status: **SOURCE-GOVERNANCE AUDIT — NO ALPHA / HOLDOUT / LIVE AUTHORITY**

## 1. Authority and purpose

This audit applies the frozen A-F source-gate contract in `INDEXALERT_KRX_SOURCE_ACCESS_CONTRACT.md`. Executable gate semantics live in `research_v1_krx_source_gates.py`.

This document records only current source readiness. It does not modify or relax `INDEXALERT_MASTER_SPEC.md`, does not constitute feature-performance evidence, does not consume the one-shot sealed holdout, and cannot authorize Shadow/Paper/Live promotion or live trading.

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
| Gate A — `AUTHORIZED_OFFICIAL_ROUTE` | `BLOCKED` | The routes are explicitly separated and `research_v1_krx_auth_preflight.py` now requires route-specific credentials **plus** a non-secret authorization-evidence reference before even a tiny authenticated probe can run. Latest audited status-probe Action `36811927281` had `KRX_ID`, `KRX_PW`, `KRX_OPENAPI_AUTH_KEY` and `KRX_AUTH_EVIDENCE_REF` all absent; `request_attempt_authorized=false`, so no authenticated KRX request occurred. |
| Gate B — `EXACT_DATASET_SCHEMA_MAPPING` | `PARTIAL` | Official screen contracts MDCSTAT213/237/238/239 are identified. The public re-audit confirms schema semantics for cleanup trading, delisting status and delisted regular-session price history. KRX also publicly lists KOSPI/KOSDAQ/KONEX basic-info OpenAPI services, but the exact approved historical transport/schema equivalence and stable full issue-ID field contract used by Final Judge are not yet frozen. |
| Gate C — `HISTORICAL_COVERAGE_SECURITY_MAPPING` | `BLOCKED` | `research_v1_krx_status_coverage.py` fail-closed audits an independently attested `(snapshot_date, symbol, isu_cd)` scope against observed official common-stock identity. It never generates missing snapshots or IDs. Current normalized identity evidence lacks the stable full issue identifier required to close this gate, and no full-period expected scope/data has been supplied. |
| Gate D — `PIT_AVAILABILITY_LINEAGE` | `BLOCKED` | `available_at` remains mandatory in status adapters, but complete historical event/publication/availability/ingestion lineage across all status families has not been supplied. Public screen semantics clarify event economics but do not establish historical availability timestamps. |
| Gate E — `REPRODUCIBLE_INTEGRITY_FAIL_CLOSED` | `PARTIAL` | Pinned probes, source labels, A-F audit, public-evidence manifest/fingerprint, status coverage/event-integrity tests now exist. `research_v1_krx_acquisition_receipt.py` fingerprints request metadata, response schema/content, route, dataset, client revision, retrieval time, approval reference and public-contract evidence without persisting numeric rows. `research_v1_krx_acquisition_batch.py` rejects tampered/duplicate receipts and silent mixing of route, approval reference, client revision, dataset or schema. Real authenticated end-to-end historical acquisition remains unavailable. |
| Gate F — `INTENDED_USE_RIGHTS` | `PARTIAL` | Current OpenAPI terms are audited as effective 2025-12-26 and restrict OpenAPI use to non-commercial purposes, prohibit charging third parties for API results and prohibit providing KRX-received information to third parties. Exact rights for the final selected historical route/product remain unverified. |

Current verdict: `judge_security_status_ready=false`. No source-gate result here is permission to burn the sealed holdout.

## 4. Investor-flow family audit

Declared source family: `KRX_INVESTOR_FLOW`  
Declared use scope: `INTERNAL_RESEARCH_CANDIDATE_FEATURE_PREPARATION`  
Overall source contract: **OPEN — PERFORMANCE TESTING REMAINS BLOCKED**

| Gate | Status | Current evidence / blocker |
|---|---|---|
| Gate A — `AUTHORIZED_OFFICIAL_ROUTE` | `BLOCKED` | The Data Marketplace preflight requires both `KRX_ID`/`KRX_PW` and non-secret `KRX_AUTH_EVIDENCE_REF`; OpenAPI AUTH_KEY is never accepted as a substitute. Latest investor probe Action `36811913060` had all four values absent, returned `AUTHORIZATION_PREFLIGHT_BLOCKED` and `authenticated_request_attempted=false`. |
| Gate B — `EXACT_DATASET_SCHEMA_MAPPING` | `PARTIAL` | KRX publicly lists stock `투자자별 거래실적` and `투자자별 거래실적(개별종목)`; the exploratory client maps the intended per-security family to MDCSTAT02303. Exact approved historical transport/OpenAPI service/schema equivalence remains unestablished. |
| Gate C — `HISTORICAL_COVERAGE_SECURITY_MAPPING` | `BLOCKED` | `research_v1_krx_investor_flow_coverage.py` compares only caller-supplied attested `(event_date, symbol, isu_cd)` keys against validated observed lineage. It never invents business days, securities or zero-flow rows; missing or extra keys keep coverage incomplete. No authorized full-period expected scope/history has yet been supplied. |
| Gate D — `PIT_AVAILABILITY_LINEAGE` | `PARTIAL` | `research_v1_krx_investor_flow_lineage.py` enforces timezone-aware `event_time <= published_at <= available_at <= ingested_at`, the official day-D publication floor of 20:00 KST, current public-contract fingerprint, a single source-contract fingerprint and decision-time eligibility only after `available_at`. This is validated infrastructure, but no real full historical dataset has yet passed it. |
| Gate E — `REPRODUCIBLE_INTEGRITY_FAIL_CLOSED` | `PARTIAL` | The source probe is metadata-only/fingerprinted; public contract evidence is versioned; PIT lineage and exact-coverage validators fail closed; future acquisitions now require secret-free immutable receipts and internally consistent receipt batches. Bulk authenticated historical retrieval and reproducible real-data coverage evidence remain unavailable. |
| Gate F — `INTENDED_USE_RIGHTS` | `PARTIAL` | Current OpenAPI non-commercial/no-third-party-distribution restrictions are frozen in the public-evidence manifest. Rights for the ultimately selected investor-flow route/use scope remain to be explicitly verified. |

Current verdict: investor-flow feature-performance experiments remain blocked. Validating synthetic/unit-test lineage, coverage or provenance structures does not turn them into source evidence.

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

Latest authorization-preflight-bound source probes:
- **Status Action `36811927281`** — workflow success as diagnostic; `status=AUTHORIZATION_PREFLIGHT_BLOCKED`; `request_attempt_authorized=false`; `authenticated_request_attempted=false`; missing `KRX_ID`, `KRX_PW`, `KRX_AUTH_EVIDENCE_REF`; A `BLOCKED`, B `PARTIAL`, C `BLOCKED`, D `BLOCKED`, E/F `PARTIAL`; contract fingerprint `766ccb09304434f947cea290a29e7f3f6322dbc06d53997d4eef4a44fe0c3e9d`; result fingerprint `1ab3b8e1b0cb73e8eba5ae0765faa9e64eb2a037c5ef8f5219c7eeac77d3a59d`; artifact `11140235232`.
- **Investor-flow Action `36811913060`** — workflow success as diagnostic; `status=AUTHORIZATION_PREFLIGHT_BLOCKED`; `request_attempt_authorized=false`; `authenticated_request_attempted=false`; missing `KRX_ID`, `KRX_PW`, `KRX_AUTH_EVIDENCE_REF`; A `BLOCKED`, B `PARTIAL`, C `BLOCKED`, D/E/F `PARTIAL`; `feature_performance_testing_authorized=false`; contract fingerprint `75b10d1d6dd46f43821840532fc97b59129e402f169847a8c8bb6edaaf14102d`; result fingerprint `9508451f23a64ba62220b9ae09c4eb45629203843fa2a8c6ba4a2f7e04cd34e3`; artifact `11140075783`.

Integrity CI milestones:
- `36809165505` — public-evidence manifest/probe binding: **success**.
- `36809680268` — investor PIT-lineage tests: **success**.
- `36809948775` — investor exact-coverage tests: **success**.
- `36810309522` — status exact-coverage protocol after fixing empty-common-stock schema handling: **success**.
- `36811118588` — status event-integrity layer: **success**.
- `36811648510` — secret-free acquisition receipt integrity: **success**.
- `36811896765` — probes/tests aligned to authorization-preflight semantics: **success**.
- `36812137960` — authorization preflight + exact credential-value redaction test: **success**.

Transient CI failures during implementation (`36811825608`, `36811871522`, `36811949339`) were test/API-alignment or test-string false-positive failures. Their follow-up runs passed without weakening any A-F gate, research threshold, economics criterion or promotion boundary.

## 7. Internal validation/provenance infrastructure vs external evidence still missing

Implemented and CI-tested internally:
- canonical A-F source-gate semantics and documentation drift checks;
- public KRX contract/schema evidence manifest and fingerprint;
- route-specific authorization preflight: credentials are not authorization and routes cannot substitute for one another;
- source-probe contract/result fingerprints;
- investor-flow PIT lineage validator;
- investor-flow exact expected-scope coverage auditor;
- status/common-stock exact expected-scope coverage auditor;
- status-event structural integrity checks across cleanup/delisting/delisted-price evidence;
- secret-free acquisition receipts binding request/schema/content/route/dataset/client/approval/public-contract provenance;
- acquisition batch manifests rejecting receipt tampering, duplicate receipts and mixed route/dataset/approval/client/schema contracts;
- fail-closed prohibition on implicit zero-flow, invented dates/universe, stale public-evidence fingerprint, mixed source contracts and unstable/missing security identity.

Still missing external evidence:
- an approved/authenticated exact historical KRX route/product;
- route credentials plus a real non-secret authorization-evidence reference for even the tiny Data Marketplace probes;
- real complete historical status/investor-flow data;
- independently attested full expected scope/security mapping;
- record-level historical PIT timestamps/availability evidence;
- exact intended-use rights for the final selected route;
- actual execution/recovery economics where status events affect tradability or liquidation.

Therefore the presence of preflight, receipts, batches and validators does not change any A-F status by itself.

## 8. Evidence required to close the gates

- **Gate A:** approved exact route/product + demonstrated authorized access without exposing credentials. For the current Data Marketplace probe path, credential presence alone is insufficient; `KRX_AUTH_EVIDENCE_REF` must also identify the non-secret approval basis before a tiny request is attempted.
- **Gate B:** exact service/screen/feed identifiers, schema/field mapping, version/transport assumptions and equivalence boundaries for the route actually used.
- **Gate C:** full-period independently attested expected scope and exact observed coverage, including stable security identity; no implicit zeros or generated history.
- **Gate D:** real record-level `event_time`/`published_at`/`available_at`/`ingested_at` lineage and decision eligibility for every historical observation.
- **Gate E:** reproducible authenticated acquisition/normalization/audit artifacts with immutable per-request receipts and consistent batch provenance sufficient to detect drift, mixing or substitution.
- **Gate F:** permitted-use scope for the exact selected route before the corresponding activation stage.

## 9. Non-negotiable separation from model promotion

Even if all A-F gates later become `PASS`, PIT/time consistency, anchored Walk-Forward, Purged/CPCV diagnostics, realistic transaction/execution costs, fill/markout realism, distributional NetEV/tail risk, recency/current evidence, empirical capacity, one-shot sealed holdout, prospective Shadow S1 and frozen Fresh Confirmation S2 remain separate mandatory gates.

No A-F result may weaken q25/abstention, alter TopK/backfill, retune rejected H10/H20 work, reduce costs, mine horizons or otherwise manufacture a promotable result.
