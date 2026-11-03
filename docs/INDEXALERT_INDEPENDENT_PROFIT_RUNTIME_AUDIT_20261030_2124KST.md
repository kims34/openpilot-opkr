# IndexAlert 독립 수익성·격리 실행환경 감사 — 2026-10-30 21:24 KST

> **범위:** 기존 원본과 CI 및 Railway 로그의 읽기전용 재검증. 이 문서는 원본 소스/PIT 승인, 새 수익성 실험, 캐시 승인, 실주문/자금/권한 변경, Champion 승격 또는 배포 승인이 아니다. 공개 문서에 개인 원본 시장자료·발행사 식별자·계좌/인증 정보는 기록하지 않는다.

## 1. 실제 GitHub HEAD / 소유 경계
- 연구 `index-alert-research-v1` HEAD **`3b8b7830612a6284d7c7a60628cb527cb741627a`**; 개발 `index-alert-position-regen-fix-v1` HEAD **`1e6367d2863a86c3470da13d81a955d277eba485`**; KRX 원본 전담 `indexalert-krx-pit-source-audit-20261013` HEAD **`073d2d49e95f69fb10b943b93e51bb179fb3c698`**. GitHub commit-ref 직접 조회.
- 모든 관련 PR은 OPEN / DRAFT / UNMERGED: [#412](https://github.com/kims34/openpilot-opkr/pull/412) `bf3d9514a87c53b1775e22ec9ba7711f6cecc49f`; [#413](https://github.com/kims34/openpilot-opkr/pull/413) `f003ef6247e16fcc71bd3b1b20cd4904c4d984c0`; [#414](https://github.com/kims34/openpilot-opkr/pull/414) **사전 기록 HEAD** `eaf829039163e6aa372b69c87afcbdd8534d1d4c`; [#416](https://github.com/kims34/openpilot-opkr/pull/416) `053de553646fc4765d2616544ca1e8d6bbdde35f`; [#418](https://github.com/kims34/openpilot-opkr/pull/418) `2f98401cc50a6c6a25808a98516efd5bf0c944ee`; [#420](https://github.com/kims34/openpilot-opkr/pull/420) `fab3cbbd63a951a4e081f9e7f08c1391ca308581`; [#422](https://github.com/kims34/openpilot-opkr/pull/422) `c14857620973531013799e44625d43080904fd5f`; [#423](https://github.com/kims34/openpilot-opkr/pull/423) `0e38004363cac9fc4475556b3a1c445de9af407f`.
- [#414 총괄 게이트 문서](https://github.com/kims34/openpilot-opkr/blob/eaf829039163e6aa372b69c87afcbdd8534d1d4c/docs/INDEXALERT_PROFITABILITY_INTEGRATION_GATE_2026-10-13.md) Git blob SHA-1 `984c933651f39f1ee9e26a1d7ac3893aaa5335be`; [20:18 독립 감사](https://github.com/kims34/openpilot-opkr/blob/eaf829039163e6aa372b69c87afcbdd8534d1d4c/docs/INDEXALERT_INDEPENDENT_PROFIT_RUNTIME_AUDIT_20261030_2018KST.md) blob `c2bfb95e22df505d40b722a65983ed4dbbb6cc2b`. 전담방 코드/워크플로/PR에 변경 없음.

## 2. 최초공시·시점·과거 종목 / 원본 승인
- 2021년 [OpenDART 최초 제출 Actions #40262558066](https://github.com/kims34/openpilot-opkr/actions/runs/40262558066), official job `121379096007` SUCCESS. **작업 로그가 보고한** original ZIP SHA-256 `8728c0a3c12761ca19e9c6455bea8f1bed0e4c1ebc2e21dc263c373a82a2b625`; SGML 1개, 표 형태 1,728개, 영업손익 표 후보 13개, 같은 표에서 2021 Q3 기간 결합 **0개**, 3개월 기간 결합 **0개**. 원본 2021년 연결 3개월 영업이익 셀·2022 최초 공시의 2021 비교열·공개시각·정정 전체 계보 **NOT VERIFIED**.
- 2022년 [최초 공시 Actions #38392847048](https://github.com/kims34/openpilot-opkr/actions/runs/38392847048)에서 **로그 보고** original ZIP SHA-256 `56639d8f6ebbecf14cd8bc3179d75d01162e2cd7bbdf8f6a3c9479b44f5084bb`, 영업이익 후보 표 15개, 엄격한 최초 연결 3개월 사실값 0개. [원본·정정 후보 비교 #38419439742](https://github.com/kims34/openpilot-opkr/actions/runs/38419439742) 2/2 SUCCESS; 후보 행 텍스트/인접 숫자 시그니처의 모양 일치일 뿐 사실값의 기간·연결 의미·public available-at 검증 아님. 정정 ZIP SHA-256은 기존 로그 보고 `606be9d03928808f0a2a05f052444587bd2457bdef7a47a8f4bff3d2ea098a30`.
- **판정:** 원본 ZIP 수집·모양 진단 제한적 PASS; 최초공시 정확한 수치·단위·부호, 기간 및 정정 lineage, intraday available-at, 기업/종목 과거 매핑, 2021 비교연결 **NOT VERIFIED**. 원본 raw ZIP을 이번 실행에서 독립 다운로드/재해시하지 않았으므로 로그 SHA를 독립 byte-level 재검증으로 표현하지 않음. M20 feature PIT **NO-GO**.

## 3. KRX 역사적 거래상태·실체결 / Railway
- KRX 2017–2022 1,565/1,565 weekday 원본 일별·마스터 쌍 SHA 저장 무결성 **기존 제한적 PASS**(이번 실행에서 private /data 원본을 재해시하지 않음). 휴장·소스공백 90일, zero-activity 12,003건, 과거 거래정지/상장폐지/기업행위/상장·종목 계보/호가·체결/lot·비용·세금은 **NOT VERIFIED**. KRX [#420 synthetic CI #39714369438](https://github.com/kims34/openpilot-opkr/actions/runs/39714369438) 1/1 SUCCESS; 실제 공식 과거 달력·종목상태 승인과 구분. #422(2021 13일)·#423(2022 14일)은 기존 private 볼륨 실제 비교 미수행.
- Railway 프로젝트 `IndexAlert` production: PIT 서비스 `indexalert-pit-rebuild` 배포 `8b354fc1-cfb2-4ef0-863e-67f7f5dda2b5` SUCCESS / running 1. **2026-10-30 21:16:06 KST** 최신 조회된 runtime 로그 `status=FAIL_CLOSED`, `error_reason_code=COMMON_OHLC_NONPOSITIVE`, `source_failure_session=2026-09-28`, `common_stock_rows=803`, `nonpositive_ohlc_rows=27`, `zero_volume_value_rows=27`, `session_manifest_sha256=null`, `independent_source_admission_verified=false`, `independent_chronology_admission_verified=false`, `independent_model_admission_verified=false`, `live_order_authorized=false`, `ordering=DISABLED`. 27건은 거래가능 판정 불가.
- PIT 서비스 HTTP 로그 조회 30건 `/anchor/latest` **전부 404**(2026-10-29~30 KST 구간, 마지막 2026-10-30 02:21 KST); 이 관측은 조회된 요청에 한정. Kiwoom REAL read-only 배포 `a77fb922-b679-4d88-92c4-03054ec579cd` SUCCESS 메타데이터이나 실제 replica `running=0, crashed=1`: **실서비스 정상 가동 PASS 아님**. KRX 역사 worker 배포 `16c93d7c-7cd0-4d84-a327-298d2805376c` SUCCESS, 현재 실행 replica 0/1; 이전 보관 원본에 대한 새 접근/작업 없음. Railway 최근 새 배포 없음.
- Railway `environment_status`가 `patch:e113dacb-6705-4416-9997-dc694539d382`의 staged 메타데이터를 반환했으나, 즉시 별도 `get_staged_changes`는 `staged=null`, `resources=[]` 반환. **일관성 없는 스냅샷이므로 배포 대기 중 변경이 있다고 단정하지 않음**. 배포/수락/변수 변경 금지.

## 4. 독립 오프라인 최적화 / 재현성
- PR #413 [Actions #38381997417](https://github.com/kims34/openpilot-opkr/actions/runs/38381997417) 및 [#38382214223](https://github.com/kims34/openpilot-opkr/actions/runs/38382214223) 각각 6/6 jobs PASS, 고정 34건; [#38419111311](https://github.com/kims34/openpilot-opkr/actions/runs/38419111311) 6/6 PASS, 13 adversarial mocks, serial 2.7647s / parallel-longest 3.3876s = **0.816x**. 더 최근 [#38508247773](https://github.com/kims34/openpilot-opkr/actions/runs/38508247773) 6/6 PASS, serial 1.7650s / parallel-longest 2.7079s = **0.6520x**, 더 느림.
- PR #418 [#38419649711](https://github.com/kims34/openpilot-opkr/actions/runs/38419649711) 1/1 PASS, serial subprocess 2.9656s vs parallel 2.6209s = **1.1315x**; [#39111405562](https://github.com/kims34/openpilot-opkr/actions/runs/39111405562) 1/1 PASS, serial 2.3911s vs parallel 2.0755s = **1.1521x** (다른 test-phase 정의의 2.3484s/2.0154s = 1.1650x). 두 트랙 모두 고정 34건 outcome SHA-256 `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34` 일치. **고정 합성 동등성 제한적 PASS**, 전체 CI wall time / 공식 백테스트 가속 **NOT VERIFIED**.
- `research_v1_runtime_manifest.py` Git blob SHA-1 **#418 head `108f66714602a1bd3ae42c34dcca7c16e38f460b`** vs **#413 head 및 #418 merge `052cf67e45500baad771527753744289529ecbc2`에서 `e0055c66c59398fd4a1158077446d886b54c4e37`**: 이번 실행 GitHub file API로 재확인. 기존 병합 원본 기대값에 대한 drift **FAIL**이며, 임의 SHA 교체로 우회 금지. exact Python wheel/OS native/runtime approval SHA-256도 **NOT VERIFIED**. **CACHE FAIL-CLOSED**; 승인된 source/data/code/Frozen/runtime/evidence SHA-256 전체 일치할 때만 고려. 읽기전용 독립 후처리만 병렬 후보; 재학습·capital transition 병렬화 금지.
- [2026-10-30 Watchdog #41027450112](https://github.com/kims34/openpilot-opkr/actions/runs/41027450112) 1/1 SUCCESS; 오프라인 정책 테스트 성공과 `M20 PIT admission: NOT ATTESTED; orders: DISABLED; holdout: NOT AUTHORIZED` 로그 재확인. 정책 CI는 시장 원본 검증이 아니다.

## 5. 통합 판정 / 순서
| 게이트 | 판정 | 이유 |
| --- | --- | --- |
| 최초공시 original-filing 수집·SHA 진단 | **PASS (제한적)** | Actions 원본 ZIP 해시 보고·형태 분석; raw bytes 독립 재해시 아님 |
| 2021/2022 CFS 3개월 영업이익·비교열·정정·available-at·issuer mapping | **NOT VERIFIED** | 최초 시점과 정확한 사실값 결합 실패 |
| KRX private 저장 1,565쌍 무결성 | **PASS (과거 보고 범위)** | 저장 영수증; 시장/거래 가능성 아님 |
| KRX 공식 과거 session/status/기업행위/체결·비용·세금 | **NOT VERIFIED** | 90일, 12,003건, 27/803건 및 공식 PIT 누락 |
| PR #413 / #418 고정 합성 회귀 동등성 | **PASS (제한적)** | 34-case SHA 일치, 별도 CI 성공 |
| PR #418 병합 source lineage | **FAIL** | manifest blob SHA mismatch |
| 실제 전체 백테스트 속도 / 승인 캐시 | **NOT VERIFIED / FAIL-CLOSED** | 실 source PIT 미승인, runtime wheel·native evidence 미승인 |
| NetEV, PF, CAGR, MDD, ES95/99, 집중도, 시점별 강건성 | **NOT EVALUABLE** | 실제 공식 세후 독립 수익성 실행 불승인 |
| M20 PIT / economic run / Holdout / Champion / Tiny Live | **NO-GO** | 독립 원본·시장·모델 게이트 미충족 |

**고정 정책 유지:** H5 Frozen/소비 Holdout 재사용 금지, M20 horizon20/purge20/WF504·126·126, PIT/label/Purged/CPCV/독립 Holdout/Champion/Top3/NO_TRADE, 비용·세금·체결·위험·승격 기준 불변. `ORDERING=false` 유지. 실주문·자금·인증·계좌권한·Champion 승격은 각각 별도 명시 승인 필요. PR #413/#414/#418 자동 병합 및 운영 배포 금지.

**다음 검증 경로:** OpenDART 전담의 2021/2022 최초공시 정확한 연결 3개월 fact/period/correction/public available-at 증거와 기업 과거 매핑 독립 증명 → KRX 전담의 원본 보존 하 공식 달력·거래상태·기업행위·실체결·비용·세금 검증 → 그때만 원본·코드·정책·runtime/evidence SHA 재현성 확인 → 사전등록 M20 단일 평가와 세후 위험지표 독립 판정. 그 전에는 합성 오프라인 정책/회귀 검증만 허용.

**변경 기록:** 이 파일 하나만 안전한 격리 감사 문서로 추가. 기존 코드/워크플로/타 전담 파일/시장 원본/환경 변수/배포/주문은 변경하지 않음.
