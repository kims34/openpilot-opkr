# IndexAlert 독립 수익성·최적화 감사 — 2026-11-07 21:22 KST

## 범위와 안전 경계
GitHub 및 Railway 커넥터로 읽기전용 조회. 이 문서는 승인 증거가 아니며 기존 Frozen H5, M20 horizon20/purge20, WF504/126/126, PIT/Purged/CPCV/독립 Holdout/Champion/Top3/NO_TRADE 및 비용·세금·위험 정책을 변경하지 않는다. M20 PIT/경제성 RUN **NO-GO**. ORDERING=false(DISABLED), 주문/자금/권한/Champion 승격/운영배포/병합 없음. 소스 PIT 승인 전 합성 오프라인 테스트만 허용.

## 이번 실행에서 직접 확인한 GitHub 증거
- PR #412 HEAD `bf3d9514a87c53b1775e22ec9ba7711f6cecc49f`; #413 `f003ef6247e16fcc71bd3b1b20cd4904c4d984c0`; #414 `18c5418d9684d1717df58261ea27f28e514385b2`; #418 `2f98401cc50a6c6a25808a98516efd5bf0c944ee`.
- KRX PR #420 `fab3cbbd63a951a4e081f9e7f08c1391ca308581`; #422 `c14857620973531013799e44625d43080904fd5f`; #423 `0e38004363cac9fc4475556b3a1c445de9af407f`. 전부 OPEN/Draft, 미병합.
- PR #414 `docs/INDEXALERT_PROFITABILITY_INTEGRATION_GATE_2026-10-13.md` blob SHA `984c933651f39f1ee9e26a1d7ac3893aaa5335be` 재조회.
- Actions #38381997417, #38382214223, #38419111311, #38498552499: 각각 6/6 success. #38419649711: 1/1 success. #38419439742: 2/2 success. #41515392296: auto-anchor FAILURE, validation SKIPPED.
- 34-case SHA `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34`, 13 adversarial mocks, 추가 28 synthetic, serial 2.9656s / concurrent 2.6209s (1.1315x)은 이전 증거의 주장으로만 보존; 이번 job 목록 조회로 artifact 내용 및 SHA 자체를 독립 재계산하지 않음. 전체 CI 및 공식 백테스트 가속 NOT VERIFIED.
- 연구 `index-alert-research-v1`, 개발 `index-alert-position-regen-fix-v1` 브랜치 README 경로 조회가 404였으므로 해당 브랜치 최신 HEAD는 **NOT VERIFIED**. PR base SHA를 브랜치 HEAD로 대체하지 않음.

## Railway production 원본 조회
- project `d1c1a050-b7d6-41ce-b300-13c20f82a20a`.
- `indexalert-pit-rebuild` latest deployment `8b354fc1-cfb2-4ef0-863e-67f7f5dda2b5`: SUCCESS(배포 상태일 뿐 데이터 승인이 아님). 2026-11-07 20:00/20:15/20:30/20:45/21:00/21:15 KST 로그에 `COMMON_OHLC_NONPOSITIVE`, 일반주식 803행 중 비정상 OHLC 27, zero volume/value 27 반복. `session_manifest_sha256=null`, `ordering=DISABLED`, independent source/chronology/model verified=false, fresh alpha admitted=false. 데이터 admission **FAIL_CLOSED**.
- `indexalert-kiwoom-real-readonly` latest deployment `a77fb922-b679-4d88-92c4-03054ec579cd`: SUCCESS. 이번 상태 API replica 필드는 null로 반환되어 실행/크래시 개수 **NOT VERIFIED**(이전 0 running/1 crashed 주장을 이번에 재확정하지 않음).
- `indexalert-krx-historical-worker` latest deployment `16c93d7c-7cd0-4d84-a327-298d2805376c`: SUCCESS, 이번 조회 구간 로그 0개. 실제 공식 달력/상태/거래가능성 NOT VERIFIED.
- `describe_environment` staged=null, `get_status` stagedChanges=null이나 pendingWork에 빈 변경목록의 `patch:e113dacb-6705-4416-9997-dc694539d382` staged로 노출: API 간 불일치 지속. 패치 적용하지 않음.

## 독립 판정
- PASS(범위 한정): 기존 GitHub synthetic CI job 성공; 2026-10-14 KRX 1565/1565 원본쌍 저장 무결성은 **이전 확인 증거**이며 이번 재해시 없음.
- FAIL: 현재 PIT source admission (COMMON_OHLC_NONPOSITIVE, fail-closed); Chronology Anchor auto-anchor job.
- NOT VERIFIED: 최초공시 original-filing/public available-at/PIT, 2021·2022 연결 최초 3개월 영업이익 기간·정정 lineage, 과거 기업/종목 매핑, KRX 공식 거래상태·기업행위·체결가능성, 세후 NetEV/PF/CAGR/MDD/ES95/99/수익 집중도·시점별 강건성, 전체 CI/공식 백테스트 가속. H5 실패/소비 Holdout 및 Dynamic 결과 독립 재사용 금지.

## 다음 안전 단계
1. 읽기전용으로 Chronology Anchor #41515392296 실패 단계 및 공개 원본 SHA/available-at 근거 확인.
2. PIT 비정상 27행의 공식 출처/세션 및 2026-09-28 source_failure_session 대조; 비정상 행 제거·보정으로 승인 우회 금지.
3. KRX 담당 PR #420/#422/#423의 공식 거래일/상태 증거, OpenDART #412 최초 공시 의미·시점 lineage 검증.
4. PR #413/#418은 격리된 합성 오프라인 CI parity와 fail-closed cache evidence SHA-256 조건만 검토. 재학습/capital transition 병렬화 금지.
5. 다른 전담 작업영역의 코드·workflow·PR·운영은 수정하지 않는다.
