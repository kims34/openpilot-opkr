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


## 2026-10-13 read-only downstream artifact integrity (post-selection engineering only)

Continuation on the **same isolated** PR #418, without changing original research or production code.

- `research_v1_runtime_handoff.py` binds exact output artifact SHA-256s to a caller-supplied upstream cache-key SHA-256. It rejects missing, changed, symlinked, traversing, absolute, duplicated or extra/missing artifact paths; output manifests are deterministic and carry explicit false evaluation/PIT/holdout/orders flags.
- `test_research_v1_runtime_handoff.py` adds **six** synthetic-only corruption, input-key drift and unauthorized-source/permission tests. This is *local byte integrity*, NOT cryptographic publisher authentication, original filing completeness, official KRX status, or a stand-alone `PIT_ADMITTED` certificate. A separately authenticated external receipt remains compulsory for real-source use; callers must not fabricate an admission receipt.
- No model re-fit, trading data download, strategy change, source PIT admission, financial performance computation, holdout read, account keys or Railway deployment.

**Independent GitHub Actions proof** at code revision `f34fccc229147b13e5e16dbf44e6ada7ba93260b`:

| Run | Trigger | Status | Synthetic negative controls | Exact pinned regression | Serial test process | Concurrent test group | Whole CI run approximate |
|---|---|---|---|---|---:|---:|---:|
| [38416831534](https://github.com/kims34/openpilot-opkr/actions/runs/38416831534) | Push | PASS | Existing 8 + one-runner 4 + new handoff 6 PASS | 34/34 SHA identical | 2.4711 s | 2.3951 s | 39 s |
| [38416843840](https://github.com/kims34/openpilot-opkr/actions/runs/38416843840) | Draft PR | PASS | Existing 8 + one-runner 4 + new handoff 6 PASS | 34/34 SHA identical | 2.6581 s | 2.5902 s | 52 s |

Exact pinned SHA256 of 34 regression test cases and outcomes (same as historic fixed baseline): `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34`.

**Speed finding:** One runner's four subprocesses are only ~1.032x and ~1.026x faster than its serial regression reference for these new executions. Total CI wall times vary substantially; this is not proof of CI speedup or actual H5/M20 profitability backtest speedup. Do not claim a production optimization from these synthetic/offline tests alone. Keep both PR #418 and PR #413 unmerged; `ORDERING=false`.
