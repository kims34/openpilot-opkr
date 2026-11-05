# IndexAlert independent profitability and isolated runtime audit — 2026-11-06 03:25 KST

Scope: read-only GitHub/Railway inspection; isolated documentation-only record. No PIT admission, M20 run, economic backtest, strategy modification, deployment, merge, broker action or workflow modification.

## Exact source refs
Research baseline SHA `3b8b7830612a6284d7c7a60628cb527cb741627a` (PR #414/#413 base; live branch HEAD not independently resolved). Development SHA `1e6367d2863a86c3470da13d81a955d277eba485` (KRX #420 base and deployed KRX worker commit; live branch HEAD not independently resolved).
All OPEN Draft, unmerged at inspection: #412 `bf3d9514a87c53b1775e22ec9ba7711f6cecc49f`; #413 `f003ef6247e16fcc71bd3b1b20cd4904c4d984c0`; #414 `18c5418d9684d1717df58261ea27f28e514385b2`; #418 `2f98401cc50a6c6a25808a98516efd5bf0c944ee`; KRX #420 `fab3cbbd63a951a4e081f9e7f08c1391ca308581`, #422 `c14857620973531013799e44625d43080904fd5f`, #423 `0e38004363cac9fc4475556b3a1c445de9af407f`. PR #414 integration gate remains Draft; direct file read on research base failed (file is on PR branch), so latest document blob is NOT VERIFIED this run.

## CI evidence
GitHub Actions jobs independently read: #38381997417 6/6 SUCCESS; #38382214223 6/6 SUCCESS; #38419111311 6/6 SUCCESS; #38419649711 1/1 SUCCESS; #38419439742 2/2 SUCCESS. Chronology #41515392296 auto-anchor FAILURE, validation SKIPPED. Historical 34-case SHA-256 `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34`, 13 adversarial mocks, 28 synthetic and 2.9656/2.6209=1.1315x regression phase remain previously supplied evidence, not freshly rehashed or timed. Full CI and official economic backtest acceleration NOT VERIFIED.

## Railway read-only evidence
IndexAlert production project `d1c1a050-b7d6-41ce-b300-13c20f82a20a`. PIT rebuild latest deployment `8b354fc1-cfb2-4ef0-863e-67f7f5dda2b5` SUCCESS (2026-10-10); KRX historical worker `16c93d7c-7cd0-4d84-a327-298d2805376c` SUCCESS (2026-10-12; commit `1e6367d2863a86c3470da13d81a955d277eba485`); runtime `eaaa9f67-b9f2-41d2-832c-7d6fad9b9b00` SUCCESS (2026-10-05). PIT rebuild and KRX worker returned no new deploy log entries for 2026-11-05 16:00Z onward, so present OHLC error persistence cannot be freshly determined. Runtime 2026-11-05 18:24Z records Investing.com FX failure and Yahoo fallback, unrelated to official PIT admission. Deployment SUCCESS does not prove healthy instances or source approval. Earlier 2026-09-28 session 27/803 nonpositive OHLC and zero-volume rows remain unresolved historical blocker, not a fresh observation.

## Admission matrix
- KRX 2017–2022 private 1565/1565 weekday raw-pair hash storage: historical PASS for bytes only; official calendar, trading state, corporate actions, fillability, execution costs/tax: NOT VERIFIED.
- OpenDART original/correction SGML 15 candidate rows and adjacent number signature: historical candidate matching PASS, first-original CFS 2021/2022 Q3 3-month semantic/period/correction lineage and exact public available-at: NOT VERIFIED.
- Historical entity/ticker mapping, PIT, labels, purging, CPCV, untouched Holdout, NetEV/PF/CAGR/MDD/ES95/99, concentration and time robustness: NOT VERIFIED.
- Chronology anchor CI: FAIL, downstream validation SKIPPED.
- Isolated offline CI jobs: PASS at job conclusion scope; immutable test evidence / complete performance acceleration NOT VERIFIED.
- M20: NO-GO / NOT EVALUABLE. No official return or profitability calculation authorised.

## Next safe work
Independently resolve live research/development HEAD and compare with recorded bases; retrieve PR #414 gate directly on its head; inspect Chronology Anchor failing job logs without workflow modification; obtain official KRX session/status/corporate-action evidence for 27 zero-price rows and OpenDART first-publication timestamps with source hashes. Only synthetic offline safety regression is allowed until all PIT source gates pass. Preserve Frozen H5, M20 horizon20/purge20, WF504/126/126, independent Holdout, Champion/Top3/NO_TRADE, all cost/risk gates, fail-closed cache identity and ORDERING=false. No merge/deploy/ordering/capital/credential change.
