# IndexAlert independent audit — 2026-11-08 21:18 KST

Scope: read-only GitHub + Railway evidence; no PIT admission, no market returns, no M20 economic run, no deployment or order. Independent audit branch base HEAD before this file: `09f2af4d798b789451c7f2ec416e7ef7b5abc109`.

## Exact refs
- research `index-alert-research-v1`: `df474df348f22aa38b1dedaa59fcff66e548b406`
- development `index-alert-position-regen-fix-v1`: `1e6367d2863a86c3470da13d81a955d277eba485`
- OPEN/DRAFT PR heads: #412 `bf3d9514a87c53b1775e22ec9ba7711f6cecc49f`; #413 `f003ef6247e16fcc71bd3b1b20cd4904c4d984c0`; #414 `18c5418d9684d1717df58261ea27f28e514385b2`; #418 `2f98401cc50a6c6a25808a98516efd5bf0c944ee`; #420 `fab3cbbd63a951a4e081f9e7f08c1391ca308581`; #422 `c14857620973531013799e44625d43080904fd5f`; #423 `0e38004363cac9fc4475556b3a1c445de9af407f`.
- PR #414 gate file `docs/INDEXALERT_PROFITABILITY_INTEGRATION_GATE_2026-10-13.md` blob SHA `984c933651f39f1ee9e26a1d7ac3893aaa5335be` verified against head.

## CI source results (latest-at-query historical run IDs)
- #38381997417: 6/6 success; #38382214223: 6/6 success; #38419111311: 6/6 success; #38419649711: 1/1 success; OpenDART #38419439742: 2/2 success. This proves those job conclusions only. Previously reported fixed 34-case SHA `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34`, synthetic 28 cases and serial 2.9656s / concurrent 2.6209s were not independently recomputed today. Whole-CI and official backtest acceleration NOT VERIFIED.
- Chronology Anchor #41515392296 auto-anchor FAIL, validation SKIPPED. Job #125517531544 logs end with `urllib.error.HTTPError: HTTP Error 404: Not Found` on external anchor retrieval, so chronology evidence NOT VERIFIED, not a proof of valid PIT.

## Railway production observations
Project `d1c1a050-b7d6-41ce-b300-13c20f82a20a`; production environment `83d5840b-270e-4d3f-a941-a37fd4a55ff7`.
- PIT rebuild `225f2279-d728-4e1a-a3f3-2447ff0f9dc1` 1 running / 0 crashed. 2026-11-08 19:00–21:15 KST sampled deploy logs repeatedly emit `KRXProspectiveOpenAPISourceError / COMMON_OHLC_NONPOSITIVE`, `fresh_alpha_observation_admitted=false`, `live_order_authorized=false`, `independent_source_admission_verified=false`. This is repeated processing of a historical source problem, not proof of a new trading-day anomaly.
- KRX historical worker `003812ee-102b-42b6-bda4-36925885b428` settled deployment SUCCESS, zero active replicas (worker/cron lifecycle); no new logs in queried 19:00–21:18 KST window.
- Real readonly `93074d5f-70b3-48e4-8671-a3c5b23daf7e` UI state online and deployment SUCCESS but replica running=0, crashed=1 (critical operational discrepancy); zero queried new deploy logs.
- Runtime `37902fde-ca05-43e0-bc76-278992bf7732` running=1. Latest queried logs include USDKRW Investing.com HTTP failure -> Yahoo fallback; not official backtest evidence.
- db-query-readonly offline + 1 critical; backend offline + 4 warnings; push offline + 1 warning.
- Environment staged pending patch `e113dacb-6705-4416-9997-dc694539d382` has empty changes; do not apply.

## Independent admission decisions
- KRX 2017–2022 1565/1565 private raw weekday pair persistence integrity: historical PASS for storage only, not independent current recalculation.
- OpenDART original-filing meaning, exact public available-at, 2021/2022 first Q3 consolidated operating-profit period/correction lineage: NOT VERIFIED.
- Historical corporate/security mapping, official KRX trading calendar/status, halts, corporate actions, tradability and execution: NOT VERIFIED.
- Cost/tax-adjusted NetEV, PF, CAGR, MDD, ES95/99, concentration and walk-forward stability: NOT VERIFIED; no official economic execution permitted.
- Chronology anchor action: FAIL; dependent validation SKIPPED. Optimization offline CI job outcomes: PASS for CI completion only; full speedup NOT VERIFIED.
- M20 PIT/returns: NO-GO. ORDERING=false. No holdout reuse or posthoc frozen H5 adjustment.

## Next safe work
Obtain independent source-authorized original filing and timestamp lineage and official KRX calendar/trading-status/corporate-action evidence with SHA provenance; fix chronology anchor retrieval via authorized owner process and rerun independent validation only after source approval; diagnose repeated nonpositive OHLC and crashed readonly replica without deployment or changes to shared code. For optimization, only synthetic offline safety/parity and fail-closed cache SHA-policy checks in isolated work, never dependent model/capital transitions in parallel. Frozen H5, M20 horizon20/purge20, WF504/126/126, holdout/Champion/Top3/NO_TRADE, costs, taxes and risk thresholds unchanged. No code/workflow changes, PR merges, production deploy, trading, fund transfers, account auth changes, or Champion promotion authorized.
