# Independent profitability/runtime audit — 2026-11-05 17:25 KST

Scope: read-only GitHub PR metadata and Actions job conclusions; Railway production service state and logs. Separate audit branch based on PR #414 HEAD, no edits to owner branches. No M20/market performance run.

## Exact GitHub PR HEAD (all OPEN/Draft)
- #412: `bf3d9514a87c53b1775e22ec9ba7711f6cecc49f`
- #413: `f003ef6247e16fcc71bd3b1b20cd4904c4d984c0`
- #414: `18c5418d9684d1717df58261ea27f28e514385b2`
- #418: `2f98401cc50a6c6a25808a98516efd5bf0c944ee`
- #420: `fab3cbbd63a951a4e081f9e7f08c1391ca308581`
- #422: `c14857620973531013799e44625d43080904fd5f`
- #423: `0e38004363cac9fc4475556b3a1c445de9af407f`

Research branch `index-alert-research-v1` and development branch `index-alert-position-regen-fix-v1`: exact current HEAD **NOT VERIFIED** this run. PR HEAD must not be substituted for branch HEAD.

## GitHub Actions (jobs queried in this run)
- 38381997417: 6/6 success
- 38382214223: 6/6 success
- 38419111311: 6/6 success
- 38466023642: 6/6 success
- 38419649711: 1/1 success (single-runner)
- 38419439742: 2/2 success (OpenDART)
- 41515392296: auto-anchor FAILURE; validation SKIPPED.
Prior 34-case SHA `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34`, 13 adversarial mocks, 28 synthetic cases and serial 2.9656s vs concurrent 2.6209s = 1.1315x are historical evidence **not independently rehashed/rebenchmarked this run**. Full CI and official backtest speed NOT VERIFIED.

## Railway production live state
Project `d1c1a050-b7d6-41ce-b300-13c20f82a20a`; environment `83d5840b-270e-4d3f-a941-a37fd4a55ff7`.
- PIT rebuild SUCCESS deployment `8b354fc1-cfb2-4ef0-863e-67f7f5dda2b5`, replicas running 1/1.
- KRX historical worker SUCCESS deployment `16c93d7c-7cd0-4d84-a327-298d2805376c`, replicas running 0/1.
- Runtime SUCCESS deployment `eaaa9f67-b9f2-41d2-832c-7d6fad9b9b00`, replicas running 1/1. Recent runtime log at 2026-11-05T08:25:46Z reports USD/KRW Yahoo Finance quote with ECOS basis; not independent PIT provenance.
- Logs since 2026-11-05T06:00Z: KRX 0, PIT rebuild 0; absence of logs is not a successful source audit.
- Kiwoom REAL readonly state displays online but replica running 0/crashed 1. Push offline 1 warning; backend offline 4 warnings; db-query-readonly offline 1 critical.
- Staged Railway patch `e113dacb-6705-4416-9997-dc694539d382` untouched.

## Gate decision
- OpenDART original filing, actual public available-at, 2021/2022 first-quarter consolidated operating-income period/correction lineage: **NOT VERIFIED**. Historical SGML 15 candidate rows and numeric adjacency signatures do not establish semantics/timing.
- Official KRX 2017–2022 1565/1565 weekday private raw-pair integrity: historical storage PASS only; official session calendar, trading state, corporate actions, historical issuer/security mapping, fillability: **NOT VERIFIED**. 90 uncertain dates and 12003 zero-activity records remain blocked.
- Transaction costs/taxes and independent annual risk-adjusted NetEV/PF/CAGR/MDD/ES95/ES99/concentration/temporal robustness: **NOT VERIFIED**.
- M20: **NOT EVALUABLE / NO-GO**; no official profitability test. H5 failed/consumed holdout cannot be reused. ORDERING=false. Frozen H5; M20 horizon20/purge20, WF504/126/126, Purged/CPCV/independent holdout/Champion/Top3/NO_TRADE unchanged.
- Cache fail-closed only on independently approved source/data/code/Frozen/runtime/evidence SHA-256 equality; only read-only independent post-processing parallelizable. No dependent retraining or capital transitions parallelized.

## Next permitted steps
1. Independently resolve exact research/development HEAD and official OpenDART original-filing/public timestamp lineage.
2. Independently reconcile KRX private raw dates with official exchange calendar/trading status and corporate actions, without releasing quarantined data.
3. Audit optimization offline synthetic parity and end-to-end CI timing without new market experiments.
4. Do not edit workflows, merge PRs, deploy, change accounts, order, promote Champion or run M20 until distinct explicit approval and source gates.
