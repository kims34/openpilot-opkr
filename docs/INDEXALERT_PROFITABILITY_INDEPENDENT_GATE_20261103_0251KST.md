# IndexAlert — independent profitability admission audit (2026-11-03 02:51 KST)

**Decision: M20 NO-GO.** This document records only fresh read-only checks and a single isolated documentation addition. No M20 performance run, Holdout read, synthetic-to-live promotion, source capture, order, funding, permissions, deployment, PR merge, Champion/Top3 change or other specialist work. Frozen/WF504-126-126/purge20/Top3/NO_TRADE remain unchanged; `ORDERING=false` (observed runtime `ordering=DISABLED`).

## GitHub exact refs and safety CI

Direct branch REST reads:
- Research `index-alert-research-v1`: `3b8b7830612a6284d7c7a60628cb527cb741627a`.
- Development `index-alert-position-regen-fix-v1`: `1e6367d2863a86c3470da13d81a955d277eba485`.
- KRX specialist `indexalert-krx-pit-source-audit-20261013`: `073d2d49e95f69fb10b943b93e51bb179fb3c698`.

Direct PR metadata: #414 `9cc6277d4d33a2c22a3fd8bc197f0b759a73b8c0`, #412 `bf3d9514a87c53b1775e22ec9ba7711f6cecc49f`, KRX #420 `fab3cbbd63a951a4e081f9e7f08c1391ca308581`, #422 `c14857620973531013799e44625d43080904fd5f`, #423 `0e38004363cac9fc4475556b3a1c445de9af407f`: all **open, draft, unmerged**. Do not infer source admission from an unchanged HEAD or a passing CI.

Repository-wide Actions list (4,637 total at query time) newest: [read-only Watchdog #41407627828](https://github.com/kims34/openpilot-opkr/actions/runs/41407627828), 2026-11-02 07:38 UTC, SUCCESS. Direct job `125153144198` log: 4 safety tests + 31 governance tests passed; explicit `M20 PIT admission: NOT ATTESTED; orders: DISABLED; holdout: NOT AUTHORIZED`. [Chronology Anchor #41091128151](https://github.com/kims34/openpilot-opkr/actions/runs/41091128151): public hash-only `/anchor/latest` returned HTTP 404, append and independent validation skipped. No retry or alternative endpoint used.

## Independent original-source / PIT / tradability adjudication

[Official OpenDART source-only run #38380988990](https://github.com/kims34/openpilot-opkr/actions/runs/38380988990), direct job `115241142185`: 2022 first-filed ZIP received and bounded CRC read passed; one non-XML SGML/HTML entry; 1,570 tables; 15 operating-profit-shaped rows, 12 with four numeric peers; **zero exact 2022/2021 Q3 window row matches, zero verified consolidated three-month operating-profit facts**. Flags `original_q3_cfs_three_month_profit_bound=false`, `historical_publication_instant_pit_verified=false`, `historical_security_corp_mapping_verified=false`, `historical_correction_lineage_complete=false`. The earlier recorded 2022 original ZIP SHA-256 `56639d8f6ebbecf14cd8bc3179d75d01162e2cd7bbdf8f6a3c9479b44f5084bb` was **not independently recomputed from source ZIP bytes in this check**. The flags-only artifact ZIP digest is not the original-source hash.

Existing 2017–2022 KRX private source-pair SHA integrity report 1,565 pairs: **prior limited storage-integrity evidence, not independently rehashed now and not PIT/tradability approval**. KRX specialist PR #420 reports 90 unresolved calendar/source-gap sessions and 27 nonpositive OHLC cases; dependent #422/#423 remain draft and cannot certify source-open, halts, listing/delisting, corporate actions, point-in-time market caps or executable fills. No cherry-picking/quarantined-row deletion to manufacture PASS.

## Direct Railway production evidence

Project `d1c1a050-b7d6-41ce-b300-13c20f82a20a`, production environment `83d5840b-270e-4d3f-a941-a37fd4a55ff7`. PIT service latest deployment `8b354fc1-cfb2-4ef0-863e-67f7f5dda2b5` is SUCCESS and health reports 1/1 running. Latest returned PIT deploy log `2026-11-02T14:46:22.403874064Z` (23:46:22 KST): `status=FAIL_CLOSED`, `COMMON_OHLC_NONPOSITIVE`, `source_failure_session=2026-09-28`, 27 nonpositive/803 common-stock OHLC rows, `session_manifest_sha256=null`, independent source/model/chronology admissions false, `ordering=DISABLED`, order/funds/permission authorization false. No newer PIT log was returned; this is a visibility limit, not proof of repair or outage.

Railway historical worker deployment `16c93d7c-7cd0-4d84-a327-298d2805376c` is marked SUCCESS, with no new deploy-log evidence in this read. `indexalert-kiwoom-real-readonly` is displayed online/SUCCESS while environment health reports 0 running / 1 crashed replica: deployment label does not establish broker readiness. Separate `indexalert-kiwoom-real-readonly-run` has 0 running / 0 crashed / 1 configured; no live brokerage proof. `describe_environment` reports staged=null, but `environment_status` reports a staged patch `e113dacb-6705-4416-9997-dc694539d382` with empty changes: cross-view discrepancy; no patch was applied.

## Economic sufficiency gate — no performance calculation authorized

- **Original source SHA:** recorded official log receipt only; independent original byte rehash absent.
- **PIT:** exact first-filed three-month CFS value, first publication timestamp, correction lineage, historical security/corp mapping absent.
- **Tradability:** official historical session/stock states, liquidity, lot size, fill timing, spread/impact/slippage not independently approved.
- **Costs and tax:** timestamped fee schedule, exchange costs, commissions, sell-side transaction tax, corporate-action handling, capacity and 2x-cost stress not independently certified for executable trades.
- **NetEV / PF / CAGR / MDD / ES95 / ES99:** **NOT EVALUABLE**. Do not impute zeros, invent sample sizes, backtest, reuse Holdout, or claim economic alpha from safety CI.
- **Gate:** M20 NO-GO, Frozen/Holdout/Champion/Top3 unchanged, `ORDERING=false`; real orders/funds/permissions/deployment/merge/promotion prohibited.

**Next non-overlapping evidence dependencies:** source specialist must independently bind original filing/three-month CFS and publication/correction/issuer PIT; KRX specialist must resolve official calendar/stock-day tradability and executable fee/tax/fill receipts. Until independently approved, no M20 profitability execution.
