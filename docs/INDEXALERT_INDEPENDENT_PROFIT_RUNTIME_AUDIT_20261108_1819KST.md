# IndexAlert independent profitability and isolated runtime audit — 2026-11-08 18:19 KST

Read-only evidence snapshot. No PIT approval, strategy tuning, economic run, deployment, merge or trading authority is conferred.

## Exact GitHub refs (independently queried)
- research index-alert-research-v1: df474df348f22aa38b1dedaa59fcff66e548b406
- development index-alert-position-regen-fix-v1: 1e6367d2863a86c3470da13d81a955d277eba485
- PR #412: bf3d9514a87c53b1775e22ec9ba7711f6cecc49f
- PR #413: f003ef6247e16fcc71bd3b1b20cd4904c4d984c0
- PR #414: 18c5418d9684d1717df58261ea27f28e514385b2
- PR #418: 2f98401cc50a6c6a25808a98516efd5bf0c944ee
- KRX PR #420: fab3cbbd63a951a4e081f9e7f08c1391ca308581
- KRX PR #422: c14857620973531013799e44625d43080904fd5f
- KRX PR #423: 0e38004363cac9fc4475556b3a1c445de9af407f
- All seven PRs OPEN, Draft, unmerged.
- PR #414 gate blob SHA: 984c933651f39f1ee9e26a1d7ac3893aaa5335be; verified on PR #414 head, not research branch.

## GitHub Actions — independently queried jobs
- 38381997417: 6/6 SUCCESS.
- 38382214223: 6/6 SUCCESS.
- 38419111311: 6/6 SUCCESS.
- 38419649711: 1/1 SUCCESS.
- 38419439742: 2/2 SUCCESS.
- Chronology Anchor 41515392296: auto-anchor FAILURE, validation SKIPPED.
- Prior 34-case SHA 5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34, 13 adversarial mocks, 28 synthetic tests and 2.9656/2.6209s comparison are historical reported evidence, not rehashed/rebenchmarked this run. Whole-CI and official economic backtest acceleration NOT VERIFIED.

## Railway IndexAlert production (read-only environment_status and deploy logs; 2026-11-08 15:00–18:19 KST)
- indexalert-pit-rebuild: online, 1 running/1 total, latest deployment SUCCESS, 0 deploy log lines in interval.
- indexalert-krx-historical-worker: online UI, 0 running/0 crashed/1 total, latest deployment SUCCESS, 0 deploy log lines.
- indexalert-kiwoom-real-readonly: online UI but 0 running/1 crashed/1 total, latest deployment SUCCESS, 0 deploy log lines. Operational inconsistency persists.
- indexalert-runtime: online, 1 running/1 total, recent USDKRW/Yahoo quote logs; not a PIT or economic approval.
- db-query-readonly offline, 1 critical; backend offline 4 warnings; push offline 1 warning.
- Pending staged patch e113dacb-6705-4416-9997-dc694539d382, changes []; no deployment committed.

## Independent gate decisions
- KRX 2017–2022 private weekday pairs 1565/1565: historical storage integrity PASS only; official calendar, 90 ambiguous days, 27 suspect OHLC and 12003 zero-activity, corporate actions and execution NOT VERIFIED / fail closed.
- OpenDART SGML 15 candidate row adjacency: historical synthetic/row fingerprint evidence PASS only; original-filing semantic classification, public available-at and PIT NOT VERIFIED.
- 2021/2022 initial three-month consolidated operating profit, correction lineage, issuer/security historical mapping: NOT VERIFIED.
- Tradeability, commissions/taxes/slippage, NetEV/PF/CAGR/MDD/ES95/99, return concentration and walk-forward robustness: NOT VERIFIED; no economic run.
- Chronology Anchor run 41515392296: FAIL; dependent validation SKIPPED.
- M20 PIT/economics: NO-GO. H5 consumed/failed holdout and Dynamic must not be independently reused or post-hoc tuned. ORDERING=false.

## Optimization safety boundary
Only synthetic offline software/policy tests pending independent source PIT approval. Frozen H5, M20 horizon20/purge20, WF504/126/126, Purged/CPCV/Holdout/Champion/Top3/NO_TRADE and risk/cost/tax gates unchanged. Cache fail closed unless approved original/data/code/Frozen/runtime/approval evidence SHA-256 all match. Parallelize read-only postprocessing only, never dependent retraining or capital transitions.

## Next independently actionable evidence
1. Source-owned first-filed 2021/2022 3-month consolidated operating profit original/correction chain with original public available-at timestamps and immutable evidence SHA.
2. Official KRX trading calendar, historical status and corporate action provenance; resolve 90 uncertain sessions, 27 suspect OHLC and zero-activity quarantine without assuming tradeability.
3. Repair/independently validate Chronology Anchor before any PIT admission; inspect crashed read-only replica and db-query critical without changing production.
4. Recompute offline parity SHA and CI wall-time only in isolated synthetic scope; do not infer full backtest speedup.
5. Only after independent PIT approval, seek separate authorization for economic run; no Champion promotion, orders, deployment or merges.

This file is an independent audit snapshot only; no workflow, code, runtime or policy changes were made.
