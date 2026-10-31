# IndexAlert 독립 총괄·최적화 읽기전용 증거 점검 — 2026-10-25 00:23 KST

> 격리 감사 기록만 추가. 본 기록은 M20 PIT 승인, 수익성 시험 허가, Holdout 접근, 주문 또는 PR 병합 승인이 아니다. 공식 원본/비공개 값/인증정보는 기록하지 않는다.

## 이번 실행에서 직접 조회한 기준 HEAD

| 대상 | SHA | 상태 |
| --- | --- | --- |
| 연구 `index-alert-research-v1` | `3b8b7830612a6284d7c7a60628cb527cb741627a` | 변경 없음; 2026-10-13 커밋 |
| 개발 `index-alert-position-regen-fix-v1` | `1e6367d2863a86c3470da13d81a955d277eba485` | 변경 없음; 2026-10-12 커밋 |
| 총괄 Draft PR #414 | `730dd6b3f827682ce9aebbade261745d5ccc8f65` | 문서 전용 격리 HEAD (이 감사 파일 생성 전) |
| 최적화 Draft PR #413 | `f003ef6247e16fcc71bd3b1b20cd4904c4d984c0` | 미병합 |
| 단일 runner Draft PR #418 | `2f98401cc50a6c6a25808a98516efd5bf0c944ee` | 미병합; #413 기반 |
| OpenDART Draft PR #412 | `e82b26e2431ea15a42888f073a4b0b72a2e11ef6` | 미병합 |
| KRX Draft PR #420 | `fab3cbbd63a951a4e081f9e7f08c1391ca308581` | 미병합 |
| KRX Draft PR #423 | `0e38004363cac9fc4475556b3a1c445de9af407f` | 미병합 |

## 이번에 직접 확인한 Actions 원본 로그 및 판정

- [최신 watchdog #40102733400](https://github.com/kims34/openpilot-opkr/actions/runs/40102733400), 2026-10-24 14:29 UTC: job SUCCESS, 로그 `M20 PIT admission: NOT ATTESTED; orders: DISABLED; holdout: NOT AUTHORIZED`. 아티팩트 ID `12563750481`, 업로드 ZIP SHA-256 `b787ec7cd669701d7daf1da17f16f70b3fb7e495df8f7f56ef93ec0c64dad8fd`. **안전성 플래그 점검 PASS**이나 실제 Railway 운영 변수 또는 데이터 PIT 승인 증거는 아님.
- [prospective chronology #39972035700](https://github.com/kims34/openpilot-opkr/actions/runs/39972035700), 2026-10-23: `/anchor/latest` 공식 prospective payload 취득 단계에서 HTTP 404, 후속 immutable chronology 기록/validation SKIPPED. **해당 prospective chronology 입증 FAIL**. 공개 시점 승인 불가. 과거에도 같은 유형 차단이 있었으므로 신규 복구라고 해석 금지.
- [OpenDART #39884427805](https://github.com/kims34/openpilot-opkr/actions/runs/39884427805) 및 [#39884427765](https://github.com/kims34/openpilot-opkr/actions/runs/39884427765), 2026-10-23: 최신 TOC/financial viewer **합성 오프라인 테스트 SUCCESS**. 최초 원본 2022/2021 연결 3개월 영업이익, 정확한 공개 시각, 정정 lineage 및 issuer/security 역사적 연결을 입증하지 못함.
- [KRX #39714369438](https://github.com/kims34/openpilot-opkr/actions/runs/39714369438) 및 [#39714207925](https://github.com/kims34/openpilot-opkr/actions/runs/39714207925), 2026-10-22: offline synthetic gate SUCCESS. 비공개 일별 원본·공식 시장달력·거래정지/상장폐지·기업행위·시점별 거래가능성/체결가능성의 독립 원본 대조는 **NOT VERIFIED**. 기존 저장 SHA 쌍 무결성 PASS를 시장 PIT 승인으로 승격하지 않음.
- [최적화 #413 최신 #38508247773](https://github.com/kims34/openpilot-opkr/actions/runs/38508247773), 2026-10-14: 6/6 jobs SUCCESS, 34-case 고정 SHA-256 `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34` 동일; serial 1.765s vs parallel 2.7079s. **오프라인 회귀 동등성 PASS / 병렬 시간 개선 FAIL (해당 실행 조건) / 전체 CI 가속 NOT VERIFIED**.
- [단일 runner #418 최신 #39111405562](https://github.com/kims34/openpilot-opkr/actions/runs/39111405562): offline runner job SUCCESS; 로그의 실제 34-case SHA는 동일, serial 2.3484s vs parallel longest 2.0154s. 해당 phase 비율은 전체 CI/공식 경제성 성능의 대리 지표가 아님. [동일 HEAD archived source gate #39111405478](https://github.com/kims34/openpilot-opkr/actions/runs/39111405478) **FAIL**: `research_v1_runtime_manifest.py` expected Git blob `108f66714602a1bd3ae42c34dcca7c16e38f460b`, observed `e0055c66c59398fd4a1158077446d886b54c4e37`. 정확한 wheel SHA 및 OS native dependency 동일성 **NOT VERIFIED**. 후보 소스 감사 [#39111405494](https://github.com/kims34/openpilot-opkr/actions/runs/39111405494) SUCCESS는 archived source FAIL을 해제하지 못함.

## 승인 게이트 (독립 원본 SHA/CI/운영 로그 기준)

| 검증 항목 | 판정 | 독립 승인까지 필요한 증거 |
| --- | --- | --- |
| OpenDART 최초 original-filing ZIP 바이트 식별 | 제한적 기존 PASS | 최초 본문에서 기간·연결·공표시점까지 별도 입증 |
| 2022·2021 최초 3개월 CFS 영업이익/정정 lineage/available-at | **NOT VERIFIED** | 최초 제출본별 기간·원본 수치·정정 시각·정확한 public timestamp |
| 과거 issuer-security mapping 및 KRX 실제 거래일/상태/기업행위 | **NOT VERIFIED** | 공식 원본과 역사적 유효시점·거래상태·비공개 snapshot SHA 대조 |
| 체결가능성/호가·슬리피지/수수료/세금 | **NOT VERIFIED** | 사전 고정 실행가능 비용 모델 및 공식 거래가능성 |
| NetEV / PF / CAGR / MDD / ES95·99 / 수익 집중도 / 시점별 강건성 | **NOT VERIFIED; 실행 금지** | 위 원본 승인 후 단 한 번 사전등록 평가; Holdout 재사용 금지 |
| #413/#418 오프라인 34-case identity | **PASS (범위 한정)** | 실제 경제성/전체 CI 가속으로 해석 금지 |
| #418 archived source identity | **FAIL** | 독립 소스 계보·전이 의존성 승인; 기존 원본 SHA 임의 변경 금지 |
| Railway IndexAlert 최신 배포·운영 로그/실제 주문 변수 | **NOT VERIFIED — connector interactive auth blocked** | 사용자 대화형 Railway 연결 인증이 선행되어야 읽기전용 조회 가능 |

## 정책·분업·후속 순서

- Frozen H5/Champion, M20 horizon20/purge20, WF504/126/126, PIT·라벨·Purged/CPCV·독립 Holdout·Top3/NO_TRADE, 비용·세금·NetEV·위험·승격 기준 불변. `ORDERING=false` **요구** 유지하되 Railway 실운영 변수 확인 불가.
- 소스 승인 전 공식 수익률 계산, M20 경제성, 모델 탐색, Holdout 접근, 캐시 경제성 재사용 **금지**. 최적화는 격리된 합성·오프라인 테스트만 가능. 캐시 승인은 원본/데이터/코드/Frozen 정책/런타임/승인 evidence의 전체 SHA-256 일치 조건에서만 fail-closed. 의존적 재학습과 자본 전이는 병렬화 금지.
- DART와 KRX 담당 코드/데이터/실험은 해당 전담방에 위임, 총괄은 독립 증거 통합만 수행. #413/#418 전담 코드 변경 없음.
- 다음 단계: (1) Railway 읽기전용 접근 복구 후 배포·로그·실제 `ORDERING` 확인, (2) DART 최초 원본 CFS/PIT 승인, (3) KRX 거래상태/기업행위/체결/비용·세금 승인, (4) #418 원본/환경 SHA 차단 해결의 독립 승인, (5) 그 후에만 사전등록 M20 1회 검증 여부 결정.
- 실매매·자금·인증/계좌권한 변경·배포·자동 병합·PR 병합·Champion 승격은 수행하지 않음. 이 문서는 권한 요청이나 승인으로 해석할 수 없음.
