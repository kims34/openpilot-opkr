# IndexAlert independent profitability gate — 2026-11-01 21:43 KST

**Audit scope:** read-only GitHub repository/PR/Actions and Railway deployment/log evidence; this one isolated documentation note is the only attempted write. No trading, execution, deployment, PR merge, research-code change, source admission, Holdout use, or Champion/Top3 change.

## Immutable repository evidence
- Research `index-alert-research-v1` HEAD: `3b8b7830612a6284d7c7a60628cb527cb741627a`.
- Development `index-alert-position-regen-fix-v1` HEAD: `1e6367d2863a86c3470da13d81a955d277eba485`.
- KRX specialist `indexalert-krx-pit-source-audit-20261013` HEAD: `073d2d49e95f69fb10b943b93e51bb179fb3c698`.
- PR #414 remains Draft/open/unmerged; head before this note `71ff66aaa5b153adce3d4b7b2213dfcd6ed140eb`. PR #412 and KRX #420/#422/#423 remain Draft/open/unmerged; no source approval.
- [Read-only watchdog Actions #41292056320](https://github.com/kims34/openpilot-opkr/actions/runs/41292056320), job `124805130699`: successful; 31 governance tests passed; actual log: `M20 PIT admission: NOT ATTESTED; orders: DISABLED; holdout: NOT AUTHORIZED`. The archived artifact SHA-256 `3a7ef97756b9a86ac7655fe7e0b02bd13ca00b0211b81920cf9149cfa540b4c1` is the *watchdog artifact ZIP digest*, **not** an original KRX/OpenDART source digest.
- [Chronology Actions #41091128151](https://github.com/kims34/openpilot-opkr/actions/runs/41091128151): auto-anchor failed on HTTP 404 at `/anchor/latest`, validation job skipped. This is not a PIT chronology attestation.
- The accessible connector checked these specific Actions IDs; it did not establish that no newer workflow run exists.

## Original source / historical PIT
- OpenDART 2022 first-filed document ZIP SHA-256 `56639d8f6ebbecf14cd8bc3179d75d01162e2cd7bbdf8f6a3c9479b44f5084bb` remains a **recorded** digest from PR #412; this audit has not independently downloaded and rehashed the original ZIP bytes. The 15 candidate operating-profit row shapes do not establish exact consolidated three-month operating profit, comparison period, initial publication time, amendment lineage, or historical ticker mapping.
- KRX #420 historical 2017–2022 scope: 1,565 source SHA-backed weekday pairs, 90 uncertain source-empty/calendar sessions, and 27 nonpositive OHLC cases. KRX specialist's wider 2015–2026 3,071 pairs/184 ambiguous days uses a different denominator. #422/#423 offline candidate comparators do not constitute original private-day-set or per-security tradability attestation.
- Railway `indexalert-pit-rebuild` last returned runtime log `2026-11-01T12:31:03.181219184Z` = 21:31:03 KST: `status=FAIL_CLOSED`, `error_reason_code=COMMON_OHLC_NONPOSITIVE`, `common_stock_rows=803`, `nonpositive_ohlc_rows=27`, `zero_volume_value_rows=27`, `session_manifest_sha256=null`, `source_failure_session=2026-09-28`. Independent source/chronology/model gates all false; `ordering=DISABLED`, real orders/funds/permissions unauthorized.
- Railway Kiwoom REAL read-only: deployment marked SUCCESS (2026-10-29), but environment health shows **0 running / 1 crashed** replicas; deploy log contains only container start, not a successful authentication or fill. Historical KRX worker latest deployment SUCCESS but no new deploy log proving original admission.
- Railway staged state inconsistent across read-only views: `get_staged_changes.staged=null` and `get_status.stagedChanges=null` while `pendingWork` retains zero-change staged patch `e113dacb-6705-4416-9997-dc694539d382`; do not commit or apply.

## Economic / policy gate
- Missing independent first-available timestamps, complete KRX session/security lifecycle, corporate actions, orderability, liquidity, spread/quotes, realistic fills and order constraints.
- Missing evidenced commission, fees, sale taxes, spread/slippage, impact, partial fills, rejected-order behavior and cash timing on an immutable trade ledger.
- Consequently after-tax **NetEV, PF, CAGR, MDD, ES95 and ES99 = NOT EVALUABLE**, not zero. No M20 profitability backtest was run; no invented metrics.
- Frozen/Holdout/Champion/Top3/preregistration remain unchanged; no Holdout tuning or Champion promotion.
- **Decision: M20 NO-GO, ORDERING=false / DISABLED** until independently verified original bytes, chronology, tradability and cost/tax admission.
