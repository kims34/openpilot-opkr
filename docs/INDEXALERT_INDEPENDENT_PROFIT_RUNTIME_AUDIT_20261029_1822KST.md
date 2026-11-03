# IndexAlert independent profitability + isolated runtime audit — 2026-10-29 18:22 KST

**Scope:** read-only GitHub and Railway source, CI and runtime evidence. This note is an isolated audit document; no model, research/development, frozen policy, workflow, holdout, trading configuration, or delegated specialist code was changed. No economic backtest, live order, deployment, merge, credential/permission change, or Champion promotion was executed.

## Exact GitHub refs checked (2026-10-29)
- Research `index-alert-research-v1`: `3b8b7830612a6284d7c7a60628cb527cb741627a`.
- Development `index-alert-position-regen-fix-v1`: `1e6367d2863a86c3470da13d81a955d277eba485`.
- Draft [#414](https://github.com/kims34/openpilot-opkr/pull/414) integration documentation: **pre-audit-write HEAD** `040ed28fa54fd5d765813ed720a35af5ad3bc2f7`, gate file Git blob `984c933651f39f1ee9e26a1d7ac3893aaa5335be`.
- Draft [#413](https://github.com/kims34/openpilot-opkr/pull/413) optimization: `f003ef6247e16fcc71bd3b1b20cd4904c4d984c0`.
- Draft [#418](https://github.com/kims34/openpilot-opkr/pull/418) one-runner: `2f98401cc50a6c6a25808a98516efd5bf0c944ee`.
- Draft [#412](https://github.com/kims34/openpilot-opkr/pull/412) OpenDART: `bf3d9514a87c53b1775e22ec9ba7711f6cecc49f`.
- Draft [#416](https://github.com/kims34/openpilot-opkr/pull/416) investor flow: `053de553646fc4765d2616544ca1e8d6bbdde35f`.
- KRX Draft [#420](https://github.com/kims34/openpilot-opkr/pull/420): `fab3cbbd63a951a4e081f9e7f08c1391ca308581`; [#422](https://github.com/kims34/openpilot-opkr/pull/422): `c14857620973531013799e44625d43080904fd5f`; [#423](https://github.com/kims34/openpilot-opkr/pull/423): `0e38004363cac9fc4475556b3a1c445de9af407f`.
- All listed PRs were open and Draft when checked. Separate ETF-open offline CI [#40828908590](https://github.com/kims34/openpilot-opkr/actions/runs/40828908590) and [#40828341381](https://github.com/kims34/openpilot-opkr/actions/runs/40828341381) succeeded on 2026-10-29, but are another workstream and **not** M20 source admission or financial-performance proof.

## Source/PIT and economic admission verdict
| Gate | Verdict | Direct evidence and limit |
|---|---|---|
| First-original DART document bytes and correction SGML candidate matching | **PASS only for previously recorded source-identity/candidate checks** | Prior official action [#38419439742](https://github.com/kims34/openpilot-opkr/actions/runs/38419439742) had 15 matching candidate signature rows; this is not proof of an authoritative first-filed earnings cell. |
| 2022/2021 initial CFS standalone three-month operating-profit cell, period/unit/sign, correction lineage, exact public available-at | **NOT VERIFIED** | Latest #412 HEAD `bf3d9514...`; [#40263193758](https://github.com/kims34/openpilot-opkr/actions/runs/40263193758) and [#40263181687](https://github.com/kims34/openpilot-opkr/actions/runs/40263181687) each 1/1 offline synthetic job PASS, not regulator-time original-semantic proof. |
| Historical issuer/security mapping and official KRX calendar, per-security trading status, corporate actions, executable fills | **NOT VERIFIED** | KRX #420 HEAD CI [#39714369438](https://github.com/kims34/openpilot-opkr/actions/runs/39714369438), #422 [#39001836000](https://github.com/kims34/openpilot-opkr/actions/runs/39001836000), #423 [#39714207925](https://github.com/kims34/openpilot-opkr/actions/runs/39714207925) offline checks SUCCESS only. Historical Railway private 1,565/1,565 weekday pairs is prior storage-integrity PASS, not official day/security trading eligibility; 90 unresolved calendar/source gaps and 12,003 zero-activity excluded. Current Railway KRX deployment has no logs in the requested recent window; old source proof was not re-admitted in this run. |
| Realistic trade fees, slippage, partial fills, taxes, cost-after-tax profitability, NetEV/PF/CAGR/MDD/ES95/99, concentration and chronological robustness | **NOT VERIFIED / NOT EVALUABLE** | No independently admitted official PIT data, no authorized M20 economics run. Do not infer results from offline CI. |
| M20 admission and performance execution | **NO-GO** | Source/PIT gates unapproved. H5 spent/failed Holdout and Dynamic outputs cannot be retrofitted or reused independently. |
| Champion/Top3, live orders and capital | **NOT AUTHORIZED** | Frozen H5, M20 horizon20/purge20, WF504/126/126, Purged/CPCV, independent Holdout and NO_TRADE policy unchanged. |

## Isolated optimization audit
- [PR #413 CI #38508247773](https://github.com/kims34/openpilot-opkr/actions/runs/38508247773) **6/6 jobs PASS**, original **34/34** offline cases and identical digest `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34`. Serial test phase **1.7650s**, parallel longest suite **2.7079s**: ratio **0.652x** (parallel slower). Not an end-to-end CI or official backtest comparison.
- [PR #418 CI #39111405562](https://github.com/kims34/openpilot-opkr/actions/runs/39111405562) 1/1 PASS: original 34-case digest unchanged; single-runner comparison reports 2.3911s serial vs 2.0755s parallel (~1.1521x) for limited test phase, both-mode validation 4.4674s; no end-to-end CI or economic speedup proof.
- [PR #418 pinned parallel CI #39111405478](https://github.com/kims34/openpilot-opkr/actions/runs/39111405478) **FAIL**, direct job #117628139395 log: `SourceDriftError: archived blob mismatch: research_v1_runtime_manifest.py expected=108f66714602a1bd3ae42c34dcca7c16e38f460b observed=e0055c66c59398fd4a1158077446d886b54c4e37`.
- Direct file fetch at current HEADs: PR #413 Git blob `e0055c66c59398fd4a1158077446d886b54c4e37` (188 lines) requires holdout and live-order receipt flags **literal False**, and optional elevated authority aliases literal False when present. PR #418 Git blob `108f66714602a1bd3ae42c34dcca7c16e38f460b` (103 lines) rejects only literal True on two receipt flags. **Semantic authority check differs**, not just a harmless pin drift. Never simply re-pin the archived baseline.
- [PR #418 candidate source audit #39111405494](https://github.com/kims34/openpilot-opkr/actions/runs/39111405494) 1/1 PASS for a reviewed candidate subset, but `all_transitive_imports_pinned=false`, `candidate_approved_for_merge=false`. Entire transitive runtime dependency closure is not approved.
- **Cache FAIL-CLOSED** until independently authenticated source/data/calculation code/Frozen policy/runtime lock/approval receipt SHA-256 and correct combined-code lineage all agree. Only independent read-only post-processing can be parallel; no dependent retraining or capital-transition parallelism. No PR #413/#418 merge or workflow modification.

## Railway production read-only checks (2026-10-29)
- Project `d1c1a050-b7d6-41ce-b300-13c20f82a20a`, production environment `83d5840b-270e-4d3f-a941-a37fd4a55ff7`.
- Latest `indexalert-kiwoom-real-readonly` deployment `a77fb922-b679-4d88-92c4-03054ec579cd`, **SUCCESS**, created `2026-10-29T06:21:36.918Z`, commit `85bb6fd10bcc9ff2b14abe1c774f0d99f8eb84ab`. Logs show container startup only; success is **not** broker permission or ordering proof.
- `indexalert-pit-rebuild` deployment `8b354fc1-cfb2-4ef0-863e-67f7f5dda2b5` SUCCESS, latest inspected logs `2026-10-28T12:46:06Z` through `14:46:43Z`: `ordering=DISABLED`, `live_order_authorized=false`, `independent_source_admission_verified=false`, `COMMON_OHLC_NONPOSITIVE` (27/803 common-stock rows). Fail-closed on prospective admission. This does not prove every service's hidden ORDERING environment-variable value.
- KRX worker deployment `16c93d7c-7cd0-4d84-a327-298d2805376c` SUCCESS (2026-10-12); no new log entries returned in requested 2026-10-28 onward window. No new official source admission.
- **Railway status API discrepancy:** `get_status` returned `stagedChanges=null` and an empty `pendingWork` entry `patch:e113dacb-6705-4416-9997-dc694539d382`; direct `get_staged_changes` returned `staged=null`, `resources=[]`, `sharedVariables=[]`, `destructive=false`. Treat as metadata inconsistency with **no verified actionable staged change**, not as proof a deployment is pending. No changes were accepted.
- Live order permission was not changed, and `ORDERING=false` remains the required policy.

## Other current CI
- [Watchdog #40806178512](https://github.com/kims34/openpilot-opkr/actions/runs/40806178512) 1/1 PASS, 2026-10-29 02:24Z, artifact ZIP SHA-256 `6f4d29f3db3475b497dbcd87c027f48a540e96c853e5e0f0131a5726001c821a`; safety/software proof only.
- [Prospective chronology anchor #40726273259](https://github.com/kims34/openpilot-opkr/actions/runs/40726273259) FAIL, job #122950285352 ended with HTTP 404 on 2026-10-28; validation job skipped. Do not treat anchor as independently admitted.

## Next non-overlapping, non-economic actions
1. OpenDART owner: exact first-filed original-vintage CFS operating-profit standalone 2022/2021 Q3 cells and authoritative public timestamps with correction chronology; independently hash receipt/source lineage. Until then **PIT NO-GO**.
2. KRX owner: official per-day/per-security session/tradability, corporate-action and issuer/security as-of mappings, resolve 90 gaps and 27 prospective OHLC failures without silently imputing or broadening eligibility.
3. Optimization owner: review PR #413 vs #418 authority semantics and candidate merged tree, pin full transitive dependency closure, retain immutable original 34-case digest; only offline synthetic fail-closed tests, no workflow security bypass. Do not claim CI/economic speedup.
4. Integration: after both source owners independently pass, review trade costs/taxes, fill realism, chronological leakage, NetEV/PF/CAGR/MDD/ES95/99 and concentration against the **unchanged** frozen thresholds; separately seek authorization before any M20 economic run or promotion.

**Overall verdict: M20 PIT NO-GO; M20 profitability NOT EVALUABLE; cache FAIL-CLOSED; ORDERING=false.** No automatic merge, deploy, live trading, funds, permissions, credentials, Champion promotion or spent Holdout reuse.
