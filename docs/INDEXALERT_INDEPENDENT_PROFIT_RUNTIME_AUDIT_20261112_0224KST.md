# IndexAlert independent profitability and offline runtime audit — 2026-11-12 02:24 KST

Read-only GitHub/Railway snapshot; this isolated document is the only intended write. No production, strategy, model, workflow, backtest, PR merge, trade, capital, or permissions changes.

## Verified immutable references
- Research branch index-alert-research-v1 HEAD df474df348f22aa38b1dedaa59fcff66e548b406 (compare identical, ahead/behind 0/0).
- Development branch index-alert-position-regen-fix-v1 HEAD 1e6367d2863a86c3470da13d81a955d277eba485 (identical 0/0).
- All OPEN Draft/unmerged: PR #412 bf3d9514a87c53b1775e22ec9ba7711f6cecc49f; #413 f003ef6247e16fcc71bd3b1b20cd4904c4d984c0; #414 18c5418d9684d1717df58261ea27f28e514385b2; #418 2f98401cc50a6c6a25808a98516efd5bf0c944ee; KRX #420 fab3cbbd63a951a4e081f9e7f08c1391ca308581; #422 c14857620973531013799e44625d43080904fd5f; #423 0e38004363cac9fc4475556b3a1c445de9af407f.
- Integration gate document docs/INDEXALERT_PROFITABILITY_INTEGRATION_GATE_2026-10-13.md fetched on PR #414 branch: Git blob 984c933651f39f1ee9e26a1d7ac3893aaa5335be. PR #414 base SHA 3b8b7830612a6284d7c7a60628cb527cb741627a is not the current research HEAD: do not treat its base as latest research.
- GitHub Actions run IDs 38381997417 (6/6), 38382214223 (6/6), 38419111311 (6/6), 38419649711 (1/1), 38419439742 (2/2): all listed jobs conclusion SUCCESS. Original fixed 34-case SHA-256 5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34 was not independently recomputed in this run. Historical synthetic 13 adversarial mocks, extra 28 tests, and serial 2.9656 s vs concurrent 2.6209 s (regression phase 1.1315x) remain prior CI claims, not official full-backtest speedup.

## Railway production live read-only snapshot
Project d1c1a050-b7d6-41ce-b300-13c20f82a20a, environment 83d5840b-270e-4d3f-a941-a37fd4a55ff7. PIT rebuild deployment 8b354fc1-cfb2-4ef0-863e-67f7f5dda2b5 SUCCESS, replicas 1/1; Runtime eaaa9f67-b9f2-41d2-832c-7d6fad9b9b00 SUCCESS, 1/1; KRX worker 16c93d7c-7cd0-4d84-a327-298d2805376c SUCCESS, 0/1 running (runtime NOT VERIFIED); Kiwoom real-readonly a77fb922-b679-4d88-92c4-03054ec579cd SUCCESS but running 0/crashed 1 (replica FAIL). Backend, Push, db-query-readonly offline; db-query-readonly one critical. Pending staged patch e113dacb-6705-4416-9997-dc694539d382 has empty changes; NOT applied.

2026-11-11 16:20–17:25 UTC deploy logs: PIT 0, KRX 0, Kiwoom 0; Runtime logs present (returned 101 entries despite requested limit 100). At 17:24:41 UTC Investing USD/KRW HTTPError triggered Yahoo fallback. This is operational evidence, NOT source PIT approval. No new KRX failure was established in this specific window; historical COMMON_OHLC_NONPOSITIVE remains a blocker.

## Independent gate decisions
- KRX 2017–2022 1565/1565 weekday original-pair SHA storage integrity: PASS only for previously recorded storage scope; current independent original SHA recheck NOT VERIFIED. Official calendar, trading status, halts, corporate actions, fillability, slippage, fees and taxes: NOT VERIFIED / FAIL-CLOSED. 90 ambiguous sessions, 12003 zero-activity rows remain excluded.
- OpenDART original/rectified SGML 15 candidate rows and adjacent numeric signatures (Action 38419439742): historical syntactic evidence only. Original-filing semantics, exact 2021/2022 first three-month consolidated operating profit, amendment/period lineage, public available-at and corp/security PIT mapping: NOT VERIFIED / FAIL-CLOSED.
- Frozen H5 failed/consumed Holdout and Dynamic results: NO-GO, no retuning or independent Holdout reuse.
- M20 horizon20/purge20, WF504/126/126 and frozen PIT/label/Purged/CPCV/Holdout/Champion/Top3/NO_TRADE, cost/tax/risk rules: unchanged. M20 official profitability run NOT AUTHORIZED; after-tax NetEV/PF/CAGR/MDD/ES95/ES99, concentration and time-slice robustness NOT VERIFIED.
- Offline PR #413/#418 CI job success PASS; independent 34-case digest, whole-CI and official-backtest acceleration NOT VERIFIED. Cache only when independently approved source/data/code/frozen policy/runtime/approval SHA-256 all match, fail-closed; parallel read-only postprocessing only; no dependent retraining or capital transition concurrency.
- ORDERING=false; no live orders, funds movement, credentials/permissions, Champion promotion, deploy or merges.

## Next independent work
Read-only original filing public timestamp/lineage proof, KRX official trading status and corporate action source SHA, independently recompute 34-case test digest from immutable artifacts if available, and obtain meaningful replica/worker diagnostics without touching production. Do not run M20 or official economic performance tests before PIT gates independently pass. Preserve ownership boundaries of other Work rooms.
