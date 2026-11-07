# IndexAlert 독립 수익성·격리 최적화 감사 — 2026-11-07 14:18 KST

## 범위와 불변 조건
읽기전용 GitHub PR 메타데이터/통합 게이트 blob, Railway production 환경 상태 및 2026-11-07 12:00 KST 이후 로그 확인. 본 문서는 기존 PR #414의 코드/정책을 변경하지 않는 별도 브랜치 기록이다. M20 경제성 실행, 모델 탐색, 실거래, 배포, 병합, workflow 변경 없음. ORDERING=false 요구 유지(운영 변수값 자체는 이 조회로 독립 확정하지 못함). Frozen H5; M20 horizon20/purge20; WF504/126/126 및 독립 holdout/NO_TRADE/Top3 정책 불변.

## GitHub 독립 확인
- PR #412 OPEN Draft HEAD bf3d9514a87c53b1775e22ec9ba7711f6cecc49f
- PR #413 OPEN Draft HEAD f003ef6247e16fcc71bd3b1b20cd4904c4d984c0
- PR #414 OPEN Draft HEAD 18c5418d9684d1717df58261ea27f28e514385b2
- PR #418 OPEN Draft HEAD 2f98401cc50a6c6a25808a98516efd5bf0c944ee
- KRX #420 OPEN Draft HEAD fab3cbbd63a951a4e081f9e7f08c1391ca308581
- KRX #422 OPEN Draft HEAD c14857620973531013799e44625d43080904fd5f
- KRX #423 OPEN Draft HEAD 0e38004363cac9fc4475556b3a1c445de9af407f
- PR #414 통합 문서 blob SHA 984c933651f39f1ee9e26a1d7ac3893aaa5335be (connector fetch 직접 확인).
- 연구/개발 브랜치 최신 HEAD는 이 실행에서 독립적으로 확인하지 못함. 이전 기록의 연구 df474df348f22aa38b1dedaa59fcff66e548b406 / 개발 1e6367d2863a86c3470da13d81a955d277eba485는 과거 증거로만 취급.
- Actions 직접 조회: 도구에서 개별 workflow run 조회 기능을 제공하지 않고 공개 URL 열람도 차단되어 이번 실행의 최신 run 상태는 NOT VERIFIED. 이전 기록 38419439742, 38419649711, 38498552499의 성공과 41515392296 실패는 이번 실행의 신규 독립 PASS로 재인증하지 않음.

## Railway production 직접 조회
Project d1c1a050-b7d6-41ce-b300-13c20f82a20a, environment 83d5840b-270e-4d3f-a941-a37fd4a55ff7.
- indexalert-kiwoom-real-readonly: deployment a77fb922-b679-4d88-92c4-03054ec579cd SUCCESS이나 replica running=0/crashed=1/total=1. 실제 프로세스 건강 FAIL, dashboard online 표시는 반증.
- indexalert-pit-rebuild: deployment 8b354fc1-cfb2-4ef0-863e-67f7f5dda2b5 SUCCESS, replica 1/1.
- indexalert-krx-historical-worker: deployment 16c93d7c-7cd0-4d84-a327-298d2805376c SUCCESS, replica running=0/crashed=0/total=1. 작업 완료/대기인지 별도 검증 필요.
- indexalert-runtime: deployment eaaa9f67-b9f2-41d2-832c-7d6fad9b9b00 SUCCESS, replica 1/1.
- db-query-readonly critical=1; indexalert-push warning=1; indexalert-backend warning=4.
- staged pending patch e113dacb-6705-4416-9997-dc694539d382, changes=[] (적용/삭제 금지).
- 2026-11-07 12:00 KST 이후 PIT/KRX/real-readonly deploy 로그 없음. 이는 문제 해결 PASS가 아님.
- Runtime 2026-11-07 14:17 KST 부근 로그: Investing.com USD/KRW HTTPError → Yahoo fallback; KOSPI CLOSED, 야간 프록시 unavailable. 표시용 시장 시세이며 M20 공식 거래가능성/수익성 증거 아님.

## 게이트 판정
- KRX 2017–2022 weekday 1565/1565 원본쌍 저장 무결성: 과거 확인 PASS (이번 실행 재검산 아님).
- KRX 공식 휴장/거래상태/기업행위/실체결/비용세금: NOT VERIFIED, FAIL-CLOSED. zero-activity 12003건 및 90일 분류 미승인.
- DART original-filing public available-at, 2021/2022 최초 연결 3개월 영업이익 기간/정정 lineage 및 과거 corp/security mapping: NOT VERIFIED, FAIL-CLOSED.
- 기존 H5 holdout 재사용/사후 조정: 금지 유지.
- PR #413/#418 합성 오프라인 CI 결과: 과거 기록 PASS, 이번 최신 CI 재조회 NOT VERIFIED. 1.1315x는 regression phase 비교이며 전체 공식 백테스트 가속 NOT VERIFIED.
- M20 공식 PIT/경제성 RUN: NO-GO. NetEV/PF/CAGR/MDD/ES95/99/수익 집중도/시점별 강건성: NOT VERIFIED.

## 다음 안전 검증
1. 담당 OpenDART/KRX 독립 원본 SHA와 official available-at, calendar/status lineage를 담당 PR/Actions 증거로 확인. 승인 전 M20 미실행.
2. Chronology Anchor 404와 해당 배포 라우팅/응답 계약을 읽기전용 확인.
3. Railway real-readonly crashed replica 및 db-query-readonly critical 원인 로그를 읽기전용 추적; 운영 변경은 별도 승인 필요.
4. PR #413/#418 원본 CI artifacts의 34-case SHA, synthetic 28건, cache fail-closed key와 순차 capital transition 제약을 재검증. 성능 신규 실험 금지.

독립 감사 브랜치 이외의 기존 전담방 소유 코드/PR 변경 없음.
