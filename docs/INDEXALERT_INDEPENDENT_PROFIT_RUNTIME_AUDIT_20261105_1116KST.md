# IndexAlert 독립 수익성·최적화 감사 — 2026-11-05 11:16 KST

읽기전용 조회 기준. 기존 연구/개발/PR 코드는 수정하지 않았으며 이 문서는 새 성능실험이나 승인서가 아니다.

## 현재 HEAD (GitHub 직접 조회)
- research index-alert-research-v1: df474df348f22aa38b1dedaa59fcff66e548b406
- development index-alert-position-regen-fix-v1: 1e6367d2863a86c3470da13d81a955d277eba485
- Draft OPEN PR #412: bf3d9514a87c53b1775e22ec9ba7711f6cecc49f
- Draft OPEN PR #413: f003ef6247e16fcc71bd3b1b20cd4904c4d984c0
- Draft OPEN PR #414: 18c5418d9684d1717df58261ea27f28e514385b2
- Draft OPEN PR #418: 2f98401cc50a6c6a25808a98516efd5bf0c944ee
- Draft OPEN KRX #420: fab3cbbd63a951a4e081f9e7f08c1391ca308581
- Draft OPEN KRX #422: c14857620973531013799e44625d43080904fd5f
- Draft OPEN KRX #423: 0e38004363cac9fc4475556b3a1c445de9af407f
- PR #414 gate document blob SHA-1: 984c933651f39f1ee9e26a1d7ac3893aaa5335be

## CI (GitHub jobs 직접 조회)
- 38381997417: 6/6 success; 38382214223: 6/6 success; 38419111311: 6/6 success
- 38419649711: 1/1 success; 38419439742: 2/2 success
- 41515392296: 1 failure, 1 skipped (Chronology Anchor)
- 고정 34-case SHA-256 5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34 및 2.9656/2.6209=1.1315x는 이전 증거이며 이번 실행에서 재계산하지 않음. 전체 CI 및 실제 백테스트 속도 NOT VERIFIED.

## Railway production (직접 조회)
- KRX worker SUCCESS 배포 16c93d7c-7cd0-4d84-a327-298d2805376c, commit 1e6367d2863a86c3470da13d81a955d277eba485.
- PIT rebuild SUCCESS 배포 8b354fc1-cfb2-4ef0-863e-67f7f5dda2b5, commit e57054ecdb3e734ced3c9a981b887d9b5fc60f97.
- 2026-11-05 01:00 UTC 이후 두 서비스 deploy 로그 각 0건. Runtime deploy 로그 조회에서 USD/KRW Yahoo 대체 데이터 사용 관측. 공식 시장 PIT 승인 증거가 아님.
- Backend/Push 최신 배포 FAILED. staged pendingWork 1건, 적용하지 않음. replica 수는 이번 get_status에서 null로 반환되어 실행 인스턴스 상태 NOT VERIFIED.

## 독립 판정
- 과거 KRX private 1565/1565 원본쌍 저장 무결성: 과거 제한적 PASS, 이번 재해시 미수행.
- 공식 KRX 달력·거래상태·기업행위·체결가능성·비용/세금: NOT VERIFIED.
- OpenDART original-filing/public available-at, 2021·2022 최초 연결 3개월 영업이익 기간·정정 lineage: NOT VERIFIED; 후보행 숫자 인접 일치는 의미·시점 승인 아님.
- 과거 기업·종목 mapping, PIT label/Purged/CPCV/독립 Holdout, NetEV/PF/CAGR/MDD/ES95/99/집중도·시점 강건성: NOT VERIFIED.
- Chronology Anchor: FAIL; H5 실패/소비 Holdout 재사용 금지.
- M20 경제성: NOT EVALUABLE / NO-GO. ORDERING=false, Champion 승격·주문·배포·병합 금지.

## 다음 허용 작업
공식 최초공시 public available-at와 정정 계보, KRX 실제 거래일/상태·기업행위 원본의 독립 SHA 증빙을 먼저 확보하고 승인 게이트 문서와 대조. PR #413/#418은 오프라인 합성 테스트의 fail-closed cache key(원본·데이터·코드·Frozen·런타임·승인 evidence SHA-256)와 읽기전용 후처리 병렬성만 검사. 재학습/capital transition 병렬화, 새 경제성/모델 탐색/M20 RUN 금지. 다른 담당 브랜치 코드 수정·workflow 우회·자동 병합·운영 변경 금지.
