# IndexAlert independent audit — 2026-11-16 04:21 KST

Scope: read-only GitHub/Railway verification, no official-market performance run, no deployment, no merge, no ordering, no policy change. Independent audit branch based on prior audit commit `fd974b5513f012dfce8726297f38ae2ebaff3d65`.

## GitHub evidence
- Research branch `index-alert-research-v1` and development branch `index-alert-position-regen-fix-v1` exist (branch search). **Exact current HEAD NOT VERIFIED**; prior reported HEADs `df474df348f22aa38b1dedaa59fcff66e548b406` and `1e6367d2863a86c3470da13d81a955d277eba485` must not be treated as current without branch-ref evidence.
- PR #414 gate document fetched from `refs/pull/414/head`; original PIT and market readiness explicitly blocked. PR #412/#413/#418 and KRX #420/#422/#423 current draft/merge state and exact HEADs **NOT VERIFIED** in this execution (GitHub issue search yielded zero; do not infer closure).
- Actions [38381997417](https://github.com/kims34/openpilot-opkr/actions/runs/38381997417) 6/6 success; [38382214223](https://github.com/kims34/openpilot-opkr/actions/runs/38382214223) 6/6 success; [38419111311](https://github.com/kims34/openpilot-opkr/actions/runs/38419111311) 6/6 success; [38419439742](https://github.com/kims34/openpilot-opkr/actions/runs/38419439742) 2/2 success; [38419649711](https://github.com/kims34/openpilot-opkr/actions/runs/38419649711) 1/1 success. These are software/row-candidate checks, NOT original filing semantics or economic PASS.
- [38486028854](https://github.com/kims34/openpilot-opkr/actions/runs/38486028854) job 115599778959 **FAIL**: `research_v1_runtime_manifest.py` expected Git blob SHA-1 `108f66714602a1bd3ae42c34dcca7c16e38f460b`, observed `e428789e2e97ca7be3a4482e0df23b483a1ad69d`; downstream regression not reached. Do not bypass source drift guard.
- Prior 34-case identity SHA-256 `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34` is historic evidence only; independent rehash this execution NOT VERIFIED. Prior single runner 2.9656s vs concurrent 2.6209s (1.1315x regression-phase), full CI / official backtest speed NOT VERIFIED.

## Railway production evidence
- Project `d1c1a050-b7d6-41ce-b300-13c20f82a20a`, environment `83d5840b-270e-4d3f-a941-a37fd4a55ff7`.
- Environment inventory staged=null but health status reports pending staged patch `e113dacb-6705-4416-9997-dc694539d382` since 2026-10-29T06:20:53Z: resolution **NOT VERIFIED**.
- PIT rebuild 1/1 running, runtime 1/1 running, historical KRX worker 0/1 running. Historical worker 2026-11-15 18:25–19:25 UTC deploy logs 0 entries; PIT same interval 0 entries. Absence of logs is not recovery.
- Runtime logs in that interval show Investing USD/KRW HTTP errors and Yahoo fallback. These are runtime observations, not source/PIT approvals.
- Previously observed KRX 2026-09-28 OHLC anomaly 27/803 and fail-closed remain unresolved; **current 27/803 status NOT VERIFIED** without fresh source evidence. Historical 2017–2022 weekday pairs 1565/1565 stored SHA PASS as previously documented, official calendar/trading eligibility NOT VERIFIED.

## Gate decisions
- Original-filing SGML 15 operating-profit candidate rows: historical shape/signature PASS only; 2021/2022 first three-month consolidated operating-profit exact period, correction lineage and public available-at **NOT VERIFIED**.
- Historical corp/security mapping, official KRX sessions/status/corporate actions, fills and taxes/costs: **NOT VERIFIED**.
- Independent after-cost-and-tax NetEV, PF, CAGR, MDD, ES95/99, concentration, temporal robustness: **NOT VERIFIED**. H5 archive/consumed holdout NO-GO; M20 performance RUN **NOT AUTHORIZED**.
- Optimization isolated offline software checks PASS for the historical jobs above, integrated manifest gate FAIL, end-to-end speed NOT VERIFIED.
- Frozen H5 and M20 horizon20/purge20 WF504/126/126, PIT/label/Purged/CPCV/holdout/Champion/Top3/NO_TRADE unchanged; ORDERING=false; no live trades, transfer, permission changes, Champion promotion, production deploy, workflow changes or PR merges.

Next: independent original filing available-at + 2021/22 three-month consolidated lineage; official KRX 27 anomalies and trade status SHA; isolate PR #418 manifest drift with authorized source owners (never relax pinned digest); independently rehash fixed 34 cases only in offline isolated environment. No economic experiments before source/PIT PASS.
