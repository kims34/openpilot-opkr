# IndexAlert independent audit — 2026-11-14 22:24 KST

Scope: read-only GitHub/Railway source and CI audit; independent integration gate and separate offline optimization audit. No performance experiment, deployment, merge, workflow edit, order, account change or Champion promotion.

## Exact live GitHub heads (direct REST branch/PR reads)
- research `index-alert-research-v1`: `df474df348f22aa38b1dedaa59fcff66e548b406`
- development `index-alert-position-regen-fix-v1`: `1e6367d2863a86c3470da13d81a955d277eba485`
- Draft/open/unmerged PR #412 `bf3d9514a87c53b1775e22ec9ba7711f6cecc49f`; #413 `f003ef6247e16fcc71bd3b1b20cd4904c4d984c0`; #414 `18c5418d9684d1717df58261ea27f28e514385b2`; #418 `2f98401cc50a6c6a25808a98516efd5bf0c944ee`; KRX #420 `fab3cbbd63a951a4e081f9e7f08c1391ca308581`; #422 `c14857620973531013799e44625d43080904fd5f`; #423 `0e38004363cac9fc4475556b3a1c445de9af407f`.
- PR #414 gate document `docs/INDEXALERT_PROFITABILITY_INTEGRATION_GATE_2026-10-13.md` blob SHA-1 `984c933651f39f1ee9e26a1d7ac3893aaa5335be` (read-only fetched).
- GitHub run jobs direct reads: 38381997417 PASS 6/6; 38382214223 PASS 6/6; 38419111311 PASS 6/6; 38419649711 PASS 1/1; 38419439742 PASS 2/2; 38486028854 FAIL 1/1. Job success does not independently revalidate artifacts or source SHA-256. Prior reported archived 34-case SHA-256 `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34` NOT RECOMPUTED in this run. Prior failed PR #418 manifest blob expected `108f66714602a1bd3ae42c34dcca7c16e38f460b` versus observed `e428789e2e97ca7be3a4482e0df23b483a1ad69d`; root byte lineage remains NOT VERIFIED, do not rewrite expectation.

## Railway production direct evidence
Project `d1c1a050-b7d6-41ce-b300-13c20f82a20a`, environment `83d5840b-270e-4d3f-a941-a37fd4a55ff7`.
- PIT rebuild deployment `8b354fc1-cfb2-4ef0-863e-67f7f5dda2b5` SUCCESS, running 1/1. Runtime deployment `eaaa9f67-b9f2-41d2-832c-7d6fad9b9b00` SUCCESS, running 1/1.
- KRX historical worker `16c93d7c-7cd0-4d84-a327-298d2805376c` SUCCESS but running 0/1; Kiwoom real-readonly-run `6d3d5812-eb91-41b6-acba-9c62a68b3271` SUCCESS but 0/1. Backend/push/db-query-readonly offline.
- Pending environment patch `e113dacb-6705-4416-9997-dc694539d382` remains staged since 2026-10-29 06:20:53 UTC. Do not commit/apply.
- PIT deploy logs 2026-11-14 12:15–13:25 UTC: five prospective runtime fail-closed observations (12:15:57, 12:31:04, 12:46:00, 13:00:59, 13:16:06), `COMMON_OHLC_NONPOSITIVE`, 27 nonpositive/zero-volume-value rows among 803 common stock rows, independent source/model/chronology admissions false, fresh alpha false, live order false. KRX worker logs in interval: 0 entries (not evidence of zero underlying work). Runtime 13:24:40 UTC Investing USD/KRW HTTP error and Yahoo fallback.
- FAIL_CLOSED operational control PASS (observed); official data/tradability PASS not established.

## Gate status
- Archived KRX 2017–2022 1565/1565 weekday raw-pair storage integrity: historical PASS only, not rehashed this run. Official market calendar, historical trading status, actions, executable fills, costs/taxes: NOT VERIFIED.
- Original filing, exact public available-at, 2021/2022 first three months consolidated operating profit period/correction lineage, historical corp/security mapping: NOT VERIFIED. Archived SGML candidate 15-row signature does not prove semantic/PIT eligibility.
- PIT source admission and M20 economics: NO-GO / NOT VERIFIED. H5 consumed holdout and Dynamic results cannot be reused independently.
- After-fee/tax NetEV, PF, CAGR, MDD, ES95/99, concentration, regime robustness: NOT VERIFIED (no authorized new official return run).
- Optimization offline CI job status PASS except #418 integration FAIL. Archived 2.9656s serial vs 2.6209s simultaneous suites = 1.1315x regression-phase ratio, not proof of whole-CI or actual backtest speedup. Cache only with full independent source/data/code/Frozen/runtime/evidence SHA-256 parity and fail-closed; parallelize only read-only independent post-processing, never dependent retraining/capital transitions.

## Invariants and next evidence
Frozen H5, M20 horizon20/purge20, WF504/126/126, PIT/labels/Purged/CPCV/independent holdout/Champion/Top3/NO_TRADE, transaction costs, tax, risk, promotion gates unchanged. ORDERING=false. No market-performance experiments, optimization parameter searches, merges, production deployment or trading.
Next: independently establish PR #418 immutable original bytes and approved manifest lineage; request DART original-filing available-at + period/correction chain and KRX official trading state/corporate action provenance from respective owners; classify the 27 prospective OHLC veto rows without admitting them; reconcile staged patch state read-only. No user approval requested unless a prohibited action becomes necessary.
