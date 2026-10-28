# IndexAlert 독립 수익성·최적화 감사 — 2026-10-28 09:21 KST

> **읽기전용 원본·CI 재조회 + 격리 문서 기록만 수행.** 이 문서는 데이터/전략/운영/주문/승격 승인서가 아니다. 최초 원본에 대한 저장 무결성과 경제적 PIT 승인·거래가능성을 엄격히 구별한다. 사용자 비밀, 공시 원문, 계좌 정보, 종목별 값은 기록하지 않는다.

## 정확한 원본 HEAD (2026-10-28 09:21 KST 조회)
| 대상 | 상태 | HEAD |
|---|---|---|
| 연구 `index-alert-research-v1` | read-only | `3b8b7830612a6284d7c7a60628cb527cb741627a` |
| 개발 `index-alert-position-regen-fix-v1` | read-only | `1e6367d2863a86c3470da13d81a955d277eba485` |
| 총괄 Draft PR #414 | OPEN/DRAFT, 변경 금지 | `3b037756f316de93d5a8206ca3fae24ad0c107de` |
| 최적화 Draft PR #413 | OPEN/DRAFT, 변경 금지 | `f003ef6247e16fcc71bd3b1b20cd4904c4d984c0` |
| 단일 실행기 Draft PR #418 | OPEN/DRAFT, 변경 금지 | `2f98401cc50a6c6a25808a98516efd5bf0c944ee` |
| OpenDART Draft PR #412 | OPEN/DRAFT | `bf3d9514a87c53b1775e22ec9ba7711f6cecc49f` |
| KRX Draft PR #420 | OPEN/DRAFT | `fab3cbbd63a951a4e081f9e7f08c1391ca308581` |
| KRX Draft PR #422 | OPEN/DRAFT | `c14857620973531013799e44625d43080904fd5f` |
| KRX Draft PR #423 | OPEN/DRAFT | `0e38004363cac9fc4475556b3a1c445de9af407f` |

PR #414 통합 게이트 원본 `docs/INDEXALERT_PROFITABILITY_INTEGRATION_GATE_2026-10-13.md` blob SHA `984c933651f39f1ee9e26a1d7ac3893aaa5335be`; 해당 파일은 읽기만 했으며 수정하지 않았다.

## 09:21 독립 신규 세부 검증: #418 현재 HEAD의 3개 CI는 전부 PASS가 아님

- **[Actions #39111405478](https://github.com/kims34/openpilot-opkr/actions/runs/39111405478) — FAIL, fail-closed 정상 작동.** job `117628139395`의 `research_v1_runtime_archived_source_gate.py`에서 `SourceDriftError`: `research_v1_runtime_manifest.py` archived blob **expected** `108f66714602a1bd3ae42c34dcca7c16e38f460b`, **observed** `e0055c66c59398fd4a1158077446d886b54c4e37`. 이 값들은 Git blob SHA-1 형식의 **소스 식별자**이지 SHA-256 결과 digest가 아니다. 원본 고정 코드 불일치로 후속 34-case 병렬 검증 job steps가 **SKIPPED**되었으므로 이 CI를 '34개 회귀 PASS'로 계산하지 않는다. 코드 변경으로 우회하지 말 것.
- **[Actions #39111405562](https://github.com/kims34/openpilot-opkr/actions/runs/39111405562) — PASS, 제한된 별도 offline one-runner 경로.** job `117628139856`의 pinned 34-case digest SHA-256 `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34` 및 outcomes identical=true. serial subprocess 2.3911초 / parallel 2.0755초 = **1.1521x** (테스트 프로세스 구간만). 전체 CI, 실데이터 백테스트, 수익성 가속은 NOT VERIFIED.
- **[Actions #39111405494](https://github.com/kims34/openpilot-opkr/actions/runs/39111405494) — PASS, 비승인 후보 merge source audit.** job `117628139749`에서 22 code files, reviewed 4 code blobs, 8+8 original blobs 확인. 그러나 `all_transitive_imports_pinned=false`, `original_archived_manifest_replayed_without_change=false`, `candidate_approved_for_merge=false`. 22개 distribution 버전은 일치하지만 `exact_wheel_hashes_verified=false`, `os_native_dependency_identity_verified=false`. PASS는 구조적 진단의 성공일 뿐 병합 승인 아님.
- PR #413 현재 HEAD의 [Actions #38508247773](https://github.com/kims34/openpilot-opkr/actions/runs/38508247773) 6/6 jobs PASS, 34-case digest 일치. job `115670744341`의 serial 1.7650초, parallel longest 2.7079초 = **0.652x** (느려짐); 실제 전체 CI·백테스트 speedup NOT VERIFIED.
- PR #413 `f003ef...` 대 PR #418 `2f9840...` 비교: **diverged, ahead 49 / behind 18**, merge base `ca6c5d915d2c0e018f4aa9f82b4488038c16f8d3`. HEAD 간 통합 안전성 NOT VERIFIED. 원본 hash drift를 사후에 기준선 재설정하여 통과 처리하면 안 된다.

## 공식 데이터·PIT 증거와 제한

- **2021 OpenDART 최초 Q3**: [Actions #40262558066](https://github.com/kims34/openpilot-opkr/actions/runs/40262558066), official job `121379096007` 성공. 최초 ZIP SHA-256 `8728c0a3c12761ca19e9c6455bea8f1bed0e4c1ebc2e21dc263c373a82a2b625`의 CI 체크 **PASS**. SGML 1, table shapes 1728, operating-label candidate tables 13. **2021 Q3 기간이 같은 표에서 확인된 후보 0, '3개월' 문구 같은 표 확인 후보 0**. 숫자 의미·연결 3개월 CFS 사실값, 2022 최초 비교 열, 최초 공개시각, 전 정정 lineage, 과거 issuer/security mapping은 NOT VERIFIED. [Actions #40263193758](https://github.com/kims34/openpilot-opkr/actions/runs/40263193758)은 viewer TOC 13개 synthetic/offline tests PASS일 뿐 공식 수치 승인 아님.
- **2022 OpenDART 최초/정정**: 기존 [Actions #38419439742](https://github.com/kims34/openpilot-opkr/actions/runs/38419439742) 2 jobs PASS, 후보행 15개/숫자 인접 시그니처 일치. 최초 ZIP SHA-256 `56639d8f6ebbecf14cd8bc3179d75d01162e2cd7bbdf8f6a3c9479b44f5084bb`, 정정 ZIP SHA-256 `606be9d03928808f0a2a05f052444587bd2457bdef7a47a8f4bff3d2ea098a30`. ZIP 바이트 및 후보형태의 사실만 입증, 2022/2021 최초 연결 3개월 영업이익·public available-at/PIT는 NOT VERIFIED.
- **KRX**: 과거 private weekday pairs 1565/1565 SHA 저장 무결성 PASS(이전 전담 원본 증거), 시장 달력/거래상태/기업행위/체결가능성·수수료/세금은 NOT VERIFIED. [Actions #39714207925](https://github.com/kims34/openpilot-opkr/actions/runs/39714207925), job `119612335677`: 32/32 synthetic tests PASS, `DRY_RUN_NO_PRIVATE_STORAGE_READ`, `2022_private_candidate_date_sets_equal=false` (실제 private 비교가 없다는 차단 플래그). KIND 코스닥/파생 공시를 코스피 원본으로 교차 인증하지 않는 테스트가 포함됨. 2021 13일/2022 14일 private 실제 날짜집합과 공식 시장별 원본 대조는 NOT VERIFIED. zero-activity 12003건 등 veto 유지.
- **최근 안전 감시**: [Actions #40604202566](https://github.com/kims34/openpilot-opkr/actions/runs/40604202566), 2026-10-28 08:44 KST 시작, job `122539521979` SUCCESS. watchdog 4 tests + research governance 31 tests PASS; 로그 `IndexAlert read-only evidence metadata: COMPLETE`, `M20 PIT admission: NOT ATTESTED; orders: DISABLED; holdout: NOT AUTHORIZED`. **metadata COMPLETE != PIT admission**. 증거 flags-only artifact SHA-256 `aeccdfcdafa0d4c8c3a2934a61e92523db4cfd728bbda6464e39f0a2aa786b7e` (업로드 ZIP의 digest).
- **Prospective anchor**: [Actions #40534270813](https://github.com/kims34/openpilot-opkr/actions/runs/40534270813), job `122295113858` FAILED: `/anchor/latest` HTTP 404, validation SKIPPED. 공개시각 PIT anchor 승인 불가.
- **Railway 최신 배포/로그**: 실제 read-only `list_projects` 호출을 시도했지만 **User input required but current turn is running in a non-interactive mode**로 차단. 따라서 2026-10-28 최신 운영 배포·실제 ORDERING 설정·비공개 KRX 파일에 대한 새로운 판정은 **NOT VERIFIED**. 과거 저장 로그를 현재 운영 상태로 대체하지 않는다. 연결 승인이 가능한 사용자 세션에서 Railway 연결 승인을 완료해야 직접 재검증 가능. 자격증명/계좌권한 변경을 시도하지 않았다.

## 종합 게이트

| 항목 | 판정 |
|---|---|
| CI로 검증된 2021/2022 OpenDART 최초 ZIP byte checksum | **PASS (원본 파일 무결성 범위 한정)** |
| 정확한 2021/2022 최초 3개월 연결 영업이익, 공표시각, 정정 lineage, historical mapping | **NOT VERIFIED** |
| KRX private 원본 저장 무결성 | **PASS (저장 범위 한정)** |
| KRX 과거 시장별 휴장·종목상태·기업행위·실체결·비용·세금 | **NOT VERIFIED** |
| PR #413 고정 34-case 동등성 | **PASS (offline-only)** |
| PR #418 current HEAD pinned-parallel archived source gate | **FAIL (expected != observed Git blob; fail-closed)** |
| PR #418 별도 one-runner 34-case parity | **PASS (offline-only; 통합 불승인)** |
| PR #418 전체 의존성/후보 병합/실백테스트 속도 | **NOT VERIFIED / NO-GO** |
| M20 PIT / 수익성 실행 | **NO-GO** |
| NetEV, PF, CAGR, MDD, ES95/99, 집중도·연도별 강건성 | **NOT EVALUABLE (공식 경제성 RUN 미승인)** |
| Holdout 재사용, Champion 승격, Tiny Live, 실주문/자금 이동 | **NOT AUTHORIZED** |

## 다음 허용 단계와 불변 안전 정책

1. **OpenDART 전담**: 최초 원본 표의 정확한 3개월 연결 기간·회계 항목·수치 및 최초 공표시각/정정 계보를 원본 SHA와 독립 증거로 결합. 후보 13/15개나 TOC synthetic PASS를 수치 PASS로 승격 금지.
2. **KRX 전담**: market/venue별 공식 당시 공시와 private 원본 날짜집합을 정확히 비교한 별도 read-only SHA 영수증; 기업행위·거래정지·상장폐지·실체결·비용/세금 검증. 날짜 수만 같은 것은 불충분.
3. **최적화 전담**: PR #418 archived source drift (`research_v1_runtime_manifest.py`)의 원인과 22 distribution exact wheel/native identity를 독립적으로 설명/승인받을 때까지 병합 불가. 안전검사 차단 workflow 변경 우회 금지. 새 수익률/성능 실험 금지. 단일 runner의 read-only 후처리만 후보로 유지.
4. **총괄**: 독립 원본/PIT/시장/비용/체결 승인이 모두 PASS가 되기 전에는 M20 경제성, Frozen H5 Holdout, Dynamic 재최적화 실행 금지. Frozen H5, M20 horizon20/purge20, WF504/126/126, Champion/Top3/NO_TRADE, 비용·세금·NetEV/위험/승격 기준 고정. `ORDERING=false` 정책 유지. 운영 실제 값은 Railway 연결 승인 전 미확인. PR #413/#414/#418 병합·배포·주문·자금이동·Champion 승격 금지.

이번 작업에서 전담 코드, workflow, 기존 총괄 문서, 원본 자료, 배포, 실거래, 계좌 설정은 변경하지 않았다.
