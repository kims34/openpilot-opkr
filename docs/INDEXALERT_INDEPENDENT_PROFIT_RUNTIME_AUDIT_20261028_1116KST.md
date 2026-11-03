# IndexAlert 독립 수익성·런타임 감사 — 2026-10-28 11:16 KST

> **승인 아님.** 이 문서는 GitHub 원본/CI의 읽기전용 증거와 Railway 연결 차단을 기록한다. 공식 금융 원본, 종목·계좌 데이터, 인증정보, 실거래, 새 시장 백테스트, Holdout을 취급하지 않는다. 기존 Work 소유 코드·워크플로·원본 게이트 문서는 수정하지 않는다.

## 1. 이번 실행 직접 조회한 HEAD와 격리 경계

| 대상 | 조회된 정확한 HEAD | 상태 |
|---|---|---|
| 연구 `index-alert-research-v1` | `3b8b7830612a6284d7c7a60628cb527cb741627a` | 읽기전용 |
| 개발 `index-alert-position-regen-fix-v1` | `1e6367d2863a86c3470da13d81a955d277eba485` | 읽기전용 |
| OpenDART Draft #412 | `bf3d9514a87c53b1775e22ec9ba7711f6cecc49f` | OPEN/DRAFT |
| 최적화 Draft #413 | `f003ef6247e16fcc71bd3b1b20cd4904c4d984c0` | OPEN/DRAFT |
| 총괄 Draft #414 쓰기 전 | `38d1848a91dd90dc4081a64bbd3b40413a683608` | OPEN/DRAFT, 기존 문서 수정 금지 |
| 독립 단일 실행기 Draft #418 | `2f98401cc50a6c6a25808a98516efd5bf0c944ee` | OPEN/DRAFT |
| KRX 전담 `indexalert-krx-pit-source-audit-20261013` | `073d2d49e95f69fb10b943b93e51bb179fb3c698` | 읽기전용 |
| KRX Draft #420 / #422 / #423 | `fab3cbbd63a951a4e081f9e7f08c1391ca308581` / `c14857620973531013799e44625d43080904fd5f` / `0e38004363cac9fc4475556b3a1c445de9af407f` | OPEN/DRAFT |

기존 PR #414 원문 `docs/INDEXALERT_PROFITABILITY_INTEGRATION_GATE_2026-10-13.md` Git blob **SHA-1** `984c933651f39f1ee9e26a1d7ac3893aaa5335be`를 재조회했고 변경하지 않았다. 10:16 및 10:52 독립 감사 문서도 읽어 중복 실험을 피했다.

## 2. 신규 독립 교차검증: #418 단독 캐시 매니페스트에 #413 안전수정 2종 미반영

**직접 fetch한 서로 다른 파일 버전의 Git blob SHA-1**:
- [#418 HEAD의 `research_v1_runtime_manifest.py`](https://github.com/kims34/openpilot-opkr/blob/2f98401cc50a6c6a25808a98516efd5bf0c944ee/research_v1_runtime_manifest.py): `108f66714602a1bd3ae42c34dcca7c16e38f460b` (103행, 이전 버전).
- [#413 HEAD의 같은 파일](https://github.com/kims34/openpilot-opkr/blob/f003ef6247e16fcc71bd3b1b20cd4904c4d984c0/research_v1_runtime_manifest.py): `e0055c66c59398fd4a1158077446d886b54c4e37` (188행, 후속 보강).

**차이 A — 수신 영수증의 권한 부정형 검사:** #418 `_check_receipt`는 `holdout_access_authorized is True` 또는 `live_orders_authorized is True`인 경우만 거부한다. 필드 누락(`None`), 문자열, 숫자 등 비정규 표현은 이 분기에서 거부되지 않는다. #413은 두 값 모두 명시적 Python `False`여야 하고 추가 elevated flag도 명시적 `False`여야 한다. 이 비교는 **정적 소스 코드의 조건식 검증**이며 실제 주문/권한 부여가 발생했다는 의미는 아니다. #413 수정 [`eafad1e`](https://github.com/kims34/openpilot-opkr/commit/eafad1e0159da70e448a8755be9abc02ad72f84b), 실제 [Actions #38498552499](https://github.com/kims34/openpilot-opkr/actions/runs/38498552499) 6/6 성공, 34-case SHA-256 `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34` 동일, 21개 offline integrity 테스트 기록.

**차이 B — 파일 fingerprint의 TOCTOU:** #418 `_hash_files`는 `p.is_file()/p.is_symlink()` 확인 후 별도 `p.open("rb")`을 수행하고, 중간 경로 심볼릭 링크와 검사 후 교체를 고정하지 않는다. #413은 `O_NOFOLLOW` dirfd 탐색, `fstat` identity, 파일 및 배치 종료 재검증으로 보강했다. #413 수정 [`3086309`](https://github.com/kims34/openpilot-opkr/commit/3086309bb83dda1f1e4aae53e118cbb5379d0e38), 실제 [Actions #38466023642](https://github.com/kims34/openpilot-opkr/actions/runs/38466023642) 6/6 성공, 19개 synthetic integrity 테스트 및 동일 34-case parity 기록. 실제 exploit을 실행하거나 새로운 시장/성능 실험을 하지 않았다.

**통합 판정:** #418 단독 34-case 회귀 성공은 **후속 #413 안전수정의 존재를 입증하지 않는다**. 반대로 [#418 merge-context #39111405478](https://github.com/kims34/openpilot-opkr/actions/runs/39111405478)의 `SourceDriftError`는 아카이브 SHA `108f...` vs merge에서 관측된 `e005...`를 정확히 차단했다. #418 단독 HEAD가 손상됐다는 증거가 아니며, 두 브랜치 결합 코드·전체 transitive dependency·원본 영수증이 승인됐다는 의미도 아니다. **SHA 기대값만 바꿔 CI를 통과시키거나 #413/#418을 병합해서는 안 된다.** 안전한 다음 단계는 각 소유 Work가 같은 정확한 소스 스냅샷에서 기존 34-case SHA, 명시적 False 권한 차단, no-follow/TOCTOU와 완전한 의존성 해시를 오프라인에서 독립 검증하는 것이다.

## 3. 최신 GitHub Actions 직접 확인과 PASS/FAIL/NOT VERIFIED

- [Watchdog #40604202566](https://github.com/kims34/openpilot-opkr/actions/runs/40604202566), job `122539521979`: **PASS** (4+31 offline tests). 로그: `M20 PIT admission: NOT ATTESTED; orders: DISABLED; holdout: NOT AUTHORIZED`. Artifact SHA-256 `aeccdfcdafa0d4c8c3a2934a61e92523db4cfd728bbda6464e39f0a2aa786b7e`; 이는 운영 설정 증명이 아니다.
- [Chronology Anchor #40534270813](https://github.com/kims34/openpilot-opkr/actions/runs/40534270813), job `122295113858`: **FAIL** (HTTP 404 `/anchor/latest`, validation skipped). Prospective available-at **NOT VERIFIED**.
- [OpenDART #412 최신 offline #40263193758](https://github.com/kims34/openpilot-opkr/actions/runs/40263193758) **PASS 13 synthetic**, [#40263181687](https://github.com/kims34/openpilot-opkr/actions/runs/40263181687) **PASS 12 synthetic**. 첫 원본 financial TOC/section 모양을 검사하지만 2021/2022 최초 3개월 연결 영업이익의 실제 의미·공표시각 증명은 **NOT VERIFIED**.
- 이전 공식 원본 ZIP SHA-256: 2021 `8728c0a3c12761ca19e9c6455bea8f1bed0e4c1ebc2e21dc263c373a82a2b625` ([#40262558066](https://github.com/kims34/openpilot-opkr/actions/runs/40262558066)); 2022 `56639d8f6ebbecf14cd8bc3179d75d01162e2cd7bbdf8f6a3c9479b44f5084bb` ([#38392847048](https://github.com/kims34/openpilot-opkr/actions/runs/38392847048)). 이 실행에서는 raw ZIP을 다시 해시하지 않았다. 2021 13개, 2022 15개 후보 표/행은 최초 3개월 CFS 수치나 정정 lineage 승인 근거가 아니다.
- [KRX #423 #39714207925](https://github.com/kims34/openpilot-opkr/actions/runs/39714207925), job `119612335677`: **PASS 32 synthetic**; `DRY_RUN_NO_PRIVATE_STORAGE_READ`, `2022_private_candidate_date_sets_equal=false`. 기존 1,565/1,565 평일쌍 SHA 저장 무결성 PASS와 별도로 2021 13일/2022 14일 실제 private 날짜집합, 공식 시장별 달력, 거래상태, 기업행위, 체결가능성은 **NOT VERIFIED**. 90일 분류 및 27건 비정상 OHLC/12,003 zero-activity 격리 유지.
- [#413 #38498552499](https://github.com/kims34/openpilot-opkr/actions/runs/38498552499) **6/6 PASS** / 34-case 고정 SHA 일치, regression phase serial 1.7114초 vs parallel 2.5776초 = **0.664x** (병렬이 느림). [#418 #39111405562](https://github.com/kims34/openpilot-opkr/actions/runs/39111405562) **offline parity PASS**, 2.3911초 vs 2.0755초 = **1.1521x** 제한 구간 개선. 서로 다른 checkout/시점의 수치이며 전체 CI/공식 백테스트 가속 **NOT VERIFIED**.

## 4. Railway, 경제성, 허용되는 다음 단계

Railway 네이티브 읽기전용 `list_projects({})` 1회 호출은 `User input required but current turn is running in a non-interactive mode.`로 중단. 비대화형 인증 우회나 다른 토큰/프록시 시도 없음. 최신 운영 배포·로그·실제 `ORDERING` 값은 **NOT DIRECTLY VERIFIED**. 정책 `ORDERING=false` 유지가 필수이며 실설정 확인을 주장하지 않는다.

**최종 게이트: M20 PIT / 경제성 RUN = NO-GO.** 공식 original-filing 2021/2022 연결 3개월 수치·기간·수정 lineage·정확한 public available-at, 역사적 기업/종목 매핑, KRX 종목별 거래상태·기업행위·실체결 및 비용/세금의 독립 승인 영수증이 없다. 따라서 세후 NetEV, PF, CAGR, MDD, ES95/99, 수익 집중도 및 시점별 강건성은 **NOT EVALUABLE**이며 0 또는 FAIL 수익률이 아니다. Frozen H5, M20 horizon20/purge20, WF504/126/126, PIT/Purged/CPCV, 봉인 Holdout, Champion/Top3, Dynamic Challenger-only, NO_TRADE 및 비용·승격 기준은 변경하지 않는다. 독립 PIT 승인 전에는 오프라인 synthetic 안전검증만 허용한다. 캐시에는 독립 승인된 source/data/code/Frozen/runtime/evidence SHA-256 전체 일치가 필요하며, 읽기전용 후처리 외 병렬화 금지. 운영 배포, PR 병합, 워크플로 변경, 실주문·자금·계좌권한 변경, Champion 승격은 수행하지 않는다.
