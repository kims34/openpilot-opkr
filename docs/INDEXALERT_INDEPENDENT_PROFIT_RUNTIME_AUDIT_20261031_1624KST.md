# IndexAlert 독립 수익성·최적화 감사 — 2026-10-31 16:24 KST

**범위:** GitHub/Railway 원본을 읽기전용 확인한 독립 증거 스냅샷. 이 문서는 신규 PIT 승인, 공식 수익률 측정, 실주문, 코드·워크플로 변경, 병합 또는 배포를 승인하지 않는다. 원시 시장 데이터·종목별 비공개 값·계좌정보·인증정보 없음.

## 읽기전용 GitHub HEAD / CI 원본

- 연구 `index-alert-research-v1`: `3b8b7830612a6284d7c7a60628cb527cb741627a`; 개발 `index-alert-position-regen-fix-v1`: `1e6367d2863a86c3470da13d81a955d277eba485` (GitHub branches API).
- PR #414 독립 감사 기록 **쓰기 전 HEAD** `8f163004477dc8807948af0fc847c91091f3b741`; 고정 총괄 게이트 문서 `docs/INDEXALERT_PROFITABILITY_INTEGRATION_GATE_2026-10-13.md` blob SHA-1 `984c933651f39f1ee9e26a1d7ac3893aaa5335be`. 이 감사 기록은 기존 총괄 문서를 수정하지 않는다.
- Draft PR #412 OpenDART HEAD `bf3d9514a87c53b1775e22ec9ba7711f6cecc49f`; #413 격리 최적화 `f003ef6247e16fcc71bd3b1b20cd4904c4d984c0`; #418 독립 단일 runner `2f98401cc50a6c6a25808a98516efd5bf0c944ee`; #420 KRX 격리 `fab3cbbd63a951a4e081f9e7f08c1391ca308581`; #422 2021 KRX 달력 `c14857620973531013799e44625d43080904fd5f`; #423 2022 KRX 달력 `0e38004363cac9fc4475556b3a1c445de9af407f`. #404 KRX 원본 SHA 감사 PR은 closed; 이 사실은 시장 PIT 승인과 다르다.
- 최신 read-only [watchdog Actions 41178674319](https://github.com/kims34/openpilot-opkr/actions/runs/41178674319): 2026-10-31 06:57:48–06:58:04 UTC (15:57–15:58 KST), 1/1 job SUCCESS. 원본 job `124471405513` 로그에서 4 watchdog 및 31 research-governance synthetic tests PASS, **`M20 PIT admission: NOT ATTESTED; orders: DISABLED; holdout: NOT AUTHORIZED`**. 성공은 승인증명 아님.
- OpenDART [Actions 38419439742](https://github.com/kims34/openpilot-opkr/actions/runs/38419439742): 2/2 jobs SUCCESS, 원본/정정 SGML 영업손익 후보 15개 숫자 인접 시그니처 일치. 2021·2022 최초 **연결 3개월** 영업이익 사실값·정확한 공개시점/기간/정정 lineage 및 과거 기업·종목 매핑은 **NOT VERIFIED**. 후보 행 동등성/원본 ZIP 일치만 제한적 PASS; 수정본으로 원본 시점 역채우기 금지.
- PR #413 [Actions 38381997417](https://github.com/kims34/openpilot-opkr/actions/runs/38381997417), [38382214223](https://github.com/kims34/openpilot-opkr/actions/runs/38382214223): 기존 6/6 jobs 및 고정 34-case SHA-256 `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34` 동등성 제한적 PASS. 교정 [38419111311](https://github.com/kims34/openpilot-opkr/actions/runs/38419111311) 6/6 및 13 adversarial mocks; PR #418 [38419649711](https://github.com/kims34/openpilot-opkr/actions/runs/38419649711) 1/1 및 합성 검증. 기존 regression-phase 직렬 2.9656s vs 병렬 2.6209s = 1.1315x, 전체 CI/공식 백테스트 wall-clock 향상은 **NOT VERIFIED**.
- [실패 Actions 39111405478](https://github.com/kims34/openpilot-opkr/actions/runs/39111405478) job `117628139395`: `SourceDriftError: archived blob mismatch: research_v1_runtime_manifest.py expected=108f66714602a1bd3ae42c34dcca7c16e38f460b observed=e0055c66c59398fd4a1158077446d886b54c4e37`. 원본 PR #413 manifest blob `e0055c66c59398fd4a1158077446d886b54c4e37` (188 lines), PR #418 blob `108f66714602a1bd3ae42c34dcca7c16e38f460b` (103 lines). **고정 원본 동등성 FAIL**. 정확한 wheel hashes 및 OS-native 의존성 identity 미검증.
- 독립 소스 코드 대조: #413 manifest는 receipt `holdout_access_authorized` 및 `live_orders_authorized`의 **명시적 False**를 요구하고 `O_NOFOLLOW`·`fstat`·후속 identity 재검사를 수행. #418은 `is True`일 때만 차단하여 누락/문자열 등 비정상 값에 대해 동일한 fail-closed 동등성을 제공하지 않고, #413과 같은 directory no-follow 및 batch identity 재검사가 없음. **안전 동등성 FAIL**. 이는 실제 권한 상승/실주문 관측 증거가 아니며 임의 SHA 교체로 해결하지 않는다.
- [Prospective Chronology Anchor Actions 41091128151](https://github.com/kims34/openpilot-opkr/actions/runs/41091128151) auto-anchor job `124184971844` FAIL: `/anchor/latest` HTTP 404, validation job skipped. PIT 독립 chronology 증명 없음.

## Railway production 직접 조회 (2026-10-31)

- Project `d1c1a050-b7d6-41ce-b300-13c20f82a20a`; environment `83d5840b-270e-4d3f-a941-a37fd4a55ff7`. `list_deployments`, `environment_status`, `get_logs`, `describe_environment`, `get_staged_changes` 모두 읽기전용.
- KRX historical worker deployment `16c93d7c-7cd0-4d84-a327-298d2805376c` SUCCESS, commit `1e6367d2863a86c3470da13d81a955d277eba485`. 과거 공식 원본 저장 2017–2022 **1,565/1,565 weekday pairs** 무결성 제한적 PASS(기존 원본 감사 범위). 공식 휴장/거래정지/상장폐지/기업행위/체결가능성/거래비용·세금, 90일 불확실 세션 및 zero-activity 12,003건은 승인되지 않음.
- PIT rebuild deployment `8b354fc1-cfb2-4ef0-863e-67f7f5dda2b5` SUCCESS, 1 running replica. 실제 조회된 최신 deploy log **2026-10-30 14:46:37.348994251 UTC = 23:46:37 KST**, `COMMON_OHLC_NONPOSITIVE`, common-stock 803 중 27 nonpositive/zero-volume-value, `status=FAIL_CLOSED`, `independent_source_admission_verified=false`, `independent_model_admission_verified=false`, `independent_chronology_admission_verified=false`, `ordering=DISABLED`, `real_orders_authorized=false`, `session_manifest_sha256=null`. 이후 새 PIT 통과 로그는 반환되지 않음.
- `indexalert-runtime` deployment `eaaa9f67-b9f2-41d2-832c-7d6fad9b9b00` SUCCESS, 1 running replica; 감시 로그는 **2026-10-31 07:23:46 UTC = 16:23:46 KST**까지 확인. 감시 시세가 원본 PIT/Alpha 승인이라는 뜻은 아님.
- Kiwoom real readonly deployment `a77fb922-b679-4d88-92c4-03054ec579cd` SUCCESS 표기와 `state=online`에도 replica `running=0, crashed=1, total=1` 불일치. 최신 deploy log에는 2026-10-29 container startup만 있으며 정상 broker 인증 증명 없음. `indexalert-backend`, `indexalert-push`, `db-query-readonly` health는 offline.
- **Railway 조회 간 불일치:** `environment_status.pendingWork`는 2026-10-29 생성 `patch:e113dacb-6705-4416-9997-dc694539d382`를 staged/changes=[]로 표시하나, `get_staged_changes.staged=null`, `describe_environment.staged=null`이며 변경 리소스 0. 실효성 있는 staged config라고 단정하지 않고 **NOT VERIFIED / API-view inconsistency**로 기록; 변경 적용하지 않음.

## 엄격한 독립 판정

| Gate | Result |
| --- | --- |
| KRX 1,565 private stored weekday raw-pair SHA integrity | **PASS, storage-only bounded scope** |
| OpenDART source ZIP / 15 SGML candidate signatures | **PASS, limited candidate/source scope only** |
| 2021/2022 first-filed 3-month CFS operating income / period / exact public available-at / correction lineage | **NOT VERIFIED** |
| historical issuer/security mapping, official KRX sessions/halts/actions, fillability/lot/depth, fees/taxes | **NOT VERIFIED** |
| PR #413 fixed 34-case offline parity | **PASS, synthetic/archived scope only** |
| PR #418 manifest blob pin / relative fail-closed equivalence | **FAIL** |
| complete CI / official approved backtest speedup, cache approval SHA-256 bundle | **NOT VERIFIED** |
| M20 after-fee/tax NetEV/PF/CAGR/MDD/ES95/ES99, concentration, date robustness, annual risk-adjusted net return | **NOT EVALUABLE; RUN NO-GO** |

**Frozen policy unchanged:** H5 failed/consumed Holdout and Dynamic results are not independent reusable evidence. M20 horizon20/purge20, WF504/126/126, PIT/labels/Purged/CPCV/independent Holdout/Champion/Top3/NO_TRADE, risk/cost/tax/approval thresholds remain frozen. Cache must require independently approved source+data+code+policy+runtime+evidence SHA-256 and fail closed; only read-only independent postprocessing may parallelize, never dependent retraining/capital transition. No new M20 economic experiment, market returns, model search, Champion promotion, live orders, money movement, account changes, PR merge or deployment. `ORDERING=false` remains mandatory.

**Next independent gates:** OpenDART specialist must attest original 2021/2022 3-month CFS facts and exact first-public available-at or explicit missingness; KRX specialist must attest official historic tradability/corporate actions/issuer mapping and executable cost/tax; optimization specialist must reconcile #413/#418 source pins and strict fail-closed behavior using synthetic-only tests and immutable environment SHA, without modifying frozen data or bypassing workflow security. The orchestrator must re-read latest HEAD/CI/Railway evidence before any future decision.