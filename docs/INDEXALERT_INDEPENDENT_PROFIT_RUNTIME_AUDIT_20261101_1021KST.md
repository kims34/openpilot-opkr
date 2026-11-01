# IndexAlert 독립 수익성·격리 최적화 증거 감사 — 2026-11-01 10:21 KST

**최종 게이트: M20 경제성 NOT EVALUABLE / NO-GO; ORDERING=DISABLED; Champion/실주문/자금/권한/병합/배포 불승인.** 이 문서는 별도 감사 브랜치의 신규 문서만 생성한다. 다른 Work의 #412/#413/#414/#418 및 KRX 담당 코드·워크플로·기존 문서는 변경하지 않는다. 이번 실행은 실제 GitHub 브랜치/PR/Actions job 로그 및 Railway production 상태·배포·런타임 로그를 읽기전용 조회했고, 신규 수익률/성능실험·Holdout·재학습·모델 탐색은 하지 않았다. 비교 기준: [직전 09:19 감사](https://github.com/kims34/openpilot-opkr/blob/c581641ac8c50572235e986ad8ac0a61398bc2f4/docs/INDEXALERT_INDEPENDENT_PROFIT_RUNTIME_AUDIT_20261101_0919KST.md).

## 1. 고정 HEAD와 충돌 회피

- 연구 `index-alert-research-v1`: `3b8b7830612a6284d7c7a60628cb527cb741627a`; 개발 `index-alert-position-regen-fix-v1`: `1e6367d2863a86c3470da13d81a955d277eba485`; KRX 담당 `indexalert-krx-pit-source-audit-20261013`: `073d2d49e95f69fb10b943b93e51bb179fb3c698` (GitHub branches API).
- [OpenDART PR #412](https://github.com/kims34/openpilot-opkr/pull/412) `bf3d9514a87c53b1775e22ec9ba7711f6cecc49f`; [최적화 #413](https://github.com/kims34/openpilot-opkr/pull/413) `f003ef6247e16fcc71bd3b1b20cd4904c4d984c0`; [총괄 #414](https://github.com/kims34/openpilot-opkr/pull/414) `f3172a08769721f52e6fd14f82fb60b2d1d571d3` (별도 09:44 KST 증거 문서 커밋); [단일 runner #418](https://github.com/kims34/openpilot-opkr/pull/418) `2f98401cc50a6c6a25808a98516efd5bf0c944ee`.
- [수급 #416](https://github.com/kims34/openpilot-opkr/pull/416) `053de553646fc4765d2616544ca1e8d6bbdde35f`; KRX [#420](https://github.com/kims34/openpilot-opkr/pull/420) `fab3cbbd63a951a4e081f9e7f08c1391ca308581`, [#422](https://github.com/kims34/openpilot-opkr/pull/422) `c14857620973531013799e44625d43080904fd5f`, [#423](https://github.com/kims34/openpilot-opkr/pull/423) `0e38004363cac9fc4475556b3a1c445de9af407f`; [ETF #424](https://github.com/kims34/openpilot-opkr/pull/424) `a4ae98f40b3e6dcaf565cc402679497e42cdabb5`. 조회 시 모두 open/Draft/unmerged.
- 감사 브랜치 `indexalert-independent-profit-runtime-audit-20261031-0425` 쓰기 직전 HEAD `c581641ac8c50572235e986ad8ac0a61398bc2f4`; PR #414 및 전담 브랜치에 쓰지 않음.

## 2. 공식 원본 및 경제성 판정 (증거 범위 한정)

| 검증 대상 | 판정 | 실제 확인과 차단 요인 |
| --- | --- | --- |
| 2021 최초 OpenDART 원본 식별 | LIMITED PASS / original CFS NOT VERIFIED | 이전 [official run #40262282075](https://github.com/kims34/openpilot-opkr/actions/runs/40262282075)와 담당 handoff에 ZIP SHA-256 `8728c0a3c12761ca19e9c6455bea8f1bed0e4c1ebc2e21dc263c373a82a2b625`, 1,728 table shapes, 13 영업손익 후보, strict same-table 3개월 바인딩 0. 이번 회차 원본 ZIP 바이트 독립 재해시 없음. |
| 2022 최초·정정 OpenDART 소스 | SOURCE-ONLY LIMITED PASS | [Actions #38419439742](https://github.com/kims34/openpilot-opkr/actions/runs/38419439742) 2/2 jobs SUCCESS; 최초 ZIP SHA-256 `56639d8f6ebbecf14cd8bc3179d75d01162e2cd7bbdf8f6a3c9479b44f5084bb`, 원본/정정 SGML 15개 후보 및 숫자 인접 시그니처. 최초 정확한 연결 3개월 영업이익 사실값/단위/부호/시각/정정 lineage 승인 아님. |
| 정확한 2021·2022 연결 3개월 Q3, 최초 public available-at, 과거 issuer/security map | NOT VERIFIED / FAIL-CLOSED | 후보 행, ZIP SHA, DART 접수일(date-only), 정정본을 원본 PIT 값으로 대체 불가. 원본/정정과 기간/연결/단위/공표시각을 독립 바이트·원본 메타데이터로 재현해야 함. |
| KRX 2017–2022 private 원본쌍 저장 | HISTORICAL LIMITED PASS | Railway KRX worker deployment `16c93d7c-7cd0-4d84-a327-298d2805376c`, source `1e6367d2863a86c3470da13d81a955d277eba485`; 과거 1,565/1,565 weekday pair 저장 무결성 PASS. 이번 worker 로그 반환 0건으로 신규 원본 SHA 독립 재계산 아님. |
| 공식 시장 캘린더·거래정지/상폐·기업행위·체결가능성·비용/세금 | NOT VERIFIED | 90일 분류, 12,003 zero-activity, 27개 비정상 OHLC veto 미해결. KRX #420/#422/#423 오프라인 날짜 비교는 실제 거래상태/체결 승인 아님. |
| H5/Dynamic/독립 Holdout | NO-GO | H5 실패/소비 Holdout 및 Dynamic 결과 사후 조정/독립 재사용 금지. Frozen Champion/Top3/NO_TRADE 유지. |
| M20 horizon20/purge20 WF504/126/126; 세후 NetEV/PF/CAGR/MDD/ES95/ES99·수익집중도·시점 강건성 | NOT EVALUABLE / NO-GO | 원본 PIT/시장 거래가능성/비용·세금 source admission 불충족으로 실수익성 RUN 미승인. 점추정치·합성 대체값 생성하지 않음. |

[최신 watchdog #41248232339](https://github.com/kims34/openpilot-opkr/actions/runs/41248232339) job `124676072097` SUCCESS이나 원본 로그 `M20 PIT admission: NOT ATTESTED; orders: DISABLED; holdout: NOT AUTHORIZED`. 최신 [Chronology Anchor #41091128151](https://github.com/kims34/openpilot-opkr/actions/runs/41091128151) auto-anchor FAIL/validation SKIPPED, 원본 job `124184971844`의 `/anchor/latest` HTTP 404 지속. Watchdog 성공은 PIT 승인이 아님.

## 3. 격리 최적화 원본 CI / fail-closed 재검증

- [#413 Actions #38381997417](https://github.com/kims34/openpilot-opkr/actions/runs/38381997417), [#38382214223](https://github.com/kims34/openpilot-opkr/actions/runs/38382214223), [#38419111311](https://github.com/kims34/openpilot-opkr/actions/runs/38419111311): 이번 회차 각 6/6 jobs SUCCESS 직접 재조회. 기존 고정 34-case SHA-256 `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34` 및 13 adversarial mocks는 과거 로그 기반 오프라인 동등성 LIMITED PASS. 원본 실행환경 전체 CI/공식 백테스트 성능 승인 아님.
- [#418 초기 #38419649711](https://github.com/kims34/openpilot-opkr/actions/runs/38419649711) 1/1 SUCCESS, synthetic 28개와 34-case parity 기존 증거. serial 2.9656s / concurrent 2.6209s = 1.1315x는 regression phase 한정.
- [#418 후속 #39111405478](https://github.com/kims34/openpilot-opkr/actions/runs/39111405478) job `117628139395` FAILURE 원본 로그: `SourceDriftError: archived blob mismatch: research_v1_runtime_manifest.py expected=108f66714602a1bd3ae42c34dcca7c16e38f460b observed=e0055c66c59398fd4a1158077446d886b54c4e37`.
- 이번 회차 두 HEAD의 실제 `research_v1_runtime_manifest.py` Git blob SHA-1 재조회: #413 `e0055c66c59398fd4a1158077446d886b54c4e37`, #418 `108f66714602a1bd3ae42c34dcca7c16e38f460b`. #413에는 `FORBIDDEN_ELEVATED_RECEIPT_FLAGS`, `os`/`stat`/`ExitStack` 방어 코드가 있고 #418 manifest에는 이 구조가 없음. **#418 병합·캐시 채택 FAIL**. 승인원본·데이터·코드·Frozen 정책·런타임/승인 SHA-256 일치 및 파일경로/권한/교체 경쟁 fail-closed 없이는 캐시 금지. 독립 읽기전용 후처리 외 병렬화 금지.

## 4. Railway production 실측

- Project `d1c1a050-b7d6-41ce-b300-13c20f82a20a`, production env `83d5840b-270e-4d3f-a941-a37fd4a55ff7`. `describe_environment` 및 `describe_service`: staged=null / 변경 0. **별도** `environment_status`: staged patch `e113dacb-6705-4416-9997-dc694539d382`, `changes=[]` 지속. 서로 다른 API 응답 불일치; 운영 적용/승인 근거 아님.
- `indexalert-pit-rebuild` latest deploy `8b354fc1-cfb2-4ef0-863e-67f7f5dda2b5` SUCCESS; 최신 반환 log `2026-10-31T14:46:01.190084194Z` (23:46:01 KST) `FAIL_CLOSED`, `COMMON_OHLC_NONPOSITIVE`, 27/803 common stock, 27 zero-volume/value, `source_failure_session=2026-09-28`, all independent admission false, `ordering=DISABLED`, live/funds/permissions false.
- `indexalert-runtime` latest deployment `eaaa9f67-b9f2-41d2-832c-7d6fad9b9b00` SUCCESS, newest returned log `2026-11-01T01:21:43.089532931Z` (10:21:43 KST), 이는 지수 알림 런타임이지 M20 투자 승인 아님.
- `indexalert-kiwoom-real-readonly` latest deploy `a77fb922-b679-4d88-92c4-03054ec579cd` SUCCESS, source deployment commit `85bb6fd10bcc9ff2b14abe1c774f0d99f8eb84ab`; health는 online 표시와 동시에 `running=0, crashed=1, total=1`. SUCCESS 배포와 실제 broker 연결/가동 성공은 다름.
- `indexalert-krx-historical-worker` SUCCESS, 최신 반환 로그 없음; 다른 오프라인 서비스/푸시/backend 경고는 수익성 게이트 승인 근거 아님.

## 5. 안전한 다음 단계 / 변경 금지

1. OpenDART 전담이 원본 ZIP/SGML과 최초 시각, 2021·2022 CFS Q3 3개월 fact·정정 lineage 및 historical mapping을 독립적으로 증명할 때까지 M20 입장 차단.
2. KRX 전담이 공식 calendar/상태·기업행위·과거 종목별 거래가능성/체결·비용/세금 원본 SHA를 입증하고 90/27/12,003 quarantines를 해결할 때까지 시장 admission 차단.
3. 최적화 전담은 #418의 manifest drift 및 #413 대비 권한·경로·파일 교체 fail-closed 동등성부터 합성 오프라인만 검증. 본 감사는 타 전담 코드 수정·workflow 변경·CI rerun 하지 않음.
4. H5 Frozen, M20 horizon20/purge20, WF504/126/126, PIT/Purged/CPCV/독립 Holdout/Champion/Top3/NO_TRADE, 고정 비용·세금·승격 조건 변경 금지. `ORDERING=false` 유지. 사용자 명시 승인 없이 주문·자금·인증/권한·승격·병합·배포 없음.

**이번 회차 결론:** 새 공식 PIT/수익성 승인 없음. 독립 소스·CI·Railway 재조회에서 기존 차단 유지. 새 성능실험 없음.
