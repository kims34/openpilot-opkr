# IndexAlert independent profitability / isolated runtime audit — 2026-11-06 14:17 KST

Scope: read-only source, CI and Railway evidence; document-only isolated write. This is NOT source PIT approval, market performance verification, deployment approval or Champion promotion.

## Current exact refs (GitHub connector, this run)
- Research `index-alert-research-v1`: `df474df348f22aa38b1dedaa59fcff66e548b406`.
- Development `index-alert-position-regen-fix-v1`: `1e6367d2863a86c3470da13d81a955d277eba485`.
- OPEN / DRAFT / UNMERGED: #412 `bf3d9514a87c53b1775e22ec9ba7711f6cecc49f`; #413 `f003ef6247e16fcc71bd3b1b20cd4904c4d984c0`; #414 `18c5418d9684d1717df58261ea27f28e514385b2`; #418 `2f98401cc50a6c6a25808a98516efd5bf0c944ee`; KRX #420 `fab3cbbd63a951a4e081f9e7f08c1391ca308581`, #422 `c14857620973531013799e44625d43080904fd5f`, #423 `0e38004363cac9fc4475556b3a1c445de9af407f`.
- #414 integration gate file `docs/INDEXALERT_PROFITABILITY_INTEGRATION_GATE_2026-10-13.md` blob SHA `984c933651f39f1ee9e26a1d7ac3893aaa5335be` (read at PR #414 head).

## Actions evidence (jobs independently queried this run)
- [38381997417](https://github.com/kims34/openpilot-opkr/actions/runs/38381997417), [38382214223](https://github.com/kims34/openpilot-opkr/actions/runs/38382214223), [38419111311](https://github.com/kims34/openpilot-opkr/actions/runs/38419111311): 6/6 successful each.
- [38419649711](https://github.com/kims34/openpilot-opkr/actions/runs/38419649711): 1/1 successful. Historical 34-case SHA `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34`, 13 adversarial mocks, 28 synthetic tests, serial 2.9656 s vs parallel 2.6209 s = regression phase 1.1315x are **prior evidence**, not independently recalculated today. Whole CI / official historical backtest speed: NOT VERIFIED.
- [38419439742](https://github.com/kims34/openpilot-opkr/actions/runs/38419439742): 2/2 successful, SGML candidate-row matching does NOT certify original semantic period / public available-at.
- [41515392296](https://github.com/kims34/openpilot-opkr/actions/runs/41515392296): auto-anchor FAILURE, validation SKIPPED. PIT admission remains blocked.

## Railway production read-only snapshot
Project `d1c1a050-b7d6-41ce-b300-13c20f82a20a`, environment `83d5840b-270e-4d3f-a941-a37fd4a55ff7`.
- PIT rebuild deployment `8b354fc1-cfb2-4ef0-863e-67f7f5dda2b5` SUCCESS, running 1/1.
- KRX historical worker deployment `16c93d7c-7cd0-4d84-a327-298d2805376c` SUCCESS, running 0/1 (cron idle, not proof of job completion).
- Runtime deployment `eaaa9f67-b9f2-41d2-832c-7d6fad9b9b00` SUCCESS, running 1/1; runtime logs at 2026-11-06 05:17 UTC show Investing.com USD/KRW failure -> Yahoo fallback and ETF closed-market proxy values. These are runtime observations, not approved official PIT or profitability inputs.
- Backend, push, db-query-readonly OFFLINE; db-query-readonly critical 1. Kiwoom real readonly displays online but replicas running 0/crashed 1. Pending Railway environment patch `e113dacb-6705-4416-9997-dc694539d382` STAGED with zero returned change entries; not committed or modified.
- PIT rebuild / KRX worker deploy log queries from 2026-11-06 03:00 UTC returned no entries; old 27/803 OHLC defect remediation NOT VERIFIED.

## Independent PASS / FAIL / NOT VERIFIED
- PASS limited to prior 1,565/1,565 weekday raw-pair storage integrity, not exchange calendar/tradability; current CI job conclusions PASS only for their offline test scope.
- FAIL: chronology anchor job (run 41515392296); H5 / 0-N historical economics promotion gate remains NO-GO per frozen evidence.
- NOT VERIFIED: original-filing semantics and exact public available-at/PIT; 2021/2022 first three-month consolidated operating profit period and restatement lineage; historical corp/security mapping; KRX official session status, corporate actions, executable fills, fees and taxes; independent post-tax annual risk-adjusted NetEV/PF/CAGR/MDD/ES95/99, concentration and temporal robustness; full CI and real backtest speedup; live ORDERING variable (policy requires false).

## Frozen constraints and next safe steps
M20 **NO-GO**. No market performance tests, model exploration, economic replay, holdout reuse or Champion change. Preserve H5, M20 horizon20/purge20, WF504/126/126, PIT/labels/Purged/CPCV/Holdout/Top3/NO_TRADE and frozen cost/risk gates. Cache only with independently approved source/data/code/policy/runtime/approval evidence SHA-256 exact match and fail-closed; parallelize read-only independent postprocessing only, never dependent training or capital transitions. ORDERING=false required; no broker orders, money movements, auth changes, deploy, PR merge, or workflow edits.
Next: resolve chronology anchor provenance failure through authorized independent evidence, validate official original filing availability and corrected Q3 period lineage, reconcile KRX 90 uncertain days and 27 OHLC exceptions with official statuses, then independently audit fill/cost/tax source SHA before any M20 admission. Do not reuse consumed Holdout or dynamic results.
