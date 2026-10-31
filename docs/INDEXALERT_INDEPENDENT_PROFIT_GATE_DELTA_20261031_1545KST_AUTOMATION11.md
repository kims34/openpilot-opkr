# Independent profitability gate — 2026-10-31 15:45 KST (documentation only)

## Scope / authority
Read-only GitHub research/development/KRX branch, PR #414/#412 and specialist PR #420/#422/#423, Actions, and Railway production service logs. This is a **no-admission** checkpoint; no replay, provider acquisition, broker operations, environment changes, or independent original raw-byte rehash performed. Do not conflate synthetic CI with source/PIT approval.

## Immutable references observed
- Research `index-alert-research-v1`: `3b8b7830612a6284d7c7a60628cb527cb741627a`.
- Development `index-alert-position-regen-fix-v1`: `1e6367d2863a86c3470da13d81a955d277eba485`.
- KRX specialist `indexalert-krx-pit-source-audit-20261013`: `073d2d49e95f69fb10b943b93e51bb179fb3c698`.
- Draft PR #414 head `e372604fe586dcf23e2439cab28628b05f817774`; Draft PR #412 head `bf3d9514a87c53b1775e22ec9ba7711f6cecc49f`. Draft KRX #420/#422/#423 unmerged. Source: https://github.com/kims34/openpilot-opkr/pulls

## Directly checked latest CI
- Read-only Watchdog https://github.com/kims34/openpilot-opkr/actions/runs/41151825793 succeeded 2026-10-31 09:45 KST; job 124389856589: 4 watchdog tests + 31 governance tests pass; explicit `M20 PIT admission: NOT ATTESTED; orders: DISABLED; holdout: NOT AUTHORIZED`.
- Chronology Anchor https://github.com/kims34/openpilot-opkr/actions/runs/41091128151 failed 2026-10-31 02:13 KST on `/anchor/latest` HTTP 404; follow-on chronology validation skipped. This is an existing unresolved blocker, not newly detected.

## Original SHA / PIT / tradeability
- PR #412 documents 2022 first-filed OpenDART original ZIP SHA-256 `56639d8f6ebbecf14cd8bc3179d75d01162e2cd7bbdf8f6a3c9479b44f5084bb` from official source-only Actions https://github.com/kims34/openpilot-opkr/actions/runs/38392847048. It is a recorded digest, **not** an independent raw ZIP byte rehash in this checkpoint. 1,570 tables, 15 operating-row shapes, zero strict original 3-month CFS operating profit matches in prior official evidence. First disclosure intraday timestamp, full correction lineage, 2021/2022 original numeric quarter, security-level PIT mapping remain unapproved.
- Historical KRX 2017–2022 private SHA integrity scope includes 1,565 weekday pairs; 90 historical calendar/source-gap sessions not independently resolved. Prospective 2026-09-28 failure has 27 nonpositive-OHLC rows among 803 common-stock rows; **distinct time horizon** from historical 90.
- KRX PR #422/#423 exact-calendar candidate checks remain synthetic / no authorized real private re-run. Original day/security-level tradeability, execution timestamps, slippage/fees/impact/taxes, delistings/corporate actions are not admitted. No returns or P&L may be inferred from these audits.

## Railway (read-only)
- Project IndexAlert / production `83d5840b-270e-4d3f-a941-a37fd4a55ff7`.
- `indexalert-pit-rebuild` service logs last returned 2026-10-30 14:46:37 UTC (23:46:37 KST): `FAIL_CLOSED`, `COMMON_OHLC_NONPOSITIVE`, 27/803, `independent_source_admission_verified=false`, `ordering=DISABLED`, `real_orders_authorized=false`. No later event in returned logs.
- `indexalert-kiwoom-real-readonly` latest returned runtime event 2026-10-29 06:22 UTC: `DETAIL_CODE=8050`, `TOKEN_OK=false`, `WS_LOGIN_OK=false`, `TYPE00_REG_ACK_OK=false`, `ORDERING=DISABLED`. Deployment SUCCESS alone is not broker authentication.
- Railway `get_status` returns replica counts null and `stagedChanges=null`, while `pendingWork` contains older staged patch `e113dacb-6705-4416-9997-dc694539d382` with empty `changes`; do not infer no pending changes or a new deploy. No Railway writes performed.

## Economic admission verdict
- Original independent SHA / semantic first-filing numeric PIT: **NOT ADMITTED**.
- Historical day/security tradeability: **NOT ADMITTED**.
- Auditable fill/fees/slippage/impact/tax inputs: **NOT ADMITTED**.
- Therefore net-of-tax NetEV, PF, CAGR, MDD, ES95, ES99: **NOT ESTIMABLE**; no placeholder or synthetic performance promoted to observed profitability.
- M20 performance execution: **NO-GO**. Preserve Frozen, sealed Holdout, Champion, Top3, preregistration, no-order guard, `ORDERING=false` / runtime `DISABLED`. No trading, capital, permissions, deployment, PR merge, Champion promotion, or backtest replay.
- Re-evaluate only on independent source bytes/hash, point-in-time first-filed semantic earnings and complete amendment timeline, KRX original calendar/security tradability evidence, and independently verifiable cost/tax/fill assumptions. Other workstreams retain ownership of their isolated tasks.
