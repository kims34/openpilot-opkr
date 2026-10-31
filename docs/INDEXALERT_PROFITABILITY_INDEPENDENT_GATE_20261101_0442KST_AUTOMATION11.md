# IndexAlert independent profitability gate — 2026-11-01 04:42 KST

Status: **NO-GO**. Read-only verification; isolated audit note only. No M20 backtest, no Holdout, no Champion/Top3 changes, no ordering, deployment, permissions, funds, trades, PR merge, or research/development code modifications.

## Independent read-only observations
- Research branch `index-alert-research-v1`: `3b8b7830612a6284d7c7a60628cb527cb741627a`.
- Development branch `index-alert-position-regen-fix-v1`: `1e6367d2863a86c3470da13d81a955d277eba485`.
- KRX PIT source audit branch `indexalert-krx-pit-source-audit-20261013`: `073d2d49e95f69fb10b943b93e51bb179fb3c698`.
- Draft PR #414: head `aeae96a33b721a8e4d71bbcef0c6d95558150a26`, open, unmerged. Draft PR #412: head `bf3d9514a87c53b1775e22ec9ba7711f6cecc49f`, open, unmerged. KRX Draft PRs #420/#422/#423 remain open/unmerged.
- Latest listed read-only watchdog Actions #41229825403, 2026-10-31 18:31 UTC: success. Its actual job logs: governance tests passed; explicit `M20 PIT admission: NOT ATTESTED; orders: DISABLED; holdout: NOT AUTHORIZED`. This is a governance check, **not** market-data admission.
- Chronology Anchor Actions #41091128151: fetch of `/anchor/latest` failed HTTP 404; validation skipped. No immutable prospective chronology admission.
- OpenDART official original 2022 source-only Actions #38380988990: ZIP received; CRC and bounded read complete; 1,570 tables, 15 operating-profit row shapes, zero exact 2021/2022 Q3 window matches. First-edition standalone 3-month CFS profit and comparison facts not verified. Source-only flags are not financial observations.
- Original ZIP bytes are not available in this independent read-only audit. Prior reported SHA-256 digests are **not independently rehashed**; no source-byte attestation, original-publication timestamp, restatement lineage, or historical security-to-corporation PIT mapping approval. Do not promote a logged digest or uploaded artifact ZIP digest to source SHA proof.
- KRX historical source uncertainty: 90 market-session classifications unresolved. Prospective KRX nonpositive common-stock OHLC: 27 rows among 803, associated with 2026-09-28 source failure. These are separate populations and must not be combined as 117 equivalent sessions.
- Railway production `indexalert-pit-rebuild`: last returned runtime entry 2026-10-31 14:46:01 UTC; `FAIL_CLOSED`, `COMMON_OHLC_NONPOSITIVE`, independent source/model/chronology admission false, session manifest SHA null, `ordering=DISABLED`, orders/funds/permissions false. No fresh admitted alpha observation.
- Railway Kiwoom REAL read-only: health reports 0 running / 1 crashed replicas despite deployment SUCCESS; no new broker authentication success proof.
- Railway staging query discrepancy: `describe_environment` and `get_staged_changes` show null/no patch; `environment_status` reports historical pending patch `e113dacb-6705-4416-9997-dc694539d382`. No commit or deployment attempted; discrepancy is not evidence of live changes.

## Profitability admission decision
- SHA original-byte provenance: **BLOCKED**; PIT publication/edition/security mapping: **BLOCKED**; exact session calendar and tradability: **BLOCKED**.
- Fees, spread, slippage, taxes, partial fills and realistic executable turnover: **NOT APPROVED**. No validated net-trade ledger exists.
- NetEV, PF, CAGR, MDD, ES95, ES99 (after taxes/costs): **NOT COMPUTABLE / NOT APPROVED**. Do not report synthetic or gross-only numbers as realized or PIT backtest results.
- M20 execution: **FORBIDDEN UNTIL ORIGINAL DATA/PIT ADMISSION**. Frozen/Holdout/Champion/Top3 unchanged. ORDERING=false.
- Next permitted action: independent first-filing ZIP-byte hash and PIT lineage verification by the authorized source owner, KRX calendar/tradability evidence, then independently verified fee/tax/execution model. Do not overlap specialist workstreams or bypass blocked permissions.

Evidence URLs:
- https://github.com/kims34/openpilot-opkr/pull/414
- https://github.com/kims34/openpilot-opkr/pull/412
- https://github.com/kims34/openpilot-opkr/pull/420
- https://github.com/kims34/openpilot-opkr/pull/422
- https://github.com/kims34/openpilot-opkr/pull/423
- https://github.com/kims34/openpilot-opkr/actions/runs/41229825403
- https://github.com/kims34/openpilot-opkr/actions/runs/41091128151
- https://github.com/kims34/openpilot-opkr/actions/runs/38380988990
