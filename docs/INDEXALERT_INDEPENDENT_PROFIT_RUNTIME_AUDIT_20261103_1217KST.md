# IndexAlert independent profitability / isolated runtime audit — 2026-11-03 12:17 KST

Read-only evidence snapshot; NOT a PIT admission, backtest, trading authorization, or deployment approval.

## Exact refs checked
- research `index-alert-research-v1`: `bba25477b41fcd0a8beca78168abb0009fb5b82c` (changed from prior audit's `3b8b7830612a6284d7c7a60628cb527cb741627a`; latest commit touches `docs/independent-audit/2026-11-03-1045-kst-readonly-audit.md` only).
- development `index-alert-position-regen-fix-v1`: `1e6367d2863a86c3470da13d81a955d277eba485`.
- Draft PR #412 `bf3d9514a87c53b1775e22ec9ba7711f6cecc49f`; #413 `f003ef6247e16fcc71bd3b1b20cd4904c4d984c0`; #414 `18c5418d9684d1717df58261ea27f28e514385b2`; #418 `2f98401cc50a6c6a25808a98516efd5bf0c944ee`; KRX #420 `fab3cbbd63a951a4e081f9e7f08c1391ca308581`, #422 `c14857620973531013799e44625d43080904fd5f`, #423 `0e38004363cac9fc4475556b3a1c445de9af407f`. All fetched as open Draft.
- PR #414 integration gate document blob SHA-1 `984c933651f39f1ee9e26a1d7ac3893aaa5335be`.
- GitHub Actions #38419111311 6/6 jobs success; #38419649711 1/1 success; chronology #41515392296 auto-anchor failure and validation skipped (latest job status queried).
- Historical synthetic parity fixed 34-case SHA-256 `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34` is **prior reported evidence**, not independently recalculated in this run.

## Railway production read-only evidence
- Project `d1c1a050-b7d6-41ce-b300-13c20f82a20a`, production environment `83d5840b-270e-4d3f-a941-a37fd4a55ff7`.
- KRX historical worker deployment `16c93d7c-7cd0-4d84-a327-298d2805376c` SUCCESS, pinned dev commit `1e6367d...`; prior 1565/1565 weekday pairs original-storage integrity PASS only.
- Prospective PIT service `225f2279-d728-4e1a-a3f3-2447ff0f9dc1` returned source session `2026-09-28` `COMMON_OHLC_NONPOSITIVE`, 27/803 common-stock nonpositive OHLC, `session_manifest_sha256=null`, `FAIL_CLOSED`, `ORDERING=DISABLED`, source/model/chronology admission false, live order false. Observed in 2026-11-02 runtime log; no newer successful PIT admission proven.
- Latest listed readonly Kiwoom deployment `a77fb922-b679-4d88-92c4-03054ec579cd` SUCCESS, 2026-10-29, commit `85bb6fd10bcc9ff2b14abe1c774f0d99f8eb84ab`. Deployment SUCCESS alone is not replica health or trading authorization.
- Chronology anchor #41515392296 failed; endpoint response body/private anchor receipt NOT VERIFIED.

## Gate decisions
| Gate | Decision |
| --- | --- |
| Original-filing SGML 15 candidate signatures | limited prior shape evidence only; exact 2021/2022 consolidated first-three-month operating income and correction lineage NOT VERIFIED |
| Exact public available-at, historical corp/security mapping | NOT VERIFIED |
| KRX private original pair storage | prior PASS for storage integrity only |
| Official trading calendar, state, actions, executions and costs/taxes | NOT VERIFIED |
| Synthetic #413 regression parity | limited prior PASS; official end-to-end speed NOT VERIFIED |
| #418 archived manifest SHA mismatch | FAIL-CLOSED pending independent evidence |
| NetEV/PF/CAGR/MDD/ES95/99, concentration, temporal robustness after tax | NOT EVALUABLE; no authorized M20 PIT/performance RUN |
| Trading / Champion promotion | NO-GO |

## Boundaries and next evidence
Keep Frozen H5, M20 horizon20/purge20, WF504/126/126, independent holdout, Top3/NO_TRADE, fees/taxes and risk thresholds unchanged. Never reuse consumed H5 holdout or tune against Dynamic. Only synthetic offline tests until independent original-filing public-time lineage and KRX market-state/tradability evidence SHA are approved. Cache only with exact approved source/data/code/Frozen/runtime/evidence SHA-256; parallelize only independent read-only postprocessing. No training/capital transition parallelism. Preserve `ORDERING=false`; no merge/deploy/order/fund/credential/Champion changes.

Next: compare new research documentation against existing audit to avoid duplicated modifications; obtain original SGML exact period/available-at evidence and official KRX calendar/trading-status evidence through their owners; independently inspect archived manifest SHA failure and verify full CI wall time, without running official returns or M20 economics. No other team code touched.
