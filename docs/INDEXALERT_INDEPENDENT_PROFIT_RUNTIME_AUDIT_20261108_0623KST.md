# IndexAlert independent profitability/runtime audit — 2026-11-08 06:23 KST

Scope: read-only GitHub PR/Actions and Railway production inspection. This document is isolated from specialist code and is not an admission, merge, deployment, performance experiment, or trading authorization.

## Fresh GitHub evidence
PR #412, #413, #414, #418, #420, #422, #423: all OPEN, Draft, unmerged at inspection. Verified head SHA from PR metadata:
- #414 18c5418d9684d1717df58261ea27f28e514385b2
- #418 2f98401cc50a6c6a25808a98516efd5bf0c944ee
- #422 c14857620973531013799e44625d43080904fd5f
- #423 0e38004363cac9fc4475556b3a1c445de9af407f
The exact head SHA of #412/#413/#420 and current research/development branch HEAD were not independently extracted in this run; do not substitute historical SHAs. Research and development branch names were confirmed by GitHub branch search.

Actual workflow job inspection: 38381997417 6/6 success; 38382214223 6/6; 38419111311 6/6; 38498552499 6/6; 38419649711 1/1; 38419439742 2/2. Chronology Anchor 41515392296: auto-anchor failure, validation skipped. Job conclusions are verified; the historical immutable 34-case SHA 5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34 and 28 synthetic cases were NOT independently recomputed from downloaded artifacts this run. Prior one-runner 2.9656s/2.6209s=1.1315x regression-phase timing is historical, not full CI or admitted-market speedup.

## Fresh Railway evidence
Project IndexAlert d1c1a050-b7d6-41ce-b300-13c20f82a20a, production 83d5840b-270e-4d3f-a941-a37fd4a55ff7. Environment inventory staged=null, but health pendingWork includes EMPTY staged patch e113dacb-6705-4416-9997-dc694539d382: inconsistent views, do not commit it. PIT rebuild and Runtime each 1 running replica; real readonly service reports 0 running, 1 crashed despite deployment SUCCESS. db-query-readonly has 1 critical notification. KRX historical worker is reported online but replica status 0 running/0 crashed/1 total; actual worker execution not proven. Logs queried since 2026-11-07T20:00Z: PIT, KRX and real readonly yielded no entries; Runtime had recent USDKRW Investing.com HTTP error and Yahoo fallback. Empty logs are not recovery proof. No production change made.

## Gate verdict
- OpenDART official original-file byte/SGML candidate integrity: historical limited PASS; actual 2021/2022 first-three-month consolidated operating-profit semantics, complete correction lineage and intraday public available-at/PIT: NOT VERIFIED.
- KRX 2017–2022 1565/1565 weekday private original pairs: historical storage-integrity PASS; 90 date exceptions, 2026-09-28 27 nonpositive OHLC cases, official calendar/security status, corporate actions, fills and costs/taxes: NOT VERIFIED.
- Historical issuer/security mapping, point-in-time tradability: NOT VERIFIED.
- Annual post-cost/post-tax risk-adjusted NetEV, PF, CAGR, MDD, ES95/99, concentration and walk-forward robustness: NOT VERIFIED; M20 profitability execution NOT AUTHORIZED.
- Offline synthetic parity CI job execution: PASS within stated synthetic scope; actual full backtest acceleration NOT VERIFIED.
- Chronology Anchor workflow: FAIL (validation SKIPPED).
- Live readonly service health: FAIL/CRASHED replica; operational remediation needs separate authorization and should not be conflated with trading authority.

## Safety and next evidence
Keep Frozen H5; M20 horizon20/purge20; WF504/126/126; PIT/Purged/CPCV/sealed Holdout/Champion/Top3/NO_TRADE; costs/tax/fills/risk/promotion policy unchanged. H5 consumed holdout and Dynamic results cannot be retrospectively tuned or reused independently. ORDERING=false, M20 NO-GO. Do not run official-market profitability experiments, alter workflow security, merge PRs, deploy, trade, move funds, or modify account permissions. Cache only when independently approved source/data/code/Frozen policy/runtime/approval SHA-256 all match; fail closed. Parallelize only independent read-only postprocessing, never dependent refits or capital transitions. Next: source owners provide immutable official first-filing timestamp/semantic/correction evidence and independently authenticated KRX date/security tradability receipts; separately diagnose readonly replica and empty staged patch read-only; independently verify CI artifact hashes and exact branch HEAD before any new authority claim.
