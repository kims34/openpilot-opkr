# IndexAlert independent read-only audit — 2026-11-06 13:22 KST

Scope: independent profitability and isolated runtime-optimisation evidence only. No market backtest, deployment, merge, workflow edit, or trade.

## Source snapshots
GitHub PRs #412 #413 #414 #418 #420 #422 #423: OPEN/Draft as fetched this run. Their head refs respectively: indexalert-m20-opendart-original-proof-20261013; index-alert-backtest-runtime-opt-v1-20261013; indexalert-profitability-integration-evidence-20261013; index-alert-backtest-single-runner-opt-v1-20261013; indexalert-krx-session-gap-review-v1-20261015; indexalert-krx-private-2021-calendar-compare-v1-20261017; indexalert-krx-private-2022-calendar-candidate-v1-20261018. Exact current branch/PR commit HEAD SHA: NOT VERIFIED this run (branch search provides names, PR fetch provides head names only). Prior research HEAD df474df348f22aa38b1dedaa59fcff66e548b406 and development HEAD 1e6367d2863a86c3470da13d81a955d277eba485 are historical, NOT current-confirmed.
PR #414 gate document Git blob SHA 984c933651f39f1ee9e26a1d7ac3893aaa5335be, read directly from PR head ref.

## GitHub Actions — direct job results this run
38381997417 6/6 success; 38382214223 6/6 success; 38419111311 6/6 success; 38419649711 1/1 success; OpenDART 38419439742 2/2 success. Chronology Anchor 41515392296 auto-anchor FAILURE, validation SKIPPED. Historical fixed 34-case SHA 5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34 and synthetic 13/28 cases not independently rehashed this run. Historical regression-phase 2.9656/2.6209=1.1315x; end-to-end CI and official backtest speed NOT VERIFIED.

## Railway production — read-only environment status
Project d1c1a050-b7d6-41ce-b300-13c20f82a20a, environment 83d5840b-270e-4d3f-a941-a37fd4a55ff7.
PIT rebuild deployment 8b354fc1-cfb2-4ef0-863e-67f7f5dda2b5 SUCCESS running 1/1; KRX historical worker deployment 16c93d7c-7cd0-4d84-a327-298d2805376c SUCCESS running 0/1; runtime eaaa9f67-b9f2-41d2-832c-7d6fad9b9b00 SUCCESS running 1/1. Both PIT and KRX worker runtime logs empty since 2026-11-06 03:00 UTC; OHLC 27/803 resolution NOT VERIFIED. Backend/push/db-query-readonly offline; db-query-readonly critical 1. Kiwoom real-readonly UI online but running 0/crashed 1. Staged patch e113dacb-6705-4416-9997-dc694539d382 remains pending; untouched.

## Gate matrix
Historical KRX 1565/1565 weekday original pairs storage integrity: historical PASS only; official calendar, trading status, corporate actions, execution, cost/tax: NOT VERIFIED.
OpenDART 15 candidate rows numerical adjacency: historical PASS at syntactic level only; original-filing semantic identity, 2021/2022 first 3-month consolidated operating profit period/correction lineage and public available-at PIT: NOT VERIFIED.
Historical company/security mapping: NOT VERIFIED.
NetEV/PF/CAGR/MDD/ES95/ES99/concentration/temporal robustness after costs and taxes: NOT VERIFIED.
Chronology anchor: FAIL; downstream validation SKIPPED. M20 PIT/economics NO-GO. H5 consumed holdout cannot be reused. ORDERING=false policy required, runtime variable not independently checked.

## Next allowed work
Obtain independent official original-filing timestamp and correction lineage, official KRX calendar/status/exec evidence, repair chronology anchor using authorised safe isolated documentation or synthetic-only tests; verify exact source/approval SHA-256 and frozen cache keys before fail-closed reuse. Preserve frozen H5, M20 horizon20/purge20, WF504/126/126, holdout and NO_TRADE policies. No official economic run, strategy search, dependent training parallelisation, capital transition parallelisation, deployment, merges or trading.
