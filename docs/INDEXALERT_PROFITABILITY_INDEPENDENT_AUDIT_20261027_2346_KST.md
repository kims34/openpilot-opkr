# IndexAlert independent profitability evidence audit — 2026-10-27 23:46 KST

> Documentation-only, independent read-only audit. This file does not authorize source admission, performance tests, orders, funds, permissions, deployment, PR merge, or Champion promotion. No original financial cells, private market records, account data or credentials are reproduced.

## Exact repository heads and workstream isolation (GitHub API read, 2026-10-27 23:46 KST)

- Research `index-alert-research-v1`: `3b8b7830612a6284d7c7a60628cb527cb741627a`.
- Development `index-alert-position-regen-fix-v1`: `1e6367d2863a86c3470da13d81a955d277eba485`.
- Independent audit branch `indexalert-profitability-integration-evidence-20261013` before this audit: `397ff725cf51a770b4038c0054e207059982d6cf`.
- [Integration Draft PR #414](https://github.com/kims34/openpilot-opkr/pull/414): head `397ff725cf51a770b4038c0054e207059982d6cf`; [source Draft PR #412](https://github.com/kims34/openpilot-opkr/pull/412): `bf3d9514a87c53b1775e22ec9ba7711f6cecc49f`.
- KRX [Draft #420](https://github.com/kims34/openpilot-opkr/pull/420): `fab3cbbd63a951a4e081f9e7f08c1391ca308581`; [Draft #422](https://github.com/kims34/openpilot-opkr/pull/422): `c14857620973531013799e44625d43080904fd5f`; [Draft #423](https://github.com/kims34/openpilot-opkr/pull/423): `0e38004363cac9fc4475556b3a1c445de9af407f`.
- Optimization [Draft #413](https://github.com/kims34/openpilot-opkr/pull/413) `f003ef6247e16fcc71bd3b1b20cd4904c4d984c0` and dependent [Draft #418](https://github.com/kims34/openpilot-opkr/pull/418) `2f98401cc50a6c6a25808a98516efd5bf0c944ee`; **no changes** made to their code or workflows.
- All listed PRs remain open, Draft, unmerged. Integration gate file `docs/INDEXALERT_PROFITABILITY_INTEGRATION_GATE_2026-10-13.md` read at Git blob SHA `984c933651f39f1ee9e26a1d7ac3893aaa5335be`. Audit is separate from this shared gate.

## Newest primary CI evidence checked

- [Watchdog Actions #40521236880](https://github.com/kims34/openpilot-opkr/actions/runs/40521236880), 2026-10-27 14:27 UTC, head `04bdfc93975bb59961f1cb3bd3598d04f8e7bff4`, job `122248583591`: SUCCESS, 31 offline governance regression tests plus 4 watchdog contract tests; log: `IndexAlert read-only evidence metadata: COMPLETE`; `M20 PIT admission: NOT ATTESTED; orders: DISABLED; holdout: NOT AUTHORIZED`. Uploaded flags-only artifact ZIP SHA-256 `c3f7b23dd472a6075ba3371abcefced624be8ed9e3ae39973684f9d542914378`. These are **software/policy PASS only**, not primary market or financial source proof.
- [2021 first-original OpenDART #40262558066](https://github.com/kims34/openpilot-opkr/actions/runs/40262558066), official job `121379096007`: SUCCESS, exact first 2021 Q3 document ZIP SHA-256 `8728c0a3c12761ca19e9c6455bea8f1bed0e4c1ebc2e21dc263c373a82a2b625` (original byte integrity PASS). Official log counts: 1,728 table shapes, 13 operating-label table candidates, 0 with 2021 Q3 period in the same table, 0 with three-month wording. Flags `original_2021_q3_three_month_cfs_profit_cell_verified=false`, `first_2022_q3_report_2021_comparator_cell_verified=false`, `2021_vs_2022_original_comparator_amounts_verified=false`, `2021_first_publication_instant_verified=false`, `2022_first_publication_instant_verified=false`, `historical_issuer_security_pit_verified=false`, `full_2021_amendment_vintage_chain_verified=false`, `m20_performance_run_authorized=false`. ZIP integrity is **not** accounting semantics, correction lineage, or PIT approval.
- Prior official [2022 OpenDART #38417433460](https://github.com/kims34/openpilot-opkr/actions/runs/38417433460) documented first ZIP SHA-256 `56639d8f6ebbecf14cd8bc3179d75d01162e2cd7bbdf8f6a3c9479b44f5084bb`, corrected ZIP SHA-256 `606be9d03928808f0a2a05f052444587bd2457bdef7a47a8f4bff3d2ea098a30`. Prior [#38466077093](https://github.com/kims34/openpilot-opkr/actions/runs/38466077093) shows 0 verified exact original three-month 2022/2021 consolidated profit cells; amendment and candidate-table similarity cannot supply original PIT. These older receipts are referenced, not independently re-fetched in this run.
- KRX [2022 candidate offline CI #39714207925](https://github.com/kims34/openpilot-opkr/actions/runs/39714207925), job `119612335677`: SUCCESS, 32 synthetic/no-provider safety tests. The job explicitly asserts `2022_private_candidate_date_sets_equal == false` in default no-private-read mode, `ordering == DISABLED`; therefore **NOT** an exact private-vs-official historical calendar PASS. Prior Railway worker storage receipt for 2017–2022 1,565/1,565 weekday daily/master source pairs is **RAW SHA STORAGE INTEGRITY PASS only**; 90 market-calendar/source gaps, 12,003 sampled zero-activity OHLC and 1 invalid sample remain excluded. No fresh private Railway storage receipt was available this run.
- [Prospective Chronology Anchor #40360864884](https://github.com/kims34/openpilot-opkr/actions/runs/40360864884), job `121705590170`: FAIL. Runtime fetched `https://indexalert-pit-rebuild-production.up.railway.app/anchor/latest` and received HTTP 404; validation job skipped. Do not infer valid chronological public-availability receipts.

## Independent admission matrix

| Gate | Verdict | Evidence boundary |
|---|---|---|
| Original OpenDART archive byte SHA | **PASS, limited** | Exact fixed first-2021 and prior first-2022 archive receipts |
| First-filing consolidated 3-month Q3 2021/2022 operating profit; correction vintage and precise public available-at | **NOT VERIFIED** | 13 candidates / 0 exact 2021 period matches; no authoritative original financial-cell/PIT lineage |
| Historical issuer/security mappings and original corporate actions | **NOT VERIFIED** | No complete point-in-time primary receipt |
| KRX raw six-year weekday pair storage SHA | **PASS, limited/prior** | 1,565/1,565 storage receipts, not official exchange state |
| Official historical session, suspension/delisting, tradability, lot/fill and costs/taxes | **NOT VERIFIED** | 90 gaps, zero-activity vetoes, synthetic-only CI, no private source comparison |
| NetEV after all costs/taxes, PF, CAGR, MDD, ES95/99, concentration, time robustness | **NOT VERIFIED / NOT RUN** | Market/financial PIT admission incomplete; never invent strategy performance |
| Watchdog fail-closed offline safety | **PASS** | #40521236880; no M20 or holdout authorization |
| Prospective chronology public endpoint | **FAIL** | #40360864884 HTTP 404 |
| Railway current deployment/logs and actual live ORDERING value | **NOT VERIFIED (ACCESS BLOCKED)** | Connected Railway `list_projects` read-only request required interactive user input, unavailable in this non-interactive audit. No alternate credential, endpoint, or bypass attempted. `ORDERING=false` remains a **required policy**, not independently attested live configuration. |

## Immutable decision and next evidence owners

**M20 PERFORMANCE NO-GO**. Frozen H5, M20 horizon20/purge20, WF504/126/126, independent consumed Holdout, Champion/Top3/NO_TRADE, cost/tax and risk thresholds remain unchanged. No reoptimization, H5 failed holdout reuse, economic backtest, strategy search, or Champion promotion. `ORDERING=false` is mandatory; no live orders, funds, credentials, production deploy or merges.

OpenDART owner: bind authoritative original 2021/2022 three-month CFS financial cells to exact first public availability and full amendment lineage; map historical issuer/security PIT. KRX owner: independently reconcile official calendar and private 90-day gaps, historical trading states, corporate actions, fill feasibility, and actual costs/taxes with source SHA and event-time. Railway: user-authorized noninteractive **read-only** access is required to independently inspect current deployment logs and actual ordering setting; do not bypass interactive access gate. Optimization owners retain separate isolated workspaces; offline CI correctness is not an economic result.

Only this independent documentation file is eligible for the single allowed write attempt. No other writes or changes attempted.
