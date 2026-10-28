# IndexAlert 독립 수익성·최적화 감사 — 2026-10-28 10:16 KST

> 증거만 읽고 독립 문서 1개만 기록. 이 문서는 원본/PIT/거래/수익성/승격 승인서가 아니다. 외부 원본이나 인증정보·금융값·계좌·종목별 데이터는 저장하지 않는다. 다른 전담 Work의 코드·실험·워크플로는 변경하지 않는다.

## 1. 직접 조회한 최신 고정 HEAD

| 대상 | 조회 HEAD | 변화 |
|---|---|---|
| 연구 `index-alert-research-v1` | `3b8b7830612a6284d7c7a60628cb527cb741627a` | 기존 대비 0/0 |
| 개발 `index-alert-position-regen-fix-v1` | `1e6367d2863a86c3470da13d81a955d277eba485` | 0/0 |
| OpenDART PR #412 | `bf3d9514a87c53b1775e22ec9ba7711f6cecc49f` | 0/0 |
| 최적화 PR #413 | `f003ef6247e16fcc71bd3b1b20cd4904c4d984c0` | 0/0 |
| 총괄 PR #414 (쓰기 전) | `6ce323d0b995877e352da4108a64a50caef70b94` | 09:44 독립 문서만 1개 추가됨 |
| 단일 실행기 PR #418 | `2f98401cc50a6c6a25808a98516efd5bf0c944ee` | 0/0 |
| KRX 전담 `indexalert-krx-pit-source-audit-20261013` | `073d2d49e95f69fb10b943b93e51bb179fb3c698` | 읽기전용 |
| KRX PR #420 | `fab3cbbd63a951a4e081f9e7f08c1391ca308581` | 0/0 |
| KRX PR #422 | `c14857620973531013799e44625d43080904fd5f` | 0/0 |
| KRX PR #423 | `0e38004363cac9fc4475556b3a1c445de9af407f` | 0/0 |

PR #414 통합 원문 `docs/INDEXALERT_PROFITABILITY_INTEGRATION_GATE_2026-10-13.md` blob SHA-1 `984c933651f39f1ee9e26a1d7ac3893aaa5335be`는 읽기전용 재조회, 변경 없음. 다른 작업자의 09:44 문서 `docs/INDEXALERT_INDEPENDENT_READONLY_PROFIT_GATE_20261028_0944KST.md`도 읽어 중복 원본 수집을 피했다.

## 2. 이번 실행의 독립적 신규 소스 교차검증: PR #418 merge CI의 정확한 drift 경계

- [PR #418 실패 Actions #39111405478](https://github.com/kims34/openpilot-opkr/actions/runs/39111405478), job `117628139395`의 실제 checkout은 **PR head가 아니라** `refs/remotes/pull/418/merge`, 테스트된 merge commit `052cf67e45500baad771527753744289529ecbc2`였다. `SourceDriftError`가 `research_v1_runtime_manifest.py`에서 발생.
- 원본 성공 CI #38382214223 고정 커밋 `05d73661bcc879fe0dd66ffcea5fe1f5ee6fbd56`의 해당 Git **blob SHA-1**은 `108f66714602a1bd3ae42c34dcca7c16e38f460b`. **현재 PR #418 head의 동일 파일도 직접 fetch 시 이 SHA와 일치**.
- **PR #413 head의 동일 파일**은 Git blob SHA-1 `e0055c66c59398fd4a1158077446d886b54c4e37`. 실패한 PR #418 merge CI에서 observed로 보고한 SHA와 정확히 일치. 따라서 현 증거가 설명하는 실패는 *#418 단독 head의 원본 파일 손상*이 아니라 **merge preview의 변경된 캐시 매니페스트와 고정 아카이브 정의 간 불일치**다. merge preview 전체 코드 출처·실행 재현성을 승인하는 의미는 아니다.
- `research_v1_runtime_archived_source_gate.py` 자체도 direct implementation 9개 blob만 pin하고 `all_transitive_imports_pinned=false`를 명시. 성공한 34-case 결과 digest가 변경된 코드·전체 dependency closure·실제 데이터 결과를 인증하지 못한다. 기대 SHA를 사후 재설정해 통과 처리하는 행위는 금지.
- #413 `f003ef...` vs #418 `2f9840...`: compare `diverged`, ahead 49/behind 18, merge base `ca6c5d915d2c0e018f4aa9f82b4488038c16f8d3`. 서로 다른 소스 스냅샷의 테스트 속도/결과를 한 승인된 실행환경으로 합성하지 않는다.

## 3. 실제 Actions 로그·원본 증거와 PASS / FAIL / NOT VERIFIED

| 증거 | 관측 판정 | 인정 범위 및 미승인 사항 |
|---|---|---|
| [OpenDART 2021 원본 #40262558066](https://github.com/kims34/openpilot-opkr/actions/runs/40262558066), job `121379096007` | **PASS** (최초 ZIP SHA-256 `8728c0a3c12761ca19e9c6455bea8f1bed0e4c1ebc2e21dc263c373a82a2b625`) | 13개 후보, 같은 표 Q3/3개월 명시 0; 원본 3개월 CFS 연결 영업이익·최초 공개시각·정정 vintage **NOT VERIFIED** |
| [OpenDART 2022 원본 #38392847048](https://github.com/kims34/openpilot-opkr/actions/runs/38392847048), job `115280695115` | **PASS** (최초 ZIP SHA-256 `56639d8f6ebbecf14cd8bc3179d75d01162e2cd7bbdf8f6a3c9479b44f5084bb`) | 15개 영업손익 후보는 사실값 아님. [원본/정정 #38419439742](https://github.com/kims34/openpilot-opkr/actions/runs/38419439742)의 15/15 시그니처 일치도 CFS 3개월 원본·정정 lineage, PIT 승인 아님 |
| KRX 과거 private 1,565/1,565 평일쌍 | **이전 저장 무결성 PASS**, 이번 직접 private 재조회 없음 | 공식 시장별 달력, 2021 13일/2022 14일 실제 날짜집합, 거래정지·기업행위·historical issuer/security·체결가능성·비용/세금 **NOT VERIFIED** |
| [KRX #39714207925](https://github.com/kims34/openpilot-opkr/actions/runs/39714207925), job `119612335677` | **PASS** (32 synthetic), `DRY_RUN_NO_PRIVATE_STORAGE_READ` | `2022_private_candidate_date_sets_equal=false`는 미승인 차단, 실원본 비교 PASS 아님. [#39721289545](https://github.com/kims34/openpilot-opkr/actions/runs/39721289545)의 164 synthetic tests 역시 원본 승인 아님 |
| [안전 watchdog #40604202566](https://github.com/kims34/openpilot-opkr/actions/runs/40604202566), job `122539521979` | **PASS** (4+31 tests) | `M20 PIT admission: NOT ATTESTED; orders: DISABLED; holdout: NOT AUTHORIZED`; 산출 artifact SHA-256 `aeccdfcdafa0d4c8c3a2934a61e92523db4cfd728bbda6464e39f0a2aa786b7e`는 안전 상태 파일 해시일 뿐 Railway 실설정 증거 아님 |
| [Prospective anchor #40534270813](https://github.com/kims34/openpilot-opkr/actions/runs/40534270813) | **FAIL** | `/anchor/latest` HTTP 404, 검증 job skipped; 정확한 public available-at 증거로 사용할 수 없음 |
| [최적화 PR #413 #38508247773](https://github.com/kims34/openpilot-opkr/actions/runs/38508247773) | **PASS** (6/6 jobs, 34-case digest 동일) | digest SHA-256 `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34`; serial 1.7650s vs parallel 2.7079s, test phase **0.652x**; CI 전체/공식 backtest 가속 **NOT VERIFIED** |
| [PR #418 단일 실행 #39111405562](https://github.com/kims34/openpilot-opkr/actions/runs/39111405562) | **PASS** (독립 offline 34-case parity) | serial 2.3911s vs parallel 2.0755s, test phase **1.1521x**; 다른 실행 경로의 #418 merge source gate #39111405478은 **FAIL-CLOSED**. 실제 backtest/수익성 가속 **NOT VERIFIED** |

## 4. Railway 직접 조회와 권한 경계

Native Railway `list_projects({})`를 읽기전용으로 **실제 1회 시도**했으나 `User input required but current turn is running in a non-interactive mode.`가 반환되었다. 인증 우회·별도 토큰 요청·비공식 대체·재시도 없음. 최신 배포/런타임 로그/운영 `ORDERING` 값은 **NOT DIRECTLY VERIFIED**. 정책상 `ORDERING=false` 유지가 필수이나 현재 실제 값에 대한 증거를 만들어내지 않는다.

## 5. 독립 게이트 결론과 다음 허용 경로

- **PIT/M20 admission: NO-GO.** 최초 제출 2021/2022 3개월 CFS 영업이익 의미·기간·정정 이력 및 intraday 공개시각, issuer/security as-of, 공식 KRX 거래상태·기업행위·체결·비용/세금 모두 독립 승인 영수증이 없음.
- **NetEV, PF, CAGR, MDD, ES95/99, 집중도, 연도/시점별 강건성: NOT EVALUABLE.** 결과가 0이거나 수익성이 없다는 뜻이 아니라 사전등록 M20 평가 실행 자체가 불허됨을 의미.
- **최적화 승인: OFFLINE parity만 PASS, 결합 source gate FAIL, 전체 CI 및 실제 백테스트 가속 NOT VERIFIED.** 이후 독립 원본 승인 영수증·완전한 소스/데이터/코드/런타임 SHA-256·Frozen 정책·비용/세금/체결 증거가 갖춰진 뒤에만 fail-closed 캐시 고려. 읽기전용 후처리만 병렬화, 의존적 재학습/capital transition 병렬화 금지.
- Frozen H5, M20 horizon20/purge20, WF504/126/126, PIT/Purged/CPCV, sealed Holdout, Champion/Top3, Dynamic Challenger-only, NO_TRADE, 비용·세금·승격 기준을 변경하지 않음. 실거래/자금/권한/Champion 승격/병합/배포/새 경제성 RUN 모두 실행하지 않음.
- 다음 허용 단계는 각 전담 원본 Work의 **별도 공식 출처 PIT 증거** 및 KRX 실제 private 날짜집합/체결 증거를 기다리면서, #413/#418의 **동일 SHA checkout 조건에서 오프라인 합성 정책·출처 검사만** 검토하는 것. 기존 archive pin을 임의 갱신하거나 Holdout을 재사용하지 않는다.
