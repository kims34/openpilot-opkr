# IndexAlert KRX Source Gate Audit — A-F

Updated: 2026-10-01 KST  
Branch: `index-alert-research-v1`  
Status: **SOURCE-GOVERNANCE AUDIT — NO ALPHA / HOLDOUT / LIVE AUTHORITY**

## 1. Authority and purpose

This audit applies the frozen A-F contract in `INDEXALERT_KRX_SOURCE_ACCESS_CONTRACT.md`; executable gate semantics live in `research_v1_krx_source_gates.py`.

This document records source readiness only. It does not relax `INDEXALERT_MASTER_SPEC.md`, does not constitute feature-performance evidence, does not consume the one-shot sealed holdout, and cannot authorize Shadow/Paper/Live promotion or live trading.

Allowed states are exactly `PASS`, `PARTIAL`, `BLOCKED`; only `PASS` closes a gate.

## 2. Frozen gate definitions

- **Gate A — `AUTHORIZED_OFFICIAL_ROUTE`**: exact official KRX route/product, appropriate authorization and explicit per-run request consent; access routes are not interchangeable.
- **Gate B — `EXACT_DATASET_SCHEMA_MAPPING`**: exact API service/screen/feed and required schema verified; similar names/provisional transports are insufficient.
- **Gate C — `HISTORICAL_COVERAGE_SECURITY_MAPPING`**: full requested history/relevant securities, stable mapping and common-stock identity where required.
- **Gate D — `PIT_AVAILABILITY_LINEAGE`**: explicit `event_time`, `published_at` where applicable, `available_at`, `ingested_at` and decision eligibility.
- **Gate E — `REPRODUCIBLE_INTEGRITY_FAIL_CLOSED`**: reproducible/auditable retrieval and provenance; ambiguity/substitution fails closed.
- **Gate F — `INTENDED_USE_RIGHTS`**: use/licensing rights verified for the declared scope; internal and external/commercial scopes are separate.

## 3. Security/status family

Declared source family: `KRX_SECURITY_STATUS`  
Declared use scope: `INTERNAL_RESEARCH_AND_FINAL_JUDGE_INPUT_PREPARATION`  
Overall: **OPEN — NOT ALL A-F PASS**

| Gate | Status | Current evidence / blocker |
|---|---|---|
| Gate A — `AUTHORIZED_OFFICIAL_ROUTE` | `BLOCKED` | `research_v1_krx_auth_preflight.py` requires route-specific credentials, a non-secret authorization-evidence reference and exact per-run explicit consent before a tiny authenticated request. `research_v1_krx_auth_readiness.py` can verify prerequisite presence without permitting or attempting a network request. Push Action `36813950791` ran dry-run only and skipped the authenticated step. No authorized authenticated KRX status request has been demonstrated. |
| Gate B — `EXACT_DATASET_SCHEMA_MAPPING` | `PARTIAL` | Public contracts MDCSTAT213/237/238/239 and status semantics are identified, but exact approved historical transport/schema equivalence and stable full issue-ID contract for Final Judge remain unfrozen. |
| Gate C — `HISTORICAL_COVERAGE_SECURITY_MAPPING` | `BLOCKED` | `research_v1_krx_status_coverage.py` can exact-audit caller-attested `(snapshot_date, symbol, isu_cd)` scope, but no authorized full-period scope/history with stable full issue identity has been supplied. |
| Gate D — `PIT_AVAILABILITY_LINEAGE` | `BLOCKED` | Status adapters require availability lineage, but complete historical event/publication/availability/ingestion evidence across all required status families is absent. |
| Gate E — `REPRODUCIBLE_INTEGRITY_FAIL_CLOSED` | `PARTIAL` | Public evidence, network-free readiness, pinned probes, push-safe workflow isolation, workflow-safety regression tests, fail-closed adapters, status coverage/event integrity, immutable acquisition receipts and consistent batch provenance are implemented. No authenticated end-to-end full historical acquisition has yet demonstrated the real-data chain. |
| Gate F — `INTENDED_USE_RIGHTS` | `PARTIAL` | Current OpenAPI terms are audited as non-commercial/no-third-party-distribution; exact rights for the final selected historical route/product remain unverified. |

Current verdict: `judge_security_status_ready=false`.

## 4. Investor-flow family

Declared source family: `KRX_INVESTOR_FLOW`  
Declared use scope: `INTERNAL_RESEARCH_CANDIDATE_FEATURE_PREPARATION`  
Overall: **OPEN — PERFORMANCE TESTING REMAINS BLOCKED**

| Gate | Status | Current evidence / blocker |
|---|---|---|
| Gate A — `AUTHORIZED_OFFICIAL_ROUTE` | `BLOCKED` | Data Marketplace preflight requires `KRX_ID` + `KRX_PW` + non-secret `KRX_AUTH_EVIDENCE_REF` + the exact explicit per-run consent sentinel; OpenAPI key cannot substitute. The network-free readiness layer can verify whether credential/reference prerequisites are configured while forcibly disabling consent. Push Action `36813973236` completed dry-run and skipped the authenticated step. No authorized authenticated investor-flow request has been demonstrated. |
| Gate B — `EXACT_DATASET_SCHEMA_MAPPING` | `PARTIAL` | Official stock investor-trading screen family is known and exploratory mapping points to MDCSTAT02303, but exact approved historical transport/OpenAPI equivalence remains unestablished. |
| Gate C — `HISTORICAL_COVERAGE_SECURITY_MAPPING` | `BLOCKED` | `research_v1_krx_investor_flow_coverage.py` exact-compares caller-attested `(event_date, symbol, isu_cd)` scope to validated observed keys and never invents dates/universe/zeros. No authorized full-period scope/history exists yet. |
| Gate D — `PIT_AVAILABILITY_LINEAGE` | `PARTIAL` | `research_v1_krx_investor_flow_lineage.py` enforces timezone-aware chronology, day-D publication floor >=20:00 KST, current public-contract fingerprint, one source contract and decision-time availability. No real full historical dataset has passed it. |
| Gate E — `REPRODUCIBLE_INTEGRITY_FAIL_CLOSED` | `PARTIAL` | Probe/public evidence, network-free readiness, push-safe workflow isolation, immutable acquisition receipts, batch provenance, PIT and exact coverage validators, and `research_v1_krx_source_data_admission.py` are fail-closed. Bulk authenticated historical retrieval and real-data admission evidence remain unavailable. |
| Gate F — `INTENDED_USE_RIGHTS` | `PARTIAL` | Current public OpenAPI restrictions are frozen; exact rights for the selected investor-flow route/use scope remain unverified. |

Current verdict: investor-flow feature-performance experiments remain blocked.

## 5. Official public evidence

Machine-readable public evidence is frozen in `research_v1_krx_public_evidence.py` version `2026-10-01.v1`, fingerprint:
`349d310647c78412e45ac13078259bab2d002958db597b2f7dd26228f8b3ca7b`.

The 2026-10-01 official public re-audit established:
1. OpenAPI authentication-key approval and per-service utilization approval are separate requirements; `AUTH_KEY` alone is not dataset authorization.
2. OpenAPI service/history mappings are service-specific; a similarly named service cannot be assumed equivalent to a Data Marketplace screen.
3. The June 2026 notice `KRX Open API 미제공 데이터에 대한 안내` exists, but no specific IndexAlert-required dataset is classified available/unavailable from the notice without its exact dataset list.
4. MDCSTAT237/238/239 public pages support cleanup/delisting/delisted regular-session schema semantics.
5. Same-day final investor trading details are provided after 20:00.
6. Korean OpenAPI terms effective 2025-12-26 restrict use to non-commercial purposes, prohibit charging/providing KRX-received information to third parties, and include request-rate/attribution/contract-end controls.

These facts improve Gate B/F evidence only; they do not close A/C/D/E.

## 6. Authorization, readiness and workflow evidence

Current Data Marketplace request boundary:
- credentials alone do not authorize a request;
- credentials + approval reference still do not authorize a request;
- the exact sentinel `KRX_EXPLICIT_PROBE_CONSENT=ALLOW_TINY_AUTHENTICATED_REQUEST` is additionally required;
- generic values such as `true`, `1` or `yes` are rejected;
- push workflows pass no KRX credentials to the probe process and run dry-run only;
- authenticated probe steps are eligible only on explicit `workflow_dispatch` with `allow_authenticated_request=true`.

The new readiness boundary is stricter than a probe: `research_v1_krx_auth_readiness.py` forcibly disables explicit consent even if the caller supplies it, reports only secret-presence/configuration booleans plus missing requirements, and hard-codes `request_attempt_authorized=false`, `authenticated_request_attempted=false` and `network_request_attempted=false`. `.github/workflows/indexalert-research-v1-krx-auth-readiness.yml` is manual-only, installs no KRX client and invokes no probe script.

Latest push-safe workflow evidence:
- **Status Action `36813950791`** — overall success; push-safe dry-run status diagnostic success; explicitly consented authenticated status probe skipped.
- **Investor Action `36813973236`** — overall success; push-safe dry-run investor-flow diagnostic success; explicitly consented authenticated investor-flow probe skipped.

Earlier preflight-bound diagnostic artifacts remain useful as evidence that the runtime had no configured KRX credentials/reference at that time:
- **Status `36811927281`** — `AUTHORIZATION_PREFLIGHT_BLOCKED`, no authenticated request; artifact `11140235232`.
- **Investor `36811913060`** — `AUTHORIZATION_PREFLIGHT_BLOCKED`, no authenticated request; artifact `11140075783`.

Key integrity Actions:
- `36809680268` — investor PIT lineage: **success**.
- `36809948775` — investor exact coverage: **success**.
- `36810309522` — status exact coverage after empty-schema implementation fix: **success**.
- `36811118588` — status event integrity: **success**.
- `36811648510` — secret-free acquisition receipt: **success**.
- `36812137960` — auth preflight + exact credential-value redaction: **success**.
- `36812299630` — acquisition batch integrity: **success**.
- `36812655201` — source-data admission: **success**.
- `36813918295` — explicit-consent probe code/unit tests: **success**.
- `36814088731` — explicit per-run consent contract/full KRX integrity suite: **success**.
- `36814594395` — network-free auth readiness + workflow-safety regression tests/full KRX integrity suite: **success**.

Transient implementation-test failures were corrected without weakening any A-F gate, research threshold, economic criterion or promotion boundary.

## 7. Internal chain now frozen

Future real KRX history must follow:

`network-free auth readiness -> explicit manual request consent -> authorization preflight -> tiny authenticated probe/acquisition -> immutable receipt -> consistent receipt batch -> PIT lineage -> exact expected-scope coverage -> A-F audit -> source-data admission -> separate experiment-registry/preregistration review`

`research_v1_krx_source_data_admission.py` requires, for investor flow, a closed A-F contract, valid untampered batch, current public evidence, structurally valid PIT lineage, exact coverage, and matching source family/use scope before setting `source_data_structurally_admissible=true`.

Even then it sets only `eligible_for_experiment_registry_review=true`. It deliberately keeps:
- `feature_performance_testing_authorized=false`;
- `sealed_holdout_authorized=false`;
- `alpha_or_final_judge_promotion_authorized=false`;
- `live_trading_authorized=false`.

Therefore no readiness/infrastructure-only success can skip the Research Ledger/preregistration gate.

## 8. External evidence still missing

- approved/authenticated exact historical KRX route/product;
- route credentials plus real non-secret authorization-evidence reference;
- a successful network-free readiness result after those are configured;
- one explicitly consented manual tiny probe demonstrating the approved route without exposing credentials;
- complete historical status/investor-flow data;
- independently attested full expected scope/stable security mapping;
- record-level historical PIT timestamps/availability;
- exact rights for the selected route/use scope;
- actual execution/recovery economics where status events affect tradability/liquidation.

The presence of readiness, preflight, workflow consent controls, receipts, batches, validators and admission code does not change A-F states by itself.

## 9. Evidence required to close gates

- **Gate A:** approved exact route/product plus explicitly consented demonstrated authorized access, without exposing credentials. A readiness result alone is not access evidence.
- **Gate B:** exact service/screen/feed, schema, version/transport and equivalence boundaries for the actual route.
- **Gate C:** full-period attested expected scope + exact observed coverage + stable security identity.
- **Gate D:** real record-level PIT lineage and decision eligibility.
- **Gate E:** reproducible authenticated acquisition with immutable per-request receipts, consistent batches, fail-closed normalization/audits and no substitution/drift.
- **Gate F:** permitted-use scope for the exact selected route before activation.

## 10. Non-negotiable promotion separation

Even all A-F `PASS` remains separate from PIT/time consistency, anchored Walk-Forward, Purged/CPCV, realistic costs/fills, distributional NetEV/tails, recency, capacity, one-shot sealed holdout, prospective Shadow S1 and frozen Fresh Confirmation S2.

No A-F/source-data result may weaken q25/abstention, alter TopK/backfill, retune rejected H10/H20 work, reduce costs, mine horizons or otherwise manufacture a promotable result.
