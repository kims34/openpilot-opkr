# IndexAlert Master Spec — Current Research Authority

Updated: 2026-09-29 KST
Branch: `index-alert-research-v1`

This document supersedes earlier research notes when they conflict with the architecture below.

## 1. Objective

Select **0 to 3 short-term candidates** only when the conservative, executable, cost-adjusted economic edge remains positive after uncertainty, execution and tail-risk controls.

The system is not a forced Top-3 stock picker and is not optimized primarily for raw hit rate, Precision@3, or an UP/DOWN label.

## 2. Current Core architecture

`Point-in-time universe / corporate events`
→ `Unified availability-time contract`
→ `Data quality / freshness fail-closed`
→ `Systemic + liquidity stress state`
→ `Market / sector / peer residual alpha context`
→ `Executable return distribution / competing event timing`
→ `Purged OOF calibration and selection-conditional uncertainty`
→ `Rank stability / recommendation inertia`
→ `Gap / VI / price-limit / halt feasibility`
→ `Execution policy`
→ `Fill ratio × fill time × fill price`
→ `Post-fill markout / adverse selection`
→ `Fallback / impact / capacity`
→ `Distributional NetEV`
→ `Selective abstention / no-trade`
→ `Stay / exit / replace`
→ `Joint-tail / concentration risk`
→ **TRADE 0–3 / WATCH / REJECT**

## 3. Objective hierarchy

Primary research target:

1. **Executable cost-adjusted Net Return / NetEV distribution**
2. Downside/tail distribution and uncertainty
3. Calibration under selection
4. Coverage / abstention quality
5. Portfolio and execution robustness

Secondary diagnostics:

- rank quality
- target/stop timing
- hit rate
- Precision@1 / Precision@3

These diagnostics must not override negative executable NetEV.

## 4. Legacy / downgraded components

The following are retained only as baselines, diagnostics or auxiliary targets unless later evidence proves incremental OOS economic value:

- fixed `+4% target / -2.5% stop` barrier as the main learning target
- UP/DOWN-only classification
- forced Top-3
- Precision@3 as the main optimization target
- probability threshold without economic utility
- gross-return-only ranking

Barrier outcomes remain useful for path/risk diagnostics and for testing execution-policy sensitivity, but they are not the primary Core objective.

## 5. Current empirical findings that constrain further work

Latest purged PIT preliminary work on 2024-01-01 through 2026-09-28 shows:

- basic barrier-context model has negative post-cost edge
- removing statutory tax and commission does not rescue the signal
- optimistic same-bar target-first handling does not rescue the signal
- common-like security filtering helps only modestly
- post-entry missing-bar cases are too infrequent among selected trades to explain the main performance problem
- PIT-safe daily path features improve gross edge materially but remain negative after realistic costs
- fixed-horizon next-open→D+5 learning targets improve stability but remain negative after costs
- simply combining path features with fixed-horizon classification does not create synergy

Therefore the next Core work must focus on **executable return distribution, uncertainty-aware admission, recency/drift, feature-family marginal value and execution realism**, rather than adding arbitrary classifiers.

## 6. Distributional NetEV v0 migration

Until intraday fill data are available, the interim executable-return proxy is:

- decision at prior close
- entry at next executable regular-session open
- horizon return to D+5 close
- date-aware statutory tax
- commission allowance
- spread/impact allowance

This proxy is explicitly **preliminary**. It is closer to the Master Spec objective than the legacy fixed-barrier label, but it does not yet model fill ratio, fill delay, intraday markout, VI/limit queues or exact halt/delisting economics.

The research engine should estimate not only a point mean but a return distribution or conservative lower bound. Admission is allowed only when the conservative distributional NetEV remains positive.

## 7. Calibration / abstention requirements

Any admission threshold must be selected only from a purged calibration block or true OOF predictions.

No threshold may be chosen using the final test block.

A valid 0–3 admission policy must report together:

- coverage / trade days
- trade count
- mean executable Net Return
- Profit Factor
- date-cluster confidence interval
- MDD
- Expected Shortfall / tail loss
- cost sensitivity
- selected-vs-rejected counterfactual outcomes where observable

## 8. Feature research requirements

New features are evaluated at the **family** and **marginal economic value** level.

Required diagnostics:

- feature-family ablation
- marginal OOS NetEV contribution
- redundancy / error-correlation
- feature freshness / TTL
- missingness type
- regime stability
- turnover / execution-cost impact
- Remaining Alpha after market/sector/peer residualization

A feature is not retained because SHAP or in-sample importance is high.

## 9. Drift / recency

Expanding-history training is not automatically preferred.

The engine must compare a prespecified rolling recent-history challenger against expanding training when recent-year performance materially diverges.

Window length itself must not be exhaustively optimized. Any later change requires a separate research trial.

## 10. Risk overlays

Risk models may veto alpha but may not manufacture positive alpha.

Independent veto candidates include:

- systemic stress
- volatility / gap tail
- liquidity drought
- event mode
- data-quality failure
- execution infeasibility
- portfolio concentration / joint tail

A risk overlay is retained only if it improves tail metrics without merely collapsing coverage or destroying NetEV.

## 11. Research promotion

No candidate is promoted merely because it loses less than the current baseline.

At minimum, a preliminary positive candidate must demonstrate:

- positive cost-adjusted OOS mean Net Return
- PF > 1
- positive date-cluster lower confidence bound
- acceptable MDD and tail loss
- stable coverage
- no data-integrity or leakage blocker

Final Judge promotion additionally requires:

- validated common-stock security master
- exact halt / delisting economics
- longer historical evidence
- sealed holdout
- Shadow S1
- frozen Fresh Confirmation S2

## 12. Current immediate research order

1. **Distributional executable NetReturn / conservative NetEV challenger**
2. Purged OOF / calibration-based selective admission
3. Expanding vs one prespecified recent rolling-window drift test
4. Feature-family ablation / Remaining Alpha
5. Prespecified liquidity and volatility veto diagnostics
6. Exact security-master + halt/delisting layer
7. Intraday execution / fill / post-fill markout data
8. Full long-history Final Judge

Complex models are deferred until the above simple architecture produces robust positive OOS economics.

## 13. Sol statistical freeze addendum — 2026-09-29

### Horizon scope

- Short H5 remains the Core development engine.
- Swing is limited to H10. H20 is outside the requested 5--10-session scope and
  is archived as out-of-scope evidence. Do not sweep H6--H9 or retune H10 from
  the completed results.
- H10 is `REJECTED_CURRENT_CANDIDATE_DO_NOT_RETUNE`: its positive aggregate
  walk-forward result is confined to 2018--2021, has no recent admissions and
  loses a positive cluster LCB after removing the best five decision days.

### Anchored walk-forward

- Primary development evidence uses train 504 / calibration 126 / test 126.
- H5 and H10 share fold endpoints and common OOS decision dates. Purge and
  embargo equal the evaluated horizon.
- Purge removes observations with overlapping label intervals; embargo removes
  the next H sessions after protected calibration/test blocks.
- Calibration is disjoint and uses only outcomes available before each test
  prediction. Test outcomes never choose thresholds, quantiles, TopK or costs.

### Purged CPCV

- CPCV is a secondary stability diagnostic only, never forward OOS, sealed
  holdout evidence or a standalone promotion gate.
- Use six contiguous groups, every two-group test combination and each of the
  four remaining groups once as calibration; the other three groups train.
  This produces 60 split/calibration cases.
- Apply label-overlap purge and H-session embargo at all protected boundaries.
  Keep path identities and never pool repeated test rows as independent trades.
- Delete the provisional p25 NetEV/PF plus 80%-positive-LCB pass/fail rule.

### Short-versus-Swing dominance

- Compare daily portfolio NetReturn paths on the common OOS period, including
  cash/no-trade days as zero return under identical capital rules.
- Primary superiority requires the 95% lower bound of the paired H10-minus-H5
  mean daily NetReturn to exceed zero under a 10-session moving-block bootstrap.
- H10 must independently satisfy mean NetReturn > 0, PF > 1, date-cluster LCB >
  0, 2x-cost mean > 0 and PF > 1, plus positive mean/PF/LCB after removing the
  best five decision days.
- The latest 504 common OOS sessions must contain admissions and have a positive
  date-cluster LCB. H10 must not worsen portfolio MDD or daily ES95/ES99 versus
  H5. Precision@Selected remains secondary.

### Metrics, execution and holdout

- Precision@Selected is the positive cost-adjusted outcome rate among selected
  executable records. Report trade ES95/ES99 and daily-portfolio ES95/ES99.
- The current fixed-participation square-root-impact estimate is a cost proxy,
  not capacity-aware NetEV; reports must say so.
- Official security/status, exact halt/delisting economics, partial fills,
  fill-time/price, markout, latency/expiry and empirical capacity remain hard
  promotion blockers.
- Do not burn sealed holdout until blockers, code and protocol are frozen.
  Holdout is one-shot and cannot tune the same model. Prospective Shadow S1 and
  frozen Fresh Confirmation S2 remain mandatory after holdout.
