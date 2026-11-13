# IndexAlert independent audit — 2026-11-14 07:17 KST

Scope: independent read-only GitHub/Railway evidence, offline-only software optimisation. No PIT source approval, economic backtest, trading, deployment, merge, or promotion.

## Exact GitHub source identity (freshly queried)
- Research `index-alert-research-v1`: compare base `df474df348f22aa38b1dedaa59fcff66e548b406` vs branch: identical, ahead=0, behind=0.
- Development `index-alert-position-regen-fix-v1`: compare base `1e6367d2863a86c3470da13d81a955d277eba485` vs branch: identical, ahead=0, behind=0.
- PR #412: `bf3d9514a87c53b1775e22ec9ba7711f6cecc49f`; #413: `f003ef6247e16fcc71bd3b1b20cd4904c4d984c0`; #414: `18c5418d9684d1717df58261ea27f28e514385b2`; #418: `2f98401cc50a6c6a25808a98516efd5bf0c944ee`; KRX #420: `fab3cbbd63a951a4e081f9e7f08c1391ca308581`; #422: `c14857620973531013799e44625d43080904fd5f`; #423: `0e38004363cac9fc4475556b3a1c445de9af407f`. All open, Draft, unmerged.
- PR #414 integration gate file `docs/INDEXALERT_PROFITABILITY_INTEGRATION_GATE_2026-10-13.md` Git blob SHA-1 `984c933651f39f1ee9e26a1d7ac3893aaa5335be`, read from `refs/pull/414/head`.

## GitHub Actions latest-attempt job states (historical run IDs, refreshed)
- https://github.com/kims34/openpilot-opkr/actions/runs/38381997417 6/6 PASS.
- https://github.com/kims34/openpilot-opkr/actions/runs/38382214223 6/6 PASS.
- https://github.com/kims34/openpilot-opkr/actions/runs/38419111311 6/6 PASS.
- https://github.com/kims34/openpilot-opkr/actions/runs/38419649711 1/1 PASS.
- https://github.com/kims34/openpilot-opkr/actions/runs/38419439742 2/2 PASS.
- https://github.com/kims34/openpilot-opkr/actions/runs/38486028854 1/1 FAIL. Archived regression manifest mismatch remains a blocker; no successful subsequent integration evidence in this set.
- Historical fixed 34-case digest claimed `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34`; **independent recomputation this run NOT VERIFIED**. Single-runner 2.9656s vs simultaneous 2.6209s = 1.1315x regression-phase only (historical), overall CI / real official backtest acceleration NOT VERIFIED.

## Railway production (fresh environment status)
- Project `d1c1a050-b7d6-41ce-b300-13c20f82a20a`, production `83d5840b-270e-4d3f-a941-a37fd4a55ff7`.
- PIT rebuild 1/1 running, runtime 1/1 running; KRX historical worker 0/1, Kiwoom real-readonly-run 0/1 despite SUCCESS deployment states. Backend, push, db-query-readonly offline.
- Pending staged environment patch `e113dacb-6705-4416-9997-dc694539d382` since 2026-10-29 remains. Not applied.
- 2026-11-13 21:10–22:18 UTC runtime deploy logs: 201 returned (limit 200, response count 201), recurring Investing USD/KRW HTTPError -> Yahoo fallback; at 22:17:43 UTC. PIT rebuild and KRX historical worker each returned zero logs for this window. Zero logs is not proof of data recovery.
- Historical 27/803 abnormal OHLC and 12,003 zero-activity exclusions have **no new clearing evidence**.

## Independent profitability and optimisation gates
- OpenDART 2021/2022 first-filed 3-month consolidated operating income, correction lineage, true public available-at and PIT: **NOT VERIFIED**. Candidate-row signature match does not establish public timestamp or semantic approval.
- Historical issuer/security mapping, official KRX calendar, trading status, corporate actions, fillability, costs/tax: **NOT VERIFIED**. 1565/1565 private raw weekday-pair storage integrity was historically PASS, not trading PIT approval.
- After-cost/tax NetEV, PF, CAGR, MDD, ES95/99, return concentration and time robustness: **NOT VERIFIED / M20 NO-GO**. H5 consumed holdout cannot be reused.
- Optimisation: offline synthetic software checks PASS only for specified historical successful jobs; PR #418 integrated check FAIL. Cache must fail closed unless independent source/data/code/Frozen/runtime/approval SHA-256 all match. Parallelise read-only postprocessing only, never dependent refits/capital transition.
- Frozen H5; M20 horizon20/purge20; WF504/126/126; PIT/label/Purged/CPCV/holdout/champion/Top3/NO_TRADE; all risk/cost/tax and promotion gates unchanged. ORDERING=false policy retained; no fresh runtime variable inspection claimed.
- No real market profitability experiments, model search, live orders, money transfers, account/auth changes, Champion promotion, production deploy, or PR merge.

## Next safe independent actions
1. Owner of PR #418 should resolve archived manifest blob mismatch in their own isolated workspace, then run approved offline-only regression and independently reproduce 34-case SHA-256; do not alter another Work's code.
2. Obtain immutable official first-filing public timestamp/period/correction lineage and KRX trading-state/corporate-action/fillability source evidence before any M20 PIT or economics admission.
3. Investigate dormant KRX 0/1 replica and outstanding staged patch via read-only evidence only; no staged change acceptance.
