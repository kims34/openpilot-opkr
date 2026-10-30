# IndexAlert independent profitability / offline-runtime evidence audit — 2026-10-31 05:22 KST

**Authority / isolation:** Direct read-only GitHub refs, PRs, Actions job logs and Railway production service logs, with this document as the **only write**. No live data acquisition, strategy search, economic backtest, H5 Holdout reuse, trading, deployment, workflow edit, PR merge, broker permission or credential change. Preserve Frozen H5, M20 horizon20/purge20, WF504/126/126, PIT/Purged/CPCV/independent Holdout, Champion/Top3/NO_TRADE, cost/tax/risk/upgrade gates, and `ORDERING=false`. No economic RUN before official original-filing and market PIT admission.

## Source identity, directly queried

| Source | HEAD / evidence | Assessment |
|---|---|---|
| research `index-alert-research-v1` | `3b8b7830612a6284d7c7a60628cb527cb741627a` | Frozen, unchanged |
| development `index-alert-position-regen-fix-v1` | `1e6367d2863a86c3470da13d81a955d277eba485` | Unchanged |
| [Draft PR #414](https://github.com/kims34/openpilot-opkr/pull/414) | `37bdab6d3559df9de3742d505e29b9b75a8df6ae`; compared with prior `85125f3569554cc6f2dc5fe7ec9f388b66b52163`: one additional **documentation-only** commit, adding `docs/INDEXALERT_INDEPENDENT_PROFIT_RUNTIME_AUDIT_20261031_0446KST.md`; original integration gate blob SHA-1 `984c933651f39f1ee9e26a1d7ac3893aaa5335be` | DRAFT, no new admission |
| [Draft PR #412](https://github.com/kims34/openpilot-opkr/pull/412) | `bf3d9514a87c53b1775e22ec9ba7711f6cecc49f` | DRAFT |
| [Draft PR #413](https://github.com/kims34/openpilot-opkr/pull/413) | `f003ef6247e16fcc71bd3b1b20cd4904c4d984c0` | DRAFT |
| [Draft PR #418](https://github.com/kims34/openpilot-opkr/pull/418) | `2f98401cc50a6c6a25808a98516efd5bf0c944ee` | DRAFT |
| [Draft PR #416](https://github.com/kims34/openpilot-opkr/pull/416) | `053de553646fc4765d2616544ca1e8d6bbdde35f` | DRAFT |
| KRX PIT source audit branch | `073d2d49e95f69fb10b943b93e51bb179fb3c698` | No new original exchange admission |
| [Draft PRs #420](https://github.com/kims34/openpilot-opkr/pull/420), [#422](https://github.com/kims34/openpilot-opkr/pull/422), [#423](https://github.com/kims34/openpilot-opkr/pull/423) | `fab3cbbd63a951a4e081f9e7f08c1391ca308581`, `c14857620973531013799e44625d43080904fd5f`, `0e38004363cac9fc4475556b3a1c445de9af407f` | DRAFT, synthetic comparison only |

## Official-source and economic gate (independent, non-admitting)

- **OpenDART:** [Action 38419439742](https://github.com/kims34/openpilot-opkr/actions/runs/38419439742) two successful jobs identified 15 original/amended SGML operating-label candidate rows and adjacent numeric signatures, **not** authenticated original 2022 and comparative 2021 CFS standalone July–September three-month operating-income cells. [Action 40263193758](https://github.com/kims34/openpilot-opkr/actions/runs/40263193758) 1/1 synthetic TOC/identity safety test SUCCESS; explicitly retains `m20_feature_pit_admitted=False`. Original document SHA, first public available-at, original/amendment temporal lineage, CFS period semantics, historical issuer-security mapping still **NOT VERIFIED**.
- **KRX:** Historical 2017–2022 private daily/master 1,565/1,565 weekday pair **storage hash integrity PASS in prior audited scope only**, not exchange session calendar, tradability or corporate-action authority. The 90 historical unknown source-empty sessions, 27 suspect common-stock OHLC rows, and 12,003 zero-activity quarantine records remain source/admission blockers. [PR #416 Action 40262192831](https://github.com/kims34/openpilot-opkr/actions/runs/40262192831) two offline guard/digest jobs SUCCESS, not private source re-acquisition or PIT approval.
- **Railway PIT:** production service `indexalert-pit-rebuild`, deployment `8b354fc1-cfb2-4ef0-863e-67f7f5dda2b5`, latest fetched record `2026-10-30T14:46:37.348994251Z` (23:46:37 KST): `COMMON_OHLC_NONPOSITIVE`, 27/803 common-stock rows, `status=FAIL_CLOSED`, `fresh_alpha_observation_admitted=false`, `independent_source_admission_verified=false`, `independent_model_admission_verified=false`, `independent_chronology_admission_verified=false`, `ordering=DISABLED`, `live_order_authorized=false`.
- **Economic admissibility:** original-filed operating-income PIT, historical corporate/security mappings, official KRX exchange state/CA/fills, actual cost and tax evidence **NOT VERIFIED**. M20 run **NO-GO**; NetEV/PF/CAGR/MDD/ES95/ES99, concentration and time robustness **NOT EVALUABLE**, not zero or negative. Consumed/failed H5 Holdout and dynamic results cannot be reused for fresh independent claims.

## Isolated offline optimization verification

- [Actions 38381997417](https://github.com/kims34/openpilot-opkr/actions/runs/38381997417) and [38382214223](https://github.com/kims34/openpilot-opkr/actions/runs/38382214223): each 6/6 job SUCCESS, immutable 34-case SHA-256 `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34`. Scope: offline case parity only.
- [PR #418 Action 39111405562](https://github.com/kims34/openpilot-opkr/actions/runs/39111405562), original job `117628139856`: 1/1 SUCCESS, `RUNTIME_OPT_PARITY` confirms exactly 34 identical outcomes and digest above, serial regression 2.3484 s versus parallel longest suite 2.0154 s = 1.1650x **test-phase only**; `actual_backtest_speedup_measured=false`, `ci_end_to_end_speedup_measured=false`, `ordering=false`. Synthetic safety guards also passed; no capital transition/retraining parallelization admitted.
- [PR #418 Action 39111405478](https://github.com/kims34/openpilot-opkr/actions/runs/39111405478), original job `117628139395`: **FAIL**, `SourceDriftError`: `research_v1_runtime_manifest.py` expected blob `108f66714602a1bd3ae42c34dcca7c16e38f460b`, observed `e0055c66c59398fd4a1158077446d886b54c4e37`. Correctly fail-closed; cannot re-label as parity PASS. [Action 39111405494](https://github.com/kims34/openpilot-opkr/actions/runs/39111405494) candidate merge audit succeeded but is non-admitting.
- **Next isolated optimization work:** without touching specialist code or Frozen inputs, require one immutable approval manifest pinning source/data/code/Frozen/runtime/evidence SHA-256 and exact archived blob identity before cache read; deny on mismatch. Keep dependent training/capital transitions serial; only independent read-only postprocessing may parallelize. Recheck job-level wall time separately from test-phase timing; do not infer full-CI or official backtest speedup.

## Production read-only operations

- Railway project `d1c1a050-b7d6-41ce-b300-13c20f82a20a`, environment `83d5840b-270e-4d3f-a941-a37fd4a55ff7`.
- `indexalert-runtime` online, deployment `eaaa9f67-b9f2-41d2-832c-7d6fad9b9b00`, 1/1 running. Latest inspected live logging `2026-10-30T20:22:43.554846100Z` (2026-10-31 05:22:43 KST) includes SPY, QQQ, SCHD checks and USD/KRW; **monitoring logs do not constitute M20 official-source admission**.
- `indexalert-kiwoom-real-readonly` UI `online`, deployment `a77fb922-b679-4d88-92c4-03054ec579cd`, replica state **running 0, crashed 1**; operational readiness **NOT VERIFIED** despite displayed SUCCESS/online. No broker action.
- `indexalert-push`, `indexalert-backend`, `db-query-readonly` shown offline (warnings/critical); this is distinct from the online `indexalert-runtime` and is not evidence that phone push delivery is working or broken. A staged patch `e113dacb-6705-4416-9997-dc694539d382` has zero enumerated changes and was not applied; do not reconcile by guessing.
- No production settings, PRs, Actions workflows, model parameters, account permissions, ordering or credentials changed.

**Final:** Original public-as-of/PIT and KRX tradability **NOT VERIFIED**; offline fixed-case parity **limited PASS**, separate archived-source check **FAIL**, full-runtime acceleration **NOT VERIFIED**; official M20 profitability **NOT EVALUABLE / NO-GO**, `ORDERING=false`. Next admission requires independently pinned original-filed 2022+2021 standalone CFS three-month earnings semantics and publication chronology, plus historical exchange/security tradability/corporate-action evidence. Keep PRs #413/#414/#418 unmerged and production untouched.
