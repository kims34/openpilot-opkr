# IndexAlert independent audit — 2026-11-12 06:16 KST

Read-only observation. No trading, deployment, merging, economic backtesting or frozen-policy changes authorized.

## GitHub evidence
- research HEAD df474df348f22aa38b1dedaa59fcff66e548b406; development HEAD 1e6367d2863a86c3470da13d81a955d277eba485 (GitHub branches API).
- PRs #412 bf3d9514a87c53b1775e22ec9ba7711f6cecc49f; #413 f003ef6247e16fcc71bd3b1b20cd4904c4d984c0; #414 18c5418d9684d1717df58261ea27f28e514385b2; #418 2f98401cc50a6c6a25808a98516efd5bf0c944ee; #420 fab3cbbd63a951a4e081f9e7f08c1391ca308581; #422 c14857620973531013799e44625d43080904fd5f; #423 0e38004363cac9fc4475556b3a1c445de9af407f. All open/draft at read.
- #414 integration document blob SHA 984c933651f39f1ee9e26a1d7ac3893aaa5335be; explicitly forbids treating stored KRX pairs or original SGML candidate rows as investment PIT approval.
- Actions 38381997417, 38382214223, 38419111311, 38419649711, 38419439742: completed/success from live GitHub API. #418 run 38419649711 jobs endpoint: one-runner-offline-comparison 1/1 success, steps for synthetic controls, regression integrity, serial-vs-concurrent suites successful. Historical claims of 34-case SHA 5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34, 13 mocks, 28 synthetic, 2.9656/2.6209 seconds not independently recalculated in this run. Overall CI and official backtest speed NOT VERIFIED.
- Links: https://github.com/kims34/openpilot-opkr/pull/414 ; https://github.com/kims34/openpilot-opkr/pull/413 ; https://github.com/kims34/openpilot-opkr/pull/418 ; https://github.com/kims34/openpilot-opkr/actions/runs/38419649711

## Railway production evidence
- Project d1c1a050-b7d6-41ce-b300-13c20f82a20a, environment 83d5840b-270e-4d3f-a941-a37fd4a55ff7. PIT rebuild running 1/1; runtime running 1/1; KRX historical worker running 0/1 (not demonstrated active); Kiwoom real-readonly 0 running / 1 crashed despite service state 'online' — runtime FAIL; backend, push, db-query-readonly offline; db-query-readonly critical 1.
- Staged patch e113dacb-6705-4416-9997-dc694539d382 has zero changes; do not apply.
- Queried deploy logs for PIT, runtime, KRX and Kiwoom, 2026-11-11 20:00–21:20 UTC. PIT/KRX/Kiwoom: zero returned. Runtime: USDKRW Investing HTTPError and Yahoo fallback observed at 21:15:44 UTC; no claim of PIT approval. No modifications.

## Independent gates
- Historical KRX private 1565/1565 weekday raw pair storage: historical PASS only, not rehashed this run. Official calendar, trading status, corporate actions, actual fillability, transaction costs/taxes: NOT VERIFIED, fail-closed.
- OpenDART original filing SGML candidate signature 15 rows: historical evidence only. Exact original available-at/PIT, 2021/2022 first 3-month consolidated operating profit period and amendment lineage, historical corp/security mapping: NOT VERIFIED.
- M20 PIT authorization: NO-GO; M20 official economic run not performed. H5 spent/failed holdout cannot be reused; frozen H5/M20 horizon20/purge20 WF504/126/126, Purged/CPCV/holdout/Champion/Top3/NO_TRADE remain unchanged.
- NetEV/PF/CAGR/MDD/ES95/99, concentration, period robustness, risk-adjusted annual net profit after costs/tax: NOT VERIFIED, no claim of alpha.
- Optimization PR #413/#418: offline CI status PASS; immutable test-result SHA parity independent rehash NOT VERIFIED. Cache only with approved evidence/source/data/code/frozen/runtime SHA-256 and fail-closed; only independent read-only postprocessing parallel. No dependent training or capital transition parallel.
- ORDERING=false / NO TRADE requirement; runtime flag values not independently read this run, so live flag state NOT VERIFIED. No orders, transfers, credentials, Champion promotion, deployment or PR merge.

## Next safe steps
Obtain independently auditable official original-filing publication timestamps and Q3 lineage, and KRX official historical market-state/corporate-action evidence from their respective owners; only after all source PIT gates PASS consider a single preregistered M20 evaluation. Independently reproduce 34-case SHA and full-CI wall-time in offline-only isolation without changing another owner's code. Investigate crashed Kiwoom read-only replica and offline db-query-readonly with owner, without deploying or changing credentials.
