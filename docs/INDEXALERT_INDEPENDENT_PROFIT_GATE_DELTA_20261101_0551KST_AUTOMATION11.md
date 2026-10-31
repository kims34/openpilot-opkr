# IndexAlert independent profitability admission gate — 2026-11-01 05:51 KST

## Boundary
Independent, read-only GitHub/Railway review; only this isolated audit Markdown may be written to Draft PR #414's documentation branch. No source data, model, strategy, CI, broker, permission, environment, deployment or funding changes. No M20 profitability execution, Holdout read, PR merge, Champion/Top3 change or trading.

## Exact GitHub observations
- Research `index-alert-research-v1`: `3b8b7830612a6284d7c7a60628cb527cb741627a`.
- Development `index-alert-position-regen-fix-v1`: `1e6367d2863a86c3470da13d81a955d277eba485`.
- KRX source-audit `indexalert-krx-pit-source-audit-20261013`: `073d2d49e95f69fb10b943b93e51bb179fb3c698`.
- Draft open/unmerged: [#414](https://github.com/kims34/openpilot-opkr/pull/414) prewrite HEAD `25c0c2c2097b6907f59b4fa3ef20fd19e3ffa68d`; [#412](https://github.com/kims34/openpilot-opkr/pull/412) `bf3d9514a87c53b1775e22ec9ba7711f6cecc49f`; KRX [#420](https://github.com/kims34/openpilot-opkr/pull/420) `fab3cbbd63a951a4e081f9e7f08c1391ca308581`, [#422](https://github.com/kims34/openpilot-opkr/pull/422) `c14857620973531013799e44625d43080904fd5f`, [#423](https://github.com/kims34/openpilot-opkr/pull/423) `0e38004363cac9fc4475556b3a1c445de9af407f`.
- Latest repo Actions listing: [read-only watchdog #41229825403](https://github.com/kims34/openpilot-opkr/actions/runs/41229825403) completed 2026-10-31 18:31 UTC; actual job `124621536897` ran 4 watchdog and 31 governance tests successfully, and explicitly printed `M20 PIT admission: NOT ATTESTED; orders: DISABLED; holdout: NOT AUTHORIZED`. A green workflow is not PIT or profitability attestation.
- [Chronology Anchor #41091128151](https://github.com/kims34/openpilot-opkr/actions/runs/41091128151) job `124184971844` failed fetching public hash-only `/anchor/latest` (HTTP 404); downstream validation job `124184974604` skipped. No fresh immutable chronology admission.

## Original bytes, PIT and tradability
- [2022 first original OpenDART #38380988990](https://github.com/kims34/openpilot-opkr/actions/runs/38380988990) source-only job `115241142185` succeeded its diagnostic assertions, not financial-value admission. Recorded 2022 document SHA-256 `56639d8f6ebbecf14cd8bc3179d75d01162e2cd7bbdf8f6a3c9479b44f5084bb` is a prior log receipt, **not independently rehashed original ZIP bytes** in this run. Historical 2021 recorded SHA-256 `8728c0a3c12761ca19e9c6455bea8f1bed0e4c1ebc2e21dc263c373a82a2b625` likewise not rehashed in this run.
- The 2022 document layout contains operating-profit-shaped candidates (15), but no verified standalone consolidated 3-month Q3 operating-profit value, matched prior-year quarter, first public timestamp, full correction lineage or security-level historical identity. Original six-slot coverage and first-filing PIT not admitted.
- Private KRX dual-source integrity does not independently resolve 90 historical source-empty/calendar sessions. KRX #420/#422/#423 are isolated offline/synthetic and candidate comparators, not certified exact historical exchange/security tradability.
- The separate prospective 2026-09-28 OHLC failure has 27 nonpositive common-stock rows. Do not conflate the 90 historical sessions and 27 prospective rows.

## Railway read-only evidence
- Project IndexAlert, production. `indexalert-pit-rebuild` last returned runtime line 2026-10-31 14:46:01 UTC (23:46:01 KST): `status=FAIL_CLOSED`, `error_reason_code=COMMON_OHLC_NONPOSITIVE`, `source_failure_session=2026-09-28`, `nonpositive_ohlc_rows=27`, `independent_source_admission_verified=false`, `independent_chronology_admission_verified=false`, `independent_model_admission_verified=false`, `ordering=DISABLED`, orders/funds/permissions false. No later runtime line returned by this read.
- `indexalert-kiwoom-real-readonly` latest deployment shows SUCCESS but environment status reports 0 running / 1 crashed replica; successful fresh real-broker authentication is not evidenced.
- `get_staged_changes` and `describe_environment` return `staged=null` and no changed resources, whereas `environment_status` lists old `patch:e113dacb-6705-4416-9997-dc694539d382` as staged with empty changes (since 2026-10-29). Treat as an unresolved read-model inconsistency, not evidence of a live change. No deployment, patch acceptance or retries attempted.

## Independent economic disposition
No independently admitted point-in-time original fundamental/market panel, security-by-session tradability, corporate-action chronology, executable fills, fee/slippage/market-impact assumptions or applicable transaction-tax basis. Therefore **after-cost/after-tax NetEV, PF, CAGR, MDD, ES95 and ES99 cannot be computed or claimed**. M20 profitability run **NO-GO** until separate source/PIT/tradability/cost/tax approvals. Preserve Frozen/Holdout/Champion/Top3, `ORDERING=false`, no live trading, capital movement, permission changes, deployment, PR merge or Champion promotion. No material newly verified admission or new major blocker relative to the previous audit; continue fail-closed and avoid overlap with KRX/OpenDART specialist work.
