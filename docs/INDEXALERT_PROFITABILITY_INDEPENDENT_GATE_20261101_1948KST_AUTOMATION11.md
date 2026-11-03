# IndexAlert independent profitability gate — 2026-11-01 19:48 KST

Scope: read-only independent audit, with this one isolated Markdown evidence record only. No source acquisition, replay, backtest, holdout access, trading, deployment, permission or capital changes.

## GitHub immutable references checked
- Research base (PR #412): `3b8b7830612a6284d7c7a60628cb527cb741627a` (`index-alert-research-v1`); development base (PR #420): `1e6367d2863a86c3470da13d81a955d277eba485` (`index-alert-position-regen-fix-v1`).
- PR #414 head before this isolated documentation attempt: `72fe9e2d8bd4e981c35ba41e426e872763ac2d9e`; PR #412 head `bf3d9514a87c53b1775e22ec9ba7711f6cecc49f`.
- KRX specialist Draft PR #420 `fab3cbbd63a951a4e081f9e7f08c1391ca308581`; #422 `c14857620973531013799e44625d43080904fd5f`; #423 `0e38004363cac9fc4475556b3a1c445de9af407f`. All PRs above remain Draft, open, unmerged. Other specialist PR #416 read-only inspected for boundary; no modifications.
- Watchdog GitHub Actions run https://github.com/kims34/openpilot-opkr/actions/runs/41292056320, job 124805130699, completed success; logs show 31 governance tests passed, `M20 PIT admission: NOT ATTESTED; orders: DISABLED; holdout: NOT AUTHORIZED`. Workflow success is a guard check, not source/return approval.
- Chronology run https://github.com/kims34/openpilot-opkr/actions/runs/41091128151: auto-anchor failed, downstream validation skipped.

## Independent source, PIT, and execution gates
- Official 2022 OpenDART first-filing ZIP SHA-256 **recorded** as `56639d8f6ebbecf14cd8bc3179d75d01162e2cd7bbdf8f6a3c9479b44f5084bb` by PR #412; raw original ZIP bytes were **not independently retrieved or rehashed in this audit**. 15 candidate operating-profit row shapes do not establish exact standalone consolidated 3-month operating profit. First public timestamp, full corrections, comparison quarter and issuer mapping remain unverified.
- Historical KRX 90 uncertain calendar/source sessions and prospective 27 nonpositive common-stock OHLC rows remain quarantined. Actual source-vintage/PIT, issuer-day eligibility, corporate actions, auction fill/tradability, orderbook/slippage, commissions, taxes and broker reconciliation are not independently admitted.
- Railway production PIT `indexalert-pit-rebuild` most recent returned deploy log 2026-11-01 10:45:45 UTC (19:45:45 KST): `status=FAIL_CLOSED`, `error_reason_code=COMMON_OHLC_NONPOSITIVE`, `nonpositive_ohlc_rows=27`, `independent_source_admission_verified=false`, `ordering=DISABLED`, `live_order_authorized=false`.
- Railway `indexalert-kiwoom-real-readonly`: deployed SUCCESS but health inventory shows 0 running / 1 crashed replica. No demonstrated working real-order pathway or authorization. Railway staged-changes endpoint shows none; health pendingWork shows a staged patch with zero changes, an existing read-view inconsistency; no accept-deploy.
- As source/PIT/tradability and real execution costs are unapproved, do not calculate or label any NetEV, PF, CAGR, MDD, ES95, ES99 as validated. No M20 profitability run is permitted. Existing Frozen/Holdout/Champion/Top3 and preregistered evaluation constraints remain intact.

## Verdict
**NO-GO / FAIL-CLOSED.** `ORDERING=false` (runtime `DISABLED`). No M20 run, new data fetch, model promotion, sealed holdout use, broker orders, money movement, secret/permission change, deployment, PR merge or Champion/Top3 promotion. This file is a documentation-only audit and not an independent data admission certificate.
