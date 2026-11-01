# IndexAlert independent profitability gate — 2026-11-01 18:45 KST

Documentation-only, read-only verification. This is NOT a PIT/source/tradability approval, backtest result, or deployment authorization.

## Source refs and scope
- Research `index-alert-research-v1`: `3b8b7830612a6284d7c7a60628cb527cb741627a`.
- Development `index-alert-position-regen-fix-v1`: `1e6367d2863a86c3470da13d81a955d277eba485`.
- KRX specialist `indexalert-krx-pit-source-audit-20261013`: `073d2d49e95f69fb10b943b93e51bb179fb3c698`.
- Draft/unmerged PRs: #414 head `86af551a02329fbd8c2fd30c1572cf49a7a3af98`; #412 `bf3d9514a87c53b1775e22ec9ba7711f6cecc49f`; KRX #420/#422/#423 draft/unmerged.
- GitHub Actions [read-only watchdog #41292056320](https://github.com/kims34/openpilot-opkr/actions/runs/41292056320), 2026-11-01 18:11–18:12 KST: success. Job log explicitly reports `M20 PIT admission: NOT ATTESTED; orders: DISABLED; holdout: NOT AUTHORIZED`. Unit tests for watchdog and research governance passed; this is NOT source admission.
- GitHub Actions [chronology #41091128151](https://github.com/kims34/openpilot-opkr/actions/runs/41091128151): failed at prospective anchor HTTP fetch, 404; downstream chronology validation skipped.
- Railway production `indexalert-pit-rebuild` deploy log last inspected `2026-11-01T09:45:31.749643520Z` (18:45:31 KST): `FAIL_CLOSED`, `COMMON_OHLC_NONPOSITIVE`, 27 nonpositive OHLC rows among 803 common stock rows, `session_manifest_sha256=null`, `independent_source_admission_verified=false`, `independent_chronology_admission_verified=false`, `independent_model_admission_verified=false`, `ordering=DISABLED`, no order or funds authority. The prospective failure receipt points to 2026-09-28.
- Railway KRX historical worker: latest deployment SUCCESS, but no new source log entries were returned in this inspection; no new original SHA/PIT admission inferred.
- Railway Kiwoom REAL read-only: deployment SUCCESS status with `running=0, crashed=1` replicas; no successful broker authentication attested. The environment_status 'online' label must not be treated as actual healthy running replica evidence.
- Railway staged change discrepancy persists: `describe_environment` and `get_staged_changes` report no staged patch; `environment_status` reports staged patch `e113dacb-6705-4416-9997-dc694539d382` with zero changes. Do not apply/accept.

## Independent admission assessment
- OpenDART 2022 first-submission recorded ZIP SHA-256: `56639d8f6ebbecf14cd8bc3179d75d01162e2cd7bbdf8f6a3c9479b44f5084bb` (recorded evidence only; independent raw original ZIP byte rehash NOT completed here). 15 operating-row shape candidates do not prove unique consolidated three-month operating profit. First public timestamps, amendment lineage, comparable prior periods and historical symbol mapping remain unapproved.
- KRX historical: 90 uncertain sessions and separate 27 bad OHLC observations unresolved. Exact calendar, daily master/source SHA receipts, security status and orderable volume/limit constraints require independent PIT/tradability approval. Do not confuse a SHA receipt with authoritative content admission.
- Economic gate: commissions, taxes, slippage, partial fills, market-impact, liquidity/limits, cash timing and executable trade prices are not independently proven. Thus after-cost NetEV, PF, CAGR, MDD, ES95 and ES99 are **NOT EVALUABLE**, not zero, and no M20 profitability run is authorized.
- Preserve immutable Frozen/Holdout/Champion/Top3 and preregistration; no tuning, leakage, promotion or model-selection using Holdout.
- **Final gate: M20 NO-GO; ORDERING=false/DISABLED; no live orders, funding, credentials/permissions, deployments, PR merges or Champion promotion.**
- Avoid duplicating KRX source-capture, OpenDART reconstruction or isolated optimization owners; this note records independent admission observations only.
