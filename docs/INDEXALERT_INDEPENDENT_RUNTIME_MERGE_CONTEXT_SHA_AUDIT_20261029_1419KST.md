# IndexAlert 독립 수익성·격리 최적화 감사 — 2026-10-29 14:19 KST

> **권한:** 읽기전용 GitHub 원본/Actions 검증과 이 독립 문서 1개 기록만. 소스 PIT 미승인, M20 경제성 NO-GO, 실주문·병합·배포·Champion 승격·Holdout 접근 금지. 이 문서는 원본/모델/승인 상태를 변경하지 않는다.

## 기준 HEAD 및 격리

- 연구 `index-alert-research-v1`: `3b8b7830612a6284d7c7a60628cb527cb741627a`; 개발 `index-alert-position-regen-fix-v1`: `1e6367d2863a86c3470da13d81a955d277eba485`; KRX 원본 전담 `indexalert-krx-pit-source-audit-20261013`: `073d2d49e95f69fb10b943b93e51bb179fb3c698` (GitHub branch REST GET).
- Draft PR #412 `bf3d9514a87c53b1775e22ec9ba7711f6cecc49f`, #413 `f003ef6247e16fcc71bd3b1b20cd4904c4d984c0`, #414 **기록 전** `0ec8480cf4a0b071468c8c7cc2b968d2eb04d756`, #416 `053de553646fc4765d2616544ca1e8d6bbdde35f`, #418 `2f98401cc50a6c6a25808a98516efd5bf0c944ee`, KRX #420 `fab3cbbd63a951a4e081f9e7f08c1391ca308581`, #422 `c14857620973531013799e44625d43080904fd5f`, #423 `0e38004363cac9fc4475556b3a1c445de9af407f`; 모두 Draft, open, unmerged. #414 기존 통합 게이트 `docs/INDEXALERT_PROFITABILITY_INTEGRATION_GATE_2026-10-13.md` Git blob SHA-1 `984c933651f39f1ee9e26a1d7ac3893aaa5335be`.
- 동일 브랜치의 별도 전담 [13:42 독립 게이트](https://github.com/kims34/openpilot-opkr/blob/0ec8480cf4a0b071468c8c7cc2b968d2eb04d756/docs/INDEXALERT_INDEPENDENT_PROFIT_GATE_DELTA_20261029_1342KST_AUTOMATION11.md)를 먼저 확인해 중복 실험·기존 문서 수정 회피.

## 신규 독립 원본 대조 — PR #418 archived manifest 실패의 merge-context 계보

- [PR #418](https://github.com/kims34/openpilot-opkr/pull/418)의 `head`는 `index-alert-backtest-single-runner-opt-v1-20261013`, `base`는 PR #413의 `index-alert-backtest-runtime-opt-v1-20261013`; GitHub PR API가 반환한 synthetic merge SHA `052cf67e45500baad771527753744289529ecbc2`.
- GitHub Contents REST에서 같은 경로 `research_v1_runtime_manifest.py`의 **PR #418 head Git blob SHA-1** = `108f66714602a1bd3ae42c34dcca7c16e38f460b` (103 lines), **PR #413 base Git blob SHA-1** = `e0055c66c59398fd4a1158077446d886b54c4e37` (188 lines), **refs/pull/418/merge Git blob SHA-1** = `e0055c66c59398fd4a1158077446d886b54c4e37`, **run #39111405478 checkout merge commit의 동일 파일** = `e0055c66c59398fd4a1158077446d886b54c4e37`.
- [실제 failed job #117628139395](https://github.com/kims34/openpilot-opkr/actions/runs/39111405478) 원본 로그는 `SourceDriftError: archived blob mismatch: research_v1_runtime_manifest.py expected=108f66714602a1bd3ae42c34dcca7c16e38f460b observed=e0055c66c59398fd4a1158077446d886b54c4e37`를 기록. **단순 파일 다운로드 손상이라고 볼 증거가 아니라, PR head에 고정한 파일 버전과 GitHub merge-context에서 선택된 base 파일 버전의 불일치**가 정확히 재현됨. 이는 PASS가 아니라 **FAIL-CLOSED**.
- Base 파일은 `_identity`, `_read_fingerprint_no_follow` 등의 별도 파일 식별·검사 헬퍼와 확장된 `_hash_files`를 포함하고, head는 구형 `_hash_files` 구현이다. 따라서 두 파일은 SHA만 다른 동일 코드가 아니다. **자동 repin, 구형 head로 덮어쓰기, workflow 우회, merge, 캐시 재사용 모두 금지**. 격리 최적화 소유자가 소스 계보와 안전성 의미를 독립 검토하고 명시적인 새로운 immutable source/runtime closure를 고정한 뒤, 허용된 오프라인 안전 CI에서 정확한 checkout context로 검증해야 한다. 본 감사에서는 타 Work 코드나 workflow를 변경하지 않았다.
- [후보 소스 검증 #39111405494](https://github.com/kims34/openpilot-opkr/actions/runs/39111405494) SUCCESS는 archived merge-context SHA FAIL을 치유하지 않는다. Wheel 정확한 해시 `exact_wheel_hashes_verified=false`, OS native identity `os_native_dependency_identity_verified=false`, 전이 의존성 전체 고정 미검증. 독립 승인 source/data/code/Frozen/runtime/authorization SHA-256 일치 전 캐시 **NO-GO**.

## 원본 로그로 재확인한 독립 게이트

| 대상 | 증거 | 판정 |
| --- | --- | --- |
| 최신 Watchdog | [#40806178512](https://github.com/kims34/openpilot-opkr/actions/runs/40806178512), job `123225555499` SUCCESS, 4 watchdog + 31 governance offline tests, `M20 PIT admission: NOT ATTESTED; orders: DISABLED; holdout: NOT AUTHORIZED`; status ZIP SHA-256 `6f4d29f3db3475b497dbcd87c027f48a540e96c853e5e0f0131a5726001c821a` (시장 원본 아님) | 오프라인 안전 PASS; PIT NOT VERIFIED |
| Prospective Anchor | [#40726273259](https://github.com/kims34/openpilot-opkr/actions/runs/40726273259), job `122950285352` HTTP 404 FAIL, validation skipped | FAIL |
| 2021 OpenDART 최초 | [#40262558066](https://github.com/kims34/openpilot-opkr/actions/runs/40262558066), job `121379096007` 원본 ZIP SHA-256 `8728c0a3c12761ca19e9c6455bea8f1bed0e4c1ebc2e21dc263c373a82a2b625`, 1,728 table shapes, 영업 후보 13, 동일 표 2021 Q3/3개월 결합 0 | 저장/shape PASS, CFS/available-at PIT NOT VERIFIED |
| 2022 OpenDART 최초 | [#38381866190](https://github.com/kims34/openpilot-opkr/actions/runs/38381866190), job `115244084285` ZIP SHA-256 `56639d8f6ebbecf14cd8bc3179d75d01162e2cd7bbdf8f6a3c9479b44f5084bb`, 후보 15, 정확한 연결 3개월 셀·정정 lineage 미입증; [정정 비교 #38419439742](https://github.com/kims34/openpilot-opkr/actions/runs/38419439742)도 값/공표시각 승인 아님 | 원본 취득 PASS, PIT NOT VERIFIED |
| KRX | [#39721289545](https://github.com/kims34/openpilot-opkr/actions/runs/39721289545) 164/164 합성 guard PASS, [#39714369438](https://github.com/kims34/openpilot-opkr/actions/runs/39714369438) no-provider CI SUCCESS; 과거 private weekday 원본쌍 1,565/1,565 저장 영수증은 거래가능성 증명 아님 | 오프라인 PASS, 공식 세션/상태/기업행위/체결 NOT VERIFIED |
| PR #413 | [#38508247773](https://github.com/kims34/openpilot-opkr/actions/runs/38508247773) 6/6 jobs SUCCESS, 34-case 고정 SHA-256 `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34`, cost 9 tests + 10 subtests PASS; test-phase speed ratio 0.6520x | 오프라인 parity/cost-code PASS; 가속 NOT VERIFIED |
| PR #418 | [#39111405562](https://github.com/kims34/openpilot-opkr/actions/runs/39111405562) 1/1 SUCCESS, 동일 34-case SHA, serial subprocess 2.3911s vs parallel 2.0755s = 1.1521x 제한된 회귀구간; [#39111405478](https://github.com/kims34/openpilot-opkr/actions/runs/39111405478) archived SHA FAIL | parity PASS; 전체 CI/공식 백테스트 가속 NOT VERIFIED; 캐시 FAIL-CLOSED |

- 위 GitHub 원본 Actions 결과는 원본 공시의 정확한 `public available-at`, 2021/2022 최초 3개월 **연결** 영업이익 기간·단위·부호·정정 이력, 역사적 기업/종목 매핑, 공식 KRX 종목별 거래정지/기업행위/체결 가능성과 비용·세금·슬리피지 검증을 대신하지 않는다. NetEV/PF/CAGR/MDD/ES95/ES99, 수익 집중도·시점별 강건성은 **NOT EVALUABLE**; M20 경제성 **NO-GO**.
- Railway read-only `list_projects({})` 한 번 시도 → `User input required but current turn is running in a non-interactive mode.` 운영 배포·로그·실제 `ORDERING` 값 **NOT VERIFIED**. 우회·재시도·계정/인증 변경 없음. `ORDERING=false`, `KIWOOM_ORDERING_ENABLED=false`는 변경 불가 정책.
- Frozen H5, M20 horizon20/purge20, WF504/126/126, Purged/CPCV, 독립 소진 Holdout, Champion/Top3/NO_TRADE, 비용·세금·위험·승격 기준 불변. 종속 재학습/capital transition 병렬화, 시장 수익률 실험, 모델 탐색, 승인 없는 실거래·배포·PR 병합 없음.

**다음:** DART 원본 소유자 최초 2021/2022 3개월 CFS 수치·available-at·정정 lineage 입증 → KRX 소유자 공식 per-security 거래가능성/기업행위/체결 가능성 입증 → 격리 최적화 소유자 PR head/base/merge-context 안전한 manifest 계보 및 전체 wheel/native/transitive SHA closure 독립 검증 → 총괄의 단일 사전등록 M20 경제성 승인 여부 별도 판정. 어느 단계도 이 문서만으로 자동 해제되지 않는다.
