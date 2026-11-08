# IndexAlert independent profitability / offline runtime audit — 2026-11-08 09:20 KST

Scope: independent read-only GitHub/Railway verification, documentation-only isolated branch. This audit does not authorize economic backtests, deployment, merges, trading or policy changes. Prior evidence and current direct observations are distinguished.

## Current exact GitHub references (direct API reads)
- Research `index-alert-research-v1`: `df474df348f22aa38b1dedaa59fcff66e548b406`.
- Development `index-alert-position-regen-fix-v1`: `1e6367d2863a86c3470da13d81a955d277eba485`.
- All OPEN, Draft, unmerged: [OpenDART #412](https://github.com/kims34/openpilot-opkr/pull/412) `bf3d9514a87c53b1775e22ec9ba7711f6cecc49f`; [optimization #413](https://github.com/kims34/openpilot-opkr/pull/413) `f003ef6247e16fcc71bd3b1b20cd4904c4d984c0`; [integration #414](https://github.com/kims34/openpilot-opkr/pull/414) `18c5418d9684d1717df58261ea27f28e514385b2`; [one-runner #418](https://github.com/kims34/openpilot-opkr/pull/418) `2f98401cc50a6c6a25808a98516efd5bf0c944ee`; [KRX #420](https://github.com/kims34/openpilot-opkr/pull/420) `fab3cbbd63a951a4e081f9e7f08c1391ca308581`; [KRX #422](https://github.com/kims34/openpilot-opkr/pull/422) `c14857620973531013799e44625d43080904fd5f`; [KRX #423](https://github.com/kims34/openpilot-opkr/pull/423) `0e38004363cac9fc4475556b3a1c445de9af407f`.
- Integration gate `docs/INDEXALERT_PROFITABILITY_INTEGRATION_GATE_2026-10-13.md` at #414 head: Git blob SHA `984c933651f39f1ee9e26a1d7ac3893aaa5335be`. The PR bases are not necessarily the current research HEAD.

## Actions checked directly (job status, not independent artifact digest recomputation)
- [38381997417](https://github.com/kims34/openpilot-opkr/actions/runs/38381997417), [38382214223](https://github.com/kims34/openpilot-opkr/actions/runs/38382214223), [38419111311](https://github.com/kims34/openpilot-opkr/actions/runs/38419111311), [38498552499](https://github.com/kims34/openpilot-opkr/actions/runs/38498552499): each 6/6 jobs success.
- [38419649711](https://github.com/kims34/openpilot-opkr/actions/runs/38419649711): 1/1 job success; [38419439742](https://github.com/kims34/openpilot-opkr/actions/runs/38419439742): 2/2 jobs success.
- [41515392296](https://github.com/kims34/openpilot-opkr/actions/runs/41515392296): auto-anchor FAILURE, validation SKIPPED.
- Historical 34-case identity SHA `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34`, 13 adversarial and 28 synthetic cases, and one-runner 2.9656s vs 2.6209s are prior attested evidence; NOT independently recalculated this run. Software parity PASS only at previously recorded scope. Full official backtest acceleration NOT VERIFIED.

## Railway production directly checked
Project `d1c1a050-b7d6-41ce-b300-13c20f82a20a`, production `83d5840b-270e-4d3f-a941-a37fd4a55ff7`. Environment stagedChanges=null, but pendingWork includes empty staged patch `e113dacb-6705-4416-9997-dc694539d382` (changes=[]). These two surfaces differ and are not interpreted as a deploy authorization. Latest deployments: PIT rebuild `8b354fc1-cfb2-4ef0-863e-67f7f5dda2b5` SUCCESS; KRX worker `16c93d7c-7cd0-4d84-a327-298d2805376c` SUCCESS; real readonly `a77fb922-b679-4d88-92c4-03054ec579cd` SUCCESS; runtime `eaaa9f67-b9f2-41d2-832c-7d6fad9b9b00` SUCCESS; backend and push latest FAILED. Replica fields were null, so live replica health NOT VERIFIED. PIT, KRX and real-readonly deploy logs from 2026-11-08 08:00 KST onward returned zero entries, not evidence of remediation. No new deployments or runtime writes.

## PASS / FAIL / NOT VERIFIED gates
- KRX 2017–2022 1565/1565 weekday private stored pairs: **PASS only for previously attested storage integrity**; official session calendar, 90-day gap classification, 12003 zero-activity records, corporate actions, delist/suspend, tradeable market state, executable lots, historical corporate/security mapping: **NOT VERIFIED**, retain fail-closed.
- OpenDART original ZIP/SGML candidate extraction: **PASS only for previously attested byte/candidate checks**; 2021/2022 exact first-filed 3-month consolidated operating-profit fact, correction lineage, public available-at and full PIT: **NOT VERIFIED / FAIL-CLOSED**. No backfill from amendments.
- Chronology anchor workflow: **FAIL** at auto-anchor; validation **SKIPPED**.
- Previously archived H5 concentration/date-LCB and consumed Holdout: **NO-GO**, never repurpose as independent Holdout. Frozen H5 and M20 policy unchanged.
- M20 horizon20/purge20, WF504/126/126, PIT, Purged/CPCV, independent Holdout, Champion/Top3/NO_TRADE, cost/tax/execution/risk and promotion criteria: **NOT VERIFIED for live-source M20**; M20 economic RUN **NOT AUTHORIZED**.
- NetEV/PF/CAGR/MDD/ES95/99, concentration, date robustness, tax-inclusive annual risk-adjusted net profit: **NOT VERIFIED**. No market-return generation or new model search.
- Optimization: synthetic offline CI **PASS at jobs level**, speedup of entire official evaluation **NOT VERIFIED**. Cache requires independently approved source/data/code/Frozen/runtime/evidence SHA-256 match, fail-closed; only independent read-only postprocessing parallelism. No dependent training or capital transitions parallelized.
- ORDERING=false, no live orders, funds, credentials, Champion promotion, merge or production deploy.

## Next evidence-only actions
DART owner must independently pin exact original filing, Q3 3-month CFS fact and public timestamp/lineage; KRX owner must prove official market status and executable prices/corporate actions; chronology owner must repair failed anchor in its own isolated scope with original SHA; optimization owner may run synthetic-only parity/security tests without changing frozen economics. Recheck SHA/CI/deploy and logs next scheduled run. Do not edit other Work code or blocked GitHub workflows.
