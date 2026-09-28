# IndexAlert Research Status

Updated: 2026-09-29 KST
Branch: `index-alert-research-v1`
Promotion authority: **none yet** — all results remain PIT preliminary until final Judge blockers are removed.

## Latest completed reference

GitHub Actions run: `36458508197` — **IndexAlert Research v1 Purged PIT**
Result: `NO_ROBUST_SHORT_TERM_EDGE_YET`

### Best completed candidate

`logistic_context_top3_only`, 5-session label embargo/purge, original top-3 only, no forced backfill.

- trades: 604
- mean gross return / trade: -0.0176%
- mean cost / trade: 0.3160%
- mean net return / trade: -0.3337%
- profit factor: 0.7707
- date-cluster bootstrap 95% interval: -0.5422% to +0.0852%
- portfolio total return: -15.85%
- portfolio max drawdown: -30.43%
- average gross exposure: ~40.7%
- trade-day coverage: ~85.1%

Current suitability: **not suitable for live short-term investing**.

## Important diagnostics already resolved

### Leakage

- Decision-time no-fill names stay in the ranking universe.
- A missing next-open fill leaves the slot empty; rank 4 is not promoted with future knowledge.
- Model train/test boundaries are purged by the full 5-session outcome horizon.
- Same-bar target/stop cases are not removed with future knowledge; primary policy is conservative stop-first.

### Cost

Historical KOSPI statutory sell tax is date-aware in the PIT label engine:

- 2024: 18bp statutory + 3bp primary round-trip commission = 21bp explicit
- 2025: 15bp + 3bp = 18bp
- 2026: 20bp + 3bp = 23bp

Cost sensitivity on the exact same 604 selected trades:

- primary mean net: -0.3337%
- 0bp broker commission, statutory tax retained: -0.3037%
- **zero statutory tax + zero commission upper bound: -0.1301%**
- zero-explicit-cost PF: 0.9029
- zero-explicit-cost total return: -2.23%

Conclusion: **explicit tax/commission is not the primary failure. Gross signal quality is still insufficient.**

### Same-bar ambiguity

Optimistic target-first upper bound with identical model scores/ranks:

- mean net improves by only +0.0861%/trade
- optimistic mean net remains -0.2476%
- optimistic PF remains 0.8250
- optimistic MDD remains -28.40%

Conclusion: **intraday first-hit ordering alone cannot rescue the current strategy.** Intraday history is still useful later for execution realism, but is not the current first priority.

### Security scope

Conservative common-like heuristic removes 115 of 980 unique symbols.

Common-like diagnostic candidate:

- mean gross: +0.0387%
- mean net: -0.2631%
- PF: 0.8134
- MDD: -29.87%

It is a small improvement but still unsuitable. The heuristic is **not** allowed to mark common-stock identity as validated; official security-master confirmation remains required for final Judge status.

### Post-entry missing bars

1,245 labelled paths hit a missing future executable daily bar under the preliminary data-gap rule.

Cause diagnostic:

- 1,209: security still present in PIT membership but bar invalid / likely halted
- 36: member absent with no later observed reappearance in the sample
- 1,018 cases later have a valid execution bar again
- median return-to-valid-bar: 2 sessions
- p90: 18 sessions

Conclusion: halt/delisting economics must be fixed before final Judge promotion, but the total incidence is small relative to ~594k labelled rows. Measure incidence among selected trades before prioritizing this above signal improvements.

## Current research priority

Do **not** increase model complexity yet.

1. `path-context` challenger: gap, intraday return, daily range, close location, trading-value surprise.
2. `fixed-horizon label` challenger: next-open -> D+5 cost-adjusted return, while execution policy remains unchanged.
3. If needed, `cross-sectional rank label` challenger.
4. If tail loss remains dominant, `volatility risk-veto` challenger.
5. If signal remains weak, prespecified liquidity-universe sensitivity (top 80/50/20% ADV20).
6. Only after a simple candidate has positive OOS economics: longer 2016+ history, official common-stock security master, exact halt/delisting economics, intraday execution data, sealed holdout and Shadow.

## Fast iteration infrastructure

- `research_v1_fast_purged_candidate.py`
- `research_v1_path_context.py`
- `research_v1_fixed_horizon_label.py`
- `research_v1_supervised_cache.py`
- fast Actions workflow: `.github/workflows/indexalert-research-v1-fast.yml`

A deterministic supervised cache is being added so repeated experiments do not rebuild ~600k 5-session paths every time.

## Promotion rule

No candidate is promoted because it merely improves relative to the current negative baseline.

A preliminary promotion candidate still requires, at minimum:

- positive cost-adjusted mean OOS return
- PF > 1
- positive date-cluster 95% lower bound
- acceptable MDD / tail risk
- no hidden degradation from coverage, turnover, costs or data-quality blockers

The full Research Constitution and final Judge requirements remain in force.
