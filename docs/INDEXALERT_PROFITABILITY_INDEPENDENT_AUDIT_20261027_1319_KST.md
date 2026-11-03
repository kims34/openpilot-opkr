# IndexAlert 독립 수익성·격리 최적화 읽기전용 감사 — 2026-10-27 13:19 KST

> 이 문서는 원본/CI/정책 상태를 분리한 독립 감사 기록이다. 신규 M20 수익률 생성, 소스 PIT 승인, Champion 승격, 실거래 승인, 배포 또는 PR 병합의 근거가 아니다. 민감한 원본 데이터·기업 식별값·계좌/인증정보는 포함하지 않는다.

## 실제 조회한 기준 HEAD 및 격리 상태

- 연구 `index-alert-research-v1` HEAD `3b8b7830612a6284d7c7a60628cb527cb741627a`; 개발 `index-alert-position-regen-fix-v1` HEAD `1e6367d2863a86c3470da13d81a955d277eba485`. 두 GitHub branch REST 응답에서 확인.
- 총괄 Draft PR [#414](https://github.com/kims34/openpilot-opkr/pull/414) head `496d499ec7e3d3eb7128bc0d085ef714641bf387` (본 문서 작성 직전), OpenDART Draft [#412](https://github.com/kims34/openpilot-opkr/pull/412) `bf3d9514a87c53b1775e22ec9ba7711f6cecc49f`, 격리 최적화 Draft [#413](https://github.com/kims34/openpilot-opkr/pull/413) `f003ef6247e16fcc71bd3b1b20cd4904c4d984c0`, 별도 단일 실행기 Draft [#418](https://github.com/kims34/openpilot-opkr/pull/418) `2f98401cc50a6c6a25808a98516efd5bf0c944ee`.
- KRX Draft [#420](https://github.com/kims34/openpilot-opkr/pull/420) `fab3cbbd63a951a4e081f9e7f08c1391ca308581`, [#422](https://github.com/kims34/openpilot-opkr/pull/422) `c14857620973531013799e44625d43080904fd5f`, [#423](https://github.com/kims34/openpilot-opkr/pull/423) `0e38004363cac9fc4475556b3a1c445de9af407f`. 모두 open/draft/unmerged. 타 담당의 코드와 원본 저장소는 수정하지 않음.

## 독립 증거별 판정 (PASS / FAIL / NOT VERIFIED)

| 항목 | 판정 | 실제 원본 또는 한계 |
|---|---|---|
| 2021 최초 제출 ZIP 원본 무결성 | **PASS — 파일 바이트 한정** | [공식 read-only Actions #40262558066](https://github.com/kims34/openpilot-opkr/actions/runs/40262558066), 원본 SHA-256 `8728c0a3c12761ca19e9c6455bea8f1bed0e4c1ebc2e21dc263c373a82a2b625`. 13개 영업이익 후보 표 중 동일 표의 Q3 기간/3개월 기간 확정 0. |
| 2022 최초/정정 ZIP 파일 구분 | **PASS — 바이트 무결성 범위** | [공식 Actions #38417433460](https://github.com/kims34/openpilot-opkr/actions/runs/38417433460): 원본 `56639d8f6ebbecf14cd8bc3179d75d01162e2cd7bbdf8f6a3c9479b44f5084bb`, 정정 `606be9d03928808f0a2a05f052444587bd2457bdef7a47a8f4bff3d2ea098a30`. [#38419439742](https://github.com/kims34/openpilot-opkr/actions/runs/38419439742)의 15개 SGML 후보 행/숫자 인접 시그니처 일치는 재무 사실값의 의미나 available-at을 증명하지 않음. |
| 2021·2022 최초 3개월 연결 영업이익, 기간/정정 lineage, 공표시각 available-at, 기업·종목 과거 매핑 | **NOT VERIFIED** | 최초 2021 원본 후보 13개/기간 같은 표 확정 0, 2022 원본 XBRL 공식 014 FILE_NOT_FOUND; 원본/정정 후보 서명 일치만으로 의미·시점 승인 불가. 수정본으로 최초시점 역채움 금지. |
| KRX 2017–2022 private 저장 1,565/1,565 평일 원본쌍 | **PASS — 2026-10-14 이전 원본 로그에서 보고된 저장 무결성 한정** | 기존 dedicated Railway 배포 `16c93d7c-7cd0-4d84-a327-298d2805376c` 증거. 이 실행에서 private 볼륨을 재조회하지 못했으므로 신규 PASS로 승격하지 않음. |
| 공식 KRX 휴장/상장·거래정지/기업행위·체결가능성·세금/비용 | **NOT VERIFIED** | 휴장/원본공백 90일 및 zero-activity 12,003건 차단 유지. [KRX #423 Actions #39714207925](https://github.com/kims34/openpilot-opkr/actions/runs/39714207925)는 합성 32건 성공이나 실제 private day-set 미조회 DRY RUN. 2021/2022 시점별 venue/공개시각 인증 불충족. |
| PIT Chronology prospective anchor | **FAIL — 실제 요청 실패** | [Actions #40360864884](https://github.com/kims34/openpilot-opkr/actions/runs/40360864884) job `auto-anchor`: 공개 hash-only `/anchor/latest` HTTP 404, 검증 job skipped. 과거 데이터나 인증 설정 변경으로 우회하지 않음. |
| Frozen/Holdout/주문 차단 소프트웨어 검증 | **PASS — 오프라인 안전 테스트 한정** | 최신 [Watchdog #40436115571](https://github.com/kims34/openpilot-opkr/actions/runs/40436115571), 31개 governance + 4개 watchdog = 35개 테스트 성공, `M20 PIT admission: NOT ATTESTED; orders: DISABLED; holdout: NOT AUTHORIZED`. 아티팩트 ZIP SHA-256 `3ea4af4d7f8dfe080b191901e6fcba21425d82cd24e57e48c8ef0eeb0d9ca7c5`. |
| 최적화 #413 34-case 고정 동등성 | **PASS — 오프라인 테스트 한정** | [Actions #38381997417](https://github.com/kims34/openpilot-opkr/actions/runs/38381997417), [#38382214223](https://github.com/kims34/openpilot-opkr/actions/runs/38382214223), 최신 [#38508247773](https://github.com/kims34/openpilot-opkr/actions/runs/38508247773) 6/6 jobs, pinned 34-case digest `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34`. 최신 parity job serial 1.7650s vs parallel max 2.7079s = 0.652x, 개선 아님. |
| 최적화 #418 단일 실행기 동등성/아카이브 원본 | **PASS/FAIL 분리** | [#39111405562](https://github.com/kims34/openpilot-opkr/actions/runs/39111405562) synthetic/offline parity 성공, 기존 34-case SHA 일치. 별도 [#39111405478](https://github.com/kims34/openpilot-opkr/actions/runs/39111405478) source gate **FAIL**: `research_v1_runtime_manifest.py` Git blob expected `108f66714602a1bd3ae42c34dcca7c16e38f460b`, observed `e0055c66c59398fd4a1158077446d886b54c4e37`. Fail-closed 유지; 기존 [#38419649711](https://github.com/kims34/openpilot-opkr/actions/runs/38419649711) 회귀 phase 1.1315x는 전체 CI/실제 백테스트 가속 증거 아님. |
| 세후 NetEV/PF/CAGR/MDD/ES95/99, 수익 집중도, 시점별 강건성 | **NOT VERIFIED** | 원본 PIT/거래가능성/비용·세금 승인 부재로 공식 M20 경제성 RUN 금지; 수익률 숫자를 생성하거나 추정하지 않음. H5 실패·소비 Holdout과 Dynamic 결과의 독립 재사용 금지. |
| Railway 현재 운영 배포·로그·실제 ORDERING 환경변수 | **NOT VERIFIED — 접근 차단** | 연결된 Railway read-only `list_projects`가 대화형 사용자 입력 요구로 차단됨. 인증 우회·권한 변경·서비스 조작 없음. 기존 문서의 `ORDERING=false` 필수 정책과 실제 런타임 값 확인은 구별. |

## 변경 불가 경계 및 다음 증거

- **M20 수익성 NO-GO.** Frozen H5; M20 horizon20/purge20, WF504/126/126; PIT/label/Purged/CPCV/독립 Holdout/Champion/Top3/NO_TRADE; 기존 비용·세금·체결·위험·승격 기준 변경 금지. `ORDERING=false` 필수; 실제 Railway 설정은 이번 조회에서 미검증.
- 캐시는 승인된 독립 source/data/code/Frozen/runtime/approval evidence SHA-256 전체 일치시에만 fail-closed. 읽기전용 독립 후처리만 병렬화 가능. 의존적 재학습·capital transition 병렬화, 신규 공식 시장 성과·모델 탐색·M20 경제성 평가 금지.
- **증거 순서:** OpenDART 원본 최초 연결 3개월 영업이익/기간/공표시각·정정 lineage → KRX 공식 시장·종목 이력/체결/비용/세금 → 독립 PIT 승인 → 고정 M20 단일 공식 평가 → 별도 명시 승인에 의한 승격·거래. 최적화는 원본 Git blob mismatch와 전체 CI wall-clock을 별도로 해결하되 이 감사에서 코드를 수정하지 않음.
- Railway 조회 차단 해소에는 사용자의 정상 연결 인증 절차가 필요할 수 있음. 보안 검사가 막은 workflow 또는 다른 쓰기는 재시도·우회하지 않음. 이 문서 이외 코드/워크플로/배포/PR 병합/주문/자금/계좌권한/Champion 승격 변경 없음.
