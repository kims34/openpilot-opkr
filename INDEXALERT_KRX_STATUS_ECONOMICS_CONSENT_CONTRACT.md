# IndexAlert KRX STATUS_ECONOMICS Consent Contract v1

Updated: 2026-10-03 KST  
Contract ID: `INDEXALERT-KRX-STATUS-ECONOMICS-CONSENT-v1`  
Stage: `STATUS_ECONOMICS`  
Status: **FROZEN SHELL — PREPARATION NOT YET COMPLETE — EXECUTION NOT AUTHORIZED**

## Purpose

This contract isolates the `STATUS_ECONOMICS` network stage from the currently running `PER_SECURITY_HISTORY` stage.

The current `PER_SECURITY_HISTORY` approval does not authorize this stage.

## Mandatory predecessor

Before this contract can become execution-ready:
- `PER_SECURITY_HISTORY` must be exactly **14,296/14,296**;
- failed task count must be **0**;
- phase status must be `COMPLETE`;
- phase_complete must be **true**;
- task-set SHA-256 must equal `fb5b883c6fe0e9c15e88aea9bdf874ddd7a11ae8a009c2ddf91c4e4249a8ba38`;
- both current PER_SECURITY_HISTORY execution consent values must be disabled again;
- the worker must be restored to preflight-only and verified network-free.

## Mandatory network-free preparation

After the predecessor is complete and locked, the only allowed next internal action is:

`python research_v1_krx_historical_worker_entrypoint.py --prepare-status-economics`

That preparation must:
- perform **zero** KRX network requests;
- create the private immutable `task_manifests/status-economics-v3.json`;
- produce a positive task count, task-set fingerprint and private manifest metadata hash;
- keep `exact_status_economics_ready=false`;
- emit no raw rows or security identifiers publicly;
- keep source gates C/D/E open;
- keep feature-performance testing, sealed holdout and live trading unauthorized.

Until those exact preparation outputs are observed and committed into this contract, this contract is **not execution-ready**.

## Exact future approval phrase

Even after preparation is complete and its exact scope is frozen, actual `STATUS_ECONOMICS` network execution still requires a new explicit user message:

`I_AUTHORIZE_INDEXALERT_KRX_STATUS_ECONOMICS_v1`

No prior approval is reusable.

## Runtime gate after future preparation

Future execution may proceed only if all of the following are true:
- exact frozen STATUS_ECONOMICS task count matches the prepared contract;
- task-set SHA-256 matches;
- private manifest metadata SHA-256 matches;
- `KRX_HISTORICAL_ACQUISITION_CONSENT=I_AUTHORIZE_INDEXALERT_KRX_HIST_ACQ_v3`;
- `KRX_STATUS_ECONOMICS_CONSENT=I_AUTHORIZE_INDEXALERT_KRX_STATUS_ECONOMICS_v1`;
- dedicated worker/private-volume checks pass;
- predecessor completion evidence remains valid.

Authorized future entrypoint, only after all gates above:

`python research_v1_krx_historical_worker_entrypoint.py --execute-status-economics`

## Explicitly not authorized

This contract does not authorize:
- any STATUS_ECONOMICS network execution now;
- expected-scope network execution;
- exact fill/recovery economics claims;
- feature-performance testing;
- Core/Champion promotion;
- sealed holdout;
- Shadow S1;
- genuine LIVE;
- real-account order submission.

Preparation alone can never grant execution authority.
