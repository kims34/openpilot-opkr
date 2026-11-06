# IndexAlert independent profitability and offline runtime audit — 2026-11-07 02:22 KST

Scope: read-only verification; no model search, market backtest, deploy, merge, order, account/permission change or champion promotion. Evidence here is not PIT approval.

## Verified repository references
Research branch index-alert-research-v1 and development branch index-alert-position-regen-fix-v1 found by branch search; exact HEAD SHA NOT VERIFIED.
Draft OPEN unmerged PR HEADs:
- #412 OpenDART bf3d9514a87c53b1775e22ec9ba7711f6cecc49f
- #413 offline optimisation f003ef6247e16fcc71bd3b1b20cd4904c4d984c0
- #414 integration 18c5418d9684d1717df58261ea27f28e514385b2
- #418 single runner 2f98401cc50a6c6a25808a98516efd5bf0c944ee
- #420 KRX fab3cbbd63a951a4e081f9e7f08c1391ca308581
- #422 KRX c14857620973531013799e44625d43080904fd5f
- #423 KRX 0e38004363cac9fc4475556b3a1c445de9af407f
Integration document docs/INDEXALERT_PROFITABILITY_INTEGRATION_GATE_2026-10-13.md blob SHA 984c933651f39f1ee9e26a1d7ac3893aaa5335be at #414 head branch.

Actions jobs independently rechecked: 38381997417 6/6 PASS; 38382214223 6/6 PASS; 38419111311 6/6 PASS; 38419649711 1/1 PASS; OpenDART 38419439742 2/2 PASS; Chronology Anchor 41515392296 auto-anchor FAIL, validation SKIPPED. Historical 34-case hash 5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34 and 1.1315x regression-phase timing are historical claims, not rederived in this run. End-to-end CI and official backtest speed NOT VERIFIED.

## Railway read-only
Project d1c1a050-b7d6-41ce-b300-13c20f82a20a, production environment 83d5840b-270e-4d3f-a941-a37fd4a55ff7.
PIT rebuild deployment 8b354fc1-cfb2-4ef0-863e-67f7f5dda2b5 SUCCESS, replica 1/1. Latest fetched logs through 2026-11-06 14:46:56Z (23:46:56 KST) show session 2026-11-06 source_failure_session 2026-09-28, 803 common stock rows, 27 nonpositive OHLC and 27 zero-volume/value rows, error COMMON_OHLC_NONPOSITIVE, session_manifest_sha256=null, FAIL_CLOSED; ordering DISABLED; all fresh-alpha/order/funds permissions false. Data quality FAIL, fail-closed guard PASS. No entries in queried later interval; resolution NOT VERIFIED.
KRX historical worker deployment 16c93d7c-7cd0-4d84-a327-298d2805376c SUCCESS but running 0/1; no logs in queried latest interval. Historic 1565/1565 weekday storage integrity is not official calendar/session/executability approval.
Runtime deployment eaaa9f67-b9f2-41d2-832c-7d6fad9b9b00 SUCCESS running 1/1. Backend, push and db-query-readonly offline; db-query-readonly critical=1. Kiwoom real readonly display online but replica running 0/crashed 1. Staged pending patch e113dacb-6705-4416-9997-dc694539d382 persists, untouched.

## Gates
PASS: historical offline CI jobs; live fail-closed order prevention.
FAIL: prospective OHLC source quality; chronology anchor job.
NOT VERIFIED: official original-filing public available-at/PIT; 2021/2022 first three-month consolidated operating-profit period/correction lineage; historical issuer/security mapping; official KRX sessions, corporate actions, executability, fees/tax; NetEV/PF/CAGR/MDD/ES95/ES99/concentration/temporal robustness; actual full-backtest acceleration; independently reproducible current research/development HEAD.
M20 economic run NO-GO. H5 consumed holdout and Dynamic results may not be retuned or reused as independent. Frozen H5/M20 horizon20 purge20, WF504/126/126, CPCV, holdout, champion/top3/NO_TRADE and all cost/risk/promotion gates unchanged. Cache fail-closed on independent source/data/code/Frozen/runtime/evidence SHA-256; only independent read-only postprocessing may parallelise.

Next: isolate original official KRX 2026-09-28 27-row OHLC/source lineage and chronology-anchor failure without changing live source or policy; resolve official DART original-filing public-time and KRX calendar/mapping lineage independently. No new performance experiments until PIT approval.
