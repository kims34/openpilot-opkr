# IndexAlert independent read-only audit — 2026-11-07 05:24 KST

Scope: evidence-only; no source admission, financial backtest, workflow modification, production deployment, order or promotion.

## Verified current observations
- GitHub branch names `index-alert-research-v1` and `index-alert-position-regen-fix-v1` exist (search_branches); current exact HEAD **NOT VERIFIED** (branch search does not expose SHA).
- Open PR search returns #412, #413, #414, #418, #420, #422, #423 (and other separate PRs). Search response does not independently establish Draft flag or current PR head SHA; those are **NOT VERIFIED**.
- Gate document at pinned historical ref `18c5418d9684d1717df58261ea27f28e514385b2` fetched read-only; do not confuse with current HEAD.
- GitHub Actions #41515392296 jobs: auto-anchor FAILURE at "Fetch today's public hash-only prospective payload"; validation SKIPPED. Previous job log analysis identified HTTP 404 on /anchor/latest; root cause of route mismatch/deployment remains **NOT VERIFIED**.
- Offline optimization CI #38498552499: six jobs SUCCESS. This confirms only synthetic offline safety/parity, not whole-CI speedup or admitted-data financial backtest speed. Prior fixed 34-case digest `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34` remains historical, not independently recomputed in this cycle.
- Railway IndexAlert production: PIT rebuild latest deployment `8b354fc1-cfb2-4ef0-863e-67f7f5dda2b5` SUCCESS (source commit `e57054ecdb3e734ced3c9a981b887d9b5fc60f97`); worker `16c93d7c-7cd0-4d84-a327-298d2805376c` SUCCESS (commit `1e6367d2863a86c3470da13d81a955d277eba485`). Latest deployment listings not necessarily chronological log freshness.
- PIT rebuild logs from 2026-11-06: `COMMON_OHLC_NONPOSITIVE`, 27/803 common stock rows, `FAIL_CLOSED`, `fresh_alpha_observation_admitted=false`, `live_order_authorized=false`, `ordering=DISABLED`. Data quality **FAIL**, safety veto **PASS**. Worker logs empty for retrieved interval: historical KRX tradability **NOT VERIFIED**.
- Runtime logs show Investing USD/KRW HTTP errors and Yahoo fallback; unrelated to PIT admission.

## Gate decisions
- OpenDART original filing, exact public available-at, 2021/2022 3-month consolidated operating profit correction lineage, historical entity/security mapping: **NOT VERIFIED**.
- Official KRX calendar/status/corporate actions/realistic fill/cost/tax: **NOT VERIFIED**. Historical pair-storage PASS is not trading admission.
- NetEV/PF/CAGR/MDD/ES95/99/concentration/robustness after costs and tax: **NOT VERIFIED**; M20 performance **NO-GO**.
- Frozen H5, M20 horizon20/purge20, WF504/126/126, sealed Holdout, Champion, Top3/NO_TRADE unchanged; ORDERING=false. No performance experiment, strategy search, merge, deployment, funds or orders.

## Next read-only steps
1. Compare /anchor/latest contract with deployed service route and exact deployment SHA; do not edit workflow or rerun anchor.
2. Validate exact original KRX OHLC offending-row provenance and official exchange status using the owning workstream's approved private evidence.
3. Independently inspect official first-filing period/lineage/available-at evidence before PIT admission.
4. Review #413/#418 cross-branch parity without repinning immutable digest or making financial speedup claims.
