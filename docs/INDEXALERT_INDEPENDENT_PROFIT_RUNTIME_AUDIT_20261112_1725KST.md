# IndexAlert independent audit — 2026-11-12 17:25 KST

## Read-only source snapshots
- Research branch HEAD: df474df348f22aa38b1dedaa59fcff66e548b406; development branch HEAD: 1e6367d2863a86c3470da13d81a955d277eba485 (GitHub branch API).
- Draft open, unmerged PR HEADs: #412 bf3d9514a87c53b1775e22ec9ba7711f6cecc49f; #413 f003ef6247e16fcc71bd3b1b20cd4904c4d984c0; #414 18c5418d9684d1717df58261ea27f28e514385b2; #418 2f98401cc50a6c6a25808a98516efd5bf0c944ee; #420 fab3cbbd63a951a4e081f9e7f08c1391ca308581; #422 c14857620973531013799e44625d43080904fd5f; #423 0e38004363cac9fc4475556b3a1c445de9af407f.
- #414 integration gate file blob SHA 984c933651f39f1ee9e26a1d7ac3893aaa5335be, fetched at #414 HEAD.
- GitHub Actions job API: 38381997417 6/6 SUCCESS; 38382214223 6/6 SUCCESS; 38419111311 6/6 SUCCESS; 38419649711 1/1 SUCCESS; 38419439742 2/2 SUCCESS. This is CI execution status, not proof of PIT correctness or profitability. Historical 34-case digest 5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34 was not independently recomputed in this audit.

## Railway production read-only status and log window
Project d1c1a050-b7d6-41ce-b300-13c20f82a20a, environment 83d5840b-270e-4d3f-a941-a37fd4a55ff7. PIT rebuild 1/1 running, runtime 1/1 running; KRX worker 0/1 running (0 crashed), Kiwoom real readonly 0/1 running and 1/1 crashed despite top-level online label: operational FAIL. Backend, push and db-query-readonly offline; db-query-readonly has 1 critical issue. Empty staged patch e113dacb-6705-4416-9997-dc694539d382, no application. Log query 2026-11-12 07:20–08:26 UTC: PIT 0, KRX 0, Kiwoom 0 deploy entries; runtime 31 returned deploy entries, including Naver KOSPI and USD/KRW Yahoo feed observations. Zero log entries is not proof of no activity.

## Independent acceptance matrix
- Historical KRX weekday raw pair storage 1565/1565: PASS **only for previously reported raw-pair integrity**; this run did not recompute private source digests. Official trading calendar, suspensions, delistings, corporate actions, historical mapping, executable liquidity, transaction costs/taxes: NOT VERIFIED, fail-closed.
- OpenDART original/correction SGML 15 candidate rows and adjacency signature: historical evidence only, original meaning, exact quarter window, 2021/2022 first 3-month consolidated operating income, correction lineage, official public available-at/PIT: NOT VERIFIED, fail-closed.
- H5 consumed/failed holdout: NO-GO; no retrospective tuning or independent holdout reuse. M20 horizon20/purge20 WF504/126/126: NO-GO pending source PIT approval; no economic run.
- Annual after-cost-and-tax risk-adjusted NetEV, PF, CAGR, MDD, ES95/99, return concentration, period robustness: NOT VERIFIED; no claimed financial PASS.
- #413/#418 isolated offline CI: PASS for enumerated jobs only; historical 34-case SHA independently NOT VERIFIED; synthetic 28/adversarial 13 reported previously, not rerun. Serial 2.9656s vs concurrent 2.6209s is regression-phase ratio 1.1315x, not end-to-end speedup.
- ORDERING=false required, live environment variable NOT VERIFIED; no credentials or variables changed.

## Frozen gates and next actions
Preserve Frozen H5, M20 horizon20/purge20, WF504/126/126, PIT/labels/Purged/CPCV/independent Holdout/Champion/Top3/NO_TRADE and all cost/tax/execution/risk/promotion thresholds. Cache only with matching approved-source/data/calculation-code/Frozen-policy/runtime/approval-evidence SHA-256, fail-closed; parallelize read-only postprocessing only, never dependent retraining or capital transitions. Next read-only checks: official original-filing available-at provenance, quarter/correction lineage, KRX trading-state/corporate-action proof and independent source SHA verification; investigate crashed readonly Kiwoom replica without restart or deployment. No market backtests, model search, workflow edits, merges, live orders, funds movement, credential changes or Champion promotion.