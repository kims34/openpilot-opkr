# IndexAlert KRX Expected-Scope Attestation Contract v1

Updated: 2026-10-02 KST  
Contract: `INDEXALERT-KRX-EXPECTED-SCOPE-ATTESTATION-v1`  
Bound historical plan: `INDEXALERT-KRX-HIST-ACQ-v3`  
Status: **FROZEN DESIGN ONLY — NO EXPECTED-SCOPE NETWORK SWEEP AUTHORIZED**

## Why this contract exists

Gate C cannot be closed by comparing a Data Marketplace dataset against an
"expected scope" derived from that same dataset. That would make missing rows
undetectable.

The independent attestor uses the two separately approved KRX OpenAPI services:

- `유가증권 일별매매정보` — exact date-by-date official daily-trade scope;
- `유가증권 종목기본정보` — same-date official identity/common-stock mapping.

The frozen research interval is `2015-06-15..2026-10-01`, exactly **4,127
calendar dates**.

## No invented trading calendar

The attestor must not generate trading sessions from weekdays, holiday tables or
a third-party calendar.

For every one of the 4,127 calendar dates it may later query
`stk_bydd_trd?basDd=YYYYMMDD`.

A date becomes an observed KRX trading-date scope only when:
1. the authenticated daily-trade response is non-empty; and
2. every returned `BAS_DD` equals the requested date.

An empty response is preserved as an exact request result. It is not turned into
a trading session and no missing rows are synthesized.

## Same-date identity attestation

Only for a non-empty daily-trade date, the worker may later query
`stk_isu_base_info` for that exact same `basDd`.

Common-stock identity requires explicit same-date official fields. Exact
`ISU_CD` is the stable join key. Name-only joins and later-snapshot fallback are
forbidden.

## Expected investor-flow scope

Key:
`(event_date, symbol, isu_cd)`

Expected keys come only from the same-date intersection of:
- official daily-trade rows; and
- same-date officially attested KOSPI common-stock identity rows.

The attestor never fills a missing security/date and never manufactures a
zero-flow observation.

## Expected security/status identity scope

Key:
`(snapshot_date, symbol, isu_cd)`

For every independently observed trading date, expected identity rows are all
same-date KOSPI common-stock identity rows from the basic-info response.

## Integrity boundary

All raw responses remain private. Every request requires an immutable receipt
and payload/schema SHA-256. Expected-scope output must carry one frozen contract
fingerprint.

The expected scope must never be derived from the Data Marketplace
`MDCSTAT21301`, `MDCSTAT23701`, `MDCSTAT23801`,
`MDCSTAT23902` or `MDCSTAT02303` rows being audited.

## Execution boundary

This contract **does not authorize** the 4,127-date network sweep.

A future execution requires a distinct exact sentinel:

`KRX_EXPECTED_SCOPE_ATTESTATION_CONSENT=I_AUTHORIZE_INDEXALERT_KRX_EXPECTED_SCOPE_ATTESTATION_v1`

Historical bulk consent and tiny-probe consent do not substitute for it.

Current authority remains:
- Gate C closed: false
- Gate D closed: false
- Gate E closed: false
- feature-performance testing: false
- sealed holdout: false
- live trading: false
