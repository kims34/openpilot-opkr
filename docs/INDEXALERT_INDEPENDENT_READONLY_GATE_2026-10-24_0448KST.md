# IndexAlert independent profitability / runtime gate — 2026-10-24 04:48 KST

Read-only independent evidence audit. This is a **documentation-only** change on the isolated integration Draft PR #414 branch; no strategy, market source, workflow, specialist branch, policy, deployment, order, funds, permissions, Holdout, Champion or merge action.

## Direct immutable refs observed in this run

- Research `index-alert-research-v1` HEAD `3b8b7830612a6284d7c7a60628cb527cb741627a`; development `index-alert-position-regen-fix-v1` HEAD `1e6367d2863a86c3470da13d81a955d277eba485`. Verified via same-ref GitHub compare API.
- Integration Draft #414 pre-write HEAD `31268f5c39561906b5721dcf1132e2a77983cd7d`; original gate `docs/INDEXALERT_PROFITABILITY_INTEGRATION_GATE_2026-10-13.md` Git blob `984c933651f39f1ee9e26a1d7ac3893aaa5335be`. Latest preceding integration commit adds only `docs/INDEXALERT_INDEPENDENT_READONLY_GATE_2026-10-24_0417KST.md`.
- OpenDART Draft #412 `e82b26e2431ea15a42888f073a4b0b72a2e11ef6`.
- Optimization Draft #413 `f003ef6247e16fcc71bd3b1b20cd4904c4d984c0`; dependent runner Draft #418 `2f98401cc50a6c6a25808a98516efd5bf0c944ee`.
- KRX Draft #420 `fab3cbbd63a951a4e081f9e7f08c1391ca308581`, #422 `c14857620973531013799e44625d43080904fd5f`, #423 `0e38004363cac9fc4475556b3a1c445de9af407f`. All Draft/open/unmerged.

## NEW independent dependency-divergence proof: #418 versus #413

The GitHub compare endpoint for #418's declared base SHA `ca6c5d915d2c0e018f4aa9f82b4488038c16f8d3` to current #413 HEAD `f003ef6247e16fcc71bd3b1b20cd4904c4d984c0` returns **ahead 18, behind 0**, merge-base `ca6c5d915d2c0e018f4aa9f82b4488038c16f8d3`. Four changed paths: `INDEXALERT_BACKTEST_RUNTIME_OPT_2026_10_13.md`, `research_v1_runtime_manifest.py`, `research_v1_runtime_one_runner.py`, `test_research_v1_runtime_ci_integrity.py`.

Comparing #418 HEAD to current #413 HEAD returns **diverged**, ahead 18 / behind 49, same merge-base. Interpretation: #418's historic declared base is not the current #413 code; the GitHub PR synthetic merge commit `052cf67e45500baad771527753744289529ecbc2` used current #413 HEAD `f003ef...` and #418 HEAD `2f984...`. Therefore a success for the standalone #418 branch, its original 34-case archive, or candidate-only source checker cannot be transposed to the merged implementation. This comparison is a code-lineage observation, **not** an accusation of repository corruption or a merge approval.

Actual [#418 pinned archived run #39111405478](https://github.com/kims34/openpilot-opkr/actions/runs/39111405478) job `117628139395` **FAIL CLOSED**: `research_v1_runtime_manifest.py` expected Git blob `108f66714602a1bd3ae42c34dcca7c16e38f460b`, merged candidate observed `e0055c66c59398fd4a1158077446d886b54c4e37`. [Candidate-only run #39111405494](https://github.com/kims34/openpilot-opkr/actions/runs/39111405494) job `117628139749` SUCCESS but `all_transitive_imports_pinned=false`, `candidate_approved_for_merge=false`; GitHub artifact `12130632455` metadata digest `sha256:e3b11f93bd67cd246c0a81c599679c83dda15176ffc687699edf5bead5e46ad8`. Fixed 34-case digest `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34` is a prior reported CI value, **not independently rehashed here**. #413 [#38508247773](https://github.com/kims34/openpilot-opkr/actions/runs/38508247773) offline-only CI SUCCESS. Full-CI or real financial backtest speedup NOT VERIFIED. No re-pinning or optimization code modification.

## Official-source and operations evidence, no admission

- OpenDART #412 HEAD [#39884427765](https://github.com/kims34/openpilot-opkr/actions/runs/39884427765) and [#39884427805](https://github.com/kims34/openpilot-opkr/actions/runs/39884427805) both SUCCESS on offline guards only. Bounded official [#39884243351](https://github.com/kims34/openpilot-opkr/actions/runs/39884243351) 2/2 SUCCESS; GitHub artifact metadata ID `12471308613`, `sha256:02e829d3a5fdde8754f649431363c74221eb192b78b8237c911f74b54325820c`. This is a bounded completed-day filing index, not exact original public available-at or 2022/2021 first-filed consolidated 3-month CFS earnings semantic proof.
- Prospective chronology [#39972035700](https://github.com/kims34/openpilot-opkr/actions/runs/39972035700) job `120476944660` FAIL: `HTTP Error 404` for `/anchor/latest`; validation skipped. Root cause NOT VERIFIED; cannot grant chronology/PIT.
- KRX [#39714369438](https://github.com/kims34/openpilot-opkr/actions/runs/39714369438) and [#39714207925](https://github.com/kims34/openpilot-opkr/actions/runs/39714207925) synthetic-only SUCCESS, not independent actual official market-calendar/stock-status/corporate-action reconciliation. Historic private 1,565/1,565 raw weekday-pair integrity PASS is not tradability; unresolved 90 sessions, 27 nonpositive OHLC quarantines remain.
- Read-only watchdog [#40002116199](https://github.com/kims34/openpilot-opkr/actions/runs/40002116199) job `120580600571` SUCCESS; log says `M20 PIT admission: NOT ATTESTED; orders: DISABLED; holdout: NOT AUTHORIZED`. Artifact metadata ID `12523225244`, `sha256:f3cbc227c4990b437a075b43409e57ea23713db46c1fea7404b898a940195d64`. No downloaded-and-rehashed artifact proof. Job flags are not Railway live ORDERING attestation.
- Railway read-only `list_projects` returned `User input required but current turn is running in a non-interactive mode.` No production deployment/replica/logs or live ORDERING setting independently confirmed; no auth or permissions change attempted.

## Explicit PASS / FAIL / NOT VERIFIED

- **PASS (narrow):** named GitHub refs, current branch-divergence comparison, CI/job outcomes, selected GitHub artifact metadata and offline safety checks.
- **FAIL (fail-closed):** merged-candidate pinned archived manifest blob mismatch; prospective `/anchor/latest` HTTP 404 chronology anchor.
- **NOT VERIFIED:** first-submitted original 2022/2021 Q3 standalone consolidated 3-month operating-income account/period/unit/sign and first-public available-at; corrections chronology and as-of issuer/security map; official KRX market status/corporate actions/fillability; full independent source/data/code/Frozen-policy/runtime/evidence SHA-256 closure; fees, taxes, slippage, after-tax NetEV/PF/CAGR/MDD/ES95/99, concentration and temporal robustness; end-to-end speedup; Railway production ORDERING setting.

**Admission: NO-GO.** Do not run M20 economics, consume/reuse H5 Holdout, retune Frozen H5/Dynamic, modify M20 horizon20/purge20 or WF504/126/126/PIT/Purged/CPCV/Champion/Top3/NO_TRADE/cost-tax-risk thresholds. `ORDERING=false` remains mandatory. No orders, funds, account/auth/permissions changes, production deploy, automatic PR merge, or Champion promotion. Next independent owner proof: original source first-public chronology + CFS cell lineage, official KRX tradability/CA per date, and separately pinned full merged-source/runtime graph before any economic RUN. Avoid delegated specialist code changes.
