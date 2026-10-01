# IndexAlert KRX Source Access Contract

Updated: 2026-10-01 KST
Branch: `index-alert-research-v1`
Status: **SOURCE / LICENSING CONTRACT — NO ALPHA CLAIM**

## 1. Purpose

This document prevents IndexAlert from confusing distinct KRX data-access products, authentication methods and licensing terms. It is source-governance infrastructure only. Nothing in this document is performance evidence and it does not authorize holdout use or live trading.

## 2. Frozen KRX source gates A-F

The following six gates are the canonical source-governance contract for every KRX data family used by IndexAlert. They consolidate requirements that were already distributed across the Master Spec, source probes and official-status adapters. They do **not** weaken or replace any statistical, PIT, execution, NetEV, holdout or prospective-promotion rule.

### Gate A — `AUTHORIZED_OFFICIAL_ROUTE`

The exact official KRX access route/product must be identified and the dataset must be accessed under the appropriate authorization. KRX OpenAPI `AUTH_KEY`, Data Marketplace authenticated web-session credentials and purchased/distributed data products are distinct routes and must never be substituted for one another.

### Gate B — `EXACT_DATASET_SCHEMA_MAPPING`

The exact API service, screen/feed contract and required fields/schema must be verified for the intended data family. A similarly named public API, a screen whose fields/history have not been verified, or a provisional low-level transport does not close this gate.

### Gate C — `HISTORICAL_COVERAGE_SECURITY_MAPPING`

Historical coverage must span the requested research/Final-Judge period and all relevant securities, with stable security mapping and common-stock identity where required. A non-empty probe result or a current-only snapshot is not evidence of complete historical coverage.

### Gate D — `PIT_AVAILABILITY_LINEAGE`

Point-in-time lineage must be explicit: `event_time`, `published_at` when applicable, `available_at` and `ingested_at` must be preserved, and no value may be used before it was officially available. Final day-D investor flow is eligible only for the next decision after its official publication time.

### Gate E — `REPRODUCIBLE_INTEGRITY_FAIL_CLOSED`

Retrieval and source metadata must be reproducible and auditable. Source/schema ambiguity must fail closed. Undocumented proxies, synthetic substitutions or source-route impersonation are forbidden. Source reachability by itself does not close this gate.

### Gate F — `INTENDED_USE_RIGHTS`

Data-use/licensing rights must be explicitly verified for the intended use scope. Internal research/personal validation and future external/commercial product use are separate scopes and must not be conflated.

### Closure semantics

Each gate has exactly one audit status: `PASS`, `PARTIAL` or `BLOCKED`.

- Only `PASS` closes a gate.
- `PARTIAL` is explicitly **not** a pass and cannot be promoted by inference.
- Any `PARTIAL` or `BLOCKED` result keeps the source contract open for that declared source family/use scope.
- All six gates passing means only that the KRX **source contract for the declared scope** is closed. It does **not** by itself authorize Alpha/Final-Judge promotion, sealed-holdout consumption, Shadow/Paper/Live promotion or live trading.
- Existing PIT/time-consistency, anchored Walk-Forward, Purged/CPCV, realistic execution-cost/fill, distributional NetEV, tail-risk, recency, holdout and prospective confirmation gates remain independent and mandatory.

Executable semantics are frozen in `research_v1_krx_source_gates.py`; the current evidence assessment is recorded in `INDEXALERT_KRX_SOURCE_GATE_AUDIT.md`.

## 3. Distinct KRX access routes

### Route 1 — KRX OpenAPI

Official KRX OpenAPI uses a separate authentication-key workflow:
1. register/login to KRX Data Marketplace;
2. apply for an API authentication key;
3. wait for administrator approval;
4. identify the desired API service;
5. apply for use of that individual API service;
6. wait for service approval;
7. call the approved service with the authentication key in the `AUTH_KEY` request header.

An OpenAPI authentication key is therefore **not equivalent** to Data Marketplace web-session credentials.

IndexAlert must not assume that an OpenAPI key grants access to a dataset until the exact official OpenAPI service has been identified, its fields/history verified and its individual usage approval obtained.

### Route 2 — KRX Data Marketplace authenticated web session

The current feasibility probes use `KRX_ID` / `KRX_PW` only for an authenticated Data Marketplace web-session route through a pinned exploratory client.

This route is used to determine whether official KRX screen/source families can be reached reproducibly. Candidate low-level BLDs or screen transports remain provisional until live authenticated responses, historical coverage and PIT lineage are validated.

`KRX_ID` / `KRX_PW` must never be described as KRX OpenAPI `AUTH_KEY` authentication.

### Route 3 — KRX data purchase / distribution products

KRX separately describes purchased/distributed data products. Its distribution catalog includes, among other reference-data products:
- per-security/per-investor EOD information;
- market-action information for KOSPI/KOSDAQ;
- EOD items including security events and investor information.

These products are a separate access/licensing route from the public OpenAPI catalog. The existence of a data-feed product does not mean it is available through public OpenAPI or through an authenticated screen without a suitable agreement.

## 4. Required IndexAlert data families

### Security/status Final Judge data

Required official history includes at least:
- common-stock identity / security mapping;
- trading-halt history;
- cleanup-trading status;
- delisting status;
- delisted-security price/economic path sufficient to model exact outcomes.

Known official Data Marketplace screen contracts include MDCSTAT213, MDCSTAT237, MDCSTAT238 and MDCSTAT239. Their existence is not enough. Before Judge readiness, IndexAlert requires a reproducible authorized source, historical coverage, stable security mapping and PIT availability lineage.

### Investor-flow candidate family

The official KRX Data Marketplace stock investor-trading screen states that final day-D trading results are provided after 20:00. Therefore final day-D investor flow can only enter the **next eligible decision after publication**. Same-day use before publication is forbidden.

Before any investor-flow performance experiment, establish:
- reproducible authorized source;
- historical coverage;
- stable security mapping;
- `event_time`, `published_at`, `available_at`, `ingested_at`;
- fail-closed handling when publication/access is unavailable.

A source/authentication probe alone is not feature-promotion evidence.

## 5. Public OpenAPI mapping rule

As of the 2026-09-30 audit, IndexAlert has verified the general OpenAPI authentication/application process and public examples of `AUTH_KEY` usage, but has **not established an exact public OpenAPI service mapping** for all required Final Judge status datasets or the required per-security investor-flow history.

Therefore:
- do not rewrite the existing web-session probes as OpenAPI probes merely because an `AUTH_KEY` can be issued;
- do not infer that a similarly named public API contains equivalent fields/history;
- do not scrape or substitute undocumented proxies to bypass missing official access;
- if an exact official OpenAPI service is later found, add it as a separate adapter with explicit service ID, schema, approval state, coverage and PIT contract.

## 6. Licensing / product boundary

Current project-audited KRX OpenAPI terms state that OpenAPI use is limited to non-commercial purposes, that users must not charge third parties for results obtained using the API, and that information received from KRX must not be provided to third parties.

Consequences for IndexAlert:
- internal research/personal validation and future external/commercial product distribution are separate compliance questions;
- public/commercial IndexAlert must not assume the free OpenAPI terms permit redistribution or paid use;
- before external distribution, obtain a data route/license whose permitted use explicitly covers the intended product behavior;
- licensing compliance is a **product activation gate**, independent of statistical Alpha promotion.

This contract does not provide legal advice; it freezes the engineering rule that data rights must be verified rather than assumed.

## 7. Fail-closed source policy

If any Gate A-F requirement for the declared source family/use scope is not `PASS`, or if source authorization, coverage, mapping, publication time or licensing scope is otherwise unknown:
- `judge_security_status_ready = false` where security/status evidence is affected;
- investor-flow feature testing remains blocked where investor-flow evidence is affected;
- no sealed holdout is consumed to compensate for missing source quality;
- no live trading is authorized from unverified source availability.

## 8. Current action state

The current source strategy is:
1. keep the Data Marketplace session probes explicitly labeled as such;
2. keep KRX OpenAPI `AUTH_KEY` as a separate route requiring exact service mapping and approval;
3. investigate the authorized KRX data-purchase/distribution route for required status/investor reference data if public OpenAPI does not supply the exact historical contract;
4. do not run investor-flow performance research until the applicable A-F source contract is closed;
5. preserve all PIT and licensing evidence in reproducible metadata before any candidate evaluation;
6. keep `INDEXALERT_KRX_SOURCE_GATE_AUDIT.md` current whenever material source evidence changes.
