# IndexAlert independent audit — 2026-11-10 08:17 KST

Read-only GitHub/Railway inspection. This audit document is the only intended write. No trading, workflow edits, merges, deployments, PIT/performance runs, or changes to another Work's code.

## Source refs checked
- Research `index-alert-research-v1`: `df474df348f22aa38b1dedaa59fcff66e548b406`.
- Development `index-alert-position-regen-fix-v1`: `1e6367d2863a86c3470da13d81a955d277eba485`.
- GitHub compare: DIVERGED, research 281 ahead and 1148 behind development (comparison base development, head research).
- All OPEN, Draft, unmerged: PR #412 `bf3d9514a87c53b1775e22ec9ba7711f6cecc49f`; #413 `f003ef6247e16fcc71bd3b1b20cd4904c4d984c0`; #414 `18c5418d9684d1717df58261ea27f28e514385b2`; #418 `2f98401cc50a6c6a25808a98516efd5bf0c944ee`; KRX #420 `fab3cbbd63a951a4e081f9e7f08c1391ca308581`, #422 `c14857620973531013799e44625d43080904fd5f`, #423 `0e38004363cac9fc4475556b3a1c445de9af407f`.
- Integration gate `docs/INDEXALERT_PROFITABILITY_INTEGRATION_GATE_2026-10-13.md` read from PR #414 branch (not research base).

## Verified CI scope
- Actions 38381997417, 38382214223, 38419111311: 6/6 completed successful jobs each.
- Action 38419649711: 1/1 successful offline one-runner job.
- Action 38419439742: 2/2 successful OpenDART row security/candidate-diff jobs; job success does not approve exact consolidated 3-month PIT values or original public available-at.
- Action 41515392296: auto-anchor FAIL, validation SKIPPED.
- Prior 34-case SHA `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34` and 2.9656s/2.6209s = 1.1315x are historical evidence, not newly rehashed in this run. Entire CI/official backtest acceleration NOT VERIFIED.

## Railway production
- Project `d1c1a050-b7d6-41ce-b300-13c20f82a20a`, production `83d5840b-270e-4d3f-a941-a37fd4a55ff7`; staged=null.
- Latest deployments: PIT rebuild SUCCESS (2026-10-10, `e57054ecdb3e734ced3c9a981b887d9b5fc60f97`), KRX worker SUCCESS (2026-10-12, `1e6367d2863a86c3470da13d81a955d277eba485`), runtime SUCCESS (2026-10-05, `8a68b01bca5d551d083ccda263df38d86fa54166`), real-readonly-run SUCCESS (2026-10-10), backend FAILED and push FAILED (2026-09-23).
- Environment configured replicas=1 for these services; configured replicas and deployment SUCCESS do not prove running health.
- Since 2026-11-09 21:00 UTC, PIT/KRX/real-readonly-run deploy log queries returned zero entries. Runtime returned entries at 2026-11-09 23:16:46 UTC, including Investing USDKRW HTTPError and Yahoo fallback. This is an operational fallback observation, not M20 market-source PIT evidence.
- Previously reported 27/803 invalid OHLC and real-readonly-run crashed replica are NOT VERIFIED as resolved or still occurring this run; runtime status requires independent health check.

## Independent gate decision
| Domain | Decision |
|---|---|
| KRX 2017–2022 private source pair integrity (historical 1565/1565) | PASS for storage SHA scope only; not rehashed today |
| Original filing 2021/2022 consolidated 3-month operating profit, correction lineage, public available-at | NOT VERIFIED |
| Historical corp/security mapping, KRX trading status, corporate actions, execution and costs/tax | NOT VERIFIED |
| M20 original-source PIT admission and performance execution | FAIL-CLOSED / NO-GO |
| After-tax NetEV, PF, CAGR, MDD, ES95/99, concentration and time robustness | NOT VERIFIED / not run |
| Offline optimization CI jobs | PASS for specified job execution, no market profitability claim |
| Runtime backend/push latest deployment | FAIL |
| Chronology anchor validation | FAIL / SKIPPED |

Frozen H5, M20 horizon20/purge20 WF504/126/126, PIT/label/Purged/CPCV/Holdout/Champion/Top3/NO_TRADE, risk/cost/tax/execution criteria remain unchanged. ORDERING=false; no promotion, trading, capital, account authority, deployment or PR merge. No H5 holdout reuse, dynamic post-hoc tuning, official backtest, model search or M20 economics.

Next: independent OpenDART original 3-month CFS and available-at lineage, KRX calendar/status/corporate-action executable evidence, runtime health, and exact source/data/code/frozen/runtime approval SHA-256 cache key verification. Only synthetic offline tests and independent read-only postprocessing permitted until source PIT approval.