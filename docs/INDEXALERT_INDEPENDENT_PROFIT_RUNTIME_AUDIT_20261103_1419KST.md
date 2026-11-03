# IndexAlert independent profit and runtime audit — 2026-11-03 14:19 KST

Scope: read-only GitHub PR metadata, original GitHub Actions job status, Railway deployment/runtime log samples. This is not a source PIT admission, historical return calculation, strategy change or order authorisation.

## GitHub immutable PR HEADs (read from get_pr_info in this audit)
- OpenDART Draft #412: bf3d9514a87c53b1775e22ec9ba7711f6cecc49f; draft, open.
- Runtime optimisation Draft #413: f003ef6247e16fcc71bd3b1b20cd4904c4d984c0; draft, open, mergeable=false.
- Profitability gate Draft #414: 18c5418d9684d1717df58261ea27f28e514385b2; draft, open. Base SHA 3b8b7830612a6284d7c7a60628cb527cb741627a is historical PR base, NOT verified latest research branch HEAD.
- Single runner Draft #418: 2f98401cc50a6c6a25808a98516efd5bf0c944ee; draft, open.
- KRX Draft #420: fab3cbbd63a951a4e081f9e7f08c1391ca308581; draft, open.
- KRX Draft #422: c14857620973531013799e44625d43080904fd5f; draft, open.
- KRX Draft #423: 0e38004363cac9fc4475556b3a1c445de9af407f; draft, open.
- Research/development branch current HEADs were NOT independently fetched as branch commit pointers in this run; previous reported research bba25477b41fcd0a8beca78168abb0009fb5b82c and development 1e6367d2863a86c3470da13d81a955d277eba485 remain prior evidence only. Railway KRX worker deployment references development commit 1e6367d2863a86c3470da13d81a955d277eba485 (2026-10-12).

## Original CI job recheck
- Actions 38419111311: six of six job conclusions success (cost, risk, gates, cache, serial, exact-parity).
- Actions 38419649711: one of one job conclusion success (one-runner-offline-comparison).
- Actions 41515392296: auto-anchor failure, validation skipped.
- Prior 34-case SHA-256 5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34 and 13 adversarial/28 synthetic cases are inherited evidence; no artifact rehash in this run.
- Single runner serial 2.9656 s / concurrent 2.6209 s = 1.1315x limited regression-phase ratio, not full CI or official backtest speedup. Prior archived manifest SHA mismatch remains FAIL-CLOSED pending independent source/artifact proof. PR #413 mergeable=false is metadata only; root cause not independently diagnosed.

## Railway live read-only evidence
- Project IndexAlert d1c1a050-b7d6-41ce-b300-13c20f82a20a; production 83d5840b-270e-4d3f-a941-a37fd4a55ff7.
- PIT service 225f2279-d728-4e1a-a3f3-2447ff0f9dc1 deployment 8b354fc1-cfb2-4ef0-863e-67f7f5dda2b5, status SUCCESS (deployment status is not PIT PASS).
- PIT log samples for 2026-11-02 show COMMON_OHLC_NONPOSITIVE, 27 nonpositive OHLC out of 803 common stock rows, session_manifest_sha256=null, independent_source_admission_verified=false, FAIL_CLOSED, ORDERING=DISABLED. Latest returned sample around 2026-11-02 13:01 UTC; do not infer service outage from absent later entries.
- KRX historical worker deployment 16c93d7c-7cd0-4d84-a327-298d2805376c SUCCESS; no new historical audit log entries returned.
- Kiwoom REAL read-only deployment a77fb922-b679-4d88-92c4-03054ec579cd SUCCESS, 2026-10-29; runtime TOKEN_OR_LOGIN_AUTH, detail 8050, TOKEN_OK=false, WS_CONNECTED=false, TYPE00_EVENT_COUNT=0, ORDERING=DISABLED.
- Indexalert-runtime logs are active as of 2026-11-03 05:19 UTC, but these are index alert market checks, NOT admitted KRX/DART source PIT evidence.
- This run did not return a fresh /anchor/latest HTTP sample, so earlier 404 and anchor recovery remain NOT VERIFIED.

## Gate decisions
- Historical OpenDART 2021/2022 original-filing first three-month consolidated operating profit, exact available-at, correction lineage: NOT VERIFIED.
- Historical issuer/security mapping, KRX exact official calendar/status/corporate actions, historical tradeability/fills, cost/tax authority: NOT VERIFIED.
- Prior 1565/1565 private weekday pair storage integrity: historical limited PASS, not independently rehashed in this run; 90 calendar exceptions and 12003 zero-activity rows remain quarantined.
- Runtime offline regression CI jobs: limited PASS; production backtest speedup: NOT VERIFIED. Archived manifest mismatch: FAIL-CLOSED.
- M20 NetEV/PF/CAGR/MDD/ES95/ES99, return concentration, period robustness and after-tax annual risk-adjusted net profitability: NOT EVALUABLE / NO-GO.

## Hard constraints and next checks
Frozen H5, M20 horizon20/purge20, WF504/126/126, PIT/label/Purged/CPCV/independent Holdout/Champion/Top3/NO_TRADE, cost/tax/fill/risk/advancement rules remain unchanged. Never reuse consumed H5/Dynamic holdout. Only synthetic offline software/policy checks until independently verified original official PIT and tradability are admitted. Cache only on exact independent source/data/code/Frozen policy/runtime/evidence SHA-256 equality; fail closed. Parallelise only independent read-only postprocessing, never dependent retraining or capital transitions. No official return/market performance experiment, M20 run, merge, deployment, account change, money movement, Champion promotion or orders. ORDERING=false.

Next: verify exact branch HEADs through branch-specific commit read; obtain official original-filing publication-time and correction-chain evidence; obtain original exchange session/status and corporate-action receipts and private exact-set comparisons under separate authority; independently reproduce archived manifest hash before any performance claim. Do not modify other specialist work.
