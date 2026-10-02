# IndexAlert KRX Permission Reply Evidence

Updated: 2026-10-02 KST  
Branch: `index-alert-research-v1`  
Evidence ID: `INDEXALERT-KRX-PERMISSION-REPLY-2026-10-02-v3`  
Status: **EXPLICIT PERSONAL-RESEARCH FULL-HISTORY / AUTOMATED / HIGH-FREQUENCY USE RIGHTS — NO REDISTRIBUTION**

## Evidence integrity

The user supplied the KRX reply text plus email-header metadata in the conversation. The recipient identity/email is deliberately not stored in GitHub.

- original screenshot SHA-256: `1983036114310ea42dd60ad49fc52c19a7378f7f1d3f1c1a65dabc7b4d1cf1e1`
- normalized redacted latest email-record SHA-256: `2aa1c2a08c108d9f71e4b5027fb697e593f2f874268567faa0d62c3ac95c3c39`
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
