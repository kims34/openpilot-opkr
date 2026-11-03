# IndexAlert — independent profitability admission gate, 2026-11-03 01:44 KST

**Scope:** Isolated, documentation-only audit; no other specialist's source/code/CI changes. All source, PR, Actions and Railway checks were read-only. This is **not** approval of M20, live execution, orders, funding, deployments, permissions, PR merge or Champion promotion. Frozen/Holdout/Champion/Top3 unchanged; `ORDERING=false` (runtime `ordering=DISABLED`).

## Direct GitHub branch-ref and PR verification

Repository: `kims34/openpilot-opkr`.

| Branch (direct GitHub branch API) | Exact HEAD |
|---|---|
| `index-alert-research-v1` | `3b8b7830612a6284d7c7a60628cb527cb741627a` |
| `index-alert-position-regen-fix-v1` | `1e6367d2863a86c3470da13d81a955d277eba485` |
| `indexalert-krx-pit-source-audit-20261013` | `073d2d49e95f69fb10b943b93e51bb179fb3c698` |

PR #412 `bf3d9514a87c53b1775e22ec9ba7711f6cecc49f`, #414 **pre-audit** `009a1b5439de779100c71dfad52bab202ba80c69`, KRX #420 `fab3cbbd63a951a4e081f9e7f08c1391ca308581`, #422 `c14857620973531013799e44625d43080904fd5f`, #423 `0e38004363cac9fc4475556b3a1c445de9af407f` are **OPEN / DRAFT / NOT MERGED**. PR #414 prior HEAD commit changed only `docs/INDEXALERT_INDEPENDENT_PROFIT_RUNTIME_AUDIT_20261103_0124KST.md`; avoid edits to this and specialist files.

Latest repository-wide GitHub Actions list (15 most recent, 4,637 total): [read-only Watchdog #41407627828](https://github.com/kims34/openpilot-opkr/actions/runs/41407627828), created `2026-11-02T07:38:39Z`, completed SUCCESS. Direct job `125153144198` log: 4 safety-contract tests + 31 offline research-governance tests PASS, **`M20 PIT admission: NOT ATTESTED; orders: DISABLED; holdout: NOT AUTHORIZED`**. CI passing means safety guard behavior, not market-data PIT or economic edge.

[Chronology Anchor #41091128151](https://github.com/kims34/openpilot-opkr/actions/runs/41091128151): `auto-anchor` job `124184971844` FAILED on public hash-only prospective payload fetch (`/anchor/latest` HTTP 404), immutable record append and validation skipped. No retries or alternate URL bypass attempted.

## Original-source SHA / PIT / tradeability decision

[OpenDART first-filed 2022 official source-only run #38380988990](https://github.com/kims34/openpilot-opkr/actions/runs/38380988990), direct job `115241142185`: official original document ZIP received; bounded ZIP CRC read completed; one non-XML SGML/HTML layout; 1,570 source tables inspected; 15 operating-profit-shaped rows (12 with 4 numeric peers), but **0 exact 2022/2021 Q3 window row matches and 0 verified consolidated three-month operating-profit facts**. `original_q3_cfs_three_month_profit_bound=false`, `historical_publication_instant_pit_verified=false`, `historical_security_corp_mapping_verified=false`, `historical_correction_lineage_complete=false`. Recorded original 2022 ZIP SHA-256 in prior official evidence: `56639d8f6ebbecf14cd8bc3179d75d01162e2cd7bbdf8f6a3c9479b44f5084bb`; **not independently rehashed from original ZIP bytes in this run**. Do not confuse uploaded flags-only artifact ZIP SHA with original document ZIP SHA.

KRX historical dedicated worker deployed `16c93d7c-7cd0-4d84-a327-298d2805376c`, source commit `1e6367d2863a86c3470da13d81a955d277eba485`. Existing 2017–2022 1,565/1,565 private daily/master source-pair storage integrity limited PASS **not rerun against original bytes this turn**. 90 unclassified calendar/source-gap sessions and 12,003 zero-activity OHLC samples are **not** historical tradability approvals. Prospective 27 nonpositive OHLC rows out of 803 common-stock rows remain fail-closed; no security selection or deletion to pass the gate. Exact exchange session calendar, historic listing/halts/delistings/corporate actions, point-in-time market cap, realistic lot-size fills, spread/impact/slippage, commissions and taxes **not independently admitted**.

## Direct Railway production status and runtime

Project `d1c1a050-b7d6-41ce-b300-13c20f82a20a`, environment `83d5840b-270e-4d3f-a941-a37fd4a55ff7`. PIT service deployment `8b354fc1-cfb2-4ef0-863e-67f7f5dda2b5` remains SUCCESS, source commit `e57054ecdb3e734ced3c9a981b887d9b5fc60f97`, health 1/1 running. Latest returned deploy log `2026-11-02T14:46:22.403874064Z` (23:46:22 KST): `status=FAIL_CLOSED`, `error_reason_code=COMMON_OHLC_NONPOSITIVE`, `source_failure_session=2026-09-28`, `nonpositive_ohlc_rows=27`, `common_stock_rows=803`, `session_manifest_sha256=null`, independent source/model/chronology approvals all false, `ordering=DISABLED`, real orders/funds/permission authority false. A query starting `2026-11-02T14:00Z` returned only four entries through 14:46Z; no post-14:46Z entries is **log observation gap**, not evidence of service repair/outage.

Historical worker query since `2026-11-02T14:00Z` returned zero new deploy entries; no fresh private raw-SHA admission. Kiwoom REAL read-only service `indexalert-kiwoom-real-readonly` latest deployment `a77fb922-b679-4d88-92c4-03054ec579cd` is marked SUCCESS/online while health replica counts show **0 running, 1 crashed**; unresolved telemetry inconsistency. No restart or configuration changes.

Railway `describe_environment` and `get_staged_changes` both show `staged=null` / no changes, but `environment_status` reports pending patch `e113dacb-6705-4416-9997-dc694539d382` with empty change list. **Cross-view inconsistency remains unverified**; no accept/deploy.

## Independent economics gate (no returns generated)

| Criterion | Verdict |
|---|---|
| Original OpenDART document source receipt / bounded row-shape | LIMITED PASS, not economic fact |
| Original exact 3-month CFS operating income, correction/publication clock, issuer PIT | NOT VERIFIED |
| KRX original pair storage integrity | PRIOR LIMITED PASS, not independently rehashed now |
| Exchange tradability, fills, spread/slippage/market impact, fees and tax by as-of | NOT VERIFIED |
| Frozen 20-session horizon, 504/126/126 train/cal/test, purge20, Top3/no rank-4 backfill, NO_TRADE | PRESERVED; no experiment run |
| After-tax NetEV, PF, CAGR, MDD, ES95/99, clustered uncertainty, concentration, 2x-cost stress | NOT EVALUABLE without admitted original PIT and executable cost/tradability |
| H5/0-N archived economic limitations and Holdout | NO REUSE / NO PROMOTION |
| M20 official profitability run / live orders / Champion promotion | **NO-GO / NOT AUTHORIZED** |

No new independently admitted original source, economic result or approval was found. **Next dependency:** original as-filed 3-month CFS/publication/correction/issuer PIT evidence from source specialist and official historical KRX market-state/lot/fill/fees/tax proofs from KRX specialist. Keep other teams' work isolated. No backtest, live trade, account change, permission change, deployment, PR merge or Champion promotion.
