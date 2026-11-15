# IndexAlert independent audit — 2026-11-15 15:24 KST

Read-only source audit; NO economic backtest, order, deployment, merge, authorization change, or workflow modification.

## Source provenance
- GitHub prior direct HEAD evidence (14:25 KST): research `df474df348f22aa38b1dedaa59fcff66e548b406`, development `1e6367d2863a86c3470da13d81a955d277eba485`. **Current branch HEAD NOT VERIFIED** in this run (branch name enumeration is not a HEAD check).
- Prior PR HEADs: #412 `bf3d9514a87c53b1775e22ec9ba7711f6cecc49f`, #413 `f003ef6247e16fcc71bd3b1b20cd4904c4d984c0`, #414 `18c5418d9684d1717df58261ea27f28e514385b2`, #418 `2f98401cc50a6c6a25808a98516efd5bf0c944ee`, #420 `fab3cbbd63a951a4e081f9e7f08c1391ca308581`, #422 `c14857620973531013799e44625d43080904fd5f`, #423 `0e38004363cac9fc4475556b3a1c445de9af407f`. **Current PR heads/state NOT VERIFIED**: GitHub issue search unexpectedly returned zero results.
- PR #414 gate fetched directly at commit `18c5418d9684d1717df58261ea27f28e514385b2`, blob Git SHA-1 `984c933651f39f1ee9e26a1d7ac3893aaa5335be`. Explicit M20 performance authority false, original Q3 and KRX trading-state unapproved.

## CI: independently queried this run
- Actions 38381997417, 38382214223, 38419111311: **PASS 6/6 jobs each**.
- Action 38419439742: **PASS 2/2 jobs**, candidate SGML rows only; original filing semantics/period/public available-at NOT VERIFIED.
- Action 38419649711: **PASS 1/1 job** synthetic one-runner.
- Action 38486028854: **FAIL 1/1 job**; job 115599778959 log directly confirms `SourceDriftError` for `research_v1_runtime_manifest.py`: expected Git blob SHA-1 `108f66714602a1bd3ae42c34dcca7c16e38f460b`, observed `e428789e2e97ca7be3a4482e0df23b483a1ad69d`. Do not relax the manifest pin or run dependent suite until isolated source reconciliation.
- Historical fixed 34-case SHA-256 `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34`: **NOT VERIFIED** independently this run. Historical serial 2.9656s vs concurrent 2.6209s = 1.1315x regression phase only; full CI and official backtest speed **NOT VERIFIED**.

## Railway production, direct read-only checks
Project `d1c1a050-b7d6-41ce-b300-13c20f82a20a`; production `83d5840b-270e-4d3f-a941-a37fd4a55ff7`.
- Service listing confirmed PIT rebuild `225f2279-d728-4e1a-a3f3-2447ff0f9dc1`, KRX historical worker `003812ee-102b-42b6-bda4-36925885b428`, runtime `37902fde-ca05-43e0-bc76-278992bf7732`.
- Deployment list confirms PIT `8b354fc1-cfb2-4ef0-863e-67f7f5dda2b5` SUCCESS (2026-10-10), KRX `16c93d7c-7cd0-4d84-a327-298d2805376c` SUCCESS (2026-10-12), development source `1e6367d2863a86c3470da13d81a955d277eba485`. Deployment SUCCESS does not establish currently active replicas or PIT approval.
- 2026-11-15 05:15–06:25 UTC service logs: PIT **0 entries**, KRX **0 entries**; Runtime **101 returned records**. At 06:24:46 UTC Investing USD/KRW HTTP error -> Yahoo fallback, and Bank of Korea ECOS prior-close basis; no source PIT proof. Log count is limited response, not exhaustive.
- Latest environment staged changes and replica status **NOT VERIFIED** in this run.

## Gate verdict
- Historical KRX 2017–2022 1565/1565 weekday raw-pair storage: **historical PASS only**; official trading calendar/state, delistings, corporate actions, executable price, costs/tax **NOT VERIFIED**. Keep 90-day classification and 12003 zero-activity cases excluded.
- OpenDART original-filing, exact 2021/2022 first consolidated 3-month operating-profit period and corrections, publication available-at/PIT, historical entity/security map **NOT VERIFIED**.
- M20 source/PIT **NO-GO**; annual post-tax, post-cost risk-adjusted NetEV/PF/CAGR/MDD/ES95/99, concentration and temporal robustness **NOT VERIFIED**. No M20 economics executed.
- Frozen H5; M20 horizon20/purge20; WF504/126/126; PIT/labels/Purged/CPCV/independent holdout/Champion/Top3/NO_TRADE; ORDERING=false unchanged. No consumed holdout reuse. Cache only on independently approved source/data/code/Frozen policy/runtime/evidence SHA-256 match, fail closed. Parallel read-only postprocessing only; no dependent retraining or capital-transition parallelization.
- Next: source owners independently certify DART original filing, correction lineage and publication time, and KRX official trading state; PR #418 owner reconcile archived manifest source SHA without weakening pin; only offline synthetic safety tests before source approval.
