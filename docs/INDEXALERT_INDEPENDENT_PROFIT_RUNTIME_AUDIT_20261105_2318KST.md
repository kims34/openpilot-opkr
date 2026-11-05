# IndexAlert independent profitability / offline optimisation audit — 2026-11-05 23:18 KST

## Scope and safety
Read-only inspection of GitHub PRs, Actions and Railway production. This document is the only intended write, isolated from all specialist Work branches. No workflow, production, strategy, capital, credentials, trading, PR merge or deployment changes. ORDERING=false; no M20 economic run. Frozen H5, M20 horizon20/purge20, WF504/126/126, independent holdout, Champion/Top3/NO_TRADE and all economic gates remain unchanged.

## Exact source and PR evidence
Repository: kims34/openpilot-opkr. Previously observed research commit `df474df348f22aa38b1dedaa59fcff66e548b406` and development commit `1e6367d2863a86c3470da13d81a955d277eba485` both resolve via GitHub fetch_commit now; **current branch-tip identity not separately proven**, therefore current branch HEAD = NOT VERIFIED.

All below PRs are OPEN/DRAFT, read directly 2026-11-05:
- #412 OpenDART head `bf3d9514a87c53b1775e22ec9ba7711f6cecc49f`
- #413 offline runtime optimisation head `f003ef6247e16fcc71bd3b1b20cd4904c4d984c0`
- #414 integration head `18c5418d9684d1717df58261ea27f28e514385b2`; document `docs/INDEXALERT_PROFITABILITY_INTEGRATION_GATE_2026-10-13.md` fetched from PR branch, blob SHA `984c933651f39f1ee9e26a1d7ac3893aaa5335be`; document explicitly retains PIT/M20 NO-GO.
- #418 one-runner head `2f98401cc50a6c6a25808a98516efd5bf0c944ee`
- KRX #420 head `fab3cbbd63a951a4e081f9e7f08c1391ca308581`
- KRX #422 head `c14857620973531013799e44625d43080904fd5f`
- KRX #423 head `0e38004363cac9fc4475556b3a1c445de9af407f`

Actions jobs directly inspected (not rerun):
- https://github.com/kims34/openpilot-opkr/actions/runs/38381997417 6/6 success
- https://github.com/kims34/openpilot-opkr/actions/runs/38382214223 6/6 success
- https://github.com/kims34/openpilot-opkr/actions/runs/38419111311 6/6 success
- https://github.com/kims34/openpilot-opkr/actions/runs/38419649711 1/1 success
- https://github.com/kims34/openpilot-opkr/actions/runs/38419439742 2/2 success
- https://github.com/kims34/openpilot-opkr/actions/runs/41515392296 failure 1, skipped 1
- Historical fixed 34-case test SHA `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34`, 13 adversarial mocks, 28 synthetic tests and serial 2.9656 s / concurrent 2.6209 s (1.1315x regression-phase) are **previously reported, not independently rehashed or retimed in this pass**. End-to-end CI and official backtest acceleration NOT VERIFIED.

## Railway production read-only
Project `d1c1a050-b7d6-41ce-b300-13c20f82a20a`, environment `83d5840b-270e-4d3f-a941-a37fd4a55ff7`; staged patch null. Latest deployment statuses: PIT rebuild SUCCESS, KRX historical worker SUCCESS, runtime SUCCESS, backend FAILED, push FAILED; deployment success does not prove replica health. PIT rebuild logs queried from 12:00 UTC: 10 periodic entries through **2026-11-05 14:16:29 UTC (23:16:29 KST)**. Latest entry: `KRXProspectiveOpenAPISourceError` / `COMMON_OHLC_NONPOSITIVE`, 803 common-stock rows, 27 nonpositive OHLC, 27 zero volume/value; `fresh_alpha_observation_admitted=false`, independent source/model/chronology admission false, `ordering=DISABLED`. Safety fail-closed PASS; candidate market-session admission FAIL. KRX worker log query from 12:00 UTC returned zero entries; absence of new logs does not prove correctness. No service config or runtime modifications.

## Gate decision
- Private 2017–2022 1565/1565 weekday raw-pair SHA storage integrity: historical PASS, not independently rehashed this run.
- 90 unclassified historical sessions, 12003 zero-activity records, prospective 27 invalid OHLC: official trading calendar, status, corporate actions and fillability NOT VERIFIED / admission blocked.
- OpenDART first filing, exact public available-at/PIT, 2021/2022 first three-month consolidated operating profit and amendment lineage: NOT VERIFIED. Candidate SGML numeric adjacency is not economic/temporal approval.
- Historical company-security mapping, commissions, slippage, taxes, realistic execution: NOT VERIFIED.
- NetEV, PF, CAGR, MDD, ES95/99, concentration, walk-forward robustness and independent annual risk-adjusted after-tax net profitability: NOT VERIFIED, not evaluated.
- Chronology Anchor CI: FAIL. M20 PIT and profitability: NO-GO / NOT EVALUABLE. No H5/holdout reuse.
- Offline optimisation CI jobs: PASS at job-conclusion level only. SHA-safe cache requires approved independent original/data/code/Frozen/runtime/evidence SHA256; read-only postprocessing parallel only. No dependent training/capital transition parallelism.

## Next safe work
1. Independently resolve exact live research/development branch tips and compare to cited commits; preserve isolation.
2. Inspect Chronology Anchor failing step and PR #413/#418 detailed job logs, synthetic identity hashes, and end-to-end CI wall time without new economic experiments.
3. Have KRX specialist reconcile 27 anomalous rows and 90 sessions against exact official historical session/tradability evidence; do not override fail-closed.
4. Have DART specialist establish original filing/public availability and 2021/2022 period/amendment lineage; only after independent approvals consider a separately authorised M20 run.
