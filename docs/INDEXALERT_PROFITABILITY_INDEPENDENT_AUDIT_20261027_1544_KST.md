# IndexAlert independent profitability evidence audit — 2026-10-27 15:44 KST

Scope: read-only independent audit; documentation-only receipt on the existing Draft PR #414 isolated branch. No official-data economic backtest, order, deployment, PR merge, branch policy change, or specialist code modification. No independent approval is inferred from CI success.

## Current GitHub identities (read directly from branch/PR endpoints)

- Research `index-alert-research-v1`: `3b8b7830612a6284d7c7a60628cb527cb741627a`.
- Development `index-alert-position-regen-fix-v1`: `1e6367d2863a86c3470da13d81a955d277eba485`.
- All **Draft, open, unmerged**: #412 OpenDART head `bf3d9514a87c53b1775e22ec9ba7711f6cecc49f`; #413 optimization `f003ef6247e16fcc71bd3b1b20cd4904c4d984c0`; #414 integration pre-receipt head `bdb02780c8c3b7ea5f6a287c160bc8abea4a00cd`; #418 one-runner `2f98401cc50a6c6a25808a98516efd5bf0c944ee`; KRX #420 `fab3cbbd63a951a4e081f9e7f08c1391ca308581`, #422 `c14857620973531013799e44625d43080904fd5f`, #423 `0e38004363cac9fc4475556b3a1c445de9af407f`.
- [Integration gate](https://github.com/kims34/openpilot-opkr/blob/indexalert-profitability-integration-evidence-20261013/docs/INDEXALERT_PROFITABILITY_INTEGRATION_GATE_2026-10-13.md), read blob SHA `984c933651f39f1ee9e26a1d7ac3893aaa5335be`. Preserve Frozen H5, M20 horizon20/purge20, WF504/126/126, label/Purged/CPCV/independent Holdout, Champion/Top3/NO_TRADE, fixed costs/taxes/advancement gates. Do not re-use consumed H5 or Dynamic holdouts.

## Directly checked Actions and scope of evidence

1. [Latest watchdog #40436115571](https://github.com/kims34/openpilot-opkr/actions/runs/40436115571), job `121965063367`, SUCCESS at 2026-10-27 02:02 UTC. Log explicitly: `M20 PIT admission: NOT ATTESTED; orders: DISABLED; holdout: NOT AUTHORIZED`. Artifact `12704386902`, uploaded ZIP SHA-256 `3ea4af4d7f8dfe080b191901e6fcba21425d82cd24e57e48c8ef0eeb0d9ca7c5`. Offline safety PASS, **not** PIT/source/financial-return approval. No later workflow run in repository latest-25 list at this read.
2. [OpenDART first-original 2021 #40262558066](https://github.com/kims34/openpilot-opkr/actions/runs/40262558066), official job `121379096007`, SUCCESS. Official flags-only log: `2021_original_zip_sha256=8728c0a3c12761ca19e9c6455bea8f1bed0e4c1ebc2e21dc263c373a82a2b625`, one SGML source, **1,728 table shapes**, 13 operating-label candidate tables, **0 same-table 2021 Q3-period or 3-month text matches**. `original_2021_q3_three_month_cfs_profit_cell_verified=false`, `first_2022_q3_report_2021_comparator_cell_verified=false`, `2021_first_publication_instant_verified=false`, `full_2021_amendment_vintage_chain_verified=false`, `m20_feature_pit_admitted=false`, `m20_performance_run_authorized=false`. Artifact `12625042488` ZIP SHA-256 `3fe75e2af23f508d3c518a14e98732a399eb0daeca46cccd7b3191b1e2e4777b`. **PASS** only first-original 2021 source ZIP identity/integrity; not CFS period-cell semantic proof. 2022 first-original source ZIP identity and later correction archive integrity have historical source-only PASS; no first-published 2022/2021 exact three-month CFS operating-profit and available-at admission.
3. [KRX #423 synthetic CI #39714207925](https://github.com/kims34/openpilot-opkr/actions/runs/39714207925), job `119612335677`, SUCCESS with 32 offline tests. Log explicitly asserts `DRY_RUN_NO_PRIVATE_STORAGE_READ` and `2022_private_candidate_date_sets_equal=false`. Thus synthetic logic PASS, private original day-set / official market calendar and tradability **NOT VERIFIED**. Historical Railway receipt of 1,565/1,565 2017–2022 weekday pairs SHA integrity PASS is storage-only; 90 unresolved market-day/source gaps, 12,003 zero-activity rows and 27 prospective invalid-OHLC common-stock candidates remain vetoed, not trading permission.
4. [Chronology anchor #40360864884](https://github.com/kims34/openpilot-opkr/actions/runs/40360864884), job `121705590170`, **FAIL** at 2026-10-26 17:16 UTC: `ANCHOR_URL=https://indexalert-pit-rebuild-production.up.railway.app/anchor/latest`, `HTTP Error 404: Not Found`. This is a failed independent prospective chronology receipt, not evidence of a functioning PIT anchor.
5. [#413 original CI #38381997417](https://github.com/kims34/openpilot-opkr/actions/runs/38381997417): 6/6 jobs SUCCESS. Historical pinned 34-case identity/outcome SHA-256 `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34`. [#418 one-runner #38419649711](https://github.com/kims34/openpilot-opkr/actions/runs/38419649711), job `115373285730`, SUCCESS with original 34-case pinned digest and 2.9656s serial vs 2.6209s parallel suite phase (1.1315x **phase only**); uploaded artifact `11825277809` ZIP SHA-256 `4510f571f1ad48d1c640b870804a2d4269cba6916551327ee52173c0b29c2409`. Whole-CI wall time, immutable combined-source dependency closure and real admitted H5/M20 performance speedup **NOT VERIFIED**. Prior stricter archived code Git blob SHA mismatch remains FAIL; never re-pin original archive to mask this.

## Independent admission verdict (PASS / FAIL / NOT VERIFIED)

| Gate | Verdict | Reason |
|---|---|---|
| 2021 first-original ZIP source integrity | PASS (source only) | Pinned official ZIP SHA; no earnings fact authorization |
| 2022 original and corrected ZIP identity | PASS (historical source-only) | No original-period/available-at semantics certified |
| 2021/2022 exact 3-month first-published CFS operating profit; correction lineage | NOT VERIFIED | 2021 13 candidate labels, zero strict period match; 2022 exact cell/edition not bound |
| Original public available-at/PIT and historical corp-to-security identity | NOT VERIFIED | First publication and as-of mapping absent |
| KRX raw stored-pair SHA integrity | PASS (historical storage only) | 1,565/1,565 prior private receipt; cannot directly refresh Railway |
| Official exchange calendar, trade states, corporate actions, executable fills | NOT VERIFIED | 90 gaps, 27 OHLC vetoes, private exact-set untested |
| Prospective chronology anchor | FAIL | GitHub Actions HTTP 404 |
| Offline synthetic safety/parity | PASS (limited) | 32 KRX mocks, 34 pinned optimization cases; no financial admission |
| Complete original #418 code SHA closure and real end-to-end acceleration | FAIL / NOT VERIFIED | Archived blob mismatch / no full workflow or market run |
| Verified fees, taxes, execution costs and after-tax NetEV/PF/CAGR/MDD/ES95/99, concentration, date-cluster robustness | NOT VERIFIED | PIT and market source prerequisites blocked; **no** M20 economic execution |
| Operational ORDERING environment value | NOT VERIFIED | Railway connector required interactive authorization in non-interactive read-only call |

## Railway and operational boundary

Attempted authenticated Railway `list_projects` read-only; connector returned **`User input required but current turn is running in a non-interactive mode.`** No project/deployment/log/variable value was read this run. Do not claim current production `ORDERING=false` has been directly observed; enforce it as a mandatory fail-closed policy. Do not bypass authorization or use alternate privileged paths.

## Next permitted independent steps

- Delegated OpenDART owner: first-published 2021/2022 CFS exact three-month profit cell, original and correction publication instants, full as-of corporate mapping with source SHA; keep original source values distinct from later corrections.
- Delegated KRX owner: official market/session/security-state and corporate-action as-of provenance, private exact-day-set SHA comparison on separately approved existing worker, executable cost/tax/fill bounds. Do not treat synthetic CI as private read.
- Delegated optimization owner: strict transitive code/source SHA closure and full-CI wall-clock A/B under immutable offline-only 34-case set, without source PIT bypass.
- Independent orchestration: refresh Railway deploy/runtime and actual order-disable flag only after supported read-only connection is authorized. Do not touch specialist code or repeat performance research. Once every source/PIT/tradability gate is independently PASS, request separate explicit authorization for any first M20 economic evaluation; until then `m20_performance_run_authorized=false`.

**Final status: M20 ECONOMIC RUN NO-GO; Frozen/Holdout/Champion/Top3 unchanged; ORDERING=false required. No live order, funds, account or credential changes, deployment, merges, Champion promotion, or holdout reuse.**
