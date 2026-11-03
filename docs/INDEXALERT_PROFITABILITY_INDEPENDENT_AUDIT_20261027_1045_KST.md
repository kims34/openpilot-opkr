# IndexAlert 독립 수익성 게이트 — 2026-10-27 10:45 KST (read-only evidence)

**범위:** 독립 총괄 감사만. 이 문서는 원본/PIT/거래가능성 승인, 주문 허가, 수익성 실행 허가가 아니다. 원본/종목/계좌/비밀정보를 포함하지 않는다. 기존 전담 Work의 코드·워크플로·데이터를 변경하지 않는다.

## 실제 확인한 GitHub HEAD / PR (2026-10-27 10:45 KST)
- 연구 `index-alert-research-v1`: PR #414 base SHA `3b8b7830612a6284d7c7a60628cb527cb741627a` (base ref 기준; 직접 브랜치 SHA endpoint 별도 미확인).
- 개발 `index-alert-position-regen-fix-v1`: PR #420 base SHA `1e6367d2863a86c3470da13d81a955d277eba485` (base ref 기준; 직접 브랜치 SHA endpoint 별도 미확인).
- 총괄 [#414](https://github.com/kims34/openpilot-opkr/pull/414): Draft/open/unmerged, head `523fd22c12ca2f89b2b5143147fa94c38f2b7290`, base research. [원본 총괄 문서](https://github.com/kims34/openpilot-opkr/blob/indexalert-profitability-integration-evidence-20261013/docs/INDEXALERT_PROFITABILITY_INTEGRATION_GATE_2026-10-13.md), Git blob `984c933651f39f1ee9e26a1d7ac3893aaa5335be`.
- OpenDART [#412](https://github.com/kims34/openpilot-opkr/pull/412): Draft/unmerged, head `bf3d9514a87c53b1775e22ec9ba7711f6cecc49f`.
- 최적화 [#413](https://github.com/kims34/openpilot-opkr/pull/413): Draft/unmerged, head `f003ef6247e16fcc71bd3b1b20cd4904c4d984c0`. 독립 단일 실행기 [#418](https://github.com/kims34/openpilot-opkr/pull/418): Draft/unmerged, head `2f98401cc50a6c6a25808a98516efd5bf0c944ee`.
- KRX [#420](https://github.com/kims34/openpilot-opkr/pull/420) head `fab3cbbd63a951a4e081f9e7f08c1391ca308581`; [#422](https://github.com/kims34/openpilot-opkr/pull/422) head `c14857620973531013799e44625d43080904fd5f`; [#423](https://github.com/kims34/openpilot-opkr/pull/423) head `0e38004363cac9fc4475556b3a1c445de9af407f`. 모두 Draft/open/unmerged.

## 독립 원본 Actions / 로그 판정
| 게이트 | 판정 | 원본 근거와 한계 |
|---|---|---|
| OpenDART 2021 최초공시 ZIP 동일성 | **PASS (바이트/형태만)** | [Actions #40262558066](https://github.com/kims34/openpilot-opkr/actions/runs/40262558066), official job `121379096007` SUCCESS. ZIP SHA-256 `8728c0a3c12761ca19e9c6455bea8f1bed0e4c1ebc2e21dc263c373a82a2b625`. 1,728 table shapes, operating-label candidates 13, same-table Q3 period 0, three-month word 0. 최초 2021 Q3 3개월 연결 영업이익 fact **NOT VERIFIED**. |
| OpenDART 2022 최초/정정 | **원본 ZIP 무결성만 기존 PASS; CFS/PIT NOT VERIFIED** | #412, 기존 [Actions #38417433460](https://github.com/kims34/openpilot-opkr/actions/runs/38417433460), 원본 `56639d8f6ebbecf14cd8bc3179d75d01162e2cd7bbdf8f6a3c9479b44f5084bb`, 정정 `606be9d03928808f0a2a05f052444587bd2457bdef7a47a8f4bff3d2ea098a30` (기존 감사 문서 기재). 2026-10-26 [Actions #40263181687](https://github.com/kims34/openpilot-opkr/actions/runs/40263181687) 및 [#40263193758](https://github.com/kims34/openpilot-opkr/actions/runs/40263193758)는 synthetic-only CI 성공; 실제 최초 연결 3개월 사실값/정정 lineage/public available-at/PIT 증명 아님. |
| 역사적 issuer/security mapping | **NOT VERIFIED** | 최초공시 원본 2021 job의 `historical_issuer_security_pit_verified=false`; 과거 종목·법인 연결 원본 증거 없음. |
| KRX 공식 시장상태/기업행위/체결 | **NOT VERIFIED** | 과거 2017–2022 1,565/1,565 weekday 원본쌍 저장 SHA 무결성 PASS는 보관 범위에 한정. 90 source/calendar gap, 27 bad OHLC, 12,003 zero-activity 미승인. [Actions #39714207925](https://github.com/kims34/openpilot-opkr/actions/runs/39714207925) job `119612335677` 32 synthetic tests PASS지만 `DRY_RUN_NO_PRIVATE_STORAGE_READ`, 실제 2022 private day-set equality false. [#39714369438](https://github.com/kims34/openpilot-opkr/actions/runs/39714369438) synthetic job PASS. |
| Chronology prospective anchor | **FAIL** | [Actions #40360864884](https://github.com/kims34/openpilot-opkr/actions/runs/40360864884), job `121705590170` HTTP 404 `/anchor/latest`; validation skipped. 소스 PIT/승인으로 사용 불가. |
| Watchdog 안전성 | **PASS (offline controls only)** | [Actions #40417624722](https://github.com/kims34/openpilot-opkr/actions/runs/40417624722), job `121903776561` SUCCESS, 4+31 synthetic tests; `M20 PIT admission: NOT ATTESTED; orders: DISABLED; holdout: NOT AUTHORIZED`. artifact ZIP SHA-256 `fdfb75060ba46b187a108a71d07c956f442ab9652719fd28eb65b321428a0dd1`. |
| 최적화 고정 동등성 | **PASS (offline tests only)** | [#413 Actions #38508247773](https://github.com/kims34/openpilot-opkr/actions/runs/38508247773) 6/6 jobs SUCCESS. [#418 Actions #39111405562](https://github.com/kims34/openpilot-opkr/actions/runs/39111405562) one-runner job SUCCESS; 34-case digest `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34`, serial 2.3484s vs parallel 2.0154s = test phase 1.165x. Full workflow and real economic backtest speedup **NOT VERIFIED**. |
| 최적화 원본 보존 | **FAIL** | [#418 Actions #39111405478](https://github.com/kims34/openpilot-opkr/actions/runs/39111405478) job `117628139395` `SourceDriftError`: `research_v1_runtime_manifest.py` expected Git blob `108f66714602a1bd3ae42c34dcca7c16e38f460b`, observed `e0055c66c59398fd4a1158077446d886b54c4e37`. Fail closed. |
| Railway 운영 배포/로그 및 실제 ORDERING | **NOT VERIFIED (접근 차단)** | Railway 프로젝트 목록 read-only 조회 시 interactive user input required; 자동 작업에서는 로그인 승인 불가. 우회/권한 변경/배포 없음. CI의 ordering false는 실제 Railway 환경 변수 확인을 대체하지 않는다. |
| 비용·세금·NetEV/PF/CAGR/MDD/ES95/99/수익 집중도/시점별 강건성 | **NOT VERIFIED** | 공식 PIT/거래가능성 원본 승인 전 경제성 테스트 금지; 새 성과/모델 탐색/실거래 백테스트 실행하지 않음. |

## 정책·다음 게이트
- **M20 NO-GO**. Frozen H5, M20 horizon20/purge20, WF504/126/126, Purged/CPCV, independent sealed Holdout, Champion/Top3/NO_TRADE, 기존 비용·세금·위험 기준 고정. 실패/소비 Holdout 재사용 및 Dynamic 사후 조정 금지.
- **ORDERING=false 요구** 및 주문 비활성 상태 유지. 실제 운영 값은 별도 인증된 읽기전용 Railway 증거 없이는 확인했다고 주장하지 않음. 주문·자금·계좌권한·배포·PR 병합·Champion 승격 없음.
- OpenDART 전담의 최초 제출 CFS 정확 기간/수치/공표 시점 lineage 증명 → KRX 전담의 공식 원본 거래일·상태·기업행위·체결가능성/비용/세금 증명 → 독립 source/code/policy/runtime/evidence SHA pin → *그 후에만* 별도 승인된 최초 M20 평가 가능.
- 최적화 전담은 기존 34-case 원본 blob mismatch 해결을 독립 작업으로만 수행. 승인원본 SHA 전부 일치 시에만 cache fail-closed, 읽기전용 후처리만 병렬화. 의존적 재학습/capital transition 병렬화 금지.

**이번 변경:** 총괄 격리 문서 신규 추가만 1회 시도. 다른 전담 파일·워크플로·운영 환경 미변경.
