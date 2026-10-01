# IndexAlert Master Spec — Current Research Authority

Updated: 2026-10-02 KST
Branch: `index-alert-research-v1`

This document supersedes earlier research notes when they conflict with the architecture below.

## 1. Objective

Select **0 to 3 short-term candidates** only when the conservative, executable, cost-adjusted economic edge remains positive after uncertainty, execution and tail-risk controls.

The system is not a forced Top-3 stock picker and is not optimized primarily for raw hit rate, Precision@3, or an UP/DOWN label.

Long-term product objective: after the Alpha/selection engine has passed the required external statistical and prospective validation gates, IndexAlert may progress to broker-assisted automated execution. Broker automation is downstream of research validation and must never be used to justify weaker Alpha evidence.

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

Future broker execution is a downstream, separately gated layer:

`Broker-neutral decision intent`
→ `Pre-trade Health Gate`
→ `Broker Adapter`
→ `Order state machine`
→ `Broker-authoritative reconciliation`
→ `Execution/PnL evidence ledger`

The prediction/decision engine must not contain Kiwoom- or broker-specific order logic.

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
- trading-policy Shadow S1
- frozen Fresh Confirmation S2

`Shadow S1` here means the staged automated-trading prospective decision mode defined below: it submits **no broker orders** and creates no broker-fill evidence. It is distinct from the legacy probability-model challenger ledger in `probability_shadow.py` / `SHADOW_LEDGER_RELEASE.md`.

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
  Holdout is one-shot and cannot tune the same model. Prospective trading-policy
  Shadow S1 and frozen Fresh Confirmation S2 remain mandatory after holdout.

## 14. Future broker automation and Kiwoom REST boundary — 2026-09-30

### Priority

- Current KOSPI Alpha/prediction/selection research and statistical validation remain first priority.
- Broker automation must not delay or restructure current research/backtest/validation solely for connectivity.
- At the present stage, maintain only broker-neutral interface/data compatibility. **Real-account order submission remains disabled.**

### Promotion sequence

The required execution promotion sequence is:

`Research / Backtest -> Shadow -> Kiwoom Paper API -> Tiny Live -> Limited Live -> Production`

No stage may be skipped merely because broker connectivity works.

The evidence semantics of these stages are frozen:
- **SHADOW:** records prospective broker-neutral decisions/intended actions only. It submits no broker order and cannot produce empirical fill, partial-fill, slippage or capacity evidence.
- **PAPER:** sends orders only to an approved paper/simulation broker environment. Its returned order/fill state is operational adapter/reconciliation evidence, not evidence of real-market fill quality or capacity.
- **TINY_LIVE / LIMITED_LIVE / LIVE:** real-account broker execution observations are the only tier eligible to contribute to empirical live fill/slippage/partial-fill/latency/markout/capacity evidence. Structurally valid live rows alone do not satisfy promotion; sample sufficiency, tails, capacity and all statistical/prospective gates remain separate.
- The older probability-model `shadow` ledger is a different concept and must never be counted as trading-policy Shadow S1 or execution evidence.

Canonical execution-evidence details are frozen in `INDEXALERT_EXECUTION_EVIDENCE_CONTRACT.md`.

### Separation of concerns

- Core prediction and decision engines emit broker-neutral decisions such as `BUY`, `HOLD`, `EXIT`, `REPLACE`, `NO_TRADE`.
- Broker-specific authentication, account, order, amend/cancel and execution logic belongs behind a separate `BrokerAdapter` interface.
- Kiwoom Securities REST is one future adapter implementation; broker-specific code must not be embedded in the Alpha/model layer so additional brokers can be added later.
- The detailed future execution boundary is defined in `INDEXALERT_BROKER_EXECUTION_CONTRACT.md`.

### Order safety and reconciliation

Future automated execution must manage the complete lifecycle rather than simply send an order:

`decision -> pre-trade gate -> submit -> acknowledgement -> partial/full/unfilled/rejected -> amend/cancel -> broker balance/position query -> reconciliation -> realised execution/PnL record`.

Mandatory design constraints include:
- idempotency / duplicate-order prevention;
- cancel/fill and amend/fill race handling;
- explicit remaining quantity after partial fills;
- timeout/unknown-result recovery by querying broker state before retry;
- reconnect and resynchronisation;
- market holiday, VI, halt and price-limit handling;
- orderable cash and actual holdings checks;
- fees, tax, slippage and rate-limit handling;
- fail-closed behavior on stale data, API failure or unresolved reconciliation.

When internal state and the real broker/account disagree, the broker state is authoritative and new automatic orders are blocked until reconciliation succeeds.

### Modes and independent controls

Execution must have explicit deny-by-default modes:

`MASTER_OFF`, `SHADOW`, `PAPER`, `TINY_LIVE`, `LIMITED_LIVE`, `LIVE`.

The system must never create a real order unless the user has explicitly activated a live-capable mode and all promotion/safety gates pass.

Independent safety controls must include at least:
- daily maximum loss;
- per-symbol maximum value;
- total invested/gross-exposure cap;
- simultaneous-position cap;
- per-order maximum value;
- abnormal repeat-order breaker;
- Kill Switch / emergency global automation stop.

### Immediate pre-trade Health Gate

A model `BUY` never directly authorizes an order. Immediately before any future executable order, revalidate:
- system/broker health;
- prediction freshness;
- current executable NetEV;
- liquidity/capacity;
- account and market tradability;
- applicable risk limits and orderable amount;
- holdings/open-order/reconciliation state.

Any failed required check produces no order.

### Secrets and Kiwoom implementation gate

API keys, secrets, account authentication material and tokens must not be committed to code/GitHub or stored in logs/DB plaintext. Use deployment-appropriate secret management and redacted logging.

When Kiwoom REST implementation actually begins, the team must first re-check the **then-current official Kiwoom Securities REST API documentation** for endpoints, authentication/token behavior, production/paper environments, order/amend/cancel schemas, order/execution status behavior, documented rate limits and error semantics. Do not implement from remembered or stale API specifications.

### Current disposition

Do not implement or activate real Kiwoom ordering while the Alpha engine remains below its statistical/external-validation gates. Continue current research blockers and prospective execution-evidence work first; broker integration starts only when the defined promotion stage is reached.

## 15. Frozen automated-operation UX contract — 2026-09-30

The final default automated-trading UX must minimize user configuration. After connecting an eligible broker account, the routine user-facing controls are limited to:

- automated operation enabled / disabled; and
- `max_automation_capital_krw`.

`max_automation_capital_krw` is a **hard upper bound, never an investment target**. The engine may deploy any amount from 0 KRW up to that ceiling. If no opportunity passes conservative executable NetEV, uncertainty, tail-risk, liquidity, capacity, tradability and execution gates, the correct result is `NO_TRADE` and cash remains uninvested.

Users must not be required to configure stop-loss %, take-profit %, number of holdings, per-symbol weights, entry thresholds, holding periods, replacement rules or re-entry rules. Those are owned by the validated Decision / Risk / Execution Engine. Internal risk controls may be stricter than the user's maximum and remain mandatory without becoming routine consumer UX knobs.

The user retains final authority to connect/disconnect the broker, enable/disable automation, use the Kill Switch and set/lower/increase the maximum capital ceiling. Increasing the ceiling never relaxes admission/risk standards and never forces immediate investment.

Future pre-trade capital accounting must conservatively include automated positions, reserved open buy orders, partial-fill residuals, uncertain submissions and applicable fee/tax buffers such that:

`projected_committed_automation_capital_krw <= max_automation_capital_krw`

Pre-existing/manual holdings are outside automated control unless a separately explicit future contract opts them in. Full product/control details are frozen in `INDEXALERT_AUTOMATION_UX_CONTRACT.md`; broker/order lifecycle details remain in `INDEXALERT_BROKER_EXECUTION_CONTRACT.md`.

## 16. Frozen KRX source gates A-F — 2026-10-01

Before a KRX source family may be treated as source-ready for its declared scope, it must satisfy all six source-governance gates below. Canonical detailed semantics are in `INDEXALERT_KRX_SOURCE_ACCESS_CONTRACT.md`; the current evidence state is in `INDEXALERT_KRX_SOURCE_GATE_AUDIT.md`; executable audit semantics are in `research_v1_krx_source_gates.py`.

- **Gate A — `AUTHORIZED_OFFICIAL_ROUTE`**: exact official route/product and appropriate authorization; OpenAPI, Data Marketplace web-session and purchased/distributed routes are not interchangeable.
- **Gate B — `EXACT_DATASET_SCHEMA_MAPPING`**: exact service/screen/feed and required schema/fields must be verified; similar names or provisional transports do not pass.
- **Gate C — `HISTORICAL_COVERAGE_SECURITY_MAPPING`**: required historical period and relevant securities must be covered with stable security mapping/common-stock identity where required.
- **Gate D — `PIT_AVAILABILITY_LINEAGE`**: event/publication/availability/ingestion lineage must be explicit and no observation may be used before official availability.
- **Gate E — `REPRODUCIBLE_INTEGRITY_FAIL_CLOSED`**: acquisition and source metadata must be reproducible/auditable; ambiguity, undocumented proxies and synthetic source substitution fail closed.
- **Gate F — `INTENDED_USE_RIGHTS`**: permitted use must be verified for the declared scope; internal research and external/commercial product use are separate scopes.

Each gate is `PASS`, `PARTIAL` or `BLOCKED`; only `PASS` closes it. `PARTIAL` is never treated as a pass. Any non-PASS gate keeps that source contract open for the declared scope.

Even six PASS results are **source-governance evidence only**. They do not by themselves authorize model/Final-Judge promotion, sealed-holdout consumption, Shadow/Paper/Tiny-Live progression or live trading. All existing PIT/time consistency, anchored Walk-Forward, Purged/CPCV, realistic transaction/execution cost and fill modeling, distributional NetEV, tail/recency/capacity, one-shot holdout, Shadow S1 and Fresh Confirmation S2 requirements remain unchanged and independent.

## 17. Frozen empirical execution-sufficiency protocol — 2026-10-01

The project execution-sufficiency criteria are frozen before any genuine LIVE observation in `INDEXALERT_EXECUTION_SUFFICIENCY_PROTOCOL.md` and the SHA-256-bound machine-readable `INDEXALERT_EXECUTION_SUFFICIENCY_PROTOCOL.json`. `research_v1_execution_sufficiency_assessment.py` is the independent evaluator. Unit-test fixtures are code-path tests only and are never project evidence.

The frozen v1 evidence window requires at least:
- 600 genuine `PROSPECTIVE_LIVE_EXECUTION_LOG` observations;
- 200 distinct decision dates;
- 400 filled observations;
- decision-time PIT ADV participation no greater than the existing research assumption `0.0005` (0.05%);
- 120 observations at or above 80% of that participation ceiling;
- date-cluster fill-ratio/slippage/fee-tax uncertainty gates;
- Wilson upper bounds for no-fill and partial-fill rates;
- complete 5m/30m/close markouts with ES95/ES99 reporting;
- recommendation-TTL/order-expiry latency integrity;
- zero capacity breaches, unknown order outcomes, unresolved reconciliation rows and risk-limit-breach rows.

The evaluator is bound to frozen decision/execution policy IDs, exact protocol-document fingerprint and PIT provenance timestamps. Thresholds may not be weakened using outcomes from the evidence window they judge. A future revision requires a new protocol ID/fingerprint and an evidence window beginning strictly after that revision is frozen.

`research_v1_execution_sufficiency_assessment.py` is now explicitly the **numerical metric evaluator**. A caller-supplied CSV, the literal `PROSPECTIVE_LIVE_EXECUTION_LOG` source label, or a CSV SHA-256 does not prove genuine real-account provenance. The separate fail-closed provenance contract is `INDEXALERT_LIVE_EXECUTION_PROVENANCE_CONTRACT.md`. A numerical pass is reported as `execution_metric_gates_passed=true`, and the act of running the numerical evaluator is reported only as `execution_metric_sufficiency_assessed=true`. The project-level `empirical_execution_sufficiency_assessed`, `live_empirical_execution_evidence_ready` and `empirical_execution_blocker_closed` fields must remain false until the exact evidence bundle also passes independent broker-native provenance admission. This provenance hardening does not change or weaken any frozen v1 numerical threshold.

Even after both numerical sufficiency and genuine provenance are established, `promotion_ready=false`, `sealed_holdout_authorized=false` and `live_trading_authorized=false` remain required until every independent Master Spec gate passes. No sealed holdout may be opened merely because execution evidence passes, and no real-account order mode may be activated from this evidence alone.

Current project state: the protocol/metric evaluator are frozen and Actions-tested, but no genuine staged LIVE evidence window and no independent broker-native provenance admission exist yet. Therefore empirical execution sufficiency remains unassessed/open and the execution blocker remains open. KRX A-F evidence, exact status-event economics, sealed holdout, Shadow S1 and Fresh Confirmation S2 remain independent blockers.

## 16. Kiwoom demo/read-only connectivity evidence — 2026-10-02

Canonical evidence: `INDEXALERT_KIWOOM_DEMO_CONNECTIVITY_EVIDENCE.md`.

A user-operated smoke test against the Kiwoom **mock/demo host only** completed `TOKEN_OK`, `ACCOUNT_OK`, `BALANCE_OK`, and `FILLS_OK`. This closes only the demo/read-only connectivity plumbing check. It does not establish real-account broker provenance, real-market execution quality, status-event economics, execution sufficiency, KRX source approval, promotion readiness, sealed-holdout authorization, or live-order authorization.

Accordingly `genuine_live_provenance_verified=false`, `empirical_execution_blocker_closed=false`, `sealed_holdout_authorized=false`, and `live_trading_authorized=false` remain unchanged. No order-create/amend/cancel or real-account endpoint is authorized by this evidence.

## 17. Continuous Research Governance — 2026-10-02

Canonical contract: `INDEXALERT_CONTINUOUS_RESEARCH_CONTRACT.md`. After a Core is frozen, continuous research runs in an isolated Research Lab. Trials must be preregistered and fingerprinted before outcomes; post-result protocol changes invalidate the trial; sealed holdout is forbidden for discovery/tuning; an accepted result is only `ACCEPTED_CHALLENGER` and has no production or live-order authority. Core replacement remains a separate versioned promotion requiring all applicable frozen external, execution, holdout, Shadow S1 and Fresh Confirmation S2 gates.

### Continuous-research successor promotion boundary — 2026-10-02

A preregistered research success does not directly overwrite Core. `research_v1_successor_core.py` may automatically stage a distinct versioned `SHADOW_CANDIDATE` only after the accepted challenger also passes the required independent OOS, cost-stress, tail-risk, recent-stability, PIT/no-leakage and frozen-protocol gates. Automatic Core/code update becomes eligible only after the separately governed sealed holdout, Shadow S1, Fresh Confirmation S2, external-source/status blockers and empirical execution blocker are all closed. Automatic real-account order activation remains forbidden even then; live-order authority is a separate gate.

### Internal completeness audit — 2026-10-02

Canonical audit: `INDEXALERT_INTERNAL_COMPLETENESS_AUDIT.md`. Internal review found and fixed a successor-promotion authority ambiguity: passing represented confirmation gates now yields only `automatic_code_update_eligible=true`; it can never self-grant `automatic_code_update_allowed` or `promotion_authority_verified`. No reviewed research, broker-normalization, automation-control or successor path authorizes real-account ordering or sealed-holdout access. External/evidence blockers remain unchanged.
