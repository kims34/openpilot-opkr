# IndexAlert independent profitability / isolated runtime audit — 2026-11-04 05:20 KST

Read-only evidence inspection; no M20 economic run, production deployment, merge, order, account or workflow changes.

## GitHub heads and source
- Research branch index-alert-research-v1 and development branch index-alert-position-regen-fix-v1 exist; **current exact HEAD NOT VERIFIED** (branch search returns names only). Prior reported heads df474df348f22aa38b1dedaa59fcff66e548b406 and 1e6367d2863a86c3470da13d81a955d277eba485 are historical, not reasserted current.
- PR #412 bf3d9514a87c53b1775e22ec9ba7711f6cecc49f; #413 f003ef6247e16fcc71bd3b1b20cd4904c4d984c0; #414 18c5418d9684d1717df58261ea27f28e514385b2; #418 2f98401cc50a6c6a25808a98516efd5bf0c944ee; KRX #420 fab3cbbd63a951a4e081f9e7f08c1391ca308581, #422 c14857620973531013799e44625d43080904fd5f, #423 0e38004363cac9fc4475556b3a1c445de9af407f. All OPEN/DRAFT, not merged at inspection.
- PR #414 gate docs/INDEXALERT_PROFITABILITY_INTEGRATION_GATE_2026-10-13.md blob SHA-1 984c933651f39f1ee9e26a1d7ac3893aaa5335be, fetched at PR head. Gate explicitly blocks M20 PIT and trading.

## Actions
- #38381997417 6/6 success; #38382214223 6/6 success; #38419111311 6/6 success; #38419649711 1/1 success. These prove isolated synthetic CI success, not actual PIT, annual net profitability or total CI acceleration.
- OpenDART #38419439742 2/2 success; 15 candidate row signatures are historical evidence only, original-filing semantic/available-at approval NOT VERIFIED.
- Chronology anchor #41515392296 auto-anchor FAIL, validation SKIPPED. No chronology PASS.
- 34-case historical SHA-256 5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34 NOT independently recomputed this run. Synthetic regression serial 2.9656s vs concurrent 2.6209s (1.1315x) historical, not total acceleration.

## Railway
- IndexAlert project d1c1a050-b7d6-41ce-b300-13c20f82a20a production. KRX historical-worker deployment 16c93d7c-7cd0-4d84-a327-298d2805376c SUCCESS (2026-10-12, commit 1e6367d2863a86c3470da13d81a955d277eba485); PIT rebuild 8b354fc1-cfb2-4ef0-863e-67f7f5dda2b5fc60f97 SUCCESS (2026-10-10). Since 2026-11-03 18:00Z KRX and PIT rebuild runtime logs returned zero entries: absence of logs does NOT prove absence or resolution of anomalies. IndexAlert runtime service had logs through 2026-11-03 20:20Z, but market quotes are not M20 PIT evidence.

## Decision
- Storage pair integrity 1565/1565 historical PASS limited to persistence; official calendar/session/halts/corporate actions/tradability and identity-history NOT VERIFIED. 90 uncertain sessions, zero-activity 12003 and suspect OHLC remain fail-closed.
- OpenDART 2021/2022 original consolidated first-three-month operating-profit period, correction lineage, exact public available-at NOT VERIFIED.
- NetEV/PF/CAGR/MDD/ES95/ES99, return concentration, time robustness and tax/fee/slippage-aware annual risk-adjusted net return NOT EVALUABLE; M20 NO-GO. H5 spent holdout and dynamic findings not reusable.
- Offline CI limited PASS; actual backtest speed NOT VERIFIED. Cache only on independent approved source/data/code/Frozen/runtime/evidence SHA-256 identity; read-only postprocessing parallelism only; no dependent retraining or capital transition parallelism.
- Frozen H5; M20 horizon20/purge20; WF504/126/126; PIT/Purged/CPCV/independent holdout/Champion/Top3/NO_TRADE, economics and promotion policy unchanged; ORDERING=false. No market performance replay, tuning, M20 run, merge or deployment.

## Next independent evidence
Obtain exact branch HEAD using authoritative ref endpoint; reconcile original filing semantics and public available-at, official KRX calendar/tradability and OHLC anomalies; verify immutable artifact hashes and holdout provenance before any economic test. Keep all changes confined to isolated documentation, and never infer PIT approval from a green CI/deployment.
