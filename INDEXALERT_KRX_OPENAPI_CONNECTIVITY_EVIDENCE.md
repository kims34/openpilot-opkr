# IndexAlert KRX OpenAPI Connectivity Evidence

Updated: 2026-10-02 KST  
Branch: `index-alert-research-v1`  
Evidence ID: `INDEXALERT-KRX-OPENAPI-CONNECTIVITY-2026-10-02-v2`  
Status: **AUTHENTICATED CONNECTIVITY / SCHEMA EVIDENCE ONLY — NO SOURCE-CLOSURE, ALPHA, HOLDOUT OR LIVE AUTHORITY**

## 1. Scope

This record freezes the first production-observed authenticated KRX OpenAPI responses for the two services that were separately enabled by the user:

- `유가증권 종목기본정보`
- `유가증권 일별매매정보`

The KRX authentication key remains only in Railway secret management. Its value is not stored in GitHub, this document, the machine-readable evidence file, the smoke log, or the public health response.

The user-side KRX My Page showed both services as `승인` on 2026-10-02. The screenshots are deliberately not committed because they contain account-identifying UI. This repository therefore treats that approval-screen observation as user-attested context; the immutable repository evidence is the successful authenticated production response and its exact schema audit.

## 2. Reproducible production evidence

Exact production server revision:
`4714f8e2d47881b7ccc42d7add0bfebb67ce3bf5`

Railway deployment:
`2ae60f51-720c-463f-96cb-c9ef98fc449b` — SUCCESS

GitHub production smoke:
- run `36956234911` — SUCCESS
- job `110679680755`
- audited `runtime_revision=4714f8e2d47881b7ccc42d7add0bfebb67ce3bf5`
- KRX request basis date `20261001`

The smoke consumes only the sanitized cached `/krx-health` result. The KRX startup probe itself reads `KRX_AUTH_KEY` from the production environment and never emits the secret. Evidence v2 additionally freezes per-service retrieval timestamps plus SHA-256 fingerprints of the observed schema and complete parsed JSON response, without storing or exposing the response rows in the repository.

## 3. Exact observed OpenAPI results

### 3.1 유가증권 종목기본정보

- Endpoint: `https://data-dbg.krx.co.kr/svc/apis/sto/stk_isu_base_info`
- Method: `GET`
- HTTP: `200`
- JSON parsed: `true`
- `OutBlock_1` rows: `942`
- Schema match: `true`
- Observed at: `2026-10-02T02:37:36.973562+00:00`
- Response schema SHA-256: `11b766977e67ed2f4665a4752a80d18ab76c086d89cf0f853e2642e5575a54e5`
- Response payload SHA-256: `cc64d8b8e9c028ee48a59928195998dfafbfd797587c9f3c1406002a4212792d`
- Observed fields:
  `ISU_ABBRV, ISU_CD, ISU_ENG_NM, ISU_NM, ISU_SRT_CD, KIND_STKCERT_TP_NM, LIST_DD, LIST_SHRS, MKT_TP_NM, PARVAL, SECT_TP_NM, SECUGRP_NM`

### 3.2 유가증권 일별매매정보

- Endpoint: `https://data-dbg.krx.co.kr/svc/apis/sto/stk_bydd_trd`
- Method: `GET`
- HTTP: `200`
- JSON parsed: `true`
- `OutBlock_1` rows: `942`
- Schema match: `true`
- Observed at: `2026-10-02T02:37:39.653451+00:00`
- Response schema SHA-256: `5d68cce946a3c9361e7d662351f4896518cad40a3804fd262f577ad29d1d56f3`
- Response payload SHA-256: `b5ff8d6894a1956aaf963aa9bad853eff1c3ee465f50f3ab611f7098ca0f93d3`
- Observed fields:
  `ACC_TRDVAL, ACC_TRDVOL, BAS_DD, CMPPREVDD_PRC, FLUC_RT, ISU_CD, ISU_NM, LIST_SHRS, MKTCAP, MKT_NM, SECT_TP_NM, TDD_CLSPRC, TDD_HGPRC, TDD_LWPRC, TDD_OPNPRC`

The exact machine-readable record is `INDEXALERT_KRX_OPENAPI_CONNECTIVITY_EVIDENCE.json`.

## 4. What this evidence establishes

This evidence establishes, for the exact observed services and date only:

1. the production runtime possessed a configured KRX OpenAPI credential without exposing it;
2. authenticated KRX OpenAPI transport succeeded;
3. both exact service endpoints responded with HTTP 200 and parseable JSON;
4. both responses contained non-empty `OutBlock_1` data;
5. the observed fields matched the uploaded KRX development specifications;
6. the exact observed response schema and payload are bound by SHA-256 fingerprints for later integrity comparison;
7. stable security identifiers `ISU_CD` and `ISU_SRT_CD` are present in the basic-information response, while `ISU_CD` is present in the daily-trade response.

This is stronger than credential-presence or dry-run evidence, but it is still only connectivity/schema evidence.

## 5. What this evidence does NOT establish

It does **not** establish:

- complete historical coverage;
- complete common-stock/security identity coverage across the Final-Judge period;
- record-level `event_time / published_at / available_at / ingested_at` PIT lineage;
- trading-halt history;
- cleanup-trading history;
- actual delisting history;
- exact delisting, halt or forced-liquidation economics;
- investor-by-security flow access;
- immutable acquisition receipts and batch provenance for a complete research history;
- exact use rights beyond the separately audited OpenAPI terms and actual service approval scope;
- feature-performance authority;
- sealed-holdout authority;
- Alpha/Final-Judge promotion authority;
- live-order authority.

The two observed OpenAPI services must never be substituted for the still-unresolved official status-event or investor-flow products merely because they share KRX provenance.

## 6. A-F impact

For declared family `KRX_SECURITY_STATUS`:

- Gate A `AUTHORIZED_OFFICIAL_ROUTE`: remains **BLOCKED** for the declared status family. Authenticated OpenAPI access is now demonstrated for basic security master and daily trading, but the exact approved route/product for halt/cleanup/delisting history remains unresolved.
- Gate B `EXACT_DATASET_SCHEMA_MAPPING`: remains **PARTIAL**, strengthened by exact live schema verification for these two services only.
- Gate C `HISTORICAL_COVERAGE_SECURITY_MAPPING`: remains **BLOCKED**.
- Gate D `PIT_AVAILABILITY_LINEAGE`: remains **BLOCKED**.
- Gate E `REPRODUCIBLE_INTEGRITY_FAIL_CLOSED`: remains **PARTIAL**, strengthened by exact-revision production smoke evidence but not by a complete historical receipt/batch chain.
- Gate F `INTENDED_USE_RIGHTS`: remains **PARTIAL**.

For `KRX_INVESTOR_FLOW`, no A-F state changes. Neither observed service is investor-by-security flow.

Therefore:
- `judge_security_status_ready=false`;
- `investor_flow_feature_testing_authorized=false`;
- `sealed_holdout_authorized=false`;
- `live_trading_authorized=false`.

## 7. Next external source targets

The next source work remains:

1. exact official authorized history for trading halt / cleanup trading / delisting / delisted-security economics;
2. exact official investor-by-security flow route;
3. complete historical coverage plus stable security mapping;
4. record-level PIT availability lineage;
5. immutable acquisition receipts/batches for any history admitted to research;
6. exact intended-use rights for each selected route/product.

No sealed holdout or real-order stage may be used to compensate for any missing source evidence.
