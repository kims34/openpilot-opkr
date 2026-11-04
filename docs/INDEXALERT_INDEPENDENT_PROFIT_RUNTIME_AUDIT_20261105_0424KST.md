# IndexAlert 독립 수익성·최적화 안전 감사 — 2026-11-05 04:24 KST

## 범위와 판정
읽기전용 GitHub PR/Actions 및 Railway production 상태·로그 재확인. 공식 최초공시 original-filing public available-at/PIT, 2021·2022 최초 연결 3개월 영업이익 기간·정정 lineage, 과거 기업/종목 매핑, KRX 거래상태·기업행위·체결가능성·비용/세금: **NOT VERIFIED / FAIL-CLOSED**. 세후 연간 위험조정 순수익 NetEV/PF/CAGR/MDD/ES95/99/수익 집중도·시점 강건성: **NOT EVALUABLE**. M20 PIT/경제성 RUN **NO-GO**. H5 실패/소비 Holdout 및 Dynamic 결과 재사용 금지.

## GitHub 직접 확인
- 연구 브랜치 `index-alert-research-v1`, 개발 브랜치 `index-alert-position-regen-fix-v1`: 존재 확인; 현재 HEAD API 검증은 이번 회차 미완료 (**NOT VERIFIED**). 과거 HEAD df474df348f22aa38b1dedaa59fcff66e548b406 / 1e6367d2863a86c3470da13d81a955d277eba485는 현시점 HEAD로 단정하지 않음.
- Draft OPEN: PR #412 HEAD bf3d9514a87c53b1775e22ec9ba7711f6cecc49f; #413 f003ef6247e16fcc71bd3b1b20cd4904c4d984c0; #414 18c5418d9684d1717df58261ea27f28e514385b2; #418 2f98401cc50a6c6a25808a98516efd5bf0c944ee; KRX #420 fab3cbbd63a951a4e081f9e7f08c1391ca308581; #422 c14857620973531013799e44625d43080904fd5f; #423 0e38004363cac9fc4475556b3a1c445de9af407f.
- PR #414 게이트 문서 `docs/INDEXALERT_PROFITABILITY_INTEGRATION_GATE_2026-10-13.md` blob SHA-1 `984c933651f39f1ee9e26a1d7ac3893aaa5335be` 직접 확인 (PR #414 HEAD).
- Actions #38381997417, #38382214223, #38419111311: 각각 6/6 success; #38419649711 1/1 success; OpenDART #38419439742 2/2 success; chronology #41515392296 auto-anchor failure / validation skipped. GitHub jobs API 결과. 기존 34-case SHA-256 `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34`, 13 adversarial mocks, 28 synthetic 및 2.9656/2.6209=1.1315x는 이번 회차 독립 재계산 없음: **과거 보고 증거**, 전체 CI/공식 백테스트 가속 **NOT VERIFIED**.
- OpenDART 15 SGML 후보행 숫자 인접 시그니처는 과거 기록; 최초 원본 의미·공개시점·기간 lineage 승인 아님. KRX 1565/1565 weekday 쌍 저장 무결성 과거 PASS; 실제 공식 거래일·상태·체결가능성 NOT VERIFIED.

## Railway production 직접 확인
Project `d1c1a050-b7d6-41ce-b300-13c20f82a20a`, environment `83d5840b-270e-4d3f-a941-a37fd4a55ff7`.
- KRX worker deployment `16c93d7c-7cd0-4d84-a327-298d2805376c` SUCCESS, commit `1e6367d2863a86c3470da13d81a955d277eba485` (2026-10-12); PIT rebuild `8b354fc1-cfb2-4ef0-863e-67f7f5dda2b5` SUCCESS (2026-10-10); runtime `eaaa9f67-b9f2-41d2-832c-7d6fad9b9b00` SUCCESS (2026-10-05). KRX/PIT deploy logs 2026-11-05 03:00~04:24 KST 조회 결과 0건: 성공/승인 추론 금지. Runtime은 04:24 KST 무렵 지수/환율 조회 및 Yahoo fallback을 기록했지만 공식 PIT 증거 아님.
- `indexalert-kiwoom-real-readonly`: UI online / deployment SUCCESS이나 replicas running=0, crashed=1 (불일치, **운영 건강성 blocker**). `indexalert-push` offline warning 1, `indexalert-backend` offline warning 4, `db-query-readonly` offline critical 1. 이전 회차에도 관측된 상태로 신규 장애 단정 금지.
- Pending staged patch `e113dacb-6705-4416-9997-dc694539d382` 존재; 적용/승인 금지.

## 최적화 경계 및 다음 단계
PR #413/#418 합성 오프라인 정책 테스트 PASS 범위 외 경제성/실시장 가속 주장 금지. 독립 승인 원본·데이터·코드·Frozen 정책·런타임·승인 evidence SHA-256 모두 동일한 캐시만 fail-closed, 읽기전용 후처리 병렬화만 허용. 재학습·capital transition 병렬화 금지. Frozen H5, M20 horizon20/purge20, WF504/126/126, PIT/라벨/Purged/CPCV/독립 Holdout/Champion/Top3/NO_TRADE 및 비용·세금·체결·위험·승격 기준 불변. ORDERING=false. 다음은 OpenDART 최초 공시 원본·public available-at/2021·2022 lineage 독립 입증, 공식 KRX calendar/status/corporate actions와 mapping·실체결 검증, chronology FAIL 원인 read-only 조사, 운영 replica/critical 상태 read-only 진단, 합성 안전 회귀만. 신규 시장 수익률·M20 경제성 실험·모델 탐색·병합·배포·주문·권한 변경·승격 없음.
