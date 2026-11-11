# IndexAlert independent profitability and isolated optimization audit — 2026-11-11 12:17 KST

## Scope and provenance
Read-only connector inspection of GitHub kims34/openpilot-opkr and Railway IndexAlert production. No workflow/code changes, no official market backtest, no deploy/merge/trade/champion promotion. This audit branch is independent of PR #412/#413/#414/#418 and KRX PRs #420/#422/#423.

- Research HEAD: df474df348f22aa38b1dedaa59fcff66e548b406 (compare API base commit).
- Development HEAD: 1e6367d2863a86c3470da13d81a955d277eba485 (compare API base commit).
- Research vs development: diverged, research 281 ahead / 1148 behind; merge-base c490974ff6619bb978dc6f83f9c24f2c46622f85.
- PR #412/#413/#414/#418/#420/#422/#423 changed-file lists returned successfully; live draft/open status and each PR HEAD not independently established this run. PR #414 integration document could not be read at research ref (404); NOT VERIFIED.
- Actions job inspection: 38381997417 6/6 success; 38382214223 6/6; 38419111311 6/6; 38419649711 1/1; 38419439742 2/2; 38498552499 6/6. This proves job conclusions only, not immutable fixture bytes or admission. Historical fixed 34-case SHA-256 claimed 5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34; NOT independently recalculated.
- Prior PR #418 synthetic 28, PR #413 adversarial 13/21, timings 2.9656 vs 2.6209 sec and 1.7114 vs 2.5776 sec are historical reported results, not newly reproduced. Official backtest speed-up NOT VERIFIED; serial/parallel regression-phase 1.1315x is not end-to-end speed-up.

## Railway production
Project d1c1a050-b7d6-41ce-b300-13c20f82a20a; environment 83d5840b-270e-4d3f-a941-a37fd4a55ff7.
- PIT rebuild deployment 8b354fc1-cfb2-4ef0-863e-67f7f5dda2b5 SUCCESS, running 1/1.
- Runtime eaaa9f67-b9f2-41d2-832c-7d6fad9b9b00 SUCCESS, running 1/1.
- KRX worker 16c93d7c-7cd0-4d84-a327-298d2805376c SUCCESS, running 0/1, live availability NOT VERIFIED.
- Kiwoom real readonly a77fb922-b679-4d88-92c4-03054ec579cd SUCCESS but running 0/1, crashed 1/1: runtime FAIL despite UI online state.
- Backend and push offline with failed latest deployments; db-query-readonly offline, 1 critical issue.
- PIT/KRX/Kiwoom deploy log query from 2026-11-11 01:00Z returned 0 entries each. Absence of logs is not evidence of health.
- Environment description staged=null, while environment_status reports pending patch e113dacb-6705-4416-9997-dc694539d382 with zero changes; contradictory metadata, do not apply.

## Independent economic admission gate
- 2026-10-14 OpenDART original/corrected SGML 15 candidate rows and adjacent number signatures: historical narrow test PASS; original filing semantic correctness, 2021/2022 initial consolidated 3-month operating profit, period/correction lineage, precise public available-at/PIT: NOT VERIFIED.
- 2017–2022 KRX private weekday pairs 1565/1565: historical storage-integrity PASS only. Official exchange calendar, trading status, corporate actions, executable fills, fees and taxes: NOT VERIFIED. 90-day classification and zero-activity 12003 external exclusion remain blocked.
- Historical company/security mapping and time-consistent membership: NOT VERIFIED.
- After-cost/tax NetEV, PF, CAGR, MDD, ES95/ES99, return concentration and regime/time robustness: NOT VERIFIED. M20 source PIT and profitability RUN: NO-GO.
- H5 failed/consumed holdout and Dynamic results cannot be reused independently or retroactively tuned.
- Frozen H5 and M20 horizon20/purge20 WF504/126/126, PIT/label/Purged/CPCV/independent Holdout/Champion/Top3/NO_TRADE and all costs, taxes, risk and promotion thresholds unchanged. ORDERING=false remains required but live env value was not independently inspected.
- Cache requires independently approved original source/data/code/Frozen policy/runtime and admission evidence SHA-256 matching, fail-closed. Only read-only independent postprocessing can parallelize; no dependent retraining or capital transition parallelism.

## Next safe steps
1. Obtain original filing source bytes and time-stamped public available-at proof for 2021 and 2022 first consolidated 3-month operating profit, independent original/correction lineage verification.
2. Obtain official KRX calendar/status/corporate-action/tradability evidence with source SHA and resolve 90-day/abnormal-price exceptions without lifting the zero-activity exclusion.
3. Read-only reconcile Railway KRX worker and Kiwoom crashed replicas with diagnostic logs; no service configuration changes without explicit approval.
4. Independently verify frozen 34-case fixture SHA and PR #413/#418 isolated offline CI only. Do not run M20 economics or new market performance tests before source PIT admission.
5. Preserve independent gates and no PR merge/deployment/real orders/capital movement/credential changes/champion promotion.
