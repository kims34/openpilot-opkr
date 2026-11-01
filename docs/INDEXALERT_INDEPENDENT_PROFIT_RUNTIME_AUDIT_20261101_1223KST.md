# IndexAlert 독립 수익성·격리 최적화 감사 — 2026-11-01 12:23 KST

**최종 판정: M20 경제성 NOT EVALUABLE / NO-GO.** ORDERING=false / Railway `DISABLED`. 본 회차는 GitHub/Railway 실원본 읽기전용 조회 및 전담 독립 감사 브랜치 신규 문서 1건만 허용한다. 연구·개발·KRX/OpenDART 전담 코드, PR #413/#414/#418, GitHub workflow, Railway 운영 설정, 계정·자금·주문·Champion·Holdout은 수정/실행하지 않았다.

비교 기준: [11:24 KST 독립 감사](https://github.com/kims34/openpilot-opkr/blob/e152acd87b3acab6c495d582e0a865d777525194/docs/INDEXALERT_INDEPENDENT_PROFIT_RUNTIME_AUDIT_20261101_1124KST.md), blob SHA-1 `ed06d352413946dfe8d15487424f7bbd77e28f81`. 11:24 이후 공식 원본 승인이나 경제성 검증 진전은 확인되지 않음.

## 1. 실제 최신 GitHub HEAD / 담당 영역 / Actions

- 연구 `index-alert-research-v1` HEAD `3b8b7830612a6284d7c7a60628cb527cb741627a`; 개발 `index-alert-position-regen-fix-v1` HEAD `1e6367d2863a86c3470da13d81a955d277eba485`; KRX 담당 `indexalert-krx-pit-source-audit-20261013` HEAD `073d2d49e95f69fb10b943b93e51bb179fb3c698` (GitHub commit-by-ref 실제 조회).
- 전부 open/Draft/unmerged: [OpenDART #412](https://github.com/kims34/openpilot-opkr/pull/412) `bf3d9514a87c53b1775e22ec9ba7711f6cecc49f`; [최적화 #413](https://github.com/kims34/openpilot-opkr/pull/413) `f003ef6247e16fcc71bd3b1b20cd4904c4d984c0`; [총괄 #414](https://github.com/kims34/openpilot-opkr/pull/414) **`784c559fd4d6faf0bf600fd931a1060dcdccf869`**; [수급 #416](https://github.com/kims34/openpilot-opkr/pull/416) `053de553646fc4765d2616544ca1e8d6bbdde35f`; [단일 실행기 #418](https://github.com/kims34/openpilot-opkr/pull/418) `2f98401cc50a6c6a25808a98516efd5bf0c944ee`; KRX [#420](https://github.com/kims34/openpilot-opkr/pull/420) `fab3cbbd63a951a4e081f9e7f08c1391ca308581`, [#422](https://github.com/kims34/openpilot-opkr/pull/422) `c14857620973531013799e44625d43080904fd5f`, [#423](https://github.com/kims34/openpilot-opkr/pull/423) `0e38004363cac9fc4475556b3a1c445de9af407f`; 격리 ETF [#424](https://github.com/kims34/openpilot-opkr/pull/424) `a4ae98f40b3e6dcaf565cc402679497e42cdabb5`.
- #414 HEAD는 11:24 대비 새 문서-only commit. 변경 파일 `docs/INDEXALERT_PROFITABILITY_INDEPENDENT_GATE_20261101_1151KST_AUTOMATION11.md` (blob SHA-1 `e92e9aa8828677387bfe4c0db5eaf34d2b863ac5`). 다른 총괄 Work의 문서를 읽기전용으로 확인했고 그 영역에 중복 기록/수정하지 않음. 그 문서도 M20 NO-GO를 유지함.
- [Watchdog Actions #41264126871](https://github.com/kims34/openpilot-opkr/actions/runs/41264126871), job `124723240979` SUCCESS. 2026-11-01 02:11 UTC 원본 로그 `M20 PIT admission: NOT ATTESTED; orders: DISABLED; holdout: NOT AUTHORIZED`. 안전검증 성공이지 원본/PIT 승인이 아님. Artifact ZIP SHA-256 `f30092454e52fb715a4cbba3631dbf2ecb8b4e9d57261e9bba942477908064b6`.
- [OpenDART Action #38419439742](https://github.com/kims34/openpilot-opkr/actions/runs/38419439742) 2/2 jobs SUCCESS 재조회, 2022 original/corrected SGML 영업손익 후보 15행 숫자 인접 시그니처의 한정된 증거. ZIP artifact `11826291004` SHA-256 `9380e385d6fc946a7668c47cce32aa23ed718d9fb5cb2c2edf620bb055bbfcb9` (이는 원본 document ZIP 해시와 다름). 원본 document SHA-256 `56639d8f6ebbecf14cd8bc3179d75d01162e2cd7bbdf8f6a3c9479b44f5084bb`는 과거 소스-reported 값이며 이번 원본 바이트 독립 재해시 없음.
- [Chronology Anchor #41091128151](https://github.com/kims34/openpilot-opkr/actions/runs/41091128151) 기존 HTTP 404 실패/validation skipped, 최초 공개시점 승인을 뒷받침하지 못함.

## 2. 원본·PIT·거래·경제성 판정

| 증거/게이트 | 판정 | 근거 및 남은 조건 |
|---|---|---|
| 2022 최초/정정 SGML 후보 행·저장 원본 식별 | **HISTORICAL LIMITED PASS (source only)** | Action #38419439742. 원본 숫자 후보 15개/인접 시그니처만으로 실제 CFS 3개월 영업이익 의미를 승인할 수 없음. |
| 2021 최초 ZIP 및 후보 | **HISTORICAL LIMITED PASS (source only)** | 이전 1,728 tables / 13 candidates, strict same-table 3-month binding 0; ZIP SHA-256 `8728c0a3c12761ca19e9c6455bea8f1bed0e4c1ebc2e21dc263c373a82a2b625`는 이전 증거, 금회 원본 재해시 없음. |
| 2021/2022 최초 July–Sept 연결 3개월 영업이익·기간·수정 계보·public available-at·과거 기업/종목 매핑 | **NOT VERIFIED** | Original-edition CFS IS/CIS cell, 단위/부호, quarter-only vs cumulative, first-public instant, correction vintage, issuer/security as-of 결합 증명 필요. |
| KRX 2017–2022 1,565/1,565 weekday daily/master 저장쌍 | **HISTORICAL STORAGE-ONLY LIMITED PASS** | Railway historical-worker 과거 SHA 검증. 금회 서비스 deploy logs 0건; 실제 공식 달력/상태·거래가능성 검증으로 확대 해석 금지. |
| KRX 90 미분류 일자·12,003 zero-activity·27 비정상 OHLC, 거래정지/기업행위/체결·세금/비용 | **NOT VERIFIED / 27 fail-closed** | 정확한 공식 거래일·종목별 상태·기업행위·호가/체결·슬리피지·세금 시점 및 과거 security identity 증거 없음. |
| H5/Dynamic/소비된 독립 Holdout | **NO-GO** | 기존 실패 및 소비 결과 재사용·사후 조정·Champion 승격 금지. |
| M20 horizon20/purge20, WF504/126/126, after-tax NetEV/PF/CAGR/MDD/ES95/ES99/집중도/시점 강건성 | **NOT EVALUABLE / NO-GO** | 원본/PIT/거래가능성·비용 admission 선행 미충족. 공식 시장 수익률 실험이나 경제성 RUN 실행 금지. |

## 3. 격리 최적화 원본 코드/CI 독립 재확인

- [PR #413 원본 Actions #38381997417](https://github.com/kims34/openpilot-opkr/actions/runs/38381997417), [#38382214223](https://github.com/kims34/openpilot-opkr/actions/runs/38382214223), [교정 #38419111311](https://github.com/kims34/openpilot-opkr/actions/runs/38419111311) 각각 6/6 jobs SUCCESS 재조회. 원래 고정 34-case SHA-256 `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34`; 13 adversarial mocks는 합성 오프라인 범위의 LIMITED PASS.
- [PR #418 초기 #38419649711](https://github.com/kims34/openpilot-opkr/actions/runs/38419649711) 1/1 SUCCESS. 추가 synthetic 28개와 34-case 결과 SHA 동등성, serial 2.9656초 / 동시 2.6209초 = regression-phase 1.1315x는 기존 제한된 증거. 전체 CI wall-time·공식 H5/M20 backtest 가속 **NOT VERIFIED**.
- [PR #418 최신 HEAD run #39111405478](https://github.com/kims34/openpilot-opkr/actions/runs/39111405478) job `117628139395` 실제 FAIL: `SourceDriftError`, archived `research_v1_runtime_manifest.py` expected Git blob SHA-1 `108f66714602a1bd3ae42c34dcca7c16e38f460b` vs observed `e0055c66c59398fd4a1158077446d886b54c4e37`. 같은 HEAD의 #39111405494 candidate audit 및 #39111405562 offline timing 성공은 이 실패를 해소하지 않음.
- **금회 직접 읽은 코드:** #413 `research_v1_runtime_manifest.py` blob `e0055c66c59398fd4a1158077446d886b54c4e37`는 권한 플래그 literal False, 6개 optional elevated aliases, POSIX `O_NOFOLLOW`/fd identity, 파일 교체 재검증. #418 자체 브랜치 manifest blob `108f66714602a1bd3ae42c34dcca7c16e38f460b`는 `is_file/is_symlink` + 일반 `open`, 명시 True만 거절. **브랜치 단독 동등성 FAIL**; PR synthetic merge context와는 별도 구분.
- #418 candidate merge checker `research_v1_runtime_candidate_merge_gate.py` blob `9bfc94edb43c10c7c06bb37b2bbafe6a05a0865c`: exact upstream HEAD `f003ef6247e16fcc71bd3b1b20cd4904c4d984c0` 및 22 direct source blobs만 고정. 반환 자체 `candidate_approved_for_merge=false`, `all_transitive_imports_pinned=false`. 즉 candidate audit 성공은 전체 의존성·권한·runtime 승인 증거가 아님. #418 archived source checker blob `92cd52a4226fe7e1b58316e298e9d862178c12f1` 역시 direct import만 검증함.
- 캐시는 독립 승인된 original/PIT source, 데이터, 계산 코드, Frozen 정책, runtime 및 승인 evidence SHA-256 전부 일치할 때만 fail-closed. 의존적 재학습/capital transition 병렬화 금지, 독립 읽기전용 후처리만 허용. 이번 회차 신규 synthetic 실험이나 workflow 실행/수정 없음.

## 4. Railway production 원본 상태

- project `d1c1a050-b7d6-41ce-b300-13c20f82a20a`, environment `83d5840b-270e-4d3f-a941-a37fd4a55ff7`. `describe_environment`는 `staged=null`, `environment_status`는 `patch:e113dacb-6705-4416-9997-dc694539d382` `staged` / `changes=[]`: **두 조회 API 상태 불일치 지속**. 승인 없이 패치/배포 적용 금지.
- PIT `indexalert-pit-rebuild` deployment `8b354fc1-cfb2-4ef0-863e-67f7f5dda2b5` SUCCESS이지만 **최신 반환 로그** `2026-10-31T14:46:01.190084194Z` (23:46:01 KST): `FAIL_CLOSED`, `COMMON_OHLC_NONPOSITIVE`, common stock 803 / nonpositive 27 / zero volume-value 27, `independent_source_admission_verified=false`, `independent_chronology_admission_verified=false`, `independent_model_admission_verified=false`, `session_manifest_sha256=null`, `ordering=DISABLED`. 반환 이후 미조회 사건이 없다는 뜻은 아님.
- 알림 `indexalert-runtime` deployment `eaaa9f67-b9f2-41d2-832c-7d6fad9b9b00` SUCCESS, **최신 반환 로그** `2026-11-01T03:23:44.116884740Z` (12:23:44 KST), 단순 지수·환율 알림이지 M20 admission/경제성 증거 아님.
- KRX historical-worker `16c93d7c-7cd0-4d84-a327-298d2805376c` SUCCESS이지만 금회 deploy logs 0. Kiwoom REAL read-only `a77fb922-b679-4d88-92c4-03054ec579cd` SUCCESS 표시와 동시에 `environment_status`는 `online` / `running=0, crashed=1, total=1` 상충. 8050 인증 성공/실거래 가능 판정 금지.

## 5. 안전한 후속 조건

OpenDART 전담은 최초 2021/2022 CFS 3개월 셀+first-public timestamp+정정 lineage+issuer/security as-of의 **원본 바이트 SHA 및 의미 검증**을 제공해야 함. KRX 전담은 90일 공식 세션/상태, 기업행위, 과거 거래가능성 및 수수료·세금·체결/시장충격 원본을 독립 검증해야 함. 최적화 전담은 #418 merged candidate의 **완전한 transitive dependency closure**, 권한/경로/교체 fail-closed 동등성, 전체 CI timing을 오프라인 합성·정책 안전검증으로 별도 입증해야 함. 다른 전담 코드/문서 중복 수정 금지. Frozen H5, M20 20/20, WF504/126/126, PIT/Purged/CPCV/독립 Holdout/Champion/Top3/NO_TRADE, 비용·세금·위험·승격 정책 유지. 운영 배포, Draft 병합, 실제 주문, 자금·인증·계정권한 변경, Champion 승격 없음. 새로운 공식 승인 증거 없음.
