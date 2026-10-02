# IndexAlert KRX Per-Security History Preparation Evidence

Updated: 2026-10-03 KST  
Evidence ID: `INDEXALERT-KRX-PER-SECURITY-HISTORY-PREP-2026-10-03-v1`  
Stage: `PER_SECURITY_HISTORY`  
Status: **PREPARED — NETWORK-FREE — EXECUTION NOT AUTHORIZED**

## Preparation result

- Railway service: `indexalert-krx-historical-worker`
- Deployment: `f683b1a2-5db6-4e95-81a7-6ec5889a2c59`
- Exact source revision: `ffe0e2c05e2a705c4b4cf06922600d07daa464cc`
- Mode: `PREPARE_PER_SECURITY_HISTORY`
- Prepared task count: **14,296**
- `investor_trading_individual_daily`: **9,485**
- `trading_halt`: **4,811**
- Task-set SHA-256: `fb5b883c6fe0e9c15e88aea9bdf874ddd7a11ae8a009c2ddf91c4e4249a8ba38`
- Private task-manifest metadata SHA-256: `0d98f45168cedeecc013e95c71abe661ca1fac9df0403ba477d2f5653572c116`
- Private task-manifest relpath: `task_manifests/per-security-history-v3.json`
- Phase status: `PENDING`
- Network requests attempted during preparation: **0**
- Raw rows / security identifiers emitted publicly: **false**

## Identity corrections applied before freezing

The frozen task set was built only after fail-closed reconciliation of official KRX identity evidence:
- official six-character alphanumeric short issue codes are preserved rather than digit-stripped;
- new-listing episodes officially classified non-common on their same-day security master are excluded from the common-stock research universe;
- pre-start delisted episodes officially classified non-common on the 2015-06-15 start master are likewise excluded;
- missing or ambiguous mappings remain fail-closed rather than silently excluded or backfilled.

## Authority boundary

This preparation performed no KRX network request and does not authorize execution.

Actual network execution requires both:
- `KRX_HISTORICAL_ACQUISITION_CONSENT=I_AUTHORIZE_INDEXALERT_KRX_HIST_ACQ_v3`
- `KRX_PER_SECURITY_HISTORY_CONSENT=I_AUTHORIZE_INDEXALERT_KRX_PER_SECURITY_HISTORY_v1`

The worker was restored to preflight-only after preparation. This evidence does not authorize `STATUS_ECONOMICS`, expected-scope execution, feature-performance testing, sealed holdout, genuine LIVE or real-account ordering.
