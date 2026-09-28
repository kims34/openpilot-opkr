# IndexAlert Research Status

Updated: 2026-09-29 KST  
Branch: `index-alert-research-v1`  
Master authority: `INDEXALERT_MASTER_SPEC.md`  
Promotion authority: **none yet** — all results remain PIT preliminary until Final Judge blockers and fresh prospective validation are removed.

## Current research principle

Use the Master Spec and prior research-room notes as references, not as unquestionable truth.  Current GitHub code, PIT lineage, CI artifacts and statistical/economic evidence take priority when they conflict with older notes.

The research center of gravity remains **executable cost-adjusted NetReturn / NetEV distribution**. Legacy barrier and UP/DOWN models are diagnostics only.

Decision policy is now fixed for current research:

- conservative NetEV lower bound > 0
- freeze original decision-time Top3
- held/unfillable/vetoed names leave empty slots
- **no rank-4+ backfill**
- 0..3 trades and NO_TRADE are valid outputs
- five-session purge around outcome/calibration boundaries
- date-aware KOSPI tax, commission, spread and impact cost

## Code-integrity corrections completed

### Distributional feature-override regression

A feature-ablation refactor accidentally left a literal `\\n` and referenced an undefined `features` variable inside `distributional_walk_forward`.  This was corrected and regression-tested.

### Ablation workflow YAML regression

The ablation workflow also contained a literal `\\n` in the path list.  The workflow is fixed and now runs compile + regression tests before research execution.

### Recency strict-Top3 consistency

The recency challenger previously sent all eligible names into stateful selection, permitting rank-4+ promotion after blocked positions.  It now freezes the original Top3 first, identical to the reference policy.

## Strict Distributional NetEV reference — reproduced

The repaired pipeline reproduces the post-backfill-fix result exactly:

- test dates: **430**
- trade days: **26**
- selected trades: **47**
- trade-day coverage: **6.05%**
- mean gross return / trade: **+0.5899%**
- mean cost / trade: **0.3936%**
- mean net return / trade: **+0.1963%**
- win rate: **46.81%**
- Profit Factor: **1.1364**
- trade ES95: **-5.93%**
- date-cluster bootstrap point: **+0.1188%**
- date-cluster 95% interval: **-1.1726% to +1.5552%**
- portfolio total return: **+0.584%**
- portfolio MDD: **-3.995%**
- average gross exposure: **~4.85%**

Verdict: **NO_ROBUST_DISTRIBUTIONAL_EDGE_YET**.

Reason: point estimate and PF are positive but the date-cluster lower confidence bound remains negative and the sample is small.

The earlier 84-trade / ~+0.41% result is **superseded** because it predated the strict Top3 no-backfill correction.

## Recency challenger — rejected

One prespecified rolling 160-session training window was compared with expanding history. No window sweep was performed.

Rolling-160 strict result:

- trades: **85**
- mean net return: **-1.5827%**
- PF: **0.4467**
- date-cluster 95% interval: **-4.1816% to -0.1542%**
- portfolio total return: **-17.64%**
- MDD: **-20.53%**

Decision: **KEEP_EXPANDING_REFERENCE**. Do not optimize recency windows from these results.

## Feature-family ablation — latest completed

All variants use the same purged walk-forward, calibration, NetEV lower-bound admission, strict Top3 freeze and no-backfill execution policy.

### all_context reference

- 47 trades
- mean net: **+0.1963%**
- PF: **1.1364**
- cluster 95% low: **-1.1726%**

### base_only

- 24 trades
- mean net: **-1.4583%**
- PF: **0.5278**

### drop_market = base + residual

- 32 trades
- mean net: **-0.1314%**
- PF: **0.9013**

### drop_residual = base + market

Numerically identical to all_context in this sample:

- 47 trades
- mean net: **+0.1963%**
- PF: **1.1364**

### context_only = market + residual

Current strongest point estimate:

- 62 trades / 24 trade days
- mean gross: **+1.7123%**
- mean cost: **0.2838%**
- mean net: **+1.4285%**
- PF: **2.0548**
- ES95: **-7.22%**
- date-cluster 95% interval: **-0.4804% to +3.2025%**
- 2x cost-stress PF: **1.7757**

This is promising but **not promotable** because the cluster lower bound remains negative and the selected sample is still small.

### market_only

- 24 trades
- mean net: **-0.0628%**
- PF: **0.9539**

### residual_only

- 0 admitted trades under conservative NetEV lower-bound rule.

Interpretation: the strong `context_only` result is not explained by market state alone or residual relative strength alone.  It appears only when the two are combined under the fixed volatility-bucket calibration architecture. This interaction must survive longer history before it is treated as genuine edge.

Note: calibration always conditions residual quantiles on `vol20_rank` terciles. Therefore `market_only` is not a mathematically pure market-only ranking experiment; it is market-model features under the fixed volatility-calibration layer.

## Historical cost schedule

The PIT engine now encodes exact effective-date KOSPI statutory sell tax for the modern price-limit regime:

- 2015-06-15 .. 2019-06-02: **30bp** statutory sell tax including rural special tax
- 2019-06-03 .. 2020-12-31: **25bp**
- 2021-2022: **23bp**
- 2023: **20bp**
- 2024: **18bp**
- 2025: **15bp**
- 2026: **20bp**

Round-trip broker commission remains separate at 3bp in current research.

## Long-history robustness — running

A new non-sealed robustness workflow is running on the PIT KOSPI universe from **2015-06-15 to 2026-09-28**.

Prespecified protocol:

- initial train: 504 sessions (~2 years)
- separate calibration: 126 sessions (~6 months)
- purge: 5 sessions
- OOS test block: 126 sessions (~6 months)
- liquidity floor: ADV20 rank >= 20th percentile
- strict original Top3 / no backfill
- compare only `all_context_reference` vs `context_only_challenger`
- no threshold/window/hyperparameter search

This is a historical robustness test, **not** a sealed holdout, because the candidate architecture was already informed by later-period research.

## Final Judge blockers still open

1. Official common-stock security master; current PIT universe contains all KOSPI listed securities.
2. Exact halt/delisting economics instead of synthetic planned-stop treatment for post-entry missing bars.
3. Intraday fill ratio × fill time × fill price and post-fill markout.
4. Recommendation latency/expiry and actual execution delay stress.
5. Longer-history robustness completion and regime/year concentration analysis.
6. Multiple-testing / research-ledger accounting across full policy search.
7. Fresh sealed evidence: prospective Shadow S1 → frozen Fresh Confirmation S2.

## Promotion rule

No candidate is promoted because it has a positive point estimate, attractive CAGR, or high PF alone.

At minimum preliminary promotion requires:

- positive cost-adjusted OOS mean Net Return
- PF > 1
- **positive date-cluster 95% lower bound**
- acceptable MDD / ES / tail dependence
- non-degenerate coverage and effective sample size
- stable performance across reasonable time/regime slices
- no hidden leakage, backfill, data-quality or cost-model dependency

Final promotion additionally requires the unresolved security-master, halt/delisting, execution-realism, sealed-holdout and prospective Shadow requirements.
