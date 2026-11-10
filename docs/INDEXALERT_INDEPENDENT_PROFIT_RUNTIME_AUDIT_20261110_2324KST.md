# IndexAlert independent audit — 2026-11-10 23:24 KST

Scope: read-only GitHub/Railway review; isolated documentation-only write. No source, model, workflow, market-performance experiment, deployment, merge, or trading changes.

## Immutable references verified in this run
- PR #412 bf3d9514a87c53b1775e22ec9ba7711f6cecc49f; #413 f003ef6247e16fcc71bd3b1b20cd4904c4d984c0; #414 18c5418d9684d1717df58261ea27f28e514385b2; #418 2f98401cc50a6c6a25808a98516efd5bf0c944ee; KRX #420 fab3cbbd63a951a4e081f9e7f08c1391ca308581; #422 c14857620973531013799e44625d43080904fd5f; #423 0e38004363cac9fc4475556b3a1c445de9af407f. All OPEN Draft and unmerged at read time.
- Research ref index-alert-research-v1 exists, but current tip SHA NOT independently resolved by branch-search interface; PR #414 base_sha 3b8b7830612a6284d7c7a60628cb527cb741627a is a PR base snapshot, NOT proof of latest research tip. Development ref index-alert-position-regen-fix-v1 exists; Railway historical KRX deployed commit 1e6367d2863a86c3470da13d81a955d277eba485 is not proof of current development tip. Do not silently substitute.
- PR #414 integration gate docs/INDEXALERT_PROFITABILITY_INTEGRATION_GATE_2026-10-13.md read on its head branch; blob SHA 984c933651f39f1ee9e26a1d7ac3893aaa5335be was previously attested, not recomputed here. Its absence on frozen research base is expected.

## GitHub Actions, actual job states checked
- 38381997417 6/6 success; 38382214223 6/6 success; 38419111311 6/6 success; 38419649711 1/1 success; OpenDART 38419439742 2/2 success. These are old historical Actions, not fresh performance runs.
- 34-case fixed digest 5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34: prior evidence only, NOT recomputed this run. 13 adversarial and 28 synthetic counts: prior evidence only. 2.9656s serial / 2.6209s concurrent = 1.1315x regression-phase only, no verified end-to-end CI or official backtest speedup.
- Safe optimization boundary: offline-only, identical frozen inputs/outputs, all approved original/data/code/policy/runtime/approval SHA-256 cache keys fail-closed; parallelize only independent read-only post-processing, not retraining or capital transitions.

## Railway production observed
- Project d1c1a050-b7d6-41ce-b300-13c20f82a20a; environment 83d5840b-270e-4d3f-a941-a37fd4a55ff7.
- PIT rebuild deployment 8b354fc1-cfb2-4ef0-863e-67f7f5dda2b5 SUCCESS; replica running 1/1. 2026-11-10 12:01–14:16 UTC deploy logs (10 records): COMMON_OHLC_NONPOSITIVE; 27/803 common-stock rows with nonpositive OHLC and zero volume/value, independent source/chronology/model admission false, ordering DISABLED, live orders false. **FAIL** prospective source quality; **PASS** observed fail-closed/no-order policy in these log records. This is not independent attestation of production environment variables.
- Runtime deployment eaaa9f67-b9f2-41d2-832c-7d6fad9b9b00 SUCCESS; running 1/1.
- KRX historical worker deployment 16c93d7c-7cd0-4d84-a327-298d2805376c SUCCESS; replica running 0/1, crashed 0; latest queried deploy logs 0. Real runtime execution NOT VERIFIED. Earlier 1565/1565 weekday private pair storage integrity PASS only on prior source evidence; 90 unresolved dates, 12003 zero-activity cases and official status/tradability remain blocked.
- Kiwoom real read-only deployment a77fb922-b679-4d88-92c4-03054ec579cd SUCCESS, but running 0/1 and crashed 1/1: runtime health FAIL. Queried logs 0.
- Backend and Push offline, latest deployments FAILED; db-query-readonly offline and one critical issue.
- Environment describe staged=null, environment-status pendingWork reports an empty staged patch e113dacb-6705-4416-9997-dc694539d382; no changes applied.

## Admission decisions
| Gate | Decision | Reason |
|---|---|---|
| Original first-filed ZIP byte identity | PASS, historical source-only | Prior official SHA evidence, not independently rehashed now |
| 2021/2022 first 3-month consolidated operating profit, period, original/correction lineage and exact public available-at PIT | NOT VERIFIED | Candidate SGML rows and ZIP SHA cannot bind correct initial CFS value or publication instant |
| Historical issuer/security mapping | NOT VERIFIED | No independent as-of issuer/security chain |
| KRX original private storage | PASS, historical storage-only | Prior 1565/1565 SHA pairs; no independent private re-read |
| KRX calendar, halts, delistings, corporate actions, fills, costs and taxes | NOT VERIFIED | Historical official tradeability not proven |
| Prospective KRX OHLC quality | FAIL | 27/803 repeated nonpositive OHLC |
| Offline regression CI | PASS, software job completion only | 6/6, 6/6, 6/6, 1/1; digest not rehashed this run |
| End-to-end runtime acceleration | NOT VERIFIED | No comparable end-to-end wall-time |
| NetEV/PF/CAGR/MDD/ES95/99, profit concentration, temporal robustness, tax-adjusted risk-adjusted annual net return | NOT VERIFIED | PIT and tradeability prerequisites blocked; M20 economic RUN prohibited |
| M20 admission, Champion, Holdout reuse, live trading | NO-GO | Frozen policy and independent approval absent |

Frozen H5; M20 horizon20/purge20; WF504/126/126; PIT/Purged/CPCV/independent Holdout/Champion/Top3/NO_TRADE unchanged. H5 consumed Holdout and Dynamic outcomes must not be retrofitted or reused as independent tests. ORDERING=false required; observed log DISABLED. No M20 run, optimization performance search, orders, money movements, auth changes, merges, deployment, or Champion promotion.

## Next safe critical path
1. OpenDART owner: prove original 2021/2022 Q3 consolidated 3-month operating profit semantics, correction chronology and exact public available-at with immutable original SHA.
2. KRX owner: independently establish official calendar, issuer/security mapping, historical corporate actions, status and feasible fills; reconcile 90 days and 27 invalid OHLC without bypass.
3. Runtime owner: investigate Kiwoom read-only crashed replica and unavailable logs without changing permissions or deploying automatically.
4. Optimization owner: only offline synthetic fixed-case safety checks and whole-CI timing provenance; never imply official backtest acceleration.
5. Orchestrator: once all independent source/PIT/tradability gates pass, seek separate authorization before the single preregistered M20 economic evaluation. No user authorization is inferred here.
