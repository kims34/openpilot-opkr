# IndexAlert independent profitability and offline runtime audit — 2026-11-05 00:24 KST

Scope: read-only GitHub/Railway audit; no economic backtest, market-data performance experiment, trading, deployment, merges, or workflow edits. This is an evidence ledger, not approval.

## Verified current GitHub refs (GitHub REST, checked this run)
- research `index-alert-research-v1`: `df474df348f22aa38b1dedaa59fcff66e548b406`
- development `index-alert-position-regen-fix-v1`: `1e6367d2863a86c3470da13d81a955d277eba485`
- independent audit branch before this write: `39d40284269c8466874a0c3561724c2e40c8e89f`
- Draft OPEN PR #412 `bf3d9514a87c53b1775e22ec9ba7711f6cecc49f`; #413 `f003ef6247e16fcc71bd3b1b20cd4904c4d984c0`; #414 `18c5418d9684d1717df58261ea27f28e514385b2`; #418 `2f98401cc50a6c6a25808a98516efd5bf0c944ee`; KRX #420 `fab3cbbd63a951a4e081f9e7f08c1391ca308581`, #422 `c14857620973531013799e44625d43080904fd5f`, #423 `0e38004363cac9fc4475556b3a1c445de9af407f`.
- PR #414 gate `docs/INDEXALERT_PROFITABILITY_INTEGRATION_GATE_2026-10-13.md` blob SHA-1 `984c933651f39f1ee9e26a1d7ac3893aaa5335be`.

## Actions independently read this run
- #38381997417 6/6 SUCCESS; #38382214223 6/6 SUCCESS; #38419111311 6/6 SUCCESS.
- #38419649711 1/1 SUCCESS (one-runner-offline-comparison).
- OpenDART #38419439742 2/2 SUCCESS (candidate row diff and security tests).
- Chronology #41515392296 auto-anchor FAILURE; validation SKIPPED.
- Previously reported 34-case SHA-256 `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34`, 13 adversarial mocks, 28 synthetic tests, serial 2.9656s versus concurrent 2.6209s (1.1315x regression phase) are historical assertions **not independently rehashed/rebenchmarked this run**. Entire CI acceleration and official backtest speed NOT VERIFIED.

## Railway deployment and fresh log evidence (UTC 2026-11-04 14:00–15:30)
- Project IndexAlert `d1c1a050-b7d6-41ce-b300-13c20f82a20a`, production `83d5840b-270e-4d3f-a941-a37fd4a55ff7`.
- PIT rebuild deployment `8b354fc1-cfb2-4ef0-863e-67f7f5dda2b5` SUCCESS 2026-10-10, commit `e57054ecdb3e734ced3c9a981b887d9b5fc60f97`. Four observed runtime log records in window; 2026-11-04 14:16:42Z shows `COMMON_OHLC_NONPOSITIVE`, `FAIL_CLOSED`, 803 common-stock rows, 27 nonpositive OHLC, 27 zero volume/value, source failure session 2026-09-28, independent source/model/chronology admissions false, session_manifest_sha256 null, ordering DISABLED, no orders or funds movement authorised.
- KRX historical worker deployment `16c93d7c-7cd0-4d84-a327-298d2805376c` SUCCESS 2026-10-12, commit `1e6367d2863a86c3470da13d81a955d277eba485`. Zero log entries in this window: not evidence of official trading calendar or execution validation.
- IndexAlert runtime deployment `eaaa9f67-b9f2-41d2-832c-7d6fad9b9b00` SUCCESS 2026-10-05, commit `8a68b01bca5d551d083ccda263df38d86fa54166`. Market quote/fallback logs through 15:23Z, not PIT approval.

## Independent gate disposition
- KRX 2017–2022 private source 1565/1565 weekday raw-pair integrity: historical PASS only; official calendar, trading status, corporate actions, security history, executable fills, taxes/costs: NOT VERIFIED / FAIL-CLOSED.
- OpenDART original-filing 2021/2022 initial 3-month consolidated operating profit period, amendment lineage and public available-at: NOT VERIFIED / FAIL-CLOSED; 15 candidate SGML rows do not prove semantic period/time.
- Historical corporation-to-security mapping: NOT VERIFIED.
- M20 PIT and economic run: NOT AUTHORISED; after-tax NetEV/PF/CAGR/MDD/ES95/ES99/concentration/regime robustness: NOT EVALUABLE / NO-GO.
- Offline synthetic regression CI: limited PASS; full official backtest acceleration NOT VERIFIED.
- Frozen H5; M20 horizon20/purge20, WF504/126/126, PIT/label/Purged/CPCV/independent Holdout/Champion/Top3/NO_TRADE and costs/taxes/risk/advancement gates unchanged. Consumed H5 holdout and dynamic output cannot be retuned or reused as independent.
- Cache only on complete approved source/data/code/Frozen/runtime/evidence SHA-256 equality (fail-closed). Parallelism only for independent read-only post-processing; no dependent retraining or capital transition parallelism. ORDERING=false.

Next permitted work: independent original-filing timestamp and financial period lineage evidence; independent official KRX market-status/corporate-action/security mapping evidence; offline-only cache invalidation and serial/parity policy tests. Do not run M20, alter protected workflows, deploy, merge PRs or trade.
