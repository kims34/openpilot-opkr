# IndexAlert independent profitability + isolated runtime audit — 2026-11-02 09:18 KST

**Audit type:** Read-only evidence review and documentation-only isolated handoff. This is not PIT/source approval, official backtest, investment result, release, merge, deployment, broker action or promotion. No official market-return calculation, parameter exploration, consumed Holdout replay, or performance experiment was run. ORDERING=false / DISABLED remains mandatory.

## 1. Exact independently observed GitHub refs

- Research `index-alert-research-v1`: `3b8b7830612a6284d7c7a60628cb527cb741627a` (resolved via commit read).
- Development `index-alert-position-regen-fix-v1`: `1e6367d2863a86c3470da13d81a955d277eba485` (resolved via commit read).
- KRX specialist `indexalert-krx-pit-source-audit-20261013`: `073d2d49e95f69fb10b943b93e51bb179fb3c698` (resolved via commit read).
- [Draft PR #414](https://github.com/kims34/openpilot-opkr/pull/414) head `76a5cd0a46d4ac5acfd0e69dd3b5197585829a65`, core `docs/INDEXALERT_PROFITABILITY_INTEGRATION_GATE_2026-10-13.md` Git blob SHA-1 `984c933651f39f1ee9e26a1d7ac3893aaa5335be` (read from PR head).
- [Draft PR #413](https://github.com/kims34/openpilot-opkr/pull/413) head `f003ef6247e16fcc71bd3b1b20cd4904c4d984c0`.
- [Draft PR #418](https://github.com/kims34/openpilot-opkr/pull/418) head `2f98401cc50a6c6a25808a98516efd5bf0c944ee`.
- [OpenDART Draft PR #412](https://github.com/kims34/openpilot-opkr/pull/412) head `bf3d9514a87c53b1775e22ec9ba7711f6cecc49f`.
- [Investor-flow Draft PR #416](https://github.com/kims34/openpilot-opkr/pull/416) head `053de553646fc4765d2616544ca1e8d6bbdde35f`.
- KRX [#420](https://github.com/kims34/openpilot-opkr/pull/420) `fab3cbbd63a951a4e081f9e7f08c1391ca308581`, [#422](https://github.com/kims34/openpilot-opkr/pull/422) `c14857620973531013799e44625d43080904fd5f`, [#423](https://github.com/kims34/openpilot-opkr/pull/423) `0e38004363cac9fc4475556b3a1c445de9af407f`. All checked PRs are open, draft and unmerged.

## 2. Actual CI / source findings, narrowly interpreted

- [PR #413 Action 38508247773](https://github.com/kims34/openpilot-opkr/actions/runs/38508247773): **6/6 jobs PASS**, exact-parity job `115670744341` raw log: 34 immutable cases; digest SHA-256 `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34`; test outcomes identical; serial 1.7650 s, longest parallel suite 2.7079 s, speedup **0.652x** (slower). **Limited synthetic parity PASS**, real backtest / end-to-end CI speedup **NOT VERIFIED**.
- [PR #418 Action 39111405478](https://github.com/kims34/openpilot-opkr/actions/runs/39111405478): archived source job `117628139395` **FAIL-CLOSED** with `SourceDriftError`, `research_v1_runtime_manifest.py` expected Git blob SHA-1 `108f66714602a1bd3ae42c34dcca7c16e38f460b`, observed `e0055c66c59398fd4a1158077446d886b54c4e37`. Separate successful synthetic-only actions 39111405494 and 39111405562 do not waive this failure; runner adoption **NO-GO**.
- [Watchdog Action 41347016768](https://github.com/kims34/openpilot-opkr/actions/runs/41347016768) job `124968921851`: 4 watchdog + 31 research governance synthetic tests PASS, explicit `M20 PIT admission: NOT ATTESTED; orders: DISABLED; holdout: NOT AUTHORIZED`.
- [OpenDART source Action 38419439742](https://github.com/kims34/openpilot-opkr/actions/runs/38419439742): both offline and official candidate-row jobs SUCCESS, original/amended SGML row-shape and adjacent numeric signatures do **not** establish first-edition 2021/2022 exact standalone 3-month consolidated operating profit, periods, first-public availability timestamps, amendment lineage or historical corp/security mapping. [Newer PR #412 Actions 40263193758](https://github.com/kims34/openpilot-opkr/actions/runs/40263193758) and [40263181687](https://github.com/kims34/openpilot-opkr/actions/runs/40263181687): one offline no-network synthetic safety job each, SUCCESS; **no source PIT promotion**.
- [Investor flow Action 40262192831](https://github.com/kims34/openpilot-opkr/actions/runs/40262192831): 2/2 offline source-boundary jobs SUCCESS; investor-flow admission remains **NOT VERIFIED**.
- KRX [Actions 39714369327](https://github.com/kims34/openpilot-opkr/actions/runs/39714369327), [39714369438](https://github.com/kims34/openpilot-opkr/actions/runs/39714369438), [39714207925](https://github.com/kims34/openpilot-opkr/actions/runs/39714207925), [39001836000](https://github.com/kims34/openpilot-opkr/actions/runs/39001836000): synthetic/offline guard jobs successful (last is commit-associated success), not official calendar, trading-status, corporate-action or execution feasibility proof.
- Historic 2017–2022 KRX 1,565/1,565 weekday raw pairs **storage integrity PASS only** under previous independent evidence; 90 ambiguous sessions, 12,003 zero-activity rows and 27 rejected common-stock OHLC records are **not tradable-state PASS**. No new official historical source re-admission.

## 3. Railway production, actual read-only evidence

Project `d1c1a050-b7d6-41ce-b300-13c20f82a20a`, production `83d5840b-270e-4d3f-a941-a37fd4a55ff7`.

- `indexalert-pit-rebuild` service `225f2279-d728-4e1a-a3f3-2447ff0f9dc1`, deployment `8b354fc1-cfb2-4ef0-863e-67f7f5dda2b5` SUCCESS, **one running replica**. Latest returned runtime record **2026-11-01 14:46:22.425Z = 23:46:22 KST**, `COMMON_OHLC_NONPOSITIVE`, 27/803 common-stock rows, 27 zero-volume/value, `status=FAIL_CLOSED`, `ordering=DISABLED`, `session_manifest_sha256=null`, independent source/chronology/model admission false, orders/funds/permission false. A read-only log query from 2026-11-01 14:30Z found only 14:31Z and 14:46Z entries; approximately **9 h 32 min** log-observation gap at audit time. Running replica alone neither establishes successful ingestion nor proves outage. No restart or redeploy performed.
- `indexalert-krx-historical-worker` deployment `16c93d7c-7cd0-4d84-a327-298d2805376c` SUCCESS; current log query returned zero deploy entries, so no fresh source audit claim.
- `indexalert-runtime` deployment `eaaa9f67-b9f2-41d2-832c-7d6fad9b9b00` SUCCESS, log observed to **2026-11-02 00:18:46.572Z = 09:18:46 KST**. Separate index/FX alert service; not PIT authorization evidence.
- `indexalert-kiwoom-real-readonly` deployment `a77fb922-b679-4d88-92c4-03054ec579cd` SUCCESS, but environment status simultaneously says `online` and replica `running=0, crashed=1, total=1`; only startup logs (2026-10-29) returned. **Status inconsistency unresolved**, no account or credential action.
- Environment inventory `describe_environment` reported `staged=null`, while `environment_status` reported `patch:e113dacb-6705-4416-9997-dc694539d382` as staged, empty change list. **API views inconsistent**; do not accept or deploy.
- `indexalert-backend`, `indexalert-push`, `db-query-readonly` show offline/issues in environment status. They are not sufficient evidence that the isolated PIT worker failed; no changes made.

## 4. Independent gate decision

| Gate | Verdict |
|---|---|
| Original official 2021/2022 3-month CFS operating profit, first-filed semantics, exact public available-at, amendment lineage | **NOT VERIFIED / FAIL-CLOSED** |
| Historical corp-to-security mapping, KRX market calendar/tradability/corporate actions, fill constraints, commissions/taxes | **NOT VERIFIED / FAIL-CLOSED** |
| KRX 1,565 raw weekday pair storage integrity | **PASS (historical scope only)** |
| PR #413 immutable offline 34-case parity | **PASS (limited)** |
| PR #413 runtime acceleration in this measured regression phase | **FAIL as speed improvement (0.652x)** |
| PR #418 archived manifest source identity | **FAIL-CLOSED**, do not adopt |
| Official M20 PIT / label / Purged / CPCV / independent Holdout admission | **NOT VERIFIED / NO-GO** |
| After-cost/tax NetEV, PF, CAGR, MDD, ES95/99, concentration, year/date robustness, risk-adjusted annual net return | **NOT EVALUABLE — NO M20 RUN** |
| Live ordering, money movement, account authority, Champion promotion, PR merges, production deploy | **NOT AUTHORIZED** |

Frozen H5, M20 horizon20/purge20, WF504/126/126, Top3/NO_TRADE, predeclared costs, holdout policy and risk gates unchanged. No dependent training/capital transitions parallelized. Cache remains fail-closed unless source/data/code/Frozen/runtime/approval SHA-256 identity independently attested. Read-only postprocessing only may be parallelized.

## 5. Next independent evidence needed, in order

1. OpenDART source owner: authoritative original 2021/2022 standalone three-month CFS facts, exact period, first-public timestamp and complete correction lineage; explicit failure if absent, without amendment backfill.
2. KRX source owner: official exact-session calendar, historic listing/suspension/corporate-action and per-security mapping, realistic executable quotes/fills/lot costs/taxes, preserving 27 veto and 90 unresolved sessions until proven.
3. Runtime owner: resolve PR #418 archived manifest identity mismatch and parity/security guard divergence offline; independently prove actual end-to-end wall-time improvement before adoption, no performance data replay.
4. Railway read-only monitoring: distinguish lack of new PIT events from log transport/collector gap, reconcile crashed/online replica and staged patch views. No restart, staged acceptance or permission change without separate explicit authorization.
5. Only after all source/PIT/market gates independently PASS, seek separate authorization for **one preregistered M20** after-cost WF assessment; no Holdout recycling or Champion/Tiny Live promotion by inference.

**Writes this audit:** only this new document in a fresh isolated audit branch. No source/workflow modification, merge, deployment, order, money or permission change.
