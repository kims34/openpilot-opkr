# IndexAlert KRX Historical Acquisition Plan v1

Updated: 2026-10-02 KST  
Plan ID: `INDEXALERT-KRX-HIST-ACQ-v1`  
Status: **RIGHTS CONFIRMED / OFFLINE PLAN FROZEN / BULK NETWORK EXECUTION NOT YET USER-AUTHORIZED**

## Required research coverage

The primary required source-coverage window is:

- start: `2015-06-15`
- end: `2026-10-01`
- market: `KOSPI`

The start is inherited from the already-frozen long-history research protocol. KRX permission to download all history does **not** silently change the model evaluation window or authorize retuning on earlier data.

## Rights boundary

KRX email permission v3 explicitly covers personal research, complete full-history download/query, automated querying, low/high-frequency collection, and no separate prior approval.

Explicitly prohibited:
- external leakage;
- sale;
- third-party distribution.

Raw KRX rows therefore remain private research data and must never be committed to GitHub or exposed in public Actions artifacts/logs.

## Phase 1 — historical identity seed

Use:
- `MDCSTAT01901` current listed identity: 1 request
- `MDCSTAT20001` new-listing history CSV: 1 full-window request
- `MDCSTAT23801` delisted history CSV: 1 full-window request

Historical identity is reconstructed as a listing episode, not a name match.

Frozen episode key:
`market|short_code|listing_date`

Fail closed on:
- name-only joins;
- overlapping episodes for the same short code;
- missing listing date for a historical episode;
- unresolved market/security-class mapping.

## Phase 2 — status history

### Cleanup trading
`MDCSTAT23701`, bounded calendar-year windows.

### Trading halt
`MDCSTAT21301`, per security episode. The pinned client proves a 730-day maximum, so the required period is frozen into six inclusive chunks:

1. 2015-06-15 .. 2017-06-13
2. 2017-06-14 .. 2019-06-13
3. 2019-06-14 .. 2021-06-12
4. 2021-06-13 .. 2023-06-12
5. 2023-06-13 .. 2025-06-11
6. 2025-06-12 .. 2026-10-01

Only chunks intersecting the listing episode may be requested.

### Delisted price/economics
`MDCSTAT23902` only for affected delisted episodes after delisting/cleanup events are known.

## Phase 3 — investor-flow history

`MDCSTAT02303`, per historical KOSPI security episode.

Because no authoritative route maximum is frozen, the project does not invent one. Instead it uses **calendar-year bounded windows** as a conservative project-level chunking rule.

Day-D final investor flow remains unavailable to a decision until after the frozen **20:00 Asia/Seoul** publication floor.

## Request-count formula

Before delisted-price economics:
- 3 fixed identity requests
- 12 cleanup-trading year windows
- at most 6 trading-halt chunks per full-period security episode
- at most 12 investor-flow year chunks per full-period security episode

Maximum-form formula:
`15 + 18 × N`

where `N` is the actual historical KOSPI listing-episode count produced by Phase 1. The project must never guess N.

## Provenance

Every request requires:
- request parameters SHA-256;
- response payload SHA-256;
- response schema SHA-256;
- retrieval timestamp;
- transport status;
- row count;
- immutable request receipt;
- batch ID.

Normalized admitted rows require:
- `event_time`
- `published_at`
- `available_at`
- `ingested_at`
- historical security episode ID
- source batch ID
- source object SHA-256

## Operational safety

- default concurrency: 4
- maximum without a new plan version: 8
- exponential backoff for 429/5xx
- no retry on auth/schema failure
- checkpoint after every request
- resume only from immutable receipts
- retries never overwrite/delete prior raw objects

## Execution gate

KRX rights are confirmed, but the bulk network job itself is not automatically authorized by rights evidence.

Bulk acquisition requires:
1. this exact plan;
2. valid v3 KRX rights evidence;
3. configured KRX credentials;
4. an exact explicit user execution-consent sentinel.

Until then:
- Gate C remains open;
- Gate D remains open;
- feature-performance testing remains blocked;
- sealed holdout remains blocked;
- live trading remains blocked.
