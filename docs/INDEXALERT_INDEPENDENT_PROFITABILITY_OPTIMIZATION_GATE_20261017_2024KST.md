# IndexAlert independent read-only profitability and offline optimisation gate — 2026-10-17 20:24 KST

Scope: evidence-only audit. No source/PIT/holdout/Champion changes, no official market return or model search, no M20 economics, no deployment, merge, orders, funds or permissions. ORDERING=false. This document does not grant approval.

## Exact repository evidence
- Research `index-alert-research-v1` SHA `3b8b7830612a6284d7c7a60628cb527cb741627a` (GitHub compare base).
- Development `index-alert-position-regen-fix-v1` SHA `1e6367d2863a86c3470da13d81a955d277eba485` (GitHub compare base).
- Draft PR #414 HEAD `9ae180487d7add1c6dfbc38a71762a98e638ebbf`, integration gate blob `984c933651f39f1ee9e26a1d7ac3893aaa5335be`.
- Draft PR #412 HEAD `dcb4a6d30c47fd84a4e7667453af5bd5a6bcf1d0`.
- Draft PR #413 HEAD `f003ef6247e16fcc71bd3b1b20cd4904c4d984c0`.
- Draft PR #418 HEAD `c9b125ff5d3d080848dd9ab1f23a8755af4faaa9`.
- KRX Draft PR #420 HEAD `588bc296eafa58525954f691a763ff6eb413f053`, #422 HEAD `c14857620973531013799e44625d43080904fd5f`.
- All PRs above open and draft at inspection; mergeability metadata is not an independent source/CI/PIT admission.

## Current observed CI (GitHub Actions)
- #412 HEAD runs 39001960412 (12/12 financial viewer-section offline synthetic tests, success) and 39001960323 (13/13 first-original TOC offline synthetic tests, success). No actual initial 2022/2021 consolidated standalone three-month operating profit, original-vs-amendment economic semantics, complete available-at/PIT or issuer-security history proven.
- KRX #420 HEAD runs 39001950024 and 39001949991 success. #422 run 39001836000: 12/12 synthetic private 2021 day-set tests PASS, including count-equal-but-date-different rejection and double-pass SHA mutation rejection. Actual private 261-day comparison and official exchange tradability/PIT remain NOT VERIFIED.
- #413 HEAD run 38508247773: six jobs success, fixed 34-case digest `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34`, serial 1.7650s vs parallel 2.7079s (ratio 0.652); performance gain FAIL for that run.
- #418 HEAD run 38822156136: archived-source gate FAIL, `research_v1_runtime_manifest.py` expected blob `108f66714602a1bd3ae42c34dcca7c16e38f460b`, observed `e0055c66c59398fd4a1158077446d886b54c4e37`. Run 38822156164 candidate proof success with 34-case digest, but its own emitted `all_transitive_imports_pinned=false` and `candidate_approved_for_merge=false`. Run 38822156116 one-runner test success with same 34-case digest; serial subprocess 2.5989s vs parallel group 2.6011s (ratio 0.9991). No full CI or actual approved economic-backtest acceleration proven.
- A `RUNTIME_OPT_RUN` cost suite with test_count=0 appears inside adversarial synthetic candidate-gate tests, not the accepted pinned 34-case production parity; do not misclassify it as a passing actual cost regression. Runtime CI has pinned cost suite 9 cases.
- PR #418 candidate gate checks selected files only; its own report disclaims all transitive dependency pinning. Successful candidate CI cannot override failing archived-source gate or certify combined PRs.

## Railway read-only observation
- IndexAlert production environment `83d5840b-270e-4d3f-a941-a37fd4a55ff7`, pendingWork empty. KRX historical worker active deployment `16c93d7c-7cd0-4d84-a327-298d2805376c`, deployed commit `1e6367d2863a86c3470da13d81a955d277eba485` on 2026-10-12.
- Worker runtime log `INDEXALERT_MISSING_2017_2022_INTEGRITY_FINAL`: 1,565/1,565 weekday original pairs stored, invalid pair count 0, six-year aggregate fingerprint `e2503a3bc623d4386e5783ec19272916fe6abba9bc191c14040d2c0831c7f01a`; 90 unverified calendar/source-gap days. This is a worker-emitted integrity result, not an independently rehashed private original-byte proof and not official tradability.
- Runtime service `indexalert-runtime`: running 1/1, deployment `eaaa9f67-b9f2-41d2-832c-7d6fad9b9b00`. Kiwoom REAL read-only service `indexalert-kiwoom-real-readonly`: 0 running/1 crashed replicas despite deployment status SUCCESS. No operational change made. No new deployment staged.
- Private original bytes, full original DART receipts and true official exchange security-state and corporate-action history were not independently available through this audit read. No private raw data copied to GitHub.

## Gate verdict (PASS / FAIL / NOT VERIFIED)
- Source metadata / pinned 34 synthetic case digest: PASS (bounded offline scope only).
- KRX worker-reported persisted weekday-pair integrity: PASS as logged, independent raw byte rehash NOT VERIFIED.
- DART first original 2022/2021 three-month CFS operating-income period and amendment lineage: NOT VERIFIED.
- Public available-at/PIT, historical issuer/security mapping: NOT VERIFIED.
- Official KRX exchange calendar, halt/delist/corporate action, tradability and fill: NOT VERIFIED.
- Pre-fixed commission, taxes, spread/slippage, execution capacity: NOT VERIFIED.
- After-tax NetEV, PF, CAGR, MDD, ES95/99, return concentration, date-cluster robustness: NOT VERIFIED (not run).
- PR #418 archived-source exact integrity: FAIL; candidate-only proof PASS with transitive pinning NOT VERIFIED.
- Fail-closed cache synthetics: partial PASS, independent PIT admission certificate authenticity NOT VERIFIED.
- Read-only independent postprocessing parity: PASS for 34 offline cases; end-to-end speedup NOT VERIFIED.
- M20 performance run: BLOCKED; H5 failed/consumed holdout not reusable; Frozen/Champion/Top3/NO_TRADE unchanged; ORDERING=false.

Next permitted steps: source owners independently attest exact original bytes, available-at, financial semantics and official KRX date/status/corporate-action/filled-trade cost evidence. Optimisation owner reconciles immutable archived blob drift and transitive dependencies, fixes CI path coverage only after explicit separate safety review, and measures allowed synthetic end-to-end wall time without changing Frozen rules. Do not merge PR #413/#414/#418 or promote any Champion.