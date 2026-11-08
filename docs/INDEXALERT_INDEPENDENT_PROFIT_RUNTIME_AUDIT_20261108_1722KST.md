# IndexAlert independent evidence audit — 2026-11-08 17:22 KST

Read-only audit of source PRs/CI and Railway; isolated documentation-only commit. No source/CI workflow/data/model/deployment/ordering modifications. Previous branch indexalert-independent-audit-20261108-1516kst was absent in exact branch search; this is a newly isolated branch based on verified development SHA.

## Source identity and PRs
- Research index-alert-research-v1: compared to 3b8b7830612a6284d7c7a60628cb527cb741627a; **ahead 2 / behind 0**. Changed files: docs/INDEXALERT_INDEPENDENT_PROFIT_RUNTIME_AUDIT_20261103_1323KST.md and docs/independent-audit/2026-11-03-1045-kst-readonly-audit.md. Exact current research HEAD not independently returned by compare API, NOT VERIFIED.
- Development index-alert-position-regen-fix-v1: **identical** to 1e6367d2863a86c3470da13d81a955d277eba485.
- OPEN Draft unmerged PRs: #412 bf3d9514a87c53b1775e22ec9ba7711f6cecc49f; #413 f003ef6247e16fcc71bd3b1b20cd4904c4d984c0; #414 18c5418d9684d1717df58261ea27f28e514385b2; #418 2f98401cc50a6c6a25808a98516efd5bf0c944ee; KRX #420 fab3cbbd63a951a4e081f9e7f08c1391ca308581, #422 c14857620973531013799e44625d43080904fd5f, #423 0e38004363cac9fc4475556b3a1c445de9af407f.
- PR #414 gate document docs/INDEXALERT_PROFITABILITY_INTEGRATION_GATE_2026-10-13.md blob SHA 984c933651f39f1ee9e26a1d7ac3893aaa5335be. Gate lives on PR branch, not research base.

## CI independently queried
- GitHub Actions 38381997417, 38382214223, 38419111311: each 6/6 jobs SUCCESS.
- 38419649711: 1/1 SUCCESS; 38419439742: 2/2 SUCCESS.
- 41515392296: auto-anchor FAILURE, validation SKIPPED (FAIL). Frozen 34-case identity SHA 5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34 and 13 adversarial / 28 synthetic assertions are previously reported, not re-hashed from artifacts this run.
- Single-runner 2.9656s versus concurrent 2.6209s (regression-phase ratio 1.1315x) is prior limited measurement; full CI / official market backtest speed NOT VERIFIED.

## Railway production 2026-11-08
- Project d1c1a050-b7d6-41ce-b300-13c20f82a20a, environment 83d5840b-270e-4d3f-a941-a37fd4a55ff7.
- PIT rebuild running 1/1; runtime running 1/1. Kiwoom real read-only is marked online with SUCCESS deployment a77fb922-b679-4d88-92c4-03054ec579cd yet replica running 0 / crashed 1: operational discrepancy **FAIL**. db-query-readonly offline Critical 1; backend offline warnings 4; push offline warning 1.
- KRX historical worker deployment SUCCESS but replica running 0 / crashed 0 / total 1; do not infer active execution.
- PIT, KRX, real-readonly deploy logs since 2026-11-08T06:00Z: 0 each, therefore OHLC 27 anomalies and source gate resolution NOT VERIFIED. Runtime returned recent USDKRW Yahoo/ECOS and KOSPI Naver quote log entries; these are not official backtest admission evidence.
- Pending staged environment patch e113dacb-6705-4416-9997-dc694539d382, changes []: do not commit or alter.

## Frozen admission matrix
- OpenDART original/correction SGML candidate-row signature: prior 15-row shape evidence; original standalone 2021/2022 first three-month consolidated operating profit, period/correction lineage, exact public available-at PIT: **NOT VERIFIED / FAIL-CLOSED**.
- KRX 2017–2022 1565/1565 weekday pairs: prior storage integrity **PASS ONLY**; official exchange calendar/status, corporate actions, historical security mapping, executable fills and fees/taxes: **NOT VERIFIED / FAIL-CLOSED**. 12003 zero-activity and 27 suspicious OHLC items remain vetoed.
- NetEV, PF, CAGR, MDD, ES95/99, concentration, cross-period robustness after all costs/taxes: **NOT VERIFIED**; no authorized M20 profitability run.
- Chronology anchor CI **FAIL**. Offline CI job completion **PASS within synthetic scope only**. Economic promotion **NO-GO**.

## Constraints / next gate
Keep Frozen H5, M20 horizon20/purge20, WF504/126/126, PIT/labels/Purged/CPCV/Holdout/Champion/Top3/NO_TRADE, costs/taxes/fill/risk gates unchanged. H5 failed/consumed Holdout and Dynamic results may not be retuned or reused. Cache must fail-closed on all independently approved SHA-256 inputs/policy/runtime evidence; parallelize read-only independent postprocessing only, never dependent retraining/capital transitions. ORDERING=false; no orders, funds, account changes, Champion promotion, deployment, PR merge, official M20 performance experiment or workflow edits. Next: DART original-filing PIT and KRX historical execution proofs from owner tracks; resolve chronology FAIL and Railway replica discrepancy with independent evidence; only then reassess authorization.