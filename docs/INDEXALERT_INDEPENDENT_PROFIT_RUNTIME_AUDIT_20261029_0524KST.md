# IndexAlert 독립 수익성·격리 최적화 감사 — 2026-10-29 05:24 KST

> **증거의 경계:** GitHub REST/Actions 원본 read-only 조회로 확인한 내용만 PASS/FAIL/NOT VERIFIED로 판정. Railway 직접 조회는 비대화식 연결 승인 요구로 **NOT VERIFIED**. 이전 채팅의 성공 주장이나 다른 전담방 문서는 원본 승인서로 취급하지 않음. 본 문서는 승인·배포·거래 명령이 아님.

## 실제 조회한 기준선과 작업 경계
- 연구 `index-alert-research-v1` HEAD `3b8b7830612a6284d7c7a60628cb527cb741627a`; 개발 `index-alert-position-regen-fix-v1` HEAD `1e6367d2863a86c3470da13d81a955d277eba485` (GitHub branches REST).
- Draft PR [#412](https://github.com/kims34/openpilot-opkr/pull/412) `bf3d9514a87c53b1775e22ec9ba7711f6cecc49f`; [#413](https://github.com/kims34/openpilot-opkr/pull/413) `f003ef6247e16fcc71bd3b1b20cd4904c4d984c0`; [#414](https://github.com/kims34/openpilot-opkr/pull/414) `00a4e4e93c17a11f67af11e2edad33a92a54c4df`; [#416](https://github.com/kims34/openpilot-opkr/pull/416) `053de553646fc4765d2616544ca1e8d6bbdde35f`; [#418](https://github.com/kims34/openpilot-opkr/pull/418) `2f98401cc50a6c6a25808a98516efd5bf0c944ee`.
- KRX Draft [#420](https://github.com/kims34/openpilot-opkr/pull/420) `fab3cbbd63a951a4e081f9e7f08c1391ca308581`; [#422](https://github.com/kims34/openpilot-opkr/pull/422) `c14857620973531013799e44625d43080904fd5f`; [#423](https://github.com/kims34/openpilot-opkr/pull/423) `0e38004363cac9fc4475556b3a1c445de9af407f`. 별도 KRX source-audit 브랜치의 최신 read-only CI [#39721289545](https://github.com/kims34/openpilot-opkr/actions/runs/39721289545) HEAD `1611b250738a17b04a1e8e06fbbcae7dbf3a4f87`.
- PR #414의 [통합 게이트 원본](https://github.com/kims34/openpilot-opkr/blob/00a4e4e93c17a11f67af11e2edad33a92a54c4df/docs/INDEXALERT_PROFITABILITY_INTEGRATION_GATE_2026-10-13.md) Git blob SHA-1 `984c933651f39f1ee9e26a1d7ac3893aaa5335be`. 전담 PR 및 코드 미수정; 이 격리 문서만 신규 작성.

## 출처/PIT 및 수익성 게이트
| 검증 항목 | 판정 | 원본과 한계 |
|---|---|---|
| OpenDART 2022 원본·정정 SGML 영업이익 후보 형식 | **PASS (형식/후보 수만)** | [#38419439742](https://github.com/kims34/openpilot-opkr/actions/runs/38419439742) 두 jobs SUCCESS, 원본·정정 각 15개 후보, 후보 텍스트 multiset 일치. 최초 연결 3개월 실질 사실값의 동일성/시점 증명은 아님. |
| 2021·2022 최초 3개월 CFS 영업이익, 정정 lineage, public available-at/PIT, 과거 issuer/security mapping | **NOT VERIFIED** | [#412 최신 offline TOC CI #40263193758](https://github.com/kims34/openpilot-opkr/actions/runs/40263193758) 13개 합성 안전 테스트 PASS이나 원본 최초 연결 분기 수치 및 공개시점 승인 아님. 정정본 역채움 금지. |
| KRX 2017–2022 private 원본쌍 SHA 저장 | **기존 저장 무결성 PASS (독립 최신 Railway 재확인 불가)** | 이전 고정 증거 1565/1565 weekday pair, 90 미분류, 12003 zero-activity 외부 차단. 실제 공식 거래일/상태/기업행위/체결가능성/비용·세금은 별도 검증 필요. |
| KRX 격리 offline safety | **PASS (합성 테스트만)** | [#39714369438](https://github.com/kims34/openpilot-opkr/actions/runs/39714369438), [#39714207925](https://github.com/kims34/openpilot-opkr/actions/runs/39714207925) SUCCESS; 2022 14일 후보 comparator는 32개 합성 테스트 PASS. [#39721289545](https://github.com/kims34/openpilot-opkr/actions/runs/39721289545) metadata-only guard SUCCESS. 실제 90일 정확한 공식 분류 및 27종목 거래가능성 **NOT VERIFIED**. |
| 최신 Watchdog | **PASS (소프트웨어 안전검사)** | [#40748772316](https://github.com/kims34/openpilot-opkr/actions/runs/40748772316), 2026-10-29 03:50 KST, 1/1 job SUCCESS; 4+31 offline tests PASS, evidence metadata COMPLETE, `M20 PIT admission: NOT ATTESTED; orders: DISABLED; holdout: NOT AUTHORIZED`. Artifact ZIP SHA-256 `65e4d21c010765e12c26d8444b698613c5fab52925d8b8b785727da921ec7d16` (artifact id 12842188315). |
| Prospective Chronology Anchor | **FAIL (수집 엔드포인트)** | [#40726273259](https://github.com/kims34/openpilot-opkr/actions/runs/40726273259), 2026-10-29 02:07 KST 완료 FAILURE, `HTTP Error 404: Not Found`; validation job SKIPPED. PIT 검증 성공으로 전환 불가. |
| M20 source PIT, official net profitability (NetEV/PF/CAGR/MDD/ES95/99, 집중도, WF robustness) | **NOT VERIFIED / NOT EVALUABLE; NO-GO** | 최초 공시·공식 거래가능성·비용/세금·정확한 available-at 미승인. 수익성 RUN 및 Holdout 접근 금지. |
| Railway 최신 운영 배포/로그, 실제 ORDERING | **NOT VERIFIED (access blocked)** | Railway `list_projects` read-only 시도에서 `User input required but current turn is running in a non-interactive mode`. 운영 값 false를 직접 확인했다고 주장하지 않음. |

## 격리 최적화 독립 검증
- PR #413 최신 [#38508247773](https://github.com/kims34/openpilot-opkr/actions/runs/38508247773) HEAD `f003ef6...`, **6/6 jobs PASS**. 고정 34-case digest `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34`, 결과 동등성 PASS. 정확한 최신 parity log: serial **1.7650 s**, parallel longest **2.7079 s**, ratio **0.6520x** (회귀 구간 오히려 느림). 실제 비용·세금 경제성 검증은 아님. 과거 [#38381997417](https://github.com/kims34/openpilot-opkr/actions/runs/38381997417), [#38382214223](https://github.com/kims34/openpilot-opkr/actions/runs/38382214223) 각 6/6 PASS; [#38419111311](https://github.com/kims34/openpilot-opkr/actions/runs/38419111311) 6/6 PASS, cost suite 실제 9개 테스트 PASS.
- PR #418 최신 [#39111405562](https://github.com/kims34/openpilot-opkr/actions/runs/39111405562) HEAD `2f98401...`, 1/1 SUCCESS, 34-case digest 동일. `RUNTIME_OPT_PARITY` serial **2.3484 s** vs parallel **2.0154 s** = **1.1650x** (test phase only). `ONE_RUNNER_OFFLINE` subprocess wall serial 2.3911 s vs parallel 2.0755 s = 1.1521x; 양 모드 검증 wall 4.4674 s. 전체 CI/공식 백테스트 가속 **NOT VERIFIED**.
- 동일 HEAD [#39111405494](https://github.com/kims34/openpilot-opkr/actions/runs/39111405494) candidate merge source audit SUCCESS이나, [#39111405478](https://github.com/kims34/openpilot-opkr/actions/runs/39111405478) archived manifest guard **FAIL**: `research_v1_runtime_manifest.py` 기대 blob `108f66714602a1bd3ae42c34dcca7c16e38f460b`, 관측 `e0055c66c59398fd4a1158077446d886b54c4e37`. 22 distributions 버전 일치만으로 wheel SHA/OS native/transitive identity 고정 불가. 캐시 승인 **FAIL-CLOSED**.
- 과거 #418 `cost test_count=0`는 의도적인 공격/누락 합성 검증 출력이며 실제 cost suite 부재를 뜻하지 않음. 실제 cost suite 9/9 PASS와 구분. 소프트웨어 동등성/안전성 PASS를 세후 수익성 PASS로 오인하지 말 것.

## 고정 정책과 다음 순서
1. Frozen H5, M20 horizon20/purge20, WF504/126/126, PIT/label/Purged/CPCV/독립 Holdout/Champion/Top3/NO_TRADE, 사전 고정 비용·세금·NetEV·체결·위험·승격 기준을 변경하지 않음. 실패/소비 Holdout 및 Dynamic 사후 재사용 금지.
2. 원본 DART first-edition Q3 CFS 2021/2022 정확한 기간·공표시각·정정 lineage, issuer mapping 독립 원본 SHA 승인 → KRX 공식 과거 거래일/상태·기업행위·실체결 및 비용·세금 승인 → 단일 M20 prereg 경제성 실행 여부 별도 게이트. 승인 전 공식 성능 실험/모델 탐색 금지.
3. 최적화는 합성 offline 안전성만 허용. 캐시는 승인원본·데이터·코드·Frozen·런타임·승인 evidence SHA-256 전부 정확히 맞을 때만 fail-closed. 병렬은 독립 read-only 후처리만, 재학습/자본 전이는 직렬.
4. ORDERING=false 정책 유지; 실제 운영 값은 Railway 권한 확인 전 NOT VERIFIED. 주문·자금이동·권한 변경·Champion 승격은 매번 별도 명시 승인 필요. PR #413/#414/#418 병합, 배포, workflow 보안 차단 우회 금지.
5. Railway는 연결 승인 필요(사용자에게 새 작업을 강요하지 않음). 허용된 독립 문서 쓰기 외 변경 금지. 신규 독립 공식 증거 또는 중대 blocker가 생기기 전 루틴 보고 금지.
