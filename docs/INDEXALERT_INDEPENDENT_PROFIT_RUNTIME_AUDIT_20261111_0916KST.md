# IndexAlert independent audit — 2026-11-11 09:16 KST

Read-only audit. No market performance execution, strategy changes, workflow changes, merge, deployment or ordering.

## Exact source refs
- Development index-alert-position-regen-fix-v1: 1e6367d2863a86c3470da13d81a955d277eba485 (GitHub compare base commit).
- Research index-alert-research-v1: diverged, compare development...research ahead 281 / behind 1148, merge base c490974ff6619bb978dc6f83f9c24f2c46622f85; research HEAD SHA not independently resolved by compare response.
- PR #412 bf3d9514a87c53b1775e22ec9ba7711f6cecc49f; #413 f003ef6247e16fcc71bd3b1b20cd4904c4d984c0; #414 18c5418d9684d1717df58261ea27f28e514385b2; #418 2f98401cc50a6c6a25808a98516efd5bf0c944ee; #420 fab3cbbd63a951a4e081f9e7f08c1391ca308581; #422 c14857620973531013799e44625d43080904fd5f; #423 0e38004363cac9fc4475556b3a1c445de9af407f. All OPEN, Draft, unmerged at inspection.
- PR #414 gate docs/INDEXALERT_PROFITABILITY_INTEGRATION_GATE_2026-10-13.md blob SHA 984c933651f39f1ee9e26a1d7ac3893aaa5335be.
- GitHub Actions: 38381997417 6/6 SUCCESS; 38382214223 6/6 SUCCESS; 38419111311 6/6 SUCCESS; 38419649711 1/1 SUCCESS; 38419439742 2/2 SUCCESS; 38498552499 6/6 SUCCESS. Jobs inspected directly, no individual output digest independently recomputed.
- Historical fixed 34-case SHA 5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34 is prior evidence, NOT freshly recalculated.
- Offline runner 2.9656s serial / 2.6209s concurrent = 1.1315x regression-phase ratio (prior evidence only). Subsequent #413 1.7114s serial / 2.5776s parallel is slower (prior evidence). Full CI and official backtest acceleration NOT VERIFIED.

## Railway production (read-only)
Project d1c1a050-b7d6-41ce-b300-13c20f82a20a, environment 83d5840b-270e-4d3f-a941-a37fd4a55ff7.
- PIT rebuild deployment 8b354fc1-cfb2-4ef0-863e-67f7f5dda2b5 SUCCESS, replica 1 running / 1.
- Runtime eaaa9f67-b9f2-41d2-832c-7d6fad9b9b00 SUCCESS, replica 1/1. Recent runtime logs contain market quote activity, NOT M20 PIT approval.
- KRX worker 16c93d7c-7cd0-4d84-a327-298d2805376c SUCCESS, replica 0 running / 1; operational readiness NOT VERIFIED.
- Kiwoom real read-only a77fb922-b679-4d88-92c4-03054ec579cd SUCCESS deployment but 0 running / 1 crashed: runtime FAIL.
- Backend, Push, db-query-readonly offline; db-query-readonly 1 critical issue.
- PIT/KRX/Kiwoom logs 2026-11-11 00:00–00:25 UTC returned 0 entries; Runtime returned 101 entries (tool limit 100 per stream), not a source validation.
- Pending patch e113dacb-6705-4416-9997-dc694539d382 staged with zero changes; untouched.

## Independent gate verdict
- Historical KRX 1565/1565 weekday original-pair storage integrity: PASS only for earlier proven storage evidence, not rehashed this run.
- OpenDART 2022 original/correction candidate rows 15 and adjacent numeric signatures: historical partial evidence; original meaning, first-filed 2021/2022 CFS exact three-month periods, amendment lineage and public available-at: NOT VERIFIED.
- Historical corporation/security mappings; official KRX calendar, security status, corporate actions, executable fills and costs/taxes: NOT VERIFIED. Keep 90 uncertain sessions, 12003 zero-activity veto and 27 abnormal OHLC veto closed.
- NetEV, PF, CAGR, MDD, ES95/99, profit concentration, year/date robustness and after-tax risk-adjusted annual net profitability: NOT VERIFIED. M20 source/PIT gate NO-GO; economic RUN forbidden.
- Synthetic offline CI job completion: PASS for execution status only. Fixed test digest, 13 adversarial mocks, 28 additional synthetic cases not independently rehashed this run. Full speedup NOT VERIFIED.
- H5 failed/consumed holdout not reusable. Frozen H5/M20 horizon20 purge20 WF504/126/126, Purged/CPCV, independent holdout, Top3/NO_TRADE, costs/taxes and promotion thresholds unchanged.
- Cache only with independently approved source/data/code/frozen/runtime/evidence SHA-256 fail-closed; only independent read-only post-processing parallel; dependent retraining/capital transitions serial.
- ORDERING=false required; actual live env var not independently inspected. No live orders, funds, account/auth changes, Champion promotion, PR merges, deployment or workflows touched.

## Next safe evidence steps
Independent original filing exact period and public timestamp lineage; KRX official calendar/status/corporate-action reconciliation and OHLC veto resolution; historical security mapping and tax/fill evidence; rerun isolated offline synthetic parity only after existing work ownership check. Do not launch M20 or performance search until source PIT and market gates independently PASS.
