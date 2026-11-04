# IndexAlert independent profitability / runtime audit — 2026-11-04 12:18 KST

## Fresh read-only evidence
- GitHub repository `kims34/openpilot-opkr`: research `index-alert-research-v1`, development `index-alert-position-regen-fix-v1`, isolated audit branch all exist in branch search. Exact live HEAD of these branches not returned by branch search: **NOT VERIFIED** (do not equate Railway deployment SHA with live branch HEAD).
- Draft OPEN unmerged PRs checked: #412 OpenDART, #413 isolated runtime, #414 integration HEAD `18c5418d9684d1717df58261ea27f28e514385b2`, #418 single runner HEAD `2f98401cc50a6c6a25808a98516efd5bf0c944ee`, KRX #420/#422/#423. PR #413 earlier reported HEAD `f003ef6247e16fcc71bd3b1b20cd4904c4d984c0` not independently transcribed from this cycle.
- Integration document `docs/INDEXALERT_PROFITABILITY_INTEGRATION_GATE_2026-10-13.md` fetched directly from PR #414 branch. It explicitly gates KRX 1565/1565 original storage SHA-only PASS and M20 PIT NO-GO.
- GitHub Actions job API read this cycle: #38381997417 6/6 SUCCESS, #38382214223 6/6 SUCCESS, #38419111311 6/6 SUCCESS, #38419649711 1/1 SUCCESS, OpenDART #38419439742 2/2 SUCCESS; chronology #41515392296 auto-anchor FAILURE and validation SKIPPED. These are CI job conclusions, not independent PIT admission. Earlier 34-case SHA256 `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34`, 13 adversarial mocks, 28 synthetic cases and 2.9656s vs 2.6209s (1.1315x regression-phase only) remain historical reports, not recomputed.
- Railway project `d1c1a050-b7d6-41ce-b300-13c20f82a20a`, production: historical worker latest observed SUCCESS deployment `16c93d7c-7cd0-4d84-a327-298d2805376c` (2026-10-12, deployed SHA `1e6367d2863a86c3470da13d81a955d277eba485`); separate readonly deployment `a77fb922-b679-4d88-92c4-03054ec579cd` SUCCESS (2026-10-29).
- Railway deploy logs queried for 2026-11-04 11:00–12:20 KST: PIT rebuild 0 entries, historical worker 0 entries; runtime 101 returned entries through 12:17:45 KST. Runtime includes ETF_CLOSED_PROXY futures-linked indicative valuations and Naver KOSPI quote; these are not official historical KRX source or fill evidence. Zero log entries are not proof that prior source errors were fixed.

## Gate verdicts
| Gate | Verdict | Scope / blocker |
|---|---|---|
| 2017–2022 KRX 1565 weekday daily/master source pairs | historical LIMITED PASS | Previous private SHA integrity evidence, not independently rerun here |
| Official KRX exchange calendar, historical issuer/security status, corporate actions, historical mapping, fillability | NOT VERIFIED / FAIL-CLOSED | 90 source gaps, 12003 zero-activity quarantined; #422/#423 synthetic-only comparator, no authorized real private exact-set audit |
| OpenDART first original filing and public available-at/PIT, 2021/2022 initial 3-month consolidated operating income, correction lineage | NOT VERIFIED / FAIL-CLOSED | #38419439742 2/2 job success only, candidate-row shapes not period/publication admission; chronology #41515392296 FAIL |
| PR #413/#418 offline safety regression | LIMITED PASS | CI jobs green; immutable parity SHA not independently recalculated this cycle |
| End-to-end CI / actual official backtest acceleration | NOT VERIFIED | 1.1315x is regression-phase ratio only |
| After-cost/tax annual risk-adjusted NetEV/PF/CAGR/MDD/ES95/99/concentration/temporal robustness | NOT EVALUABLE / NO-GO | M20 source PIT and execution not authorized; no profitability replay |

## Fixed guardrails and next steps
- Keep Frozen H5, M20 horizon20/purge20, WF504/126/126, PIT/label/Purged/CPCV/sealed independent Holdout/Champion/Top3/NO_TRADE, costs/taxes/risk/promotion thresholds unchanged; ORDERING=false.
- No model search, official market performance replay, M20 economics, H5 consumed Holdout reuse, live orders, capital movement, permission changes, Champion promotion, deployment, PR merges or workflow edits.
- Cache only with independently admitted source/data/code/Frozen/runtime/approval evidence SHA-256 exact match and fail-closed; parallelise read-only independent postprocessing, never dependent retraining or capital transitions.
- Next evidence: original filing semantic period/correction/publication timestamp proof; independently authenticated historical KRX calendar/status/corporate-action/fill evidence; only then separately authorized PIT admission and M20 economics. Existing KRX worker private read-only audit requires separate approval and must not be launched here.
- No other Work-owned code or operational settings touched. This document is the only intended isolated write.
