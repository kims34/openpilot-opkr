# IndexAlert independent audit — 2026-11-14 21:21 KST

Read-only source inspection; no official market backtest, model search, deployment, merge, trade, or policy change.

## Exact GitHub source refs (GitHub REST live reads)
- research index-alert-research-v1 HEAD: `df474df348f22aa38b1dedaa59fcff66e548b406`
- development index-alert-position-regen-fix-v1 HEAD: `1e6367d2863a86c3470da13d81a955d277eba485`
- Draft/unmerged PR HEADs: #412 `bf3d9514a87c53b1775e22ec9ba7711f6cecc49f`; #413 `f003ef6247e16fcc71bd3b1b20cd4904c4d984c0`; #414 `18c5418d9684d1717df58261ea27f28e514385b2`; #418 `2f98401cc50a6c6a25808a98516efd5bf0c944ee`; KRX #420 `fab3cbbd63a951a4e081f9e7f08c1391ca308581`, #422 `c14857620973531013799e44625d43080904fd5f`, #423 `0e38004363cac9fc4475556b3a1c445de9af407f`.
- PR #414 gate document directly read at the above PR HEAD: `docs/INDEXALERT_PROFITABILITY_INTEGRATION_GATE_2026-10-13.md`. Existing gate says source integrity is not historical market admission or alpha validation.
- Workflow runs (GitHub REST completed/conclusion): 38381997417 success (HEAD 55e7fe2b3fe322e39f817914ff1ed5b589bbe0da), 38382214223 success (05d73661bcc879fe0dd66ffcea5fe1f5ee6fbd56), 38419111311 success (b22e4f39517c2bc38e173e63e8fd52f29a535dad), 38419439742 success (39af5b0043e122bc0e42935d8813759ff6c1a6e7), 38419649711 success (8f363b8683d34a48754916b34810a5a8bb958896), 38486028854 **failure** (8f9a473d7751afd85e39f24bfa956d3283f77347). The last known manifest blob mismatch was expected `108f66714602a1bd3ae42c34dcca7c16e38f460b` versus observed `e428789e2e97ca7be3a4482e0df23b483a1ad69d`; **not rederived from current job logs**. Do not silently replace expected SHA. Fixed 34-case SHA-256 `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34` is prior CI evidence, not independently recomputed this run.

## Railway production evidence (read-only, 2026-11-14 11:15–12:25 UTC)
- Project `d1c1a050-b7d6-41ce-b300-13c20f82a20a`, production `83d5840b-270e-4d3f-a941-a37fd4a55ff7`.
- PIT rebuild `8b354fc1-cfb2-4ef0-863e-67f7f5dda2b5` SUCCESS, running 1/1; runtime `eaaa9f67-b9f2-41d2-832c-7d6fad9b9b00` SUCCESS, running 1/1; KRX worker `16c93d7c-7cd0-4d84-a327-298d2805376c` SUCCESS but running 0/1; Kiwoom real-readonly-run `6d3d5812-eb91-41b6-acba-9c62a68b3271` SUCCESS but running 0/1. Backend/push/db-query-readonly offline. Deployment SUCCESS is not live data admission.
- Pending staged patch `e113dacb-6705-4416-9997-dc694539d382` since 2026-10-29T06:20:53Z, changes array empty in status; do not apply.
- PIT service returned **5 prospective FAIL_CLOSED records** at 11:15:48, 11:30:46, 11:45:53, 12:00:50, 12:15:57 UTC. Direct parsed latest record: `COMMON_OHLC_NONPOSITIVE`, common_stock_rows=803, nonpositive_ohlc_rows=27, zero_volume_value_rows=27, session_manifest_sha256=null; source/model/chronology admission flags false, live order and funds authorisation false. This is **PASS for observed fail-closed guard**, **FAIL for prospective source admission**, not proof of a valid market sample. KRX worker returned zero log records in window (not proof of no activity). Runtime returned capped 251 records including 12:20:42 UTC Investing USD/KRW HTTP error and Yahoo fallback; no official KRX admission inferred.

## Independent gate verdict
| Gate | Verdict |
| --- | --- |
| Prior KRX 2017–2022 weekday raw pair storage 1565/1565 | Historical storage integrity PASS (prior evidence only); official session/market state NOT VERIFIED |
| OpenDART original/correction SGML candidate signatures | Historical candidate matching PASS (prior Action evidence only); 2021/2022 first three-month consolidated operating profit, original-filing meaning, complete correction lineage, exact public available-at/PIT NOT VERIFIED |
| Historical issuer/security mapping, official KRX calendar, halts, delistings, corporate actions, fills, cost/tax | NOT VERIFIED; source admission blocked |
| PR #413 offline CI and PR #418 earlier synthetic parity | CI conclusion PASS; 34-case digest independent recomputation NOT VERIFIED; PR #418 integration 38486028854 FAIL |
| Single runner 2.9656s versus concurrent 2.6209s (1.1315x regression phase) | Prior phase observation only; full CI and official backtest acceleration NOT VERIFIED |
| After-cost/tax annual risk-adjusted NetEV, PF, CAGR, MDD, ES95/99, return concentration, temporal robustness | NOT VERIFIED; M20 economics run NOT AUTHORIZED |
| Prospective runtime source/guard | FAIL_CLOSED observed, no source/PIT/alpha admission |

## Frozen constraints and next independent steps
Maintain H5 Frozen/consumed Holdout, M20 horizon20/purge20, WF504/126/126, Purged/CPCV, independent Holdout, Champion/Top3/NO_TRADE, cost/tax/fill/risk criteria, ORDERING=false. Cache only with approved source/data/code/Frozen/runtime/evidence SHA-256 equality and fail-closed; parallelise only read-only independent post-processing, never retraining or capital transitions. No M20 economic test, official market return experiment, model search, workflow bypass, deployment, automatic merge, account changes, real orders, funds transfer, or Champion promotion.

Next: (1) owner of PR #418 independently trace manifest file bytes and approved Git blob before any repair; (2) DART/KRX owners provide official first-publication timestamps, CFS 3-month period/correction lineage and exchange session/corporate-action/fill provenance; (3) read-only investigate Railway pending patch and recurring OHLC source rejection without relaxing gate; (4) run only synthetic offline safety tests in isolated authorised code. Do not touch other Work-owned files. No approvals newly inferred.
