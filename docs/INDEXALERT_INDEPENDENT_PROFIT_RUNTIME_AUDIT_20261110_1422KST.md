# IndexAlert independent profitability and offline runtime audit — 2026-11-10 14:22 KST

## Scope and safety
Read-only GitHub and Railway production inspection; no official market replay, M20 profitability run, model search, order, money transfer, credential change, Champion promotion, merge, workflow edit, or deployment. This isolated document is the only repository modification. Other Work-owned code untouched. ORDERING=false; H5 frozen, consumed Holdout/Dynamic results never independently reused. M20 horizon20/purge20; WF504/126/126; frozen PIT, labels, Purged/CPCV, Holdout, Champion/Top3/NO_TRADE, execution, cost, tax and risk gates unchanged.

## GitHub immutable evidence
- Compare `index-alert-research-v1...index-alert-position-regen-fix-v1`: DIVERGED; research base HEAD `df474df348f22aa38b1dedaa59fcff66e548b406`; development HEAD previously established `1e6367d2863a86c3470da13d81a955d277eba485` (this run compare endpoint did not expose head commit SHA directly); merge base `c490974ff6619bb978dc6f83f9c24f2c46622f85`; development ahead 1148, behind 281. [Compare](https://github.com/kims34/openpilot-opkr/compare/index-alert-research-v1...index-alert-position-regen-fix-v1).
- PR #412 OPEN/Draft/unmerged HEAD `bf3d9514a87c53b1775e22ec9ba7711f6cecc49f`; #413 `f003ef6247e16fcc71bd3b1b20cd4904c4d984c0`; #414 `18c5418d9684d1717df58261ea27f28e514385b2`; #418 `2f98401cc50a6c6a25808a98516efd5bf0c944ee`; KRX #420 `fab3cbbd63a951a4e081f9e7f08c1391ca308581`, #422 `c14857620973531013799e44625d43080904fd5f`, #423 `0e38004363cac9fc4475556b3a1c445de9af407f`. All OPEN/Draft/unmerged as queried.
- PR #414 gate `docs/INDEXALERT_PROFITABILITY_INTEGRATION_GATE_2026-10-13.md` fetched on PR branch; blob SHA `984c933651f39f1ee9e26a1d7ac3893aaa5335be`. It explicitly preserves M20 PIT NO-GO and 2017–2022 raw storage integrity versus unverified market tradability.
- Actions [38381997417](https://github.com/kims34/openpilot-opkr/actions/runs/38381997417) and [38382214223](https://github.com/kims34/openpilot-opkr/actions/runs/38382214223): each 6/6 jobs success. [38419111311](https://github.com/kims34/openpilot-opkr/actions/runs/38419111311): 6/6 success. [38419649711](https://github.com/kims34/openpilot-opkr/actions/runs/38419649711): 1/1 success. [38419439742](https://github.com/kims34/openpilot-opkr/actions/runs/38419439742): 2/2 success. These are software CI conclusions, not source PIT or economics PASS. Prior 34-case fixture SHA `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34` and 13/28 synthetic case counts were supplied in historical evidence, not independently recalculated this run.
- Prior offline regression-phase serial 2.9656s versus concurrent 2.6209s = 1.1315x, **not** full CI or official backtest speedup. Only read-only independent post-processing may parallelize; dependent refits/capital transitions remain serial; cache must fail closed unless independently approved source/data/code/frozen policy/runtime/approval SHA-256 all match.

## Railway production read-only evidence
- Project `d1c1a050-b7d6-41ce-b300-13c20f82a20a`; environment `83d5840b-270e-4d3f-a941-a37fd4a55ff7`.
- PIT rebuild deployment `8b354fc1-cfb2-4ef0-863e-67f7f5dda2b5`: SUCCESS, replicas running 1/1; KRX historical worker `16c93d7c-7cd0-4d84-a327-298d2805376c`: SUCCESS, running 0/1 (not proof of live worker); Runtime `eaaa9f67-b9f2-41d2-832c-7d6fad9b9b00`: SUCCESS, running 1/1.
- Kiwoom real readonly `a77fb922-b679-4d88-92c4-03054ec579cd`: deployment SUCCESS and UI state online, but replica running 0, crashed 1 of 1 => **FAIL runtime replica health**. Backend, Push and db-query-readonly offline; latter reports critical issue. Do not infer health from deployment SUCCESS.
- From 2026-11-10T00:00Z, Railway service deploy logs PIT, KRX and Kiwoom readonly each returned zero entries. Runtime returned live informational index/FX checks. Zero log entries are NOT evidence of correctness or of fixing 27/803 anomalous OHLC.
- Environment reports staged patch `e113dacb-6705-4416-9997-dc694539d382` with zero changes; do not apply.

## Independent gate decisions
| Gate | Decision | Reason |
| --- | --- | --- |
| 2017–2022 KRX 1565/1565 weekday private raw pair storage integrity | HISTORICAL PASS only | Previously pinned SHA audit; no fresh raw bytes reread |
| Official trading calendar/status, corporate actions, historical ticker/entity mapping, fillability, zero-activity 12003, 90-day classification, 27/803 OHLC anomalies | NOT VERIFIED / fail-closed | No independently reconciled official point-in-time state |
| OpenDART 2021/2022 original first-filed consolidated 3-month operating income, amendment lineage and exact public available-at | NOT VERIFIED / fail-closed | 15 candidate rows/signatures and successful Action do not establish semantic original or timestamp |
| H5 / consumed Holdout | NO-GO / non-reusable | No retrospective tuning or independent reuse |
| M20 PIT and economic RUN | NOT APPROVED | Source admission incomplete |
| Cost/tax-adjusted annual risk-adjusted NetEV, PF, CAGR, MDD, ES95/99, concentration, temporal robustness | NOT VERIFIED | No approved PIT/fillability/economics run |
| Offline CI job execution | PASS for listed job conclusions only | Does not certify full backtest performance |
| Full CI/backtest acceleration | NOT VERIFIED | Only isolated regression-phase 1.1315x historical observation |
| Kiwoom readonly replica | FAIL | 0 running / 1 crashed |

## Next safe steps
1. Independently fingerprint exact official original filings, correction lineage, timestamp/public available-at and 2021/2022 consolidated three-month periods; document only non-sensitive flags and SHA evidence.
2. Reconcile original official KRX calendar/trading states/corporate actions and historical security mapping, including anomalous OHLC; do not admit zero activity as tradable.
3. Inspect Kiwoom readonly crashed replica diagnosis/logs without restart or config/deployment changes. Distinguish deployment success from runtime health.
4. In isolated optimization scope, audit offline-only cache provenance and read-only parallel post-processing parity; avoid new market/economic experiments. Preserve frozen gates and M20 NO-GO.
5. Only after independent PIT admission and separate explicit approvals consider a single frozen M20 economic evaluation. No automatic promotion, order or deployment.
