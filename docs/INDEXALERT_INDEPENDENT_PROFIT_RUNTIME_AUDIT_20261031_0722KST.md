# IndexAlert independent profitability and isolated runtime audit — 2026-10-31 07:22 KST

**Scope:** independently re-read current GitHub refs, source-file blobs, original Actions job logs and Railway production inventory/logs. Evidence only. No market strategy run, model search, frozen Holdout access, broker order, permission change, CI workflow edit, deployment or PR merge. This document is on the existing dedicated audit branch, not on research/development/PR #413/#414/#418.

## Pinned GitHub evidence (read at 2026-10-31 ~07:22 KST)

| Authority | HEAD SHA | Interpretation |
| --- | --- | --- |
| Research `index-alert-research-v1` | `3b8b7830612a6284d7c7a60628cb527cb741627a` | Frozen M20/PIT gate remains |
| Development `index-alert-position-regen-fix-v1` | `1e6367d2863a86c3470da13d81a955d277eba485` | No production authority inferred |
| Integration Draft [#414](https://github.com/kims34/openpilot-opkr/pull/414) | `17c9c525660642134983761ea66ec62ef000fe0b` | Integration gate document blob `984c933651f39f1ee9e26a1d7ac3893aaa5335be`, not a source approval |
| OpenDART Draft [#412](https://github.com/kims34/openpilot-opkr/pull/412) | `bf3d9514a87c53b1775e22ec9ba7711f6cecc49f` | Original first-edition CFS operating-income cell/public time NOT VERIFIED |
| Optimization Draft [#413](https://github.com/kims34/openpilot-opkr/pull/413) | `f003ef6247e16fcc71bd3b1b20cd4904c4d984c0` | Synthetic parity only |
| Single runner Draft [#418](https://github.com/kims34/openpilot-opkr/pull/418) | `2f98401cc50a6c6a25808a98516efd5bf0c944ee` | Source closure FAIL / real acceleration NOT VERIFIED |
| KRX specialist `indexalert-krx-pit-source-audit-20261013` | `073d2d49e95f69fb10b943b93e51bb179fb3c698` | Official tradeability NOT VERIFIED |
| Investor-flow Draft [#416](https://github.com/kims34/openpilot-opkr/pull/416) | `053de553646fc4765d2616544ca1e8d6bbdde35f` | Non-admitting |
| KRX Draft [#420](https://github.com/kims34/openpilot-opkr/pull/420) | `fab3cbbd63a951a4e081f9e7f08c1391ca308581` | 90 unknown sessions / 27 bad OHLC guard |
| KRX Draft [#422](https://github.com/kims34/openpilot-opkr/pull/422) | `c14857620973531013799e44625d43080904fd5f` | 2021 calendar candidate, not official |
| KRX Draft [#423](https://github.com/kims34/openpilot-opkr/pull/423) | `0e38004363cac9fc4475556b3a1c445de9af407f` | 2022 calendar candidate, not official |

**Additional independently reproduced source-lineage blocker:** `research_v1_runtime_manifest.py` is blob SHA-1 `e0055c66c59398fd4a1158077446d886b54c4e37` when fetched at **current PR #413 HEAD**, while **current PR #418 HEAD** and its historical PR-base commit `ca6c5d915d2c0e018f4aa9f82b4488038c16f8d3` expose the **archived** blob `108f66714602a1bd3ae42c34dcca7c16e38f460b`. PR #418's own `research_v1_runtime_archived_source_gate.py` hard-pins that latter blob. This independently establishes **cross-branch implementation identity drift**, consistent with failed [Actions 39111405478](https://github.com/kims34/openpilot-opkr/actions/runs/39111405478), job `117628139395`, which explicitly reports expected `108f667...` and observed `e0055c6...` in checked-out CI context. It does **not** establish which version is approved or authorize resetting the pinned baseline. Resolve via separately reviewed source lineage and exact merge-tree/transitive closure; never silently re-pin, force green, override checkout, or bypass workflow security.

## Source admission and economic verdict

- [OpenDART Actions 38419439742](https://github.com/kims34/openpilot-opkr/actions/runs/38419439742): two jobs SUCCESS for original/amended SGML operating-row candidate signatures (15 candidates). Source ZIP/row-shape evidence is not proof of first-original consolidated July–September 2022 **or comparative 2021** three-month operating-income amounts, statement/period/sign/unit/currency, correction lineage or first public available-at. **Original filing semantic PIT: NOT VERIFIED**. [Action 40263193758](https://github.com/kims34/openpilot-opkr/actions/runs/40263193758) 1/1 synthetic TOC identity success is non-admitting.
- Historical KRX 2017–2022 private 1,565/1,565 weekday daily/master pairs: **limited PASS for prior raw-storage SHA/integrity only** (not independently rerun against mounted private bytes in this audit). Ninety unknown calendar/source-empty days and 12,003 zero-activity quarantined records remain blocked. Official historical calendar, issuer/security PIT mapping, suspensions, corporate actions, market-cap/fills, fees/taxes: **NOT VERIFIED**. [Action 40262192831](https://github.com/kims34/openpilot-opkr/actions/runs/40262192831) 2/2 offline-only success does not grant authority.
- Frozen H5 and M20 horizon20/purge20, WF504/126/126, Purged/CPCV/independent Holdout/Champion/Top3/NO_TRADE and original cost/risk/selection policies unchanged. Consumed H5 Holdout and dynamic results may not be re-used as independent tests.
- **M20 PIT: NO-GO**. Official after-tax NetEV, PF, CAGR, MDD, ES95/ES99, concentration, date sensitivity, robust execution, annual risk-adjusted net profit: **NOT EVALUABLE** (not a negative or zero performance estimate).

## Offline runtime evidence

- [Actions 38381997417](https://github.com/kims34/openpilot-opkr/actions/runs/38381997417) and [38382214223](https://github.com/kims34/openpilot-opkr/actions/runs/38382214223): each 6/6 SUCCESS, archived 34-case identity/outcome SHA-256 `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34`. [Action 38419111311](https://github.com/kims34/openpilot-opkr/actions/runs/38419111311) 6/6 SUCCESS / 13 adversarial mocks; [38508022564](https://github.com/kims34/openpilot-opkr/actions/runs/38508022564) 6/6 SUCCESS / 23 synthetic guards. **Limited fixed-case parity PASS only**.
- [Actions 38419649711](https://github.com/kims34/openpilot-opkr/actions/runs/38419649711) 1/1 SUCCESS, serial 2.9656 s / parallel 2.6209 s = 1.1315x (old isolated regression phase).
- [Actions 39111405562](https://github.com/kims34/openpilot-opkr/actions/runs/39111405562), job `117628139856`, 1/1 SUCCESS, original log 34-case digest exact; serial 2.3484 s / longest parallel 2.0154 s = 1.165x **only fixed regression phase**. Log says `ci_end_to_end_speedup_measured=false`, `actual_profitability_backtest_speedup_measured=false`, `ordering=false`.
- [Actions 39111405478](https://github.com/kims34/openpilot-opkr/actions/runs/39111405478), job `117628139395`, **FAIL** at immutable archived source gate as detailed above. Its environment gate reports `exact_wheel_hashes_verified=false`, `os_native_dependency_identity_verified=false`. Real H5/M20 runtime acceleration and whole CI wall-clock speedup: **NOT VERIFIED**. No official data economic run authorized.
- Cache may be reused only with independently approved original data/code/Frozen policy/runtime/authority evidence SHA-256 matching, fail closed on any mismatch. Only independent read-only postprocessing may parallelize; no dependent retraining/capital transition parallelization.

## Latest Railway production read-only observation

Project `d1c1a050-b7d6-41ce-b300-13c20f82a20a`, environment `83d5840b-270e-4d3f-a941-a37fd4a55ff7`.

- `indexalert-runtime`: deployment `eaaa9f67-b9f2-41d2-832c-7d6fad9b9b00` SUCCESS, 1/1 running; most recent fetched monitoring message **2026-10-30 22:22:46 UTC (2026-10-31 07:22:46 KST)**. Quotes/FX checks only, not proof of push delivery or trading permission.
- `indexalert-pit-rebuild`: deployment `8b354fc1-cfb2-4ef0-863e-67f7f5dda2b5` SUCCESS, 1/1 running. Latest fetched fail-closed event **2026-10-30 14:46:37 UTC (23:46:37 KST)**: `COMMON_OHLC_NONPOSITIVE`, 27/803 common-stock rows, 27 zero volume/value rows, source failure session 2026-09-28, `session_manifest_sha256=null`, `independent_source_admission_verified=false`, `independent_chronology_admission_verified=false`, `fresh_alpha_observation_admitted=false`, `ordering=DISABLED`, `real_orders_authorized=false`. No later PIT admission event in returned logs.
- KRX historical worker deployment `16c93d7c-7cd0-4d84-a327-298d2805376c` SUCCESS; no new entries in returned deployment log.
- `indexalert-kiwoom-real-readonly` deployment `a77fb922-b679-4d88-92c4-03054ec579cd` SUCCESS, dashboard status online **but replica running 0 / crashed 1**; operational readiness **NOT VERIFIED**. Push, backend and db-query-readonly services reported offline, separately from live monitoring.
- Railway `describe_environment` and `get_staged_changes` both show `staged=null` / no changed fields; `environment_status` still shows `patch:e113dacb-6705-4416-9997-dc694539d382` pending, empty `changes=[]`. This API inconsistency is **NOT VERIFIED**, not authorization to apply/clear anything.
- [Chronology Anchor Actions 41091128151](https://github.com/kims34/openpilot-opkr/actions/runs/41091128151), job `124184971844`: prior HTTP 404 at `/anchor/latest` after retry, **FAIL**; no chronology admission.
- Latest [Hourly Proof Watchdog 41125666590](https://github.com/kims34/openpilot-opkr/actions/runs/41125666590), job `124303425989`, 1/1 SUCCESS at 2026-10-31 05:45 KST, but original job log explicitly prints `M20 PIT admission: NOT ATTESTED; orders: DISABLED; holdout: NOT AUTHORIZED`. Workflow metadata success is not source/PIT success.

## Independent next steps

1. OpenDART owner: immutable first-original filing receipt+SHA, 2022/2021 standalone three-month CFS operating-profit semantic cell, corrected lineage and exact first public time, issuer/security as-of.
2. KRX owner: official historical session/tradeability/corporate action and actual execution/cost/tax as-of proofs; reconcile 90 unknown days, 27 OHLC anomalies, without silent exclusions.
3. Runtime owner: independently review PR #413 `e0055c...` vs PR #418 `108f667...` and GitHub synthetic merge context; obtain approved transitive closure and exact wheel/OS-native hashes before comparing end-to-end CI wall time. No new economic experiment.
4. Orchestrator: preserve immutable frozen gates, `ORDERING=false`, no M20 performance, holdout reuse, Champion promotion, Tiny Live, deployment, account permissions, funds or PR merge. Any real-order or rights change needs separate explicit approval.

**Verdict:** raw-storage SHA limited PASS; offline 34-case parity limited PASS; merged-context archived source identity FAIL; official PIT/tradability/after-tax economics NOT VERIFIED or NOT EVALUABLE; M20 NO-GO and ORDERING disabled.
