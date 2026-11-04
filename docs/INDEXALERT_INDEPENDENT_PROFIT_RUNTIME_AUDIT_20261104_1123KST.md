# IndexAlert independent profitability / runtime audit — 2026-11-04 11:23 KST

## Read-only evidence and scope
- Research branch `index-alert-research-v1` and development `index-alert-position-regen-fix-v1` exist via branch search; exact live branch HEAD not independently resolved this cycle (NOT VERIFIED). The README path probe returned 404 and is not proof of branch absence.
- Draft OPEN unmerged PRs: #412 (OpenDART), #413 (runtime), #414 (integration), #418 (one-runner), #420/#422/#423 (KRX). PR #414 HEAD `18c5418d9684d1717df58261ea27f28e514385b2`; gate document blob SHA-1 `984c933651f39f1ee9e26a1d7ac3893aaa5335be`. Other exact PR HEADs not transcribed into this report because full returned metadata was not retained in the audit output.
- Actual GitHub Actions jobs queried this cycle: #38381997417 6/6 SUCCESS; #38382214223 6/6 SUCCESS; #38419111311 6/6 SUCCESS; #38419649711 1/1 SUCCESS; OpenDART #38419439742 2/2 SUCCESS; chronology #41515392296 auto-anchor FAILURE, validation SKIPPED. Jobs success is not PIT source admission.
- Previous immutable 34-case regression SHA256 `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34`, 13 adversarial mocks, 28 synthetic tests and serial 2.9656s / concurrent 2.6209s (1.1315x regression-phase only) are **prior reported evidence**, not independently recomputed this cycle.
- Railway project IndexAlert, production services discovered. Historical KRX worker deployment `16c93d7c-7cd0-4d84-a327-298d2805376c` SUCCESS 2026-10-12, commit `1e6367d2863a86c3470da13d81a955d277eba485`; separate readonly deployment `a77fb922-b679-4d88-92c4-03054ec579cd` SUCCESS 2026-10-29. No deployment or config changes performed.
- Railway deploy logs read-only for 2026-11-04 10:00–11:23 KST: PIT rebuild 0 entries; historical KRX worker 0 entries; IndexAlert runtime returned live log entries through 11:22:44 KST including Investing USD/KRW HTTP errors and Yahoo fallback, and closed ETF proxy valuation. These logs do not establish official filing chronology or market tradability.

## Independent gates
| Gate | Verdict | Reason |
|---|---|---|
| KRX private original byte storage 2017–2022 | historical LIMITED PASS | Earlier 1565/1565 weekday source pairs SHA integrity; not rerun this cycle |
| Official KRX calendar, stock status, corporate actions, fillability, fees and taxes | NOT VERIFIED / FAIL-CLOSED | 90 unclassified days, zero-activity 12003 quarantined; #422/#423 describe synthetic-only comparisons without private exact-set run |
| OpenDART original-filing, public available-at PIT, 2021/2022 first 3-month consolidated operating-profit and amendment lineage | NOT VERIFIED / FAIL-CLOSED | #38419439742 successful candidate-row shape tests do not establish meaning or precise public time; chronology anchor failed |
| Historical company/security mapping | NOT VERIFIED | no independently admitted time-varying mapping |
| Offline runtime software parity | LIMITED PASS | CI jobs successful; fixed-case SHA not independently recomputed now |
| Actual full CI and official backtest speedup | NOT VERIFIED | regression-phase 1.1315x is not end-to-end acceleration |
| M20 NetEV/PF/CAGR/MDD/ES95/ES99, concentration, temporal robustness, net after costs/taxes | NOT EVALUABLE / NO-GO | PIT and tradability gates not approved; no economic run permitted |

## Safety and next permissible work
Keep Frozen H5, M20 horizon20/purge20, WF504/126/126, PIT/purging/CPCV/independent holdout/Champion/Top3/NO_TRADE, fees/tax/risk/promotion unchanged; ORDERING=false. Never reuse consumed H5 Holdout or post-hoc Dynamic results. Cache only with independently admitted immutable source/data/code/policy/runtime/evidence SHA256 and fail-closed mismatch; parallelize read-only independent postprocessing only, not dependent refits or capital transitions. No official-return or M20 economics run, model search, order, transfer, credentials change, Champion promotion, deployment, workflow edit or PR merge. Next: independently establish official OpenDART publication timing and full correction lineage; official historical KRX day/status and exact private set audit under separate authorization; pin exact source and policy SHA before a separately approved M20 gate review.
