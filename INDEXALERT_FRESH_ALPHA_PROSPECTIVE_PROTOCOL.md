# IndexAlert Fresh Alpha Prospective Diagnostic Protocol

Status: **FROZEN PROSPECTIVE DIAGNOSTIC — NOT SHADOW S1 / NOT PROMOTION AUTHORITY**

## Purpose

Test whether the current frozen H5 reference policy retains executable positive edge in genuinely future market observations without reopening or re-mining the historical development sample.

This protocol is diagnostic only. The current H5 reference is developmental/not currently promotable and is not an ACCEPTED_CHALLENGER. Therefore observations gathered under this protocol must not be relabelled as formal Shadow S1, Fresh Confirmation S2, sealed-holdout evidence, or LIVE execution evidence.

## Evidence chronology

Only decisions whose decision timestamp is strictly after the GitHub commit that first introduces this protocol are eligible.

Historical rows, backfilled decisions, reconstructed signals, replayed historical outcomes, synthetic rows, paper fills, or any observation whose recommendation was not produced prospectively are ineligible.

No outcome observed before preregistration may be attached to this protocol.

## Frozen policy under observation

No research parameter is changed for this diagnostic:

- H5 horizon.
- Point-in-time / availability-time rules unchanged.
- Anchored WF train 504 / calibration 126 / test 126 remains the research reference.
- Purge / embargo = H5.
- Existing selection-conditioned conservative NetEV/q25 logic unchanged.
- Normal-market eligibility overlay unchanged.
- 0 to 3 names only.
- Original decision-time Top3 frozen before downstream vetoes.
- No rank-4+ backfill.
- NO_TRADE is a valid and expected outcome.
- Existing cost/tax/slippage assumptions unchanged.
- Corporate-action-safe return policy unchanged.
- Champion/Core/operating code is not modified by this protocol.

## Observation checkpoints

The first preregistered diagnostic checkpoint is after **126 completed KRX sessions** following the freeze anchor, matching the frozen test-block length.

A second long-current-regime checkpoint is after **504 completed KRX sessions**, matching the existing recent-evidence audit window.

A checkpoint may be reported earlier only for data-integrity failure or to state that the required number of future sessions has not yet accrued. It may not be used to retune the policy.

## Required observations

Every eligible KRX session must preserve the exact prospective decision output, including zero-admission / NO_TRADE sessions. For admitted candidates preserve the information needed to evaluate the existing executable H5 return proxy and the existing cost assumptions.

The diagnostic must report at least:
- eligible future sessions;
- admission days and NO_TRADE days;
- selected trade count;
- mean cost-adjusted NetReturn;
- Profit Factor;
- date-cluster 95% LCB(NetReturn);
- 2x-cost mean NetReturn and PF;
- MDD;
- trade and daily ES95 / ES99 where defined;
- turnover / coverage;
- concentration by decision date and symbol;
- remove-best-1/3/5-decision-day sensitivity when enough decision days exist.

## Interpretation

The frozen promotion-style robustness conjunction remains the reference diagnostic:
- mean cost-adjusted NetReturn > 0;
- PF > 1;
- date-cluster LCB > 0;
- 2x-cost mean > 0 and PF > 1;
- best-five-decision-day removal preserves positive mean, PF > 1 and positive date-cluster LCB when the sample supports that diagnostic.

Passing these conditions does **not** promote the policy. It only creates genuinely new evidence that may justify a separately preregistered next-stage Challenger/confirmation decision.

Failure, zero admissions, weak LCB, extreme concentration or deterioration must be preserved. Do not change thresholds, horizon, TopK, model, features, costs or regime rules in response within this same protocol.

## Hard boundaries

- Project-v1 consumed failed-invalid holdout is never reopened, reset or relabelled.
- No real order is submitted by this research protocol.
- No broker permission, account setting, funds movement or live-order authorization is granted.
- Development/Android/server code is outside this protocol.
- Any future formal Shadow S1 or Fresh Confirmation S2 requires its own applicable canonical gate and independent admission.

## Current disposition

**CONTINUE VALIDATION** — protocol frozen now; qualifying evidence must be generated prospectively after the freeze anchor.
