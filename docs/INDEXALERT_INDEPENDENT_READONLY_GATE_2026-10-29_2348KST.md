# IndexAlert independent read-only profitability gate — 2026-10-29 23:48 KST

## Scope and provenance (read-only)
This document records a **metadata/log review only**, not a backtest, data admission, deployment, execution, or financial recommendation. This is a one-file isolated documentation update on the existing Draft PR #414 integration branch. No other specialist branch or implementation modified.

- Research `index-alert-research-v1`: `3b8b7830612a6284d7c7a60628cb527cb741627a`.
- Development `index-alert-position-regen-fix-v1`: `1e6367d2863a86c3470da13d81a955d277eba485`.
- KRX specialist `indexalert-krx-pit-source-audit-20261013`: `073d2d49e95f69fb10b943b93e51bb179fb3c698`.
- Draft/unmerged PRs: #412 `bf3d951`, #414 `3f74e3a` (pre-document), #416 `053de55`, #418 `2f98401`, #420 `fab3cbb`, #422 `c148576`, #423 `0e38004`.
- GitHub Actions latest list: 4,618 runs; latest read-only Watchdog [#40853112299](https://github.com/kims34/openpilot-opkr/actions/runs/40853112299), created 2026-10-29 09:53 UTC, SUCCESS. Its job logs show 4 watchdog + 31 research-governance tests passed, while `M20 PIT admission: NOT ATTESTED; orders: DISABLED; holdout: NOT AUTHORIZED`. Chronology Anchor [#40726273259](https://github.com/kims34/openpilot-opkr/actions/runs/40726273259) remains FAILED.

## Original-source SHA / point-in-time gate
- Official OpenDART first-filed 2022 Q3 document [#38392847048](https://github.com/kims34/openpilot-opkr/actions/runs/38392847048) logs the source ZIP SHA-256 `56639d8f6ebbecf14cd8bc3179d75d01162e2cd7bbdf8f6a3c9479b44f5084bb`. This run **rechecked the log assertion and recorded digest, not the original ZIP bytes**; no independent byte-level rehash is claimed.
- Official first-vs-corrected diagnostic [#38419439742](https://github.com/kims34/openpilot-opkr/actions/runs/38419439742) logs 15 candidate label rows in each edition, with no label-text multiset difference. This does not prove identical normalized financial values.
- No verified original 2022/2021 comparable consolidated three-month operating-profit facts, full correction lineage, original publication instant, historical issuer/security PIT map, or source-level admission. `m20_feature_pit_admitted=false`; performance remains prohibited.

## KRX historical / prospective and economics
- KRX #420/#422/#423 are Draft offline/synthetic comparator work, not authoritative PIT evidence. Historic 2017–2022 90 unresolved session/calendar-source exceptions; 2021 private 13-day and 2022 private 14-day exact original date-set comparisons not executed or admitted; stock-level historical tradability remains unverified.
- Railway production `indexalert-pit-rebuild` latest observed 2026-10-29 14:46:21 UTC (23:46:21 KST) reports `status=FAIL_CLOSED`, `ordering=DISABLED`, `independent_source_admission_verified=false`, `independent_chronology_admission_verified=false`, `independent_model_admission_verified=false`, `live_order_authorized=false`, `real_orders_authorized=false`, `funds_movement_authorized=false`. `source_failure_session=2026-09-28`; 27 nonpositive common-stock OHLC rows, distinct from historical 90 sessions.
- Railway `indexalert-kiwoom-real-readonly` latest deployment SUCCESS 2026-10-29 06:21 UTC, pinned deployment source `85bb6fd10bcc9ff2b14abe1c774f0d99f8eb84ab` (not current development HEAD). No new runtime deploy logs in the requested late window; actual Kiwoom order-enabling environment value **not independently established**. Do not equate deployment SUCCESS with trading permission or safe configuration.
- Recorded offline tests and SHA-shaped receipts do not establish independent raw historical source bytes, order-book liquidity, corporate-action adjustment, stock-level fills, slippage, commissions, tax treatment, or executable NetEV. Runtime-manifest archived SHA mismatch previously identified remains unclosed; no attempt to change hashes or caches.
- NetEV, PF, CAGR, MDD, ES95/ES99 **not estimable/approved** from admitted historical executions. No synthetic or prospective observations may be relabeled as live/holdout profitability.

## Hard decision and authority
**M20 profitability run NO-GO** until independent original SHA-byte, source/PIT, tradability, cost/tax and chronology acceptance with immutable source lineage. Frozen, sealed Holdout, Champion, Top3, preregistration and ORDERING=false/disabled must remain unchanged. No trades, money movement, permission changes, production deploy, PR merge, Champion promotion, or other specialist implementation edits. No new material approval or novel critical blocker observed at this check.
