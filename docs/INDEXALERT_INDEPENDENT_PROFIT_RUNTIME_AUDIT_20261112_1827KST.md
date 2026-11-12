# IndexAlert independent profitability and runtime audit — 2026-11-12 18:27 KST

## Fresh read-only evidence
- Research branch `index-alert-research-v1` HEAD `df474df348f22aa38b1dedaa59fcff66e548b406`; GitHub compare against same SHA: identical, ahead/behind 0/0.
- Development branch `index-alert-position-regen-fix-v1` HEAD `1e6367d2863a86c3470da13d81a955d277eba485`; compare identical 0/0.
- GitHub pull requests directly fetched, all OPEN/Draft/unmerged: #412 `bf3d9514a87c53b1775e22ec9ba7711f6cecc49f`; #413 `f003ef6247e16fcc71bd3b1b20cd4904c4d984c0`; #414 `18c5418d9684d1717df58261ea27f28e514385b2`; #418 `2f98401cc50a6c6a25808a98516efd5bf0c944ee`; KRX #420 `fab3cbbd63a951a4e081f9e7f08c1391ca308581`; #422 `c14857620973531013799e44625d43080904fd5f`; #423 `0e38004363cac9fc4475556b3a1c445de9af407f`.
- #414 frozen integration gate file fetched on its own branch: blob SHA `984c933651f39f1ee9e26a1d7ac3893aaa5335be`. Its KRX storage-only PASS / PIT fail-closed and H5/0-N NO-GO remain binding.
- Actions jobs fetched directly: 38381997417 6/6 success; 38382214223 6/6 success; 38419111311 6/6 success; 38419649711 1/1 success; 38419439742 2/2 success; 38498552499 6/6 success. Exact immutable 34-case SHA `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34` is previously reported but **NOT independently recomputed** this cycle.
- Offline #413/#418 tests are software-safety/parity evidence only. Previously reported serial 2.9656 s vs concurrent 2.6209 s, ratio 1.1315x for regression phase only; more recent #413 timing 1.7114 s serial vs 2.5776 s concurrent (parallel slower), with #413/#418 implementation-SHA mismatch. Actual complete CI/official market backtest speedup **NOT VERIFIED**. No new benchmarks run.
- Railway IndexAlert production environment `83d5840b-270e-4d3f-a941-a37fd4a55ff7`: PIT rebuild 1/1 running, runtime 1/1 running; KRX worker 0/1 running, 0 crashed; Kiwoom real-readonly 0/1 running, 1 crashed **operational FAIL** despite service summary 'Online'. Backend, push and db-query-readonly offline; db-query-readonly 1 critical. Pending staged patch `e113dacb-6705-4416-9997-dc694539d382` contains **zero changes**, untouched.
- Railway deployment logs queried for 2026-11-12 08:20–09:30 UTC: PIT/KRX/Kiwoom 0 entries; runtime 31 returned, including 09:27 UTC Investing.com USD/KRW HTTPError and Yahoo fallback. Empty logs do not establish source validity or successful collection. No production mutation.

## Admission verdict (strict source and economic separation)
| Gate | Verdict | Rationale |
| --- | --- | --- |
| OpenDART original/correction bytes and SGML candidate-row signatures | Historical narrow PASS only | Action 38419439742 2/2 CI; 15 candidate operating-result rows previously reported; semantic period/original-public timestamp unapproved |
| 2021/2022 initial 3-month consolidated operating-profit period/correction lineage and exact original public available-at/PIT | NOT VERIFIED / FAIL-CLOSED | No independently approved first-filing event-time and correction chain |
| Historical entity/security mapping | NOT VERIFIED | Point-in-time identity not admitted |
| KRX 2017–2022 private weekday daily/master pairs | Historical storage-integrity PASS only | 1,565/1,565 previously SHA audited; this run did not rehash private originals |
| KRX exact calendar, 90 uncertain sessions, 27 invalid OHLC, 12,003 zero-activity, corporate actions, halts/delistings, fills, costs and taxes | NOT VERIFIED / FAIL-CLOSED | Specialist drafts #420/#422/#423 do not grant official market PIT or tradability |
| H5 consumed/failed Holdout and dynamic economics | NO-GO | Cannot reuse or tune against consumed Holdout |
| M20 horizon20/purge20, WF504/126/126 official PIT admission and economic run | NO-GO | No approved source PIT; no M20 profitability experiment |
| Post-cost/post-tax annual risk-adjusted NetEV, PF, CAGR, MDD, ES95/99, concentration, temporal robustness | NOT VERIFIED | No admissible independent real-source results |
| Offline runtime CI | PASS for listed job conclusions only | Test output hashes and real whole-backtest acceleration NOT VERIFIED |

## Immutable safety and next evidence
- Frozen H5; M20 horizon20/purge20; WF504/126/126; label/Purged/CPCV/independent Holdout/Champion/Top3/NO_TRADE; all cost, tax, fill, risk, NetEV and promotion gates unchanged. ORDERING=false required; actual production variable value NOT VERIFIED.
- Cache fail-closed unless approved source, data, calculation code, Frozen policy, runtime and approval evidence SHA-256 all match; parallelize read-only independent postprocessing only, never dependent retraining or capital transitions.
- Next independent evidence: exact 2021/2022 first-filed consolidated 3-month operating-profit row + filing-public-time lineage and approved KRX session/security-state source receipts, each pinned by SHA, then historical mapping/fills/cost/tax, then only separately authorized immutable M20 economic run.
- No model search, economic replay, deployment, merge, workflow edit, ordering, real trade, account/auth changes, fund transfer or Champion promotion. This isolated document is the only write in this cycle.
