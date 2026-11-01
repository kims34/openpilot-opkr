# IndexAlert 독립 수익성·격리 최적화 감사 — 2026-11-01 09:19 KST

**판정: M20 경제성 NOT EVALUABLE / NO-GO, ORDERING=DISABLED.** 이 회차는 GitHub 브랜치·Draft PR·Actions 원본 job 로그와 Railway production의 실제 배포/상태/로그를 읽기전용 재조회했다. 수익률 계산·Holdout 접근·재학습·모델 탐색·주문·권한/자금 변경·병합·배포·workflow/실행코드 수정 없음. 다른 전담의 PR #414 08:47 독립 source-gate 문서와 중복 편집하지 않고, 이 독립 감사 브랜치의 새 문서에만 증거를 보존한다. 이전 [08:26 독립 감사](https://github.com/kims34/openpilot-opkr/blob/a673d9f123d479607df28e373634b46df72bacd7/docs/INDEXALERT_INDEPENDENT_PROFIT_RUNTIME_AUDIT_20261101_0826KST.md) 대비 확인.

## 1. 고정 원본 HEAD / 작업 격리

- 연구 `index-alert-research-v1` HEAD `3b8b7830612a6284d7c7a60628cb527cb741627a`; 개발 `index-alert-position-regen-fix-v1` HEAD `1e6367d2863a86c3470da13d81a955d277eba485`; KRX 소스 전담 `indexalert-krx-pit-source-audit-20261013` HEAD `073d2d49e95f69fb10b943b93e51bb179fb3c698` (GitHub branch API).
- [OpenDART #412](https://github.com/kims34/openpilot-opkr/pull/412) `bf3d9514a87c53b1775e22ec9ba7711f6cecc49f`; [최적화 #413](https://github.com/kims34/openpilot-opkr/pull/413) `f003ef6247e16fcc71bd3b1b20cd4904c4d984c0`; [총괄 #414](https://github.com/kims34/openpilot-opkr/pull/414) **새 문서 HEAD** `7339fa46859b3cf9cf1e96007ffd204606a01f2c` (2026-10-31 23:48 UTC update; 새 파일 `docs/INDEXALERT_PROFITABILITY_INDEPENDENT_GATE_20261101_0847KST_AUTOMATION11.md`); [단일 실행기 #418](https://github.com/kims34/openpilot-opkr/pull/418) `2f98401cc50a6c6a25808a98516efd5bf0c944ee`. #416 `053de553646fc4765d2616544ca1e8d6bbdde35f`, KRX #420 `fab3cbbd63a951a4e081f9e7f08c1391ca308581`, #422 `c14857620973531013799e44625d43080904fd5f`, #423 `0e38004363cac9fc4475556b3a1c445de9af407f`, ETF #424 `a4ae98f40b3e6dcaf565cc402679497e42cdabb5`. 모두 Draft/open/unmerged.
- PR #414 최신 변경은 별도 Work의 **독립 증거 문서 1개**. 해당 파일과 소유 브랜치를 수정하지 않았다.

## 2. 공식 원본/PIT/시장 경제성 — 엄격한 판정

| 범위 | 판정 | 이 회차 직접 조회 증거와 미해결 경계 |
| --- | --- | --- |
| 2021 최초 OpenDART 원본 소스 식별 | **LIMITED PASS** | [official Action #40262282075](https://github.com/kims34/openpilot-opkr/actions/runs/40262282075) 2/2 jobs SUCCESS; [담당 문서](https://github.com/kims34/openpilot-opkr/blob/bf3d9514a87c53b1775e22ec9ba7711f6cecc49f/INDEXALERT_M20_2021_FIRST_ORIGINAL_Q3_SOURCE_HANDOFF_20261026.md) ZIP SHA-256 `8728c0a3c12761ca19e9c6455bea8f1bed0e4c1ebc2e21dc263c373a82a2b625`, 1,728 table shapes, 13 operating-label candidates, strict same-table 2021 Q3 three-month binding 0. **이번 감사에서 원본 ZIP 바이트 독립 재해시 없음**. |
| 2022 최초·정정 원본/공시 계보 | **SOURCE-ONLY LIMITED PASS** | [Action #38419439742](https://github.com/kims34/openpilot-opkr/actions/runs/38419439742) 2/2 jobs SUCCESS; 최초 ZIP SHA-256 `56639d8f6ebbecf14cd8bc3179d75d01162e2cd7bbdf8f6a3c9479b44f5084bb` 및 원본·정정 SGML 후보 15개/인접 숫자 시그니처 일치. [#39721626218](https://github.com/kims34/openpilot-opkr/actions/runs/39721626218) official complete edition-index job SUCCESS, 그러나 색인 범위 한정이고 실제 원본 CFS 사실값이나 최초 public time을 입증하지 않음. |
| 2021/2022 최초 standalone 3-month **CFS** operating profit, 정확한 public available-at, correction PIT lineage, historical issuer/security map | **NOT VERIFIED / FAIL CLOSED** | 단순 SGML 후보 행·서류 ZIP SHA·current normalized API·2021 별도 최초공시는 2022 원본의 2021 비교열과 동일하다는 증거가 아님. 원본과 정정 금액/기간/연결 문맥/단위/부호/공개시각을 별도 독립 승인할 것. 정정본 역채우기 금지. |
| KRX 2017–2022 private 원본쌍 | **HISTORICAL STORAGE LIMITED PASS** | Railway KRX worker live deployment `16c93d7c-7cd0-4d84-a327-298d2805376c`, source commit `1e6367d2863a86c3470da13d81a955d277eba485`; 과거 로그상 1,565/1,565 weekday pair SHA integrity, invalid stored pair 0. 이번 조회에서는 worker 신규 로그가 없어 독립 재해시 아님. |
| 공식 KRX 달력·거래정지·기업행위·체결/비용/세금 | **NOT VERIFIED** | 90 source-empty/휴장 미분류, zero-activity 12,003 및 27 OHLC veto. [#420](https://github.com/kims34/openpilot-opkr/pull/420)/[#422](https://github.com/kims34/openpilot-opkr/pull/422)/[#423](https://github.com/kims34/openpilot-opkr/pull/423) offline holiday comparator는 날짜 개수 또는 후보집합 증거이지 공식 PIT 거래가능성 승인 아님. |
| H5/Dynamic/독립 Holdout, M20 horizon20/purge20 WF504/126/126 | **NO-GO / NOT EVALUABLE** | H5 실패/소비 Holdout 및 Dynamic 사후 조정·독립 재사용 금지. 비용·세금·NetEV/PF/CAGR/MDD/ES95/99/수익 집중도·연도/시점별 강건성은 미실행이므로 독립 실측 PASS 불가. [최신 watchdog #41248232339](https://github.com/kims34/openpilot-opkr/actions/runs/41248232339), job `124676072097` SUCCESS지만 원본 로그 `M20 PIT admission: NOT ATTESTED; orders: DISABLED; holdout: NOT AUTHORIZED`. |

## 3. 격리 백테스트 최적화 — 채택 조건과 실제 CI

- [#413 Actions #38381997417](https://github.com/kims34/openpilot-opkr/actions/runs/38381997417), [#38382214223](https://github.com/kims34/openpilot-opkr/actions/runs/38382214223), [#38419111311](https://github.com/kims34/openpilot-opkr/actions/runs/38419111311), [HEAD-associated #38508247773](https://github.com/kims34/openpilot-opkr/actions/runs/38508247773): 각 **6/6 jobs SUCCESS**. 최신 parity job `115670744341` 원본 로그에서 34-case SHA-256 `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34` 재확인. 이는 **합성/기존 오프라인 회귀 동등성 LIMITED PASS**이지 공식 백테스트 경제성/전체 CI 가속 PASS 아님.
- [#418 초기 #38419649711](https://github.com/kims34/openpilot-opkr/actions/runs/38419649711) 1/1 SUCCESS, 기존 고정 34-case digest 일치; 초기 regression-phase serial 2.9656초 vs concurrent 2.6209초 = 1.1315x는 전체 CI/실제 M20 성능이 아님. 최신 HEAD-associated [#39111405478](https://github.com/kims34/openpilot-opkr/actions/runs/39111405478) job `117628139395` **FAIL**, 원본 로그 `SourceDriftError`: archived `research_v1_runtime_manifest.py` expected blob SHA-1 `108f66714602a1bd3ae42c34dcca7c16e38f460b`, observed `e0055c66c59398fd4a1158077446d886b54c4e37`. #39111405494/#39111405562 각각 1/1 SUCCESS이나 후보 전체 코드 의존성 승인이 아님.
- **실제 HEAD 소스 재조회**: #413 manifest blob SHA-1 `e0055c66c59398fd4a1158077446d886b54c4e37`는 명시적 elevated-permission flags 부정, 경로 요소 O_NOFOLLOW/identity recheck를 포함. #418 manifest blob `108f66714602a1bd3ae42c34dcca7c16e38f460b`는 이 보호를 동일하게 갖추지 않음. 따라서 #418 채택/병합 **FAIL**, 캐시 승격 **NO-GO**. 원본 source/data/code/Frozen/runtime/independent admission evidence SHA-256 전체 동일·원자성·권한 fail-closed가 승인된 후에만 재평가.
- 읽기전용 독립 후처리만 병렬 가능. 재학습·capital transition은 순차 유지. Frozen H5, M20, Top3/NO_TRADE, 비용/세금·위험/승격 규칙 변경 없음. 신규 synthetic 테스트도 다른 담당 영역과 중복 실행하지 않았다.

## 4. Railway production 관측 및 운영 경계

- Project `d1c1a050-b7d6-41ce-b300-13c20f82a20a`, environment `83d5840b-270e-4d3f-a941-a37fd4a55ff7`. Latest deployments API상 최신 2026-10-29 06:21 UTC Kiwoom read-only `a77fb922-b679-4d88-92c4-03054ec579cd` (deployed commit `85bb6fd10bcc9ff2b14abe1c774f0d99f8eb84ab`), KRX worker 2026-10-12, PIT 2026-10-10, alert runtime 2026-10-05. 이 회차 신규 배포 없음.
- PIT service `8b354fc1-cfb2-4ef0-863e-67f7f5dda2b5`: 최신 **반환된** 로그 `2026-10-31T14:46:01.190084194Z` = 23:46:01 KST; `FAIL_CLOSED`, `COMMON_OHLC_NONPOSITIVE`, 27/803, `independent_source_admission_verified=false`, chronology/model false, `session_manifest_sha256=null`, `ordering=DISABLED`, orders/funds/permissions false. 새 로그가 안 보인다고 이후 이벤트 부재를 증명하지는 않음.
- Alert runtime `eaaa9f67-b9f2-41d2-832c-7d6fad9b9b00` 1 running / 0 crashed, 최신 반환 로그 `2026-11-01T00:19:43.190671744Z` (09:19:43 KST). 이는 **알림 데이터**이고 M20 원본/PIT/경제성 증거가 아님.
- Kiwoom real read-only는 deployment SUCCESS 표시와 **0 running / 1 crashed**가 모순; 계좌/인증/주문 접근 시도 없음. Railway `describe_environment` 및 `get_staged_changes`는 staged=null이나 `environment_status`는 patch `e113dacb-6705-4416-9997-dc694539d382` (zero changes)를 pending으로 반환. 불일치 **NOT VERIFIED**이며 accept/deploy 금지.
- `indexalert-push`, `indexalert-backend`, `db-query-readonly`는 health API offline 및 warning/critical로 반환되지만, 이는 이 M20 수익성 판정의 PIT 통과 증거가 아니며 이번 격리 감사 범위에서 임의 재시작/배포하지 않음.

## 5. 다음 단일 중요 경로

OpenDART 소스 담당: 최초 2022 및 비교 2021 standalone 3-month CFS 영업이익 원본 문맥/값·공표시점·정정 lineage·issuer/security PIT를 독립 원본 SHA로 PASS 증명. KRX 담당: 90 공백의 공식 as-of 달력/거래상태, 종목별 거래정지/기업행위·실제 체결가능성·비용/세금 및 27 invalid OHLC의 안전 차단 입증. 최적화 담당: #418 manifest provenance/fail-closed 문제를 자기 격리 영역에서 해소하고 전체 CI/정확한 의존성 SHA 및 실제 허용된 workload에서만 속도 평가. 총괄: 위 source/market gates 승인 전 **M20 수익률/경제성 RUN 금지**; 세후 NetEV/PF/CAGR/MDD/ES95/99·수익 집중도·시점 강건성 모두 NOT EVALUABLE.

**안전 불변식:** `ORDERING=false`, `KIWOOM_ORDERING_ENABLED=false`; NO_TRADE; 실주문·자금 이동·인증/계좌권한 변경·Champion 승격은 매번 별도 명시 승인. PR #413/#414/#418 병합, 운영 배포, workflow 변경 금지. 별도 Work 소유 코드 불변.
