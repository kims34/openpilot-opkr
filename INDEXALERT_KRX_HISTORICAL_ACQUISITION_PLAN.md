# IndexAlert KRX Historical Acquisition Plan v2

Updated: 2026-10-02 KST  
Plan ID: `INDEXALERT-KRX-HIST-ACQ-v2`  
Supersedes: `INDEXALERT-KRX-HIST-ACQ-v1` **before any bulk network execution**  
Status: **RIGHTS CONFIRMED / STABLE-IDENTITY PLAN FROZEN / BULK NETWORK EXECUTION NOT YET USER-AUTHORIZED**

## Why v2 replaced v1

Per-security KRX requests such as `MDCSTAT21301` and `MDCSTAT02303` require the KRX standard issue code (`ISU_CD`). A current-only identity snapshot is not sufficient to prove the correct historical standard code for every listing episode, especially securities that were active at the research start and later delisted.

v2 therefore requires official OpenAPI basic-info snapshots to bind each listing episode to:
- `ISU_CD` standard code;
- `ISU_SRT_CD` short code;
- listing date;
- official market/security/stock-type identity.

No per-security history request may be generated until this mapping is complete.

## Required research coverage

- start: `2015-06-15`
- end: `2026-10-01`
- market: `KOSPI`

This remains the frozen research period. Broader KRX download rights do not change the research/evaluation window.

## Rights boundary

KRX permission v3 supports, for the declared personal-research scope:
- complete historical-period download/query;
- programmatic and automated collection;
- low- and high-frequency collection;
- no separate prior approval.

Explicitly prohibited:
- external leakage;
- sale;
- third-party distribution.

Raw rows remain private research data and must never be committed to GitHub or placed in public Actions artifacts/logs.

## Phase 1 — stable historical identity seed

### Fixed snapshots

1. KRX OpenAPI `stk_isu_base_info` at `2015-06-15`
   - establishes standard/short-code mapping for securities already active at the research start.
2. KRX OpenAPI `stk_isu_base_info` at `2026-10-01`
   - reconciliation only; it may not invent a historical episode that is missing from the historical seed.

### Year-bounded history

Use 12 deterministic calendar windows from 2015-06-15 through 2026-10-01 for:
- `MDCSTAT20001` new-listing history;
- `MDCSTAT23801` delisted-security history.

The project intentionally uses yearly windows rather than assuming an undocumented unlimited transport window.

### Listing-date standard-code snapshots

After new-listing history is acquired, request one OpenAPI basic-info snapshot for each **unique listing date** inside the research period.

For every newly listed episode:
- `ISU_CD` and `ISU_SRT_CD` must come from the basic-info snapshot whose `basDd` equals the episode listing date.
- A later snapshot cannot be used as a silent fallback.

Frozen episode key:
`market|short_code|listing_date`

Fail closed on:
- name-only joins;
- unresolved standard code;
- missing listing date;
- overlapping episodes for the same short code;
- inconsistent standard code across snapshots;
- unresolved official common-stock identity.

Per-security route parameters:
- `isuCd = standard_code`
- for trading halt, `isuCd2 = short_code`.

## Phase 2 — status history

### Cleanup trading
`MDCSTAT23701`, 12 calendar-year bounded windows, then filter KOSPI.

### Trading halt
`MDCSTAT21301`, per validated listing episode.

The confirmed 730-day limit is frozen into six inclusive chunks:
1. 2015-06-15 .. 2017-06-13
2. 2017-06-14 .. 2019-06-13
3. 2019-06-14 .. 2021-06-12
4. 2021-06-13 .. 2023-06-12
5. 2023-06-13 .. 2025-06-11
6. 2025-06-12 .. 2026-10-01

Only chunks intersecting the listing episode may be requested.

### Delisted-price economics
`MDCSTAT23902` only for resolved delisted KOSPI episodes after delisting/cleanup events are known.

## Phase 3 — investor-flow history

`MDCSTAT02303`, per validated KOSPI listing episode.

Use deterministic calendar-year windows intersected with the episode lifetime. No undocumented route maximum is invented.

Day-D final investor flow remains decision-eligible only after the frozen **20:00 Asia/Seoul** publication floor.

## Request-count formula

Before delisted-price economics:
- 2 fixed OpenAPI boundary snapshots;
- 12 new-listing windows;
- 12 delisting windows;
- `U_new_listing_dates` listing-date OpenAPI snapshots;
- 12 cleanup-trading windows;
- trading-halt episode/chunk intersections;
- investor-flow episode/year intersections.

Exact formula:
`38 + U_new_listing_dates + halt_episode_chunk_intersections + investor_episode_year_intersections`

Conservative upper form if every episode spans the full period:
`38 + U_new_listing_dates + 18 × N`

Neither `N` nor `U_new_listing_dates` may be guessed.

## Provenance

Every request requires:
- request-parameter SHA-256;
- response-payload SHA-256;
- response-schema SHA-256;
- retrieval timestamp;
- transport status;
- row count;
- immutable request receipt;
- batch ID.

Normalized admitted rows require:
- `event_time`;
- `published_at`;
- `available_at`;
- `ingested_at`;
- historical security episode ID;
- standard code;
- short code;
- source batch ID;
- source object SHA-256.

## Operational safety

- default concurrency: 4
- maximum without a new plan version: 8
- exponential backoff for 429/5xx
- no retry on auth/schema failure
- checkpoint after every request
- resume only from immutable receipts
- retries never overwrite/delete prior raw objects

## Execution gate

Rights are established, but the bulk network job itself is not automatically authorized.

Bulk acquisition requires:
1. this exact v2 plan;
2. valid KRX permission v3 rights;
3. configured KRX credentials;
4. the exact v2 historical-acquisition execution consent sentinel.

Until then:
- Gate C remains open;
- Gate D remains open;
- feature-performance testing remains blocked;
- sealed holdout remains blocked;
- live trading remains blocked.
