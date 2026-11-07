# IndexAlert independent profitability and runtime audit — 2026-11-07 16:23 KST

Scope: read-only evidence verification; no M20 economics, live trading, deployment, workflow modifications, merges, or Frozen-policy changes. This audit is not a source/PIT approval.

## Exact heads and source
- Research index-alert-research-v1: df474df348f22aa38b1dedaa59fcff66e548b406 (GitHub compare self-ref, identical).
- Development index-alert-position-regen-fix-v1: 1e6367d2863a86c3470da13d81a955d277eba485 (same method).
- PR #412 bf3d9514a87c53b1775e22ec9ba7711f6cecc49f; #413 f003ef6247e16fcc71bd3b1b20cd4904c4d984c0; #414 18c5418d9684d1717df58261ea27f28e514385b2; #418 2f98401cc50a6c6a25808a98516efd5bf0c944ee; KRX #420 fab3cbbd63a951a4e081f9e7f08c1391ca308581; #422 c14857620973531013799e44625d43080904fd5f; #423 0e38004363cac9fc4475556b3a1c445de9af407f. All OPEN, Draft, not merged at read time.
- PR #414 integration gate docs/INDEXALERT_PROFITABILITY_INTEGRATION_GATE_2026-10-13.md blob 984c933651f39f1ee9e26a1d7ac3893aaa5335be, fetched from PR head.
- OpenDART Action 38419439742: 2/2 jobs success; offline single-runner 38419649711: 1/1; runtime optimisation 38498552499: 6/6; chronology anchor 41515392296: auto-anchor FAILURE, validation SKIPPED. These are job-status checks, not independent proof of original-filing semantic PIT or real market returns.
- Previously reported 34-case SHA 5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34 and serial 2.9656s vs parallel 2.6209s remain historical evidence; raw artifact SHA and new performance not independently recalculated in this run.

## Railway production read-only
Project d1c1a050-b7d6-41ce-b300-13c20f82a20a, environment 83d5840b-270e-4d3f-a941-a37fd4a55ff7.
- indexalert-kiwoom-real-readonly deployment a77fb922-b679-4d88-92c4-03054ec579cd SUCCESS but running=0, crashed=1 (total=1): **runtime health FAIL** despite UI Online.
- PIT rebuild deployment 8b354fc1-cfb2-4ef0-863e-67f7f5dda2b5 SUCCESS, running=1/1; runtime eaaa9f67-b9f2-41d2-832c-7d6fad9b9b00 SUCCESS, running=1/1. KRX historical worker deployment 16c93d7c-7cd0-4d84-a327-298d2805376c SUCCESS, running=0/crashed=0/total=1: not proof of currently active ingestion.
- db-query-readonly: Critical=1, offline; backend offline warning=4; push offline warning=1.
- describe_environment staged=null but environment_status pendingWork patch e113dacb-6705-4416-9997-dc694539d382 STAGED with empty changes: API state mismatch, NOT VERIFIED whether material changes exist; do not apply.
- PIT/KRX/real-readonly service deploy logs queried from 2026-11-07 04:00Z; all empty in returned window, no proof of recovery or issue resolution.

## Evidence gate verdicts
PASS (limited): GitHub branch HEAD and PR metadata fetched; listed CI job status; historical KRX 1565/1565 stored pairs from prior evidence (not newly rehashed).
FAIL: chronology anchor auto-anchor job; real-readonly running replica health.
NOT VERIFIED: OpenDART original-filing public available-at, 2021/2022 initial connected 3-month operating profit period/correction lineage, historical corporation/security mapping, official KRX session/halts/corporate actions/executability, 27 OHLC anomalies, transaction costs/tax, M20 NetEV/PF/CAGR/MDD/ES95/99/concentration/date robustness, total CI and real backtest speedups, crashed replica root cause, staged patch interpretation.

## Next safe actions
1. Read failed chronology anchor job logs and its routing/original hash-only artifact without modifying workflows.
2. Inspect real-readonly deployment historical startup/exit logs and replica evidence, do not restart or change credentials.
3. Require independent official original-filing PIT and official KRX state/feasibility gates before authorising any economic M20 run.
4. Optimisation track restricted to synthetic offline equivalence and fail-closed SHA cache safety; parallelise independent read-only postprocessing only. Keep H5 Frozen, M20 horizon20/purge20 WF504/126/126, independent Holdout and Top3/NO_TRADE unchanged. ORDERING=false; no live orders, promotion, merge or deploy.
