# IndexAlert independent gate audit — 2026-11-09 12:18 KST

Scope: read-only source/CI/Railway verification, separate from PR #413/#418 engineering and other Work rooms. No strategy, economics, orders, deployment or workflow modifications.

## Verified HEAD and immutable references
- research index-alert-research-v1: df474df348f22aa38b1dedaa59fcff66e548b406
- development index-alert-position-regen-fix-v1: 1e6367d2863a86c3470da13d81a955d277eba485
- PR #412 OPEN Draft bf3d9514a87c53b1775e22ec9ba7711f6cecc49f
- PR #413 OPEN Draft f003ef6247e16fcc71bd3b1b20cd4904c4d984c0
- PR #414 OPEN Draft 18c5418d9684d1717df58261ea27f28e514385b2; docs/INDEXALERT_PROFITABILITY_INTEGRATION_GATE_2026-10-13.md blob 984c933651f39f1ee9e26a1d7ac3893aaa5335be
- PR #418 OPEN Draft 2f98401cc50a6c6a25808a98516efd5bf0c944ee
- KRX PR #420 OPEN Draft fab3cbbd63a951a4e081f9e7f08c1391ca308581; #422 OPEN Draft c14857620973531013799e44625d43080904fd5f; #423 OPEN Draft 0e38004363cac9fc4475556b3a1c445de9af407f.

## Actions evidence (read-only, current query)
- 38381997417, 38382214223, 38419111311: each 6/6 success.
- 38419649711: 1/1 success; 38419439742: 2/2 success.
- Chronology anchor 41515392296: auto-anchor failure, validation skipped. FAIL.
- Prior evidence, not independently recomputed in this run: 34-case SHA 5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34, synthetic 28, adversarial 13, serial 2.9656s / parallel 2.6209s = 1.1315x regression phase. End-to-end CI and official backtest speedup NOT VERIFIED.

## Railway production evidence
Project d1c1a050-b7d6-41ce-b300-13c20f82a20a, environment 83d5840b-270e-4d3f-a941-a37fd4a55ff7.
- PIT rebuild 1 running / 0 crashed, runtime 1 running / 0 crashed.
- indexalert-kiwoom-real-readonly: UI online and deployment SUCCESS, but replica running 0 / crashed 1. Runtime health FAIL.
- db-query-readonly offline, critical 1; backend and push offline.
- Existing staged patch e113dacb-6705-4416-9997-dc694539d382 with empty changes, not applied.
- Deploy logs query 2026-11-09 02:25–03:20 UTC: PIT 0, KRX 0, real-readonly 0; runtime 31 entries, sample quotes only. Zero logs does not establish no processing or data completeness.

## Gate verdict
- KRX 2017–2022 1565/1565 weekday source-pair storage SHA integrity PASS per earlier independent evidence; official trading calendar/status/corporate actions/exec feasibility NOT VERIFIED. Historical zero-activity 12003 excluded.
- OpenDART SGML candidate-row adjacency 15 PASS for candidate extraction only per prior Action evidence; original-filing meaning, public available-at, 2021/2022 first-quarter consolidated operating income period and correction lineage NOT VERIFIED.
- Historical issuer/security mappings, source PIT, costs/taxes, NetEV/PF/CAGR/MDD/ES95/99, concentration, time robustness NOT VERIFIED.
- Chronology anchor FAIL. M20 PIT/economic RUN NO-GO; H5 spent holdout and Dynamic cannot be reused or retuned.
- Frozen H5; M20 horizon20/purge20, WF504/126/126; PIT/labels/Purged/CPCV/independent holdout/Champion/Top3/NO_TRADE, costs/risk/promotion thresholds unchanged. ORDERING=false policy retained; live environment value not independently inspected.
- Optimization: only synthetic/offline software CI PASS at job level; cache fail-closed on independent approved data/code/Frozen/runtime/evidence SHA256; only independent read-only post-processing parallelizable; dependent training and capital transition not parallelizable.

Next: independent original-filing chronology/available-at anchor, exact correction lineage, official KRX trading calendar/status/issuer actions and executable cost evidence, then separate approval gate. No deployment, PR merge, market experiment, order, credential change or Champion promotion authorized.
