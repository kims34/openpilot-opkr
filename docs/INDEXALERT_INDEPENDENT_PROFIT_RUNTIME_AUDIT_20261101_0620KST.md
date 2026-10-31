# IndexAlert 독립 수익성·격리 최적화 감사 — 2026-11-01 06:20 KST

**방법/권한:** GitHub PR/브랜치/Actions의 실제 원본 및 Railway production 배포/로그/상태를 읽기전용 재조회했다. 별도 담당 PR·코드·워크플로·데이터·운영은 변경하지 않는다. 이 문서는 원본 PIT/경제성 승인이나 새 백테스트가 아니다.

## 1. HEAD 및 전담 격리 확인
- 연구 `index-alert-research-v1` HEAD `3b8b7830612a6284d7c7a60628cb527cb741627a`; 개발 `index-alert-position-regen-fix-v1` HEAD `1e6367d2863a86c3470da13d81a955d277eba485` (GitHub commit ref 직접 조회).
- KRX 전담 `indexalert-krx-pit-source-audit-20261013` HEAD `073d2d49e95f69fb10b943b93e51bb179fb3c698`.
- Draft/open/unmerged: [#412](https://github.com/kims34/openpilot-opkr/pull/412) `bf3d9514a87c53b1775e22ec9ba7711f6cecc49f`; [#413](https://github.com/kims34/openpilot-opkr/pull/413) `f003ef6247e16fcc71bd3b1b20cd4904c4d984c0`; [#414](https://github.com/kims34/openpilot-opkr/pull/414) `0d3f37eddfa8973b82fff4f26651a2c51127c656` (별도 담당자가 05:51 KST 문서 전용 갱신); [#418](https://github.com/kims34/openpilot-opkr/pull/418) `2f98401cc50a6c6a25808a98516efd5bf0c944ee`; [#416](https://github.com/kims34/openpilot-opkr/pull/416) `053de553646fc4765d2616544ca1e8d6bbdde35f`; KRX [#420](https://github.com/kims34/openpilot-opkr/pull/420) `fab3cbbd63a951a4e081f9e7f08c1391ca308581`, [#422](https://github.com/kims34/openpilot-opkr/pull/422) `c14857620973531013799e44625d43080904fd5f`, [#423](https://github.com/kims34/openpilot-opkr/pull/423) `0e38004363cac9fc4475556b3a1c445de9af407f`; [#424](https://github.com/kims34/openpilot-opkr/pull/424) `a4ae98f40b3e6dcaf565cc402679497e42cdabb5`. 각 전담 코드/실험은 그대로 둔다.
- 총괄 기준 문서 `docs/INDEXALERT_PROFITABILITY_INTEGRATION_GATE_2026-10-13.md` blob SHA-1 `984c933651f39f1ee9e26a1d7ac3893aaa5335be` (PR #414 HEAD에서 재조회). 05:51 담당 문서 `docs/INDEXALERT_INDEPENDENT_PROFIT_GATE_DELTA_20261101_0551KST_AUTOMATION11.md`도 읽고 중복 수정을 피함.

## 2. 공식 원본·PIT·경제성 판정
| 항목 | 판정 | 독립 증거/한계 |
| --- | --- | --- |
| 2022 OpenDART 원본/정정 SGML 후보 형태 | **제한적 과거 PASS (형태만)** | [Action 38419439742](https://github.com/kims34/openpilot-opkr/actions/runs/38419439742) 2/2 성공 및 원본 job 로그 재조회. 영업손익 후보 각 15개와 숫자 인접 시그니처는 **연결 3개월 영업이익의 수치/기간 의미 승인 아님**. 기존 원본 ZIP SHA-256 `56639d8f6ebbecf14cd8bc3179d75d01162e2cd7bbdf8f6a3c9479b44f5084bb`; 이번 원본 ZIP 바이트 독립 재해시 없음. |
| 2021 OpenDART 최초공시 원본 | **제한적 과거 PASS (원본 형태만)** | [Action 40262558066](https://github.com/kims34/openpilot-opkr/actions/runs/40262558066) 2/2 성공, official job `121379096007` 원본 로그: ZIP SHA-256 `8728c0a3c12761ca19e9c6455bea8f1bed0e4c1ebc2e21dc263c373a82a2b625`, 표 형태 1,728개, 영업이익 label 후보 13개, **2021 Q3 기간 동일표 0개 / 3개월 문구 동일표 0개**, `original_2021_q3_three_month_cfs_profit_cell_verified=false`, `first_2022_q3_report_2021_comparator_cell_verified=false`. 원본 ZIP 재해시 없음. |
| 2021·2022 최초 CFS 3개월 영업이익, original public available-at, 정정 lineage, 과거 기업/종목 매핑 | **NOT VERIFIED / FAIL-CLOSED** | 단순 SGML 표/숫자 근접성 및 공시일은 원본 연결 3개월 셀·최초 공개 *시각*·정정 계보 증명이 아니다. 최초 XBRL/비교 셀 바인딩 미확정. |
| KRX 2017–2022 private 원본쌍 저장 | **과거 제한적 PASS (저장 무결성만)** | 1,565/1,565 weekday pair 기존 worker 원본 검증; 90개 달력/원천 공백 미해결, zero-activity 12,003건 외부 차단. 이번 worker 로그 0행으로 원본 바이트 재검증 없음. |
| KRX 공식 세션/거래정지/기업행위/종목 PIT/체결가능성 | **NOT VERIFIED / FAIL-CLOSED** | 90 historical gaps와 prospective 27/803 OHLC 비정상은 **서로 다른 모집단**. 평일 저장쌍은 공식 거래 가능일 증명이 아니다. |
| 독립 거래비용·세금·체결원장 및 M20 NetEV/PF/CAGR/MDD/ES95·99/집중도·시점별 강건성 | **NOT VERIFIED / NOT EVALUABLE / NO-GO** | 공식 원본/PIT/체결/비용 승인 전 경제성 계산 및 M20 RUN 금지. H5 실패/소비 Holdout 및 Dynamic 결과 독립 재사용 금지. |

## 3. 격리 최적화 코드·CI 원본 검증
- #413 원본 [Actions 38381997417](https://github.com/kims34/openpilot-opkr/actions/runs/38381997417), [38382214223](https://github.com/kims34/openpilot-opkr/actions/runs/38382214223), [38419111311](https://github.com/kims34/openpilot-opkr/actions/runs/38419111311) 각각 6/6 job SUCCESS. HEAD 연계 [38508247773](https://github.com/kims34/openpilot-opkr/actions/runs/38508247773)도 6/6 SUCCESS. 기존 34-case immutable digest `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34`; 교정 13 adversarial mocks는 기존 증거 범위의 **오프라인 동등성 제한적 PASS**.
- #418 초기 [38419649711](https://github.com/kims34/openpilot-opkr/actions/runs/38419649711) 1/1 SUCCESS, 추가 synthetic 28개/34-case 일치; serial 2.9656초 / parallel 2.6209초 = **1.1315x 회귀 테스트 phase 비율만**. HEAD 연계 후속 [39111405478](https://github.com/kims34/openpilot-opkr/actions/runs/39111405478) 1/1 **FAILURE**: job `117628139395` 원본 로그 `SourceDriftError` (archived manifest expected `108f66714602a1bd3ae42c34dcca7c16e38f460b`, observed `e0055c66c59398fd4a1158077446d886b54c4e37`). [39111405494](https://github.com/kims34/openpilot-opkr/actions/runs/39111405494) candidate source check SUCCESS이나 원본 로그 `all_transitive_imports_pinned=false`, `candidate_approved_for_merge=false`; [39111405562](https://github.com/kims34/openpilot-opkr/actions/runs/39111405562) 1/1 synthetic runner SUCCESS. 성공 job 둘은 실패/미승인을 덮어쓰지 못함.
- **실제 코드 blob 대조:** #413 `research_v1_runtime_manifest.py` SHA-1 `e0055c66c59398fd4a1158077446d886b54c4e37`는 `O_NOFOLLOW/O_DIRECTORY`로 경로 각 구성요소를 열고 `fstat`/파일 모드·inode·mtime·ctime 재확인 및 전체 파일 일괄 후 재검사를 시행하며 필수 권한 flag literal false와 추가 6개 elevated flag도 검사. #418 SHA-1 `108f66714602a1bd3ae42c34dcca7c16e38f460b`는 `Path.is_file/is_symlink` 후 재확인 없는 `open`과 두 flag의 `is True`만 검사. 따라서 missing/문자열 `"true"`/정수 1/교체 경쟁조건을 안전하게 동일하게 거부한다는 증거 없음. **#418 fail-closed 보안 동등성 FAIL / 채택 NO-GO**.
- 캐시는 독립 승인 원본·데이터·코드·Frozen·런타임/승인 evidence SHA-256 전부 맞을 때만 fail-closed. 독립 읽기전용 후처리만 병렬화; 의존 재학습·capital transition 병렬화 금지. 전체 CI wall time 및 공식 백테스트 가속 **NOT VERIFIED**.

## 4. Railway production 읽기전용 실측
- Project `d1c1a050-b7d6-41ce-b300-13c20f82a20a`, environment `83d5840b-270e-4d3f-a941-a37fd4a55ff7`. 최근 deploy 목록과 서비스 inventory 재조회, 이번 작업에서 배포 없음.
- `indexalert-pit-rebuild` SUCCESS deploy `8b354fc1-cfb2-4ef0-863e-67f7f5dda2b5`의 최신 반환 runtime line `2026-10-31T14:46:01.190084194Z` (23:46:01 KST): `FAIL_CLOSED`, `COMMON_OHLC_NONPOSITIVE`, 27/803 common-stock rows, `session_manifest_sha256=null`, source/chronology/model admission false, `ORDERING=DISABLED`, real orders/funds/permissions false. 이보다 새로운 PIT 로그 반환 없음.
- `indexalert-runtime` SUCCESS deploy `eaaa9f67-b9f2-41d2-832c-7d6fad9b9b00`, 1/1 running; 최신 반환 로그 `2026-10-31T21:20:42.217953993Z` = 11월 1일 **06:20:42 KST**. 알림 데이터는 PIT/세후 경제성 증거 아님.
- `indexalert-kiwoom-real-readonly` SUCCESS deploy `a77fb922-b679-4d88-92c4-03054ec579cd`와 online 표시에도 `running=0,crashed=1,total=1`. 2026-10-29 06:22 UTC 로그 `DETAIL_CODE=8050`, `TOKEN_OR_LOGIN_AUTH`, `TOKEN_OK=false`, `WS_CONNECTED=false`, `TYPE00_EVENT_COUNT=0`, `ORDERING=DISABLED`. 실제 broker 인증·체결 승인 증거 아님.
- `describe_environment`/`get_staged_changes`: staged=null/0 changed resources, `environment_status`: 오래된 `patch:e113dacb-6705-4416-9997-dc694539d382` staged/changes=[] 표시. **조회모델 불일치 NOT VERIFIED**; patch 승인/적용 금지.

## 5. 다음 독립 게이트 및 불변사항
1. OpenDART 담당: 최초 2021·2022 연결 독립 3개월 셀의 기간·계정·부호·단위·원본/정정 바이트 SHA 및 최초 public available-at, 과거 기업/종목 연결을 원본별 독립 입증.
2. KRX 담당: 공식 실제 거래세션·상태·기업행위·체결가능성/세금·비용 시점별 원장과 90개 gap 해소; prospective 27개는 별도 fail-closed 유지.
3. #418 담당: 전체 의존성 closure SHA, 권한 flag strictness, symlink/rename/TOCTOU 및 batch recheck에 대한 격리 synthetic adversarial parity를 복원한 뒤 전체 CI A/B 비교. archived 34-case baseline 사후 변경 금지.
4. 원본 승인 전에는 Frozen H5, M20 horizon20/purge20, WF504/126/126, PIT/label/Purged/CPCV/독립 Holdout/Champion/Top3/NO_TRADE, 비용/세금/위험/승격 정책 고정. `ORDERING=false`; 실매매·자금·인증/계좌권한·Champion 승격은 각각 별도 명시 승인. M20 경제성 RUN, 새 공식 시장 수익률 실험, 재학습, PR 병합/배포/자동병합 없음. 기존 workflow 보안 차단 우회 없음.
