# IndexAlert independent profitability evidence delta — 2026-10-29 16:50 KST

**Scope:** Independent read-only GitHub branch/PR/Actions and Railway production inspection. This is a source and safety audit, **not** a financial backtest or a trading, deployment, merge, or promotion authorization. Other specialists' KRX, OpenDART, and optimization work was not repeated or modified.

## Immutable checks (UTC times unless specified)

- Research `index-alert-research-v1` HEAD `3b8b7830612a6284d7c7a60628cb527cb741627a`; development `index-alert-position-regen-fix-v1` HEAD `1e6367d2863a86c3470da13d81a955d277eba485`; KRX source-audit branch `indexalert-krx-pit-source-audit-20261013` HEAD `073d2d49e95f69fb10b943b93e51bb179fb3c698`.
- Draft/unmerged PRs: #412 `bf3d9514`, #414 `678c7375` (documentation-only head advanced since prior audit), #416 `053de553`, #418 `2f98401c`, #420 `fab3cbbd`, #422 `c1485762`, #423 `0e380043`. #414 advance does not itself confer any source/economic admission.
- GitHub Actions list: 4,617 runs at inspection; latest two #40828908590 and #40828341381 are ETF offline-only successes, **not** M20 evidence. [Hourly Watchdog #40806178512](https://github.com/kims34/openpilot-opkr/actions/runs/40806178512) succeeded, and its raw job log says `M20 PIT admission: NOT ATTESTED; orders: DISABLED; holdout: NOT AUTHORIZED`; 31 governance tests passed (4 safety tests reported separately in prior audit).
- Prior prospective chronology [#40726273259](https://github.com/kims34/openpilot-opkr/actions/runs/40726273259) HTTP 404 remains an unresolved earlier failure; no independently authenticated replacement anchor observed.

## Railway production independent read-only check

- Project `d1c1a050-b7d6-41ce-b300-13c20f82a20a`, production environment `83d5840b-270e-4d3f-a941-a37fd4a55ff7`.
- Real read-only service latest deployment `a77fb922-b679-4d88-92c4-03054ec579cd` SUCCESS, created 2026-10-29 06:21:36Z, source commit `85bb6fd10bcc9ff2b14abe1c774f0d99f8eb84ab` (not current development HEAD). Actual deployment logs only show container startup; build logs show image digest `sha256:9fe36921f791844fb1487c873c015bf30f82e0f933f915c143316ea85bdf95fa`. **Neither proves live environment ordering flags.** No new deployment or config change performed.
- PIT service historical runtime log (last observed 2026-10-26 14:31Z) remains `FAIL_CLOSED`, `ordering=DISABLED`, `real_orders_authorized=false`, `independent_source_admission_verified=false`, `COMMON_OHLC_NONPOSITIVE` (27 rows among 803 common-stock rows, source failure session 2026-09-28). This is a *service-specific observed flag*, not an attestation of all Railway variables or other services.
- Railway environment health shows 3 pre-existing offline/issue services (`indexalert-push`, `indexalert-backend`, `db-query-readonly`), zero recent failed deployments in the queried 8-hour window; no evidence these are newly introduced M20 blockers. Staged configuration in the environment description is null.

## Source / PIT / profitability admission gates

| Gate | Verdict and exact limitation |
| --- | --- |
| OpenDART original ZIP SHA-256 and 2021/2022 Q3 3-month CFS operating-profit semantics, original publication available-at, amendment chain, historical issuer-security mapping | Historical official-run digest receipts exist (2022 first original SHA-256 `56639d8f6ebbecf14cd8bc3179d75d01162e2cd7bbdf8f6a3c9479b44f5084bb` from PR #412); **raw ZIP bytes not independently rehashed this run**; strict semantic/time/correction/issuer PIT remains NOT VERIFIED. |
| KRX raw 2017–2022 storage and exact trading-day/security admissibility | Historical 1,565/1,565 private SHA-pair integrity is a prior scoped receipt, not fresh raw-byte rehash. 90 uncertain 2017–2022 sessions, exact 2021 13-day and 2022 14-day private date-set comparison, 2026-09-28's 27 quarantined OHLC rows, corporate actions and executable fills are NOT ADMITTED. Draft #420/#422/#423 synthetic CI cannot grant source/tradability authority. |
| Costs, slippage, spread, taxes, fill model, settlement | Offline regression success only; no independently reconciled actual fee/tax schedule or executable fills for an admitted M20 universe. NOT VERIFIED. |
| Runtime optimization / manifest parity | Prior #418 merged-context pinned-parallel CI failed on archived Git blob mismatch (`108f6671` expected vs `e0055c66` observed); separate offline successes do not clear semantic/cache lineage or frozen manifest gate. No rerun/patch here. |
| NetEV after fees/tax, PF, CAGR, MDD, ES95/ES99, date/concentration robustness | **NOT EVALUABLE. M20 PERFORMANCE NO-GO.** No backtest, invented metrics, or Holdout replay. |

**Hard guard:** Frozen H5; M20 horizon20/purge20, WF504/126/126; PIT/purged/CPCV/Holdout/Champion/Top3/NO_TRADE policy unchanged. `ORDERING=false` is a required invariant; global runtime variable value not independently attested by this audit. No orders, funds, permission change, deployment, PR merge, Champion promotion, or external API retry. Next admissible progress requires independently verified first-filed financial semantics and timestamps plus exact KRX day/security tradability and cost/tax evidence; only then consider separately authorized one-shot Frozen M20 economic run.

**Delta:** No new admissible original source or economic evidence; no new critical blocker discovered. Only this isolated documentation file was attempted.
