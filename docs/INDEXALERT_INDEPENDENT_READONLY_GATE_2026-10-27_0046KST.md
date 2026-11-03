# IndexAlert independent read-only gate — 2026-10-27 00:46 KST

Scope: integration evidence only, separate from OpenDART/KRX/optimization owners. NO M20 financial run, no official data retrieval, no code/workflow edit, no deployment/merge, no orders/funds/credentials/permissions/Champion. All tests described below were previously executed by owners; this document independently checks current GitHub refs and CI log metadata. No new model search, Holdout or economics test.

## Current immutable refs (GitHub API read-only)
- Research `index-alert-research-v1`: `3b8b7830612a6284d7c7a60628cb527cb741627a`
- Development `index-alert-position-regen-fix-v1`: `1e6367d2863a86c3470da13d81a955d277eba485`
- Draft #414 (this documentation-only integration branch): `c0b05edd61215c8f12f423d4b6c20969adc2b9c4` before this audit-document addition.
- Draft #412 (OpenDART): `bf3d9514a87c53b1775e22ec9ba7711f6cecc49f`.
- Draft #413 (isolated runtime): `f003ef6247e16fcc71bd3b1b20cd4904c4d984c0`.
- Draft #418 (independent single runner): `2f98401cc50a6c6a25808a98516efd5bf0c944ee`.
- KRX delegated Drafts: #420 `fab3cbbd63a951a4e081f9e7f08c1391ca308581`, #422 `c14857620973531013799e44625d43080904fd5f`, #423 `0e38004363cac9fc4475556b3a1c445de9af407f`, #416 investor-flow `053de553646fc4765d2616544ca1e8d6bbdde35f`. All are still open/draft per metadata, not merged.

## Actual CI evidence and limited verdict
- Latest observed watchdog [run 40326183435](https://github.com/kims34/openpilot-opkr/actions/runs/40326183435), 2026-10-26 12:54 UTC, 1/1 job success; log explicitly: `M20 PIT admission: NOT ATTESTED; orders: DISABLED; holdout: NOT AUTHORIZED`. This is a governance observation, not a production config read.
- OpenDART first-filed 2021 Q3 [run 40262558066](https://github.com/kims34/openpilot-opkr/actions/runs/40262558066) successful. Artifact #12625042488 has GitHub-recorded ZIP artifact digest `3fe75e2af23f508d3c518a14e98732a399eb0daeca46cccd7b3191b1e2e4777b` (artifact ZIP, not statutory source ZIP). Source owner reports fixed official statutory original ZIP SHA-256 `8728c0a3c12761ca19e9c6455bea8f1bed0e4c1ebc2e21dc263c373a82a2b625`; 1 SGML, 1,728 tables, 13 candidate profit labels, **zero** independently bound original three-month CFS operating-profit facts. This audit did not independently download and rehash statutory raw bytes, therefore do not upgrade source proof to full financial semantics or PIT.
- Latest OpenDART TOC [run 40263193758](https://github.com/kims34/openpilot-opkr/actions/runs/40263193758), 1/1 offline synthetic job success with 13 tests; explicit `m20_feature_pit_admitted=False`, `m20_performance_run_authorized=False`, `ordering=DISABLED`. No real original first-publication timestamp/quarterly CFS proof.
- KRX investor-flow [run 40262192831](https://github.com/kims34/openpilot-opkr/actions/runs/40262192831), two offline jobs success; source-boundary job log shows 214 synthetic tests passed, and owner records 49 original-pinned pandas tests (263 aggregate). This is synthetic/archived-contract parity only, not actual original private state/receipt/provider payload authentication.
- KRX 2021/2022 day-set comparator Drafts #422/#423 and exceptional-session Draft #420 have offline CI, but **no authorized real Railway private day-set execution**; equality of empty-day counts cannot certify exact exchange trading calendar, historical security tradability or PIT.
- Optimization Draft #413 latest associated [run 38508247773](https://github.com/kims34/openpilot-opkr/actions/runs/38508247773) success is offline 34-case regression only; PR #418 old archive source blob mismatch remains an unresolved merge-context gate. No independent full CI or official backtest acceleration is proven; fail-closed source/code/policy/runtime SHA binding remains required.

## Railway connector access boundary
A direct read-only Railway project inventory attempt in this audit returned **`User input required but current turn is running in a non-interactive mode`**. No Railway deployment, private volume, production log, live ORDERING configuration or staging state was accessed in this run. Previous 1,565/1,565 weekday private storage SHA claim is prior evidence only, NOT re-attested today. No auth workaround or environment changes attempted. Owner must complete normal interactive Railway connection/authorization before future live-log attestation.

## Explicit gate matrix
- Source identity: prior OpenDART/KRX SHA and successful CI evidence **LIMITED PASS** for archived/source bytes only; no independent rehash of protected raw sources this run.
- First-public original filing, exact public available-at, 2022/2021 standalone July–September consolidated operating income, correction/vintage lineage, historical corp/security mapping: **NOT VERIFIED**.
- Official KRX calendar/trading status, suspensions, delistings, corporate actions, market cap, execution/fillability and fees/slippage/tax: **NOT VERIFIED**.
- Independent after-cost/tax NetEV, Profit Factor, CAGR, MDD, ES95/ES99, return concentration, date-cluster confidence, time-window robustness and tiny-lot feasibility: **NOT VERIFIED** (no approved M20 economic run).
- H5 consumed/failed Holdout: **DO NOT REUSE**; Frozen H5, M20 horizon20/purge20, WF504/126/126, Purged/CPCV, independent Holdout, Champion, Top3, NO_TRADE, costs/tax/risk/promotion policy unchanged.
- `ORDERING=false` remains required, **not freshly confirmed on Railway**. M20 performance run **NO-GO**; PR #413/#414/#418 merge, production deploy, live orders, funds, permission changes, Champion promotion forbidden.

## Next permitted independent steps
1. OpenDART owner: independently bind first-edition official 2022/2021 three-month CFS facts and exact earliest public availability with edition/correction SHA, without modern revised-value backfill.
2. KRX owner: separately authorized read-only private source audit and original exchange-calendar, issuer-security, corporate-action and tradeability evidence; no new worker deploy or data acquisition.
3. Runtime owner: fail-closed transitive source/code/runtime manifest parity and repeatable full-job CI timing with synthetic inputs only.
4. Integration owner: check updated evidence SHA/CI/production logs, update isolated audit documentation only; no financial performance experiment until *all* original source/PIT/market gates independently PASS.

This file records evidence boundaries only and grants no trading, data, holdout or deployment authorization.
