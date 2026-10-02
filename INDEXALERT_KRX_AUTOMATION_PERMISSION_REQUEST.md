# IndexAlert KRX Automated Data Access Permission Request

Updated: 2026-10-02 KST  
Purpose: obtain explicit KRX guidance/permission before any automated Data Marketplace web-session collection.

Official contact surfaced by KRX Data Marketplace: `krxdata@krx.co.kr`  
Official homepage terms: `https://data.krx.co.kr/contents/MDC/INFO/informationController/MDCINFO003.cmd`

## Recommended subject

`[이용문의] KRX Data Marketplace 통계 데이터의 자동 조회 허용 여부 및 공식 제공 경로 문의`

## Recommended message

안녕하세요.

개인 내부 연구 목적으로 KRX Data Marketplace의 주식 통계 데이터를 이용하고 있습니다.
현재 KRX OpenAPI에서 제공·승인된 별도 서비스는 공식 OpenAPI 방식으로만 사용하고 있으며,
OpenAPI에 없는 아래 통계 데이터의 공식적인 이용 방법을 확인하고자 문의드립니다.

확인하고 싶은 데이터는 다음과 같습니다.

1. 매매거래정지 내역(개별종목) — MDCSTAT213 계열
2. 정리매매종목 현황 — MDCSTAT237 계열
3. 상장폐지종목 현황 — MDCSTAT238 계열
4. 상장폐지종목 시세 추이 — MDCSTAT239 계열
5. 투자자별 거래실적(개별종목) 일별추이 — 화면 12009 / MDCSTAT02303 계열

용도는 외부 판매·배포가 아닌 개인 내부 연구 및 모델 검증입니다.
KRX Data Marketplace 홈페이지 이용약관상 무단 자동수집이 금지되어 있는 점을 확인하였기 때문에,
사전 허용 없이 자동 조회를 진행하지 않고 아래 사항을 먼저 확인하고자 합니다.

- 위 통계를 프로그램이 로그인 세션을 이용해 소량·저빈도로 자동 조회하는 것이 허용되는지
- 허용되는 경우 별도 신청/승인 절차가 필요한지
- 허용되는 공식 API, OpenAPI 서비스 또는 데이터 상품이 따로 존재하는지
- 권장되는 공식 데이터 상품/엔드포인트/화면이 있다면 정확한 명칭
- 자동 조회 허용 시 호출 빈도 또는 기간 제한
- 조회 데이터를 개인 내부 연구 목적으로 저장·분석하는 것이 허용되는지
- 과거 전체 기간 데이터를 연구 목적으로 확보하려면 어떤 상품/절차를 이용해야 하는지
- 위 각 데이터의 재배포 없이 내부 연구에만 사용하는 경우 적용되는 이용조건

가능하다면 답변에
“개인 내부 연구 목적의 자동 조회가 허용되는지 여부”와
“허용되는 공식 접근 경로”를 명시해 주시면 감사하겠습니다.

감사합니다.

## Evidence intake rule

A KRX reply must **not** be translated into project automation permission unless it clearly identifies:
- KRX as issuer/respondent;
- the exact allowed route/product or screen family;
- whether automated collection is permitted;
- intended-use scope;
- any frequency/history/storage limitations;
- any validity period or revocation condition.

If the reply is ambiguous, `automated_collection_authorized` remains `false`.

Do not commit the user's email address, account ID, password, cookies, auth keys or other private identifiers. Preserve only a redacted copy/hash and non-secret authorization metadata.
