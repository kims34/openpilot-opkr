# Current application — official OpenAPI automation remains available

The owner's original October2 reply was re-read on2026-10-08 from the actual .eml, with quoted-printable MIME decoding and no tracking-image request. Its decisive wording is: “자동화된 데이터 이용이 필요한 경우 KRX OPEN API에서 제공하는 항목은 OPEN API를 이용해 주시기 바랍니다.” It also permits internal-research storage/analysis and restricts original-data third-party provision/redistribution. This positively directs automated use to the official OpenAPI for its offered items; it is not an all-API automation prohibition.

Current official terms and use instructions were independently checked:
- https://openapi.krx.co.kr/contents/OPP/INFO/OPPINFO002.jsp — key/terms/service scope, non-commercial use, restricted third-party provision, up to10,000 requests per key per day, and possible narrower provider limits.
- https://openapi.krx.co.kr/contents/OPP/INFO/OPPINFO003.jsp — key issuance and API service utilization approval are separate steps. Existing project service approval/connectivity remains evidence; no duplicate owner approval/application is requested.
- https://openapi.krx.co.kr/contents/OPP/INFO/service/OPPINFO004.cmd — daily trades/security basics offered from2010; no separately named halt-history API appears in the inspected public list. Catalog absence is scoped, not proof no other official product exists.

| Exact route | Operational application |
|---|---|
| Approved AUTH_KEY OpenAPI /stk_bydd_trd and /stk_isu_base_info | Continue already-authorized automated private research capture under existing read-only runtime authority, service scope and provider limits. The withdrawn web-permission record must not veto these requests. |
| data.krx.co.kr screen backend /comm/bldAttendant/getJsonData.cmd + MDCSTAT21301 | A JSON/HTTP request is technically an API call but remains the website's screen-data route, not the separately published/approved OPEN API. Technical reachability does not resolve its current permission conflict. Do not globally label all APIs blocked. |
| Historical halt/cleanup/delisting/investor-flow coverage | Resolve the exact official product, service fields, history and availability. Do not substitute daily prices/master for event history or classify zero volume as an official halt. |

Code application: the historical permission validator now reports access_route=DATA_MARKETPLACE_WEB_SESSION and separately_approved_openapi_restricted_by_this_evidence=false, retaining legacy generic false fields for the withdrawn web claim and old hashes. These fields neither self-authorize API requests nor grant any source/model/Alpha/trading admission. The prospective runtime already uses the two official OpenAPI endpoints with AUTH_KEY and explicit read-only authority independently of the historical mixed web-acquisition preflight. No misplaced OpenAPI veto was found in that inspected path; its observed FAIL_CLOSED is invalid OHLC data, not an API permission rejection.

A network-free regression verifies superseded web rights remain blocked while exact OpenAPI evidence validates and an explicitly authorized injected API request succeeds; absent per-request authority still blocks before transport. No real KRX request, credentials, purchase, source/holdout/model admission or broker action is made by this correction. All Frozen/100,000-KRW live gates and disabled trading remain unchanged.

---

# Current disposition — 2026-10-07

The unrestricted web-automation claims in the historical v3 record below are superseded by the owner-supplied original email and confirmation that no matching unrestricted reply exists. Current validator returns automation/high-frequency/full-history web acquisition rights false. Internal research storage/analysis and separately approved OpenAPI services are distinct. See INDEXALERT_KRX_ORIGINAL_MESSAGE_CONFLICT_2026-10-07.md. Historical hashes/content below are preserved, not rewritten.

---

# IndexAlert KRX Permission Reply Evidence

Updated: 2026-10-02 KST  
Branch: `index-alert-research-v1`  
Evidence ID: `INDEXALERT-KRX-PERMISSION-REPLY-2026-10-02-v3`  
Status: **EXPLICIT PERSONAL-RESEARCH FULL-HISTORY / AUTOMATED / HIGH-FREQUENCY USE RIGHTS — NO REDISTRIBUTION**

## Evidence integrity

The user supplied the KRX reply text plus email-header metadata in the conversation. The recipient identity/email is deliberately not stored in GitHub.

- original screenshot SHA-256: `1983036114310ea42dd60ad49fc52c19a7378f7f1d3f1c1a65dabc7b4d1cf1e1`
- normalized redacted latest email-record SHA-256: `7361065e06599f947216233fc84e97126b1675de5af41068114cf6ef9577e304`
- subject: `[KRX Data Marketplace] 데이터 이용 문의에 대한 답변의 건`
- thread sender: `krxdata@krx.co.kr`
- prior reply time previously supplied: `2026-10-02T14:40:00+09:00`
- latest v3 reply exact timestamp: **not re-provided / intentionally unknown**
- recipient: **redacted**
- metadata source: user-provided email-thread context plus latest reply text
- sender domain matches the official `krx.co.kr` domain
- sender origin remains user-attested, not independently fetched by the repository

## Latest reply text supplied by the user

> 안녕하십니까.
>
> KRX Data Marketplace 데이터 이용에 대해 문의해 주셔서 감사합니다.
>
> 문의하신 데이터 이용 조건 및 권한에 대해 안내해 드립니다.
>
> 개인 연구 목적의 경우, 제3자 배포나 외부 판매 목적이 아니라면 다음과 같은 조건으로 제한 없이 이용 가능합니다.
>
> 전체 과거 기간 데이터 다운로드 가능: 전체 과거 이력 기간에 대한 완전한 데이터 다운로드 및 조회가 가능합니다.
>
> 조회 방식 및 빈도 제한 없음: 프로그램을 통한 자동 조회는 물론, 저빈도 및 고빈도 데이터 수집 등 모든 형태의 조회가 허용됩니다.
>
> 승인 절차 없음: 상기 이용 방식에 대해 별도의 사전 승인이나 절차가 필요하지 않습니다.
>
> 단, 수집하신 데이터의 외부 유출, 판매 및 제3자 배포는 엄격히 금지되오니 이 점 유의하여 이용해 주시기 바랍니다.
>
> 추가 문의 사항이 있으시면 언제든지 연락해 주시기 바랍니다.
>
> 감사합니다.

## Supported rights for the declared personal-research scope

The supplied KRX reply explicitly supports:

- personal research;
- non-commercial use;
- complete full-historical-period download and query;
- programmatic querying;
- automated querying;
- low-frequency collection;
- high-frequency collection;
- no separate prior approval procedure.

The project records the permission state as `PERMITTED_NO_SEPARATE_APPROVAL`.

For the declared **personal/internal research** scope, Gate F intended-use rights may now be treated as **PASS**. This PASS is scope-specific and must never be generalized to redistribution, sale, third-party delivery or a commercial service.

## Explicit prohibitions

The supplied KRX reply explicitly prohibits:

- external leakage;
- external sale;
- third-party distribution.

Any artifact or workflow that would expose raw acquired KRX data outside the private project/research boundary must fail closed.

## Rights are not evidence of technical completeness

The email establishes use rights. It does **not** establish by itself:

- exact BLD/schema equivalence across every date;
- that every required historical date is technically available;
- stable security identity mapping across all history;
- record-level PIT lineage;
- exact halt/cleanup/delisting execution economics;
- model performance validity.

Those are separate Gates B/C/D/E and later research/admission questions.

## Project effect

- `automated_collection_authorized=true`
- `high_frequency_collection_authorized=true`
- `full_historical_download_rights_authorized=true`
- `bulk_historical_acquisition_rights_authorized=true`
- Gate F for declared personal/internal research: **PASS**
- bulk historical **network execution** remains separately gated by a frozen acquisition plan plus explicit user execution consent
- feature-performance testing remains unauthorized until source admission closes
- sealed holdout remains unauthorized
- live trading remains unauthorized

The distinction between **rights to acquire** and **authorization to start a bulk network job now** is intentional.
