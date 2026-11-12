# IndexAlert independent audit — 2026-11-12 13:22 KST

Read-only evidence verification. No new financial backtest, market return calculation, workflow change, deployment, merge, order or Champion promotion. This isolated document is the only write.

## GitHub (fresh connector queries)
- PR #412 OPEN Draft head bf3d9514a87c53b1775e22ec9ba7711f6cecc49f; #413 OPEN Draft head f003ef6247e16fcc71bd3b1b20cd4904c4d984c0; #414 OPEN Draft head 18c5418d9684d1717df58261ea27f28e514385b2; #418 OPEN Draft head 2f98401cc50a6c6a25808a98516efd5bf0c944ee.
- KRX #420 OPEN Draft head fab3cbbd63a951a4e081f9e7f08c1391ca308581; #422 OPEN Draft head c14857620973531013799e44625d43080904fd5f; #423 OPEN Draft head 0e38004363cac9fc4475556b3a1c445de9af407f.
- PR #414 gate blob SHA 984c933651f39f1ee9e26a1d7ac3893aaa5335be (fetched from PR head). Research branch index-alert-research-v1 and development index-alert-position-regen-fix-v1 previously pinned df474df348f22aa38b1dedaa59fcff66e548b406 and 1e6367d2863a86c3470da13d81a955d277eba485: **current tip SHA NOT VERIFIED**; branch name search does not provide tip hashes.
- GitHub Actions freshly fetched jobs: 38381997417 6/6 SUCCESS, 38382214223 6/6 SUCCESS, 38419111311 6/6 SUCCESS, 38419649711 1/1 SUCCESS; OpenDART 38419439742 2/2 SUCCESS. 34-case SHA-256 5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34, 13 adversarial and 28 synthetic cases: **historical report only; independent artifact recomputation NOT VERIFIED**. Serial 2.9656s vs parallel 2.6209s = 1.1315x only for regression phase; full CI and official backtest speed NOT VERIFIED.

## Railway production (fresh environment status)
Project d1c1a050-b7d6-41ce-b300-13c20f82a20a; environment 83d5840b-270e-4d3f-a941-a37fd4a55ff7.
- PIT rebuild SUCCESS deployment 8b354fc1-cfb2-4ef0-863e-67f7f5dda2b5: 1/1 running; runtime SUCCESS eaaa9f67-b9f2-41d2-832c-7d6fad9b9b00: 1/1 running.
- KRX worker SUCCESS deployment 16c93d7c-7cd0-4d84-a327-298d2805376c: 0/1 running, 0 crashed; service label online does not prove continuous operational readiness.
- Kiwoom real readonly SUCCESS deployment a77fb922-b679-4d88-92c4-03054ec579cd: 0/1 running, 1 crashed **FAIL**; do not confuse deployment SUCCESS with live replica health.
- Backend and Push offline; db-query-readonly offline with one critical notification. Empty staged patch e113dacb-6705-4416-9997-dc694539d382 untouched.
- Deployment logs requested 2026-11-12 03:25–04:25 UTC: PIT 0, KRX 0, Kiwoom 0. Runtime returned 121 entries despite limit 120; at 04:13:45 UTC Investing USD/KRW HTTPError and Yahoo fallback. No claim of exhaustive log coverage.

## Independent gate decisions
- Historical KRX private weekday raw pairs 1565/1565: **PASS for storage integrity only** (historical 2026-10-14 evidence, no fresh SHA recomputation). Official trading calendar, 90 uncertain sessions, 12003 zero-activity samples, OHLC, halts/delistings, corporate actions, historical mappings, executable fills, fees and taxes: **NOT VERIFIED / fail closed**.
- OpenDART first/late SGML 15 candidate operating-profit rows with adjacent numeric signatures: **historical extraction PASS only**. 2021/2022 exact original consolidated three-month operating income, correction lineage, original filing and public available-at/PIT: **NOT VERIFIED / fail closed**; amended data cannot fill historical original.
- H5 failed/consumed Holdout and Dynamic post-hoc results: **NO-GO for reuse**. Frozen H5 and M20 horizon20/purge20, WF504/126/126, PIT, labels, Purged/CPCV, independent Holdout, Champion, Top3, NO_TRADE, cost/risk/upgrade gates unchanged.
- Post-fee/post-tax annual risk-adjusted net profitability, NetEV/PF/CAGR/MDD/ES95/99, concentration and temporal robustness: **NOT VERIFIED**. M20 performance run **NOT AUTHORIZED**. ORDERING=false required; deployed effective value **NOT VERIFIED**.
- Optimization: offline CI job success **PASS**; complete speed improvement **NOT VERIFIED**. Cache fail-closed only on independently approved source/data/code/Frozen/runtime/approval evidence SHA-256 equality. Parallelize independent read-only postprocessing only; no dependent retraining/capital transition.

## Next safe work
Independent raw artifact SHA recomputation and original-filing period/available-at verification by source owner; official KRX trading-status/corporate-action/fill evidence by owner; read-only diagnosis of Kiwoom crashed replica and KRX non-running worker. Keep all PIT/market/economic gates closed pending actual independent proof. Do not touch other teams' code, workflows, deployment, merges or trading.
