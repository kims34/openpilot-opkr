# IndexAlert KRX Historical Acquisition Plan v2

Updated: 2026-10-02 KST  
Plan ID: `INDEXALERT-KRX-HIST-ACQ-v2`  
Supersedes: `INDEXALERT-KRX-HIST-ACQ-v1` **before any bulk network execution**  
Status: **RIGHTS CONFIRMED / STABLE-IDENTITY PLAN FROZEN / BULK NETWORK EXECUTION NOT YET USER-AUTHORIZED**

## Why v2 supersedes v1

v1 could reconstruct listing episodes from current/new/delisted history, but it did not require a historical KRX **standard code `ISU_CD` for every episode**. That is insufficient because the per-security Data Marketplace routes require a stable security identifier.

v2 therefore fail-closes identity before any bulk status/investor request:
- securities already active at research start get `ISU_CD` from the exact `2015-06-15` KRX basic-info snapshot;
- newly listed episodes get `ISU_CD` from a basic-info snapshot whose `basDd` equals the episode's listing date;
- the `2026-10-01` basic-info snapshot is reconciliation only and can never backfill an unresolved historical episode;
- inconsistent or missing standard codes fail closed.

No v1 bulk request was executed, so v2 replaces it without contaminating evidence.

## Required research coverage

Primary required source window:
- start: `2015-06-15`
- end: `2026-10-01`
- market: `KOSPI`

This inherits the frozen long-history research protocol. Earlier KRX availability/rights must not silently expand the model evaluation window.

## Rights boundary

KRX permission v3 explicitly allows, for personal research:
- complete full-historical-period download/query;
- automated/programmatic collection;
- low-frequency collection;
- high-frequency collection;
- no separate prior approval.

It explicitly prohibits:
- external leakage;
- sale;
- third-party distribution.

Gate F is PASS only for this declared personal/internal-research scope.

## Phase 1 — stable historical identity

Fixed master snapshots:
1. OpenAPI `stk_isu_base_info?basDd=20150615`
2. OpenAPI `stk_isu_base_info?basDd=20261001`

Windowed history:
- `MDCSTAT20001` new listings: 12 calendar-year windows
- `MDCSTAT23801` delisted history: 12 calendar-year windows

Dynamic master snapshots:
- after discovering new-listing dates, request one `stk_isu_base_info` snapshot for each unique listing date;
- each newly listed episode must take `ISU_CD` from the snapshot on its own listing date;
- no later snapshot fallback.

Frozen episode key:
`market|short_code|listing_date`

Every episode must have:
- KOSPI market;
- common stock identity;
- short code;
- listing date;
- standard code `ISU_CD`;
- non-overlapping lifetime.

Name-only joins are forbidden.

## Phase 2 — status history

### Cleanup trading
`MDCSTAT23701`, 12 bounded calendar-year windows.

### Trading halt
`MDCSTAT21301`, per validated episode:
- `isuCd = standard_code`
- `isuCd2 = short_code`
- maximum 730 calendar days/request

Frozen six outer chunks:
1. 2015-06-15 .. 2017-06-13
2. 2017-06-14 .. 2019-06-13
3. 2019-06-14 .. 2021-06-12
4. 2021-06-13 .. 2023-06-12
5. 2023-06-13 .. 2025-06-11
6. 2025-06-12 .. 2026-10-01

Only episode-intersecting portions may be requested.

### Delisted price/economics
`MDCSTAT23902` only after the delisted/cleanup event and stable identity are resolved.

## Phase 3 — investor-flow history

`MDCSTAT02303`, per validated historical episode:
- `isuCd = standard_code`
- calendar-year bounded windows
- no invented undocumented route maximum
- day-D final data unavailable to a decision until after **20:00 Asia/Seoul**

## Request-count structure

Fixed identity acquisition:
- 2 fixed OpenAPI master snapshots
- 12 new-listing windows
- 12 delisted-history windows
= **26 fixed identity requests**

Dynamic:
- `U_new_listing_dates` listing-date master snapshots
- 12 cleanup windows
- halt episode/chunk intersections
- investor episode/year intersections

Frozen formula before delisted-price economics:
`38 + U_new_listing_dates + halt_episode_chunk_intersections + investor_episode_year_intersections`

Conservative upper form:
`38 + U_new_listing_dates + 18 × N`

Neither `N` nor `U` may be guessed.

## Provenance and privacy

Raw KRX rows are private research data:
- never commit raw rows to this public GitHub repository;
- never expose raw rows in public Actions logs/artifacts;
- only metadata summaries may be public.

Every request needs:
- request-parameter SHA-256;
- response-payload SHA-256;
- response-schema SHA-256;
- retrieval timestamp;
- transport status;
- row count;
- immutable receipt;
- batch ID.

Admitted normalized rows additionally require:
- `event_time`
- `published_at`
- `available_at`
- `ingested_at`
- historical episode ID
- standard code
- short code
- source-batch ID
- source-object SHA-256

## Operational safety

- default concurrency: 4
- maximum without a new plan version: 8
- retry 429/5xx with exponential backoff
- no retry on auth/schema failure
- checkpoint after every request
- resume only from immutable receipts
- retries never delete/overwrite prior raw objects

## Execution gate

Rights are confirmed; **network execution is not**.

Bulk execution requires:
1. this exact v2 plan;
2. valid v3 KRX rights evidence;
3. configured KRX credentials;
4. exact user execution consent sentinel  
   `I_AUTHORIZE_INDEXALERT_KRX_HIST_ACQ_v2`.

Until then Gate C/D remain open, feature-performance testing remains blocked, sealed holdout remains blocked and live trading remains blocked.
