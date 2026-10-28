# Independent M20 profitability source gate — 2026-10-28 18:43 KST

**Decision: NO-GO.** Source PIT is not admitted. Do not execute M20 economic backtest or interpret NetEV/PF/CAGR/MDD/ES95/ES99 as measured. This is documentation-only, read-only evidence integration; it is not new data admission or operational authorization.

## Directly checked immutable refs and Draft PR state
- Research `index-alert-research-v1` = `3b8b7830612a6284d7c7a60628cb527cb741627a`.
- Development `index-alert-position-regen-fix-v1` = `1e6367d2863a86c3470da13d81a955d277eba485`.
- KRX specialist `indexalert-krx-pit-source-audit-20261013` = `073d2d49e95f69fb10b943b93e51bb179fb3c698`.
- PR #412 `bf3d9514a87c53b1775e22ec9ba7711f6cecc49f`, #414 before this receipt `326dbccc22e9c5347360b8b7d97c5273b57184a8`, #416 `053de553646fc4765d2616544ca1e8d6bbdde35f`, #418 `2f98401cc50a6c6a25808a98516efd5bf0c944ee`, KRX #420 `fab3cbbd63a951a4e081f9e7f08c1391ca308581`, #422 `c14857620973531013799e44625d43080904fd5f`, #423 `0e38004363cac9fc4475556b3a1c445de9af407f`: all directly read OPEN/DRAFT/unmerged. Latest #414 prior commit changed only `docs/INDEXALERT_INDEPENDENT_PROFIT_RUNTIME_AUDIT_20261028_1823KST.md`, not an original source.

## Independently decoded CI logs, with strict scope
- [Watchdog #40638905543](https://github.com/kims34/openpilot-opkr/actions/runs/40638905543), job 122652181922: 4 watchdog + 31 governance offline tests passed, `M20 PIT admission: NOT ATTESTED; orders: DISABLED; holdout: NOT AUTHORIZED`. Flags-only artifact ZIP SHA-256 `e2ba2a470207125f1d061b5378fe1a1e68f1676ad4dee9d5bae36686ec297903` is not a source-archive digest. No repository-wide latest Actions listing available, so do not claim absolute newest.
- [DART 2021 first-original #40262558066](https://github.com/kims34/openpilot-opkr/actions/runs/40262558066), job 121379096007: original ZIP SHA-256 `8728c0a3c12761ca19e9c6455bea8f1bed0e4c1ebc2e21dc263c373a82a2b625` asserted by official CI; 13 operating-label table candidates, no exact same-table three-month CFS operating profit. 2021 first-publication instant, issuer/security as-of and complete amendment chain not proven.
- [DART 2022 first-original #38380988990](https://github.com/kims34/openpilot-opkr/actions/runs/38380988990), job 115241142185, and [correction #38419439742](https://github.com/kims34/openpilot-opkr/actions/runs/38419439742), job 115372636726: 15 original/corrected operating-label row shapes; no verified exact three-month 2022/2021 CFS comparator, correction semantics, or historical publication PIT. Previous recorded first-original ZIP SHA-256 `56639d8f6ebbecf14cd8bc3179d75d01162e2cd7bbdf8f6a3c9479b44f5084bb`; original bytes not rehashed in this run.
- [KRX offline #39721289545](https://github.com/kims34/openpilot-opkr/actions/runs/39721289545), job 119635081965: 164 synthetic/offline tests pass, **not** authenticated official exchange calendar or individual stock tradability. 90 unresolved historical source-empty sessions, 27 bad nonpositive OHLC, 12,003 zero-activity observations, and exact original-private 2021 13-day / 2022 14-day comparisons remain unresolved. No original private bytes/day sets were accessed.
- [Chronology Anchor #40534270813](https://github.com/kims34/openpilot-opkr/actions/runs/40534270813): job 122295113858 failed HTTP 404; validation job 122295116456 skipped. No fallback.
- [Runtime #418 archived parity #39111405478](https://github.com/kims34/openpilot-opkr/actions/runs/39111405478) failed manifest Git blob SHA mismatch expected `108f66714602a1bd3ae42c34dcca7c16e38f460b`, observed `e0055c66c59398fd4a1158077446d886b54c4e37`; candidate #39111405494 explicitly denies merge, complete transitive pinning, official PIT and economic measurement.

## Operational/economic decision
- Railway `list_projects({})` read-only attempted once; connector returned `User input required but current turn is running in a non-interactive mode.` Stop there, no authentication workaround. Actual production logs and `ORDERING` value **not directly verified**; policy requires `ORDERING=false`.
- No authenticated historical security tradability, delisting/halt/corporate action, executable price/volume, fee/slippage/tax, or as-of financial feature panel. Therefore after-cost/tax NetEV, PF, CAGR, MDD, ES95/99, cost stress, and holdout verdict **NOT EVALUABLE** (not zero or PASS).
- Preserve Frozen horizon20/purge20, WF504/126/126, sealed Holdout, Champion/Top3 unchanged, Dynamic 0–N Challenger-only, NO_TRADE, no ordering. No source/performance/holdout/live authority was granted.
- Specialist DART/KRX lanes own original-source admission and private exact-day comparison; no duplicate capture or test replay here. No trades, funds, permissions, secrets, deployments, PR merges, Champion promotions or code changes.
- No newly approved original source or new critical blocker was found; previous blockers remain open.

**Change scope:** one new isolated Markdown receipt on existing Draft #414 branch only. Git blob SHA-1 of this Markdown is not an original-data SHA-256.
