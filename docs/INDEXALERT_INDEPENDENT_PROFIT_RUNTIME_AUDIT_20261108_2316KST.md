# IndexAlert independent audit — 2026-11-08 23:16 KST

## Scope and immutable policy
Read-only verification of GitHub and Railway; no economic backtest, Holdout reuse, source admission, model search, deployment, workflow modification, trading, promotion or merge. Frozen H5 and M20 horizon20/purge20, WF504/126/126, PIT/CPCV/independent Holdout, costs and taxes unchanged. ORDERING=false; M20 NO-GO.

## GitHub provenance checked this run
- Research `index-alert-research-v1`: comparison against `df474df348f22aa38b1dedaa59fcff66e548b406` returned **identical** (0 ahead/behind).
- Development `index-alert-position-regen-fix-v1`: comparison against `1e6367d2863a86c3470da13d81a955d277eba485` returned **identical**.
- Branch `indexalert-independent-audit-20261108-1921kst` exists. PR #414 and #418 found via GitHub PR search; full current draft/head metadata of all seven PRs **NOT VERIFIED** this run.
- Actions 38381997417, 38382214223, 38419111311: six jobs each success; 38419649711: one job success; 38419439742: two jobs success. 41515392296: auto-anchor failure, validation skipped. These are existing run IDs, not new run evidence. 34-case identity SHA `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34` and 2.9656s vs 2.6209s not independently recomputed this run. No whole-CI or official-backtest speedup admission.

## Railway production evidence
Project `d1c1a050-b7d6-41ce-b300-13c20f82a20a`, environment `83d5840b-270e-4d3f-a941-a37fd4a55ff7`. PIT rebuild and Runtime: running 1/1 each. Real-readonly service: UI online/deploy SUCCESS but replicas running 0, crashed 1. db-query-readonly offline, critical 1; backend and push offline. Empty staged patch still present, not touched.
PIT deploy logs at 2026-11-08 21:00–22:45 KST repeatedly report `KRXProspectiveOpenAPISourceError / COMMON_OHLC_NONPOSITIVE`, source_failure_session=2026-09-28, common_stock_rows=803, nonpositive_ohlc_rows=27, zero_volume_value_rows=27, status=FAIL_CLOSED, ordering=DISABLED, fresh_alpha_observation_admitted=false, session_manifest_sha256=null. This is a repeated old-session failure, not new official session validation. KRX historical worker returned no deploy logs in requested period.

## Independent gate judgments
- Historical KRX 1565/1565 weekday pair storage integrity: historical PASS claim, not rehashed this run. Official trading calendar, states, corporate actions, fillability, fees and tax: **NOT VERIFIED**.
- OpenDART 15 candidate-row signatures: historical candidate evidence only; original filing semantics, public available-at and 2021/2022 consolidated first 3-month operating-income period/correction lineage: **NOT VERIFIED**.
- Historical corporate/security mapping and PIT chronology: **NOT VERIFIED**; chronology anchor job **FAIL**.
- NetEV, PF, CAGR, MDD, ES95/99, return concentration and time-slice robustness after executable costs/taxes: **NOT VERIFIED**. M20 **NO-GO**.
- Offline optimization job outcomes: **PASS for job execution only**. Exact frozen suite parity SHA not rehashed this run; whole-CI and official economic acceleration **NOT VERIFIED**.

## Next safe steps
Independent source owners must produce immutable official original-filing/available-at/lineage receipts, historical mapping and official KRX session/tradability/corporate-action evidence with SHA-256 and CI logs. Resolve chronology anchor provenance failure, then independently recheck admission gates; do not start M20 before explicit authorization. Independently diagnose real-readonly crashed replica without modifying production or permissions. Preserve fail-closed cache binding and serial dependent phases; only read-only post-processing may parallelize. Do not reuse consumed H5 Holdout.
