# IndexAlert independent profitability gate — 2026-11-02 13:48 KST

Documentation-only independent read of GitHub and Railway. No M20 backtest, model or code change, source capture, production write, order, capital, permission change, deployment, PR merge, Holdout read, or Champion promotion. This note is on the existing isolated Draft PR #414 branch only, without altering other specialists' branches.

## Exact current evidence (read-only)
- Research branch `index-alert-research-v1` HEAD `3b8b7830612a6284d7c7a60628cb527cb741627a`; development `index-alert-position-regen-fix-v1` HEAD `1e6367d2863a86c3470da13d81a955d277eba485`; KRX specialist `indexalert-krx-pit-source-audit-20261013` HEAD `073d2d49e95f69fb10b943b93e51bb179fb3c698`. Direct GitHub branch GET, unchanged.
- PR #414, #412, KRX #420/#422/#423 all open Draft, unmerged. PR #414 HEAD before this note: `6432ff4719b28c83db0ec066c726288c92c55fce`. KRX synthetic CI cannot certify original historic tradability.
- Repository-wide Actions first page (20 latest) has latest run `41368406818` (2026-11-02 00:40:24Z), completed success; job `125033414398` logs: 4/4 watchdog synthetic tests and 31/31 research-governance tests pass; explicit `M20 PIT admission: NOT ATTESTED; orders: DISABLED; holdout: NOT AUTHORIZED`. Success is not source or economics admission.
- Chronology run `41091128151` job `124184971844` failed `HTTP Error 404: Not Found` at `/anchor/latest`; job `124184974604` validation skipped. No chronology admission.
- Official first-filed 2022 OpenDART run `38381866190` job `115244084285` re-read directly: reported original document ZIP SHA-256 `56639d8f6ebbecf14cd8bc3179d75d01162e2cd7bbdf8f6a3c9479b44f5084bb`, original document ZIP integrity true, 15 operating-row *shape candidates*, first-filing provenance only. Exact consolidated three-month Q3 operating-profit semantic binding, first-publication instant, full corrections and historic corp/security mapping are not verified. The job's report is NOT independent original-byte rehash in this audit. Workflow artifact SHA is not source ZIP SHA. Later correction census in PR #412 is source-only and does not authorize PIT.
- Historical KRX prior private original daily/master storage audit: 1,565 pairs with SHA integrity reported, 90 uncertain 2017–2022 weekday sessions; prospective 2026-09-28 common-stock OHLC nonpositive 27 of 803, not admitted. Neither private raw bytes nor actual market-calendar and security/day source evidence independently rehashed/reconciled in this audit.
- Railway project IndexAlert production `83d5840b-270e-4d3f-a941-a37fd4a55ff7`: PIT runtime most recent returned log `2026-11-01T14:46:22Z` says `FAIL_CLOSED`, `COMMON_OHLC_NONPOSITIVE`, `fresh_alpha_observation_admitted=false`, `independent_source_admission_verified=false`, `ordering=DISABLED`, `real_orders_authorized=false`; session field 2026-11-01 and failure-source session 2026-09-28. No newer runtime log returned.
- Railway Kiwoom REAL read-only service latest deployment reports SUCCESS, but environment-status reports 0 running / 1 crashed replica; a deployment success label is not healthy broker connectivity. `describe_environment` and `get_staged_changes` show staged=null, while `environment_status.pendingWork` still reports old staged patch `e113dacb-6705-4416-9997-dc694539d382` with empty changes. Treat as inconsistent read surfaces, not a reason to apply or alter pending work. No deploy or configuration action taken.

## Admission and economics
- **M20 NO-GO**. First-filed source SHA recorded by CI is not a new independent source-byte attestation. Original exact Q3 and comparable Q-4 financial semantics, correction/publication-time PIT, issuer/universe survivorship, 2017–2022 calendar/stock-level tradability, execution path and slippage, fees and taxes all require independent source admission.
- No independently admitted executable transaction path or complete cost/tax inputs, so net EV, profit factor, CAGR, maximum drawdown, ES95 and ES99 are **not estimable**; no fabricated metrics or performance backtest.
- Frozen, sealed Holdout, Champion and Top3 are unchanged. `ORDERING=false` / runtime `DISABLED`; no orders, funds, permissions, deployment, merge, or promotion.
- Next independent prerequisite is actual source-byte SHA + source-vintage/first-available-time verification, exact financial period and amendment mapping, official historic calendar/security tradability reconciliation, then preregistered cost/tax execution model and immutable PIT panel. Require separate explicit admission before M20.

Evidence:
- https://github.com/kims34/openpilot-opkr/pull/414
- https://github.com/kims34/openpilot-opkr/pull/412
- https://github.com/kims34/openpilot-opkr/pull/420
- https://github.com/kims34/openpilot-opkr/pull/422
- https://github.com/kims34/openpilot-opkr/pull/423
- https://github.com/kims34/openpilot-opkr/actions/runs/41368406818
- https://github.com/kims34/openpilot-opkr/actions/runs/41091128151
- https://github.com/kims34/openpilot-opkr/actions/runs/38381866190
