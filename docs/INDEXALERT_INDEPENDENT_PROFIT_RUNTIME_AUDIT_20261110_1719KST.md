# IndexAlert independent profitability / isolated runtime audit — 2026-11-10 17:19 KST

Scope: read-only GitHub/Railway evidence, frozen source-admission and offline-only optimisation. No production or economic experiment authorised. Independent audit branch indexalert-independent-audit-20261110-1719kst; branch base is research HEAD.

## Exact source refs
- Research index-alert-research-v1 HEAD: `df474df348f22aa38b1dedaa59fcff66e548b406`.
- Development index-alert-position-regen-fix-v1: previously established `1e6367d2863a86c3470da13d81a955d277eba485`; today's compare endpoint confirms divergence (development ahead 1148, behind 281) but did **not** independently return its head SHA. Thus current dev HEAD SHA: NOT VERIFIED this run.
- Merge base `c490974ff6619bb978dc6f83f9c24f2c46622f85`.
- PRs all OPEN, Draft, unmerged at query: [#412](https://github.com/kims34/openpilot-opkr/pull/412) HEAD `bf3d9514a87c53b1775e22ec9ba7711f6cecc49f`; [#413](https://github.com/kims34/openpilot-opkr/pull/413) HEAD `f003ef6247e16fcc71bd3b1b20cd4904c4d984c0`; [#414](https://github.com/kims34/openpilot-opkr/pull/414) HEAD `18c5418d9684d1717df58261ea27f28e514385b2`; [#418](https://github.com/kims34/openpilot-opkr/pull/418) HEAD `2f98401cc50a6c6a25808a98516efd5bf0c944ee`; [#420](https://github.com/kims34/openpilot-opkr/pull/420) HEAD `fab3cbbd63a951a4e081f9e7f08c1391ca308581`; [#422](https://github.com/kims34/openpilot-opkr/pull/422) HEAD `c14857620973531013799e44625d43080904fd5f`; [#423](https://github.com/kims34/openpilot-opkr/pull/423) HEAD `0e38004363cac9fc4475556b3a1c445de9af407f`.
- PR #414 [gate](https://github.com/kims34/openpilot-opkr/blob/18c5418d9684d1717df58261ea27f28e514385b2/docs/INDEXALERT_PROFITABILITY_INTEGRATION_GATE_2026-10-13.md) blob SHA `984c933651f39f1ee9e26a1d7ac3893aaa5335be`; directly read from PR HEAD.
- Action jobs directly queried: [38381997417](https://github.com/kims34/openpilot-opkr/actions/runs/38381997417) 6/6 success; [38382214223](https://github.com/kims34/openpilot-opkr/actions/runs/38382214223) 6/6 success; [38419111311](https://github.com/kims34/openpilot-opkr/actions/runs/38419111311) 6/6 success; [38419649711](https://github.com/kims34/openpilot-opkr/actions/runs/38419649711) 1/1 success; [38419439742](https://github.com/kims34/openpilot-opkr/actions/runs/38419439742) 2/2 success. Job success is NOT original evidence/semantic PIT admission. The 34-case frozen SHA `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34`, 13 adversarial and 28 synthetic case contents were NOT independently recomputed in this run.

## Railway production (read-only)
Project `d1c1a050-b7d6-41ce-b300-13c20f82a20a`; environment `83d5840b-270e-4d3f-a941-a37fd4a55ff7`.
- PIT rebuild deployment `8b354fc1-cfb2-4ef0-863e-67f7f5dda2b5` SUCCESS, running 1/1.
- Runtime deployment `eaaa9f67-b9f2-41d2-832c-7d6fad9b9b00` SUCCESS, running 1/1.
- KRX worker deployment `16c93d7c-7cd0-4d84-a327-298d2805376c` SUCCESS, running 0/1, crashed 0/1: execution normality NOT VERIFIED.
- Kiwoom real readonly deployment `a77fb922-b679-4d88-92c4-03054ec579cd` SUCCESS but running 0/1 and crashed 1/1: **FAIL runtime health**, despite aggregate 'online' display.
- Backend and Push latest deployments FAILED/offline; db-query-readonly offline, 1 critical issue.
- PIT, KRX worker, Kiwoom readonly deploy logs queried from 2026-11-10T00:00:00Z: 0 entries each. Absence of logs is NOT evidence of execution.
- Environment inventory staged=null, but status endpoint lists old pending patch `e113dacb-6705-4416-9997-dc694539d382` with zero changes. Contradictory metadata: NOT VERIFIED, no application.
- Production ORDERING setting not inspected: NOT VERIFIED; required false remains a policy constraint, not a verified deployment fact.

## Gate matrix
| Evidence requirement | Verdict | Rationale |
|---|---|---|
| 2017–2022 1565/1565 weekday private raw pairs storage | Historical scoped PASS | Earlier immutable integrity evidence; not recalculated today |
| Official trading calendar, halts, corporate actions, execution, historical corp/security mapping | NOT VERIFIED / fail-closed | 90-day classification, zero-activity 12003 quarantined; raw storage != tradability |
| Original OpenDART filing SGML candidate signatures (15) | Historical scoped PASS for candidate shape only | Action 38419439742 2/2 CI success, semantic original period and public available-at unapproved |
| 2021/2022 first three-month consolidated operating profit, correction lineage, original filing PIT | NOT VERIFIED / fail-closed | No period/semantic/temporal admission |
| H5 reused/consumed holdout, dynamic retuning | FAIL admission | No post-hoc tuning or independent reuse |
| M20 horizon20/purge20, WF504/126/126 official source PIT | NOT VERIFIED, NO-GO | No official economic run |
| After-cost/tax NetEV, PF, CAGR, MDD, ES95/99, return concentration, robustness | NOT VERIFIED | No authorised independent original-source backtest |
| Offline CI harness | PASS scoped to jobs | 6/6, 6/6, 6/6, 1/1 observed; parity evidence SHA not recomputed |
| Whole CI / actual backtest acceleration | NOT VERIFIED | 2.9656/2.6209=1.1315 historical regression-phase only, not whole-run speedup |

## Frozen boundaries and safe next steps
Preserve Frozen H5 and M20 horizon20/purge20, WF504/126/126, PIT/label/Purged/CPCV/independent Holdout/Champion/Top3/NO_TRADE, original costs/taxes/NetEV/execution/risk/promotion gates, ORDERING=false. No model search, M20 economic run, official market return experiment or performance tuning until independently approved source PIT. Optimisation cache only if independent approved original/data/code/frozen policy/runtime/approval evidence SHA-256 all match, fail closed; parallelise read-only postprocessing only, never dependent retraining or capital transitions. Next: obtain independently auditable original filing public-time/period lineage, official KRX calendar/tradability, and immutable per-source manifests; separately verify 34-case SHA and synthetic mock outputs in existing isolated CI without altering frozen policy; diagnose readonly replica crash by logs without changing deployment. Do not merge #413/#414/#418, deploy, trade, transfer funds, change account/auth, or promote Champion without separate explicit approval. No workflow writes attempted.
