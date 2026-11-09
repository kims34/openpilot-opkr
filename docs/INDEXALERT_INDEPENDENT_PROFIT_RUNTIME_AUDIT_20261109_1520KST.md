# IndexAlert 독립 수익성·격리 최적화 감사 — 2026-11-09 15:20 KST

## 범위와 검증 방법
GitHub PR metadata, GitHub Actions jobs, PR #414 문서 blob, Railway production status 및 2026-11-09 14:15–15:25 KST 서비스 deploy 로그를 이번 실행에서 읽기전용 조회. 다른 담당 영역 변경 없음. 아래 PASS는 명시된 좁은 범위에만 적용한다.

## 정확한 GitHub HEAD (이번 실행 직접 조회)
- 연구 index-alert-research-v1: 브랜치 존재 확인, tip SHA **NOT VERIFIED** (branch search는 SHA 미반환). 기존 참고 SHA df474df348f22aa38b1dedaa59fcff66e548b406은 이번 tip 확정값 아님.
- 개발 index-alert-position-regen-fix-v1: 브랜치 존재 확인, tip SHA **NOT VERIFIED**. 기존 참고 SHA 1e6367d2863a86c3470da13d81a955d277eba485는 이번 tip 확정값 아님.
- PR #412 Open/Draft head bf3d9514a87c53b1775e22ec9ba7711f6cecc49f.
- PR #413 Open/Draft head f003ef6247e16fcc71bd3b1b20cd4904c4d984c0.
- PR #414 Open/Draft head 18c5418d9684d1717df58261ea27f28e514385b2. docs/INDEXALERT_PROFITABILITY_INTEGRATION_GATE_2026-10-13.md blob 984c933651f39f1ee9e26a1d7ac3893aaa5335be (PR #414 branch에서 직접 읽음).
- PR #418 Open/Draft head 2f98401cc50a6c6a25808a98516efd5bf0c944ee.
- KRX PR #420 Open/Draft head fab3cbbd63a951a4e081f9e7f08c1391ca308581.
- KRX PR #422 Open/Draft head c14857620973531013799e44625d43080904fd5f.
- KRX PR #423 Open/Draft head 0e38004363cac9fc4475556b3a1c445de9af407f.
- 독립 감사 브랜치 존재 확인, 작성 직전 tip SHA 미확정. 각 PR 미병합.

## CI 직접 재확인
- Actions https://github.com/kims34/openpilot-opkr/actions/runs/38381997417 6/6 success; /38382214223 6/6 success; /38419111311 6/6 success.
- https://github.com/kims34/openpilot-opkr/actions/runs/38419649711 1/1 success.
- https://github.com/kims34/openpilot-opkr/actions/runs/38419439742 2/2 success.
- https://github.com/kims34/openpilot-opkr/actions/runs/41515392296 auto-anchor FAILURE, validation SKIPPED.
- 34-case SHA-256 5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34, 13 adversarial mocks, 28 synthetic, serial 2.9656s vs concurrent 2.6209s (1.1315x) are **prior evidence**, not independently recomputed this run. Whole CI and official backtest speed NOT VERIFIED.

## Railway production 직접 조회
Project d1c1a050-b7d6-41ce-b300-13c20f82a20a, environment 83d5840b-270e-4d3f-a941-a37fd4a55ff7.
- Latest deployments: PIT rebuild SUCCESS (8b354fc1-cfb2-4ef0-863e-67f7f5dda2b5), KRX worker SUCCESS (16c93d7c-7cd0-4d84-a327-298d2805376c), runtime SUCCESS (eaaa9f67-b9f2-41d2-832c-7d6fad9b9b00), real readonly SUCCESS (a77fb922-b679-4d88-92c4-03054ec579cd). Backend and Push FAILED. db-query-readonly latest deployment null.
- numReplicas null for all returned services: **runtime replica health NOT VERIFIED**, not a PASS and not a 0 count.
- 2026-11-09T05:15:00Z to 06:25:00Z: PIT/KRX/real readonly deploy logs each 0 returned; runtime 101 entries returned, ETF closed proxy display logs, not trading PIT evidence.
- environment stagedChanges=null yet pendingWork includes empty staged patch e113dacb-6705-4416-9997-dc694539d382; no accept/deploy.
- ORDERING actual environment variable not inspected; policy remains false, operational state NOT VERIFIED.

## 경제성·원본 판정
- KRX weekday private original pair 1565/1565 storage integrity: **historical PASS only**, not rehashed this run. Official calendar, trading status, corporate actions, actual executable prices, cost/tax: **NOT VERIFIED**; 90-day classification and 12003 zero-activity entries excluded.
- OpenDART original/corrected SGML 15 candidate rows and adjacent numeric signatures: **historical narrow PASS**, original-filing semantics, public available-at/PIT and 2021/2022 first 3 months consolidated operating profit period/correction lineage **NOT VERIFIED**.
- Historical entity/security mapping, cost/tax, NetEV, PF, CAGR, MDD, ES95/99, concentration, temporal robustness: **NOT VERIFIED**.
- Chronology Anchor CI **FAIL**; M20 PIT and economic RUN **NO-GO**. Frozen H5 holdout already consumed/failed, no reuse or posthoc tuning. No promotion.
- Independent optimization: offline CI job success **PASS (job completion only)**; cache approval/evidence SHA matching and fail-closed runtime, full speedup **NOT VERIFIED**. Only read-only postprocessing parallelism permitted.

## 안전 경계 및 다음 단계
Frozen H5, M20 horizon20/purge20, WF504/126/126, PIT/Purged/CPCV/independent holdout/Champion/Top3/NO_TRADE, cost/tax/execution/risk gates unchanged. ORDERING=false policy. No market performance experiments, M20 run, strategy search, workflow edits, merges, production deploy, credentials, capital transfers or live orders. Next: obtain official original filing timestamp/lineage proof and historical KRX tradability proof in separate owners' evidence; resolve chronology anchor failure; validate frozen evidence SHA before any economic authorization. Do not modify Work-owned code or reuse holdout.
