# IndexAlert 독립 읽기전용 증거 감사 — 2026-10-15 22:19 KST

범위: 총괄 판정과 격리 최적화 원본 확인만. 이 문서는 소스/PIT/수익성/병합/실거래 승인서가 아니며, 기존 PR #412/#413/#414/#418/#420 코드·총괄 게이트 문서를 수정하지 않는다.

## 고정 HEAD 및 출처 (2026-10-15 22:19 KST 조회)
- 연구 `index-alert-research-v1`: `3b8b7830612a6284d7c7a60628cb527cb741627a`.
- 개발 `index-alert-position-regen-fix-v1`: `1e6367d2863a86c3470da13d81a955d277eba485`.
- [총괄 Draft PR #414](https://github.com/kims34/openpilot-opkr/pull/414): `2c2c1ec373f2170a29930752380f022e6919a921`. 기존 총괄 문서 blob SHA `984c933651f39f1ee9e26a1d7ac3893aaa5335be`.
- [OpenDART Draft PR #412](https://github.com/kims34/openpilot-opkr/pull/412): `7d0a10a6da90584a192196b8e3cead81147abf30`.
- [KRX Draft PR #420](https://github.com/kims34/openpilot-opkr/pull/420): `841d3c74e9f20d3023e3cdf1f82b3e594ba3190d`.
- [최적화 Draft PR #413](https://github.com/kims34/openpilot-opkr/pull/413): `f003ef6247e16fcc71bd3b1b20cd4904c4d984c0`.
- [단일 실행기 Draft PR #418](https://github.com/kims34/openpilot-opkr/pull/418): `ecb5662e728365c24e3ae8f43c5683062d88aace`. PR #413 HEAD 대비 compare `diverged`, ahead 43 / behind 18. GitHub의 `mergeable=true`는 본 안전/경제성 승인과 별개.

## 원본/시장/수익성 증거 판정
| 항목 | 판정 | 독립 조회 |
|---|---|---|
| OpenDART 최초 제출 문서 구조용 오프라인 검증 | PASS (합성 12/12만) | [Actions #38731845863](https://github.com/kims34/openpilot-opkr/actions/runs/38731845863), job `116411271826`. [#38731845569](https://github.com/kims34/openpilot-opkr/actions/runs/38731845569)도 synthetic CI PASS. |
| 2022/2021 최초 3개월 연결 영업이익, 정정 lineage, 정확한 최초 공개 시점, 기업-종목 과거 매핑 | NOT VERIFIED | 위 두 최신 Actions는 공식 데이터 의미/시점 확정이 아닌 no-network synthetic CI. 2022 원본 ZIP SHA는 이전 총괄 문서의 저장 무결성 증거이며 사실값/PIT 권한이 아님. |
| KRX 2017~2022 저장 원본쌍 | PASS (저장만) | Railway `indexalert-krx-historical-worker` 로그 `INDEXALERT_MISSING_2017_2022_INTEGRITY_FINAL`: 1565/1565, missing 0, invalid 0, aggregate SHA256 `e2503a3bc623d4386e5783ec19272916fe6abba9bc191c14040d2c0831c7f01a`; `network_request_attempted=false`, `storage_mutated=false`. |
| KRX 공식 거래일·거래상태·기업행위·체결가능성 | NOT VERIFIED | 같은 로그의 `unverified_exchange_calendar_or_source_gap_days=90`, `sampled_zero_activity_ohlc_rows=12003`, `sampled_other_invalid_ohlc_rows=1`, `official_trading_status_verified=false`, `corporate_action_paths_verified=false`. [KRX synthetic Actions #38731494982](https://github.com/kims34/openpilot-opkr/actions/runs/38731494982) 35/35 PASS는 실데이터 승인 아님. |
| 비용/세금·실제 체결·NetEV·PF·CAGR·MDD·ES95/99·집중도·시점별 강건성 | NOT VERIFIED | 공식 PIT/거래가능성 미승인으로 M20 수익성 RUN 금지. H5 실패 및 소비 Holdout, Dynamic 사후 결과를 독립 검증으로 재사용 금지. |

## 격리 최적화/무결성
- [PR #413 Actions #38508247773](https://github.com/kims34/openpilot-opkr/actions/runs/38508247773): 6/6 jobs PASS, 오프라인 전용.
- [PR #418 Actions #38708560192](https://github.com/kims34/openpilot-opkr/actions/runs/38708560192): 34-case 결과 SHA256 `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34` 일치, serial subprocess 1.9997s / concurrent group 2.0426s (속도비 0.979; 병렬 약 2.1% 느림). 새 synthetic handoff 14건은 파일/디렉터리 교체, symlink, TOCTOU 및 fail-closed 방어 PASS. 이는 실전 환경의 완전한 TOCTOU 방지 증명 아님.
- [Actions #38708559866](https://github.com/kims34/openpilot-opkr/actions/runs/38708559866): archived-source gate가 `research_v1_runtime_manifest.py` Git blob 기대 `108f66714602a1bd3ae42c34dcca7c16e38f460b`, 관측 `e0055c66c59398fd4a1158077446d886b54c4e37` 불일치를 발견해 **정상 차단(FAIL-CLOSED)**. 후속 회귀 suite는 실행되지 않음.
- [Actions #38708560319](https://github.com/kims34/openpilot-opkr/actions/runs/38708560319): 후보 21개 직접 파일 검사 및 기존 34-case SHA 일치, upstream `f003ef6247e16fcc71bd3b1b20cd4904c4d984c0` 계보 일치. **`all_transitive_imports_pinned=false`, `candidate_approved_for_merge=false`**. 전체 전이 의존성/병합 안전성 NOT VERIFIED.
- 캐시: 승인된 독립 원본·데이터·계산코드·Frozen 정책·런타임·승인 증거 SHA-256 모두 일치할 때만 fail-closed. 읽기전용 독립 비용/위험/후처리만 병렬화 가능; 재학습·capital transition 병렬화 금지. 전체 CI/공식 백테스트 가속 NOT VERIFIED.

## Railway 운영 읽기전용
- production 환경 `83d5840b-270e-4d3f-a941-a37fd4a55ff7`, 10개 서비스, staged/pending work 없음.
- `indexalert-backend`, `indexalert-push`, `db-query-readonly` 3개 offline.
- `indexalert-kiwoom-real-readonly`는 UI state online이나 replica `running=0, crashed=1`; 서비스 online만으로 정상 판정 금지.
- KRX worker 로그 `ordering=DISABLED`, `m20_performance_testing_authorized=false`, `live_orders_authorized=false`, `historical_publication_pit_verified=false`. 설정 변경 없음.

## 최종 게이트 및 다음 단계
1. OpenDART 담당 원본 2022/2021 정확한 연결 3개월 표·최초 available-at·정정 lineage를 공식 출처/해시로 증명할 때까지 M20 금지.
2. KRX 담당 90일과 27 의심 종목의 공식 달력/종목별 거래상태/기업행위/체결 증거를 원본 SHA로 독립 대조할 때까지 PIT 및 거래가능성 미승인.
3. 최적화 담당은 기존 전담 코드와 격리된 offline-only 원본 의존성 완전성/후처리 parity 확인만 진행. #413/#418 병합 금지.
4. Frozen H5, M20 horizon20/purge20, WF504/126/126, PIT, Purged/CPCV, 독립 Holdout, Champion/Top3/NO_TRADE, 비용/세금/위험/승격 정책 불변. `ORDERING=false` 유지. 실매매·자금 이동·인증/권한 변경·배포·자동병합·Champion 승격 금지.

이 문서는 이전 증거를 현재 GitHub HEAD/Actions/Railway에 다시 연결한 읽기전용 감사 기록이며 새로운 경제적 수익성 증거를 생성하지 않는다.
