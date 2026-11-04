# IndexAlert independent profitability and isolated runtime audit — 2026-11-04 21:17 KST

Scope: read-only GitHub/Railway verification; no source admission, market replay, performance experiment, code/workflow change, deployment, merge, trading or permissions change. Separate workstreams must not edit each other's code.

## Exact refs checked live
- Research `index-alert-research-v1` HEAD `df474df348f22aa38b1dedaa59fcff66e548b406` (GitHub branch API).
- Development `index-alert-position-regen-fix-v1` HEAD `1e6367d2863a86c3470da13d81a955d277eba485` (GitHub branch API).
- Independent audit branch prior HEAD `3149c18e96bbfd9cf9793f1c6148d9e9eb12139f` before this note.
- All OPEN/DRAFT/unmerged: PR #412 `bf3d9514a87c53b1775e22ec9ba7711f6cecc49f`; #413 `f003ef6247e16fcc71bd3b1b20cd4904c4d984c0`; #414 `18c5418d9684d1717df58261ea27f28e514385b2`; #418 `2f98401cc50a6c6a25808a98516efd5bf0c944ee`; KRX #420 `fab3cbbd63a951a4e081f9e7f08c1391ca308581`; #422 `c14857620973531013799e44625d43080904fd5f`; #423 `0e38004363cac9fc4475556b3a1c445de9af407f`.
- PR #414 gate `docs/INDEXALERT_PROFITABILITY_INTEGRATION_GATE_2026-10-13.md` blob SHA-1 `984c933651f39f1ee9e26a1d7ac3893aaa5335be`, fetched directly at PR head.

## Actual Actions evidence checked live
- #38381997417 6/6 SUCCESS, head `55e7fe2b3fe322e39f817914ff1ed5b589bbe0da`; #38382214223 6/6 SUCCESS, head `05d73661bcc879fe0dd66ffcea5fe1f5ee6fbd56`.
- #38419111311 6/6 SUCCESS, head `b22e4f39517c2bc38e173e63e8fd52f29a535dad`; #38419649711 1/1 SUCCESS, head `8f363b8683d34a48754916b34810a5a8bb958896`.
- OpenDART #38419439742 2/2 SUCCESS, head `39af5b0043e122bc0e42935d8813759ff6c1a6e7`; chronology #41515392296 auto-anchor FAILURE, validation SKIPPED, head `f17283d9a5f0427c3d5b8a865d39455f92ee2f1d`.
- Prior fixed 34-case SHA-256 `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34`, 13 adversarial mocks, additional 28 synthetic cases and serial 2.9656 s vs concurrent 2.6209 s (=1.1315x regression-phase) are **prior attestations, not independently rehashed/rebenchmarked in this run**. Offline CI conclusions PASS; actual end-to-end backtest speed NOT VERIFIED.

## Railway live read-only evidence
- IndexAlert project `d1c1a050-b7d6-41ce-b300-13c20f82a20a`, production `83d5840b-270e-4d3f-a941-a37fd4a55ff7`.
- KRX worker deployment `16c93d7c-7cd0-4d84-a327-298d2805376c` SUCCESS (2026-10-12), commit `1e6367d2863a86c3470da13d81a955d277eba485`; 2026-11-04 20:00–21:20 KST deploy logs 0; absence not validation.
- PIT rebuild deploy logs 2026-11-04 20:01, 20:16, 20:31, 20:46, 21:01, 21:16 KST: `COMMON_OHLC_NONPOSITIVE`, `FAIL_CLOSED`; 803 common stock rows, 27 nonpositive OHLC, 27 zero-volume/value; source failure session 2026-09-28; independent source/model/chronology verified=false; session manifest SHA null; ordering DISABLED; live orders=false; rejected source receipt saved. No new approved source.
- Separate runtime deployment `eaaa9f67-b9f2-41d2-832c-7d6fad9b9b00` SUCCESS (2026-10-05), latest observed logs through 21:17 KST include market quotes and USD/KRW Investing HTTP failure/Yahoo fallback, not official KRX/DART PIT evidence.

## Admission matrix (strict evidence scope)
- Historical private KRX 2017–2022 1565/1565 weekday raw-pair SHA storage: PASS *prior evidence*, not current independent rehash. Official calendar/90 uncertain days, 12003 zero-activity observations, corporate actions, historical listing/trading state, executable fills, costs/taxes: NOT VERIFIED / FAIL-CLOSED.
- OpenDART original/amended SGML 15 operating-profit candidate rows with numeric-adjacency signature: extraction-only PASS *prior evidence*. 2021/2022 original-filing consolidated first-three-month operating-profit semantics, amendments, precise public available-at, corp/security point-in-time mapping: NOT VERIFIED / FAIL-CLOSED.
- H5 archived failed/consumed holdout: NO-GO, no independent reuse; Dynamic post-hoc tuning prohibited. M20 horizon20/purge20, WF504/126/126 and Frozen H5 policies unchanged.
- NetEV/PF/CAGR/MDD/ES95/99, concentration, temporal robustness, after-cost/tax annual risk-adjusted net profitability: NOT EVALUABLE, no authorized official PIT performance run. NO_TRADE and ORDERING=false.
- Optimization #413/#418: historical synthetic offline CI PASS limited to software safety/parity. Cache must fail closed unless approved original/data/code/Frozen/runtime/approval evidence SHA-256 all match; only independent read-only postprocessing parallel. Dependent retraining/capital transition remain serial.

## Safe next steps
1. DART owner independently proves original-filing period, amendment lineage and public available-at for both years; do not backfill from corrections.
2. KRX owner resolves exact private source vs official calendar/90-day status, 27 bad OHLC, 12003 zero-activity and execution/corporate-action mapping with independent SHA; no arbitrary filtering to pass.
3. Independently verify source/code/Frozen/runtime evidence hashes and safe synthetic cache rejection/parity, without market performance replay.
4. Maintain blocked M20/H5 admission and separate explicit approvals for any order, funds, permission or Champion promotion. No merges/deployments.
