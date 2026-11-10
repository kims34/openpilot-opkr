# IndexAlert independent profitability and runtime audit — 2026-11-11 06:20 KST

Read-only source check, independent document-only isolation. No market-performance experiment, production write, workflow edit, order, approval, or merge.

## GitHub pinned evidence
- Research `index-alert-research-v1`: `df474df348f22aa38b1dedaa59fcff66e548b406`; development `index-alert-position-regen-fix-v1`: `1e6367d2863a86c3470da13d81a955d277eba485` (development HEAD corroborated by deployed KRX worker commit, prior direct confirmation; current compare returns base research SHA, diverged ahead 1148/behind 281, not head SHA).
- Draft OPEN/unmerged PR HEADs: #412 `bf3d9514a87c53b1775e22ec9ba7711f6cecc49f`; #413 `f003ef6247e16fcc71bd3b1b20cd4904c4d984c0`; #414 `18c5418d9684d1717df58261ea27f28e514385b2`; #418 `2f98401cc50a6c6a25808a98516efd5bf0c944ee`; #420 `fab3cbbd63a951a4e081f9e7f08c1391ca308581`; #422 `c14857620973531013799e44625d43080904fd5f`; #423 `0e38004363cac9fc4475556b3a1c445de9af407f`.
- #414 gate file blob SHA `984c933651f39f1ee9e26a1d7ac3893aaa5335be`, fetched from PR branch `indexalert-profitability-integration-evidence-20261013`.
- GitHub Actions jobs directly rechecked: 38381997417 6/6 success, 38382214223 6/6 success, 38419111311 6/6 success, 38419649711 1/1 success, 38419439742 2/2 success, follow-up 38498552499 6/6 success. Fixed 34-case SHA `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34` and 13/28/21 synthetic details NOT independently recomputed this run.
- PR #413's later offline result: serial 1.7114s vs parallel 2.5776s, negative speed-up. PR #418 merged-context implementation SHA mismatch must remain blocked. Full CI/official market backtest acceleration NOT VERIFIED.

## Railway production read-only
- Project `d1c1a050-b7d6-41ce-b300-13c20f82a20a`, production. No staged changes; all services configured replicas=1 (this is *configuration*, not runtime health). PIT, KRX worker, runtime and Kiwoom readonly latest deployments SUCCESS; backend and push latest FAILED. PIT/worker/Kiwoom recent deploy logs zero; runtime deploy log has 31 entries including market quote checks, not source PIT approval. No evidence that KRX worker is actually healthy just from deployment SUCCESS.
- KRX worker latest SUCCESS deployment `16c93d7c-7cd0-4d84-a327-298d2805376c`, commit `1e6367d2863a86c3470da13d81a955d277eba485` (2026-10-12). PIT latest SUCCESS `8b354fc1-cfb2-4ef0-863e-67f7f5dda2b5`, commit `e57054ecdb3e734ced3c9a981b887d9b5fc60f97` (2026-10-10).
- Historical protected KRX 2017–2022 1565/1565 weekday daily/master raw pair integrity PASS as *prior evidence*, not rerun. Ninety unknown calendar flags, 27 nonpositive OHLC rows, 12003 zero-activity exclusions remain not independently resolved. Runtime ORDERING env var NOT directly checked; no authorization to change it.

## Admission gates
- OpenDART original SGML candidate row and original ZIP identity: limited historical source-fingerprint PASS only. Original first-filed 2022/2021 standalone Q3 3-month CFS operating profit cells, public available-at, corrections/lineage, issuer/security historical mapping: NOT VERIFIED.
- KRX official trading sessions, instrument trading states, corporate actions, realistic executable fills, fees/taxes: NOT VERIFIED.
- After-tax/after-cost NetEV, PF, CAGR, MDD, ES95/99, concentration and time-slice robustness: NOT VERIFIED. **M20 NO-GO**. No economic backtest authorized.
- Frozen H5 and M20 horizon20/purge20, WF504/126/126, PIT, Purged/CPCV, sealed Holdout, Champion, Top3, NO_TRADE unchanged. Holdout already consumed/failed must not be reused. Cache requires independent original/data/code/Frozen/runtime/evidence SHA256 exact parity and fail-closed; only independent read-only postprocessing may parallelize.
- Next independent work: source-owner proof of 2021/2022 first-filed three-month CFS amount and exact publication time; KRX owner's authenticated original official session/status/CA provenance and private historical comparator; only then independent transaction-cost/tax/fill and economic admission review. Never merge, deploy, trade, alter credentials, or enable ORDERING without explicit separate authorization.
