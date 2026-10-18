# IndexAlert isolated offline backtest runtime audit — 2026-10-15 07:47 KST

Scope: PR #413/#418 only. Read-only GitHub Actions and Railway production checks; no PR #414 profitability work, no new official data/model/profitability runs. This document is evidence only, NOT admission or merge authorization.

## Exact immutable references
- PR #413 DRAFT, HEAD `f003ef6247e16fcc71bd3b1b20cd4904c4d984c0`, base `index-alert-research-v1`; GitHub run 38508247773: 6/6 jobs success, including synthetic mutation and 34-case pinned parity.
- PR #418 DRAFT, HEAD `f82e755ff74b1ce393109a3b281d6f34344f4306`, base `index-alert-backtest-runtime-opt-v1-20261013`, PR base SHA `ca6c5d915d2c0e018f4aa9f82b4488038c16f8d3`. GitHub compare of that base SHA to current #413 HEAD: 18 ahead, zero behind. This is not the five-commit delta from a later candidate checkpoint.
- GitHub Actions 38597969010 pinned archived-source replay: FAIL CLOSED at `research_v1_runtime_manifest.py` archived Git blob `108f66714602a1bd3ae42c34dcca7c16e38f460b` vs current `e0055c66c59398fd4a1158077446d886b54c4e37`. No pinned-parallel artifact produced in that failed job. Do NOT treat as a regression parity pass.
- GitHub Actions 38597969021 candidate-merge proof: PASS, 21 exact Git blob files, four reviewed candidate blobs, immutable 34-case SHA-256 `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34`; explicitly `all_transitive_imports_pinned=false`, `candidate_approved_for_merge=false`, `official_pit_admitted=false`.
- GitHub Actions 38597969051 one-runner synthetic offline parity: PASS, but not full CI or real-backtest acceleration. Archived runtime check verified 22 distribution versions and Python 3.12; exact wheel hashes and native OS dependency identities NOT VERIFIED.
- PR #413 manifest Git blob `e0055c66c59398fd4a1158077446d886b54c4e37` requires six PIT/source/tradability gates, literal false for holdout/live permissions, explicit source/code hashes and policy/runtime/receipt SHA-256; rejects symlink, nonregular file and in-flight file substitution. Structural software safety only: supplied receipt authentication is external and multi-file atomicity is not established.
- PR #418 candidate gate Git blob `9174fd9c3e0155678e6a45a3112bf2eaa2d1afce` explicitly rejects base/HEAD drift, checks 21 direct blobs, and does not attest indirect imports. Candidate merge safety remains NOT VERIFIED. Dependency-ordered retraining and capital transitions must not be parallelised.

## Railway read-only
- Project IndexAlert production; pendingWork empty, no changes staged.
- `indexalert-runtime` ONLINE 1 running replica. `db-query-readonly` OFFLINE with 1 critical; `indexalert-push` and `indexalert-backend` OFFLINE with warnings; `indexalert-kiwoom-real-readonly` shows ONLINE but replicaStatus running=0, crashed=1. Do not infer health from UI state alone.
- Runtime logs read-only; no independent production `ORDERING` environment variable verification in this audit. CI outputs show `ordering=false`; enforce `ORDERING=false` unchanged.

## Gate
Offline synthetic software parity: PASS in scoped CI.
Archived source replay on changed manifest: FAIL CLOSED (expected safety stop).
Candidate 21-blob lineage: PASS (non-admitting).
Full transitive dependency, wheel/OS provenance, integrated merge safety, production speedup: NOT VERIFIED.
Official PIT approval, actual M20 performance, Holdout, Champion: NOT AUTHORIZED.
No orders, funds, credentials, permissions, deployment, merge, or strategy policy change made.

Next safe independent work: review indirect import graph and exact dependency artifacts under offline-only synthetic CI; preserve archived source gate and add a distinct non-admitting candidate gate, never rewrite archived baseline. Require explicit separate authorisation for any later merge or operational action.

Sources:
- https://github.com/kims34/openpilot-opkr/pull/413
- https://github.com/kims34/openpilot-opkr/pull/418
- https://github.com/kims34/openpilot-opkr/actions/runs/38508247773
- https://github.com/kims34/openpilot-opkr/actions/runs/38597969010
- https://github.com/kims34/openpilot-opkr/actions/runs/38597969021
- https://github.com/kims34/openpilot-opkr/actions/runs/38597969051
