# IndexAlert KRX Data Marketplace Route Map

Updated: 2026-10-02 KST  
Branch: `index-alert-research-v1`  
Status: **PINNED THIRD-PARTY TRANSPORT MAP ONLY — NOT KRX AUTHORIZATION**

## Purpose

This record freezes the exact Data Marketplace route candidates used by IndexAlert before any authenticated historical acquisition. It is derived from the project's pinned `beaten-by-the-market/krx-data-api` commit `e6ebac9b71482db127348d8a08ebc6743aa3b50e` plus official KRX screen identities already frozen in the source contract.

It is **not** official KRX authorization evidence. A third-party client can document how an official screen was reached, but cannot by itself prove that KRX approved the route, that the schema is complete for Final Judge, or that the intended use is permitted.

## Authentication transport frozen by the pinned client

The pinned client implements a KRX Data Marketplace login session through:

- login page: `https://data.krx.co.kr/contents/MDC/COMS/client/view/login.jsp?site=mdc`
- login API: `https://data.krx.co.kr/contents/MDC/COMS/client/MDCCOMS001D1.cmd`
- credentials: `KRX_ID` and `KRX_PW` environment variables
- session reuse: 25 minutes in the pinned implementation

The pinned README states that its live validation observed KRX rejecting unauthenticated requests with `LOGOUT` from 2026-09. Treat that as pinned-client operational evidence only, not as an official KRX policy statement.

## Candidate mappings

| Need | BLD | Method | Screen | Current state |
|---|---|---|---|---|
| trading halt history | `dbms/MDC/STAT/issue/MDCSTAT21301` | JSON | MDCSTAT213 | pinned-client catalogued; project authentication not yet demonstrated |
| cleanup trading | `dbms/MDC/STAT/issue/MDCSTAT23701` | JSON direct transport | MDCSTAT237 | **provisional**; not catalogued in pinned client |
| delisted status | `dbms/MDC/STAT/issue/MDCSTAT23801` | CSV | MDCSTAT238 | pinned-client catalogued; project authentication not yet demonstrated |
| delisted price history | `dbms/MDC/STAT/issue/MDCSTAT23902` | CSV | MDCSTAT239 | pinned-client catalogued; project authentication not yet demonstrated |
| per-security investor flow daily trend | `dbms/MDC/STAT/standard/MDCSTAT02303` | CSV | 12009 | pinned-client catalogued; project authentication not yet demonstrated |

For `MDCSTAT21301`, the pinned client freezes a 730-day request limit and requires an exact security. Long history therefore requires deterministic chunking and exact coverage reconciliation.

For investor flow, the existing KRX public-contract evidence still requires day-D final results to enter only a later eligible decision after the official publication floor.

## A-F impact

This route map strengthens only **candidate transport reproducibility** inside Gate B/E. It does not change project states:

- Security/status: A BLOCKED, B PARTIAL, C BLOCKED, D BLOCKED, E PARTIAL, F PARTIAL.
- Investor flow: A BLOCKED, B PARTIAL, C BLOCKED, D PARTIAL, E PARTIAL, F PARTIAL.

No source contract is closed. No performance experiment, sealed holdout, promotion or live trading is authorized.

## Next admissible step

The next admissible external step is one explicitly consented, metadata-only authenticated Data Marketplace probe under the frozen project preflight. The probe must not persist numeric research history and must produce only reachability/schema/row-count metadata until route authorization evidence is independently admitted.

If the Data Marketplace route cannot be authorized or cannot provide the required complete history, the separately documented KRX purchase/distribution products remain a fallback path and require their own product-specific rights/ingestion contract.
