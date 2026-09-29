# IndexAlert Research Status

Updated: 2026-09-29 KST  
Branch: `index-alert-research-v1`  
Master authority: `INDEXALERT_MASTER_SPEC.md`  
Promotion authority: **none yet** — development evidence cannot promote a live strategy without sealed holdout + prospective Shadow.

## Current research principle

Use the Master Spec and prior research-room notes as references, not unquestionable truth. Current GitHub code, PIT lineage, CI artifacts and statistical/economic evidence take priority when they conflict with older notes.

Primary target is **executable, cost-adjusted 5-session NetReturn / NetEV distribution**. Legacy barrier and UP/DOWN models are diagnostics only.

Decision policy:

- conservative lower NetEV > 0
- freeze original decision-time Top3
- held/unfillable/vetoed names leave empty slots
- **no rank-4+ backfill**
- 0..3 trades and NO_TRADE are valid outputs
- five-session purge around train/calibration/test outcome boundaries
- date-aware KOSPI statutory tax + commission + spread/impact allowance
- normal-market fail-closed veto after Top3 freeze when decision-day KRX base-price return is outside +/-30% plus 50bp tolerance; blocked slots remain empty

## Major data-integrity correction: corporate-action-safe returns

All raw-close-based feature/label conclusions are now superseded.

Current CA-safe policy:

- `ret1` = KRX `FLUC_RT / ChangesRatio` base-price-adjusted daily return
- `ret5/ret20` and volatility = compounded CA-safe daily returns
- market breadth / market median / residual returns use the same CA-safe return axis
- fixed-horizon economic return starts from next executable open and compounds KRX base-price-adjusted returns through D+5 close
- research MTM uses a corporate-action-safe economic price index rather than raw share-count × close
- supervised cache is fingerprinted and fail-closed against stale pre-CA-safe caches

Synthetic split and cache-integrity tests are included in CI.

## Normal-market eligibility gate

KRX normal equities use a +/-30% daily price limit, while liquidation/cleanup trading is exempt. The research engine therefore treats decision-day absolute KRX base-price return >30.5% as a **non-standard market-state signal**, not an alpha threshold.

The gate:

- uses decision-time information only
- is applied after original Top3 is frozen
- never backfills rank 4/5
- remains preliminary until official KRX security-status/security-master data is joined

Historical audit confirmed that many vetoed observations had -67% to -98% one-day returns and correspond to non-standard states such as cleanup trading.

## CA-safe long-history robustness: completed

Period: **2015-06-15 .. 2026-09-23**  
Protocol: initial train 504 sessions, independent calibration 126, purge 5, OOS test 126, ADV20 rank >=20th percentile, strict Top3/no-backfill.  
This is a falsification/robustness test, **not a sealed holdout**.

### all_context without normal-market gate

- 115 trades / 51 trade days / 2.42% trade-day coverage
- mean net: **-6.50% / trade**
- PF: **0.370**
- cluster 95% interval: **-18.80% to -4.29%**
- ES95: **-71.0%**
- portfolio total return: **-71.5%**
- MDD: **-73.3%**

### context_only without normal-market gate

- 92 trades / 45 trade days / 2.14% coverage
- mean net: **-4.74% / trade**
- PF: **0.491**
- cluster 95% interval: **-19.00% to -3.09%**
- ES95: **-70.2%**
- portfolio total return: **-65.5%**
- MDD: **-71.1%**

Conclusion: the short-window positive result **does not survive long history without a market-status fail-closed layer**.

### context_only + normal-market fail-closed overlay

- 80 trades / 34 trade days / 1.62% coverage
- mean gross: **+0.731%**
- mean cost: **0.378%**
- mean net: **+0.353% / trade**
- PF: **1.082**
- cluster 95% interval: **-7.85% to +3.19%**
- 2x-cost mean: **-0.025%**, PF **0.994**

This removes obvious non-standard price-limit exceptions but **still does not establish robust edge**. 2026 includes a severe cleanup/delisting-related loss cluster and the confidence interval remains wide.

Long-history verdict: **LONG_HISTORY_DOES_NOT_YET_ESTABLISH_ROBUST_EDGE**.

## Selection-conditioned calibration: current strongest developmental direction

Diagnosed issue: marginal residual calibration severely underestimates winner's-curse/post-selection error for names selected near the top of the cross-section.

Developmental challenger keeps model, q25/q50/q75 levels, Top3 rule and test threshold fixed, but estimates calibration residual quantiles from **calibration-day Top3 by predicted mean only**. Test outcomes are not used to select calibration rows.

### all_context + selection-conditioned calibration + normal-market fail-closed

- 278 trades / 137 trade days
- trade-day coverage: **6.51%**
- mean net: **+1.150% / trade**
- PF: **1.546**
- win rate: **52.16%**
- ES95: **-20.64%**
- cluster 95% interval: **-0.489% to +2.193%**
- 2x-cost mean: **+0.787%**, PF **1.344**
- portfolio total return: **+16.39%**
- CAGR: **~1.83%**
- MDD: **-24.39%**
- Sharpe (0rf): **~0.23**
- average gross exposure: **~5.20%**

Important failure modes:

- admissions occur only in **2018-2021** in the completed long-history test
- **no admissions in 2022-2026**
- remove best 1 decision day: mean net **+0.694%**, PF **1.326**
- remove best 3 decision days: mean net **+0.053%**, PF **1.025**
- remove best 5 decision days: mean net **-0.362%**, PF **0.836**

Interpretation: this is not a current general-purpose Champion. It is a **developmental regime-specialist / dormant candidate** whose positive average depends materially on a handful of strong historical decision days. Overall cluster lower bound is still negative.

### context_only + selection-conditioned calibration

- 21 trades / 9 trade days
- mean net: **+6.92%**
- PF: **1.98**
- cluster 95% lower bound: **-5.66%**

This sample is far too small for promotion and remains research-only.

## Promotion-evidence audit

A separate no-tuning audit has been added to CI. It does not change model predictions or thresholds. It checks:

- overall date-cluster 95% lower bound
- remove-best 1/3/5 decision-day dependence
- latest 504 test-session evidence
- 2x cost stress
- tail loss / portfolio drawdown snapshot

Expected current classification for the strongest developmental candidate is **DEVELOPMENTAL_NOT_CURRENTLY_PROMOTABLE** because the cluster LCB is negative, the best-5-day removal fails, and recent-session admissions are absent.

## Recency challenger: rejected

Rolling-160 strict Top3 result:

- 85 trades
- mean net: **-1.583%**
- PF: **0.447**
- cluster 95% interval: **-4.18% to -0.15%**
- portfolio total return: **-17.64%**
- MDD: **-20.53%**

Decision: **KEEP_EXPANDING_REFERENCE**. Do not sweep/tune recency windows from this result.

## Historical tax schedule

Current PIT engine uses exact effective-date KOSPI statutory sell tax in the modern price-limit regime:

- 2015-06-15 .. 2019-06-02: **30bp**
- 2019-06-03 .. 2020-12-31: **25bp**
- 2021-2022: **23bp**
- 2023: **20bp**
- 2024: **18bp**
- 2025: **15bp**
- 2026: **20bp**

Round-trip broker commission remains separate at 3bp in current research.

## Current independent judgment

The current price/volume/context-only research stack is **not yet suitable for live short-term investment recommendations**.

What has improved:

- PIT discipline and leakage protection are materially stronger
- corporate-action distortion has been removed from features/labels/MTM
- post-selection calibration is now explicitly tested
- normal vs non-standard KRX market states are fail-closed
- strict Top3/no-backfill and abstention are enforced

What remains weak:

- no positive cluster lower bound
- no robust recent evidence
- extreme-day dependence remains material
- risk-adjusted portfolio performance is poor even for the strongest developmental candidate
- current data stack lacks official security status, investor flow, disclosure/event and richer sector/peer signals that may be needed for current edge

Do **not** relax q25, TopK, cost or recent-evidence standards just to create trades.

## Final Judge blockers still open

1. Official common-stock/security-status master; current PIT source alone does not conclusively classify all non-standard issues.
2. Exact cleanup-trading / halt / delisting economics and status joins rather than proxy inference.
3. Current-regime signal expansion using genuinely PIT-valid sources (flows, disclosures/events, sector/peer) without contaminating historical availability.
4. Intraday fill ratio × fill time × fill price and post-fill markout.
5. Recommendation latency/expiry and execution-delay stress.
6. Multiple-testing / research-ledger accounting across the full policy search.
7. Fresh sealed historical evidence followed by prospective Shadow S1 → frozen Fresh Confirmation S2.

## Promotion rule

No candidate is promoted because of a positive point estimate, PF or CAGR alone.

Preliminary evidence requires at least:

- positive cost-adjusted OOS mean Net Return
- PF > 1
- **positive date-cluster 95% lower bound**
- no material dependence on a handful of best decision days
- credible recent-regime evidence for a current general-purpose strategy
- acceptable MDD / ES / tail dependence
- reasonable cost-stress survival
- no hidden leakage, backfill, corporate-action, market-status or cache-lineage dependency

Final promotion additionally requires official security/status data, execution realism, sealed holdout and prospective Shadow.
