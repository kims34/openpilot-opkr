# IndexAlert 독립 수익성·격리 최적화 감사 — 2026-11-01 17:21 KST

**결정: M20 NOT EVALUABLE / NO-GO, PIT NOT VERIFIED, ORDERING=DISABLED, #418 채택 NO-GO.** 본 기록은 GitHub branch/PR API, 실제 Actions jobs 및 job logs, 소스 blob SHA, Railway production 배포/로그/복제본의 이번 회차 읽기전용 교차검증이다. 공개 원본 공시 ZIP/민감 종목 자료는 다운로드하거나 재해시하지 않았고, 경제성/실데이터 백테스트, Holdout, 주문, 운영 변경, merge, workflow 변경은 수행하지 않았다.

## 1. HEAD와 변경 중복 격리

- 연구 `index-alert-research-v1` `3b8b7830612a6284d7c7a60628cb527cb741627a`; 개발 `index-alert-position-regen-fix-v1` `1e6367d2863a86c3470da13d81a955d277eba485`; KRX 담당 `indexalert-krx-pit-source-audit-20261013` `073d2d49e95f69fb10b943b93e51bb179fb3c698` (GitHub branches API 직접 조회).
- 전부 open/Draft/unmerged: [#412](https://github.com/kims34/openpilot-opkr/pull/412) `bf3d9514a87c53b1775e22ec9ba7711f6cecc49f`; [#413](https://github.com/kims34/openpilot-opkr/pull/413) `f003ef6247e16fcc71bd3b1b20cd4904c4d984c0`; [#414](https://github.com/kims34/openpilot-opkr/pull/414) `86af551a02329fbd8c2fd30c1572cf49a7a3af98`; [#416](https://github.com/kims34/openpilot-opkr/pull/416) `053de553646fc4765d2616544ca1e8d6bbdde35f`; [#418](https://github.com/kims34/openpilot-opkr/pull/418) `2f98401cc50a6c6a25808a98516efd5bf0c944ee`; KRX [#420](https://github.com/kims34/openpilot-opkr/pull/420) `fab3cbbd63a951a4e081f9e7f08c1391ca308581`, [#422](https://github.com/kims34/openpilot-opkr/pull/422) `c14857620973531013799e44625d43080904fd5f`, [#423](https://github.com/kims34/openpilot-opkr/pull/423) `0e38004363cac9fc4475556b3a1c445de9af407f`, [#424](https://github.com/kims34/openpilot-opkr/pull/424) `a4ae98f40b3e6dcaf565cc402679497e42cdabb5`.
- #414 이전 `1bcf0c72f01c0faeb3b7c1cd7a5570bd87f679dd` 대비 정확히 1 commit 전진, 새 독립 문서 `docs/INDEXALERT_PROFITABILITY_INDEPENDENT_GATE_20261101_1646KST_AUTOMATION11.md` 26줄만 추가(비교 API). 총괄 원문 `docs/INDEXALERT_PROFITABILITY_INTEGRATION_GATE_2026-10-13.md` blob SHA-1 `984c933651f39f1ee9e26a1d7ac3893aaa5335be`. 담당 #414 파일 및 코드 수정 없음.

## 2. 원본/PIT/시장/경제성 증거 매트릭스

| Gate | 이번 판정 | 검증 범위와 잔여 blocker |
| --- | --- | --- |
| OpenDART 2022 최초 원본 | **과거 공식 ZIP SHA 기록 제한적 PASS; 의미·시점 NOT VERIFIED** | [#38419439742](https://github.com/kims34/openpilot-opkr/actions/runs/38419439742) 2/2 jobs SUCCESS. 최초 ZIP SHA-256 `56639d8f6ebbecf14cd8bc3179d75d01162e2cd7bbdf8f6a3c9479b44f5084bb`, 정정 ZIP `606be9d03928808f0a2a05f052444587bd2457bdef7a47a8f4bff3d2ea098a30`; 후보 15/15 행 및 인접 숫자 시그니처 일치. 이는 원본 CFS 3개월 영업이익 값/기간·정정 cell lineage·first public available-at 인증이 아님. |
| OpenDART 2021 최초 원본 | **과거 원본 출처 제한적 PASS; 분기 CFS NOT VERIFIED** | [#40262558066](https://github.com/kims34/openpilot-opkr/actions/runs/40262558066) 2/2 jobs SUCCESS 재조회; 기존 공식 로그의 ZIP SHA-256 `8728c0a3c12761ca19e9c6455bea8f1bed0e4c1ebc2e21dc263c373a82a2b625`. 독립 재해시 미수행. 2021 최초 standalone 3개월 연결 값과 2022 최초 비교열을 동일 시점 데이터로 오인 금지. |
| 과거 issuer/security mapping, 공시 vintage/정정 | **NOT VERIFIED** | 최초 원본/정정 전후 공개시점, 종목·기업 과거 매핑 및 원본 기간 cell binding 미입증. 정정본 역채우기 금지. |
| KRX 원본 저장 | **과거 로그 범위 RAW STORAGE PASS** | 2017–2022 weekday 1,565/1,565 원본쌍 저장 기록; production KRX worker 배포 `16c93d7c-7cd0-4d84-a327-298d2805376c` SUCCESS. 이번 Railway deploy-log 반환 0건, private volume 신규 재검증 아님. |
| KRX 공식 달력/거래가능성/기업행위/체결 | **NOT VERIFIED / veto** | 불확실 90일, zero-activity 12,003건, prospective nonpositive OHLC 27/803, 과거 거래정지/상폐/기업행위/수량/실체결 불충족. #420/#422/#423 offline candidate comparator는 공식 승인 아님. |
| 수수료·세금·슬리피지/NetEV/PF/CAGR/MDD/ES95/ES99/수익 집중도/시점 강건성/연간 위험조정 순수익 | **NOT EVALUABLE / NO-GO** | PIT-admitted executable ledger 및 비용/세금 독립 입증 부재. M20 경제성 RUN 금지. H5 실패·소비 Holdout 및 Dynamic 결과 독립 재사용 금지. |

- [Watchdog #41264126871](https://github.com/kims34/openpilot-opkr/actions/runs/41264126871) job `124723240979` SUCCESS (2026-11-01 02:11 UTC); 실제 로그 `M20 PIT admission: NOT ATTESTED; orders: DISABLED; holdout: NOT AUTHORIZED`. [Chronology #41091128151](https://github.com/kims34/openpilot-opkr/actions/runs/41091128151) auto-anchor HTTP 404 FAIL, validation SKIPPED. Watchdog 성공은 원본 시점 승인과 별개.
- Frozen H5/Champion, M20 horizon20/purge20, WF504/126/126, Purged/CPCV/독립 Holdout/Top3/NO_TRADE, 기존 비용·위험·승격 정책 불변.

## 3. 최적화 격리 CI 및 소스 SHA 교차 검증

- #413 [38381997417](https://github.com/kims34/openpilot-opkr/actions/runs/38381997417), [38382214223](https://github.com/kims34/openpilot-opkr/actions/runs/38382214223), [38419111311](https://github.com/kims34/openpilot-opkr/actions/runs/38419111311), **각 6/6 jobs SUCCESS**. 최신 HEAD의 [38508247773](https://github.com/kims34/openpilot-opkr/actions/runs/38508247773)도 **6/6 SUCCESS**; 해당 exact-parity job 로그의 pinned 34-case SHA-256 `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34`, 직렬 1.765초 vs parallel longest 2.7079초, **이 CI 회차의 test-phase 속도비 0.652x(병렬이 더 느림)**. 이전 13 adversarial mocks는 과거 CI에 한정된 PASS. end-to-end/실백테스트 가속 미입증.
- #418 [38419649711](https://github.com/kims34/openpilot-opkr/actions/runs/38419649711) 1/1 SUCCESS, 고정 34-case 동일, serial 2.9656초 vs parallel 2.6209초=1.1315x (회귀 phase 한정). **현재 #418 HEAD**에서 2026-10-18 [39111405562](https://github.com/kims34/openpilot-opkr/actions/runs/39111405562) one-runner SUCCESS, 실제 34-case 로그 serial 2.3911초 vs parallel 2.0755초(약 1.152x); [39111405494](https://github.com/kims34/openpilot-opkr/actions/runs/39111405494) candidate source audit SUCCESS. 그러나 **같은 HEAD의 [39111405478](https://github.com/kims34/openpilot-opkr/actions/runs/39111405478) archived replay FAIL**; `SourceDriftError` expected `108f66714602a1bd3ae42c34dcca7c16e38f460b` observed `e0055c66c59398fd4a1158077446d886b54c4e37`.
- 두 blob을 실제 소스 fetch로 직접 확인: `research_v1_runtime_manifest.py` #418 SHA-1 `108f66714602a1bd3ae42c34dcca7c16e38f460b`, #413 SHA-1 `e0055c66c59398fd4a1158077446d886b54c4e37`. #413은 `O_NOFOLLOW`/directory-fd open, inode/device 재검사, explicit holdout/live flag false 요구; #418은 `Path.is_symlink` 후 `Path.open`과 `True`만 거부하는 약한 검사. **정책/경로 보호 동등성 FAIL/채택 NO-GO**, 일부 성공한 candidate/runner CI로 archived drift를 덮지 않음.
- 캐시는 독립 승인 source+data+code+Frozen policy+runtime/receipt SHA-256 전체 일치에만 fail-closed. 읽기전용 독립 후처리만 병렬화, 재학습/자본 transition 병렬화 금지. workflow 수정 보안 차단 우회 금지.

## 4. Railway production (read-only)

- 프로젝트 `d1c1a050-b7d6-41ce-b300-13c20f82a20a`, environment `83d5840b-270e-4d3f-a941-a37fd4a55ff7`. `indexalert-pit-rebuild` 배포 `8b354fc1-cfb2-4ef0-863e-67f7f5dda2b5` SUCCESS, 1/1 replica running. 최신 반환 PIT 로그 **2026-10-31 14:46:01 UTC (23:46:01 KST)**: `FAIL_CLOSED`, `COMMON_OHLC_NONPOSITIVE`, 27/803, `independent_source_admission_verified=false`, `independent_chronology_admission_verified=false`, `independent_model_admission_verified=false`, `ordering=DISABLED`, `live_order_authorized=false`. 이것이 현재 시각의 새 거래일 원본 검증은 아님.
- `indexalert-runtime` SUCCESS 1/1 running, 로그는 **2026-11-01 08:20 UTC (17:20 KST)**까지 반환. 별도 지수 알림 운영 로그이며 M20 PIT/수익성 승인 아님.
- `indexalert-kiwoom-real-readonly` 배포 `a77fb922-b679-4d88-92c4-03054ec579cd` SUCCESS지만 environment-status는 **0 running / 1 crashed replica**를 동시에 표시. 서비스 온라인 문자열이나 배포 성공만으로 브로커 연결/인증 성공을 주장할 수 없음.
- `describe_environment` 및 `get_staged_changes`는 `staged=null`; `environment_status.pendingWork`는 `patch:e113dacb-6705-4416-9997-dc694539d382` staged, `changes=[]` 반환. **서로 다른 read API 불일치**, 배포·accept-deploy·patch 변경 금지. `indexalert-backend`, `indexalert-push`, `db-query-readonly`은 environment_status offline으로 반환; 본 감사의 운영 변경 권한/증거 아님.

## 5. 다음 증거 순서 및 제한

1. OpenDART 담당: 2021·2022 original-filing exact CFS 3개월 기간/수치/비교열/정정 lineage와 첫 public available-at를 독립 원본으로 attestation, 역사적 issuer/security mapping.
2. KRX 담당: 공식 시장 달력과 불확실 90일, 27 invalid OHLC 및 zero-activity, 거래정지·기업행위·체결가능성, 세금·비용 증거를 실제 원본/CI로 확정.
3. 최적화 격리: #418 manifest blob drift와 #413 대비 no-follow/inode/flag fail-closed 차이 해결 및 전체 dependency/evidence SHA 검증. 승인된 합성 오프라인 테스트만; workflow 쓰기 차단 시 우회 금지.
4. 독립 원본/PIT/거래가능성 승인 전 **M20 실수익률·새 모델 탐색·경제성 테스트·Holdout·Champion 승격·실거래·배포·PR 병합 모두 NO-GO**. 사용자 승인 없이는 자금/계좌/권한/주문 변경 불가.

**이번 변경:** 이 독립 감사 문서만 기록. 다른 Work의 PR, 코드, 워크플로, Railway, 운영 권한/자금은 변경하지 않음.
