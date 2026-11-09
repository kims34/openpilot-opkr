# IndexAlert independent audit — 2026-11-09 11:24 KST

Read-only evidence refreshed on this run. No market backtest, model tuning, deployment, workflow modification, PR merge, ORDERING enablement, trading or account changes.

## GitHub immutable refs
- Research index-alert-research-v1 HEAD: df474df348f22aa38b1dedaa59fcff66e548b406
- Development index-alert-position-regen-fix-v1 HEAD: 1e6367d2863a86c3470da13d81a955d277eba485
- All listed PRs OPEN / Draft / unmerged: #412 bf3d9514a87c53b1775e22ec9ba7711f6cecc49f; #413 f003ef6247e16fcc71bd3b1b20cd4904c4d984c0; #414 18c5418d9684d1717df58261ea27f28e514385b2; #418 2f98401cc50a6c6a25808a98516efd5bf0c944ee; KRX #420 fab3cbbd63a951a4e081f9e7f08c1391ca308581; #422 c14857620973531013799e44625d43080904fd5f; #423 0e38004363cac9fc4475556b3a1c445de9af407f.
- PR #414 integration gate docs/INDEXALERT_PROFITABILITY_INTEGRATION_GATE_2026-10-13.md blob SHA 984c933651f39f1ee9e26a1d7ac3893aaa5335be.
- Actions jobs independently queried: 38381997417 6/6 SUCCESS; 38382214223 6/6 SUCCESS; 38419111311 6/6 SUCCESS; 38419649711 1/1 SUCCESS; 38419439742 2/2 SUCCESS; chronology anchor 41515392296 auto-anchor FAILURE and validation SKIPPED.
- Earlier reported 34-case SHA 5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34 and 2.9656/2.6209=1.1315x regression-phase comparison were NOT independently recalculated this run. End-to-end CI / official backtest speedup NOT VERIFIED.

## Railway production read-only evidence
- Project d1c1a050-b7d6-41ce-b300-13c20f82a20a, environment 83d5840b-270e-4d3f-a941-a37fd4a55ff7.
- PIT rebuild and runtime each running 1/1. KRX historical worker reports SUCCESS deployment but 0 running / 0 crashed of 1; not evidence of live trading-calendar validation.
- Kiwoom real readonly: online/SUCCESS surface, replicas 0 running / 1 crashed = runtime health FAIL. db-query-readonly offline with 1 critical; backend and push offline.
- PIT, KRX and Kiwoom real readonly deploy logs queried for 2026-11-09 01:00–02:25 UTC: 0 entries each. Zero logs is not proof of zero activity.
- Pending staged patch e113dacb-6705-4416-9997-dc694539d382 has changes=[]; untouched.
- ORDERING actual live variable value NOT VERIFIED (policy remains false).

## Independent profitability admission
- OpenDART original/correction SGML candidate row numeric adjacency historical evidence: limited technical match PASS; public available-at, original meaning and 2021/2022 first-three-month consolidated operating-income period/correction lineage NOT VERIFIED.
- KRX private 2017–2022 1565/1565 weekday raw pair storage historical integrity PASS; official calendar, security historical identity mapping, corporate actions, tradability, fills, taxes/fees NOT VERIFIED.
- Chronology Anchor job FAIL; PIT source approval NOT VERIFIED.
- NetEV, PF, CAGR, MDD, ES95/99, concentration, temporal robustness after costs/taxes NOT VERIFIED; M20 NO-GO.
- Frozen H5, M20 horizon20/purge20, WF504/126/126, independent holdout/Champion/Top3/NO_TRADE, cache SHA-256 fail-closed and dependent execution serial constraints unchanged.

## Next admissible actions
1. Obtain independent original-filing public timestamps and 2021/2022 consolidated period lineage, source hashes and chronology anchor evidence without reusing consumed holdout.
2. Independently reconcile official KRX calendar/status/corporate actions and historical mappings and execution/cost evidence.
3. Keep optimization limited to synthetic offline safety/parity and read-only postprocessing until independent PIT admission. Do not infer whole-backtest speedup from regression phase.
4. Diagnose readonly crashed replica and offline critical service read-only; do not redeploy or alter credentials.
