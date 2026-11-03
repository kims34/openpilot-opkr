# IndexAlert independent profitability admission audit — 2026-11-01 09:44 KST

**Scope:** evidence-only isolated documentation on Draft PR #414. No code, model, data, trading, credentials, Railway or GitHub Actions execution change. No M20 backtest. No Holdout access.

## Independent repository and PR snapshot
- Research `index-alert-research-v1`: `3b8b7830612a6284d7c7a60628cb527cb741627a` (fresh same-ref comparison).
- Development `index-alert-position-regen-fix-v1`: `1e6367d2863a86c3470da13d81a955d277eba485` (fresh same-ref comparison).
- KRX source audit `indexalert-krx-pit-source-audit-20261013`: `073d2d49e95f69fb10b943b93e51bb179fb3c698` (fresh same-ref comparison).
- Draft PR #414: head `7339fa46859b3cf9cf1e96007ffd204606a01f2c` before this isolated audit commit; #412 `bf3d9514a87c53b1775e22ec9ba7711f6cecc49f`. KRX Draft #420 `fab3cbbd63a951a4e081f9e7f08c1391ca308581`, #422 `c14857620973531013799e44625d43080904fd5f`, #423 `0e38004363cac9fc4475556b3a1c445de9af407f`. All open, Draft, unmerged when read.
- Watchdog Actions run #41248232339: job #124676072097 successful; governance log explicitly `M20 PIT admission: NOT ATTESTED; orders: DISABLED; holdout: NOT AUTHORIZED`. Offline tests are not original data admission.
- Chronology Anchor Actions #41091128151: auto-anchor failed, validation skipped; prior HTTP 404 remains unresolved.

## Original-source integrity and point-in-time admission
- Official OpenDART 2022 first-filed source-only Actions #38381866190, official job #115244084285: source ZIP integrity flag true; log records document SHA-256 `56639d8f6ebbecf14cd8bc3179d75d01162e2cd7bbdf8f6a3c9479b44f5084bb`, 1 SGML/HTML markup entry, 15 operating-row *candidates*, not facts.
- **Not independently rehashed:** raw official ZIP bytes were not available to this audit. A SHA logged by the originating job is not an independent second-party byte-for-byte digest.
- No verified original CFS Q3 3-month operating profit for 2022; no proven comparable 2021 Q3 period; no verified intraday first-publication instant, full correction lineage, historical corp-to-security mapping or full original historical universe. Official date-only receipt index is insufficient for an intraday PIT assertion.
- KRX private historical SHA receipts were not independently recomputed from raw volume bytes in this run. Historical 90 uncertain sessions and prospective 27 common-stock nonpositive OHLC cases remain quarantined. Offline comparator tests in KRX Draft PRs #420/#422/#423 do not authenticate actual source dates, stock tradability or historical PIT.
- No independent per-symbol market cap, suspension/limit-up-down/volume/entry-exit fill, auction/price-limit, taxes, commissions, spreads or slippage source admission. These are preconditions, not adjustable assumptions.

## Railway live read-only observations
- Production project `d1c1a050-b7d6-41ce-b300-13c20f82a20a`, environment `83d5840b-270e-4d3f-a941-a37fd4a55ff7` read-only inventory and health checked.
- PIT service `indexalert-pit-rebuild` last returned runtime log 2026-10-31 14:46:01 UTC (23:46:01 KST): `FAIL_CLOSED`, `COMMON_OHLC_NONPOSITIVE`, 27 rejected common-stock rows from failed source session 2026-09-28, all independent admission flags false, `ordering=DISABLED`, live orders and funds false.
- Kiwoom REAL readonly service has deployment status SUCCESS but health replica counts running 0, crashed 1, total 1; no new authenticated broker success shown. Deployment status must not be mistaken for running health.
- Inventory reports no staged patch, while health reports a staged pending patch with zero changes from 2026-10-29. This contradictory read-only metadata is not an authorization to apply/deploy or modify settings.
- KRX historical worker deployment SUCCESS is not an original raw-data independent hash or PIT admission.

## Economic gates and non-results
- M20 profitability execution: **NO-GO** until original-source independent SHA/PIT, complete 2021/2022 Q3 financial comparability, source correction lineage, stock-level tradability and executable net-cost/tax assumptions are independently admitted.
- NetEV, PF, CAGR, MDD, ES95 and ES99: **NOT ESTIMABLE / NOT APPROVED** on admissible trade-level original data; no point estimates, synthetic substitute, extrapolation or Holdout peek.
- Frozen / Holdout / Champion / Top3 preserved. `ORDERING=false` (runtime reports `DISABLED`). No trades, funds, permissions, deploy, PR merge, Champion promotion or workflow rerun.

## Evidence boundaries and follow-up
Independent verification still needs original raw ZIP and KRX receipt bytes for a second digest; official historical publication/correction lineage; verified quarter-specific numeric CFS facts; exact security-day exchange/calendar evidence; and independently reproducible fill/cost/tax models. Do not repeat specialist source capture or execute M20 until those admission gates are proven. This note records **no new original approval and no newly discovered major blocker**.

Sources: https://github.com/kims34/openpilot-opkr/pull/414 ; https://github.com/kims34/openpilot-opkr/pull/412 ; https://github.com/kims34/openpilot-opkr/pull/420 ; https://github.com/kims34/openpilot-opkr/pull/422 ; https://github.com/kims34/openpilot-opkr/pull/423 ; https://github.com/kims34/openpilot-opkr/actions/runs/41248232339 ; https://github.com/kims34/openpilot-opkr/actions/runs/38381866190 ; https://github.com/kims34/openpilot-opkr/actions/runs/41091128151 .
