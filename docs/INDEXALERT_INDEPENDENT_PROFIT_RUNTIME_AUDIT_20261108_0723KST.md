# IndexAlert independent profitability and isolated runtime audit — 2026-11-08 07:23 KST

Read-only audit of GitHub and Railway; this isolated documentation file is the only intended write. No workflow/code/model/data/trading/deployment changes. No M20 performance run.

## Fresh immutable references
- Research `index-alert-research-v1`: `df474df348f22aa38b1dedaa59fcff66e548b406` (self-comparison identical).
- Development `index-alert-position-regen-fix-v1`: `1e6367d2863a86c3470da13d81a955d277eba485` (self-comparison identical).
- All OPEN/Draft/unmerged: [#412](https://github.com/kims34/openpilot-opkr/pull/412) `bf3d9514a87c53b1775e22ec9ba7711f6cecc49f`; [#413](https://github.com/kims34/openpilot-opkr/pull/413) `f003ef6247e16fcc71bd3b1b20cd4904c4d984c0`; [#414](https://github.com/kims34/openpilot-opkr/pull/414) `18c5418d9684d1717df58261ea27f28e514385b2`; [#418](https://github.com/kims34/openpilot-opkr/pull/418) `2f98401cc50a6c6a25808a98516efd5bf0c944ee`; KRX [#420](https://github.com/kims34/openpilot-opkr/pull/420) `fab3cbbd63a951a4e081f9e7f08c1391ca308581`, [#422](https://github.com/kims34/openpilot-opkr/pull/422) `c14857620973531013799e44625d43080904fd5f`, [#423](https://github.com/kims34/openpilot-opkr/pull/423) `0e38004363cac9fc4475556b3a1c445de9af407f`.
- PR #414 gate `docs/INDEXALERT_PROFITABILITY_INTEGRATION_GATE_2026-10-13.md` Git blob `984c933651f39f1ee9e26a1d7ac3893aaa5335be` (direct read).

## Original CI job results checked
- [38381997417](https://github.com/kims34/openpilot-opkr/actions/runs/38381997417), [38382214223](https://github.com/kims34/openpilot-opkr/actions/runs/38382214223), [38419111311](https://github.com/kims34/openpilot-opkr/actions/runs/38419111311), [38498552499](https://github.com/kims34/openpilot-opkr/actions/runs/38498552499): each 6/6 success.
- [38419439742](https://github.com/kims34/openpilot-opkr/actions/runs/38419439742): 2/2 success; [38419649711](https://github.com/kims34/openpilot-opkr/actions/runs/38419649711): 1/1 success.
- [41515392296](https://github.com/kims34/openpilot-opkr/actions/runs/41515392296): auto-anchor FAILURE, validation SKIPPED.
- Fixed 34-case SHA-256 `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34`, 13 adversarial mocks, 28 synthetic tests and serial 2.9656s vs parallel 2.6209s are **historical reports, not recomputed from downloaded artifacts this run**. Only offline synthetic parity is supported; real end-to-end acceleration NOT VERIFIED. The 1.1315x figure concerns regression-phase ratio only.

## Railway production live read-only snapshot
Project `d1c1a050-b7d6-41ce-b300-13c20f82a20a`, production environment `83d5840b-270e-4d3f-a941-a37fd4a55ff7`.
- PIT rebuild deployment `8b354fc1-cfb2-4ef0-863e-67f7f5dda2b5`: SUCCESS, running 1/1; runtime `eaaa9f67-b9f2-41d2-832c-7d6fad9b9b00`: SUCCESS, running 1/1. Deployment success is not PIT admission.
- Real read-only service deployment `a77fb922-b679-4d88-92c4-03054ec579cd`: SUCCESS but replica **running 0, crashed 1**, despite UI service state 'online'; treat runtime health as FAIL/needs independent diagnosis. `db-query-readonly`: offline, 1 critical. Backend offline with 4 warnings; push offline with 1 warning.
- KRX historical worker `16c93d7c-7cd0-4d84-a327-298d2805376c`: SUCCESS, 0 running replicas (possibly completed worker); no new proof of official market state.
- Pending staged patch `e113dacb-6705-4416-9997-dc694539d382` has **zero listed changes**; leave untouched. No deployment/commit.
- PIT/KRX/real-readonly deploy-log queries since 2026-11-07T21:00:00Z returned empty. Absence of new logs cannot establish remediation of 27 bad OHLC rows or market/source approval.

## Admission decisions
| Gate | Verdict | Basis |
|---|---|---|
| OpenDART original ZIP candidate/source-byte provenance | PASS (previous scoped evidence only) | Historical original/correction signatures; no current original re-download |
| 2021/2022 exact first 3-month consolidated operating income, correction lineage, first public available-at | NOT VERIFIED | No complete original semantic period and time binding |
| Historical issuer/security as-of map | NOT VERIFIED | Incomplete authoritative lineage |
| KRX 2017–2022 private 1565/1565 stored weekday pairs | PASS (previous storage integrity only) | Not proof of official sessions/trading |
| KRX official calendar, halts, corporate actions, fill feasibility, cost/tax | NOT VERIFIED | 90 uncertain sessions, 12003 zero-activity blocked, 27 bad OHLC |
| H5 consumed holdout/Dynamic | FAIL for independent promotion | No reuse, no post-hoc retuning |
| M20 PIT and annual after-tax risk-adjusted NetEV/PF/CAGR/MDD/ES95/99, concentration/temporal robustness | NOT VERIFIED / NO-GO | Prerequisite data gates blocked; no economics run |
| Offline optimization safety CI | PASS (job outcomes only) | 6/6 and 1/1 successful, full CI/real backtest speed NOT VERIFIED |
| Real read-only Railway replica health | FAIL (observed 0 running, 1 crashed) | Separate operational blocker; no restart authorised |

## Safe next steps
1. Obtain independent original-filing/period/available-at evidence for 2021 and 2022 and reconcile corrections; preserve immutable evidence hashes.
2. Independently reconcile official KRX sessions, corporate actions, tradeability, zero-activity and 27 OHLC anomalies; no blanket exclusion for apparent performance improvement.
3. Diagnose crashed read-only replica using existing read-only deployment logs and service evidence; do not restart or modify production without separate authorisation.
4. In isolated optimization track, only synthetic offline fail-closed policy/cache provenance and read-only postprocessing parity; no dependent training/capital-transition parallelization. Preserve Frozen H5, M20 horizon20/purge20, WF504/126/126, Holdout/Champion/Top3/NO_TRADE and all cost/tax/risk thresholds.
5. Keep `ORDERING=false`, M20 NO-GO; no trades, funds movement, credentials changes, merges, deployments, workflow edits or Champion promotion.
