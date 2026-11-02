# IndexAlert independent profitability gate delta — 2026-11-02 23:03 KST

**Decision: M20 NO-GO; ORDERING=DISABLED.** Documentation-only checkpoint from read-only connector evidence. No historical raw-data read, no M20/Holdout execution, no broker/order/funds/permissions/deployment/merge/Champion change.

## GitHub SHA and workflow evidence
- Research `index-alert-research-v1`: `3b8b7830612a6284d7c7a60628cb527cb741627a`.
- Development `index-alert-position-regen-fix-v1`: `1e6367d2863a86c3470da13d81a955d277eba485`.
- KRX specialist `indexalert-krx-pit-source-audit-20261013`: `073d2d49e95f69fb10b943b93e51bb179fb3c698`.
- Draft, open, unmerged: PR #414 head before this audit `7b5005c47c235b804e88678ab564a2e1ac52f125` (latest change was documentation-only), #412 `bf3d9514a87c53b1775e22ec9ba7711f6cecc49f`, KRX #420 `fab3cbbd63a951a4e081f9e7f08c1391ca308581`, #422 `c14857620973531013799e44625d43080904fd5f`, #423 `0e38004363cac9fc4475556b3a1c445de9af407f`.
- Repository-wide Actions first page at check: latest [read-only Watchdog #41407627828](https://github.com/kims34/openpilot-opkr/actions/runs/41407627828), 2026-11-02 07:38:39 UTC, success; actual job `125153144198` logs: fail-closed contract tests and research governance regression succeeded, but `M20 PIT admission: NOT ATTESTED; orders: DISABLED; holdout: NOT AUTHORIZED`. CI pass is not data admission.
- [Chronology Anchor #41091128151](https://github.com/kims34/openpilot-opkr/actions/runs/41091128151): actual job `124184971844` fails on public hash-only `/anchor/latest` HTTP 404; downstream chronology append and validation skipped.

## Original source and PIT checks
- [Official OpenDART provenance #38381866190](https://github.com/kims34/openpilot-opkr/actions/runs/38381866190), job `115244084285`: 2022 first-filed original ZIP recorded SHA-256 `56639d8f6ebbecf14cd8bc3179d75d01162e2cd7bbdf8f6a3c9479b44f5084bb`, ZIP integrity flag true, **not independently rehashed original bytes here**. Its exact CFS 3-month operating profit, initial public timestamp, amendment lineage and historical issuer/security mapping all remain unverified. [Original layout #38380988990](https://github.com/kims34/openpilot-opkr/actions/runs/38380988990) shows 1,570 tables, 15 operating-profit row-shapes (not financial facts), zero strict 2022 Q3 / prior-period exact window matches.
- Prior KRX 2017–2022 1,565 historical daily/master SHA pairs are storage-integrity receipts only, not PIT/tradability. Historical 90 uncertain sessions and prospective 27 nonpositive OHLC common-stock cases remain unresolved; KRX Draft comparators #420/#422/#423 do not grant historical admission.
- Railway production PIT service `indexalert-pit-rebuild` latest log 2026-11-02 14:01:18 UTC (23:01:18 KST): `COMMON_OHLC_NONPOSITIVE`, source/model/chronology independent approvals false, `session_manifest_sha256=null`, `ordering=DISABLED`, no live order authority. Source remains FAIL_CLOSED.
- Railway Kiwoom REAL read-only service: deployment `a77fb922-b679-4d88-92c4-03054ec579cd` reports SUCCESS but health shows 0 running / 1 crashed replica. This is not broker readiness.
- Railway `describe_environment` and `get_staged_changes` report staged=null; `environment_status.pendingWork` separately lists patch `e113dacb-6705-4416-9997-dc694539d382` as staged with empty changes. Treat discrepancy as unresolved read-only metadata; no patch applied.

## Economic admission and safety
- Independent original SHA byte equality, earliest publication instant/correction chronology, stock-level historical market calendar/corporate actions/tradability, immutable session quotes and order-lot constraints, fees/commissions/spread/slippage/impact/taxes are **not all attested**. Therefore after-tax NetEV, PF, CAGR, MDD, ES95 and ES99 cannot be estimated or independently validated; absence of estimates is not a zero-return result.
- Keep Frozen H5/M20, 20-session horizon, WF 504/126/126, purge20, CPCV, sealed Holdout, Champion, Top3/no rank-4 backfill, NO_TRADE and ORDERING=false. Do not execute M20 profitability before all source/PIT/chronology and full-cost preregistered approvals. No new approval or material blocker in this checkpoint. Other specialist workstreams unchanged.
