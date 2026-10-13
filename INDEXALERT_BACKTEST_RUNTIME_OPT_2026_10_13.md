# IndexAlert backtest execution environment — isolated optimization evidence

Date: 2026-10-13 KST. Scope: engineering-only, NOT a new trial, NOT a market-data source-admission certificate.

## Base and isolation
- Research source baseline: `index-alert-research-v1` at `3b8b7830612a6284d7c7a60628cb527cb741627a`.
- Engineering branch: `index-alert-backtest-runtime-opt-v1-20261013`.
- Do not alter research/dev branches, Frozen H5, M20 preregistration, 504/126/126, 20-session purge/embargo, 5-day H5 horizon, taxes, costs, champion/holdout gates, or `ORDERING=false`.

## Existing bottlenecks identified by code inspection
1. `.github/workflows/indexalert-research-v1.yml` builds a preliminary marcap PIT panel and then executes four dependent research analyses sequentially in its `pit-preliminary` job. Its `smoke-test-and-backtest` job likewise executes multiple analyses sequentially. These are archived developmental methods, not approved official profitability verdicts.
2. `.github/workflows/indexalert-research-v1-fast.yml` restores year/date/name caches and computes six challenger recipes sequentially. A matching path/date cache key alone is insufficient proof of source or policy immutability. This archived workflow must NOT be replayed as an independent OOS result.
3. `research_v1_supervised_cache.py` already validates policy and a source fingerprint, but its underlying fingerprint uses aggregate 64-bit hashes; it is not a source-byte SHA-256 or independent admission certificate. Current code invalidates mismatched existing labels instead of silently accepting them, which must be preserved.
4. `research_v1_cost_sensitivity.py` computes selection once then multiple cost scenarios; the cost scenarios can be fan-out tasks only when the identical fully admitted immutable selection/evaluation data exist. Risk/ES and cost stress can also be independent consumers of one pinned portfolio path; model fitting, fold ordering, and capital-state transitions must NOT be parallelized across dependencies.

## Implemented (without running profitability)
- `research_v1_runtime_manifest.py` builds a SHA-256 content-addressed key of exact source bytes, calculation code bytes, independent source receipt, frozen policy and runtime lock. A missing source admission flag/hash, altered input, code, policy or runtime makes a cache non-reusable. It never authorizes evaluation, holdout or orders.
- Synthetic regression tests verify deterministic same-byte reuse, tamper rejection, all required admission gates, and no order/holdout authorization.
- New isolated GitHub Actions workflow runs existing **offline unit tests only**, independently by cost/risk/frozen-gate/cache groups, alongside one serial control; comparison rejects even one different test identity or status. Outputs wall-clock test process timings, SHA-256 testcase parity and artifacts; measures no backtest wall-time improvement.
- No data acquisition, original evidence mutation, market-model fitting, numerical profitability generation, or consumed holdout read.
- Tests using synthetic market bars are only software regression fixtures; success does not admit financial source data.

## Preparation for future data-admitted economic evaluation
Only after official source and PIT gates independently pass:
- Persist one verified, immutable source panel and lineage receipts. Never trust GitHub cache name/date alone; require content and policy digest parity.
- Build pinned supervised features and fixed original rank/entry/exit paths once. Reuse only when byte-identical receipt, code and policy hashes match; any upstream change invalidates dependent artifacts.
- Fan-out *post-selection* cost, risk/ES and sensitivity analyses as read-only consumers of identical pinned artifacts; independently reproduce serial results before promotion. Keep cash days and stateful trade-position transitions ordered.
- Keep a fixed scheduler barrier before joining outputs. No silent missing-job substitution, no rank4+ backfill, no false `PIT_ADMITTED` from a local manifest, and no new official returns until external admission passes.
- Benchmark end-to-end on admissible, previously sanctioned replay only; distinguish setup time, data acquisition time, model time and post-processing time. The new CI measures **offline regression test duration only**, not expected full profitability run speed.

## Admission / authorization state
- H5: archival developmental evidence only; no new holdout or promotion.
- M20: `NOT_EVALUABLE_NEW_EVIDENCE_REQUIRED` until multi-year original-filing PIT evidence and official KRX tradability/economics are admitted.
- KRX unverified status/affected symbols are never converted to eligible positions by cache reuse.
- `ORDERING=false`, no live orders, funds transfer, permission changes or Champion mutation.

## CI evidence
See the dedicated GitHub Actions job run and artifact `runtime-opt-parity-report` on this branch for observed serial/parallel test phase timings, exact testcase parity and outcome. Do not claim a speedup until the job completes and the report says `test_outcomes_identical=true`.

## CI observed outcome — 2026-10-13 KST
- [CI run 38381997417](https://github.com/kims34/openpilot-opkr/actions/runs/38381997417), branch `index-alert-backtest-runtime-opt-v1-20261013`, workflow code revision `55e7fe2b3fe322e39f817914ff1ed5b589bbe0da`.
- Serial control, four independent suites (cost, risk, gates, cache), and exact parity aggregation: **all six jobs succeeded**.
- Exact **34 test cases** matched in identifier and pass status; canonical testcase digest SHA-256: `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34`.
- Serial regression test process: **2.8951 s**. Parallel longest suite test process: **2.7165 s**. Test-phase speed ratio **1.066x** (approximately 6.2% reduction); excludes environment setup, queueing, installation, artifact I/O and aggregation.
- **Do not claim full CI wall-time speedup or actual trading backtest speedup**: these were not measured, and independently admitted source panels for official evaluation are unavailable.
- [Parity artifact](https://github.com/kims34/openpilot-opkr/actions/runs/38381997417/artifacts/11803677039), ZIP digest `sha256:6ce417d0474c2b89789f0a7d4d7d4ee7f06e6751acab0327722b885c0d8abd01`.
- This passing run authorizes **no performance evaluation, Holdout, champion promotion, live trading or data-source admission**.

## Independent second CI reproduction on draft PR
- [Draft PR #413](https://github.com/kims34/openpilot-opkr/pull/413) against `index-alert-research-v1`, **unmerged**. Review is separate from approved changes.
- [Pull-request CI run 38382214223](https://github.com/kims34/openpilot-opkr/actions/runs/38382214223): second independent execution; **6/6 jobs passed**, exact **34/34** test-case identity/outcome parity. Testcase digest is identical to first run: `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34`.
- Second-run test-process durations: serial **4.8867 s**, parallel longest suite **2.2094 s**, apparent phase ratio **2.212x**. These changes between runners illustrate why one must **not** promise a backtest/CI overall acceleration from microbenchmark phase timings.
- Frozen research branch and production environment remain unchanged. No official profitability/performance trial authorized or executed.


## 2026-10-13 next-cycle integrity repair (isolated branch, no profitability execution)
- **Observed previous false-pass hole:** `research_v1_runtime_ci.py` compared the serial and combined parallel cases but did not pin the **expected** testcase set; if both dropped the same case, their shorter result could match and be incorrectly accepted.
- Immutable expectation grounded in previously independent [run 38381997417](https://github.com/kims34/openpilot-opkr/actions/runs/38381997417) and [38382214223](https://github.com/kims34/openpilot-opkr/actions/runs/38382214223): exact 34-case SHA `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34`. Suite test-count / SHA checks are cost=9/`0a11d4ec...`, risk=9/`49185a1d...`, gates=8/`717cd517...`, cache=8/`2353b839...`; numbers/digests are fixed from **previous** immutable execution logs, not regenerated from the latest shortened run.
- [Code commit a9b2c90](https://github.com/kims34/openpilot-opkr/commit/a9b2c90b6f4da209aefed374210a47e434f7ce77) requires exact per-suite test files/count/pinned testcase SHA, serial 34 digest, case uniqueness, finished/positive process timing, false PIT/evaluation/ordering flags.
- [Test commit 0ef696c](https://github.com/kims34/openpilot-opkr/commit/0ef696c104c4cc0e806c95f7db20a73df7c20c22) adds synthetic, offline adversarial tests of symmetric case deletion/rename, suite/file mislabel, runtime flags, invalid timing/count/digest, duplicates and empty collection.
- [Workflow commit 4959c45](https://github.com/kims34/openpilot-opkr/commit/4959c4518c593dc13d097657ff859359db483f89) runs the adversarial integrity unittest before the original cost/risk/gates/cache serial and parallel control. [Result run 38413552682](https://github.com/kims34/openpilot-opkr/actions/runs/38413552682) **started/pending at first observation; do not mark PASS until jobs and pinned case digest verified**.
- **Next exact step:** inspect run 38413552682 job summaries and its parity artifact. If failures, fix only isolated CI/test-report verification until all jobs pass; record the actual 34/34 digest and serial/parallel process timings separately from overall CI and full backtest time. Keep draft/unmerged; no source admission, new performance run or production deployment.


## 2026-10-13 pinned-case correction — actual GitHub Actions PASS
- The safety fix is independently verified by [GitHub Actions run **38413552682**](https://github.com/kims34/openpilot-opkr/actions/runs/38413552682), after [code a9b2c90](https://github.com/kims34/openpilot-opkr/commit/a9b2c90b6f4da209aefed374210a47e434f7ce77), [adversarial tests 0ef696c](https://github.com/kims34/openpilot-opkr/commit/0ef696c104c4cc0e806c95f7db20a73df7c20c22), [CI wiring 4959c45](https://github.com/kims34/openpilot-opkr/commit/4959c4518c593dc13d097657ff859359db483f89): **six of six Actions jobs SUCCESS**, plus **8/8 synthetic parity attack tests passed** within the serial job. No price data, new market APIs, model fitting or Holdout read.
- Four independent suites: cost 9 tests SHA `0a11d4ec...`, risk 9 SHA `49185a1d...`, gates 8 SHA `717cd517...`, cache 8 SHA `2353b839...`. Serial 34 tested, combined 34, canonical identity/outcome SHA `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34` **equal to both prior immutable runs**. The synthetic adversarial test explicitly shows symmetric serial/parallel case omission, renaming, bogus digest, duplicate and permission flag fail closed.
- True regression-test-process durations observed on run: serial **2.2589 s**, longest parallel **2.8422 s**, `test_phase_speedup_only=0.795` (parallel **slower**, not faster). Full CI wall-clock speed and original H5/M20 backtest execution speed **NOT MEASURED**. Never advertise a full-backtest acceleration on the basis of six green CI jobs.
- Recorded immutable parity artifact ID [11822958491](https://github.com/kims34/openpilot-opkr/actions/runs/38413552682/artifacts/11822958491), artifact ZIP SHA256 `20b0f1c0a54557b7a31364f92c79f53f91177e4e497f0089cb218a781e893722`. This ZIP hash is distinct from its internal case digest.
- **Next exact step:** because parallel is slower in this run, compare actual per-job setup/install/queue/artifact overhead (not model metrics) on prior two runs and new run, and avoid complex fan-out until a measured whole-workflow advantage is shown. Security hardening PASS; performance acceleration remains **NOT VERIFIED**. Preserve existing H5/M20 prereg, source/PIT gates, Champion and `ORDERING=false`. Draft PR stays unmerged.


## 2026-10-13 log-derived CI overhead audit and safer candidate (NOT yet validated)
- Directly inspected GitHub Actions raw job logs from [run 38381997417](https://github.com/kims34/openpilot-opkr/actions/runs/38381997417) and [run 38413552682](https://github.com/kims34/openpilot-opkr/actions/runs/38413552682). This is an observational log comparison, not a backtest benchmark or GH Actions queue-time measurement.
- From first timestamp across all six job logs to last timestamp: **38.51 sec** (38381997417), **47.80 sec** (38413552682). This span includes overlap, inter-job scheduling, steps and last post-job cleanup, but **does not include pre-run queue waiting or assert actual workflow billing/runtime**. Latest run: serial job log **24.36 s**, risk job **34.86 s**, parity aggregation job **5.51 s**. Previous run: serial **26.86 s**, risk **28.02 s**, parity **4.42 s**.
- Pip-step begin to suite-step begin on latest four matrix jobs (cost/risk/gates/cache) was **19.96 / 18.70 / 20.00 / 17.32 sec**, vs observed original suite CPU/subprocess wall **~1–3 sec**. This interval includes pip installation plus step transition, **not strictly pip-only**. Launching a runner for each tiny suite repeats dependencies and artifact handling; simple four-runner matrix is not a proven optimization.
- [Source candidate commit 7d11c29](https://github.com/kims34/openpilot-opkr/commit/7d11c29101aaed8ac34377fbf790660c52bc3ddc) adds `research_v1_runtime_one_runner.py`, a **not yet executed** single-runner/single-install four-subprocess comparison: pinned 34-case reference, four independent children, fail-closed `_acceptable` and canonical parity before reporting performance, no market input or Holdout. **No speedup claim, no independent validation of this new source yet.**
- Attempt to wire the one-runner candidate into isolated `.github/workflows/indexalert-backtest-runtime-opt-ci.yml` was **blocked by tool security review**. No workflow change from that attempt, no alternate bypass or merge; existing workflow retained its original 6-job shape. [Run 38417102159](https://github.com/kims34/openpilot-opkr/actions/runs/38417102159) triggered on branch/PR and **6/6 jobs passed**, eight synthetic attack tests passed, canonical 34-case digest remained `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34`; latest isolated existing-suite timings serial 1.9582 sec vs parallel longest 2.1198 sec (ratio **0.924**). This run **did not execute the new one-runner benchmark**.
- **Next exact step:** obtain permitted isolated CI review/validation of the new candidate or withdraw it if unreviewed; do not represent source-only commit as run-verified. Benchmark same-runner with one dependency installation and compare job-level setup, test phase, artifact/upload/aggregation separately. Review immutable source/policy SHA and dependency attestations before any admitted-data work. Keep PR #413 draft and no production change.
