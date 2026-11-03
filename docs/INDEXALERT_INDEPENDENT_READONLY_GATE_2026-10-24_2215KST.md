# IndexAlert independent read-only gate — 2026-10-24 22:15 KST

Scope: independent integration review only. No model/market-data replay, PIT admission, M20 economic run, holdout reuse, trading, code/workflow change, deployment, or merge. All references below were read via connected GitHub API in this cycle. Railway read-only listing was attempted but requires interactive authorisation.

## Immutable reference ledger (read-only)
- Research `index-alert-research-v1` HEAD `3b8b7830612a6284d7c7a60628cb527cb741627a` (resolved by fetch_commit on branch ref).
- Development `index-alert-position-regen-fix-v1` HEAD `1e6367d2863a86c3470da13d81a955d277eba485` (same method).
- Integration Draft PR #414 pre-write HEAD `adffae869397f5299c0936078ede7e99db1c8aff`, source integration gate Git blob `984c933651f39f1ee9e26a1d7ac3893aaa5335be`.
- OpenDART Draft #412 `e82b26e2431ea15a42888f073a4b0b72a2e11ef6`.
- KRX Draft #420 `fab3cbbd63a951a4e081f9e7f08c1391ca308581`, #422 `c14857620973531013799e44625d43080904fd5f`, #423 `0e38004363cac9fc4475556b3a1c445de9af407f`.
- Optimization Draft #413 `f003ef6247e16fcc71bd3b1b20cd4904c4d984c0`, dependent one-runner Draft #418 `2f98401cc50a6c6a25808a98516efd5bf0c944ee`.

## New independent boundary check this cycle
- The connected API returned **70 changed paths for Draft PR #414; all 70 are within `docs/`**, no non-document paths in the PR's reported changed-file list. This is a metadata/path-level documentation-only check, **not** an audit of every commit's runtime side effects or a guarantee against future updates. No branch merge or deployment authorised.
- PR #413 changed-file list includes runtime manifest, tests, workflow and requirements; PR #418 includes separate candidate runner/source/env gates and workflows. These specialist-owned code paths were not edited.
- Independently fetched actual [#413 run 38508247773](https://github.com/kims34/openpilot-opkr/actions/runs/38508247773) exact-parity job `115670744341` log: `cases=34`, canonical case digest SHA-256 `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34`, `test_outcomes_identical=true`, `ordering=false`, `admissible_profitability_generated=false`, `actual_backtest_speedup_measured=false`, `ci_end_to_end_speedup_measured=false`. Serial regression 1.7650 s vs longest parallel 2.7079 s = **0.652x**, negative regression-phase timing. Five downloaded CI artifact ZIP SHA digests were checked by the Action downloader; no independent local ZIP byte rehash performed.
- Independently fetched [#418 run 39111405478](https://github.com/kims34/openpilot-opkr/actions/runs/39111405478) job `117628139395` log: **FAIL** `SourceDriftError` for `research_v1_runtime_manifest.py`: expected Git blob `108f66714602a1bd3ae42c34dcca7c16e38f460b`, observed `e0055c66c59398fd4a1158077446d886b54c4e37`. This is a **source-identity mismatch**, not evidence of corrupted KRX/OpenDART data. Do not silently re-pin or bypass; wheel/native/transitive runtime identity still not independently established.
- Independently fetched KRX [#420 run 39714369438](https://github.com/kims34/openpilot-opkr/actions/runs/39714369438) job `119612852155`: offline synthetic groups 39 + 25 + 8 = **72 PASS**. These do not inspect protected 2021/2022 Railway original private volumes or authenticate historical market sessions/trading status.
- Other KRX #423 [run 39714207925](https://github.com/kims34/openpilot-opkr/actions/runs/39714207925) completed successfully on **offline-only** candidate logic, not exact private 14-day original reconciliation. OpenDART #412 earlier official [run 39884243351](https://github.com/kims34/openpilot-opkr/actions/runs/39884243351) remains a narrow later-amendment census, not original quarterly CFS/PIT admission.
- Railway `list_projects` read-only call returned: `User input required but current turn is running in a non-interactive mode.` No deployment IDs, fresh runtime logs, private original bytes or actual live `ORDERING` value were obtained. **Do not claim live ORDERING verification.**

## Gate matrix and prohibition
| Independent gate | Verdict | Why |
|---|---|---|
| Git HEAD / Draft PR metadata | PASS (limited) | API commit refs and Draft state returned; #414 path list docs-only |
| Synthetic parity / isolated safety | PASS (limited) | CI logs above; not market source or economic admission |
| #418 pinned archived source | FAIL | Explicit archived blob mismatch in real CI |
| OpenDART original 2022/2021 3-month consolidated operating profit, original/correction semantic lineage, exact public available-at | NOT VERIFIED | Original filing financial facts and exact as-of timestamp not established |
| Issuer/security historical PIT map | NOT VERIFIED | No independently admitted mapping |
| Official KRX calendar, per-security halt/delist, corporate action and actual fillability | NOT VERIFIED | Historical private source comparison/official vintage not independently established; 90 uncertain sessions and 27 OHLC vetoes remain |
| Commissions/taxes/slippage/impact, NetEV/PF/CAGR/MDD/ES95/99, return concentration, temporal robustness | NOT VERIFIED / NOT EVALUABLE | Admitted source and immutable M20 economic run absent |
| Production Railway deployment/logs, live ORDERING | NOT VERIFIED | Interactive connector authorisation required |

**Decision: M20 PIT admission NO-GO; M20 profitability execution NO-GO.** Preserve Frozen H5, M20 horizon20/purge20, WF504/126/126, label PIT, Purged/CPCV, sealed independent Holdout, Champion, Top3/NO_TRADE, cost/tax/risk thresholds. `ORDERING=false` is mandatory but live setting unverified. Do not run economic experiments, reuse consumed Holdout, modify specialist branches, change workflow/permissions, move funds, place orders, deploy, merge, or promote.

Next admissible evidence: source-owner OpenDART original available-at/first 3-month CFS lineage, KRX-owner authenticated original private calendar/security status/actions, optimization-owner independently attested archived-source and wheel/native dependency identity. Railway operational verification requires explicit interactive connection authorisation. No security bypass attempted.
