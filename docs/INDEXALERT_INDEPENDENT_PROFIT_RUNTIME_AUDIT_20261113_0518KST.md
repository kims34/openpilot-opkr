# IndexAlert independent audit — 2026-11-13 05:18 KST

Scope: read-only GitHub/Railway checks; documentation-only isolated audit. No market performance execution, code/workflow edit, deployment, merge, orders, account or authority change.

## Exact source refs
- Research branch HEAD `df474df348f22aa38b1dedaa59fcff66e548b406` (self-compare identical).
- Development branch HEAD `1e6367d2863a86c3470da13d81a955d277eba485` (self-compare identical).
- Independent audit branch before this write HEAD `551d56c607c745b181b0acae3a144ac09e0d1a95`.
- PR heads (all OPEN/Draft/unmerged): #412 `bf3d9514a87c53b1775e22ec9ba7711f6cecc49f`; #413 `f003ef6247e16fcc71bd3b1b20cd4904c4d984c0`; #414 `18c5418d9684d1717df58261ea27f28e514385b2`; #418 `2f98401cc50a6c6a25808a98516efd5bf0c944ee`; #420 `fab3cbbd63a951a4e081f9e7f08c1391ca308581`; #422 `c14857620973531013799e44625d43080904fd5f`; #423 `0e38004363cac9fc4475556b3a1c445de9af407f`.
- PR #414 integration gate file blob `984c933651f39f1ee9e26a1d7ac3893aaa5335be` (fetched at PR HEAD).
- Actions directly checked: 38381997417 (6/6 success), 38382214223 (6/6), 38419111311 (6/6), 38419649711 (1/1), OpenDART 38419439742 (2/2). These are CI job outcomes, **not** original market evidence/PIT approval. Prior stated 34-case SHA `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34` independently recomputed: NOT VERIFIED. 13 adversarial mocks and 28 synthetic cases independently rerun: NOT VERIFIED.
- One-runner regression-phase reported serial 2.9656s vs concurrent 2.6209s (1.1315x): historical claim only; end-to-end CI and official-backtest acceleration NOT VERIFIED.

## Railway production evidence
Project `d1c1a050-b7d6-41ce-b300-13c20f82a20a`, environment `83d5840b-270e-4d3f-a941-a37fd4a55ff7`. Latest deployment/status metadata queried.
- PIT rebuild `8b354fc1-cfb2-4ef0-863e-67f7f5dda2b5` SUCCESS, 1/1 running; Runtime `eaaa9f67-b9f2-41d2-832c-7d6fad9b9b00` SUCCESS, 1/1 running.
- Kiwoom real readonly `a77fb922-b679-4d88-92c4-03054ec579cd` reports SUCCESS/online but **0 running, 1 crashed**: operational FAIL; service label is not proof of health.
- KRX historical worker `16c93d7c-7cd0-4d84-a327-298d2805376c`: 0 running / 0 crashed / 1 total, live activity NOT VERIFIED. Backend/push/db-query-readonly offline; db-query-readonly 1 critical.
- Staged environment patch `e113dacb-6705-4416-9997-dc694539d382` has zero listed changes. Do not commit it.
- Log window 2026-11-12 19:00–20:25 UTC: PIT 0, KRX 0, Kiwoom 0 deploy log records. Runtime returned 201 records (tool limit 200; count reflects response); USD/KRW Investing HTTP failure -> Yahoo fallback observed at 20:18:40 UTC. No evidence of KRX OHLC remediation or new original-filing approval. **ORDERING live config NOT VERIFIED** this run; required policy ORDERING=false, no authority to turn on.

## Profitability / PIT gate
- 2017–2022 KRX private 1565/1565 weekday pairs original storage SHA integrity: historical scoped PASS, not independently rehashed this run. 90 uncertain sessions, 12003 zero-activity exclusions and 2026-09-28 27 bad OHLC remain unapproved. Official calendar/trading state, corporate actions, fillability, security/corporate historical mapping and tax/cost: NOT VERIFIED.
- OpenDART original/correction SGML candidate rows 15 and adjacent numeric signature: historical source-form evidence only; exact original filing meaning, 2021/2022 first three-month consolidated operating profit, period/correction lineage, public available-at/PIT: NOT VERIFIED.
- M20 original PIT/labels, purging/CPCV, independent holdout, cost/tax-adjusted NetEV, PF, CAGR, MDD, ES95/99, concentration and regime robustness: NOT VERIFIED; economic RUN **NO-GO**.
- H5 holdout consumed/failed, Dynamic and archived alternatives cannot be retuned or recycled. Frozen H5; M20 horizon20/purge20; WF504/126/126; Champion/Top3/NO_TRADE and all risk/cost/tax gates unchanged.
- Cache only with complete independently approved source/data/code/Frozen/runtime/approval evidence SHA-256 matching, fail-closed. Only independent read-only postprocessing may parallelize; no dependent retraining or capital-transition parallelism.

## Next admissible steps
1. KRX owner independently rehash 27 private originals and prove exact official session/status/tradability and corporate-action lineage; do not publish private records.
2. OpenDART owner prove original-filing timestamps, precise first three-month consolidated operating-profit periods, corrections and corp/security PIT mapping, with original SHA.
3. Offline-only inspect PR #413/#418 immutable test artifacts and implementation SHA, independently reproduce fixed synthetic parity and CI wall-time without official market data.
4. Until source gates independently PASS, keep M20 NO-GO, ORDERING=false, no economic tests, trading, deployment, merges, workflow writes, or Champion promotion.
