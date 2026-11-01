# IndexAlert 독립 수익성·격리 최적화 증거 감사 — 2026-11-01 11:24 KST

**게이트: M20 세후 경제성 NOT EVALUABLE / NO-GO. 주문 `ORDERING=false` / 운영 로그 `DISABLED`. Frozen H5·Champion·Top3·NO_TRADE 유지.** 공식 시장 백테스트, Holdout 재사용, 모델 탐색·재학습, 수익률 추정, 배포·병합·주문·자금·인증/권한·승격을 실행하지 않았다. 본 감사는 타 전담 작업을 건드리지 않는 독립 감사 브랜치의 신규 문서 1개에 한정한다. 비교 기준 [10:21 KST 직전 감사](https://github.com/kims34/openpilot-opkr/blob/9dff585cd62879d71e2ea353a668314f9897f47f/docs/INDEXALERT_INDEPENDENT_PROFIT_RUNTIME_AUDIT_20261101_1021KST.md).

## 1. 실제 최신 GitHub 원본 HEAD·CI 조회

- GitHub REST branches: 연구 `index-alert-research-v1` **`3b8b7830612a6284d7c7a60628cb527cb741627a`**, 개발 `index-alert-position-regen-fix-v1` **`1e6367d2863a86c3470da13d81a955d277eba485`**, KRX 담당 `indexalert-krx-pit-source-audit-20261013` **`073d2d49e95f69fb10b943b93e51bb179fb3c698`**. 직전 감사와 동일.
- 모두 open/Draft/unmerged: [OpenDART #412](https://github.com/kims34/openpilot-opkr/pull/412) `bf3d9514a87c53b1775e22ec9ba7711f6cecc49f`; [최적화 #413](https://github.com/kims34/openpilot-opkr/pull/413) `f003ef6247e16fcc71bd3b1b20cd4904c4d984c0`; [총괄 #414](https://github.com/kims34/openpilot-opkr/pull/414) **`9391a12e43058f3d11ea919dc64e263c784ea9ef`** (직전 `f3172a08769721f52e6fd14f82fb60b2d1d571d3`에서 문서 전용 커밋; 변경 파일 `docs/INDEXALERT_INDEPENDENT_PROFITABILITY_AUDIT_2026_11_01_1045_KST.md`); [수급 #416](https://github.com/kims34/openpilot-opkr/pull/416) `053de553646fc4765d2616544ca1e8d6bbdde35f`; [단일 runner #418](https://github.com/kims34/openpilot-opkr/pull/418) `2f98401cc50a6c6a25808a98516efd5bf0c944ee`; KRX [#420](https://github.com/kims34/openpilot-opkr/pull/420) `fab3cbbd63a951a4e081f9e7f08c1391ca308581`, [#422](https://github.com/kims34/openpilot-opkr/pull/422) `c14857620973531013799e44625d43080904fd5f`, [#423](https://github.com/kims34/openpilot-opkr/pull/423) `0e38004363cac9fc4475556b3a1c445de9af407f`; ETF [#424](https://github.com/kims34/openpilot-opkr/pull/424) `a4ae98f40b3e6dcaf565cc402679497e42cdabb5`.
- [최신 Watchdog Actions #41264126871](https://github.com/kims34/openpilot-opkr/actions/runs/41264126871), job `124723240979`, 2026-11-01 02:11 UTC (11:11 KST) **SUCCESS**, checkout 연구 SHA `3b8b...`; 원본 로그: `M20 PIT admission: NOT ATTESTED; orders: DISABLED; holdout: NOT AUTHORIZED`. 해당 job artifact ZIP SHA-256 **`f30092454e52fb715a4cbba3631dbf2ecb8b4e9d57261e9bba942477908064b6`**. 성공은 원본 PIT 승인이 아니라 안전 감시 성공.
- [Chronology Anchor #41091128151](https://github.com/kims34/openpilot-opkr/actions/runs/41091128151), job `124184971844` FAILURE, validation SKIPPED; 실제 로그 HTTP **404 Not Found**. 독립 chronology proof 미승인.

## 2. 공식 원본·PIT·거래가능성·경제성 게이트

| 항목 | 판정 | 독립 근거와 미해결 조건 |
| --- | --- | --- |
| 2021 최초 OpenDART ZIP/후보 | HISTORICAL LIMITED PASS, FACT NOT VERIFIED | 직전 감사의 2021 ZIP SHA-256 `8728c0a3c12761ca19e9c6455bea8f1bed0e4c1ebc2e21dc263c373a82a2b625`, 1,728 tables / 13 candidates / strict 3-month same-table binding 0. 이번 회차 원본 바이트 재해시 없음. |
| 2022 최초·정정 OpenDART ZIP/SGML | HISTORICAL SOURCE-ONLY LIMITED PASS | [Actions #38419439742](https://github.com/kims34/openpilot-opkr/actions/runs/38419439742) 두 jobs SUCCESS 원본 재조회. 최초 ZIP SHA-256 `56639d8f6ebbecf14cd8bc3179d75d01162e2cd7bbdf8f6a3c9479b44f5084bb`는 기존 증거. 15개 후보와 숫자 인접 시그니처는 실제 3개월 CFS fact·최초 공개 시각의 증명이 아님. |
| 2021·2022 Q3 최초 연결 3개월 영업이익, 수정 공시 lineage, 정확한 available-at, 과거 기업·종목 매핑 | **NOT VERIFIED** | 원본 edition·CFS IS/CIS context·July–Sept standalone period·단위/부호·first-public timestamp·correction chronology를 동일 원본에서 증명해야 함. |
| KRX 2017–2022 private 1,565/1,565 weekday pairs | HISTORICAL STORAGE-ONLY LIMITED PASS | Railway historical-worker 원본 배포 `16c93d7c-7cd0-4d84-a327-298d2805376c`; 이번 로그 반환 0건으로 SHA 독립 재계산 아님. |
| KRX 공식 거래일·상태·기업행위·체결가능성·비용·세금 | **NOT VERIFIED** | 90 calendar/source gaps, 12,003 zero-activity 격리, 27 비정상 OHLC veto. 오프라인 캘린더 후보 비교는 공식 거래상태 증명이 아님. |
| H5/Dynamic/독립 Holdout | **NO-GO** | 기존 실패·소비 Holdout 및 Dynamic 결과 사후 조정·독립 재사용 금지. |
| M20 horizon20/purge20, WF504/126/126, 세후 NetEV/PF/CAGR/MDD/ES95/99·집중도·시간 강건성 | **NOT EVALUABLE / NO-GO** | source/PIT/시장/비용 admission 불충족; 공식 수익률·새 성능실험·경제성 RUN 금지. |

## 3. 격리 최적화 CI·코드 SHA 재검증

- [#413 #38381997417](https://github.com/kims34/openpilot-opkr/actions/runs/38381997417), [#38382214223](https://github.com/kims34/openpilot-opkr/actions/runs/38382214223), [#38419111311](https://github.com/kims34/openpilot-opkr/actions/runs/38419111311): 각각 **6/6 jobs SUCCESS** 원본 jobs 재조회. 기존 34-case 결과 SHA-256 `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34`, 13 adversarial mocks는 합성 오프라인 동등성 범위만 LIMITED PASS.
- [#418 #38419649711](https://github.com/kims34/openpilot-opkr/actions/runs/38419649711) 1/1 SUCCESS. 로그 34-case SHA 일치, serial 2.9656초 / parallel group 2.6209초 = regression phase **1.1315x**; 전체 CI/실제 경제성 백테스트 속도는 NOT VERIFIED. [#418 HEAD workflow runs](https://github.com/kims34/openpilot-opkr/pull/418/checks): #39111405478 FAILURE, #39111405494 candidate non-admitting SUCCESS, #39111405562 wall-time probe SUCCESS. 성공한 다른 작업은 실패한 provenance gate를 상쇄하지 못함.
- [#418 #39111405478](https://github.com/kims34/openpilot-opkr/actions/runs/39111405478), job `117628139395` 원본 로그 `SourceDriftError`: archived manifest expected blob SHA-1 **`108f66714602a1bd3ae42c34dcca7c16e38f460b`**, observed **`e0055c66c59398fd4a1158077446d886b54c4e37`**.
- 실제 두 브랜치의 `research_v1_runtime_manifest.py` Git blob 재조회: #413 `e0055c66c59398fd4a1158077446d886b54c4e37` (8,590 bytes); #418 `108f66714602a1bd3ae42c34dcca7c16e38f460b` (4,204 bytes). #413은 optional elevated authority flags를 literal False로 제한하고, path-component no-follow, fd identity/mtime/ctime, batch recheck를 갖지만 #418은 `Path.is_file`/leaf `is_symlink`와 일반 open, literal True만 거절한다. 따라서 #418은 #413의 fail-closed 보호와 **동등하지 않으며 채택 FAIL**. #418 archived source gate는 직접 import만 고정하고 transitive closure를 보장하지 않는다고 자체 명시.
- 캐시는 독립 인증된 original/source/PIT·데이터·계산코드·Frozen 정책·런타임/승인 evidence SHA-256의 전부가 일치할 때만 검토 가능. 승인 전에는 생성·복원 불가; 의존적 학습/capital transition 병렬화 금지, 독립 read-only 후처리만 검토. 신규 테스트 실행이나 workflow 변경 없음.

## 4. Railway production 실제 조회

- project `d1c1a050-b7d6-41ce-b300-13c20f82a20a`, environment `83d5840b-270e-4d3f-a941-a37fd4a55ff7`. `describe_environment`는 **staged=null**, `environment_status`는 **staged patch `e113dacb-6705-4416-9997-dc694539d382` / changes=[]**로 API간 상태 불일치 지속. 배포/패치 적용 금지.
- PIT service deployment `8b354fc1-cfb2-4ef0-863e-67f7f5dda2b5` SUCCESS이지만 최신 반환 runtime `2026-10-31T14:46:01.190084194Z` (23:46:01 KST), session `2026-10-31`, source failure `2026-09-28`, `COMMON_OHLC_NONPOSITIVE`, **27/803** common stock rows, zero volume/value 27, `independent_source_admission_verified=false`, `independent_chronology_admission_verified=false`, `ordering=DISABLED`, `FAIL_CLOSED`.
- indexalert-runtime deployment `eaaa9f67-b9f2-41d2-832c-7d6fad9b9b00` SUCCESS; 최신 반환 알림 log `2026-11-01T02:23:45.720365244Z` (11:23:45 KST). **지수 알림 로그이지 M20 승인 증거 아님**.
- KRX historical-worker deployment `16c93d7c-7cd0-4d84-a327-298d2805376c` SUCCESS / 이번 deploy log 0건. Kiwoom real read-only deployment `a77fb922-b679-4d88-92c4-03054ec579cd` SUCCESS 표시이나 `environment_status`는 **online + running=0/crashed=1/total=1**로 실제 가동 미확인. 타 서비스의 offline/critical도 독립 M20 source admission 아님.

## 5. 다음 단계와 변경 경계

OpenDART 전담의 original 2021/2022 3개월 CFS fact+first public instant+correction lineage와 과거 issuer/security proof, KRX 전담의 공식 historical trade-state/corporate-action/fill/cost/tax 증거가 각각 독립 원본 SHA로 승인되기 전까지 M20 경제성 RUN을 차단한다. 최적화 전담은 #418 manifest SHA mismatch 및 #413 대비 권한·경로·교체 fail-closed 동등성을 오프라인 합성 테스트에서 해결해야 한다. **이번 감사의 새로운 공식 원본 승인 없음.** Frozen H5, M20 20/20, WF504/126/126, PIT/Purged/CPCV/독립 Holdout/Champion/Top3/NO_TRADE, 세후 비용·위험·승격 규칙 변경 없음. 운영 배포/PR #413/#414/#418 병합, 주문, 자금, 계정·인증·권한, Champion 승격 없음.
