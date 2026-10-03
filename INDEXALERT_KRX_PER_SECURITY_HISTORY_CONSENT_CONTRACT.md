# IndexAlert KRX Per-Security History Consent Contract v1

Updated: 2026-10-03 KST  
Contract ID: `INDEXALERT-KRX-PER-SECURITY-HISTORY-CONSENT-v1`  
Stage: `PER_SECURITY_HISTORY`  
Status: **USER-AUTHORIZED — EXECUTION IN PROGRESS**

## Purpose

This contract isolates the bulk per-security historical network stage from the completed `IDENTITY_STANDARD_CODE_BINDING` stage.

Earlier approvals do not authorize this stage.

## Frozen prerequisite and task set

Prerequisite:
- `IDENTITY_STANDARD_CODE_BINDING`: **COMPLETE 145/145**
- canonical execution evidence: `INDEXALERT_KRX_IDENTITY_BINDING_EXECUTION_EVIDENCE.md/.json`

Network-free preparation is complete:
- prepared task count: **14,296**
- investor-flow daily requests: **9,485**
- trading-halt requests: **4,811**
- task-set SHA-256: `fb5b883c6fe0e9c15e88aea9bdf874ddd7a11ae8a009c2ddf91c4e4249a8ba38`
- private task-manifest metadata SHA-256: `0d98f45168cedeecc013e95c71abe661ca1fac9df0403ba477d2f5653572c116`
- private manifest: `task_manifests/per-security-history-v3.json`
- preparation network requests: **0**
- canonical public preparation evidence: `INDEXALERT_KRX_PER_SECURITY_HISTORY_PREPARATION_EVIDENCE.md/.json`

## Exact future approval phrase

To authorize this stage only, the user must explicitly send:

`I_AUTHORIZE_INDEXALERT_KRX_PER_SECURITY_HISTORY_v1`

Until that exact phrase is supplied, network execution remains unauthorized.

## Runtime gate

Execution requires **both**:
- `KRX_HISTORICAL_ACQUISITION_CONSENT=I_AUTHORIZE_INDEXALERT_KRX_HIST_ACQ_v3`
- `KRX_PER_SECURITY_HISTORY_CONSENT=I_AUTHORIZE_INDEXALERT_KRX_PER_SECURITY_HISTORY_v1`

Authorized entrypoint for this stage only:

`python research_v1_krx_historical_worker_entrypoint.py --execute-per-security-history`

The worker must reject execution if task count, task-set hash, private manifest metadata hash, predecessor state, private volume, credentials, or either consent value differs from the frozen contract.

## Allowed scope after explicit approval

Approval would authorize only:
- the exact frozen **14,296** `PER_SECURITY_HISTORY` requests;
- checkpoint/resume of the same immutable task set;
- private content-addressed storage of raw response bytes on the dedicated Railway volume;
- metadata-only public evidence.

## Explicitly not authorized

This contract does not authorize:
- any task outside the frozen 14,296 requests;
- `STATUS_ECONOMICS`;
- expected-scope execution;
- feature-performance testing;
- Core/Champion promotion;
- sealed holdout;
- Shadow S1;
- genuine LIVE;
- real-account order submission.

## Post-run lock

After successful one-shot execution:
- both consent values must be disabled again;
- worker start command must return to network-free preflight;
- public evidence must contain metadata only;
- later stages remain unauthorized unless separately approved.


## Authorization / active execution record — 2026-10-03 KST

The exact user approval phrase `I_AUTHORIZE_INDEXALERT_KRX_PER_SECURITY_HISTORY_v1` was received and is consumed only for this one-shot stage.

- Railway deployment: `bc79d1b5-5fb8-46c7-8067-682e61947014`
- source revision: `9009c48a00394063c813d29219507ee2190ce09e`
- command: `python research_v1_krx_historical_worker_entrypoint.py --execute-per-security-history`
- exact frozen scope: **14,296** tasks
- task-set SHA-256: `fb5b883c6fe0e9c15e88aea9bdf874ddd7a11ae8a009c2ddf91c4e4249a8ba38`
- restart policy: `NEVER`
- later-stage auto-authorization: **false**

This authorization does **not** authorize `STATUS_ECONOMICS`, expected-scope network execution, feature-performance testing, sealed holdout, genuine LIVE, or live trading. After this stage completes or fails, both execution consent variables must be disabled again and the worker must return to preflight-only.


## Interrupted execution — 2026-10-03

The original one-shot deployment `bc79d1b5-5fb8-46c7-8067-682e61947014` at source revision `9009c48a00394063c813d29219507ee2190ce09e` terminated at 2026-10-03T00:45:16Z with `KRXHistoricalRequestExecutorError`.

The failure was an internal validator mismatch: the frozen PIT-safe planner correctly permits official six-character ASCII alphanumeric short codes, while that execution revision's request executor incorrectly required decimal digits only. No raw security identifier is recorded in this public contract.

The original one-shot authority is **consumed and inactive**. Both execution consent environment values have been disabled again, the configured start command has been restored to preflight-only, and restart policy remains NEVER. The run is **not complete** and no completion count is asserted here until a network-free aggregate checkpoint inspection verifies it.

Any resume must preserve the exact frozen 14,296-task manifest/fingerprint and private checkpoint semantics, use a CI-validated patched source revision, and requires a **new explicit user authorization** before any network request resumes. The exact resume approval phrase is `I_AUTHORIZE_INDEXALERT_KRX_PER_SECURITY_HISTORY_RESUME_v1`; runtime additionally requires `KRX_PER_SECURITY_HISTORY_RESUME_CONSENT` to equal that sentinel. This interruption does not authorize STATUS_ECONOMICS or any later protected stage.
