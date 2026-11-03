# IndexAlert 독립 수익성·런타임 증거 점검 — 2026-10-28 12:18 KST

> **증거 점검만 수행; 승인서 아님.** 본 기록은 소스/CI의 GitHub 읽기전용 확인과 Railway 조회 차단을 구분한다. 다른 Work 소유 코드·workflow·원본 게이트는 수정하지 않았고, M20 수익률 계산·Holdout·실거래·배포·병합은 수행하지 않았다.

## 1. 직접 확인한 정확한 ref/HEAD

| 범위 | GitHub SHA | 판정 |
|---|---|---|
| 연구 `index-alert-research-v1` | `3b8b7830612a6284d7c7a60628cb527cb741627a` | read-only |
| 개발 `index-alert-position-regen-fix-v1` | `1e6367d2863a86c3470da13d81a955d277eba485` | read-only |
| KRX source audit `indexalert-krx-pit-source-audit-20261013` | `073d2d49e95f69fb10b943b93e51bb179fb3c698` | read-only |
| OpenDART Draft PR #412 | `bf3d9514a87c53b1775e22ec9ba7711f6cecc49f` | OPEN/DRAFT |
| Runtime Draft PR #413 | `f003ef6247e16fcc71bd3b1b20cd4904c4d984c0` | OPEN/DRAFT |
| 총괄 Draft PR #414 (이 기록 쓰기 전) | `b6c0c38bf9c64f373938313f559bf04207c0a449` | OPEN/DRAFT |
| 투자자 수급 Draft PR #416 | `053de553646fc4765d2616544ca1e8d6bbdde35f` | OPEN/DRAFT |
| 단일 runner Draft PR #418 | `2f98401cc50a6c6a25808a98516efd5bf0c944ee` | OPEN/DRAFT |
| KRX Draft PR #420 / #422 / #423 | `fab3cbbd63a951a4e081f9e7f08c1391ca308581` / `c14857620973531013799e44625d43080904fd5f` / `0e38004363cac9fc4475556b3a1c445de9af407f` | OPEN/DRAFT |

기존 총괄 게이트 `docs/INDEXALERT_PROFITABILITY_INTEGRATION_GATE_2026-10-13.md`의 Git blob SHA-1은 `984c933651f39f1ee9e26a1d7ac3893aaa5335be`; 원문 수정 없음. 직전 [11:16 독립 감사](https://github.com/kims34/openpilot-opkr/blob/1e9c1894acc681d17162c52c76cb067309aaa092/docs/INDEXALERT_INDEPENDENT_PROFIT_RUNTIME_AUDIT_20261028_1116KST.md) 및 [11:51 총괄 독립 게이트](https://github.com/kims34/openpilot-opkr/blob/b6c0c38bf9c64f373938313f559bf04207c0a449/docs/INDEXALERT_PROFITABILITY_INDEPENDENT_GATE_20261028_1151KST_AUTOMATION11.md)를 읽고 중복 변경을 피했다.

## 2. 최적화 분기: 서로 다른 PASS/FAIL을 섞지 않는다

- #413 [Action 38508247773](https://github.com/kims34/openpilot-opkr/actions/runs/38508247773): 6/6 CI jobs PASS. 실제 parity job `115670744341`의 `RUNTIME_OPT_PARITY`: 34-case SHA-256 `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34`, `test_outcomes_identical=true`, serial 1.7650s / parallel longest 2.7079s, speed ratio **0.652x** (병렬이 느림). `ci_end_to_end_speedup_measured=false`, `actual_backtest_speedup_measured=false`.
- #418 [Action 39111405562](https://github.com/kims34/openpilot-opkr/actions/runs/39111405562): one-runner offline job `117628139856` PASS, 동일 34-case archived SHA 유지; 제한된 test subprocess phase ratio 1.1521x, 전체 CI 및 공식 백테스트 속도 개선 NOT VERIFIED.
- #418 [candidate merge proof Action 39111405494](https://github.com/kims34/openpilot-opkr/actions/runs/39111405494), job `117628139749`: CI job은 **PASS**지만 내부 영수증 `CANDIDATE_MERGED_SOURCE_PROOF`는 `candidate_approved_for_merge=false`, `all_transitive_imports_pinned=false`, `original_archived_manifest_replayed_without_change=false`, checked_files=22, exact_four_reviewed_candidate_code_blobs_verified=true라고 명시. 즉 **CI PASS는 통합 승인 PASS가 아니다.**
- 같은 #418의 [pinned parallel Action 39111405478](https://github.com/kims34/openpilot-opkr/actions/runs/39111405478), job `117628139395`는 **FAIL**: `SourceDriftError` on `research_v1_runtime_manifest.py`, archived Git blob SHA-1 `108f66714602a1bd3ae42c34dcca7c16e38f460b` vs merged-context observed `e0055c66c59398fd4a1158077446d886b54c4e37`. 독립 #418 HEAD 손상이라고 해석하지 않으며, 기대 해시 재기록·우회·병합 금지.
- `compare_commits` direct: #413 대비 #418 branch **diverged**, ahead 49 / behind 18; 결합 안전성 NOT VERIFIED. #418 독립 캐시의 명시적 False 권한 검증/TOCTOU 보강이 #413 최신 구현과 다르다는 11:16 정적 비교를 계속 승인 차단으로 유지.
- 캐시 허용은 독립 승인된 source/data/code/Frozen/runtime/evidence SHA-256 전체 일치 및 immutable lineage가 전제다. 단순 내부 hash/22 files/34 tests는 독립 PIT authority가 아니다. 병렬화는 읽기전용 후처리로 한정한다.

## 3. 원본/PIT 및 운영 증거

- [Watchdog 40604202566](https://github.com/kims34/openpilot-opkr/actions/runs/40604202566) job `122539521979` 성공; 실제 로그 `M20 PIT admission: NOT ATTESTED; orders: DISABLED; holdout: NOT AUTHORIZED`; offline governance 35 tests PASS. 이는 Railway live `ORDERING` 증명이 아님.
- [Chronology 40534270813](https://github.com/kims34/openpilot-opkr/actions/runs/40534270813): auto-anchor job `122295113858` FAIL (HTTP 404), validation job `122295116456` SKIPPED. Prospective public available-at NOT VERIFIED.
- [OpenDART #412 Action 40263193758](https://github.com/kims34/openpilot-opkr/actions/runs/40263193758): synthetic TOC CI PASS. 2021 original ZIP SHA-256 `8728c0a3c12761ca19e9c6455bea8f1bed0e4c1ebc2e21dc263c373a82a2b625`, 2022 `56639d8f6ebbecf14cd8bc3179d75d01162e2cd7bbdf8f6a3c9479b44f5084bb`는 **이전 official Actions 로그의 기록**이며 이번 실행에서 원본 ZIP bytes 재해시 안 함. 2021/2022 최초 3개월 연결 영업이익 cell/기간/정정 lineage/정확한 공개시각/기업-종목 역사 매핑 NOT VERIFIED.
- [KRX 39721289545](https://github.com/kims34/openpilot-opkr/actions/runs/39721289545) job `119635081965`: 164개 오프라인 synthetic source/venue/holiday/XLSX safety tests PASS. [KRX #423 39714207925](https://github.com/kims34/openpilot-opkr/actions/runs/39714207925) job `119612335677` PASS지만 `DRY_RUN_NO_PRIVATE_STORAGE_READ` 및 `2022_private_candidate_date_sets_equal=false` 확인. 1,565/1,565 weekday private 저장쌍 SHA 무결성은 과거 기록상 PASS이나 공식 KRX 시장별 2021 13일/2022 14일 정확한 private 날짜집합·실거래상태·기업행위·체결가능성 NOT VERIFIED. 90개 세션 분류, 27 비정상 OHLC, zero-activity 12,003건 격리 유지.
- Railway 네이티브 `list_projects({})` 읽기전용 호출 1회 시도 결과 `User input required but current turn is running in a non-interactive mode.`로 인증 입력 차단. 비대화형 우회 안 함. 최신 live deployments/logs/actual ORDERING **NOT DIRECTLY VERIFIED**.

## 4. 판정 및 허용 다음 단계

**M20 PIT / economic RUN = NO-GO.** NetEV after costs/taxes, PF, CAGR, MDD, ES95/99, 수익 집중도 및 시점별 강건성 **NOT EVALUABLE** (0이나 수익성 FAIL이 아님). 독립 원본 승인 전 M20/새 전략·성능탐색/시장 백테스트 금지. Frozen H5, M20 horizon20/purge20, WF504/126/126, PIT/Purged/CPCV, sealed Holdout, Champion/Top3, Dynamic Challenger-only, NO_TRADE, 비용·세금·승격 기준 유지. `ORDERING=false` 정책을 반드시 유지하되 실제 운영 설정을 확인했다고 주장하지 않는다.

다음 허용 단계: 소스 담당이 독립 원본 byte/SHA 및 public available-at·3개월 CFS period/correction lineage 증명; KRX 담당이 공식 시장별 달력·private exact-set·종목별 거래가능성 원본 증명; 최적화 담당이 별도 오프라인 환경에서 **동일 고정 snapshot**에 대한 #413 보안 보강과 #418 runner 통합 후보의 전체 transitive dependencies/immutable receipt/34-case parity를 검증. 세 게이트 모두 승인 전에는 공식 M20 실행 금지. 운영 배포, 자동병합, workflow 수정, 실주문·자금이동·계좌권한 변경, Champion 승격 없음.
