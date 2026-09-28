# IndexAlert Research Status

Updated: 2026-09-29 KST
Branch: `index-alert-research-v1`
Master authority: `INDEXALERT_MASTER_SPEC.md`
Promotion authority: **none yet** — all results remain PIT preliminary until final Judge blockers are removed.

## Current direction

The research center of gravity has moved from fixed barrier / UP-DOWN classification to **executable cost-adjusted NetReturn / NetEV distribution**.

Legacy barrier models remain only as diagnostics and reference baselines.

## Latest completed Core candidate

GitHub Actions run: `36466349857` — **IndexAlert Research v1 Distributional NetEV**

Candidate:

`Ridge mean fixed-horizon NetReturn + purged calibration residual q25/q50/q75 by volatility tercile`

Admission:

`conservative NetEV lower bound > 0` → select **0 to 3**

Execution proxy:

prior-close decision → next executable regular-session open → D+5 close → date-aware tax + commission + spread/impact allowance

### Distributional NetEV v0 result

- test dates: 430
- trade days: 30
- trade-day coverage: **6.98%**
- selected trades: **84**
- mean gross return / trade: **+0.7572%**
- mean cost / trade: **0.3454%**
- mean net return / trade: **+0.4118%**
- win rate: 47.62%
- Profit Factor: **1.2982**
- trade ES95: **-6.35%**
- date-cluster bootstrap point estimate: +0.2765%
- date-cluster bootstrap 95% interval: **-0.7563% to +1.4187%**
- portfolio total return: **+1.60%**
- portfolio MDD: **-2.98%**
- annualized volatility: ~4.12%
- average gross exposure: ~5.58%
- average cash weight: ~94.42%

Verdict: **NO_ROBUST_DISTRIBUTIONAL_EDGE_YET**

Reason: mean, PF and MDD improved materially, but the date-cluster lower confidence bound remains negative and the selected sample is only 84 trades / 30 trade days.

## Distribution calibration diagnostic

Target lower quantile: q25.

Observed:

- actual return >= predicted lower bound: **74.32%**
- intended lower-bound coverage: 75%
- actual inside q25-q75 interval: **45.53%**
- nominal central q25-q75 interval: 50%

Interpretation: the simple calibration layer is directionally credible enough to continue research, but no formal exchangeability/conformal guarantee is claimed.

## Counterfactual observable diagnostic

Within test rows with observable D+5 return:

- admitted mean fixed-horizon Net Return: **+0.4118%**
- rejected mean fixed-horizon Net Return: **-0.0809%**
- rejected positive-return rate: ~45.14%

This is evidence that the abstention gate is separating a more attractive subset, but confidence remains insufficient for promotion.

## Year / drift note

Earlier fixed-horizon and path-context challengers showed material 2025→2026 performance instability. This motivates one prespecified rolling-recency challenger against expanding history.

No train-window sweep is allowed.

## Important diagnostics already resolved

### Leakage

- Decision-time no-fill names remain in the ranking universe.
- Missing next-open fill leaves a slot empty; no future-aware promotion.
- Learning boundaries are purged by the full five-session outcome horizon.
- Distributional architecture uses a separate calibration block with purge on both sides.
- Same-bar target/stop ambiguity is no longer the Core learning objective.

### Cost

Historical KOSPI statutory sell tax is date-aware in the PIT engine.

Legacy cost sensitivity showed that removing explicit tax/commission alone did not rescue the old signal, so research no longer treats fee reduction as the main path to improvement.

### Same-bar ambiguity

Optimistic target-first handling did not rescue the legacy strategy. Intraday first-hit data remains useful for future execution realism, but it is not the current source of the observed distributional improvement.

### Security scope

Current PIT membership is valid for the full KOSPI listed-security universe, but official common-stock identity is not yet validated. Heuristic common-like filtering remains diagnostic only.

### Post-entry missing bars

The old barrier ledger had 1,245 post-entry missing-bar cases across ~594k labelled rows; only a very small number occurred among selected candidates in recent simple models. Exact halt/delisting economics remains a Final Judge blocker but is not currently the dominant performance driver.

## Prior challenger findings

### Path-context

PIT-safe gap / intraday / range / close-location / trading-value-surprise features improved gross edge materially, but still produced negative post-cost mean and unstable confidence interval.

### Fixed-horizon label Logistic

Learning next-open→D+5 direction improved stability versus the barrier label but remained negative after costs.

### Path + fixed-horizon combination

Simple combination did **not** create synergy; it remained negative and worsened MDD. The combined classifier is rejected as a Core direction.

### Fixed-horizon Ridge positive-only

Underperformed and is rejected as a standalone admission rule.

## Current research priority

Follow `INDEXALERT_MASTER_SPEC.md`.

1. **Distributional NetEV v0** — retain as current Core challenger, not Champion.
2. **One prespecified recency test** — expanding vs rolling 160-session training, with calibration/purge unchanged.
3. If recency improves robustness, freeze that direction for further fresh validation; do not window-optimize.
4. Feature-family ablation / marginal economic value / Remaining Alpha.
5. Feature freshness / TTL and missingness semantics.
6. Independent liquidity / volatility / systemic-risk veto diagnostics.
7. Official common-stock security master + exact halt/delisting economics.
8. Intraday fill-ratio × fill-time × fill-price + post-fill markout.
9. Longer historical Judge, sealed holdout, Shadow S1 and Fresh Confirmation S2.

## Promotion rule

A candidate is not promoted because it merely loses less or has a positive point estimate.

At minimum a preliminary promotion candidate requires:

- positive cost-adjusted OOS mean Net Return
- PF > 1
- **positive date-cluster 95% lower bound**
- acceptable MDD / ES / tail loss
- non-degenerate coverage and sample size
- no hidden degradation from costs, data quality or leakage

Final Judge promotion additionally requires the unresolved security-master, halt/delisting, long-history, sealed-holdout and Shadow requirements.
