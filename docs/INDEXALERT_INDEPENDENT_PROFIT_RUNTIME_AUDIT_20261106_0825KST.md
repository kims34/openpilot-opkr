# IndexAlert independent profitability/runtime audit — 2026-11-06 08:25 KST

Read-only independent verification; this document is NOT PIT/source approval, trading authority, or a performance result.

## Verified GitHub refs
- Research `index-alert-research-v1` HEAD `df474df348f22aa38b1dedaa59fcff66e548b406`; development `index-alert-position-regen-fix-v1` HEAD `1e6367d2863a86c3470da13d81a955d277eba485` (fetch_commit by ref).
- OPEN/Draft PR HEAD: #412 `bf3d9514a87c53b1775e22ec9ba7711f6cecc49f`; #413 `f003ef6247e16fcc71bd3b1b20cd4904c4d984c0`; #414 `18c5418d9684d1717df58261ea27f28e514385b2`; #418 `2f98401cc50a6c6a25808a98516efd5bf0c944ee`; #420 `fab3cbbd63a951a4e081f9e7f08c1391ca308581`; #422 `c14857620973531013799e44625d43080904fd5f`; #423 `0e38004363cac9fc4475556b3a1c445de9af407f`.
- PR #414 integration gate document read directly at PR HEAD; explicitly keeps M20 performance blocked, H5 holdout consumed, and no live order.
- Actions jobs checked live: #38381997417, #38382214223, #38419111311 each 6/6 success; #38419649711 1/1 success; #38419439742 2/2 success. Chronology #41515392296 auto-anchor FAILURE, validation SKIPPED.
- Historical fixture digest `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34`, 34 cases, 13 adversarial mocks, 28 synthetic tests and serial 2.9656s / parallel 2.6209s = 1.1315x are prior evidence, **not freshly independently recomputed**. End-to-end CI and approved official backtest acceleration NOT VERIFIED.

## Railway production read-only evidence
- Project `d1c1a050-b7d6-41ce-b300-13c20f82a20a`; production environment `83d5840b-270e-4d3f-a941-a37fd4a55ff7`.
- PIT rebuild deployment `8b354fc1-cfb2-4ef0-863e-67f7f5dda2b5` SUCCESS, replicas 1 running / 0 crashed. KRX historical worker `16c93d7c-7cd0-4d84-a327-298d2805376c` SUCCESS, replicas 0 running / 0 crashed. Both had **zero deploy log entries** for query from 2026-11-05 22:00Z; no fresh OHLC repair evidence.
- Runtime 1/1 running. Backend, Push, db-query-readonly offline; db-query-readonly 1 critical. Kiwoom real readonly service status displays online but replicas 0 running / 1 crashed: display label is not proof of process health.
- Existing Railway staged patch `e113dacb-6705-4416-9997-dc694539d382` untouched.
- Prior 1565/1565 weekday source pair integrity PASS is limited to storage SHA, not market calendar, tradeability or PIT. Prior 27/803 nonpositive OHLC and zero-volume observations remain unresolved; fresh occurrence NOT VERIFIED.

## Independent gates (scope-specific)
- Storage integrity: historical PASS, not newly rerun.
- OpenDART original-filing ZIP / correction SGML candidate extraction: prior narrow PASS (15 candidate rows), **exact 2021/2022 consolidated initial 3-month operating income period, semantic lineage, original public available-at and full corrections NOT VERIFIED**.
- Historical corporation/security mapping; official KRX session calendar, halts/delistings, corporate actions, fillability and costs/taxes: NOT VERIFIED.
- Chronology anchor: FAIL for observed action; downstream validation SKIPPED.
- NetEV, PF, CAGR, MDD, ES95/99, profit concentration, time-slice robustness, post-tax annual risk-adjusted return: NOT VERIFIED; **M20 NO-GO**.
- Offline optimization regression job success: PASS for CI job status only; fixed fixture SHA and speed independent rerun NOT VERIFIED this round; full official runtime gain NOT VERIFIED.

## Safe next steps
1. Independent DART/KRX owners deliver exact SHA-linked original public timestamp, period/correction lineage, official historical status/action and fillability proofs. Do not replace missing original data with later revisions or exclude suspect symbols to force PASS.
2. Resolve chronology anchor failure with authorized owner; never bypass security controls or change workflow to evade prior block.
3. Offline-only synthetic security/parity tests for #413/#418; cache requires independently approved source/data/code/Frozen/runtime/evidence SHA256 equality and fail-closed behavior. Only independent read-only postprocessing parallelized.
4. Keep Frozen H5, M20 horizon20/purge20, WF504/126/126, PIT/label/Purged/CPCV/independent holdout/Champion/Top3/NO_TRADE and cost/risk thresholds unchanged; no holdout reuse, dynamic retuning, economic experiment, deployment, merge, ordering, capital movement or champion promotion.
5. `ORDERING=false` / disabled; each live trading, account authorization and promotion action needs separate explicit approval.
