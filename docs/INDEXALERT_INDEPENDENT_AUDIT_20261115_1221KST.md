# IndexAlert independent audit — 2026-11-15 12:21 KST

## Scope and immutable boundaries
Read-only GitHub PRs #412/#413/#414/#418/#420/#422/#423, designated Actions and Railway production. No official market performance run, optimization search, deployment, workflow mutation, merge, order, account/credential change or Champion promotion. Frozen H5/M20 horizon20/purge20/WF504-126-126, independent holdout, Top3/NO_TRADE, costs/taxes and ORDERING=false unchanged. Separate Work code untouched.

## GitHub verified PR heads (all DRAFT/open/unmerged)
- #412 bf3d9514a87c53b1775e22ec9ba7711f6cecc49f
- #413 f003ef6247e16fcc71bd3b1b20cd4904c4d984c0
- #414 18c5418d9684d1717df58261ea27f28e514385b2
- #418 2f98401cc50a6c6a25808a98516efd5bf0c944ee
- #420 fab3cbbd63a951a4e081f9e7f08c1391ca308581
- #422 c14857620973531013799e44625d43080904fd5f
- #423 0e38004363cac9fc4475556b3a1c445de9af407f
- Research branch last independently reported df474df348f22aa38b1dedaa59fcff66e548b406; development branch last reported 1e6367d2863a86c3470da13d81a955d277eba485. **Current branch tip NOT VERIFIED in this run** (branch search lists names, not tip SHAs).
- PR #414 gate blob SHA-1 984c933651f39f1ee9e26a1d7ac3893aaa5335be, fetched from PR branch. This is a Git blob identifier, not independent original source approval.

## Actions
- 38381997417: 6/6 SUCCESS; 38382214223: 6/6 SUCCESS; 38419111311: 6/6 SUCCESS; 38419649711: 1/1 SUCCESS; OpenDART 38419439742: 2/2 SUCCESS. Historical 34-case fixed SHA-256 5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34 reported in prior CI; **fresh independent recomputation NOT VERIFIED**.
- 38486028854 job 115599778959 **FAIL**: source gate research_v1_runtime_manifest.py expected Git blob SHA-1 108f66714602a1bd3ae42c34dcca7c16e38f460b, observed e428789e2e97ca7be3a4482e0df23b483a1ad69d. SourceDriftError before parity/equivalence tests. Do not bypass by altering expected hash without source provenance. CI URL https://github.com/kims34/openpilot-opkr/actions/runs/38486028854
- Single-runner previously measured regression phase serial 2.9656s vs concurrent 2.6209s = 1.1315x; whole CI / approved real PIT backtest speed **NOT VERIFIED**.

## Railway production read-only evidence
Project d1c1a050-b7d6-41ce-b300-13c20f82a20a, production 83d5840b-270e-4d3f-a941-a37fd4a55ff7.
- PIT rebuild 8b354fc1-cfb2-4ef0-863e-67f7f5dda2b5 SUCCESS, replicas 1/1; runtime eaaa9f67-b9f2-41d2-832c-7d6fad9b9b00 SUCCESS, replicas 1/1.
- KRX worker 16c93d7c-7cd0-4d84-a327-298d2805376c SUCCESS, replicas 0/1 (online service classification does NOT prove active replica).
- backend and push OFFLINE; db-query-readonly OFFLINE with 1 critical warning.
- pending staged environment patch e113dacb-6705-4416-9997-dc694539d382 since 2026-10-29T06:20:53Z; no deployment authorized.
- Read-only deploy logs 2026-11-15 02:15–03:25 UTC: PIT 0 entries, KRX 0 entries, runtime 101 entries returned (limit 100 per stream). At 03:21:43Z runtime reported Investing USD/KRW HTTP errors and Yahoo fallback; this is a runtime quote source fallback, **not** official historical KRX/PIT approval.

## Independent admission decisions
- 2017–2022 1565/1565 weekday raw KRX pair persistence: historical storage integrity PASS per prior evidence; official exchange calendar, trade state, corporate actions, fills, cost/tax: NOT VERIFIED; 90 uncertain sessions, 12003 zero-activity records fail-closed.
- OpenDART original/correction candidate row matching: previous source-level evidence PASS only; 2021/2022 first-filed standalone 3-month consolidated operating profit, correction lineage, public available-at/PIT, historical issuer/security mapping: NOT VERIFIED.
- M20 original-filing PIT, label/purge/CPCV/holdout admission: NOT VERIFIED / NO-GO.
- NetEV, PF, CAGR, MDD, ES95/99, concentration, date-cluster robustness, post-tax annual risk-adjusted net profitability: NOT VERIFIED / NO-GO, no economic run authorized.
- PR #413 offline CI regression PASS (specified jobs), PR #418 archived source integrity gate FAIL; cache fail-closed and independent read-only postprocessing only. Full CI and real backtest acceleration NOT VERIFIED.

## Next safe steps
1. Owner of #418 independently compare the expected vs observed archived Git blob contents and commit lineage, document legitimate source provenance; do not bypass source gate or modify workflows.
2. OpenDART owner furnish original-filing period/available-at/correction evidence for both 2021 and 2022.
3. KRX owner furnish official calendar/trade state/corporate action and fill/cost/tax provenance, resolving uncertain/zero-activity without selective exclusions.
4. Only after independent SHA/CI/PIT/source PASS, reconsider a separately approved frozen M20 run. No promotion or live trading.
