# IndexAlert 독립 수익성·격리 실행환경 감사 — 2026-11-01 05:20 KST

**범위:** GitHub/Railway 읽기전용 실제 재조회 및 기존 합성 CI의 증거 판정. 이 문서는 공식 M20 성과 실행, 새로운 모델/전략 탐색, Holdout 사용, 배포 또는 매매 승인이 아니다. 다른 담당자의 PR #412/#413/#414/#418 및 KRX 격리 브랜치 코드를 변경하지 않았다.

## 1. 고정 HEAD / 변경 중복 회피

- 연구 `index-alert-research-v1`: `3b8b7830612a6284d7c7a60628cb527cb741627a` (branch ref를 GitHub commit API로 재조회).
- 개발 `index-alert-position-regen-fix-v1`: `1e6367d2863a86c3470da13d81a955d277eba485` (동일).
- [Draft #414](https://github.com/kims34/openpilot-opkr/pull/414): HEAD `25c0c2c2097b6907f59b4fa3ef20fd19e3ffa68d`, 2026-11-01 04:42 KST 문서 갱신; 통합 게이트 `docs/INDEXALERT_PROFITABILITY_INTEGRATION_GATE_2026-10-13.md` blob SHA-1 `984c933651f39f1ee9e26a1d7ac3893aaa5335be`. 다른 총괄 작업이 문서를 갱신 중이므로 **수정하지 않음**.
- [Draft #412](https://github.com/kims34/openpilot-opkr/pull/412): `bf3d9514a87c53b1775e22ec9ba7711f6cecc49f`; [#413](https://github.com/kims34/openpilot-opkr/pull/413): `f003ef6247e16fcc71bd3b1b20cd4904c4d984c0`; [#418](https://github.com/kims34/openpilot-opkr/pull/418): `2f98401cc50a6c6a25808a98516efd5bf0c944ee`.
- KRX [Draft #420](https://github.com/kims34/openpilot-opkr/pull/420): `fab3cbbd63a951a4e081f9e7f08c1391ca308581`; [#422](https://github.com/kims34/openpilot-opkr/pull/422): `c14857620973531013799e44625d43080904fd5f`; [#423](https://github.com/kims34/openpilot-opkr/pull/423): `0e38004363cac9fc4475556b3a1c445de9af407f`; 수급 [#416](https://github.com/kims34/openpilot-opkr/pull/416): `053de553646fc4765d2616544ca1e8d6bbdde35f`. 모두 Draft/unmerged. 이외 연구 #424는 독립 ETF 오프라인 작업이므로 변경/실험 중복 없음.

## 2. 독립 수익성 승인 게이트

| 검증 항목 | 현재 판정 | 이번 실행에서 재조회한 근거 및 제한 |
| --- | --- | --- |
| OpenDART 2022 최초/정정 SGML 후보 | **제한적 과거 PASS (source shape only)** | [Actions #38419439742](https://github.com/kims34/openpilot-opkr/actions/runs/38419439742) 실제 jobs 2/2 success. 원본·정정 각각 15개 영업손익 후보, 숫자 인접 시그니처 일치. 최초 2022 ZIP SHA-256 `56639d8f6ebbecf14cd8bc3179d75d01162e2cd7bbdf8f6a3c9479b44f5084bb`은 기존 Actions 증거이며 이번에 원본 ZIP 바이트를 재해시하지 않음. |
| OpenDART 2021 최초 Q3 | **제한적 과거 PASS (source shape only)** | [Actions #40262558066](https://github.com/kims34/openpilot-opkr/actions/runs/40262558066) 2/2 success. 첫 원본 ZIP SHA-256 `8728c0a3c12761ca19e9c6455bea8f1bed0e4c1ebc2e21dc263c373a82a2b625`, 1,728개 표/13 후보/0 엄격 기간 바인딩은 담당 원본 handoff 기록. 원본 바이트의 이번 독립 재해시는 미실시. |
| 2021/2022 최초 연결 3개월 영업이익 기간·정정 lineage·단위·원본 공개시점 | **NOT VERIFIED / FAIL-CLOSED** | 2022 최초 XBRL 공식 014, 2021/2022 standalone July–September CFS 셀/정확한 public available-at/원본 대 정정 vintage 및 기업·종목 과거 매핑 미확정. `rcept_dt`는 날짜일 뿐 장중 최초 공개시각 아님. 15/15 후보 일치는 회계 수치 불변의 증거 아님. |
| KRX 2017–2022 원본 보관 | **과거 제한적 PASS (저장 무결성)** | 1,565/1,565 weekday pair private 저장, 90일 분류 불확실 및 zero-activity 12,003건 외부 차단은 기존 worker 증거. 이번 Railway worker 로그는 0행 반환; 실제 원본 쌍 재해시 미실시. |
| 공식 거래일/거래상태/기업행위/과거 상장·시총/체결가능성 | **NOT VERIFIED / FAIL-CLOSED** | 평일은 공식 개장일이 아니며 90일 불확실, prospective 27/803 OHLC 비정상은 별도 모집단. 27건을 임의 삭제해 승인 금지. |
| 수수료·세금·스프레드·슬리피지·호가·부분체결 원장 | **NOT VERIFIED** | 독립 검증된 거래 가능 일별·종목별 세후 체결원장 없음. |
| M20 NetEV/PF/CAGR/MDD/ES95·99/수익 집중도·시점별 강건성 | **NOT EVALUABLE / NO-GO** | PIT/원본/시장/비용 승인 전 공식 성과 실행 금지. H5/0–N 과거 Holdout 실패·소비 기록을 새 독립 성과로 재활용 금지. |

## 3. 별도 격리 최적화: CI 및 원본 SHA

- [#413 Actions 38381997417](https://github.com/kims34/openpilot-opkr/actions/runs/38381997417), [38382214223](https://github.com/kims34/openpilot-opkr/actions/runs/38382214223), [38419111311](https://github.com/kims34/openpilot-opkr/actions/runs/38419111311): 이번 실행에서 각각 실제 job list **6/6 SUCCESS** 재조회. 과거 고정 34-case SHA-256 `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34`, 13 adversarial mocks는 기존 로그/문서 증거; 원시 test-case bytes의 이번 독립 해시 아님.
- [#418 Actions 38419649711](https://github.com/kims34/openpilot-opkr/actions/runs/38419649711): 실제 **1/1 SUCCESS**; 기존 추가 synthetic 28개, 고정 34-case 일치 및 regression phase serial 2.9656s vs concurrent 2.6209s (1.1315x)는 **전체 CI/실제 공식 백테스트 가속 증거 아님**.
- **현재 #418 FAIL:** [Actions 39111405478](https://github.com/kims34/openpilot-opkr/actions/runs/39111405478) 실제 **1/1 FAILURE**; job 원본 로그 `SourceDriftError`: `research_v1_runtime_manifest.py expected=108f66714602a1bd3ae42c34dcca7c16e38f460b observed=e0055c66c59398fd4a1158077446d886b54c4e37`. 이번에 GitHub blob SHA를 각각 재조회: #413 `e0055c66c59398fd4a1158077446d886b54c4e37`, #418 `108f66714602a1bd3ae42c34dcca7c16e38f460b`. #413은 파일 모드/경로 정체성/교체 재확인을 수행하나 #418 manifest는 그 보호가 축소됨. **보안 동등성 및 #418 채택 FAIL**; 1/1 구 CI 성공을 최종 안전 승인으로 덮어쓰기 금지.
- 캐시는 독립 승인된 원본·데이터·계산코드·Frozen·런타임/승인 증거의 SHA-256 완전 일치만 fail-closed. 독립 읽기전용 후처리만 병렬화; 재학습·capital transition·시점 의존 상태변경 병렬화 금지.

## 4. Railway 운영 실제 재조회

- Project `d1c1a050-b7d6-41ce-b300-13c20f82a20a`, production `83d5840b-270e-4d3f-a941-a37fd4a55ff7`.
- `indexalert-pit-rebuild` deployment `8b354fc1-cfb2-4ef0-863e-67f7f5dda2b5` SUCCESS. **최신 반환** 로그 `2026-10-31T14:46:01.190084194Z` = 23:46:01 KST, `FAIL_CLOSED`, `COMMON_OHLC_NONPOSITIVE`, 27/803 common-stock OHLC nonpositive, source failure session 2026-09-28, `session_manifest_sha256=null`, independent source/model/chronology admission false, `ordering=DISABLED`, live orders/funds/permissions false. 로그가 새로 도착하지 않은 것을 정상 소스 PASS로 해석 금지.
- `indexalert-runtime` deployment `eaaa9f67-b9f2-41d2-832c-7d6fad9b9b00` SUCCESS, 1/1 running; 이번 반환 최신 로그 `2026-10-31T20:20:43.382563279Z` = 2026-11-01 05:20:43 KST. 가격 알림 출력은 원본 PIT/세후 성과 승인 아님.
- `indexalert-kiwoom-real-readonly` deployment `a77fb922-b679-4d88-92c4-03054ec579cd` SUCCESS/online 표시 vs 실제 `running=0, crashed=1, total=1` 불일치. broker authentication 정상 승인 증거 없음.
- **Railway 상태 조회 모순 재확인:** `get_status` 및 `get_staged_changes`는 `staged=null`이지만 `environment_status`는 patch `e113dacb-6705-4416-9997-dc694539d382`를 `staged`/changes 0으로 반환. 이 모순을 운영 반영/승인으로 해석하거나 accept-deploy하지 않음.
- `indexalert-backend`, `indexalert-push`, `db-query-readonly` offline; 이 감사에서 재배포/복구 시도하지 않음.

## 5. 불변 정책 및 다음 독립 게이트

- Frozen H5 유지; M20 `horizon20/purge20`, WF `504/126/126`, PIT/label/Purged/CPCV/독립 Holdout/Champion/Top3/NO_TRADE, 기존 세금·비용·위험·승격 기준 **변경 금지**.
- **다음 필요 증거:** (1) 원본 2021/2022 최초 CFS 3개월 수치/period/scale 및 정정 계보의 바이트 SHA와 public available-at/과거 corp-security mapping을 원본 담당이 독립 입증; (2) KRX 담당이 공식 세션/기업행위/상장·정지·체결가능성/거래비용·세금의 시점별 원장 승인; (3) #418 전담이 manifest 및 파일 교체 fail-closed 동등성을 격리 synthetic CI로 복원; (4) 모든 독립 원본 SHA가 일치할 때만 Frozen M20 본 평가 여부를 별도 승인 판단.
- 이 실행은 **합성 오프라인 기존 CI 읽기 및 정책 안전검증만** 했다. 새로운 시장 수익률/성능실험/모델 탐색/M20 경제성 RUN 없음. PR #413/#414/#418 병합·운영 배포·자동 병합 없음. `ORDERING=false`/실매매·자금·인증·계좌권한·Champion 승격 미승인. GitHub workflow 파일 수정 또는 과거 보안 차단 우회 없음.
