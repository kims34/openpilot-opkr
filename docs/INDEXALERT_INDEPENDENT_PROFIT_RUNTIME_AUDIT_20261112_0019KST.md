# IndexAlert independent gate audit — 2026-11-12 00:19 KST

## Exact refs and authority
- Research `index-alert-research-v1` HEAD: `df474df348f22aa38b1dedaa59fcff66e548b406`; comparison to ref: identical 0/0.
- Development `index-alert-position-regen-fix-v1` HEAD: `1e6367d2863a86c3470da13d81a955d277eba485`; identical 0/0.
- Draft OPEN/unmerged PRs #412 #413 #414 #418 #420 #422 #423 independently read. #414 head `18c5418d9684d1717df58261ea27f28e514385b2`; integration document blob SHA `984c933651f39f1ee9e26a1d7ac3893aaa5335be`.
- Actions runs 38381997417 (6/6), 38382214223 (6/6), 38419111311 (6/6), 38419649711 (1/1), 38419439742 (2/2): all jobs success as retrieved. This does NOT independently recompute fixed 34-case SHA `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34`; that exact-byte parity is NOT VERIFIED this cycle.
- PR #413/#418 offline-only software gate: CI jobs PASS; serial 2.9656s vs concurrent 2.6209s historical claimed regression-phase ratio 1.1315x, not reproduced this cycle; full CI/official backtest acceleration NOT VERIFIED.

## Railway production read-only observation
- Project `d1c1a050-b7d6-41ce-b300-13c20f82a20a`, production `83d5840b-270e-4d3f-a941-a37fd4a55ff7`. Environment staged summary null, pendingWork nevertheless lists empty staged patch `e113dacb-6705-4416-9997-dc694539d382`; no commit/deploy.
- PIT rebuild `8b354fc1-cfb2-4ef0-863e-67f7f5dda2b5` and Runtime `eaaa9f67-b9f2-41d2-832c-7d6fad9b9b00`: 1/1 running.
- Historical KRX worker `16c93d7c-7cd0-4d84-a327-298d2805376c`: 0/1 running; live readiness NOT VERIFIED. Kiwoom real readonly `a77fb922-b679-4d88-92c4-03054ec579cd`: 0 running/1 crashed, runtime FAIL notwithstanding deployment SUCCESS.
- Backend/push/db-query-readonly offline; db-query-readonly 1 critical.
- PIT deployment log 2026-11-11 13:00–15:20 UTC: eight entries at 13:01, 13:16, 13:31, 13:46, 14:01, 14:16, 14:31, 14:46, all `KRXProspectiveOpenAPISourceError` / `COMMON_OHLC_NONPOSITIVE`. `fresh_alpha_observation_admitted=false`, `independent_source_admission_verified=false`, `independent_chronology_admission_verified=false`, `live_order_authorized=false`, `funds_movement_authorized=false`. FAIL-CLOSED observed; source validation FAIL.
- KRX/Kiwoom deploy logs zero in same interval (absence of entries is NOT health proof). Runtime USD/KRW Investing HTTPError with Yahoo fallback at 15:18 UTC; unrelated to approved PIT.

## Independent source/economic gates
- OpenDART original/SGML candidate 15 rows: historical structural signature evidence only. Original 2021/2022 first 3-month consolidated operating-profit period, complete correction lineage, actual intraday public available-at and historic issuer/security mapping: NOT VERIFIED; no retroactive corrected-value backfill.
- Historical KRX 2017–2022 1565/1565 weekday source pairs: prior storage-integrity PASS only; 90 missing/holiday classifications, 12003 zero-activity records, 2021/2022 exact-set private comparison, official trading status/corporate actions/fillability: NOT VERIFIED. No private volume audit run.
- PIT and M20: NO-GO; no official performance run authorized. NetEV, PF, CAGR, MDD, ES95/99, date concentration, cost/tax stress, time robustness and independent holdout: NOT VERIFIED. Historical H5/0-N promotion NO-GO; consumed holdout cannot be reused.
- Frozen H5, M20 horizon20/purge20, WF504/126/126, PIT/label/Purged/CPCV/Holdout/Champion/Top3/NO_TRADE, costs/tax/execution/risk unchanged. ORDERING=false. Cache only on independently approved complete SHA256 provenance; only independent read-only postprocessing may parallelize; no dependent refits/capital transition parallelization.
- Next: specialist source owners establish official original PIT/lineage and authenticated historical KRX market/tradability evidence, then independent admission; separately rerun approved synthetic fixed-SHA parity audit only. No model search, M20 economic test, real orders, fund movement, auth changes, Champion promotion, PR merge or deployment.
