# IndexAlert independent profitability evidence gate — 2026-11-01 22:47 KST

Scope: isolated **documentation-only** read-only audit. No historical source replay, M20 profitability backtest, trading, deployment, PR merge, account/funds/permission changes, Champion/Top3 changes, or Holdout use. This record is **not** a PIT admission or authorization.

## Immutable refs and review state
- Research `index-alert-research-v1`: `3b8b7830612a6284d7c7a60628cb527cb741627a` (GitHub branch API).
- Development `index-alert-position-regen-fix-v1`: `1e6367d2863a86c3470da13d81a955d277eba485`.
- KRX source audit `indexalert-krx-pit-source-audit-20261013`: `073d2d49e95f69fb10b943b93e51bb179fb3c698`.
- Draft PR #414 head before this doc-only audit `437ea3982642ba925c0b917c9a9bdcaa9dcb050a`. PR #412, #420, #422, #423 all open, draft, unmerged at read time. This write, if accepted, advances only the isolated PR #414 documentation branch.
- API: https://api.github.com/repos/kims34/openpilot-opkr/actions/runs?per_page=15 — newest returned workflow run was #41292056320, 2026-11-01 09:11:52 UTC, success; actual job #124805130699 reports 31 governance tests passed, `M20 PIT admission: NOT ATTESTED; orders: DISABLED; holdout: NOT AUTHORIZED`. The run is on `HKG_community`, **not** a substitute for tests on every research/PR branch.
- Chronology anchor #41091128151 (2026-10-30 16:34 UTC) failed source fetch HTTP 404; validation job skipped. No independent chronology admission.

## Official source/PIT provenance — NOT ADMITTED
- OpenDART PR #412's source-only evidence records 2022 first-filed Q3 ZIP SHA-256 `56639d8f6ebbecf14cd8bc3179d75d01162e2cd7bbdf8f6a3c9479b44f5084bb`, 15 operating-profit-label candidates, **zero** strictly bound quarterly 3-month consolidated operating-profit facts. The 2021 first-filed Q3 ZIP `8728c0a3c12761ca19e9c6455bea8f1bed0e4c1ebc2e21dc263c373a82a2b625` was independently re-read in prior source-only CI, but does **not** validate 2022 report's 2021 comparative account. These are recorded provenance hashes, **not independently rehashed raw ZIP bytes in this audit**.
- Required but missing: raw first-vintage 2022/2021 comparable CFS three-month operating profit with exact period, unit, scale, sign and account; first public availability timestamp; correction lineage; point-in-time issuer/security mapping. No M20 feature authorization.
- KRX PR #420 records 1,565 weekday daily/master SHA-pair receipts, 90 historical uncertain session classifications, 27 prospective nonpositive OHLC common-stock rows. PR #422/#423 are offline candidate calendar comparators; passing synthetic tests or count equality does **not** resolve private exact-day/calendar/source or stock-level tradability PIT. No live private 2021/2022 exact-set audit was performed here.

## Railway operational observations (read-only)
- Production `indexalert-pit-rebuild` latest returned event: 2026-11-01 13:46:07 UTC (22:46:07 KST). `FAIL_CLOSED`, `COMMON_OHLC_NONPOSITIVE`, `ordering=DISABLED`, `nonpositive_ohlc_rows=27`, `independent_source_admission_verified=false`, `independent_chronology_admission_verified=false`, `real_orders_authorized=false`, `funds_movement_authorized=false`.
- `indexalert-kiwoom-real-readonly` latest deployment marked SUCCESS but environment status showed 0 running / 1 crashed replicas. This is **not** proof of successful broker auth/WS or readiness.
- Environment status showed a pending staged patch `e113dacb-6705-4416-9997-dc694539d382` while the separate staged-changes endpoint returned `staged=null`; unresolved read-view discrepancy. No changes applied.

## Economic admission gates
- Execution/tradability: original security/day status, exchange calendar, price limits, suspension, corporate actions, fill assumptions and available liquidity are not independently established.
- Fees, taxes, spreads, market impact and slippage need timestamped, venue/period-specific assumptions, order sizing, sensitivity bounds and conservative fill accounting; not admitted.
- Net EV, PF, CAGR, MDD, ES95 and ES99 (including post-cost/post-tax values) are **NOT ESTIMABLE** from approved PIT/tradability evidence. No fabricated point estimates, no M20 profitability execution.
- Frozen/Holdout/Champion/Top3 remain unchanged. `ORDERING=false` / `DISABLED`. **M20 profitability GO/NO-GO = NO-GO**. Continue source-provenance and independent PIT gate only, avoiding KRX and OpenDART specialists' execution scopes.

Evidence links: https://github.com/kims34/openpilot-opkr/pull/414 ; https://github.com/kims34/openpilot-opkr/pull/412 ; https://github.com/kims34/openpilot-opkr/pull/420 ; https://github.com/kims34/openpilot-opkr/pull/422 ; https://github.com/kims34/openpilot-opkr/pull/423 ; https://github.com/kims34/openpilot-opkr/actions/runs/41292056320 ; https://github.com/kims34/openpilot-opkr/actions/runs/41091128151 .
