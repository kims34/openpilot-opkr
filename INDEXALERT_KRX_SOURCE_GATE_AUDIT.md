# IndexAlert KRX Source Gate Audit — A-F

Updated: 2026-10-02 KST  
Branch: `index-alert-research-v1`  
Status: **SOURCE-GOVERNANCE AUDIT — NO ALPHA / HOLDOUT / LIVE AUTHORITY**

## 1. Authority and purpose

This audit applies the frozen A-F contract in `INDEXALERT_KRX_SOURCE_ACCESS_CONTRACT.md`; executable gate semantics live in `research_v1_krx_source_gates.py`.

This document records source readiness only. It does not relax `INDEXALERT_MASTER_SPEC.md`, does not constitute feature-performance evidence, does not consume the one-shot sealed holdout, and cannot authorize Shadow/Paper/Live promotion or live trading.

Allowed states are exactly `PASS`, `PARTIAL`, `BLOCKED`; only `PASS` closes a gate.

## 2. Frozen gate definitions

- **Gate A — `AUTHORIZED_OFFICIAL_ROUTE`**: exact official KRX route/product, route-specific credentials where applicable, validated non-secret authorization evidence and explicit per-run request consent; access routes are not interchangeable.
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
| Gate A — `AUTHORIZED_OFFICIAL_ROUTE` | `BLOCKED` | Authenticated KRX OpenAPI access is now demonstrated in production for the separately enabled `유가증권 종목기본정보` and `유가증권 일별매매정보` services (2026-10-01 basis date, HTTP 200, Action `36952309738`). This proves the OpenAPI transport/key works for those exact services only. The declared `KRX_SECURITY_STATUS` family still lacks an exact approved/authenticated route for trading-halt, cleanup-trading and actual-delisting history, and the canonical structured authorization-evidence / source-acquisition chain for that status route remains incomplete. Therefore Gate A for the declared status family stays `BLOCKED`. |
| Gate B — `EXACT_DATASET_SCHEMA_MAPPING` | `PARTIAL` | Exact live schemas are now verified for `유가증권 종목기본정보` (`stk_isu_base_info`) and `유가증권 일별매매정보` (`stk_bydd_trd`): both returned 942 rows for `20261001`, and the observed fields matched the KRX development specifications. Public contracts MDCSTAT213/237/238/239 and status semantics are identified, but exact approved historical transport/schema equivalence for halt/cleanup/delisting status and the stable full issue-ID contract for Final Judge remain unfrozen. |
| Gate C — `HISTORICAL_COVERAGE_SECURITY_MAPPING` | `BLOCKED` | `research_v1_krx_status_coverage.py` can exact-audit caller-attested `(snapshot_date, symbol, isu_cd)` scope, but no authorized full-period scope/history with stable full issue identity has been supplied. |
| Gate D — `PIT_AVAILABILITY_LINEAGE` | `BLOCKED` | Status adapters require availability lineage, but complete historical event/publication/availability/ingestion evidence across all required status families is absent. |
| Gate E — `REPRODUCIBLE_INTEGRITY_FAIL_CLOSED` | `PARTIAL` | Public evidence, structured authorization-evidence validation, network-free readiness, pinned probes, push-safe workflow isolation, workflow-safety regression tests, fail-closed adapters, status coverage/event integrity, immutable acquisition receipts and consistent batch provenance are implemented. Production Action `36952309738` additionally freezes exact-revision sanitized OpenAPI connectivity/schema evidence for the two enabled services. That startup probe is not a full historical acquisition receipt/batch chain, so Gate E remains `PARTIAL`. |
| Gate F — `INTENDED_USE_RIGHTS` | `PARTIAL` | Current OpenAPI terms are audited as non-commercial/no-third-party-distribution; exact rights for the final selected historical route/product remain unverified. |

Current verdict: `judge_security_status_ready=false`.

## 4. Investor-flow family

Declared source family: `KRX_INVESTOR_FLOW`  
Declared use scope: `INTERNAL_RESEARCH_CANDIDATE_FEATURE_PREPARATION`  
Overall: **OPEN — PERFORMANCE TESTING REMAINS BLOCKED**

| Gate | Status | Current evidence / blocker |
|---|---|---|
| Gate A — `AUTHORIZED_OFFICIAL_ROUTE` | `BLOCKED` | Data Marketplace preflight now requires `KRX_ID` + `KRX_PW` + non-secret `KRX_AUTH_EVIDENCE_REF` + a matching validated `KRX_AUTH_EVIDENCE_JSON` record + exact explicit per-run consent. OpenAPI key cannot substitute. Network-free readiness can validate configuration while forcibly disabling consent. No authorized authenticated investor-flow request has been demonstrated. |
| Gate B — `EXACT_DATASET_SCHEMA_MAPPING` | `PARTIAL` | Official stock investor-trading screen family is known and exploratory mapping points to MDCSTAT02303, but exact approved historical transport/OpenAPI equivalence remains unestablished. |
| Gate C — `HISTORICAL_COVERAGE_SECURITY_MAPPING` | `BLOCKED` | `research_v1_krx_investor_flow_coverage.py` exact-compares caller-attested `(event_date, symbol, isu_cd)` scope to validated observed keys and never invents dates/universe/zeros. No authorized full-period scope/history exists yet. |
| Gate D — `PIT_AVAILABILITY_LINEAGE` | `PARTIAL` | `research_v1_krx_investor_flow_lineage.py` enforces timezone-aware chronology, day-D publication floor >=20:00 KST, current public-contract fingerprint, one source contract and decision-time availability. No real full historical dataset has passed it. |
| Gate E — `REPRODUCIBLE_INTEGRITY_FAIL_CLOSED` | `PARTIAL` | Probe/public evidence, structured authorization-evidence validation, network-free readiness, push-safe workflow isolation, immutable acquisition receipts, batch provenance, PIT and exact coverage validators, and `research_v1_krx_source_data_admission.py` are fail-closed. Bulk authenticated historical retrieval and real-data admission evidence remain unavailable. |
| Gate F — `INTENDED_USE_RIGHTS` | `PARTIAL` | Current public OpenAPI restrictions are frozen; exact rights for the selected investor-flow route/use scope remain unverified. |

Current verdict: investor-flow feature-performance experiments remain blocked.

## 5. Official public evidence

Machine-readable public evidence is frozen in `research_v1_krx_public_evidence.py` version `2026-10-02.v2`, fingerprint:
`39f357fda6eec5bb994f1dcba1ba44ed913714df256ec6b542b5aeadf14a0380`.

The 2026-10-01 official public re-audit established:
1. OpenAPI authentication-key approval and per-service utilization approval are separate requirements; `AUTH_KEY` alone is not dataset authorization.
2. OpenAPI service/history mappings are service-specific; a similarly named service cannot be assumed equivalent to a Data Marketplace screen.
3. The June 2026 notice `KRX Open API 미제공 데이터에 대한 안내` exists, but no specific IndexAlert-required dataset is classified available/unavailable from the notice without its exact dataset list.
4. MDCSTAT237/238/239 public pages support cleanup/delisting/delisted regular-session schema semantics.
5. Same-day final investor trading details are provided after 20:00.
6. Korean OpenAPI terms effective 2025-12-26 restrict use to non-commercial purposes, prohibit charging/providing KRX-received information to third parties, and include request-rate/attribution/contract-end controls.

These facts improve Gate B/F evidence only; they do not close A/C/D/E.

### 5.1 Authenticated OpenAPI production evidence — 2026-10-02

Canonical record: `INDEXALERT_KRX_OPENAPI_CONNECTIVITY_EVIDENCE.md` and `INDEXALERT_KRX_OPENAPI_CONNECTIVITY_EVIDENCE.json`.

Production server revision `62cb089131ca519815434616dd7f217315fbe346`, Railway deployment `3cc6ffb2-4f11-4582-a5ba-aeca7fb1b681`, and GitHub Smoke Action `36952309738` / job `110667696519` demonstrated authenticated KRX OpenAPI GET access for basis date `20261001` without exposing the authentication key:

- `유가증권 종목기본정보` / `stk_isu_base_info`: HTTP 200, JSON parsed, 942 rows, exact expected schema.
- `유가증권 일별매매정보` / `stk_bydd_trd`: HTTP 200, JSON parsed, 942 rows, exact expected schema.

This supersedes the older generic statement that no authenticated KRX request had been demonstrated. It does **not** demonstrate an authenticated halt/cleanup/delisting route or investor-flow route, does not establish full history/PIT/use rights, and grants no performance, holdout, promotion or live authority.

## 6. Authorization, readiness and workflow evidence

The production OpenAPI probe is a separate operational path from the Data Marketplace source-probe workflows below. It successfully demonstrated the two exact approved OpenAPI services recorded in `INDEXALERT_KRX_OPENAPI_CONNECTIVITY_EVIDENCE.md`; it must not be re-labeled as status-event or investor-flow acquisition evidence.


Current Data Marketplace request boundary:
- credentials alone do not authorize a request;
- credentials + opaque approval reference still do not authorize a request;
- `research_v1_krx_authorization_evidence.py` must validate a structured non-secret record matching the exact family/route/use-scope/reference;
- only `APPROVED` active evidence with a KRX issuer and valid evidence-document SHA-256 can be sufficient for tiny-probe preflight metadata;
- even valid structured evidence caps Gate-A evidence at `PARTIAL` and grants no bulk/performance/holdout/promotion/live authority;
- the exact sentinel `KRX_EXPLICIT_PROBE_CONSENT=ALLOW_TINY_AUTHENTICATED_REQUEST` is additionally required;
- generic values such as `true`, `1` or `yes` are rejected;
- push workflows pass no KRX credentials/evidence JSON to the probe process and run dry-run only;
- authenticated probe steps are eligible only on explicit `workflow_dispatch` with `allow_authenticated_request=true`.

The network-free readiness layer forcibly disables explicit consent even if the caller supplies it. It reports only presence/validation/fingerprint metadata plus missing requirements and hard-codes `request_attempt_authorized=false`, `authenticated_request_attempted=false` and `network_request_attempted=false`. `.github/workflows/indexalert-research-v1-krx-auth-readiness.yml` is manual-only, installs no KRX client and invokes no probe script.

Latest push-safe workflow evidence before structured-evidence hardening:
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
- `36816437900` — structured-evidence workflow-safety integration/full KRX integrity suite: **success**.

Transient implementation-test failures were corrected without weakening any A-F gate, research threshold, economic criterion or promotion boundary.

## 7. Internal chain now frozen

Future real KRX history must follow:

`structured authorization-evidence validation -> network-free auth readiness -> explicit manual request consent -> authorization preflight -> tiny authenticated probe/acquisition -> immutable receipt -> consistent receipt batch -> PIT lineage -> exact expected-scope coverage -> A-F audit -> source-data admission -> separate experiment-registry/preregistration review`

`research_v1_krx_source_data_admission.py` requires, for investor flow, a closed A-F contract, valid untampered batch, current public evidence, structurally valid PIT lineage, exact coverage, and matching source family/use scope before setting `source_data_structurally_admissible=true`.

Even then it sets only `eligible_for_experiment_registry_review=true`. It deliberately keeps:
- `feature_performance_testing_authorized=false`;
- `sealed_holdout_authorized=false`;
- `alpha_or_final_judge_promotion_authorized=false`;
- `live_trading_authorized=false`.

Therefore no authorization/readiness/infrastructure-only success can skip the Research Ledger/preregistration gate.

## 8. External evidence still missing

- approved/authenticated exact historical **status-event and investor-flow** route/product (basic security-master/daily-trade OpenAPI connectivity is now proven separately);
- route-specific non-secret authorization-evidence references and matching structured authorization-evidence records for the still-unresolved status/investor routes;
- network-free readiness and explicitly consented tiny-probe evidence for those still-unresolved routes where the canonical research preflight applies;
- complete historical status/investor-flow data;
- independently attested full expected scope/stable security mapping;
- record-level historical PIT timestamps/availability;
- exact rights for the selected route/use scope;
- actual execution/recovery economics where status events affect tradability/liquidation.

The presence of structured-evidence validators, readiness, preflight, workflow consent controls, receipts, batches, validators and admission code does not change A-F states by itself.

## 9. Evidence required to close gates

- **Gate A:** for each declared source family, approved exact route/product, matching validated structured authorization evidence, and demonstrated authorized access without exposing credentials. The successful basic-info/daily-trade OpenAPI proof does not substitute for the unresolved status-event or investor-flow route.
- **Gate B:** exact service/screen/feed, schema, version/transport and equivalence boundaries for the actual route.
- **Gate C:** full-period attested expected scope + exact observed coverage + stable security identity.
- **Gate D:** real record-level PIT lineage and decision eligibility.
- **Gate E:** reproducible authenticated acquisition with immutable per-request receipts, consistent batches, fail-closed normalization/audits and no substitution/drift.
- **Gate F:** permitted-use scope for the exact selected route before activation.

## 10. Non-negotiable promotion separation

Even all A-F `PASS` remains separate from PIT/time consistency, anchored Walk-Forward, Purged/CPCV, realistic costs/fills, distributional NetEV/tails, recency, capacity, one-shot sealed holdout, prospective Shadow S1 and frozen Fresh Confirmation S2.

No A-F/source-data result may weaken q25/abstention, alter TopK/backfill, retune rejected H10/H20 work, reduce costs, mine horizons or otherwise manufacture a promotable result.
