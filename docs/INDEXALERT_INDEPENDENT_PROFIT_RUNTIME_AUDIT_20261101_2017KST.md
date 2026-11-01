# IndexAlert independent profitability and isolated runtime audit — 2026-11-01 20:17 KST

**Decision:** M20 economic run **NO-GO / NOT EVALUABLE**; original PIT **NOT VERIFIED**; PR #418 archived replay **FAIL-CLOSED**, adoption **NO-GO**; `ORDERING=DISABLED`. This is a source/log/CI-only audit. No financial backtest, new strategy exploration, Holdout replay, real order, permission/credential/funds change, merge, deploy, or workflow edit.

## Ref and ownership snapshot (GitHub connector, read-only)

GitHub repository: `kims34/openpilot-opkr`. Branch identity independently queried using identical-ref GitHub compare (base commit SHA), not inferred from earlier prose:

- Research `index-alert-research-v1`: `3b8b7830612a6284d7c7a60628cb527cb741627a`.
- Development `index-alert-position-regen-fix-v1`: `1e6367d2863a86c3470da13d81a955d277eba485`.
- KRX `indexalert-krx-pit-source-audit-20261013`: `073d2d49e95f69fb10b943b93e51bb179fb3c698`.
- Draft [#414](https://github.com/kims34/openpilot-opkr/pull/414): `49bdc4c6e0f05652c1d92018789f1d4f7e29ab54`, integration gate file blob SHA-1 `984c933651f39f1ee9e26a1d7ac3893aaa5335be`.
- Draft [#413](https://github.com/kims34/openpilot-opkr/pull/413): `f003ef6247e16fcc71bd3b1b20cd4904c4d984c0`; Draft [#418](https://github.com/kims34/openpilot-opkr/pull/418): `2f98401cc50a6c6a25808a98516efd5bf0c944ee`.
- Draft [#412](https://github.com/kims34/openpilot-opkr/pull/412): `bf3d9514a87c53b1775e22ec9ba7711f6cecc49f`; KRX-related Draft [#420](https://github.com/kims34/openpilot-opkr/pull/420): `fab3cbbd63a951a4e081f9e7f08c1391ca308581`, [#422](https://github.com/kims34/openpilot-opkr/pull/422): `c14857620973531013799e44625d43080904fd5f`, [#423](https://github.com/kims34/openpilot-opkr/pull/423): `0e38004363cac9fc4475556b3a1c445de9af407f`. Draft [#416](https://github.com/kims34/openpilot-opkr/pull/416) `053de553646fc4765d2616544ca1e8d6bbdde35f`. No edits to delegated branches.

## Independent admission matrix

| Gate | Verdict | Scope and missing proof |
|---|---|---|
| 2022 original/adjusted OpenDART source ZIP and SGML candidate signatures | **LIMITED PASS** | [official/offline Actions #38419439742](https://github.com/kims34/openpilot-opkr/actions/runs/38419439742) 2/2 success, 15 candidate-row signatures; source edition byte identity only, not economic facts. |
| 2021/2022 *first-filed* consolidated stand-alone Q3 three-month operating profit, exact original public available-at, correction-vintage lineage, historical issuer/security identity | **NOT VERIFIED** | Exact source cell/period/first release timestamp and point-in-time mappings not independently attested; no amended value backfill. |
| KRX 2017–2022 private original weekday source pair integrity | **LIMITED PASS (prior original evidence)** | 1,565/1,565 private raw pairs, no invalid stored pair in previous Railway audit; **not** official session calendar or tradability proof. |
| KRX official 90 unresolved sessions, 12,003 zero-activity rows, historical halt/listing/corporate actions/fillability, fees/taxes/slippage | **NOT VERIFIED** | Source-quality flags remain blockers, not filters to optimize away. |
| M20 after-tax NetEV, PF, CAGR, MDD, ES95/ES99, concentration and date-cluster/year sensitivity | **NOT EVALUABLE / NO-GO** | No independently admitted source PIT or official execution economics. Do not calculate performance or reuse consumed H5 Holdout. |
| PR #413 frozen offline 34-case regression parity | **LIMITED PASS** | [#38381997417](https://github.com/kims34/openpilot-opkr/actions/runs/38381997417), [#38382214223](https://github.com/kims34/openpilot-opkr/actions/runs/38382214223), [#38419111311](https://github.com/kims34/openpilot-opkr/actions/runs/38419111311), [#38508247773](https://github.com/kims34/openpilot-opkr/actions/runs/38508247773) all 6/6 jobs success. Frozen case digest SHA-256 `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34` from archived evidence. |
| PR #418 standalone runner synthetic/offline parity | **LIMITED PASS only** | [#38419649711](https://github.com/kims34/openpilot-opkr/actions/runs/38419649711) 1/1; earlier test-phase serial 2.9656s versus concurrent 2.6209s = 1.1315x; no complete CI or official backtest acceleration proof. |
| PR #418 archived source replay | **FAIL-CLOSED / adoption NO-GO** | [#39111405478](https://github.com/kims34/openpilot-opkr/actions/runs/39111405478) failed with `SourceDriftError`: archived expected `research_v1_runtime_manifest.py` blob `108f66714602a1bd3ae42c34dcca7c16e38f460b` vs actual PR #413 `e0055c66c59398fd4a1158077446d886b54c4e37`. PR #418 `research_v1_runtime_archived_source_gate.py` blob `92cd52a4226fe7e1b58316e298e9d862178c12f1` uses path pre-check and `read_bytes`, not PR #413 manifest's descriptor-based no-follow protection. The distinct PR #418 `research_v1_runtime_handoff.py` blob `c3b629a62fd60704d0c6a18c4dfb4a863294eaa4` *does* implement descriptor no-follow checks, but does not fix archived source gate or prove authenticated PIT. |
| PR #418 candidate merge-source audit | **LIMITED PASS, non-admitting** | [#39111405494](https://github.com/kims34/openpilot-opkr/actions/runs/39111405494) 1/1 success, candidate 22-package-version checks and direct source controls; transitive dependency closure not pinned. [#39111405562](https://github.com/kims34/openpilot-opkr/actions/runs/39111405562) 1/1 one-runner CI success, not a merge or production speed approval. |

## Fresh Railway production and watchdog checks

Railway IndexAlert project `d1c1a050-b7d6-41ce-b300-13c20f82a20a`, production `83d5840b-270e-4d3f-a941-a37fd4a55ff7`. Read-only `describe_environment` and `get_staged_changes` report **staged=null**, zero resources. However `environment_status` still returns an old **staged** pendingWork patch `e113dacb-6705-4416-9997-dc694539d382` (2026-10-29). This cross-API disagreement is **NOT VERIFIED**; do not accept/deploy or assume patch is actionable. `indexalert-kiwoom-real-readonly` reports SUCCESS deployment `a77fb922-b679-4d88-92c4-03054ec579cd` but `running=0, crashed=1` despite summary state online: unresolved health inconsistency, no changes.

PIT-rebuild deployment `8b354fc1-cfb2-4ef0-863e-67f7f5dda2b5` returned logs through **2026-11-01 11:15:47 UTC = 20:15:47 KST**. Session 2026-11-01: `FAIL_CLOSED`, `COMMON_OHLC_NONPOSITIVE`, common-stock 803, nonpositive OHLC 27, `fresh_alpha_observation_admitted=false`, `independent_source_admission_verified=false`, `real_orders_authorized=false`, `ordering=DISABLED`. Runtime logs through 2026-11-01 11:17:46 UTC (20:17:46 KST) show read-only index/FX monitoring, not profitability admission. KRX historical worker deployment `16c93d7c-7cd0-4d84-a327-298d2805376c` SUCCESS but this log query returned zero entries; old original source integrity proof is not newly reattested this run.

[Watchdog #41292056320](https://github.com/kims34/openpilot-opkr/actions/runs/41292056320) one successful job, actual log 2026-11-01 09:12:03 UTC: **`M20 PIT admission: NOT ATTESTED; orders: DISABLED; holdout: NOT AUTHORIZED`**.

## Locked policy and next independent proof

Preserve Frozen H5, M20 horizon20/purge20, WF504/126/126, PIT/label/Purged/CPCV, sealed independent Holdout, Champion/Top3/NO_TRADE, costs, taxes, execution and promotion thresholds; no unapproved re-fit/capital transition parallelism. Cache reuse requires independently authenticated original/data/code/Frozen/runtime/evidence SHA-256 identities, strict fail-closed; parallelism only for independent read-only postprocessing. No M20 performance RUN, official market return experiments, model search, real orders, capital movement, credential/permission changes, Champion promotion, deployment, workflow bypass or PR merge. The only permitted change in this run is this isolated audit document.

**Next critical path:** OpenDART owner must prove first-published 2021/2022 exact Q3 consolidated operating-profit cells, period, available-at and correction vintage; KRX owner must independently prove official session/security/tradability/corporate-action and fill economics; optimization owner must resolve #418 archived source drift and full transitive security equivalence without rewriting old archived baseline. Only after independent PIT/source/execution approval may the single preregistered M20 economics gate be considered.
