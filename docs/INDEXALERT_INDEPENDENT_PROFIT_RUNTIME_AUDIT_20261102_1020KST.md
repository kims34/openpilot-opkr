# IndexAlert independent profitability and isolated runtime audit — 2026-11-02 10:20 KST

**Scope and authority:** Independent, read-only evidence inspection plus this isolated documentation commit. No official market-return computation, new model search, M20 profitability experiment, Holdout reuse, code/workflow change, broker access, Railway deployment, merge or Champion promotion. Frozen H5 and M20 preregistration remain immutable; `ORDERING=false / DISABLED`.

## 1. Verified GitHub refs and separation of work

Direct GitHub branch API and PR metadata reads:
- Research `index-alert-research-v1` HEAD `3b8b7830612a6284d7c7a60628cb527cb741627a`; development `index-alert-position-regen-fix-v1` HEAD `1e6367d2863a86c3470da13d81a955d277eba485`.
- KRX specialist `indexalert-krx-pit-source-audit-20261013` HEAD `073d2d49e95f69fb10b943b93e51bb179fb3c698`.
- [Draft PR #414](https://github.com/kims34/openpilot-opkr/pull/414) HEAD `e861630704fd15513f3d7ef7b48fd1c74654c6c7`. Core `docs/INDEXALERT_PROFITABILITY_INTEGRATION_GATE_2026-10-13.md` Git blob SHA-1 `984c933651f39f1ee9e26a1d7ac3893aaa5335be`. Comparison against prior HEAD `76a5cd0a46d4ac5acfd0e69dd3b5197585829a65`: one new independent 09:48 audit document only, no core gate change. That other Work's document was read to avoid duplicate specialist edits.
- [Draft PR #413](https://github.com/kims34/openpilot-opkr/pull/413) HEAD `f003ef6247e16fcc71bd3b1b20cd4904c4d984c0`; [Draft PR #418](https://github.com/kims34/openpilot-opkr/pull/418) HEAD `2f98401cc50a6c6a25808a98516efd5bf0c944ee` (base #413 branch).
- [OpenDART Draft #412](https://github.com/kims34/openpilot-opkr/pull/412) HEAD `bf3d9514a87c53b1775e22ec9ba7711f6cecc49f`; [investor-flow Draft #416](https://github.com/kims34/openpilot-opkr/pull/416) HEAD `053de553646fc4765d2616544ca1e8d6bbdde35f`.
- KRX specialist [#420](https://github.com/kims34/openpilot-opkr/pull/420) `fab3cbbd63a951a4e081f9e7f08c1391ca308581`, [#422](https://github.com/kims34/openpilot-opkr/pull/422) `c14857620973531013799e44625d43080904fd5f`, [#423](https://github.com/kims34/openpilot-opkr/pull/423) `0e38004363cac9fc4475556b3a1c445de9af407f`. All named PRs remained open/draft/unmerged at inspection.

## 2. Independent CI and original-document evidence (actual job/log reads)

- [Latest read-only Watchdog run #41368406818](https://github.com/kims34/openpilot-opkr/actions/runs/41368406818), 2026-11-02 00:40:24Z, job `125033414398` SUCCESS: 4 watchdog and 31 governance synthetic tests passed. Log explicitly: `M20 PIT admission: NOT ATTESTED; orders: DISABLED; holdout: NOT AUTHORIZED`. This is safety software, **not** source or economics admission.
- [OpenDART original-vs-correction candidate Action #38419439742](https://github.com/kims34/openpilot-opkr/actions/runs/38419439742) two jobs SUCCESS (candidate shapes/numeric adjacency only). Independently inspected [2022 original official source job #115280695115](https://github.com/kims34/openpilot-opkr/actions/runs/38392847048): first-filed ZIP SHA-256 `56639d8f6ebbecf14cd8bc3179d75d01162e2cd7bbdf8f6a3c9479b44f5084bb`, 15 candidate operating-label row shapes, no bound Q3 standalone 3-month CFS fact. [2021 original official job #121377826016](https://github.com/kims34/openpilot-opkr/actions/runs/40262532310): ZIP SHA-256 `8728c0a3c12761ca19e9c6455bea8f1bed0e4c1ebc2e21dc263c373a82a2b625`, 1,728 table shapes, 13 operating-label candidates, zero same-table Q3-period or 3-month-bound labels; first publication instant and cross-year comparator linkage remain false. These hashes were verified as original official job **log claims**, not independently rehashed ZIP bytes here. Latest [PR #412 synthetic jobs #40263193758](https://github.com/kims34/openpilot-opkr/actions/runs/40263193758) and [#40263181687](https://github.com/kims34/openpilot-opkr/actions/runs/40263181687) each SUCCESS but not source/PIT approval.
- KRX 2017–2022 1,565/1,565 private weekday daily/master stored-pair SHA integrity **PASS under prior independent storage audit**, not independently rehashed private bytes this run. 90 uncertain historical sessions, 12,003 zero-activity rows and separate prospective 27 common-stock invalid OHLC cases remain vetoed; market calendar, historic issuer/security mapping, suspension/delisting, corporate actions, real bid/ask, fill/lot and costs/taxes **NOT VERIFIED**. [KRX offline CI #39714369327](https://github.com/kims34/openpilot-opkr/actions/runs/39714369327), [#39714369438](https://github.com/kims34/openpilot-opkr/actions/runs/39714369438), [#39714207925](https://github.com/kims34/openpilot-opkr/actions/runs/39714207925), [#39001836000](https://github.com/kims34/openpilot-opkr/actions/runs/39001836000) SUCCESS, synthetic-only.
- [PR #413 latest associated run #38508247773](https://github.com/kims34/openpilot-opkr/actions/runs/38508247773) **6/6 jobs SUCCESS**, exact-parity job `115670744341` log confirms immutable 34 cases, SHA-256 `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34`, identical outcomes. Serial regression 1.7650 s vs parallel longest 2.7079 s = **0.652x** (slower). Historic [#38381997417](https://github.com/kims34/openpilot-opkr/actions/runs/38381997417), [#38382214223](https://github.com/kims34/openpilot-opkr/actions/runs/38382214223), [#38419111311](https://github.com/kims34/openpilot-opkr/actions/runs/38419111311) each 6/6 jobs SUCCESS. Limited offline parity PASS; end-to-end CI and official backtest acceleration **NOT VERIFIED**.
- [PR #418 archived-source run #39111405478](https://github.com/kims34/openpilot-opkr/actions/runs/39111405478), job `117628139395` **FAIL-CLOSED** with `SourceDriftError`: `research_v1_runtime_manifest.py` expected Git blob SHA-1 `108f66714602a1bd3ae42c34dcca7c16e38f460b`, observed `e0055c66c59398fd4a1158077446d886b54c4e37`. [One-runner synthetic #39111405562](https://github.com/kims34/openpilot-opkr/actions/runs/39111405562) SUCCESS does not waive failed archive identity. PR #418 adoption **NO-GO**.
- [Chronology Anchor #41091128151](https://github.com/kims34/openpilot-opkr/actions/runs/41091128151) FAILED at `/anchor/latest` HTTP 404 (2026-10-30); independent chronology admission absent.

## 3. Railway production read-only operational evidence

Project `d1c1a050-b7d6-41ce-b300-13c20f82a20a`, production `83d5840b-270e-4d3f-a941-a37fd4a55ff7`. Latest deployment inventory and runtime logs read; no deploy action.

- `indexalert-pit-rebuild` service `225f2279-d728-4e1a-a3f3-2447ff0f9dc1`, deployment `8b354fc1-cfb2-4ef0-863e-67f7f5dda2b5` SUCCESS, running replicas 1/1. Targeted read-only log query from `2026-11-01T14:40:00Z` returned **one** entry, at `2026-11-01T14:46:22.425Z` = 23:46:22 KST: `status=FAIL_CLOSED`, `COMMON_OHLC_NONPOSITIVE`, 27/803 common-stock rows invalid and 27 zero-volume/value rows, `session_manifest_sha256=null`, independent source/chronology/model flags false, `ordering=DISABLED`, no order/funds/permission authority. At approximately 10:20 KST the last observable PIT event was ~10 h 34 min old. Log gap is an **observability blocker**, not proof of service outage or of successful ingestion. Do not restart/redeploy without explicit approval.
- `indexalert-krx-historical-worker` deployment `16c93d7c-7cd0-4d84-a327-298d2805376c` SUCCESS; no new official trading-state evidence. `indexalert-runtime` deployment `eaaa9f67-b9f2-41d2-832c-7d6fad9b9b00` SUCCESS, separate ETF/FX index alert logs observed to `2026-11-02T01:19:44Z` = 10:19:44 KST, not PIT authorization.
- `indexalert-kiwoom-real-readonly` deployment `a77fb922-b679-4d88-92c4-03054ec579cd` SUCCESS, but environment status simultaneously shows `online` and replicas `running=0, crashed=1, total=1`; read-model inconsistency unresolved. No account/credential action.
- `environment_status.pendingWork` lists `patch:e113dacb-6705-4416-9997-dc694539d382` staged with empty changes; `get_staged_changes` reports `staged=null`. Conflicting Railway read APIs; no staged patch accepted. Other services `indexalert-backend`, `indexalert-push`, `db-query-readonly` show offline/issues, not by themselves PIT proof.

## 4. Formal independent gate verdict

| Evidence gate | Decision |
|---|---|
| First-filed 2021/2022 exact 3-month consolidated operating profit, vintage/public available-at, correction lineage | **NOT VERIFIED / FAIL-CLOSED** |
| Historical corp-security mapping, official KRX sessions/stock status/corporate actions, fills, commission/taxes | **NOT VERIFIED / FAIL-CLOSED** |
| 1,565 raw weekday private storage pairs | **PASS (historic storage-only scope)** |
| PR #413 fixed 34-case synthetic parity | **PASS (limited)** |
| PR #413 measured test-phase speedup | **FAIL** (0.652x) |
| PR #418 immutable archived-source identity | **FAIL-CLOSED / NO-GO** |
| M20 PIT/labels/Purged/CPCV/independent Holdout admission | **NOT VERIFIED / NO-GO** |
| After-cost/tax NetEV, PF, CAGR, MDD, ES95/99, risk-adjusted annual net return, concentration and time robustness | **NOT EVALUABLE: NO AUTHORIZED M20 RUN** |
| Live orders, funds, account authority, Champion promotion, merges, deployments | **NOT AUTHORIZED** |

Frozen H5 (consumed/failed Holdout cannot be reused), M20 horizon20/purge20, WF504/126/126, Champion/Top3/no-rank-4-backfill/NO_TRADE, PIT/label/CPCV and fixed risk/cost/tax gates remain unchanged. Cache must fail closed unless independently approved source/data/code/Frozen policy/runtime/approval evidence SHA-256 all match. Only independent read-only postprocessing can be parallelized; never dependent retraining or capital transition.

## 5. Nonduplicative next actions

1. DART specialist: first-public original Q3 2021/2022 3-month CFS fact, period, original-vs-amended lineage and exact available-at; absent facts remain explicitly unavailable, never amended-backfilled.
2. KRX specialist: independent official calendar/session + historic security status, issuer mappings, corporate actions and executable quotes/fees/taxes; preserve unresolved 90-day and 27-row vetoes.
3. Runtime specialist: independently resolve #418 archived SHA drift and security parity, then demonstrate end-to-end wall-time improvement **offline-only**, not by changing Frozen or running market returns.
4. Railway monitoring: read-only isolate PIT event production vs log transport gap and resolve online/crashed and staged patch discrepancies. No restart, deployment or credentials.
5. Profitability orchestration: only after every PIT/market/source gate passes and a **separate explicit authorization** is granted, perform one frozen M20 after-tax risk-adjusted WF evaluation. No Holdout reuse, new M20 experiment, Champion promotion or real trading before that.

**New independent decision-changing evidence this run:** none. This audit independently corroborates first-filed 2021 source log and latest watchdog, but no new authority. Only this new file in a dedicated audit branch is written; all specialist branches and operating code remain untouched.
