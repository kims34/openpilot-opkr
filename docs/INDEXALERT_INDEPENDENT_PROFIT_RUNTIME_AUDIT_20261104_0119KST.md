# IndexAlert independent profitability / isolated runtime audit — 2026-11-04 01:19 KST

Scope: Read-only GitHub PR, Actions jobs and Railway production deployment/log review; this audit document is the only repository change. No official backtest, performance search, model training, workflow modification, deploy, merge, orders, permissions, Champion promotion, or capital movement.

## Exact verified GitHub refs
- PR #414 integration: draft/open, HEAD `18c5418d9684d1717df58261ea27f28e514385b2`, base SHA `3b8b7830612a6284d7c7a60628cb741627a`; integration gate `docs/INDEXALERT_PROFITABILITY_INTEGRATION_GATE_2026-10-13.md` blob SHA-1 `984c933651f39f1ee9e26a1d7ac3893aaa5335be`.
- PR #413 optimization: draft/open, HEAD `f003ef6247e16fcc71bd3b1b20cd4904c4d984c0`.
- PR #418 single runner: draft/open, HEAD `2f98401cc50a6c6a25808a98516efd5bf0c944ee`.
- PR #412 OpenDART: draft/open, HEAD `bf3d9514a87c53b1775e22ec9ba7711f6cecc49f`.
- KRX PR #420: draft/open HEAD `fab3cbbd63a951a4e081f9e7f08c1391ca308581`; #422: `c14857620973531013799e44625d43080904fd5f`; #423: `0e38004363cac9fc4475556b3a1c445de9af407f`.
- Research branch latest HEAD and development branch latest HEAD: NOT VERIFIED by direct branch-ref resolution this run; PR bases are NOT substituted for live branch heads. Earlier development SHA `1e6367d2863a86c3470da13d81a955d277eba485` also appears in KRX Railway deployment metadata, but this is not proof of current development HEAD.

## CI and operational evidence
- GitHub Actions [38419111311](https://github.com/kims34/openpilot-opkr/actions/runs/38419111311): six named jobs completed SUCCESS (gates, cache, cost, risk, serial reference, exact parity). [38419649711](https://github.com/kims34/openpilot-opkr/actions/runs/38419649711): one-runner-offline-comparison SUCCESS. These are offline synthetic software validation only; immutable 34-case digest `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34`, 13 adversarial and 28 synthetic cases, and 2.9656s vs 2.6209s / 1.1315x were previously reported, NOT independently recomputed this run.
- [Chronology Anchor Action 41515392296](https://github.com/kims34/openpilot-opkr/actions/runs/41515392296): auto-anchor FAIL, validation SKIPPED. No successful chronology admission established.
- Railway IndexAlert project `d1c1a050-b7d6-41ce-b300-13c20f82a20a`: historical KRX worker deployment `16c93d7c-7cd0-4d84-a327-298d2805376c` SUCCESS (2026-10-12 13:07 UTC, commit `1e6367d2863a86c3470da13d81a955d277eba485`); PIT rebuild deployment `8b354fc1-cfb2-4ef0-863e-67f7f5dda2b5` SUCCESS (2026-10-10 10:28 UTC, commit `e57054ecdb3e734ced3c9a981b887d9b5fc60f97`). Deployment success is not source PIT acceptance.
- PIT rebuild runtime latest log in sampled 50 entries: 2026-11-03 14:46:33 UTC (23:46:33 KST) `KRXProspectiveOpenAPISourceError / COMMON_OHLC_NONPOSITIVE`; ongoing repeated errors. No admission or orders inferred.
- Historical KRX worker runtime log query returned no entries in sampled window; this does not invalidate earlier archived private SHA-pair evidence, nor verify current market tradability.

## Independent gate decisions
- 2017–2022 KRX 1565/1565 weekday raw-pair persistence: historical archival integrity PASS (prior attestation, not rehashed here). Official exchange calendar, trading halts/delistings, corporate actions, historical identity/security mapping, executions, costs/taxes and PIT tradability: NOT VERIFIED / FAIL-CLOSED; 90-day classification and 12003 zero-activity exclusions remain.
- OpenDART SGML original/correction 15 operating-income candidate rows and adjacent-number signatures: historical limited evidence, not an original-filing Q3 consolidated operating profit period/lineage/available-at proof. 2021/2022 original first-three-month values and corrections: NOT VERIFIED / FAIL-CLOSED.
- Chronology anchor: FAIL; independent validated chronology: NOT VERIFIED.
- Offline isolated #413/#418 CI: limited PASS for software test execution; source/data/Frozen/runtime/approval SHA-256 cache equality, full CI wall-clock improvement, official PIT backtest speedup: NOT VERIFIED.
- NetEV, PF, CAGR, MDD, ES95/99, concentration, regime stability and annual after-tax risk-adjusted net return for M20: NOT EVALUABLE / NO-GO. Do not convert archived H5 or consumed Holdout / Dynamic results into independent evidence.

## Policy / next steps
Frozen H5; M20 horizon20/purge20, WF504/126/126, PIT/label/Purged/CPCV/independent Holdout/Champion/Top3/NO_TRADE, execution and promotion criteria unchanged. ORDERING=false. Cache fail-closed unless independently approved source/data/code/Frozen policy/runtime/approval evidence SHA-256 match; parallelize only independent read-only postprocessing, not dependent retraining or capital transitions.
Next: independently retrieve current branch refs, verify official original-filing available-at and correction lineage with original SHA, reconcile official KRX calendar/trading-state/corporate actions/executability, resolve chronology anchor failure, and recompute fixed synthetic digest on permitted isolated CI evidence. No M20 economics run before formal source-PIT admission. No merge/deploy/trade.
