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
| Gate A — `AUTHORIZED_OFFICIAL_ROUTE` | `PARTIAL` | Explicitly consented authenticated status probe Action `36976085781` succeeded. `MDCSTAT21301` trading-halt and `MDCSTAT23701` cleanup-trading candidates were live reachable, along with current identity, new-listing history and delisted-history samples. This closes the prior authenticated-reachability blocker but not the full historical product/access contract, so Gate A is `PARTIAL`, not PASS. |
| Gate B — `EXACT_DATASET_SCHEMA_MAPPING` | `PARTIAL` | Authenticated Action `36976085781` live-validated the exact returned schemas for `MDCSTAT21301` and `MDCSTAT23701`, and also returned new-listing/delisted-history samples. This materially strengthens the status schema map. Gate B remains `PARTIAL` because the complete historical family, exact all-period security mapping and remaining status-route equivalence are not yet closed. |
| Gate C — `HISTORICAL_COVERAGE_SECURITY_MAPPING` | `BLOCKED` | `research_v1_krx_status_coverage.py` can exact-audit caller-attested `(snapshot_date, symbol, isu_cd)` scope, but no authorized full-period scope/history with stable full issue identity has been supplied. |
| Gate D — `PIT_AVAILABILITY_LINEAGE` | `BLOCKED` | Status adapters require availability lineage, but complete historical event/publication/availability/ingestion evidence across all required status families is absent. |
| Gate E — `REPRODUCIBLE_INTEGRITY_FAIL_CLOSED` | `PARTIAL` | Public evidence, structured authorization-evidence validation, network-free readiness, pinned probes, push-safe workflow isolation, workflow-safety regression tests, fail-closed adapters, status coverage/event integrity, immutable acquisition receipts and consistent batch provenance are implemented. Production Action `36956234911` freezes exact-revision OpenAPI response fingerprints, while `research_v1_krx_data_marketplace_route_map.py` fail-closed validates the pinned candidate BLD map. Neither is a full authenticated historical acquisition receipt/batch chain, so Gate E remains `PARTIAL`. |
| Gate F — `INTENDED_USE_RIGHTS` | `PARTIAL` | The 2026-10-02 KRX reply identifies the sender as `krxdata@krx.co.kr` in user-provided email-header metadata and explicitly states that low-frequency **programmatic and automated querying** is permitted for personal non-commercial/internal research without a separate approval procedure. This materially strengthens intended-use rights. Gate F remains `PARTIAL` because bulk/high-frequency collection, redistribution/commercial use, exact BLD-specific rights and full-history acquisition rights are not established. |

Current verdict: `judge_security_status_ready=false`.

## 4. Investor-flow family

Declared source family: `KRX_INVESTOR_FLOW`  
Declared use scope: `INTERNAL_RESEARCH_CANDIDATE_FEATURE_PREPARATION`  
Overall: **OPEN — PERFORMANCE TESTING REMAINS BLOCKED**

| Gate | Status | Current evidence / blocker |
|---|---|---|
| Gate A — `AUTHORIZED_OFFICIAL_ROUTE` | `PARTIAL` | Explicitly consented authenticated investor-flow probe Action `36976873119` succeeded against `MDCSTAT02303`, returning 3 rows for `005930` over `2026-09-21..2026-09-23`. Authenticated reachability is now demonstrated; the full historical access contract remains open, so Gate A is `PARTIAL`, not PASS. |
| Gate B — `EXACT_DATASET_SCHEMA_MAPPING` | `PARTIAL` | Authenticated Action `36976873119` live-validated `MDCSTAT02303` and observed the daily columns `일자, 금융투자, 보험, 투신, 사모, 은행, 기타금융, 연기금 등, 기타법인, 개인, 외국인, 기타외국인, 전체`. Exact full-history service/schema equivalence remains open. |
| Gate C — `HISTORICAL_COVERAGE_SECURITY_MAPPING` | `BLOCKED` | `research_v1_krx_investor_flow_coverage.py` exact-compares caller-attested `(event_date, symbol, isu_cd)` scope to validated observed keys and never invents dates/universe/zeros. No authorized full-period scope/history exists yet. |
| Gate D — `PIT_AVAILABILITY_LINEAGE` | `PARTIAL` | `research_v1_krx_investor_flow_lineage.py` enforces timezone-aware chronology, day-D publication floor >=20:00 KST, current public-contract fingerprint, one source contract and decision-time availability. No real full historical dataset has passed it. |
| Gate E — `REPRODUCIBLE_INTEGRITY_FAIL_CLOSED` | `PARTIAL` | Probe/public evidence, structured authorization-evidence validation, network-free readiness, push-safe workflow isolation, immutable acquisition receipts, batch provenance, PIT and exact coverage validators, and `research_v1_krx_source_data_admission.py` are fail-closed. Bulk authenticated historical retrieval and real-data admission evidence remain unavailable. |
| Gate F — `INTENDED_USE_RIGHTS` | `PARTIAL` | The KRX reply explicitly covers low-frequency programmatic/automated querying for personal non-commercial/internal research without a separate approval procedure, so the automation-permission prerequisite is satisfied for the stated scope. Gate F remains `PARTIAL` because exact `MDCSTAT02303`/BLD-specific rights, bulk/full-history acquisition rights, redistribution and commercial use are not established. |

Current verdict: investor-flow feature-performance experiments remain blocked.

Authorization configuration remains canonical and explicit: `KRX_AUTH_EVIDENCE_REF` identifies the non-secret evidence reference, while `KRX_AUTH_EVIDENCE_JSON` carries the structured non-secret record validated by `research_v1_krx_authorization_evidence.py`. For the Data Marketplace web-session route, that record is insufficient unless it also establishes `automated_collection_authorized=true` from KRX-issued permission evidence.

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

Production server revision `62cb089131ca519815434616dd7f217315fbe346`, Railway deployment `3cc6ffb2-4f11-4582-a5ba-aeca7fb1b681`, and GitHub Smoke Action `36956234911` / job `110667696519` demonstrated authenticated KRX OpenAPI GET access for basis date `20261001` without exposing the authentication key:

- `유가증권 종목기본정보` / `stk_isu_base_info`: HTTP 200, JSON parsed, 942 rows, exact expected schema, schema SHA-256 `11b766977e67ed2f4665a4752a80d18ab76c086d89cf0f853e2642e5575a54e5`, payload SHA-256 `cc64d8b8e9c028ee48a59928195998dfafbfd797587c9f3c1406002a4212792d`.
- `유가증권 일별매매정보` / `stk_bydd_trd`: HTTP 200, JSON parsed, 942 rows, exact expected schema, schema SHA-256 `5d68cce946a3c9361e7d662351f4896518cad40a3804fd262f577ad29d1d56f3`, payload SHA-256 `b5ff8d6894a1956aaf963aa9bad853eff1c3ee465f50f3ab611f7098ca0f93d3`.

This supersedes the older generic statement that no authenticated KRX request had been demonstrated. It does **not** demonstrate an authenticated halt/cleanup/delisting route or investor-flow route, does not establish full history/PIT/use rights, and grants no performance, holdout, promotion or live authority.

### 5.2 Pinned Data Marketplace route map

Canonical records: `INDEXALERT_KRX_DATA_MARKETPLACE_ROUTE_MAP.md` / `.json`.

The project-pinned `beaten-by-the-market/krx-data-api` commit `e6ebac9b71482db127348d8a08ebc6743aa3b50e` maps:
- `MDCSTAT21301` — trading-halt history candidate;
- `MDCSTAT23801` — delisted-status candidate;
- `MDCSTAT23902` — delisted-price candidate;
- `MDCSTAT02303` — per-security investor-flow daily trend candidate.

`MDCSTAT23701` cleanup-trading remains explicitly provisional direct transport because it is not catalogued by the pinned client. The route map is third-party transport evidence only and is validated fail-closed by `research_v1_krx_data_marketplace_route_map.py`. It cannot make Gate A/B pass, cannot prove rights, and cannot authorize bulk history or performance testing.

### 5.3 Data Marketplace automation terms

Canonical audit: `INDEXALERT_KRX_DATA_MARKETPLACE_TERMS_AUDIT.md/.json`.

The current KRX homepage terms make ordinary membership/account access insufficient for automated collection. The subsequent 2026-10-02 KRX reply explicitly permits low-frequency programmatic/automated querying for the stated personal, non-commercial/internal-research scope. Structured permission records validate for both source families. Network-free Action `36973737546` established readiness; authenticated status Action `36976085781` and investor-flow Action `36976873119` subsequently succeeded under separate explicit one-run consent.

### 5.4 User-provided low-frequency internal-research permission reply

Canonical record: `INDEXALERT_KRX_PERMISSION_REPLY_EVIDENCE.md/.json`; fail-closed validator: `research_v1_krx_permission_reply_evidence.py`.

The original screenshot is fingerprinted but not stored in the repository. The user subsequently supplied the email subject, sender `krxdata@krx.co.kr`, reply time `2026-10-02T14:40:00+09:00`, and the full reply text explicitly including `프로그램을 통한 조회 및 자동 조회`. Recipient identity is intentionally redacted. The redacted normalized email-record SHA-256 is `c50a76bb22d8e16b48b9b2eb56c78ab97f620068ed4fae4a65cd4bf6f4ae5f38`.

This allows `automated_collection_authorized=true` for the stated low-frequency personal/non-commercial/internal-research scope and makes the permission-evidence layer eligible for a tiny authenticated probe. It does not authorize bulk history or make Gate A PASS.

### 5.5 Authenticated status tiny probe

Canonical record: `INDEXALERT_KRX_STATUS_TINY_PROBE_EVIDENCE.md/.json`.

Action `36976085781` / job `110740113447` executed the explicitly consented authenticated `KRX_SECURITY_STATUS` tiny probe. Observed safe metadata included:
- current listed identity: 2,873 rows;
- new-listing history sample: 148 rows;
- delisted-history sample: 154 rows;
- `MDCSTAT21301` trading halt: reachable, 1 row;
- `MDCSTAT23701` cleanup trading: reachable, 10 rows.

`candidate_blds_live_validated=true`; `authenticated_request_attempted=true`; numeric market data was not persisted. Gate A is now `PARTIAL`, Gate B remains `PARTIAL`, Gates C/D remain `BLOCKED`, and Judge/holdout/live authority remain false.

### 5.6 Authenticated investor-flow tiny probe

Canonical record: `INDEXALERT_KRX_INVESTOR_FLOW_TINY_PROBE_EVIDENCE.md/.json`.

Action `36976873119` / job `110742487933` executed the explicitly consented authenticated `KRX_INVESTOR_FLOW` tiny probe. `MDCSTAT02303` returned 3 rows for security `005930`, window `2026-09-21..2026-09-23`, with the expected investor-category columns. Numeric market data was not persisted.

Investor-flow Gate A is now `PARTIAL`; Gate B remains `PARTIAL`; Gate C remains `BLOCKED`; Gate D remains `PARTIAL`; feature-performance/holdout/live authority remain false.

## 6. Authorization, readiness and workflow evidence

The production OpenAPI probe is a separate operational path from the Data Marketplace source-probe workflows below. It successfully demonstrated the two exact approved OpenAPI services recorded in `INDEXALERT_KRX_OPENAPI_CONNECTIVITY_EVIDENCE.md`; it must not be re-labeled as status-event or investor-flow acquisition evidence.


Current Data Marketplace request boundary:
- credentials alone do not authorize a request;
- credentials + opaque approval reference still do not authorize a request;
- `research_v1_krx_authorization_evidence.py` must validate a structured non-secret record matching the exact family/route/use-scope/reference;
- `APPROVED` or `PERMITTED_NO_SEPARATE_APPROVAL` active evidence with a KRX issuer, explicit automation permission where required, and valid evidence-document SHA-256 can be sufficient for tiny-probe preflight metadata;
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

- complete approved/attested **historical** status-event and investor-flow acquisition contract beyond the now-completed tiny probes;
- immutable full-history acquisition receipts/batches and exact authenticated route/schema equivalence across the required period;
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
