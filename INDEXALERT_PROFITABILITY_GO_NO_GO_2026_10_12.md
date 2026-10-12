# IndexAlert — Profitability Evidence Adjudication (2026-10-12 KST)

**Purpose:** close the *current-evidence* profitability decision before any further unrelated development. This is a NO-GO adjudication on available evidence, **not** an assertion that an unevaluated M20 strategy has negative returns. Do not loosen Frozen/H5, PIT, independent OOS/Holdout, costs/Net EV, Champion or promotion criteria.

## Executive decision (evidence as of this checkpoint)

| Strategy/path | Verifiable evidence | Decision |
|---|---|---|
| Existing Frozen H5 reference | Saved **developmental** 278-trade audit, with negative date-cluster lower bound and adverse best-five-day deletion | `DEVELOPMENTAL_NOT_PROMOTABLE`; do not represent positive mean as a real-world edge |
| Fixed preregistered M20 fundamental-drift Challenger | Two original Q3 filing archives for **one preselected issuer**, with date/context counts; no independently admitted cross-sectional historical PIT input/return panel | `NOT_EVALUABLE_NEW_EVIDENCE_REQUIRED`; **no numerical M20 return/PF/MDD/NetEV estimate** |
| Capital-capped Tiny Live | Neither strategy has independently admissible positive successor alpha; broker/status/execution blockers persist | `NO_GO`; `ORDERING=DISABLED`, all real-order/funds/permission flags false |

**No additional H5 backtest, alternative horizon/feature/threshold sweep, consumed v1 holdout read, or synthetic M20 performance run is authorized by this decision.**

## 1. H5 final verdict on saved developmental evidence

Evidence: [pre-existing immutable audit](INDEXALERT_H5_PROFITABILITY_AUDIT_2026_10_09.md), with archived workflow artifact SHA-256 and original programmatic recomputation stated there. No claim of a fresh independent OOS result.

- 278 development selections across 137 decision dates; last selected day **2021-03-17**.
- Mean per-trade post-cost return +1.15011265% and PF 1.54614261 are descriptive, not independent alpha.
- Date-equal-weighted 95% confidence interval **[-0.48897793%, +2.19283882%]** has a **negative** lower bound. This is a stored, date-resampling interval, not a newly established overlapping-hold-period dependence-aware bound.
- Delete the best five decision days: mean **-0.36245729%**, PF **0.83593211**.
- Original portfolio summary MDD **-24.3899%** (not rederived at this checkpoint).
- Recently available 504-session diagnostic covered **2024-08-20 to 2026-09-16**; it is not a current live profitability result. No selected H5 entries after 2021 in the cited final-selection CSV.

**H5 profitability/promotability condition is not satisfied.** Do not reframe trade-mean +1.15% as annual portfolio return or a bankable trade edge.

## 2. What official OpenDART source checks actually proved (M20)

The preregistered trial is `EXP-2026-10-08-M20-FUNDAMENTAL-DRIFT-01` ([unchanged preregistration](INDEXALERT_MEDIUM_SWING_M20_PREREG.json)):
- One fixed 20-KRX-session hold; Ridge alpha 1, NetEV_low > 0, 0–3 original Top3 with NO backfill; WF504/126/126; purge and embargo 20; full after-cost/tax/turnover/capacity/tail portfolio evidence mandatory.
- [Account taxonomy and fixed-issuer official source shape](https://github.com/kims34/openpilot-opkr/actions/runs/38194625753): official list/financial line shape verified; `pit_source_admitted=false`.
- [Historical Q3 receipt *dates*](https://github.com/kims34/openpilot-opkr/actions/runs/38195451379): 2024 Q3 first filing 2024-11-14; 2025 Q3 first filing 2025-11-14; **not verified intraday publication time**.
- [Original XBRL archive bytes](https://github.com/kims34/openpilot-opkr/actions/runs/38196614911): both first-filing official ZIPs retrieved and CRC/content digests checked; **not historical revision/availability admission**.
- [Quarter-context facts](https://github.com/kims34/openpilot-opkr/actions/runs/38197303913): July–September original operating-profit tag/context counts 9 (2024) and 10 (2025) for the one fixed issuer; **not 9/10 distinct comparable financial values** and no amounts persisted.

All four probed pipelines keep historical PIT/source/economic/performance/holdout/live authorization false. Their workflow status SUCCESS denotes *bounded source-shape test success*, not a validated candidate or profitability result.

## 3. Data-gate reasons M20 may NOT run its performance evaluation

1. No independently admitted **multi-year, full intended universe** M20 feature panel exists in the checked-in `research_results` (the directory contains only older price-reference summaries). The two verified Q3 reports cannot establish the frozen 504+126+126 session WF history/event sufficiency for a cross-sectional M20 strategy. This statement is specifically about the inspected repository/workflow evidence; it does not claim no private historical bytes exist anywhere.
2. No independently proven exact **original period-specific consolidated standalone-quarter values**, q-minus-4 comparability, original-document/revision lineage, historical issuer/security mapping or verified decision-time available-at timestamps for that panel. Later corrected/account data must never be backdated.
3. No independently admitted exact-session **KRX market capitalization, status/tradability, corporate-action-safe entry/exit paths and affected-position economics** across the intended historical panel. The saved 2026-09-28 27-symbol, nonpositive OHLC source remains `FAIL_CLOSED`. Research-only Top3 no-backfill quarantine **does not** admit the other 776 rows.
4. The [KRX permission reply evidence](INDEXALERT_KRX_PERMISSION_REPLY_EVIDENCE.json) records full-history/personal-research collection permission **as a user-attested KRX-domain email**, with independent issuer verification still false; the project's **bulk_historical_network_execution_authorized_by_user=false** and full source provenance/coverage audits remain unadmitted. Do not use a restricted Data Marketplace web session, bulk historical network route or bypass the consent/gates based on the existence of an OPEN API key.
5. No independently admitted M20 net portfolio-return path, post-cost capacity/execution, untouched successor holdout, or predeclared incremental B-minus-A block-bootstrap confidence evidence exists. It is invalid to fill missing observations with zero or infer positions exited at an OHLC that is not a verified fill.

**M20 verdict: `NOT_EVALUABLE_NEW_EVIDENCE_REQUIRED`**. Not FAIL based on poor numerical performance; not PASS; no rescue tuning. Do not fabricate a percentage, CAGR, MDD, PF or probability of success.

## 4. Single next sequence for a meaningful numerical M20 trial

This is a dependency chain, **not** an endorsement of unsourced acquisition or a promise to run later:

1. Obtain independently authenticated official multi-year **original-filing** historical report series/point-in-time universe, actual standalone Q and Q-4 values, version/available-at lineage, and stable corporate security mapping under permission/collection contract.
2. Independently admit matching date-level KRX market capitalization, source and trading-status coverage, corporate actions, exact affected-position economic treatment and return paths. Reconcile/exclude invalid proposed new entries prospectively **without retrospective candidate/holding deletion or rank-4 backfill**.
3. Independently inspect/pin source receipts, dates, counts, hashes and coverage before any outcome is revealed. If enough independently admitted dates/events do not exist, report `NEW_EVIDENCE_REQUIRED` rather than relaxing 504/126/126 or embargo20.
4. Run **once** the pre-registered M20 developmental WF, explicitly net of dated taxes/fees/spread/impact with full NO_TRADE daily cash path and capital occupancy. Report mean, date-cluster 95% LCB, PF, CAGR, MDD, daily/trade ES95/99, underwater duration, 2x cost, best 1/3/5 dates, concentration and capacity. Compare on common date-wise portfolio paths against unchanged H5. B-minus-A moving-block-bootstrap 95% LCB must exceed zero; robust absolute M20 and nonworsening tail gates also required.
5. Even a positive developmental result is **only ADOPT CANDIDATE**; further independent untouched OOS/holdout, prospective Shadow/Fresh Confirmation, execution and explicit live consent remain separate.

## 5. Security and scope

- No new KRX network acquisition, unauthorized scraping, historical bulk run, new data purchase, broker order or credential/permission change was executed in this adjudication.
- No Railway operating configuration changed; `ORDERING=false/DISABLED`, real orders, money movement and permission-change gates remain false.
- This is a **decision on available evidence**. New independent source evidence may permit a *new* predeclared developmental assessment, but it must not reverse an H5 failed test or represent a missing M20 score as passed.

**Current portfolio-level answer: there is no independently validated deployable profit-making IndexAlert strategy. Tiny Live should remain blocked.**
