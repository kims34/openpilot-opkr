# IndexAlert independent profitability gate — 2026-10-24 18:47 KST

Scope: read-only cross-workstream audit, **not** an authorization for market-source admission, a new profitability run, Holdout access, trading, deployment, PR merge, or Champion promotion. Only this independent audit document is written on the existing Draft #414 isolation branch. Do not alter other workstreams.

## Exact refs observed via GitHub connector
- Research `index-alert-research-v1`: `3b8b7830612a6284d7c7a60628cb527cb741627a`.
- Development `index-alert-position-regen-fix-v1`: `1e6367d2863a86c3470da13d81a955d277eba485`.
- Draft #414 integration head **before this document write**: `413f7d91190ee8308fd1111a468e10927e9d87c3`; integration gate document Git blob `984c933651f39f1ee9e26a1d7ac3893aaa5335be`.
- Draft #412 OpenDART head: `e82b26e2431ea15a42888f073a4b0b72a2e11ef6`.
- Draft #413 offline optimization head: `f003ef6247e16fcc71bd3b1b20cd4904c4d984c0`.
- Draft #418 single runner head: `2f98401cc50a6c6a25808a98516efd5bf0c944ee`.
- KRX Draft #420 head `fab3cbbd63a951a4e081f9e7f08c1391ca308581`; #422 `c14857620973531013799e44625d43080904fd5f`; #423 `0e38004363cac9fc4475556b3a1c445de9af407f`. All remain Draft/unmerged.

## Independently inspected actual Actions evidence
- Latest read-only watchdog [#40067673639](https://github.com/kims34/openpilot-opkr/actions/runs/40067673639), created 2026-10-24 05:48 UTC: one job SUCCESS, governance tests PASS; log says `M20 PIT admission: NOT ATTESTED; orders: DISABLED; holdout: NOT AUTHORIZED`. Flags-only ZIP artifact ID `12550355815`, ZIP SHA-256 `99fea0e7137c5f2b4cd24f520d3beab0b35a5e075cec71c2dcd1c482ed00e8d2`. This ZIP SHA is **not** an independently validated OpenDART/KRX raw-source SHA.
- Prospective chronology [#39972035700](https://github.com/kims34/openpilot-opkr/actions/runs/39972035700), created 2026-10-23 14:43 UTC: FAIL; `/anchor/latest` HTTP 404 after retries, immutable chronology append and validation SKIPPED. This is a prospective anchor-source availability failure, not a retrospective market-return result.
- OpenDART Draft #412 current-head offline-only [#39884427765](https://github.com/kims34/openpilot-opkr/actions/runs/39884427765) and [#39884427805](https://github.com/kims34/openpilot-opkr/actions/runs/39884427805): SUCCESS for synthetic edition/TOC guards, **not** official first-original financial-cell proof. Official narrowly scoped 2026-10-22 index [#39884243351](https://github.com/kims34/openpilot-opkr/actions/runs/39884243351): two jobs SUCCESS, `013` no periodic rows in that one-day query, zero newly identified target corrections; ZIP SHA-256 `02e829d3a5fdde8754f649431363c74221eb192b78b8237c911f74b54325820c`. Its own log explicitly leaves first-publication instant, 2022/2021 standalone CFS quarter, amendment lineage, issuer/security mapping and PIT FALSE.
- KRX #420 current-head synthetic-only [#39714369438](https://github.com/kims34/openpilot-opkr/actions/runs/39714369438): SUCCESS; actual private historic day sets, official session/status, corporate actions, fill feasibility NOT independently verified.
- Optimization #413 current-head [#38508247773](https://github.com/kims34/openpilot-opkr/actions/runs/38508247773): 6/6 jobs SUCCESS; offline parity only. Prior 34-case canonical digest `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34` is **a fixed test-outcome digest**, not a historical price-data SHA. Total CI/full admitted backtest acceleration NOT VERIFIED.
- Single runner #418 current-head [#39111405478](https://github.com/kims34/openpilot-opkr/actions/runs/39111405478): FAIL CLOSED on `research_v1_runtime_manifest.py` archived blob identity (expected Git blob `108f66714602a1bd3ae42c34dcca7c16e38f460b`, observed `e0055c66c59398fd4a1158077446d886b54c4e37`). Python/package versions PASS (22 packages), exact wheel SHA and native OS dependency identity NOT VERIFIED. Do not silently repin archived baseline or enable cache/merge.
- Prior official first-original OpenDART document SHA-256 `56639d8f6ebbecf14cd8bc3179d75d01162e2cd7bbdf8f6a3c9479b44f5084bb` remains a **previously reported source-identity digest**, not re-downloaded/recomputed in this audit. Railway 2017–2022 private 1,565/1,565 weekday-pair storage SHA PASS is also **previously reported**, not independently refreshed in this audit.

## Railway read-only boundary
Direct `list_projects` attempt returned `User input required but current turn is running in a non-interactive mode.` No latest deployments/logs, private KRX volume, or actual current production ORDERING flag could be independently read. **Do not claim production ORDERING=false is freshly verified.** Existing policy requires ORDERING=false. Do not change credentials, access or deployment.

## Gate verdict (as of this audit)
- PASS (limited): GitHub ref/status snapshots, watchdog governance/offline tests, OpenDART one-day index query, KRX synthetic safety checks, #413 offline parity; previous OpenDART raw archive and KRX storage identity are *historical reported* integrity evidence only.
- FAIL: #418 archived source blob identity; prospective chronology endpoint 404.
- NOT VERIFIED: 2022/2021 original standalone three-month consolidated operating-profit cells; exact first-public `available-at`/PIT and full correction chronology; historical issuer-security map; official KRX daily session/security trade status, corporate actions, fills, real fees/taxes; admitted immutable raw-source SHA chain for full cohort; NetEV, PF, CAGR, MDD, ES95/99, return concentration, temporal robustness; production deployment/logs/ORDERING state; end-to-end optimization.
- **M20 PIT admission: NO-GO. M20 economic/backtest run: PROHIBITED.** Frozen H5; M20 horizon20/purge20; WF504/126/126; PIT, Purged/CPCV, sealed/consumed Holdout, Champion/Top3/NO_TRADE, costs/tax and promotion thresholds unchanged. No post-hoc H5/Dynamic repair, no sealed Holdout reuse. Only synthetic/offline software safety work permitted before source admission. Fail-closed cache requires exact approved source/data/code/policy/runtime/evidence SHA; only independent read-only postprocessing can be parallelized, not training or capital transitions.
- No orders, money movements, permissions/credentials changes, production deploys, PR merges, Champion promotion or live ORDERING change.

## Next independent evidence
1. Source owners must independently establish original-first-edition CFS 2022 and 2021 three-month operating-profit cells and their first-public timestamp/correction lineage; no M20 economics until PASS.
2. KRX owners must establish official vintage/session/security tradability, corporate actions and fill/cost/tax evidence against original private SHA receipts; keep 90 unresolved historical days and 27 prospective nonpositive-OHLC rows quarantined.
3. #418 owner must resolve immutable archived-source blob drift *without baseline repinning* and establish full dependency/wheel/native integrity, then benchmark whole CI separately from real admitted-data backtest.
4. Railway read-only access remains blocked by interactive authentication; no workaround. Preserve distinct specialist ownership and Draft PR isolation.

Evidence is bounded to sources actually queried this turn.