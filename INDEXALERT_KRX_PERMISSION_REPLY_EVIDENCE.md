# IndexAlert KRX Permission Reply Evidence

Updated: 2026-10-02 KST  
Branch: `index-alert-research-v1`  
Evidence ID: `INDEXALERT-KRX-PERMISSION-REPLY-2026-10-02-v2`  
Status: **EXPLICIT LOW-FREQUENCY PROGRAMMATIC/AUTOMATED USE PERMISSION — TINY-PROBE SCOPE ONLY**

## Evidence integrity

The user supplied the KRX reply text plus email-header metadata in the conversation. The recipient identity/email is deliberately not stored in GitHub.

- original screenshot SHA-256: `1983036114310ea42dd60ad49fc52c19a7378f7f1d3f1c1a65dabc7b4d1cf1e1`
- redacted normalized email-record SHA-256: `c50a76bb22d8e16b48b9b2eb56c78ab97f620068ed4fae4a65cd4bf6f4ae5f38`
- subject: `[KRX Data Marketplace] 데이터 이용 문의에 대한 답변의 건`
- sender: `krxdata@krx.co.kr`
- reply time: `2026-10-02T14:40:00+09:00`
- recipient: **redacted**
- sender metadata source: user-provided email-header text
- sender domain matches the official `krx.co.kr` domain
- sender origin is user-attested, not independently fetched by the repository

## Reply text supplied by the user

> 안녕하십니까.
>
> KRX Data Marketplace 데이터 이용에 대해 문의해 주셔서 감사합니다.
>
> 문의하신 개인 내부 연구 목적의 데이터 이용과 관련하여 안내해 드립니다.
>
> 개인이 내부 연구 목적(비상업적 용도)으로 사용하는 경우, 프로그램을 통한 조회 및 자동 조회를 포함하여 저빈도 사용에 대해 별도의 승인 절차 없이 모두 제한 없이 이용 가능합니다.
>
> 추가 문의 사항이 있으시면 언제든지 연락해주시기 바랍니다.
>
> 감사합니다.

## Supported permission scope

The supplied reply explicitly covers:

- personal-user use;
- non-commercial/internal research;
- low-frequency querying;
- **programmatic querying**;
- **automated querying**;
- no separate approval procedure required for that stated scope.

The project records the permission state as `PERMITTED_NO_SEPARATE_APPROVAL` rather than inventing a formal approval event that KRX expressly said was unnecessary.

## Deliberate limits

This evidence does **not** authorize or prove:

- bulk/high-frequency collection;
- unrestricted full-history downloading;
- redistribution;
- commercial use;
- exact BLD/schema equivalence;
- complete historical coverage;
- PIT lineage;
- performance validity;
- sealed-holdout use;
- live trading.

The email permission is sufficient only to satisfy the **permission/automation prerequisite for a metadata-only, low-frequency tiny authenticated Data Marketplace probe**. A successful probe may raise Gate A at most to `PARTIAL`; it can never make Gate A `PASS` by itself.

## Project effect

- `automated_collection_authorized=true` for the stated personal/non-commercial/internal-research, low-frequency scope;
- permission state = `PERMITTED_NO_SEPARATE_APPROVAL`;
- structured authorization evidence may now be created for the two declared Data Marketplace research families;
- `sufficient_for_data_marketplace_tiny_probe_preflight=true` at the permission-evidence layer;
- before an actual authenticated probe, Gate A remains `BLOCKED`;
- bulk history, feature-performance testing, sealed holdout and live trading remain unauthorized.

The actual probe still requires the exact one-run consent gate and the other canonical preflight checks.
