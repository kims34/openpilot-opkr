# IndexAlert independent profitability and runtime audit — 2026-11-05 08:22 KST

Read-only verification, no authorization for live trading, M20, merge, deployment, or champion promotion.

## GitHub PR snapshots
- #412 OPEN Draft HEAD bf3d9514a87c53b1775e22ec9ba7711f6cecc49f
- #413 OPEN Draft HEAD f003ef6247e16fcc71bd3b1b20cd4904c4d984c0
- #414 OPEN Draft HEAD 18c5418d9684d1717df58261ea27f28e514385b2
- #418 OPEN Draft HEAD 2f98401cc50a6c6a25808a98516efd5bf0c944ee
- KRX #420 fab3cbbd63a951a4e081f9e7f08c1391ca308581, #422 c14857620973531013799e44625d43080904fd5f, #423 0e38004363cac9fc4475556b3a1c445de9af407f; all OPEN Draft.
- Research index-alert-research-v1 and development index-alert-position-regen-fix-v1 exist; HEAD not independently resolved this run, NOT VERIFIED.
- #414 gate document blob SHA-1 984c933651f39f1ee9e26a1d7ac3893aaa5335be (fetched at #414 HEAD).

## CI (current read-only job result)
- Actions 38381997417, 38382214223, 38419111311: 6/6 jobs success each.
- 38419649711: 1/1 success; 38419439742: 2/2 success.
- Chronology anchor 41515392296: auto-anchor FAIL, validation SKIPPED. Independent official chronology approval BLOCKED.
- Previously recorded 34-case SHA-256 5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34 and serial 2.9656s vs concurrent 2.6209s (1.1315x) NOT independently recomputed this run. This is regression-phase only, not end-to-end speedup.

## Railway production read-only
Project d1c1a050-b7d6-41ce-b300-13c20f82a20a; environment 83d5840b-270e-4d3f-a941-a37fd4a55ff7.
- PIT rebuild deployment 8b354fc1-cfb2-4ef0-863e-67f7f5dda2b5 SUCCESS, running 1; KRX worker 16c93d7c-7cd0-4d84-a327-298d2805376c SUCCESS.
- PIT/KRX deploy logs: zero entries for 2026-11-05 07:00–08:25 KST; absence does not establish PIT approval.
- Runtime deployment eaaa9f67-b9f2-41d2-832c-7d6fad9b9b00 SUCCESS; 08:21 KST log shows USDKRW Investing.com HTTP errors and Yahoo fallback. This is not official market PIT evidence.
- Kiwoom real-readonly Online UI but replica running 0/crashed 1; push and backend Offline warnings; db-query-readonly Offline Critical.
- Pending staged patch e113dacb-6705-4416-9997-dc694539d382 untouched.

## Gate judgments
- KRX 2017–2022 stored 1565/1565 weekday raw pairs: historical storage-integrity PASS only (prior evidence); official trading calendar, halt/delist, corporate actions, executable quotes, fees/taxes NOT VERIFIED.
- OpenDART SGML candidate 15 rows: candidate structure prior PASS; first original filing semantics, public available-at, 2021/2022 connected first three-month operating profit period and correction lineage NOT VERIFIED.
- Historical issuer/security mapping NOT VERIFIED.
- Frozen H5 holdout failed/consumed, no independent reuse. M20 horizon20/purge20 WF504/126/126 PIT/labels/Purged/CPCV/holdout/champion/top3/NO_TRADE unchanged.
- Annual risk-adjusted after-cost-and-tax NetEV/PF/CAGR/MDD/ES95/99/concentration/time robustness NOT VERIFIED. M20 NOT EVALUABLE / NO-GO.
- Cache only on independently approved exact SHA-256 evidence match, fail closed. Parallelism restricted to independent read-only postprocessing. No dependent retraining or capital-transition parallelism. ORDERING=false.
- Next: independently authenticate original filing/public timestamp and 2021/2022 lineage; official KRX trading state and historical mapping; verify evidence hashes and offline synthetic regression parity. Do not run market profitability or change frozen policy until approval.
