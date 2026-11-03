# IndexAlert 독립 검증 — 2026-11-04 03:17 KST

## 현재 읽기전용 출처
- PR #412 HEAD bf3d9514a87c53b1775e22ec9ba7711f6cecc49f, #413 f003ef6247e16fcc71bd3b1b20cd4904c4d984c0, #414 18c5418d9684d1717df58261ea27f28e514385b2, #418 2f98401cc50a6c6a25808a98516efd5bf0c944ee: 모두 Draft OPEN.
- KRX #420 HEAD fab3cbbd63a951a4e081f9e7f08c1391ca308581, #422 c14857620973531013799e44625d43080904fd5f, #423 0e38004363cac9fc4475556b3a1c445de9af407f: Draft OPEN.
- 연구 index-alert-research-v1 및 개발 index-alert-position-regen-fix-v1 브랜치 존재 재확인. **현재 정확한 HEAD NOT VERIFIED**. 과거 df474df348f22aa38b1dedaa59fcff66e548b406 / 1e6367d2863a86c3470da13d81a955d277eba485는 현 HEAD로 단정 금지.
- PR #414 게이트 문서 GitHub ref=indexalert-profitability-integration-evidence-20261013에서 읽기 성공. 현재 문서 blob SHA는 이번 호출 반환 중 별도 추출하지 못함.
- Actions 38419111311: 6/6 SUCCESS; 38419649711: 1/1 SUCCESS; chronology 41515392296 auto-anchor FAILURE, validation SKIPPED. 고정 34-case SHA 5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34는 과거 근거이며 이번 독립 재계산 아님.
- Railway IndexAlert project d1c1a050-b7d6-41ce-b300-13c20f82a20a: production app deployment a77fb922-b679-4d88-92c4-03054ec579cd SUCCESS (2026-10-29), KRX worker 16c93d7c-7cd0-4d84-a327-298d2805376c SUCCESS (2026-10-12). 2026-11-03T00:00Z 이후 두 서비스 deploy log 요청 결과 각각 0 entries; 과거 OHLC 오류가 해결됐다는 증거가 아님.

## 독립 판정
- 2017–2022 KRX 1565/1565 private weekday raw pairs: **historical storage integrity PASS only**; 공식 거래일/정지/기업행위/과거 종목 매핑/체결·세금 **NOT VERIFIED**.
- OpenDART original filing SHA 및 15개 영업손익 후보 형태: **historical byte-level evidence only**; 2022·2021 최초 연결 3개월 영업이익 기간·정정 lineage 및 정확한 public available-at **NOT VERIFIED**.
- Chronology Anchor: **FAIL**. PIT admission **FAIL-CLOSED**.
- PR #413/#418 offline synthetic software CI: **limited PASS**; cache SHA-256 end-to-end independent approval, actual M20 wall-clock improvement **NOT VERIFIED**. 과거 단일 runner 2.9656초 vs concurrent suite 2.6209초는 regression-phase 1.1315x일 뿐.
- NetEV/PF/CAGR/MDD/ES95/99/수익 집중도/연도별 강건성/세후 연간 위험조정 수익: **NOT EVALUABLE / NO-GO**; M20 성과 실행 금지.

## 경계 및 다음 단계
Frozen H5, M20 horizon20/purge20, WF504/126/126, PIT/Purged/CPCV/독립 Holdout/Champion/Top3/NO_TRADE 및 비용·세금·승격 기준 고정. ORDERING=false. 기존 Holdout 재사용·Dynamic 사후조정 금지. 캐시는 독립 승인 원본·데이터·코드·Frozen·런타임·승인 evidence SHA-256 전부 일치할 때만 fail-closed, 읽기전용 후처리만 병렬화. 공식 PIT 증명 전에는 합성 오프라인 검증만 허용. 다음: OpenDART 최초 시점/원본 연결 3개월 수치, KRX 공식 시장 상태/체결가능성, Chronology Anchor 독립 원본 SHA를 각 담당자가 증명한 뒤 총괄 재판정. 병합·운영 배포·주문·자금이동·Champion 승격 없음.
