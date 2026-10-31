# IndexAlert 독립 수익성·격리 최적화 증거 감사 — 2026-10-30 22:21 KST

> **읽기전용 근거 재검증 / 별도 감사 문서만 추가.** 아래 CI·원본 SHA·운영 상태는 서로 다른 검증 범위이다. 이 문서는 데이터 PIT, M20 경제성, 실거래, 캐시, Champion 승격의 승인이 아니다. 계좌·원본 시장데이터·기업 식별값·인증정보를 기록하지 않는다.

## 1. 실제 소유권 경계와 HEAD

- GitHub [연구 `index-alert-research-v1`](https://github.com/kims34/openpilot-opkr/commit/3b8b7830612a6284d7c7a60628cb527cb741627a) HEAD `3b8b7830612a6284d7c7a60628cb527cb741627a`; [개발 `index-alert-position-regen-fix-v1`](https://github.com/kims34/openpilot-opkr/commit/1e6367d2863a86c3470da13d81a955d277eba485) HEAD `1e6367d2863a86c3470da13d81a955d277eba485`; KRX 전담 `indexalert-krx-pit-source-audit-20261013` HEAD `073d2d49e95f69fb10b943b93e51bb179fb3c698` (GitHub commit/ref API 직접 조회).
- OPEN / DRAFT / UNMERGED PR 원본 HEAD: [#412](https://github.com/kims34/openpilot-opkr/pull/412) `bf3d9514a87c53b1775e22ec9ba7711f6cecc49f`; [#413](https://github.com/kims34/openpilot-opkr/pull/413) `f003ef6247e16fcc71bd3b1b20cd4904c4d984c0`; [#414](https://github.com/kims34/openpilot-opkr/pull/414) **쓰기 전** `338201ce0b486d9254f2b9ba25bf4501ed51116c`; [#416](https://github.com/kims34/openpilot-opkr/pull/416) `053de553646fc4765d2616544ca1e8d6bbdde35f`; [#418](https://github.com/kims34/openpilot-opkr/pull/418) `2f98401cc50a6c6a25808a98516efd5bf0c944ee`; [#420](https://github.com/kims34/openpilot-opkr/pull/420) `fab3cbbd63a951a4e081f9e7f08c1391ca308581`; [#422](https://github.com/kims34/openpilot-opkr/pull/422) `c14857620973531013799e44625d43080904fd5f`; [#423](https://github.com/kims34/openpilot-opkr/pull/423) `0e38004363cac9fc4475556b3a1c445de9af407f`.
- [#414 총괄 게이트](https://github.com/kims34/openpilot-opkr/blob/338201ce0b486d9254f2b9ba25bf4501ed51116c/docs/INDEXALERT_PROFITABILITY_INTEGRATION_GATE_2026-10-13.md) Git blob SHA-1 `984c933651f39f1ee9e26a1d7ac3893aaa5335be`. 다른 Work의 PR/코드/워크플로 변경 없음.

## 2. OpenDART 최초공시 및 PIT

- [2021 공식 최초공시 Actions #40262558066](https://github.com/kims34/openpilot-opkr/actions/runs/40262558066) 2/2 SUCCESS; official job `121379096007` 원본 로그에서 2021 ZIP SHA-256 **보고값** `8728c0a3c12761ca19e9c6455bea8f1bed0e4c1ebc2e21dc263c373a82a2b625`, SGML 1개, 1,728개 table shape, 영업손익 후보 13개, 동일 표의 Q3 기간 결합 **0**, 3개월 결합 **0**. 로그에 `original_2021_q3_three_month_cfs_profit_cell_verified=false`, `2021_first_publication_instant_verified=false`, `m20_performance_run_authorized=false` 명시.
- [2022 최초·정정 SGML 후보 비교 #38419439742](https://github.com/kims34/openpilot-opkr/actions/runs/38419439742) 2/2 SUCCESS; official job `115372636726`: 최초/정정 후보 각 15개, 동일 텍스트 및 인접 숫자 후보 15개. **수치 의미·연결 CFS·3개월 기간·정정 vintage·최초 공개시각을 증명하지 않음**. 2022 최초 ZIP SHA-256 기존 공식 로그 보고 `56639d8f6ebbecf14cd8bc3179d75d01162e2cd7bbdf8f6a3c9479b44f5084bb`, 정정 ZIP `606be9d03928808f0a2a05f052444587bd2457bdef7a47a8f4bff3d2ea098a30`.
- 이번 감사에서 원본 ZIP 바이트를 재다운로드/재해시하지 않음. **ZIP 수집·모양 진단 제한적 PASS**, 2021/2022 최초 연결 3개월 영업이익, 2021 비교열, original-vs-correction lineage, exact public available-at, 과거 issuer/security mapping **NOT VERIFIED**. 정정본으로 최초 시점 소급 금지.

## 3. KRX 공식 거래가능성 및 Railway 최신 운영

- 기존 KRX private 2017–2022 weekday 일별·마스터 **1,565/1,565쌍** 저장 SHA 무결성은 **과거 기록 범위 제한적 PASS**. 이번 실행에서 private volume 재해시하지 않음. 90일 원본 공백/휴장 분류, zero-activity 12,003건, 공식 과거 시장 달력·종목 거래정지·상장폐지·기업행위·호가/체결·비용/세금 **NOT VERIFIED**. KRX [#420 synthetic CI #39714369438](https://github.com/kims34/openpilot-opkr/actions/runs/39714369438) 1/1 SUCCESS는 정책 안전성 검증에만 해당. #422의 2021 13일, #423의 2022 14일 private exact-set 비교 결과 승인 없음.
- Railway `IndexAlert` production: PIT `indexalert-pit-rebuild` 배포 `8b354fc1-cfb2-4ef0-863e-67f7f5dda2b5` SUCCESS / running 1. **2026-10-30 22:16:21 KST** 실 deploy 로그 `INDEXALERT_PROSPECTIVE_RUNTIME`: `status=FAIL_CLOSED`, `error_reason_code=COMMON_OHLC_NONPOSITIVE`, `source_failure_session=2026-09-28`, `common_stock_rows=803`, `nonpositive_ohlc_rows=27`, `zero_volume_value_rows=27`, `session_manifest_sha256=null`, independent source/chronology/model admissions all `false`, `live_order_authorized=false`, `ordering=DISABLED`. 27건을 거래 가능으로 인정하지 않음.
- PIT HTTP 최근 조회 **100건 모두 `/anchor/latest` 404** (2026-10-29~30 UTC 조회 표본; 조회한 요청에 한정). Kiwoom REAL read-only 배포 `a77fb922-b679-4d88-92c4-03054ec579cd` 메타데이터 SUCCESS이나 runtime replicas **running 0 / crashed 1**. KRX historical worker `16c93d7c-7cd0-4d84-a327-298d2805376c` 배포 SUCCESS / replicas running 0. 이번 조회에서 새로운 배포·private 작업 실행 없음.
- Railway `environment_status`는 과거 `patch:e113dacb-6705-4416-9997-dc694539d382` staged 작업을 표시하나, 별도 `get_staged_changes`는 `staged=null`, `resources=[]` 반환. **일관되지 않은 관측**으로, 실제 미적용 변경 존재를 단정하지 않으며 어떤 배포도 수락하지 않음.

## 4. 격리 최적화: 원본 SHA, CI 및 캐시

- PR #413 [#38381997417](https://github.com/kims34/openpilot-opkr/actions/runs/38381997417), [#38382214223](https://github.com/kims34/openpilot-opkr/actions/runs/38382214223) 각각 기존 6/6 jobs, 고정 34건 동등성; [#38508247773](https://github.com/kims34/openpilot-opkr/actions/runs/38508247773) 이번 job API 직접 6/6 SUCCESS. 기존 고정 outcome SHA-256 `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34`. 기존 로그 test phase serial 1.7650s vs parallel-longest 2.7079s = **0.652x**, 더 느림. 전체 CI 가속 아님.
- PR #418 [#39111405562](https://github.com/kims34/openpilot-opkr/actions/runs/39111405562) one-runner job `117628139856` SUCCESS, serial 2.3911s vs parallel 2.0755s = **1.1521x**; 다른 regression phase 2.3484s vs 2.0154s = **1.165x**. 34-case 동일 SHA. 이들은 **합성 오프라인 테스트 phase**에만 해당하며 전체 CI·실제 공식 백테스트 성능 NOT VERIFIED.
- 같은 PR #418 [병합 환경 archived source gate #39111405478](https://github.com/kims34/openpilot-opkr/actions/runs/39111405478) job `117628139395` **FAIL**: `research_v1_runtime_manifest.py` expected Git blob `108f66714602a1bd3ae42c34dcca7c16e38f460b`, observed `e0055c66c59398fd4a1158077446d886b54c4e37`. 이번 실행 GitHub 원본 HEAD/merge `052cf67e45500baad771527753744289529ecbc2` 파일 API에서 두 SHA 직접 재확인. [candidate merge audit #39111405494](https://github.com/kims34/openpilot-opkr/actions/runs/39111405494) SUCCESS는 기존 archived baseline FAIL을 취소하지 않음. exact wheel hash, OS native dependencies, runtime approval evidence SHA-256 **NOT VERIFIED**.
- [Watchdog #41027450112](https://github.com/kims34/openpilot-opkr/actions/runs/41027450112) job `123968824089` 31개 offline governance tests PASS; `M20 PIT admission: NOT ATTESTED; orders: DISABLED; holdout: NOT AUTHORIZED` 명시.
- **CACHE FAIL-CLOSED**: 독립 승인된 source/data/code/Frozen policy/runtime/approval evidence SHA-256이 모두 일치해야만 고려. 승인 없는 해시 교체 금지. 읽기전용 독립 후처리만 병렬화 후보; 의존 재학습·capital transition 병렬화 금지.

## 5. 독립 총괄 판정

| Gate | 판정 | 근거 |
| --- | --- | --- |
| OpenDART 최초 ZIP 수집·형태·로그 SHA | **PASS (제한적)** | 2021/2022 Actions; 이번 실행 raw bytes 독립 재해시 아님 |
| 2021/2022 CFS 3개월 사실값, 정정 계보, exact available-at, 과거 기업/종목 매핑 | **NOT VERIFIED** | 후보 기간·연결 결합 0, 원본 시점 증명 없음 |
| KRX 1,565쌍 private 저장 SHA | **PASS (기존 범위)** | official session/tradability 승인과 별개 |
| KRX 공식 과거 시장상태·기업행위·체결·비용/세금 | **NOT VERIFIED** | 90일·12,003건·27/803건 및 공식 상태 공백 |
| PR #413/#418 고정 34건 합성 parity | **PASS (제한적)** | 독립 CI SHA 동일 |
| PR #418 archived 병합 원본 SHA | **FAIL** | Git blob lineage mismatch |
| 전체 CI/실제 백테스트 속도·캐시 승인 | **NOT VERIFIED / FAIL-CLOSED** | source PIT와 runtime wheel/native evidence 미승인 |
| 세후 NetEV/PF/CAGR/MDD/ES95·99/수익 집중도/시점별 강건성 | **NOT EVALUABLE** | M20 공식 독립 경제성 평가 미승인 |
| M20 PIT / M20 경제성 / Holdout / Champion / Tiny Live | **NO-GO** | 상위 원본·시장·모델 게이트 미통과 |

**고정 정책:** Frozen H5와 소비된 Holdout 독립 재사용 금지, M20 horizon20/purge20, WF504/126/126, PIT/라벨/Purged/CPCV/독립 Holdout/Champion/Top3/NO_TRADE, 비용·세금·체결·위험·승격 기준 불변. `ORDERING=false`. 실주문·자금·인증/계좌권한·Champion 승격은 각각 별도 명시 승인 필요. 운영 배포/PR #413/#414/#418 병합 금지.

**다음 검증 경로:** OpenDART 전담이 최초 2021/2022 연결 3개월 fact+period+correction+public available-at 및 issuer/security history를 원본 SHA와 함께 입증 → KRX 전담이 공식 역사적 session/status/corporate actions/체결·비용·세금을 입증 → 별도 runtime/계산코드/Frozen/evidence 해시 및 안전 게이트를 독립 검증 → 그 후에만 사전등록 M20 단일 평가와 세후 위험지표 판정. 그 전에는 오프라인 합성 정책/소프트웨어 검증만 허용.

**변경 범위:** 이 독립 문서 한 개 추가만 시도. 다른 전담 소스/워크플로/시장 원본/운영 설정/주문/배포/PR 병합 변경 없음.
