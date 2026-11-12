# IndexAlert independent source / offline optimization audit — 2026-11-13 02:19 KST

Read-only inspection; no official-market economics test, model search, workflow modification, deployment, merge, trading or permission action. Source PIT remains unapproved.

## GitHub refs and CI (fresh connector reads)
- Research `index-alert-research-v1`: `df474df348f22aa38b1dedaa59fcff66e548b406`, comparison identical 0 ahead/behind.
- Development `index-alert-position-regen-fix-v1`: `1e6367d2863a86c3470da13d81a955d277eba485`, comparison identical 0 ahead/behind.
- Independent audit parent HEAD: `8df8f4bbe6d9ce3490db0a1297929ce6af7ee0c6`, identical to isolated branch before this write.
- All open, draft, unmerged: #412 `bf3d9514a87c53b1775e22ec9ba7711f6cecc49f`; #413 `f003ef6247e16fcc71bd3b1b20cd4904c4d984c0`; #414 `18c5418d9684d1717df58261ea27f28e514385b2`; #418 `2f98401cc50a6c6a25808a98516efd5bf0c944ee`; #420 `fab3cbbd63a951a4e081f9e7f08c1391ca308581`; #422 `c14857620973531013799e44625d43080904fd5f`; #423 `0e38004363cac9fc4475556b3a1c445de9af407f`.
- PR #414 gate document blob `984c933651f39f1ee9e26a1d7ac3893aaa5335be` independently fetched. Gate is policy, not source approval.
- GitHub Actions direct jobs: 38381997417 6/6 success; 38382214223 6/6; 38419111311 6/6; 38419649711 1/1; 38498552499 6/6; OpenDART 38419439742 2/2. Job-level CI PASS only. Original 34-case SHA-256 `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34` independent reproduction NOT VERIFIED. #413/#418 code parity and full official backtest speedup NOT VERIFIED; historical 2.9656s serial versus 2.6209s concurrent only regression-phase.

## Railway production direct status
Project `d1c1a050-b7d6-41ce-b300-13c20f82a20a`; production `83d5840b-270e-4d3f-a941-a37fd4a55ff7`.
- PIT rebuild 1/1 running, runtime 1/1 running. Kiwoom real-readonly 0/1 running, 1/1 crashed: operational FAIL despite deployment SUCCESS label. KRX historical worker 0/1 running, 0 crashed: runtime activity NOT VERIFIED. Backend, push, db-query-readonly offline; latter criticalCount=1.
- PIT deployment `8b354fc1-cfb2-4ef0-863e-67f7f5dda2b5`; query 2026-11-12 16:15–17:25 UTC returned zero deploy log entries. This is absence of observed logs, not evidence of source repair, healthy ingestion, or ORDERING setting.
- Inventory staged=null, status pendingWork has empty-change staged patch `e113dacb-6705-4416-9997-dc694539d382`; discrepancy not resolved, no accept/deploy.
- Last previously observed source failure `COMMON_OHLC_NONPOSITIVE` (2026-09-28 common-stock 803 rows, 27 anomalous OHLC): previous evidence only; latest-window independent remediation NOT VERIFIED. Previously observed FAIL_CLOSED and ordering DISABLED only in those records; live global config NOT VERIFIED.

## Independent gate
- Historical KRX private 1565/1565 weekday raw-pair storage integrity: historical limited PASS only. Official calendar, trading status, corporate actions, mapping, execution feasibility, taxes and transaction costs: NOT VERIFIED.
- OpenDART candidate 15 original/amended SGML rows with adjacent numeric signatures: historical CI-limited PASS for extraction only. Original-filing meaning, precise public available-at/PIT, 2021/2022 first consolidated 3-month operating-profit period and correction lineage: NOT VERIFIED.
- NetEV/PF/CAGR/MDD/ES95/99, concentration, temporal robustness, annual after-tax risk-adjusted net return: NOT VERIFIED. M20 economic run NO-GO; no H5 consumed holdout reuse.
- Frozen H5; M20 horizon20/purge20; WF504/126/126; PIT/label/Purged/CPCV/independent Holdout/Champion/Top3/NO_TRADE, cost/tax/risk/upgrade gates unchanged. Cache fail-closed without independent approved source/data/code/Frozen/runtime/approval SHA-256 parity; only independent read-only postprocessing may parallelize; dependent retraining/capital transition serial. ORDERING=false required; no live orders, transfers, credential/account authority changes, Champion promotion, deployment or PR merges.

## Next safe verification
KRX owner: independently hash 27 private source rows and classify against official calendar/status and execution; DART owner: original filing public timestamps, consolidated period/correction lineage; isolated optimization owners: offline implementation and fixture SHA parity for #413/#418. No market returns or performance exploration until PIT approval.
