# IndexAlert independent profitability and runtime audit — 2026-11-11 04:22 KST

Scope: read-only independent evidence check; no strategy, economic experiment, merge, deployment or ordering authorisation. Sources checked this run via GitHub repository/PR/Actions APIs and Railway production environment_status/get_logs.

## Exact GitHub HEADs
- research index-alert-research-v1: df474df348f22aa38b1dedaa59fcff66e548b406
- development index-alert-position-regen-fix-v1: 1e6367d2863a86c3470da13d81a955d277eba485
- PR #412: bf3d9514a87c53b1775e22ec9ba7711f6cecc49f
- PR #413: f003ef6247e16fcc71bd3b1b20cd4904c4d984c0
- PR #414: 18c5418d9684d1717df58261ea27f28e514385b2
- PR #418: 2f98401cc50a6c6a25808a98516efd5bf0c944ee
- KRX PR #420: fab3cbbd63a951a4e081f9e7f08c1391ca308581
- KRX PR #422: c14857620973531013799e44625d43080904fd5f
- KRX PR #423: 0e38004363cac9fc4475556b3a1c445de9af407f
All seven PRs open, draft, unmerged at lookup. PR #414 gate document blob SHA 984c933651f39f1ee9e26a1d7ac3893aaa5335be.

## CI evidence
- Runs 38381997417 (HEAD 55e7fe2b3fe322e39f817914ff1ed5b589bbe0da), 38382214223 (05d73661bcc879fe0dd66ffcea5fe1f5ee6fbd56), 38419111311 (b22e4f39517c2bc38e173e63e8fd52f29a535dad): each 6/6 jobs success.
- Run 38419649711 (8f363b8683d34a48754916b34810a5a8bb958896): 1/1 success.
- OpenDART run 38419439742 (39af5b0043e122bc0e42935d8813759ff6c1a6e7): 2/2 success.
- Offline CI outcome PASS (job conclusion only); claimed 34-case SHA 5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34, 13 adversarial and 28 synthetic counts NOT independently recomputed this run.
- Reported serial 2.9656 s / concurrent 2.6209 s = 1.1315x for regression phase only; end-to-end CI and official backtest acceleration NOT VERIFIED.

## Railway production
Project d1c1a050-b7d6-41ce-b300-13c20f82a20a, environment 83d5840b-270e-4d3f-a941-a37fd4a55ff7. PIT rebuild 1/1 running; runtime 1/1 running. KRX worker 0/1 running, 0 crashed, actual execution NOT VERIFIED. Kiwoom real readonly 0/1 running and 1 crashed: replica health FAIL notwithstanding deployment SUCCESS/UI online. Backend and Push offline; db-query-readonly offline with 1 critical issue. Pending empty staged patch e113dacb-6705-4416-9997-dc694539d382; DO NOT apply. PIT, KRX and Kiwoom deploy logs returned zero entries for 2026-11-10 18:00–19:22 UTC: no fresh runtime approval evidence.

## Profitability gate
- KRX 2017–2022 private 1565/1565 weekday raw-pair storage integrity: historical PASS only; official holiday/calendar/status, corporate actions, fillability and costs/taxes NOT VERIFIED.
- Original-filing OpenDART, public available-at/PIT, 2021/2022 first 3-month consolidated operating-profit period and amendment lineage: NOT VERIFIED; SGML candidate row signature match is not semantic/timestamp approval.
- Historical entity/security mapping, realistic execution, tax, NetEV, PF, CAGR, MDD, ES95/99, return concentration and temporal robustness: NOT VERIFIED.
- H5 consumed/failed holdout may not be retuned/reused. M20 source PIT and economic run NO-GO; no new market backtest/model search.
- Frozen H5, M20 horizon20/purge20, WF504/126/126, PIT/labels/Purged/CPCV/independent Holdout/Champion/Top3/NO_TRADE, costs/taxes/risk/promotion criteria unchanged. ORDERING=false required; current environment variable value NOT independently inspected. No orders, funds, credential changes, Champion promotion, merge or deploy.
- Cache only on independent approved source/data/code/frozen policy/runtime/approval evidence SHA-256 match; fail-closed. Parallelise read-only postprocessing only, never dependent retraining or capital transition.

## Next safe steps
1. Independently verify official original-filing timestamps and 2021/2022 consolidated first-quarter period/lineage using approved private evidence, not candidate row signatures alone.
2. Independently reconcile KRX official sessions, statuses, corporate actions, execution and tax schedule before any economic run.
3. Offline-only CI artefact/hash re-computation and synthetic policy safety checks in a separate sandbox; do not duplicate PR #413/#418 owned code.
4. Diagnose readonly Kiwoom crashed replica and missing runtime logs without restart/deploy/credential changes.
5. Keep M20 NO-GO until explicit source PIT gate approval; do not alter Frozen policies.
