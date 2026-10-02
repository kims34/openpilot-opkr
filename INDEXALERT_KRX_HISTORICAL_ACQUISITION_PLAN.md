# IndexAlert KRX Historical Acquisition Plan v3

Updated: 2026-10-02 KST  
Plan ID: `INDEXALERT-KRX-HIST-ACQ-v3`  
Supersedes: `INDEXALERT-KRX-HIST-ACQ-v2` **before any bulk network execution**  
Status: **RIGHTS CONFIRMED / STABLE-IDENTITY + CLEANUP-CORRECT PLAN FROZEN / BULK NETWORK EXECUTION NOT YET USER-AUTHORIZED**

## Why v3 supersedes v2

v2 correctly made every historical listing episode standard-code exact, but it still treated `MDCSTAT23701` as though historical `strtDd/endDd` windows had been verified. The authenticated tiny probe did **not** demonstrate that behavior: the successful request used `mktId=ALL` as a current/reconciliation snapshot.

v3 keeps all v2 stable-identity protections and corrects cleanup history before any bulk execution:
- securities already active at research start get `ISU_CD` from the exact `2015-06-15` KRX basic-info snapshot;
- newly listed episodes get `ISU_CD` from a basic-info snapshot whose `basDd` equals that episode's listing date;
- the `2026-10-01` basic-info snapshot is reconciliation only and cannot backfill an unresolved historical episode;
- `MDCSTAT23801` delisted-history rows supply historical cleanup-period start/end fields for delisted episodes;
- `MDCSTAT23701` is used only once as a current/ongoing cleanup reconciliation snapshot with `mktId=ALL`;
- historical `MDCSTAT23701` date-window semantics must never be invented.

No v1/v2 bulk request was executed, so v3 replaces both without contaminating evidence.

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

Historical cleanup intervals for delisted episodes are taken from the already acquired `MDCSTAT23801` delisted-history rows using:
- `정리매매기간_시작일`
- `정리매매기간_종료일`
- `폐지일`
- `폐지사유`

This adds **zero** historical requests beyond the 12 delisted-history windows already in Phase 1.

`MDCSTAT23701` is called **once** with `mktId=ALL` only for current/ongoing cleanup reconciliation. It is not treated as a historical date-window source unless a future separately evidenced route contract proves that behavior.

This historical cleanup reconstruction still does **not** close Gate D: retrieval-time historical facts do not establish the original historical `published_at/available_at`.

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

Dynamic / additional:
- `U_new_listing_dates` listing-date master snapshots
- 1 current `MDCSTAT23701` cleanup reconciliation snapshot
- halt episode/chunk intersections
- investor episode/year intersections

Historical cleanup periods reuse `MDCSTAT23801` and add no extra historical requests.

Frozen formula before delisted-price economics:
`27 + U_new_listing_dates + halt_episode_chunk_intersections + investor_episode_year_intersections`

Conservative upper form:
`27 + U_new_listing_dates + 18 × N`

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
1. this exact v3 plan;
2. valid v3 KRX rights evidence;
3. configured KRX credentials;
4. exact user execution consent sentinel  
   `I_AUTHORIZE_INDEXALERT_KRX_HIST_ACQ_v3`.

Until then Gate C/D remain open, feature-performance testing remains blocked, sealed holdout remains blocked and live trading remains blocked.
