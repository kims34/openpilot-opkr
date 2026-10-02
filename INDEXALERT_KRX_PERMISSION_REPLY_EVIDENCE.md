# IndexAlert KRX Permission Reply Evidence

Updated: 2026-10-02 KST  
Branch: `index-alert-research-v1`  
Evidence ID: `INDEXALERT-KRX-PERMISSION-REPLY-2026-10-02-v1`  
Status: **STRONG SCOPE EVIDENCE — AUTOMATION / SENDER VERIFICATION STILL AMBIGUOUS**

## Evidence integrity

The user supplied a screenshot in the conversation. The image itself is not committed to the repository.

- SHA-256: `1983036114310ea42dd60ad49fc52c19a7378f7f1d3f1c1a65dabc7b4d1cf1e1`
- screenshot sender identity visible: **no**
- reply date visible: **no**
- original question visible in the same screenshot: **no**

## Visible reply text

> KRX Data Marketplace 데이터 이용에 대해 문의해 주셔서 감사합니다.
>
> 문의하신 개인 내부 연구 목적의 데이터 조회 및 이용 건과 관련하여 안내해 드립니다.
>
> 개인 사용자에 한해 비상업적·내부 연구 목적으로 저빈도 조회를 수행하는 경우에는 별도의 승인 절차 없이 제한 없이 이용 가능합니다.
>
> 추가로 궁금하신 사항이 있으시면 언제든지 문의해 주시기 바랍니다.
>
> 감사합니다.

## What the visible text supports

The visible text directly supports all of the following within its stated scope:

- the requester is treated as a **personal user**;
- **non-commercial / internal research** use is permitted;
- **low-frequency querying** is permitted;
- the visible reply says **no separate approval procedure is required** for that scope;
- it says use is available without a stated limit within that visible low-frequency, personal, non-commercial/internal-research scope.

This materially strengthens Gate-F/use-scope evidence.

## What the visible text does not prove by itself

The screenshot does not visibly contain the sender identity, the original question, or the words "automatic", "programmatic", "API", or an equivalent explicit statement that the low-frequency allowance includes automated authenticated web-session collection.

Therefore this evidence is **not** upgraded to `automated_collection_authorized=true` yet.

It also does not prove:
- bulk/high-frequency collection;
- exact BLD authorization;
- complete historical-download rights;
- redistribution;
- commercial use;
- source-family completeness, PIT or schema coverage.

## Project effect

Current project interpretation:

- scope/use-rights evidence: **strengthened**
- `automated_collection_authorized=false`
- `sufficient_for_data_marketplace_tiny_probe_preflight=false`
- Gate A ceiling remains **BLOCKED**
- Gate F may cite this evidence but is not closed for every route/product/history requirement
- bulk history, feature performance testing, sealed holdout and live trading remain unauthorized

## Exact evidence needed for upgrade

Either of the following would close the wording/origin ambiguity:

1. an email/thread view showing the KRX sender identity together with the original question that explicitly asked about programmatic/automated low-frequency querying and this reply; or
2. a KRX follow-up reply explicitly stating that the permitted "저빈도 조회" includes **프로그램을 이용한 자동 조회** for the stated personal, non-commercial, internal-research purpose.

Ambiguous evidence must remain fail-closed.
