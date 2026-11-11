# IndexAlert independent audit — 2026-11-11 13:25 KST

Read-only source checks plus isolated documentation only. No trading, workflow edit, merge, deployment, official profitability replay, or parameter change.

## GitHub source observations
- Research branch `index-alert-research-v1` and development branch `index-alert-position-regen-fix-v1` both resolved in branch search. Their exact live HEAD SHAs were **NOT VERIFIED** by this run's branch search API (branch names only); previously reported research `df474df348f22aa38b1dedaa59fcff66e548b406` and development `1e6367d2863a86c3470da13d81a955d277eba485` must not be presented as freshly revalidated.
- PRs #412, #413, #414, #418, #420, #422, #423: fetched GitHub metadata; all OPEN, Draft, unmerged. The #414 integration document fetched from its isolated branch: Git blob SHA `984c933651f39f1ee9e26a1d7ac3893aaa5335be`; document itself states M20 NO-GO.
- Actions job APIs independently returned success for 38381997417 (6/6), 38382214223 (6/6), 38419111311 (6/6), 38419649711 (1/1), 38419439742 (2/2), 38498552499 (6/6). These are CI job-status PASS only; individual 34-case parity SHA `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34`, 13 adversarial mocks, 28 synthetic cases, artifact bytes and performance timings were NOT independently recalculated in this run.
- #413 and #418 remain offline-only. Historic 2.9656s serial vs 2.6209s concurrent ratio 1.1315x is a regression-phase observation, not verified full-CI or real official backtest acceleration. Another reported follow-up 1.7114s serial vs 2.5776s parallel was slower; no speedup claim authorized.

## Railway production read-only
- Project `d1c1a050-b7d6-41ce-b300-13c20f82a20a`. Latest deployments: PIT `8b354fc1-cfb2-4ef0-863e-67f7f5dda2b5` SUCCESS; KRX `16c93d7c-7cd0-4d84-a327-298d2805376c` SUCCESS; Runtime `eaaa9f67-b9f2-41d2-832c-7d6fad9b9b00` SUCCESS; Kiwoom real read-only `a77fb922-b679-4d88-92c4-03054ec579cd` SUCCESS. Deployment success is not operational-health PASS.
- Health: PIT 1/1 running, Runtime 1/1 running; KRX 0/1 running (NOT VERIFIED operational); Kiwoom real read-only 0/1 running and 1/1 crashed (runtime FAIL). Backend and Push offline; db-query-readonly offline with one critical issue. Staged patch exists but contains zero listed changes; not applied.
- Logs since 2026-11-11 02:00 UTC: PIT 0, KRX 0, Kiwoom real 0; Runtime 81 entries, including USD/KRW Investing HTTP error and Yahoo fallback. Runtime market quote activity is not official historical PIT proof.

## Source and profitability admission
- Historical KRX 2017–2022 1,565/1,565 weekday dual-source raw storage integrity: **PASS only on previously attested scope**; exact official exchange calendar, stock/day tradability, corporate actions, execution and fees/taxes **NOT VERIFIED**. Existing 90-day unresolved classification and 12,003 zero-activity records remain blocked.
- OpenDART Action 38419439742 2/2 CI PASS; original/corrected SGML candidate row shapes and adjacent signatures do not establish original-filing meaning, 2021/2022 first 3-month consolidated operating profit, full correction lineage or exact public available-at: **NOT VERIFIED**.
- Historical corporate/security mapping, labels, PIT, Purged/CPCV, independent holdout, NetEV, PF, CAGR, MDD, ES95/99, concentration, temporal robustness and tax/cost-adjusted annual risk-adjusted net return: **NOT VERIFIED**. No M20 economic run approved; H5 failed/consumed holdout and Dynamic results must not be reused or tuned.
- Frozen H5, M20 horizon20/purge20, WF504/126/126, Champion/Top3/NO_TRADE, costs/tax, execution and promotion gates unchanged. ORDERING=false requirement maintained (actual runtime environment variable value not independently read).
- Optimization remains limited to synthetic offline checks, immutable manifest fail-closed on independently approved source/data/code/frozen-policy/runtime/evidence SHA-256, and parallel independent read-only postprocessing; dependent retraining and capital transition remain serial.

## Next permitted steps
1. Independently obtain exact current GitHub branch HEADs and per-PR head SHAs; pin evidence bytes and compare to CI/artifact hashes.
2. Source owners provide independently admissible official original-filing/public-time, historical security mapping, exchange session/status/corporate action and execution evidence. No actual M20 run until full gate PASS.
3. Railway operator reviews KRX 0/1, Kiwoom crashed 1/1 and db-query-readonly critical, without changes or secret exposure in this audit track.
4. PR #413/#418 optimization evaluation only on offline synthetic immutable fixtures; no workflow security bypass, merge, deploy or Champion promotion.
