# IndexAlert single-runner offline runtime comparison — independent branch

Date: 2026-10-13. Scope: execution-engineering regression only; NOT an official PIT admission, NOT new strategy/OOS/holdout/profitability testing, NOT approved trading. Original base: `index-alert-backtest-runtime-opt-v1-20261013` HEAD `ca6c5d915d2c0e018f4aa9f82b4488038c16f8d3`. Independent Draft [PR #418](https://github.com/kims34/openpilot-opkr/pull/418) targets the existing optimization branch, not the research or production branch.

## Hypothesis and implementation

The prior four-matrix-runner + serial + artifact aggregation CI repeated runner provisioning and dependency installation. Try **one** GitHub runner with a single pinned Python environment: execute the **unchanged, pinned 34-case** reference suite serially, launch four isolated pytest subprocesses via a four-worker executor, then run the existing fail-closed serial/parallel digest comparison. Isolation uses separate JSON and JUnit report paths; model fitting, fold ordering, stateful portfolio/capital, holdout and source panels are untouched.

Code:
- `research_v1_runtime_single_runner.py`: orchestration, strict child exit-code checks, output gate, serial / concurrent subprocess timing, exact existing 34-case parity verification.
- `test_research_v1_runtime_single_runner.py`: synthetic-only matching control, unexpected test identity, failure-status, and invalid parallelism tests.
- `.github/workflows/indexalert-backtest-single-runner-ci.yml`: standalone Actions runner installing already pinned offline CI requirements once, running the **8 prior adversarial identity controls** and **4 new synthetic tests**, then the preexisting 34-case regression in both modes. No external market/broker access and no secret or ordering permission.

## Actual CI evidence (verified, no invented speedup)

| Independent run | Workflow event | All jobs | Serial one-runner regression subprocess | Four-suites parallel group | Both-mode verification phase | Full GitHub run (created→updated, approximate) |
|---|---|---|---:|---:|---:|---:|
| [38415661452](https://github.com/kims34/openpilot-opkr/actions/runs/38415661452) | push | 1/1 success | 2.5426 s | 2.3948 s | 4.9383 s | 44 s |
| [38415772193](https://github.com/kims34/openpilot-opkr/actions/runs/38415772193) | PR | 1/1 success | 2.8371 s | 2.5386 s | 5.3767 s | 37 s |

- Both runs: exactly **34/34 pinned test identities/results**, canonical SHA-256 `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34`. Preexisting adversarial integrity tests and new synthetic failure tests all passed.
- One-runner concurrent execution was modestly faster **within the regression subprocess phase** (~1.062x then ~1.118x), but this is **not a trading backtest or overall CI speedup claim**.
- Prior **different** six-job original workflow runs [38413767425](https://github.com/kims34/openpilot-opkr/actions/runs/38413767425) and [38414002495](https://github.com/kims34/openpilot-opkr/actions/runs/38414002495) completed in approximately 47 s and 51 s, respectively. The newer **single-job** approach completed in ~44 s and ~37 s. These are uncontrolled separate runner/time runs and do not establish statistically reliable end-to-end performance improvement. Each one-runner run deliberately executes serial **and** parallel tests for parity validation, whereas a future productionized test-only CI would need a separate design and validation.
- GitHub run metadata `created_at → updated_at` is used for approximate end-to-end observations. Workflow-start, setup, queue, install, artifact I/O and test subprocess times are not interchangeable.
- **Actual H5/M20 profitability backtest acceleration: NOT VERIFIED.** Eligible original-filing PIT and historical official KRX tradability/economics remain external gates. Never treat synthetic fixtures as admitted source data.

## Decision and next gated steps

This optimization is **engineering-safe experimental proof**, not a merge/promotion approval. Keep [PR #418](https://github.com/kims34/openpilot-opkr/pull/418) Draft and keep [PR #413](https://github.com/kims34/openpilot-opkr/pull/413) separate/unmerged. The small test phase and variable total CI times do not justify replacing frozen evaluation workflows. No legacy candidate replay, source refresh, parameter search, new profitability testing, holdout read, Champion promotion, Railway deployment, key exposure or real order.

If independently admitted official PIT evidence ever becomes available and there is a separately authorized identical fixed replay, pin the exact upstream panel/receipt/code/policy/runtime bytes before fan-out, keep all stateful transitions serial, then compare complete deterministic results and real end-to-end timing. Until then continue only offline tests and performance engineering.

Unchanged: H5 Frozen, M20 preregistration, WF504/126/126, 20-session purge, PIT/label/CPCV/holdout, costs/tax/NetEV/risk/Champion, `ORDERING=false`.
