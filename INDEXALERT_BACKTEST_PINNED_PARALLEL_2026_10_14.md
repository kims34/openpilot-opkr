# IndexAlert pinned-parallel-only regression optimization — offline CI evidence

**Date:** 2026-10-14 KST. **Repository:** kims34/openpilot-opkr. **Isolated branch:** index-alert-backtest-single-runner-opt-v1-20261013. **Review:** Draft PR #418 (unmerged), based on the earlier optimization PR #413 (also Draft/unmerged). This is an **offline regression-engineering acceleration**, not an official H5/M20 backtest or PIT admission.

## Scope and fixed baseline

- Archived, independently reproduced 34-case baseline from original GitHub Actions 38381997417 and 38382214223, pinned in existing `research_v1_runtime_ci.PINNED_CASES` (9 cost + 9 risk + 8 frozen gates + 8 cache).
- Canonical 34-case identity/result SHA-256: `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34`.
- Earlier exploratory `research_v1_runtime_single_runner.py` ran the fixed 34-case suite **twice**: once serially, once in four independent subprocesses, and compared both results to each other and to the fixed baseline.
- New `research_v1_runtime_pinned_parallel.py` eliminates the redundant serial re-run. It runs **exactly four independent suites** in one runner, requires valid output for every fixed suite, pins each suite's testcase identities/count/sha256 and rejects duplicates/missing/extra suites, recomputes the union digest vs the fixed 34-case baseline, and requires no-source-admission/no-profitability/no-Holdout/no-order authority flags.
- Additional `test_research_v1_runtime_pinned_parallel.py` has **8 synthetic controls** covering expected parity, missing/renamed/duplicate cases, failed status, elevated authority flags, unexpected suite, fixed four-process limit, and proof no serial reference process is invoked.
- Standalone read-only GitHub Actions `.github/workflows/indexalert-backtest-pinned-parallel-ci.yml` runs 8 existing adversarial parity tests and 8 new synthetic controls before executing four pinned suites. Pinned offline Python dependency list is unchanged; no broker or market data credentials read.

## Observed proof (two distinct GitHub Actions runs)

| Run | Trigger | Workflow | Exact pinned cases | Parallel offline 34-case test phase | Created-to-updated GitHub run elapsed* |
|---|---|---|---|---:|---:|
| [38466019576](https://github.com/kims34/openpilot-opkr/actions/runs/38466019576) | push | **SUCCESS** | **34/34, fixed SHA-256 match** | **2.8753 s** | approx. 37 s |
| [38466025500](https://github.com/kims34/openpilot-opkr/actions/runs/38466025500) | PR | **SUCCESS** | **34/34, fixed SHA-256 match** | **1.8763 s** | approx. 59 s |

*End-to-end estimates include queue / setup / install / artifact uploads and cloud-runner variability, so **they are NOT proof of overall workflow speedup**. All observed timing is **offline unit-regression time**, not an H5 or M20 trading backtest. No fresh holdout, parameter search, profitability/economics or official price data evaluation was performed.

## Decision and safety

**Result:** Redundant serial execution was removed in the alternative **experimental regression-only workflow** while preserving archived testcase baseline, exact per-suite/union identity, and no-trading flags. CI passed twice. The original serial-vs-parallel integrity workflow remains intact and available as an independent control. This does not justify merging a research/backtest performance change, promotion, changing the Frozen Champion, or enabling real orders.

**Current hard gates:** Official KRX historic market state/tradability and original OpenDART M20 fiscal disclosure PIT/operating-income matching still require independent admission. `m20_feature_pit_admitted=false`, `m20_performance_run_authorized=false` until externally proven. This change **does not address those blockers**.

Frozen H5, M20 preregistration, WF504/126/126, purge/embargo, PIT/labels, holdout/CPCV, taxes, costs, net EV, risk, Champion, and `ORDERING=false` remain unchanged. No branch merge, Railway deployment, holdings, keys, funds or live orders.
