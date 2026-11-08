# IndexAlert independent audit — 2026-11-09 04:22 KST

Scope: independent read-only GitHub/Railway inspection; offline-only optimization evidence; no M20 economics or live trading.

## Current PR heads (fresh connector reads)
| PR | HEAD | State |
|---|---|---|
| #412 | bf3d9514a87c53b1775e22ec9ba7711f6cecc49f | OPEN Draft |
| #413 | f003ef6247e16fcc71bd3b1b20cd4904c4d984c0 | OPEN Draft |
| #414 | 18c5418d9684d1717df58261ea27f28e514385b2 | OPEN Draft |
| #418 | 2f98401cc50a6c6a25808a98516efd5bf0c944ee | OPEN Draft |
| #420 | fab3cbbd63a951a4e081f9e7f08c1391ca308581 | OPEN Draft |
| #422 | c14857620973531013799e44625d43080904fd5f | OPEN Draft |
| #423 | 0e38004363cac9fc4475556b3a1c445de9af407f | OPEN Draft |

PR #414 gate document blob SHA 984c933651f39f1ee9e26a1d7ac3893aaa5335be (fetched at PR HEAD). Research and development branch exact HEAD not independently resolved this run; prior SHA references df474df348f22aa38b1dedaa59fcff66e548b406 and 1e6367d2863a86c3470da13d81a955d277eba485 are **historical only**.

## GitHub Actions jobs (fresh)
- 38381997417: 6/6 SUCCESS; 38382214223: 6/6 SUCCESS; 38419111311: 6/6 SUCCESS.
- 38419649711: 1/1 SUCCESS, offline isolated runner.
- 38419439742: 2/2 SUCCESS, OpenDART candidate-row verification (not semantic/PIT admission).
- 41515392296: auto-anchor FAILURE; validation SKIPPED. **FAIL** for chronology anchor.
- Historical frozen 34-case SHA: 5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34; not recomputed. Historical regression-phase 2.9656/2.6209 = 1.1315x; total CI and official backtest speed NOT VERIFIED.

## Railway production fresh status
Project d1c1a050-b7d6-41ce-b300-13c20f82a20a, environment 83d5840b-270e-4d3f-a941-a37fd4a55ff7.
- PIT rebuild and runtime: 1/1 running.
- Real readonly: state online and deployment SUCCESS, but **0 running / 1 crashed** (operational discrepancy; no assumption of healthy live execution).
- db-query-readonly offline, 1 critical; backend offline (4 warnings); push offline (1 warning).
- Pending staged patch e113dacb-6705-4416-9997-dc694539d382 with empty changes []; untouched.
- 2026-11-08 18:00–19:25 UTC log search: PIT/KRX/real readonly 0 deploy entries; runtime returned 101 entries (limit 100 per stream; truncated result), including 19:22 UTC index/FX quotes. These are not official KRX/PIT admissibility evidence. No new official source acceptance.

## Gate verdict
- Historical KRX 1565/1565 weekday raw pairs: storage integrity **PASS (historical)**, actual trading calendar/status/halts/corporate actions/execution **NOT VERIFIED**.
- OpenDART SGML 15 candidate rows and adjacent numeric signatures: candidate mechanics **PASS (historical)**, original filing semantics, 2021/2022 exact consolidated first-quarter lineage, public available-at/PIT **NOT VERIFIED**.
- Corporate identity historical mapping, fees/taxes, execution, NetEV/PF/CAGR/MDD/ES95/99, concentration, walk-forward robustness **NOT VERIFIED**.
- Chronology Anchor **FAIL**. M20 PIT and profitability **NO-GO**; H5 spent holdout cannot be reused. No official economic backtest or new model search.
- Frozen H5, M20 horizon20/purge20, WF504/126/126, PIT/label/Purged/CPCV/Holdout/Champion/Top3/NO_TRADE and cost/risk/tax rules unchanged. ORDERING=false policy preserved; no runtime config write performed.
- Optimization limited to synthetic offline tests; fail-closed cache requires approved source/data/code/policy/runtime/evidence SHA-256; only independent read-only postprocessing parallelizable; dependent retraining/capital transition serial.

## Next evidence requirements
1. Resolve failed official chronology anchor and independently prove original filing/public available-at, exact period and correction lineage.
2. Reconcile official KRX calendar, security mapping, statuses, corporate actions and executable fills before any PIT admission.
3. Independently bind immutable source SHA/CI/logs and all cost/tax/risk checks before M20 approval; separately verify end-to-end CI wall time.
4. Diagnose readonly crashed replica and critical DB service in operational track; no deploy/restart without separate permission.

No code, workflow, model, order, Railway configuration, PR merge or deployment changed. This document is independent audit only.
