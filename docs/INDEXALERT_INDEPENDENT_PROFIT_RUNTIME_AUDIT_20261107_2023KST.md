# IndexAlert independent profitability and isolated optimisation audit — 2026-11-07 20:23 KST

Scope: read-only GitHub and Railway production evidence. No model search, official market backtest, M20 economic run, order, deploy, merge, workflow modification or promotion.

## Exact source refs
- research index-alert-research-v1: df474df348f22aa38b1dedaa59fcff66e548b406 (GitHub branch API read 2026-11-07).
- development index-alert-position-regen-fix-v1: 1e6367d2863a86c3470da13d81a955d277eba485.
- PR #414 OPEN/Draft head 18c5418d9684d1717df58261ea27f28e514385b2; docs/INDEXALERT_PROFITABILITY_INTEGRATION_GATE_2026-10-13.md blob 984c933651f39f1ee9e26a1d7ac3893aaa5335be.
- #413 OPEN/Draft head f003ef6247e16fcc71bd3b1b20cd4904c4d984c0; #418 OPEN/Draft head 2f98401cc50a6c6a25808a98516efd5bf0c944ee; #412 OPEN/Draft head bf3d9514a87c53b1775e22ec9ba7711f6cecc49f.
- KRX #420 OPEN/Draft fab3cbbd63a951a4e081f9e7f08c1391ca308581; #422 OPEN/Draft c14857620973531013799e44625d43080904fd5f; #423 OPEN/Draft 0e38004363cac9fc4475556b3a1c445de9af407f.

## Actions inspected (latest attempt jobs)
- #38381997417, #38382214223, #38419111311, #38498552499: each 6/6 success, offline synthetic parity only.
- #38419649711: 1/1 success, offline single-runner only; prior frozen 34-case SHA 5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34, additional 28 synthetic cases are historical claims, not freshly re-hashed in this run.
- #38419439742: 2/2 success, candidate row tests; not official public-available-at approval.
- #41515392296: auto-anchor failure, validation skipped. No chronology approval.

## Railway production evidence
Project d1c1a050-b7d6-41ce-b300-13c20f82a20a, environment 83d5840b-270e-4d3f-a941-a37fd4a55ff7.
- PIT service 225f2279-d728-4e1a-a3f3-2447ff0f9dc1, deployed SUCCESS, replica 1/1. Logs at 2026-11-07 10:00,10:15,10:30,10:45,11:00,11:15 UTC each report COMMON_OHLC_NONPOSITIVE, 27 nonpositive OHLC and 27 zero-volume/value among 803 common-stock rows, source_failure_session 2026-09-28, session_manifest_sha256 null, independent source/chronology/model admission false, fresh_alpha_observation_admitted false, ordering DISABLED, FAIL-CLOSED.
- KRX historical worker 003812ee-102b-42b6-bda4-36925885b428: deployed SUCCESS, 0 running/0 crashed; no new deploy logs in 10:00–11:30 UTC window.
- Kiwoom real read-only 93074d5f-70b3-48e4-8671-a3c5b23daf7e: deployed SUCCESS but 0 running/1 crashed; no new deploy logs in window. Service health remains a blocker, not evidence of broker readiness.
- Runtime 37902fde-ca05-43e0-bc76-278992bf7732: 1/1 running; logs 11:22 UTC Investing.com FX HTTPError -> Yahoo fallback; closed/extended data unavailable for some cards. Runtime market display is not PIT validation.
- db-query-readonly: one critical issue. describe_environment staged=null while environment_status pendingWork shows empty staged patch e113dacb-6705-4416-9997-dc694539d382: inconsistent read surfaces; no accept/deploy.

## Gates (PASS / FAIL / NOT VERIFIED)
- Historical KRX 1565/1565 private weekday source pair hash storage: PASS within historical integrity scope only (2026-10-14 evidence); actual official session calendar, historical trading status, corporate actions, executable fills: NOT VERIFIED.
- Prospective source admission for 2026-09-28: FAIL-CLOSED (27/803 nonpositive common-stock OHLC); not equivalent to proving all source data false.
- Original filing exact public available-at, 2021/2022 first-three-month consolidated operating-profit period/amendment lineage, historical issuer/security mapping: NOT VERIFIED.
- Cost/tax adjusted NetEV, PF, CAGR, MDD, ES95/99, concentration, regime robustness and independent holdout: NOT VERIFIED; no authorised economic run.
- Synthetic optimisation regression CI: PASS in scoped jobs; 2.9656s serial vs 2.6209s concurrent = 1.1315x regression-phase ratio from historical evidence only; whole CI / official backtest acceleration NOT VERIFIED.
- Chronology anchor CI: FAIL; validation SKIPPED.
- M20 PIT / economic RUN: NO-GO. ORDERING=false retained as observed disabled.

## Frozen controls and next safe steps
Preserve Frozen H5; M20 horizon20/purge20, WF504/126/126, PIT/labels/Purged/CPCV/independent holdout/Champion/Top3/NO_TRADE, original cost/tax/risk/promotion thresholds. Never reuse consumed H5 holdout/dynamic for independent approval. No official economic experiments until original-filing and KRX PIT admission independently signed. Offline-only isolated optimisation can verify SHA-bound fail-closed cache keys, serial dependency ordering, read-only postprocessing and synthetic parity without changing policy. Next read-only evidence: inspect failed chronology anchor job logs and source routing; independently reconcile 2026-09-28 OHLC against official session/corporate-action records; inspect crashed read-only replica failure evidence without restart. Do not modify other Work-owned branches, blocked workflows, live settings or staged patch.
