# IndexAlert 독립 수익성·최적화 감사 — 2026-11-10 09:16 KST

## 범위 및 원칙
GitHub/Railway 읽기전용 확인. 공식 PIT 미승인, M20 경제성 RUN 금지, H5 소비 Holdout 재사용 금지. ORDERING=false, Frozen H5, M20 horizon20/purge20, WF504/126/126, CPCV/독립 Holdout/Champion/Top3/NO_TRADE 유지. 병합·배포·거래·권한 변경 없음.

## GitHub 최신 HEAD 및 상태
- 연구 `index-alert-research-v1`: `df474df348f22aa38b1dedaa59fcff66e548b406`.
- 개발 `index-alert-position-regen-fix-v1`: `1e6367d2863a86c3470da13d81a955d277eba485`. compare research...development DIVERGED, development ahead 1148 / behind 281; merge-base `c490974ff6619bb978dc6f83f9c24f2c46622f85`.
- PR #412 OpenDART `bf3d9514a87c53b1775e22ec9ba7711f6cecc49f`; #413 최적화 `f003ef6247e16fcc71bd3b1b20cd4904c4d984c0`; #414 총괄 `18c5418d9684d1717df58261ea27f28e514385b2`; #418 단일 runner `2f98401cc50a6c6a25808a98516efd5bf0c944ee`; #420 `fab3cbbd63a951a4e081f9e7f08c1391ca308581`; #422 `c14857620973531013799e44625d43080904fd5f`; #423 `0e38004363cac9fc4475556b3a1c445de9af407f`. 모두 OPEN/Draft/unmerged.
- 총괄 문서 PR #414 HEAD 파일 `docs/INDEXALERT_PROFITABILITY_INTEGRATION_GATE_2026-10-13.md` blob SHA `984c933651f39f1ee9e26a1d7ac3893aaa5335be`; 연구 브랜치의 같은 경로는 조회 실패. PR #414의 문서를 연구 HEAD에 존재하는 것으로 오인하지 말 것.
- Actions 38381997417, 38382214223, 38419111311 각 6/6 jobs success; 38419649711 1/1 success; 38419439742 2/2 success. 41515392296 auto-anchor FAILURE / validation SKIPPED. 이는 job 결과이며 공식 원본/PIT 승인 아님. 과거 34-case 고정 SHA `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34` 및 1.1315x regression-phase 수치는 과거 증거로만 보존; 이번 회차 artifact byte 재해시/전체 wall-clock 측정 없음.

## Railway production 최신 읽기
Project `d1c1a050-b7d6-41ce-b300-13c20f82a20a`, environment `83d5840b-270e-4d3f-a941-a37fd4a55ff7`. PIT rebuild deployment `8b354fc1-cfb2-4ef0-863e-67f7f5dda2b5` SUCCESS; KRX worker `16c93d7c-7cd0-4d84-a327-298d2805376c` SUCCESS; runtime `eaaa9f67-b9f2-41d2-832c-7d6fad9b9b00` SUCCESS. Backend `cce12a43-592a-4910-9b75-89c6b7cdd159` FAILED; Push `3ad3102d-ced6-416b-a6da-85c390c9a606` FAILED. All get_status numReplicas null: 실제 replica/건강상태 NOT VERIFIED. stagedChanges null이나 pendingWork에 changes=[]인 staged patch `e113dacb-6705-4416-9997-dc694539d382` 표시: 조회 불일치, 변경 금지.
- 2026-11-09 22:00Z ~ 2026-11-10 00:20Z deploy logs: PIT 0, KRX 0, real-readonly-run 0; 해결/정상화 근거 아님. Runtime 101 entries, 00:15Z Investing USD/KRW HTTPError -> Yahoo fallback 확인; 환율 fallback은 PIT 승인 증거 아님.

## 독립 판정
- KRX 1565/1565 평일 원본쌍 저장 무결성: 과거 증거 PASS (이번 재해시 없음); 공식 달력/거래상태/기업행위/체결가능성/비용·세금: NOT VERIFIED.
- OpenDART SGML 15 후보행 숫자 인접 시그니처: 과거 증거 PASS(형태 검사만); 최초공시 original-filing 의미, 정확한 public available-at, 2021/2022 최초 3개월 연결 영업이익 기간·정정 lineage, 과거 corp/security mapping: NOT VERIFIED.
- PIT/라벨/체결/세후 NetEV, PF, CAGR, MDD, ES95/99, 수익 집중도, 시점별 강건성: NOT VERIFIED; M20 RUN NO-GO.
- 최적화 오프라인 CI jobs PASS; 전체 CI/실제 공식 백테스트 속도 및 독립 SHA evidence-chain: NOT VERIFIED.
- Chronology Anchor FAIL, 후속 validation SKIPPED; 성공으로 승격 금지.

## 다음 안전 단계
담당 트랙의 공식 원본 증거/정정 계보/available-at/기업행위/거래상태를 독립 SHA 및 원본 로그로 재검증. 안전한 합성 오프라인 CI만 허용; 승인 SHA-256 전체 결합 cache fail-closed, 읽기전용 독립 후처리만 병렬화. workflow 변경 우회 금지. 모든 소스 게이트 통과 전 M20 성과 실행 및 승격 금지.
