# IndexAlert independent profitability/runtime audit — 2026-11-05 07:20 KST

Scope: read-only GitHub/Railway verification; no PIT source approval, economic run, code/workflow modification, merge, deployment, order, or policy change. Previous independent branch reused, new uniquely named document only.

## GitHub evidence (observed this run)
- Research branch index-alert-research-v1 and development branch index-alert-position-regen-fix-v1: branch existence verified by search; **current commit HEAD not independently resolved**. Prior historical SHAs df474df348f22aa38b1dedaa59fcff66e548b406 and 1e6367d2863a86c3470da13d81a955d277eba485 are NOT current HEAD attestations.
- Draft OPEN PR #412 head bf3d9514a87c53b1775e22ec9ba7711f6cecc49f; #413 f003ef6247e16fcc71bd3b1b20cd4904c4d984c0; #414 18c5418d9684d1717df58261ea27f28e514385b2; #418 2f98401cc50a6c6a25808a98516efd5bf0c944ee; KRX #420 fab3cbbd63a951a4e081f9e7f08c1391ca308581, #422 c14857620973531013799e44625d43080904fd5f, #423 0e38004363cac9fc4475556b3a1c445de9af407f. All draft/open at query time, no merge.
- PR #414 gate file docs/INDEXALERT_PROFITABILITY_INTEGRATION_GATE_2026-10-13.md blob SHA-1 984c933651f39f1ee9e26a1d7ac3893aaa5335be verified from GitHub fetch.
- Actions https://github.com/kims34/openpilot-opkr/actions/runs/38381997417 and /38382214223: each 6/6 jobs SUCCESS; /38419111311 6/6 SUCCESS; /38419649711 1/1 SUCCESS; /38419439742 2/2 SUCCESS. Chronology /41515392296 auto-anchor FAILURE and validation SKIPPED. These are job status observations, not independent original-filing PIT or real performance approval.
- Prior synthetic 34-case digest 5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34, 13 adversarial mocks, 28 synthetic cases, serial 2.9656s vs parallel 2.6209s (1.1315x regression phase) are HISTORICAL, not recomputed this run; end-to-end speed NOT VERIFIED.

## Railway production (queried 2026-11-05 ~07:20 KST)
Project d1c1a050-b7d6-41ce-b300-13c20f82a20a, environment 83d5840b-270e-4d3f-a941-a37fd4a55ff7.
- PIT rebuild deployment 8b354fc1-cfb2-4ef0-863e-67f7f5dda2b5 SUCCESS, running 1/1; KRX worker 16c93d7c-7cd0-4d84-a327-298d2805376c SUCCESS, running 0/1 (nonrunning may be batch/cron; not evidence of execution). No deploy logs returned in 2026-11-04 21:20–22:25 UTC for either.
- Runtime eaaa9f67-b9f2-41d2-832c-7d6fad9b9b00 SUCCESS, running 1/1, logs through 22:19 UTC show USDKRW investing HTTPError -> Yahoo fallback and KOSPI quote; **not official PIT proof**.
- Kiwoom real-readonly service a77fb922-b679-4d88-92c4-03054ec579cd shows Online while replica running=0 crashed=1: health inconsistency (previously observed). Push offline warning 1, backend offline warning 4, db-query-readonly offline critical 1. No action taken.
- Existing staged environment patch e113dacb-6705-4416-9997-dc694539d382 remains staged and untouched.

## Independent gate verdict
- KRX 2017–2022 1565/1565 weekday original pair storage: historical integrity PASS only. Official calendar/90 uncertain sessions, 12003 zero-activity exclusions, 27 invalid OHLC, trading status/corporate actions/feasible fills: NOT VERIFIED / FAIL-CLOSED.
- OpenDART 2021/2022 first original filing, public available-at, exact 3-month consolidated operating income period and restatement lineage, historical corp/security mapping: NOT VERIFIED / FAIL-CLOSED. 15 candidate rows and numeric adjacency do not establish meaning/time.
- Frozen H5 previously failed, consumed holdout never reused. M20 horizon20/purge20, WF504/126/126, PIT/Purged/CPCV/Holdout/Champion/Top3/NO_TRADE all unchanged. M20 economics NOT EVALUABLE / NO-GO. NetEV/PF/CAGR/MDD/ES95/99, tax/cost, concentration and robustness NOT VERIFIED. ORDERING=false; no live permissions.
- Optimization: offline CI job-level PASS, 34-case hash and speed measurements not independently rerun; full CI and official backtest acceleration NOT VERIFIED. Cache requires exact independent approved source/data/code/Frozen/runtime/approval evidence SHA-256 fail-closed; only independent read-only postprocessing parallel, never dependent retraining/capital transitions.

## Next safe gates
1. Source teams independently attest original-filing/public timestamps/lineage and KRX exact market status/calendar, corp actions, security mapping and tradability with immutable source SHAs.
2. Independently revalidate 34-case fixed digest and synthetic mock invariants in isolated offline-only CI without workflow security bypass, and benchmark whole CI only after proper gate; no market performance experiment.
3. Preserve frozen policies and require distinct explicit approval before any M20 economics, Champion promotion, ordering, merge or deployment.
