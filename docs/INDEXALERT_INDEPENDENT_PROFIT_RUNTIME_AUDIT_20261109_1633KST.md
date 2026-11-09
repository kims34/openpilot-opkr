# IndexAlert 독립 수익성·격리 최적화 감사 — 2026-11-09 16:33 KST

## 이번 실행 직접 검증 (read-only)
- GitHub PR #412 OPEN/Draft head bf3d9514a87c53b1775e22ec9ba7711f6cecc49f; #413 OPEN/Draft head f003ef6247e16fcc71bd3b1b20cd4904c4d984c0; #414 OPEN/Draft head 18c5418d9684d1717df58261ea27f28e514385b2; #418 OPEN/Draft head 2f98401cc50a6c6a25808a98516efd5bf0c944ee.
- KRX PR #420 OPEN/Draft head fab3cbbd63a951a4e081f9e7f08c1391ca308581; #422 OPEN/Draft head c14857620973531013799e44625d43080904fd5f; #423 OPEN/Draft head 0e38004363cac9fc4475556b3a1c445de9af407f. All unmerged.
- Research index-alert-research-v1 and development index-alert-position-regen-fix-v1 exact *current branch tip* NOT VERIFIED. Prior reference SHA df474df348f22aa38b1dedaa59fcff66e548b406 and 1e6367d2863a86c3470da13d81a955d277eba485 must not be asserted as current HEAD. Railway KRX worker deployment metadata commit 1e6367d... is deployment-specific, not branch-tip proof.
- PR #414 gate file docs/INDEXALERT_PROFITABILITY_INTEGRATION_GATE_2026-10-13.md blob SHA 984c933651f39f1ee9e26a1d7ac3893aaa5335be directly fetched at #414 HEAD.
- GitHub Actions jobs directly fetched: 38381997417 6/6 success; 38382214223 6/6 success; 38419111311 6/6 success; 38419649711 1/1 success; 38419439742 2/2 success; chronology anchor 41515392296 auto-anchor FAILURE, validation SKIPPED. Sources: https://github.com/kims34/openpilot-opkr/actions/runs/41515392296 and corresponding /actions/runs/<id>.
- Prior 34-case fixed SHA-256 5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34, 13 adversarial mocks, 28 synthetic, serial 2.9656s vs concurrent 2.6209s (1.1315x) NOT recomputed; offline CI job success PASS only for job completion. Full CI and official backtest acceleration NOT VERIFIED.

## Railway production directly verified
- Project d1c1a050-b7d6-41ce-b300-13c20f82a20a; production environment 83d5840b-270e-4d3f-a941-a37fd4a55ff7.
- PIT rebuild deployment 8b354fc1-cfb2-4ef0-863e-67f7f5dda2b5 SUCCESS, replicas 1 running/0 crashed.
- KRX historical worker deployment 16c93d7c-7cd0-4d84-a327-298d2805376c SUCCESS, replicas 0 running/0 crashed of total 1; no claim of active execution.
- Runtime deployment eaaa9f67-b9f2-41d2-832c-7d6fad9b9b00 SUCCESS, replicas 1 running/0 crashed.
- Real readonly service deployment a77fb922-b679-4d88-92c4-03054ec579cd SUCCESS but replicas **0 running/1 crashed** while service UI state says online: **runtime health FAIL**. Do not equate deploy SUCCESS with service health.
- db-query-readonly offline, 1 critical; backend offline 4 warnings; push offline 1 warning.
- Pending environment patch e113dacb-6705-4416-9997-dc694539d382 staged with empty changes; not accepted.
- Deploy logs queried 2026-11-09T06:20:00Z to 07:40:00Z: PIT 0, KRX 0, real readonly 0; runtime 121 returned (quote/display, not PIT or economic evidence). Log absence is not proof of inactivity.
- ORDERING actual variable value NOT VERIFIED; ORDERING=false remains mandatory policy.

## Evidence-specific verdict
- Official KRX 2017–2022 private 1565/1565 weekday original pair storage integrity: historical narrow PASS, not independently rehashed this run. Official exchange calendar/status, corporate actions, tradability/execution, costs/taxes: NOT VERIFIED. 90-day classification and 12003 zero-activity samples excluded.
- OpenDART original/corrected SGML candidate 15 rows/numeric-adjacency: historical narrow PASS, not re-derived. Original-filing meaning, precise public available-at/PIT, 2021/2022 first-three-month consolidated operating profit period and correction lineage: NOT VERIFIED.
- Historical entity/security mapping, post-tax NetEV/PF/CAGR/MDD/ES95/99, concentration, time robustness: NOT VERIFIED.
- Chronology Anchor FAIL; M20 original PIT and economic RUN **NO-GO**; H5 failed/consumed holdout and Dynamic results may not be reused or tuned.
- Frozen H5, M20 horizon20/purge20, WF504/126/126, PIT/Purged/CPCV/independent Holdout/Champion/Top3/NO_TRADE and all cost/tax/execution/risk/promotion thresholds unchanged. Cache fail-closed unless all independent approved source/data/code/frozen/runtime/approval SHA-256 match; parallelize only read-only postprocessing, never dependent retraining/capital transitions.

## Next independent gates
1. Obtain independently hash-anchored official original filing timestamps, amendment lineage, and period semantics from responsible OpenDART evidence owner; do not infer public available-at from SGML row matching.
2. Obtain official historical KRX calendar/trading-state/corporate-action/feasible fill proof with exact source SHA from KRX owner.
3. Resolve chronology anchor failure and validate evidence hash chain before considering any M20 PIT authorization. Check real-readonly crashed replica with deployment logs, without restarting/deploying.
4. Independently prove exact current research/development branch tips and frozen cache evidence fingerprints.
No market profitability run, strategy search, holdout reuse, workflow modification, merge, deployment, ordering enablement, account change, live order, or promotion performed.
