# IndexAlert independent profitability / isolated optimisation audit — 2026-11-11 00:17 KST

Scope: read-only GitHub/Railway evidence inspection. No strategy tuning, PIT admission, production deployment, live order, merge, or workflow changes.

## GitHub exact observed PR HEADs
- #412 OPEN DRAFT bf3d9514a87c53b1775e22ec9ba7711f6cecc49f
- #413 OPEN DRAFT f003ef6247e16fcc71bd3b1b20cd4904c4d984c0
- #414 OPEN DRAFT 18c5418d9684d1717df58261ea27f28e514385b2; gate file blob 984c933651f39f1ee9e26a1d7ac3893aaa5335be
- #418 OPEN DRAFT 2f98401cc50a6c6a25808a98516efd5bf0c944ee
- KRX #420 OPEN DRAFT fab3cbbd63a951a4e081f9e7f08c1391ca308581
- KRX #422 OPEN DRAFT c14857620973531013799e44625d43080904fd5f
- KRX #423 OPEN DRAFT 0e38004363cac9fc4475556b3a1c445de9af407f
- Research and development branch HEAD not independently re-resolved in this execution; do not treat earlier observed SHAs as current.

## Actions independently inspected (job conclusions)
- 38381997417: 6/6 SUCCESS
- 38382214223: 6/6 SUCCESS
- 38419111311: 6/6 SUCCESS
- 38419649711: 1/1 SUCCESS
- 38419439742: 2/2 SUCCESS
- Fixed 34-case SHA 5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34 and 13 adversarial / 28 synthetic case assertions are historical supplied evidence, **not independently recomputed this run**.
- 2.9656s serial / 2.6209s concurrent = 1.1315x regression-phase only; end-to-end CI and official backtest speed NOT VERIFIED.

## Railway production read-only
Project d1c1a050-b7d6-41ce-b300-13c20f82a20a.
- PIT rebuild latest deployment 8b354fc1-cfb2-4ef0-863e-67f7f5dda2b5 SUCCESS (deployment status only). Actual deploy logs at 2026-11-10 14:01:30, 14:16:27, 14:31:35, 14:46:33 UTC repeatedly show COMMON_OHLC_NONPOSITIVE; common_stock_rows=803, nonpositive_ohlc_rows=27, zero_volume_value_rows=27; ordering=DISABLED, independent source/model/chronology admission=false, live_order_authorized=false. Operational source acceptance FAIL-CLOSED; exact environment configuration NOT VERIFIED.
- KRX historical worker deployment 16c93d7c-7cd0-4d84-a327-298d2805376c SUCCESS; selected window logs zero, worker runtime readiness NOT VERIFIED.
- Kiwoom real read-only deployment a77fb922-b679-4d88-92c4-03054ec579cd SUCCESS; selected window logs zero, current replica health NOT VERIFIED.
- Runtime deployment eaaa9f67-b9f2-41d2-832c-7d6fad9b9b00 SUCCESS; backend cce12a43-592a-4910-9b75-89c6b7cdd159 FAILED; push 3ad3102d-ced6-416b-a6da-85c390c9a606 FAILED. Deployment statuses are not runtime health.

## Independent gate decisions
- PASS (limited scope): specified offline Actions job conclusions; prior 1565/1565 weekday private KRX raw-pair storage integrity (historical evidence, not independently rehashed now).
- FAIL / FAIL-CLOSED: prospective OHLC source quality (27/803 invalid); missing independent admission; M20 economic run remains NO-GO.
- NOT VERIFIED: original-filing authoritative meaning and public available-at/PIT; 2021/2022 first three months consolidated operating profit period/correction lineage; historical issuer/security mapping; official KRX session/halts/corporate actions/fillability; brokerage costs/taxes; independent post-cost annual risk-adjusted NetEV/PF/CAGR/MDD/ES95/99, return concentration and temporal robustness; full CI / backtest acceleration; current branch HEAD and deployment replica health.
- The 15 SGML candidate-row match in OpenDART Action 38419439742 does not approve semantic interpretation or public timestamp.
- H5 consumed/failed holdout and dynamic results must not be independently reused or tuned.

## Frozen boundary and next allowed work
Keep H5, M20 horizon20/purge20, WF504/126/126, PIT, label, Purged/CPCV, independent holdout, Champion/Top3/NO_TRADE and all cost/tax/NetEV/fill/risk/promotion thresholds unchanged. ORDERING=false. Cache only with independently approved source/data/calculation/Frozen/runtime/approval evidence SHA-256 all matching fail-closed; parallelise read-only postprocessing only. No dependent retraining or capital transition parallelism.
Next: independently validate official original-filing available-at and correction lineage, historical KRX market state and execution, then authorise PIT separately before any M20 economic run. Investigate prospective 27 OHLC exceptions in source-quality-only offline scope. Check Kiwoom replica health in a later read-only pass. No workflow bypass, merges, deploys, orders, money movement or Champion promotion.
