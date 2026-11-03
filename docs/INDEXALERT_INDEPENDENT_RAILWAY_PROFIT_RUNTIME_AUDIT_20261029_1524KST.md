# IndexAlert 독립 수익성·격리 실행환경 감사 — 2026-10-29 15:24 KST

> 범위: GitHub PR/Actions 원본 및 Railway **읽기전용** 프로젝트·서비스·배포·설정 이름·운영 로그 확인. 공식 데이터·모델·실거래·권한·환경변수·코드·워크플로 변경 없음. 이전 Railway 연결 차단 기록은 **당시 상태**이며, 본 회차에서는 직접 조회에 성공했다. 성공한 읽기전용 접근은 새로운 승인 권한이 아니다.

## 정확한 기준선 및 협업 경계

- 연구 기준 `index-alert-research-v1` / PR #414 base SHA `3b8b7830612a6284d7c7a60628cb527cb741627a`. 개발 기준 `index-alert-position-regen-fix-v1` / Railway KRX worker SHA `1e6367d2863a86c3470da13d81a955d277eba485`.
- PR head (조회 시): #412 `bf3d9514a87c53b1775e22ec9ba7711f6cecc49f`, #413 `f003ef6247e16fcc71bd3b1b20cd4904c4d984c0`, #414 기록 전 `605f1d3ce1d7011b36ee05dcc697c34a2daeca15`, #416 `053de553646fc4765d2616544ca1e8d6bbdde35f`, #418 `2f98401cc50a6c6a25808a98516efd5bf0c944ee`, KRX #420 `fab3cbbd63a951a4e081f9e7f08c1391ca308581`, #422 `c14857620973531013799e44625d43080904fd5f`, #423 `0e38004363cac9fc4475556b3a1c445de9af407f`. 전부 Draft/open/unmerged.
- 총괄 기존 게이트 `docs/INDEXALERT_PROFITABILITY_INTEGRATION_GATE_2026-10-13.md` blob SHA-1 `984c933651f39f1ee9e26a1d7ac3893aaa5335be`. 직전 격리 manifest 분석 문서 `docs/INDEXALERT_INDEPENDENT_RUNTIME_MERGE_CONTEXT_SHA_AUDIT_20261029_1419KST.md` blob SHA-1 `55d0cd5badf59a5cb3a9f6640d4b0c1b48bffffc`. 다른 Work 코드/문서 및 테스트 변경 회피.

## 이번 회차의 신규 독립 증거 — Railway 실운영 읽기전용 접근 성공

- Railway `IndexAlert` 프로젝트 ID `d1c1a050-b7d6-41ce-b300-13c20f82a20a`, production 환경 ID `83d5840b-270e-4d3f-a941-a37fd4a55ff7`에 대해 `list_projects`, `list_services`, `describe_environment`, `describe_service`, `list_deployments`, `get_logs`, `environment_status`, `list_variables` **조회만 성공**. staged patch 없음. `list_variables`는 OAuth 응답 `valuesRedacted=true`: 실제 환경변수 **값은 확인 불가**; 이름만 조회. 비밀값 수집/출력/수정 없음.
- **신규 운영 배포:** `indexalert-kiwoom-real-readonly` 최신 deployment `a77fb922-b679-4d88-92c4-03054ec579cd`, 2026-10-29 06:21:36 UTC = 15:21:36 KST, `SUCCESS`; 소스 `index-alert-position-regen-fix-v1`, 배포 snapshot commit `85bb6fd10bcc9ff2b14abe1c774f0d99f8eb84ab`, start `python -B smoke.py`, restart `NEVER`, `KIWOOM_ORDERING_ENABLED` **변수명 존재**, 값 **REDACTED / NOT VERIFIED**. build/runtime 로그에서 주문 실행이나 거래 권한 승인 증거 없음. 이 배포 성공은 주문 비활성 상태의 완전한 증명이 아님. 운영 배포를 이번 감사에서 유발하지 않았다.
- **Prospective PIT 서비스:** `indexalert-pit-rebuild` 최신 deployment `8b354fc1-cfb2-4ef0-863e-67f7f5dda2b5` (2026-10-10 10:28:46 UTC) `SUCCESS`, 소스 `e57054ecdb3e734ced3c9a981b887d9b5fc60f97`. 2026-10-28 09:30:13~14:46:43 UTC 운영 `INDEXALERT_PROSPECTIVE_RUNTIME` 구조화 로그 22건의 오류 유형은 모두 `COMMON_OHLC_NONPOSITIVE`. **마지막 실제 운영 로그** `2026-10-28T14:46:43.515172457Z`: `ordering="DISABLED"`, `live_order_authorized=false`, `real_orders_authorized=false`, `independent_source_admission_verified=false`, `independent_model_admission_verified=false`, `independent_chronology_admission_verified=false`, `fresh_alpha_observation_admitted=false`, `funds_movement_authorized=false`. 이 **서비스·로그 시점 한정 실제 상태**는 PASS(주문 거부/미승인)이며, 전체 서비스·현재 시각의 모든 환경변수 값 확인을 의미하지 않는다.
- **KRX historical worker:** latest deployment `16c93d7c-7cd0-4d84-a327-298d2805376c`, 2026-10-12 13:07:31 UTC, `SUCCESS`, commit `1e6367d2863a86c3470da13d81a955d277eba485`, `/data` 볼륨 연결, start `python -B research_v1_krx_openapi_missing_2017_2022_integrity_audit.py --audit`. 이 회차 기간의 새 worker 로그 없음. 과거 원본 1,565/1,565 쌍 무결성 PASS는 공식 90일 캘린더/종목별 거래가능성 PASS가 아님.
- `indexalert-runtime` deployment `eaaa9f67-b9f2-41d2-832c-7d6fad9b9b00`, commit `8a68b01bca5d551d083ccda263df38d86fa54166`, `SUCCESS`, `KIWOOM_ORDERING_ENABLED` 변수명 존재하나 값은 redacted. 일반 지수 시세 로그는 M20 수익성/공식 PIT 증거가 아님.
- Railway health: 10 services, 3 with issues (`indexalert-push`, `indexalert-backend`, `db-query-readonly` offline); 이번 8시간 집계 failed/crashed deployments 0. 이들은 기존 비핵심/오래된 상태일 수 있으므로 M20 원본 PIT 또는 거래 승인 근거로 사용하지 않는다.

## GitHub Actions·최적화 독립 대조

- [Watchdog #40806178512](https://github.com/kims34/openpilot-opkr/actions/runs/40806178512) job `123225555499` SUCCESS, 로그 `M20 PIT admission: NOT ATTESTED; orders: DISABLED; holdout: NOT AUTHORIZED`; 상태 artifact ZIP SHA-256 `6f4d29f3db3475b497dbcd87c027f48a540e96c853e5e0f0131a5726001c821a`. 이는 시장 원본이 아닌 안전 상태 증거.
- [PR #413 CI #38508247773](https://github.com/kims34/openpilot-opkr/actions/runs/38508247773) 6/6 jobs SUCCESS; 34-case 고정 결과 SHA-256 `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34` parity PASS. 전체 CI·공식 백테스트 가속 NOT VERIFIED.
- [PR #418 CI #39111405562](https://github.com/kims34/openpilot-opkr/actions/runs/39111405562) one-runner 1/1 SUCCESS, 제한된 34-case 회귀 구간 직렬 2.3911s vs 병렬 2.0755s = 1.1521x. 그러나 [#39111405478](https://github.com/kims34/openpilot-opkr/actions/runs/39111405478) job `117628139395` **실제 FAIL**: `research_v1_runtime_manifest.py` archived expected Git blob `108f66714602a1bd3ae42c34dcca7c16e38f460b`, merge-context observed `e0055c66c59398fd4a1158077446d886b54c4e37`. 단순 repin/워크플로 우회 금지, 캐시 **FAIL-CLOSED**. Wheel/native/transitive/runtime/authorization closure NOT VERIFIED.

## 원본 데이터·경제성 게이트 (증거 범위 구분)

| 대상 | 판정 |
| --- | --- |
| OpenDART 2021/2022 original ZIP 보존 및 후보 shape | 기존 SHA 근거에 한해 PASS |
| 2021/2022 최초 연결 3개월 영업이익 기간·단위·정정 lineage, 최초 public available-at/PIT | NOT VERIFIED |
| 기업·종목 역사 매핑, 공식 KRX 거래일·종목상태·기업행위·체결가능성·수수료·세금·슬리피지 | NOT VERIFIED |
| KRX 2017–2022 1,565/1,565 private weekday 원본쌍 저장 무결성 | 기존 독립 기록 범위 PASS, 시장 PIT는 NO-GO |
| 최적화 합성 오프라인 parity | PASS (정해진 34-case 범위) |
| PR #418 archived manifest SHA closure / 승인 캐시 | FAIL / FAIL-CLOSED |
| M20 수익성 RUN, 세후 NetEV/PF/CAGR/MDD/ES95·99/집중도·시점별 강건성 | NO-GO / NOT EVALUABLE |
| 전체 주문 환경변수 값 및 모든 서비스의 최신 실제 주문 상태 | NOT VERIFIED (OAuth 값 redacted, 단 PIT 로그 한정 DISABLED 확인) |

## 변경 불가·다음 게이트

- H5 소비 Holdout 재사용·Dynamic 사후 최적화 금지, M20 horizon20/purge20, WF504/126/126, PIT/Purged/CPCV/Champion/Top3/NO_TRADE, 비용·세금·위험·승격 기준 불변. `ORDERING=false` 정책 유지. 주문·자금·권한·Champion 승격·운영 배포·PR #413/#414/#418 병합 금지.
- OpenDART 소유자가 최초 2021/2022 3개월 CFS/정정/available-at 입증 → KRX 소유자가 공식 역사 거래상태·기업행위·체결/비용 입증 → 최적화 소유자가 PR #418 head/base/merge manifest 및 wheel/native/transitive/runtime/승인 SHA closure 재현 PASS → **별도 승인 후** 단일 Frozen M20 평가. 어떤 운영 배포 성공이나 오프라인 CI도 이 순서를 단축하지 않는다.
