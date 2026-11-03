# IndexAlert independent profitability / isolated runtime audit — 2026-10-28 07:18 KST

> Documentation-only read-only audit. **NO-GO** for M20 PIT admission and economic backtest. This note neither grants data/source admission nor authorises orders, deployment, merge, Champion promotion or consumed Holdout reuse.

## Snapshot and scope

Checked current GitHub PR metadata, exact branch commit objects, repository Actions collection (latest returned run 40574617617 created 2026-10-27 20:03:29 UTC), selected decoded job logs and exact implementation files. All listed PRs remain open Draft.

| Source | Exact HEAD |
| --- | --- |
| Research `index-alert-research-v1` | `3b8b7830612a6284d7c7a60628cb527cb741627a` |
| Development `index-alert-position-regen-fix-v1` | `1e6367d2863a86c3470da13d81a955d277eba485` |
| Integration Draft PR #414, pre-audit | `c09b3a60f9fbe732ec4d96258899acb583740dda` |
| OpenDART Draft PR #412 | `bf3d9514a87c53b1775e22ec9ba7711f6cecc49f` |
| Runtime Draft PR #413 | `f003ef6247e16fcc71bd3b1b20cd4904c4d984c0` |
| Single-runner Draft PR #418 | `2f98401cc50a6c6a25808a98516efd5bf0c944ee` |
| KRX specialist `indexalert-krx-pit-source-audit-20261013` | `073d2d49e95f69fb10b943b93e51bb179fb3c698` |
| KRX Draft PR #420 | `fab3cbbd63a951a4e081f9e7f08c1391ca308581` |
| KRX Draft PR #422 | `c14857620973531013799e44625d43080904fd5f` |
| KRX Draft PR #423 | `0e38004363cac9fc4475556b3a1c445de9af407f` |

Frozen integration gate document `docs/INDEXALERT_PROFITABILITY_INTEGRATION_GATE_2026-10-13.md` remains Git blob `984c933651f39f1ee9e26a1d7ac3893aaa5335be`. No edits to the gate, specialist code, workflows or existing PRs.

## Independent source and economics gates

| Claim | Verdict | Evidence / boundary |
| --- | --- | --- |
| 2021 original OpenDART ZIP byte identity | **PASS (bytes only)** | Previously verified SHA-256 `8728c0a3c12761ca19e9c6455bea8f1bed0e4c1ebc2e21dc263c373a82a2b625`; #412 latest [viewer TOC offline Action 40263193758](https://github.com/kims34/openpilot-opkr/actions/runs/40263193758) retains explicit `m20_feature_pit_admitted=False`, `m20_performance_run_authorized=False`. |
| 2022 original OpenDART ZIP byte identity | **PASS (bytes only)** | Previously verified SHA-256 `56639d8f6ebbecf14cd8bc3179d75d01162e2cd7bbdf8f6a3c9479b44f5084bb`. |
| 2021/2022 original 3-month July–September CFS operating income, original public available-at, corrected edition lineage, historical issuer-to-security PIT | **NOT VERIFIED** | ZIP integrity, SGML candidate rows and synthetic viewer checks cannot bind original accounting context/period/publication timestamp. No source admission. |
| KRX 2017–2022 raw weekday daily/master source pair integrity | **PASS (storage only)** | Previously verified 1,565/1,565 pairs; does not establish official exchange calendar, stock-day state or execution. |
| KRX 2021 13-day and 2022 14-day private exact-set corroboration; 90 unknown sessions, 12,003 zero-activity rows, 27 nonpositive OHLC | **NOT VERIFIED / quarantined** | [#423 Action 39714207925](https://github.com/kims34/openpilot-opkr/actions/runs/39714207925) decoded job `119612335677` runs synthetic controls only: `DRY_RUN_NO_PRIVATE_STORAGE_READ`, `2022_private_candidate_date_sets_equal=False`. |
| Official KRX trading status, corporate actions, realistic fills/fees/tax, annual post-cost risk-adjusted NetEV/PF/CAGR/MDD/ES95/ES99, concentration and time robustness | **NOT EVALUABLE** | Neither official data PIT nor execution economics admitted. Do not run M20 profitability, new model search or market performance experiments. |
| Prospective public chronology anchor | **FAIL for the attempted run** | [Action 40534270813](https://github.com/kims34/openpilot-opkr/actions/runs/40534270813), job `122295113858`, HTTP 404 at `/anchor/latest` after bounded attempts; validation skipped. 404 does not prove the cause. |
| Latest watchdog governance | **PASS offline controls only** | [Action 40574617617](https://github.com/kims34/openpilot-opkr/actions/runs/40574617617), job `122437575718`, log: `M20 PIT admission: NOT ATTESTED; orders: DISABLED; holdout: NOT AUTHORIZED`; artifact ZIP SHA-256 `94bd636632f12535e2e015a23c08c7cf9c656c81c7961e34ccda24de512e3930`. Not a live Railway setting attestation. |

## Isolated runtime optimisation: verified logs and static-code audit

- [PR #413 Action 38508247773](https://github.com/kims34/openpilot-opkr/actions/runs/38508247773): 6/6 jobs successful; decoded parity job `115670744341`: 34/34 exact cases identical, digest `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34`; serial 1.7650 s, longest parallel suite 2.7079 s, **0.6520x**. This phase regressed.
- [PR #418 Action 39111405562](https://github.com/kims34/openpilot-opkr/actions/runs/39111405562): job `117628139856` logs the same 34-case digest and identical outcomes; serial subprocess 2.3911 s vs concurrent group 2.0755 s = **1.1521x** subprocess group ratio. A separate parity field compares 2.3484 s with longest suite 2.0154 s = **1.1650x**; these are distinct clock definitions, not interchangeable end-to-end measures. Full GitHub CI and real PIT-admitted backtest acceleration **NOT VERIFIED**.
- [PR #418 candidate source Action 39111405494](https://github.com/kims34/openpilot-opkr/actions/runs/39111405494), job `117628139749`: `checked_files=22`, `all_transitive_imports_pinned=false`, `candidate_approved_for_merge=false`. Archived manifest source gate deliberately fails closed on expected Git blob `108f66714602a1bd3ae42c34dcca7c16e38f460b` versus current `e0055c66c59398fd4a1158077446d886b54c4e37`. Never repin the archived baseline.
- Fresh GitHub compare `#413 HEAD...#418 HEAD`: **diverged, 49 ahead / 18 behind**, merge base `ca6c5d915d2c0e018f4aa9f82b4488038c16f8d3`. A 34-case digest does not attest combined latest source tree.
- **Additional direct static review (no code change):** #413 `research_v1_runtime_manifest.py`, Git blob `e0055c66c59398fd4a1158077446d886b54c4e37`, verifies receipt *shape* and source/code/policy/runtime hashes but explicitly relies on a **separate caller-authenticated PIT admission receipt**. Its `cache_manifest` is not an admission authority. #418 `research_v1_runtime_handoff.py`, blob `c3b629a62fd60704d0c6a18c4dfb4a863294eaa4`, binds artifact bytes to a **caller-authenticated** upstream cache key and likewise cannot authenticate the upstream origin. Therefore neither an internally self-consistent cache digest nor a handoff digest closes the independent admission/authority chain. This is a **NOT VERIFIED** integration precondition, not evidence of an exploit or a regression.
- #418 `research_v1_runtime_single_runner.py` blob `edf4e8a8c49cc873bd8ceb414ed16b69e4ef14c1` invokes independent synthetic regression subprocesses, runs serial then four parallel suites, and explicitly reports `ci_end_to_end_speedup_measured=false`, `actual_profitability_backtest_speedup_measured=false`, `holdout_accessed=false`, `ordering=false`. No model fit or economic test was run in this audit.

## Railway read-only access limitation

Direct `list_projects({})` again returned `User input required but current turn is running in a non-interactive mode.` This is an **access-approval blocker**, not a successful read. Latest Railway IndexAlert deployment, service routes, runtime logs, private KRX date-set audit and actual production `ORDERING` value are **NOT DIRECTLY VERIFIED**. No alternate credentials, bypass, permission changes or deployment actions attempted. The user must approve the Railway connector read when interactive access is available; until then do not claim current live state from GitHub-only evidence.

## Admission decision and permitted next steps

**M20 PIT NO-GO; M20 economic RUN NO-GO; post-fee/tax NetEV, PF, CAGR, MDD, ES95/99, concentration and time robustness NOT EVALUABLE.** Maintain Frozen H5, M20 horizon20/purge20, WF504/126/126, PIT/Purged/CPCV, consumed/sealed independent Holdout, Champion/Top3/NO_TRADE and immutable cost/tax/fill/risk/promotion gates. `ORDERING=false` remains a mandatory policy; the actual Railway runtime setting is unverified. Only isolated synthetic offline safety tests and read-only evidence review are allowed pending independently authenticated first-original OpenDART PIT and official KRX tradeability proofs. Cache reuse requires separately approved source/data/code/Frozen/runtime/evidence SHA-256 and fail-closed equality. Parallelize only independent read-only postprocessing; never dependent refitting/capital transitions. No workflow edits, PR merge, deployment, live orders, funds, account rights or Champion promotion.

Next independent work: delegated original-edition CFS semantics/publication chronology; authorised KRX private exact-day and official stock-state/corporate-action proof; Railway `/anchor/latest` 404 diagnosis via approved read-only access; complete transitive runtime dependency lineage and matched full-CI synthetic-only timing. Keep owner boundaries intact.
