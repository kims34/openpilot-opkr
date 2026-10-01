# IndexAlert KRX Source Access Contract

Updated: 2026-10-01 KST  
Branch: `index-alert-research-v1`  
Status: **SOURCE / LICENSING CONTRACT — NO ALPHA CLAIM**

## 1. Purpose

This document prevents IndexAlert from confusing distinct KRX data-access products, authentication methods, authorization evidence, runtime consent, acquisition provenance and licensing terms. It is source-governance infrastructure only. Nothing here is performance evidence and nothing here authorizes sealed-holdout use or live trading.

## 2. Frozen KRX source gates A-F

The following six gates are the canonical source-governance contract for every KRX data family used by IndexAlert. They do **not** weaken or replace any statistical, PIT, execution, NetEV, holdout or prospective-promotion rule.

### Gate A — `AUTHORIZED_OFFICIAL_ROUTE`

The exact official KRX access route/product must be identified and the dataset must be accessed under the appropriate authorization. KRX OpenAPI `AUTH_KEY`, Data Marketplace authenticated web-session credentials and purchased/distributed data products are distinct routes and must never be substituted for one another.

**Credential presence is not authorization, and authorization metadata is not runtime consent.** For any online route, IndexAlert must preserve a non-secret authorization/approval evidence reference separately from the credential itself. A tiny authenticated reachability probe may be attempted only after the route-specific preflight is satisfied **and** the exact per-run explicit-consent sentinel is present. Successful reachability may contribute only partial Gate-A evidence; it can never make Gate A `PASS` by itself.

Normal push-triggered diagnostics are dry-run only. Pushes must not inject KRX credentials into the probe process and must never trigger an authenticated request merely because repository secrets happen to be configured.

### Gate B — `EXACT_DATASET_SCHEMA_MAPPING`

The exact API service, screen/feed contract and required fields/schema must be verified for the intended data family. A similarly named public API, a screen whose fields/history have not been verified, or a provisional low-level transport does not close this gate.

### Gate C — `HISTORICAL_COVERAGE_SECURITY_MAPPING`

Historical coverage must span the requested research/Final-Judge period and all relevant securities, with stable security mapping and common-stock identity where required. A non-empty probe result or a current-only snapshot is not evidence of complete historical coverage. Expected dates/security scope must be independently attested; missing rows may not be silently converted into zeros or generated history.

### Gate D — `PIT_AVAILABILITY_LINEAGE`

Point-in-time lineage must be explicit: `event_time`, `published_at` when applicable, `available_at` and `ingested_at` must be preserved, and no value may be used before it was officially available. Final day-D investor flow is eligible only for the next decision after its official publication time.

### Gate E — `REPRODUCIBLE_INTEGRITY_FAIL_CLOSED`

Retrieval and source metadata must be reproducible and auditable. Source/schema ambiguity must fail closed. Undocumented proxies, synthetic substitutions or source-route impersonation are forbidden. Source reachability by itself does not close this gate.

Every future authenticated acquisition used for research evidence must produce a **secret-free immutable acquisition receipt** binding at least the declared source family/use scope, access route, exact dataset identifier, non-secret authorization-evidence reference, client revision, timezone-aware retrieval time, request-metadata fingerprint, response-schema fingerprint, response-content fingerprint and current public-contract-evidence fingerprint.

Multiple acquisitions belonging to one logical historical dataset must additionally pass a **batch provenance** check. Duplicate/tampered receipts or silent mixing of access route, dataset, intended-use scope, authorization reference, client revision, schema or public-contract evidence fail closed.

Receipt or batch validity is provenance evidence only. It does not establish historical coverage, PIT validity, Alpha, holdout readiness or live-trading authority.

### Gate F — `INTENDED_USE_RIGHTS`

Data-use/licensing rights must be explicitly verified for the intended use scope. Internal research/personal validation and future external/commercial product use are separate scopes and must not be conflated.

### Closure semantics

Each gate has exactly one audit status: `PASS`, `PARTIAL` or `BLOCKED`.

- Only `PASS` closes a gate.
- `PARTIAL` is explicitly **not** a pass and cannot be promoted by inference.
- Any `PARTIAL` or `BLOCKED` result keeps the source contract open for that declared source family/use scope.
- **All six gates passing means only** that the KRX source contract for the declared scope is closed. It does **not** by itself authorize Alpha/Final-Judge promotion, sealed-holdout consumption, Shadow/Paper/Live promotion or live trading.
- Existing PIT/time-consistency, anchored Walk-Forward, Purged/CPCV, realistic execution-cost/fill, distributional NetEV, tail-risk, recency, holdout and prospective confirmation gates remain independent and mandatory.

Executable gate semantics are frozen in `research_v1_krx_source_gates.py`; the current evidence assessment is `INDEXALERT_KRX_SOURCE_GATE_AUDIT.md`.

## 3. Authorization and runtime-consent preflight contract

`research_v1_krx_auth_preflight.py` is the canonical pre-request guard.

### Data Marketplace web-session route

A tiny authenticated probe requires all of:
- `KRX_ID` present through secret management;
- `KRX_PW` present through secret management;
- non-secret `KRX_AUTH_EVIDENCE_REF` identifying the approval/authorization basis;
- exact runtime sentinel `KRX_EXPLICIT_PROBE_CONSENT=ALLOW_TINY_AUTHENTICATED_REQUEST` for that specific run.

`KRX_AUTH_EVIDENCE_REF` is an opaque reference only. It must not contain a password, token, cookie, API key, bearer token or session identifier. Its presence is necessary for the probe but is not itself proof that Gate A passes.

The explicit-consent sentinel is deliberately exact. Generic values such as `true`, `1`, `yes` or similar text are not accepted. The sentinel is not a persistent authorization grant and must not be stored as a substitute for the per-run workflow control.

### KRX OpenAPI route

A tiny OpenAPI request requires all of:
- `KRX_OPENAPI_AUTH_KEY` present through secret management;
- exact approved OpenAPI service mapping for the dataset;
- non-secret authorization-evidence reference for the relevant service approval;
- the same exact explicit per-run request-consent sentinel.

An `AUTH_KEY` alone is not authorization for every KRX API and cannot substitute for Data Marketplace session credentials.

### Purchased/distributed-data route

Purchased/distributed product access must be verified by a product-specific ingestion/authorization contract. Online `KRX_ID`/`KRX_PW` or OpenAPI `AUTH_KEY` cannot be used to infer this route is authorized.

### Workflow execution boundary

The two current Data Marketplace probe workflows are frozen as follows:
- `push` events run a dry-run diagnostic only;
- dry-run steps receive empty KRX credential/authorization/consent environment values;
- the authenticated step is skipped on push;
- an authenticated tiny probe is eligible only on `workflow_dispatch` when `allow_authenticated_request=true` is explicitly selected;
- only that authenticated manual step receives `KRX_ID`/`KRX_PW`, an authorization-evidence reference and the exact consent sentinel;
- `KRX_OPENAPI_AUTH_KEY` is not injected into these Data Marketplace probe steps.

This workflow boundary is defense in depth. The Python preflight independently enforces the same consent sentinel, so a future workflow mistake or local invocation must still fail closed without the sentinel.

### Preflight authority boundary

A positive preflight may authorize only the explicitly declared tiny source request. It must keep:
- bulk historical acquisition authority = false unless separately approved;
- feature-performance testing authority = false;
- sealed-holdout authority = false;
- Alpha/Final-Judge promotion authority = false;
- live-trading authority = false.

## 4. Distinct KRX access routes

### Route 1 — KRX OpenAPI

Official KRX OpenAPI uses a separate authentication-key workflow:
1. register/login to KRX Data Marketplace;
2. apply for an API authentication key;
3. wait for administrator approval;
4. identify the desired API service through the official service list/specification;
5. apply for use of that individual API service;
6. wait for service approval;
7. call only that approved service with the authentication key in the `AUTH_KEY` request header.

An OpenAPI key therefore does not by itself authorize every API service. IndexAlert must not use an OpenAPI key for a dataset until the exact service, schema/history and approval state are frozen.

### Route 2 — KRX Data Marketplace authenticated web session

The current feasibility probes are explicitly Data Marketplace web-session probes through a pinned exploratory client. They may attempt an authenticated request only when `KRX_ID`, `KRX_PW`, `KRX_AUTH_EVIDENCE_REF` **and** the exact explicit per-run consent sentinel satisfy the preflight.

Candidate low-level BLDs or screen transports remain provisional until live authorized responses, exact schema equivalence, historical coverage and PIT lineage are validated.

`KRX_ID` / `KRX_PW` must never be described as OpenAPI `AUTH_KEY` authentication. A green push workflow whose authenticated step was skipped is diagnostic execution evidence only.

### Route 3 — KRX data purchase / distribution products

Purchased/distributed data products are separate access/licensing routes from the free/public OpenAPI catalog and from authenticated web-session screens. The existence of a feed, screen or API name does not imply another route may legally or technically substitute for it.

## 5. Required IndexAlert data families

### Security/status Final Judge data

Required official history includes at least:
- common-stock identity / stable security mapping;
- trading-halt history;
- cleanup-trading status;
- actual delisting status;
- delisted-security price/economic history sufficient to model exact outcomes.

Known official Data Marketplace screen contracts include MDCSTAT213, MDCSTAT237, MDCSTAT238 and MDCSTAT239. Their existence is not enough. Before Judge readiness, IndexAlert requires an authorized reproducible route, complete history, stable identity, PIT availability and exact status/economic joins.

Current public schema evidence supports:
- **MDCSTAT237:** cleanup-trading interval, scheduled delisting and reason fields;
- **MDCSTAT238:** actual delisting status/date/reason and related identity fields, based on the last trading day immediately before delisting;
- **MDCSTAT239:** delisted-security regular-session (09:00-15:30) price/volume/value/capitalization history.

These confirmations strengthen Gate B evidence but do not establish an authorized historical retrieval route, complete history or exact public OpenAPI mapping.

### Investor-flow candidate family

KRX publicly lists stock `투자자별 거래실적` and `투자자별 거래실적(개별종목)`. The official investor-trading page states final day-D results are provided after 20:00. Therefore final day-D investor flow can only enter the **next eligible decision after publication**; same-day use before publication is forbidden.

Before any investor-flow performance experiment, real data must establish:
- authorized reproducible source;
- historical coverage and stable security mapping;
- `event_time`, `published_at`, `available_at`, `ingested_at`;
- immutable acquisition provenance;
- exact intended-use rights;
- fail-closed handling of missing/unavailable observations.

A source/authentication probe alone is not feature-performance evidence.

## 6. Public OpenAPI mapping and current public evidence

Machine-readable official-public evidence is frozen in `research_v1_krx_public_evidence.py`, version `2026-10-01.v1`, fingerprint:
`349d310647c78412e45ac13078259bab2d002958db597b2f7dd26228f8b3ca7b`.

The 2026-10-01 public re-audit establishes the OpenAPI key + per-service approval model, public status-screen semantics, final investor-result after-20:00 rule and current OpenAPI-use restrictions. It also confirms that the KRX OpenAPI site has a June 2026 notice titled `KRX Open API 미제공 데이터에 대한 안내`; because the retrievable notice body did not reliably expose a dataset list, no specific IndexAlert-required dataset may be inferred available or unavailable from that notice alone.

Frozen mapping rules:
- a Data Marketplace screen name is not an OpenAPI service ID;
- a similarly named OpenAPI service is not equivalent without schema/history verification;
- a provisional BLD is not an approved OpenAPI mapping;
- absence from public search/index results is not proof a service does not exist;
- if an exact official service is later verified, implement it as a separate adapter with explicit service ID, schema, approval state, coverage and PIT contract.

## 7. Licensing / product boundary

The current Korean KRX OpenAPI terms are effective from **2025-12-26** and include controls that:
- limit API use to **non-commercial purposes**;
- prohibit charging third parties for API results;
- prohibit providing KRX-received information to third parties;
- limit one authentication key to at most **10,000 requests/day** unless KRX otherwise limits the service;
- require applicable KRX-statistics attribution for screens built from results;
- require use to cease when the usage contract expires/terminates.

Consequences for IndexAlert:
- internal research/personal validation and external/commercial product distribution are separate compliance questions;
- a future paid/external IndexAlert product must not assume free OpenAPI rights permit redistribution or third-party delivery;
- licensing compliance is a product activation gate independent of statistical Alpha promotion;
- request-rate/service-specific constraints remain binding even for authorized internal acquisition.

This contract freezes an engineering/compliance boundary; exact rights must be verified for the actual route/product before activation.

## 8. Acquisition provenance and source-data admission

### Per-acquisition receipt

`research_v1_krx_acquisition_receipt.py` must generate a metadata-only receipt for every acquisition intended to contribute source evidence. Numeric market rows need not be embedded in the receipt; instead the response content is fingerprinted. Secret-like request fields are forbidden from receipt metadata.

### Batch provenance

`research_v1_krx_acquisition_batch.py` must verify receipt fingerprints and a single consistent contract for each logical dataset batch. Tampering, duplicate receipts, schema drift or silent mixing of route/dataset/use-scope/approval/client/public-contract evidence fails closed.

### Source-data admission

`research_v1_krx_source_data_admission.py` composes source governance and real-data evidence. For investor flow, structural admission requires at least:
- A-F source contract closed for the declared scope;
- valid untampered acquisition batch;
- current public-contract evidence;
- PIT lineage structurally valid;
- exact historical coverage structurally complete;
- matching source family and intended-use scope.

Even then, `source_data_structurally_admissible=true` means only `eligible_for_experiment_registry_review=true`. It must **not** directly set `feature_performance_testing_authorized=true`. A separate research-ledger/preregistration decision is required before any performance experiment, and all later statistical/execution/holdout/promotion gates remain independent.

## 9. Fail-closed source policy

If any Gate A-F requirement for the declared source family/use scope is not `PASS`, or if authorization, runtime consent, provenance, coverage, mapping, PIT publication/availability or licensing scope is unknown:
- `judge_security_status_ready = false` where security/status evidence is affected;
- investor-flow feature testing remains blocked where investor-flow evidence is affected;
- no sealed holdout is consumed to compensate for missing source quality;
- no live trading is authorized from unverified source availability.

Receipts, batches, validators or green diagnostic workflows must never be used as substitutes for the missing external evidence.

## 10. Current action state

The current source strategy is:
1. keep Data Marketplace probes explicitly labeled as that route;
2. require route-specific credentials, non-secret approval evidence **and exact per-run consent** before a tiny authenticated request;
3. keep push-triggered probe runs dry-run only and never inject KRX secrets on push;
4. keep OpenAPI `AUTH_KEY` as a separate route requiring exact service mapping and approval;
5. investigate purchased/distributed KRX products if public OpenAPI does not supply the exact required historical contract;
6. create immutable acquisition receipts and consistent batch manifests for any future real history;
7. require PIT/coverage/source-data admission before research-registry review;
8. do not run investor-flow performance research merely because a probe, receipt, batch or admission validator exists;
9. keep `INDEXALERT_KRX_SOURCE_GATE_AUDIT.md` current whenever material source evidence changes;
10. never store KRX IDs/passwords/authentication keys in source, artifacts or logs; use repository/deployment secret management.
