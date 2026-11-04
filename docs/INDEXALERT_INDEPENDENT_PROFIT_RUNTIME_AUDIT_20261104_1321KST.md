# IndexAlert independent profitability/runtime audit — 2026-11-04 13:21 KST

Read-only evidence review; no strategy, data, deployment, workflow, ordering or trading changes. This is an audit, not a PIT admission.

## GitHub source and isolation
- Branch search confirms `index-alert-research-v1`, `index-alert-position-regen-fix-v1` and `indexalert-independent-audit-20261104-0222kst` exist. Exact current branch commit HEAD: **NOT VERIFIED** (branch search does not return commit SHA; README.md path fetch gave 404, which is not proof of branch absence).
- Draft OPEN unmerged PRs #412, #413, #414, #418, #420, #422, #423 checked via GitHub connector. PR #414 head `18c5418d9684d1717df58261ea27f28e514385b2`; PR #413 previously observed `f003ef6247e16fcc71bd3b1b20cd4904c4d984c0`, PR #418 previously observed `2f98401cc50a6c6a25808a98516efd5bf0c944ee` (these latter two not independently SHA-rechecked in this cycle).
- PR #414 gate document fetched directly; blob SHA was not preserved in this run. It explicitly denies M20 authority.
- KRX #422 2021 exact-day and #423 2022 exact-day comparator descriptions explicitly state original private stored day-set has **not** been actually inspected. Synthetic controls do not resolve historical market-calendar gaps.

## GitHub Actions directly checked in this cycle
- #38381997417: 6/6 jobs success; #38382214223: 6/6 success; #38419111311: 6/6 success; #38419649711: 1/1 success; #38419439742: 2/2 success.
- #41515392296: auto-anchor failure, validation skipped. Chronology is **FAIL/BLOCKED**; successful OpenDART row-shape CI does not prove original filing semantics, first public timestamp, or period lineage.
- Historical 34-case fingerprint `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34`, 13 adversarial mocks, 28 synthetic cases and 2.9656s/2.6209s=1.1315x regression-phase ratio are **previously reported evidence, not independently recalculated here**. Full CI and official backtest acceleration: **NOT VERIFIED**.

## Railway directly checked
- Project IndexAlert `d1c1a050-b7d6-41ce-b300-13c20f82a20a`, production service discovery.
- Historical KRX worker deployment `16c93d7c-7cd0-4d84-a327-298d2805376c`, SUCCESS (created 2026-10-12 UTC), source commit `1e6367d2863a86c3470da13d81a955d277eba485`. Existing 1565/1565 weekday pair storage integrity PASS is historical evidence, not independently rehashed in this cycle.
- Read-only 2026-11-04 12:00–13:22 KST log window: PIT rebuild deployment `8b354fc1-cfb2-4ef0-863e-67f7f5dda2b5` SUCCESS but zero runtime log entries; KRX worker SUCCESS, zero entries. Runtime deployment `eaaa9f67-b9f2-41d2-832c-7d6fad9b9b00` SUCCESS with logs at 13:21 KST showing Investing USD/KRW HTTP errors and Yahoo fallback. No inference of source-PIT approval from these logs.

## Independent verdicts
- Original OpenDART original-filing, public available-at/PIT, 2021/2022 first three-month consolidated operating profit, corrections lineage: **NOT VERIFIED / fail-closed**.
- Historical corp/security identity mapping, official KRX calendar/status/actions/tradability, fills, costs and taxes: **NOT VERIFIED / fail-closed**. Private raw-pair storage integrity historical PASS is not tradability PASS.
- Frozen H5/consumed Holdout/Dynamic cannot be re-used as independent validation. M20 horizon20/purge20, WF504/126/126, costs/taxes/NetEV, independent Holdout/Champion/Top3/NO_TRADE and ORDERING=false remain unchanged.
- NetEV/PF/CAGR/MDD/ES95/99, concentration, time robustness, after-tax annual risk-adjusted net returns: **NOT EVALUABLE; M20 NO-GO**. No new market-return run performed.
- Offline-only synthetic CI **limited PASS**, actual official backtest speedup **NOT VERIFIED**. Fail-closed cache requires source/data/code/Frozen/runtime/approval SHA-256 equality; only independent read-only postprocessing may parallelize; no dependent training or capital transition parallelism.

## Next evidence-only steps
1. Obtain original official first-filing document and exact publication-time, period, amendment and corporate mapping provenance under independent SHA and approved PIT.
2. Independently reconcile historical KRX private exact day sets with authenticated historical calendar/status and actual tradability/fees/taxes, preserving quarantine.
3. Resolve failed chronology anchor before admission. Recheck current branch HEAD and CI artifacts with SHA rather than interpreting branch search as commit verification.
4. Only after all gates pass, separately authorize the one preregistered M20 evaluation. No workflow changes, merges, production deployment, live order or Champion promotion.
