# IndexAlert independent PIT/profitability and isolated runtime audit — 2026-11-03 08:18 KST

**Scope:** GitHub and Railway read-only inspection, followed only by this uniquely named audit document. No official M20 economic run, official return calculation, consumed Holdout replay, model exploration, trading, capital movement, credentials, workflow edit, merge, deployment or Champion promotion. ORDERING=false/disabled.

## Source pinning / change isolation

- Research `index-alert-research-v1`: `3b8b7830612a6284d7c7a60628cb527cb741627a` (independently corroborated by PR #413/#414 base SHA).
- Development `index-alert-position-regen-fix-v1`: `1e6367d2863a86c3470da13d81a955d277eba485` (PR #420 base SHA and deployed KRX worker commit).
- Draft [PR #414](https://github.com/kims34/openpilot-opkr/pull/414) inspection HEAD `0146589b440efe0d76748b8352354cbe554874fb`; frozen integration gate `docs/INDEXALERT_PROFITABILITY_INTEGRATION_GATE_2026-10-13.md` blob SHA-1 `984c933651f39f1ee9e26a1d7ac3893aaa5335be` unchanged.
- Open, draft heads: [#412](https://github.com/kims34/openpilot-opkr/pull/412) `bf3d9514a87c53b1775e22ec9ba7711f6cecc49f`; [#413](https://github.com/kims34/openpilot-opkr/pull/413) `f003ef6247e16fcc71bd3b1b20cd4904c4d984c0`; [#418](https://github.com/kims34/openpilot-opkr/pull/418) `2f98401cc50a6c6a25808a98516efd5bf0c944ee`; KRX [#420](https://github.com/kims34/openpilot-opkr/pull/420) `fab3cbbd63a951a4e081f9e7f08c1391ca308581`, [#422](https://github.com/kims34/openpilot-opkr/pull/422) `c14857620973531013799e44625d43080904fd5f`, [#423](https://github.com/kims34/openpilot-opkr/pull/423) `0e38004363cac9fc4475556b3a1c445de9af407f`. No branch edits or experiments in specialist workspaces.

## Direct evidence reconfirmation (not admission)

- [Chronology Action #41515392296](https://github.com/kims34/openpilot-opkr/actions/runs/41515392296), job `125517531544`: **FAIL**, 20 anchor-fetch attempts exhausted with HTTP 404 at 2026-11-02 20:40:58 UTC; downstream validation job `125517534895` skipped. GitHub job log corroborates exact URL `https://indexalert-pit-rebuild-production.up.railway.app/anchor/latest`.
- Railway `indexalert-pit-rebuild` HTTP stream directly returns `GET /anchor/latest` HTTP **404**, including 2026-11-02 20:34:57, 20:36:57, 20:38:57 and 20:40:58 UTC. This is independent corroboration of failed HTTP status, **not** evidence of exact response body, missing private file path or root cause. No newer successful anchor response was returned in the inspected stream.
- Railway `indexalert-pit-rebuild` latest returned deploy log at 2026-11-02 14:46:22 UTC (23:46:22 KST) reports `FAIL_CLOSED`, `COMMON_OHLC_NONPOSITIVE`, 27/803 common-stock rows, source failure session `2026-09-28`, `session_manifest_sha256=null`, all independent source/chronology/model admission flags false, `ordering=DISABLED`. No later application log returned; neither recovery nor outage inferred. Deployment `8b354fc1-cfb2-4ef0-863e-67f7f5dda2b5` SUCCESS, 1/1 running replica.
- Railway KRX worker deployment `16c93d7c-7cd0-4d84-a327-298d2805376c` SUCCESS at development SHA `1e6367d...`; no new worker deploy log returned. Environment `get_status` shows `stagedChanges=null`, while `pendingWork` still lists an empty-change staged patch `e113dacb-6705-4416-9997-dc694539d382`: cross-view state NOT VERIFIED. Kiwoom REAL read-only shows deployment SUCCESS / UI online but replica snapshot 0 running / 1 crashed: NOT VERIFIED, no intervention.
- [OpenDART #412 Actions #40263193758](https://github.com/kims34/openpilot-opkr/actions/runs/40263193758) and [#40263181687](https://github.com/kims34/openpilot-opkr/actions/runs/40263181687) offline-only PASS. Prior [SGML original/correction #38419439742](https://github.com/kims34/openpilot-opkr/actions/runs/38419439742) 15 candidate rows/numeric adjacent signatures are shape evidence only. Exact 2021/2022 first-published consolidated three-month Q3 operating profit, period, correction lineage, first public available-at, contemporaneous company/security mapping: **NOT VERIFIED**.
- KRX 2017–2022 1,565/1,565 weekday private raw pairs stored and SHA-checked: **LIMITED PASS** for storage only. Official 90-day session/holiday classification, 12,003 zero-activity rows, 27/803 suspect OHLC, historical trading status, actions, execution, fees/slippage and taxes: **NOT VERIFIED / FAIL-CLOSED**. [KRX #420 CI #39714369438](https://github.com/kims34/openpilot-opkr/actions/runs/39714369438) synthetic-only PASS, not market admission.

## Isolated offline runtime CI

- [#413 CI #38508247773](https://github.com/kims34/openpilot-opkr/actions/runs/38508247773) **6/6 jobs PASS**; original exact-parity job `115670744341` reports 34 fixed outcomes identical, SHA-256 `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34`, serial 1.7650 s, parallel longest 2.7079 s, test-phase speed ratio **0.652x** (slower). No end-to-end CI or real official backtest speedup.
- [#418 archived pinned CI #39111405478](https://github.com/kims34/openpilot-opkr/actions/runs/39111405478) job `117628139395` **FAIL-CLOSED**: `research_v1_runtime_manifest.py` expected SHA-1 `108f66714602a1bd3ae42c34dcca7c16e38f460b`, observed `e0055c66c59398fd4a1158077446d886b54c4e37`. Separate [candidate merge proof #39111405494](https://github.com/kims34/openpilot-opkr/actions/runs/39111405494) and [one-runner #39111405562](https://github.com/kims34/openpilot-opkr/actions/runs/39111405562) pass synthetic-only, do **not** override SHA drift.
- Cache requires independent source/data/code/Frozen/runtime/approval evidence SHA-256 exact match, otherwise fail-closed. Parallelism limited to read-only independent postprocessing; no dependent retraining or capital transition.

## Independent decision / follow-up

| Gate | Decision |
|---|---|
| Original-filing public PIT, exact 2021/2022 3-month operating profit and correction lineage | NOT VERIFIED |
| Historical KRX market states, corporate actions, tradability, fills, fees and tax | NOT VERIFIED / FAIL-CLOSED |
| Prospective chronology anchor | FAIL-CLOSED (404, response body and private root unverified) |
| Offline CI parity #413 | LIMITED PASS (34 cases only, 0.652x speed ratio) |
| Archived source pin #418 | FAIL-CLOSED (blob mismatch) |
| H5 consumed/failed Holdout and Dynamic promotion | NO-GO |
| M20 NetEV/PF/CAGR/MDD/ES95/99, concentration, date robustness, annual after-tax risk-adjusted net return | NOT EVALUABLE / NO-GO |

**Next safe steps:** source owner should use already authorized read-only evidence to inspect exact anchor HTTP body, mounted private file root and eligible filename/format without disclosing private raw data; DART and KRX owners independently establish original/public PIT and official historical tradability; optimization owner independently reconcile archived SHA drift without relaxing gates. Preserve Frozen H5, M20 horizon20/purge20, WF504/126/126, PIT/labels/Purged/CPCV/independent Holdout/Champion/Top3/NO_TRADE and preregistered cost/risk/promotion gates. No M20 economic run, workflow security bypass, merge, deploy, real order, fund or credential change.

**No new admission-grade evidence or material change to NO-GO observed in this inspection.**
