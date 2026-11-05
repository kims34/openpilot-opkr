# IndexAlert independent profitability and runtime audit — 2026-11-05 09:17 KST

Scope: read-only GitHub PR/Actions and Railway production review. Independent isolated documentation only. No market backtest, deployment, merge, workflow edit, live order or model tuning.

## GitHub snapshot
Research base ref evidenced by PR #412/#413/#414: `3b8b7830612a6284d7c7a60628cb527cb741627a` (NOT a separately verified current research branch HEAD). Development base evidenced by PR #420: `1e6367d2863a86c3470da13d81a955d277eba485` (NOT a separately verified current development branch HEAD).

All fetched PRs OPEN, Draft, unmerged:
- #412 OpenDART HEAD `bf3d9514a87c53b1775e22ec9ba7711f6cecc49f`
- #413 runtime optimization HEAD `f003ef6247e16fcc71bd3b1b20cd4904c4d984c0`
- #414 profitability integration HEAD `18c5418d9684d1717df58261ea27f28e514385b2`
- #418 single runner HEAD `2f98401cc50a6c6a25808a98516efd5bf0c944ee`
- KRX #420 `fab3cbbd63a951a4e081f9e7f08c1391ca308581`, #422 `c14857620973531013799e44625d43080904fd5f`, #423 `0e38004363cac9fc4475556b3a1c445de9af407f`.

Actions jobs checked via original run IDs: #38381997417 6/6 success; #38382214223 6/6 success; #38419111311 6/6 success; #38419649711 1/1 success; #38419439742 2/2 success; chronology #41515392296 auto-anchor failure, validation skipped. Job conclusions PASS as CI execution status only. Previous 34-case fixed SHA `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34`, 13 adversarial mocks, 28 synthetic cases and 2.9656/2.6209=1.1315x regression-phase comparison were not independently recomputed in this run; whole-CI and official backtest speedup NOT VERIFIED.

## Railway production read-only snapshot
Project `d1c1a050-b7d6-41ce-b300-13c20f82a20a`, production environment `83d5840b-270e-4d3f-a941-a37fd4a55ff7`.
PIT rebuild SUCCESS deployment `8b354fc1-cfb2-4ef0-863e-67f7f5dda2b5`, running 1/1. KRX worker SUCCESS deployment `16c93d7c-7cd0-4d84-a327-298d2805376c`, running 0, crashed 0, total 1 (worker lifecycle not inferred). Both have zero returned deploy log entries for query since 2026-11-05 08:00 KST; absence of logs does not prove success or PIT admission.
Kiwoom real readonly UI online, deployment `a77fb922-b679-4d88-92c4-03054ec579cd`, running 0/crashed 1. Push offline (1 warning), backend offline (4 warnings), db-query-readonly offline (1 critical). Pending staged patch `e113dacb-6705-4416-9997-dc694539d382` untouched.

## Independent gate judgments
- GitHub CI job conclusions: PASS (execution outcomes only); chronology anchor: FAIL; validation SKIPPED.
- Historical Railway KRX 1565/1565 weekday raw pair integrity: historical reported PASS, not independently rehashed this run. Official trading calendar, security status, corporate actions, fillability and fee/tax provenance: NOT VERIFIED.
- OpenDART 15 candidate rows/signatures: historical reported match; original-filing meaning, public available-at timestamp, 2021/2022 initial three-month consolidated operating-profit period/correction lineage: NOT VERIFIED.
- Historical issuer/security mapping, original source SHA admission, PIT chronology, costs and taxes, NetEV/PF/CAGR/MDD/ES95/99, concentration, time-regime robustness and independent annual risk-adjusted after-tax net profitability: NOT VERIFIED.
- M20 horizon20/purge20, WF504/126/126, Frozen H5, independent Holdout, Champion/Top3/NO_TRADE, Purged/CPCV, execution/risk thresholds: unchanged; M20 NOT EVALUABLE / NO-GO; ORDERING=false.
- Runtime optimization: isolated synthetic CI PASS, full CI and official backtest acceleration NOT VERIFIED. Cache fail-closed unless source/data/code/Frozen/runtime/approval evidence SHA-256 all match. Parallelize only independent read-only postprocessing; never dependent retraining or capital transition.

## Next safe work
1. Independent original filing/public timestamp and corrected consolidated 3-month operating-profit lineage attestation with source SHA.
2. Independent official KRX calendar/status/corporate action and fillability/cost/tax source SHA verification, excluding zero activity from tradable observations.
3. Repair chronology anchor evidence in separate owner-approved workflow (do not edit workflow here), then independent source/PIT admission before any M20 economic run.
4. Independently recompute immutable synthetic 34-case SHA and runner timings without market data, keeping #413 and #418 separate; inspect Kiwoom crashed replica read-only.

No existing team code edited. No operational changes or permissions changed.