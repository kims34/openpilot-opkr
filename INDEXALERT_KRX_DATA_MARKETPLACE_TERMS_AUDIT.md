# IndexAlert KRX Data Marketplace Terms Audit

Updated: 2026-10-02 KST  
Branch: `index-alert-research-v1`  
Evidence ID: `INDEXALERT-KRX-DATA-MARKETPLACE-TERMS-2026-10-02-v1`  
Status: **TERMS REQUIRE EXPLICIT PERMISSION; SEPARATE KRX v3 FULL-HISTORY/HIGH-FREQUENCY PERSONAL-RESEARCH PERMISSION NOW EXISTS**

Official source:
`https://data.krx.co.kr/contents/MDC/INFO/informationController/MDCINFO003.cmd`

The current KRX Data Marketplace homepage terms state that the membership contract is formed through signup and agreement to the terms, and that the site provides online KRX-data lookup/search/guidance services. The same terms prohibit unauthorized collection/reproduction/distribution by automated means and separately prohibit copying/reproduction/distribution/transmission/public transmission of site information without prior KRX permission. Market-data products are governed by separate purchase/use terms.

## Project consequence

A valid KRX account, successful login, or possession of `KRX_ID/KRX_PW` is **not** evidence that automated collection is permitted.

Therefore, for `DATA_MARKETPLACE_AUTHENTICATED_WEB_SESSION`:

- `research_v1_krx_authorization_evidence.py` requires `automated_collection_authorized=true` in an otherwise valid KRX-issued authorization evidence record;
- `research_v1_krx_auth_preflight.py` independently requires the same permission signal before any tiny authenticated request can become authorized;
- ordinary membership credentials cannot satisfy this requirement;
- missing or ambiguous permission yields `EXPLICIT_KRX_AUTOMATED_COLLECTION_PERMISSION` and blocks the request.

This constraint applies to the candidate Data Marketplace mappings including `MDCSTAT21301`, `MDCSTAT23701`, `MDCSTAT23801`, `MDCSTAT23902`, and `MDCSTAT02303`.

## Route separation

This restriction does not convert the separately approved KRX OpenAPI services into Data Marketplace rights and does not prohibit use of a distinct KRX product or route that explicitly authorizes automated access. Any OpenAPI or purchased/distributed-product route must remain separately mapped, licensed, evidenced and admitted.

## Frozen authority state

This terms audit by itself never authorizes a request. Separate `INDEXALERT_KRX_PERMISSION_REPLY_EVIDENCE.md/.json` now supplies explicit complete full-history download/query plus low/high-frequency programmatic/automated collection rights for the personal non-commercial/internal-research scope, while explicitly prohibiting external leakage, sale and third-party distribution. After structured evidence and network-free readiness, the remaining prerequisite for a tiny authenticated probe is exact per-run consent.

The terms audit alone keeps:

- Data Marketplace authenticated probe: **not authorized by this terms record alone**
- bulk historical acquisition rights: **authorized only by the separate v3 permission record for the declared personal-research scope; this terms record alone does not authorize execution**
- investor-flow feature performance testing: **not authorized**
- sealed holdout: **not authorized**
- live trading: **not authorized**

No username/password, cookie, session identifier, authentication key or other secret belongs in this evidence record.
