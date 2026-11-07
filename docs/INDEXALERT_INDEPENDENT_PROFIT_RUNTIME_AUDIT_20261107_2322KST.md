# IndexAlert independent audit — 2026-11-07 23:22 KST

Scope: evidence-only, no strategy replay, no deployment, no trading. This isolated branch was created from verified historical development commit `1e6367d2863a86c3470da13d81a955d277eba485`; this is NOT proof of the live branch HEAD. Other workstreams are untouched.

## Directly read GitHub PR metadata
| PR | HEAD SHA | state |
|---|---|---|
| 412 OpenDART | bf3d9514a87c53b1775e22ec9ba7711f6cecc49f | open draft |
| 413 optimization | f003ef6247e16fcc71bd3b1b20cd4904c4d984c0 | open draft |
| 414 integration | 18c5418d9684d1717df58261ea27f28e514385b2 | open draft |
| 418 single runner | 2f98401cc50a6c6a25808a98516efd5bf0c944ee | open draft |
| 420 KRX | fab3cbbd63a951a4e081f9e7f08c1391ca308581 | open draft |
| 422 KRX | c14857620973531013799e44625d43080904fd5f | open draft |
| 423 KRX | 0e38004363cac9fc4475556b3a1c445de9af407f | open draft |

PR #414 integration gate file blob SHA `984c933651f39f1ee9e26a1d7ac3893aaa5335be` directly read. PR base SHA is NOT proof of current branch HEAD. Research `index-alert-research-v1` and development `index-alert-position-regen-fix-v1` current HEAD: NOT VERIFIED this run.

## Direct GitHub Actions job evidence
- 38381997417: 6/6 success; 38382214223: 6/6 success; 38419111311: 6/6 success; 38498552499: 6/6 success.
- 38419649711: 1/1 success, offline one-runner; 38419439742: 2/2 success, offline OpenDART row tests.
- 41515392296: auto-anchor FAILURE, validation SKIPPED.
- Prior pinned 34-case SHA-256 `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34` and synthetic 28 / adversarial 13 / serial 2.9656s vs concurrent 2.6209s are historical claims, not newly reproduced artifact-hash evidence. Real market backtest acceleration NOT VERIFIED.

## Direct Railway production status and logs
Project `d1c1a050-b7d6-41ce-b300-13c20f82a20a`, environment `83d5840b-270e-4d3f-a941-a37fd4a55ff7`.
- PIT service deployment `8b354fc1-cfb2-4ef0-863e-67f7f5dda2b5` SUCCESS, replicas 1 running / 0 crashed. Logs through 2026-11-07 22:46 KST: repeated `FAIL_CLOSED`, `KRXProspectiveOpenAPISourceError`, `COMMON_OHLC_NONPOSITIVE`; 803 common stock rows, 27 nonpositive OHLC, 27 zero volume/value, source_failure_session 2026-09-28, manifest SHA null, independent source/chronology/model approvals false, ordering DISABLED, orders/funds not authorized. This is a source validation FAIL, not a deployment failure.
- Real-account read-only deployment `a77fb922-b679-4d88-92c4-03054ec579cd` SUCCESS but replicas 0 running / 1 crashed; apparent online status is misleading. No new service deploy logs in requested window.
- KRX historical worker deployment `16c93d7c-7cd0-4d84-a327-298d2805376c` SUCCESS; replicas 0 running / 0 crashed; no new logs in requested window. Cron completion and official trading-state proof NOT VERIFIED.
- Runtime 1/1 running; db-query-readonly 1 critical alert; empty staged patch `e113dacb-6705-4416-9997-dc694539d382` still reported. No change applied.

## Independent evidence gates
| Gate | Verdict |
|---|---|
| KRX 2017–2022 1565/1565 stored original weekday pairs | Historical storage integrity PASS only; not freshly rehashed |
| KRX official sessions / suspensions / corporate actions / fills / tax / costs | NOT VERIFIED |
| Prospective OHLC validation | FAIL_CLOSED (27/803) |
| Original-filing 2021/2022 connected operating profit, exact period, correction lineage, public available-at/PIT | NOT VERIFIED |
| Historical corp-security mapping and first-publication chronology | NOT VERIFIED |
| Offline CI software jobs listed above | PASS (job outcomes only) |
| NetEV, PF, CAGR, MDD, ES95/99, concentration, temporal robustness after costs/tax | NOT VERIFIED; no authorized economic run |
| Full end-to-end official backtest speedup | NOT VERIFIED |
| M20 admission / live trading / champion promotion | NO-GO |

Next safe steps: independently establish official original filing timestamps and lineage; compare 2021/2022 private official calendar/session evidence; reconcile 27 OHLC failures without backfilling or source substitution; diagnose read-only crashed replica from deployment-specific logs; investigate chronology anchor failure using existing logs; independently validate full CI evidence SHA before claiming optimization. Maintain Frozen H5, M20 horizon20/purge20, WF504/126/126, holdout isolation, NO_TRADE, ORDERING=false. No workflow edits, merges, deployments, market performance tests, model search, permission changes or orders.
