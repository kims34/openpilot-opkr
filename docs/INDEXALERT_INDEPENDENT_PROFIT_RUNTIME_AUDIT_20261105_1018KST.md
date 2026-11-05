# IndexAlert independent profitability/runtime audit — 2026-11-05 10:18 KST

Read-only observations in this run; no official PIT/performance replay.

## GitHub CI evidence (actual jobs API)
- Actions 38381997417: 6/6 jobs SUCCESS; 38382214223: 6/6 SUCCESS.
- 38419111311: 6/6 SUCCESS; 38419649711: 1/1 SUCCESS; 38419439742: 2/2 SUCCESS.
- Chronology anchor 41515392296: auto-anchor FAIL at public hash-only payload fetch, validation SKIPPED.
- 34-case canonical SHA-256 5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34 and serial 2.9656s/concurrent 2.6209s (ratio 1.1315x) are historical user-provided/artifact claims, not independently recomputed in this run. CI job success does not prove speedup or source authority.
- PR #413 body confirms offline-only fail-closed comparator, no live execution; KRX #422/#423 explicitly say private exact date sets not yet audited. GitHub PR search returned #413 and KRX #420/#422/#423; current exact HEAD for research/development and #412/#414/#418 NOT VERIFIED in this run. A fetch of integration document on research branch returned 404; wrong speculative integration branch also 404. Do not infer absence of document on PR #414.

## Railway evidence (actual read-only API)
- Project d1c1a050-b7d6-41ce-b300-13c20f82a20a, production 83d5840b-270e-4d3f-a941-a37fd4a55ff7.
- KRX worker latest SUCCESS deployment from 2026-10-12, commit 1e6367d2863a86c3470da13d81a955d277eba485; PIT rebuild latest SUCCESS from 2026-10-10, commit e57054ecdb3e734ced3c9a981b887d9b5fc60f97.
- Both services deploy logs: zero entries from 2026-11-05 00:00 UTC onward in this query; zero logs is not proof of source/PIT acceptance.
- Runtime log at 2026-11-05 01:16-01:17 UTC shows live USD/KRW Yahoo, QQQ/SPY futures-proxy estimates; these are display data, not admissible historical original filings or official market tradability.

## Gate decisions
- Historical 1565/1565 weekday pair private storage integrity: historical PASS only; independent fresh rehash NOT VERIFIED.
- OpenDART original filing semantic/available-at and 2021/2022 initial three-month consolidated operating-profit correction lineage: NOT VERIFIED.
- KRX exact official session/status, corporate actions, mapping, fillability, costs/taxes: NOT VERIFIED.
- PIT/label/Purged/CPCV/holdout independence and after-cost/tax NetEV, PF, CAGR, MDD, ES95/99, concentration, time stability: NOT VERIFIED.
- Offline CI job completion: PASS for the listed jobs only. Whole CI and full-backtest acceleration: NOT VERIFIED.
- M20: NOT EVALUABLE / NO-GO; ORDERING=false; Frozen H5 and consumed holdout remain sealed.

## Next safe steps
Independently obtain exact PR/branch HEAD and immutable blob SHA, inspect official first-filing public chronology and KRX original historical authority without changing source or Frozen rules. Only offline synthetic fail-closed software/policy tests until source admission. Do not merge, deploy, order, transfer funds, change credentials, run M20 economics or promote Champion. No workflow modification attempted.
