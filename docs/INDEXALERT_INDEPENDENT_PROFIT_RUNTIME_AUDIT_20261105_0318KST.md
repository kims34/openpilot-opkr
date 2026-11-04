# IndexAlert independent profit/runtime audit — 2026-11-05 03:18 KST

Scope: read-only evidence, synthetic-only optimization. This document records directly observed evidence versus historical claims. No economic M20 run, order, deployment, merge, workflow or policy change.

## GitHub Actions directly checked
- 38381997417: 6/6 success; 38382214223: 6/6 success; 38419111311: 6/6 success.
- 38419649711: 1/1 success; 38419439742: 2/2 success.
- Chronology anchor 41515392296: auto-anchor failure, validation skipped. Chronology source remains blocked.
- Historical fixed 34-case SHA-256 5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34, 13 adversarial mocks, 28 synthetic cases, serial 2.9656 s vs suite 2.6209 s (1.1315x regression phase): not independently recalculated this run. Full CI/official backtest speedup NOT VERIFIED.
- Branch search confirms index-alert-backtest-runtime-opt-v1-20261013 and index-alert-backtest-single-runner-opt-v1-20261013 exist; current HEAD not resolved. PR search returned no items, so current PR HEAD and Draft status NOT VERIFIED. Prior PR HEADs are historical only: #413 f003ef6247e16fcc71bd3b1b20cd4904c4d984c0; #414 18c5418d9684d1717df58261ea27f28e514385b2; #418 2f98401cc50a6c6a25808a98516efd5bf0c944ee. Research/dev HEAD NOT VERIFIED this run.
- Integration gate file lookup at index-alert-research-v1 returned 404; do not interpret as deletion from PR #414.

## Railway directly checked
Project d1c1a050-b7d6-41ce-b300-13c20f82a20a. Environment inventory: KRX historical worker latest deployment SUCCESS (2026-10-12 13:07 UTC), PIT rebuild SUCCESS (2026-10-10 10:28 UTC), runtime SUCCESS (2026-10-05 20:34 UTC). Push/backend latest deployments FAILED from 2026-09-23. No pending patch in environment inventory this run (prior staged-patch assertion not reconfirmed).
- 2026-11-04 17:30–18:20 UTC: KRX worker and PIT rebuild deploy logs 0, Kiwoom real readonly deploy logs 0. Runtime logs present through 18:18 UTC, index and USD/KRW quote/fallback only. Absence of logs does not establish recovery, approval or service health.
- Prior Kiwoom replica crash inconsistency was not independently rechecked in this run. Latest deployment SUCCESS alone does not prove running replica health.

## Independent source/economics gates
- Historical private weekday raw-pair storage integrity 1565/1565 PASS only for storage evidence; official KRX calendar/trading state/corporate actions/fillability NOT VERIFIED.
- Original-filing semantics and exact public available-at, 2021/2022 initial 3-month consolidated operating-profit period and correction lineage, historical issuer/security mapping NOT VERIFIED.
- NetEV/PF/CAGR/MDD/ES95/ES99, tax/fee/slippage and concentration/stability NOT VERIFIED. M20 NOT EVALUABLE / NO-GO. Chronology anchor FAIL.
- Frozen H5, M20 horizon20/purge20, WF504/126/126, PIT/label/Purged/CPCV/independent holdout/Champion/Top3/NO_TRADE unchanged. ORDERING=false. No reuse of consumed H5 holdout/Dynamic results.
- Optimization gate: fail-closed cache only with independent approved source/data/code/Frozen/runtime/evidence SHA-256; parallelize read-only postprocessing only; dependent training/capital transitions serial. Synthetic-only policy tests permitted, no market return/performance experiment before PIT approval.

## Next safe checks
Resolve current branch and PR HEAD via independent immutable references; compare approved source manifests and official public timestamps; read official KRX status/corporate-action evidence and CI SHA artifacts. Inspect Kiwoom replica health read-only. Do not run M20 or change deployment/ordering.
