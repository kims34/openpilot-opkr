# IndexAlert independent audit — 2026-11-09 09:16 KST

Read-only evidence collected in this run; historical user-supplied assertions are not newly certified.

## GitHub
- Repository kims34/openpilot-opkr: branch search confirms index-alert-research-v1, index-alert-position-regen-fix-v1, and indexalert-independent-audit-20261108-1921kst exist. Search endpoint does NOT expose HEAD SHA; current exact branch tips NOT VERIFIED. Previous audit recorded research df474df348f22aa38b1dedaa59fcff66e548b406 and development 1e6367d2863a86c3470da13d81a955d277eba485; do not treat as fresh HEAD.
- GitHub PR search for #412/#413/#414/#418/#420/#422/#423 returned no results in this run. Consequently latest PR state, draft flags, merge state, and exact HEADs NOT VERIFIED; no inference that PRs were deleted. Previous PR #414 document blob 984c933651f39f1ee9e26a1d7ac3893aaa5335be is historical.
- Fetching docs/INDEXALERT_PROFITABILITY_INTEGRATION_GATE_2026-10-13.md on research branch returned NOT_FOUND, not proof that it is absent from PR #414.
- Actions jobs independently fetched: 38381997417 6/6 success; 38382214223 6/6 success; 38419111311 6/6 success; 38419649711 1/1 success; OpenDART 38419439742 2/2 success. Chronology 41515392296 auto-anchor FAIL at public hash-only prospective payload fetch; validation SKIPPED.
- Historical 34-case SHA-256 5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34, 13 adversarial mocks, 28 synthetic controls and serial 2.9656s vs concurrent 2.6209s (1.1315x) were not independently recomputed; full CI and official backtest speedup NOT VERIFIED.

## Railway production
Project d1c1a050-b7d6-41ce-b300-13c20f82a20a; environment 83d5840b-270e-4d3f-a941-a37fd4a55ff7. environment_status directly queried:
- PIT rebuild 1 running / 0 crashed; Runtime 1 running / 0 crashed.
- indexalert-kiwoom-real-readonly UI state online, but 0 running / 1 crashed: runtime health FAIL. This is NOT evidence that trading is enabled.
- db-query-readonly offline with 1 critical; Backend offline 4 warnings; Push offline 1 warning.
- KRX historical worker SUCCESS deployment but 0 running / 0 crashed / total 1; no claim of continuous worker execution.
- Pending empty staged patch e113dacb-6705-4416-9997-dc694539d382 exists, not applied.
- Deploy logs 2026-11-08 23:00Z to 2026-11-09 00:20Z: PIT 0, KRX 0, real-readonly 0. Runtime has ETF proxy display logs around 00:13Z, not official PIT or execution evidence. Absence of log lines does not certify health. ORDERING environment value not independently read; policy remains false, not a verified runtime value.

## Independent PASS/FAIL/NOT VERIFIED
- Offline CI job completion: PASS for the exact named historical runs only; fixture parity SHA, whole-CI acceleration and official economic runtime: NOT VERIFIED.
- Chronology Anchor 41515392296: FAIL; downstream validation SKIPPED.
- Official original filing / public available-at PIT, 2021/2022 first-three-month consolidated operating-profit period/correction lineage, issuer/security historical mapping: NOT VERIFIED.
- KRX 2017–2022 1565/1565 weekday raw-pair integrity is prior historical evidence only; official calendar, security status, corporate actions, executable fills, fees/taxes NOT VERIFIED. Historical zero-activity 12003 records remain excluded.
- NetEV, PF, CAGR, MDD, ES95/99, return concentration and temporal robustness after all costs and taxes: NOT VERIFIED. M20 NO-GO.
- Real-readonly service actual running health: FAIL (0 running / 1 crashed).

## Frozen constraints and safe next steps
No M20 economic run, new official-market profitability test, model search, holdout reuse, or parameter changes before original-filing PIT, chronology and KRX official evidence independently pass. Maintain Frozen H5, M20 horizon20/purge20, WF504/126/126, PIT/label/Purged/CPCV/independent Holdout/Champion/Top3/NO_TRADE and all frozen cost/tax/risk/promotion gates. Keep ORDERING=false; fail-closed cache only with approved source/data/code/Frozen policy/runtime/approval evidence SHA-256; parallelize only independent read-only postprocessing, not dependent retraining or capital transitions. Next read-only checks: exact PR/branch SHA via authorized PR endpoint, chronology failure logs, original-filing time lineage, official KRX status, runtime crash logs. No workflow changes, PR merge, deployment, orders, fund movement, credentials changes, or Champion promotion.
