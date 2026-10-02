# IndexAlert KRX Historical Worker Deployment Contract v1

Updated: 2026-10-02 KST  
Deployment contract: `INDEXALERT-KRX-HIST-WORKER-DEPLOY-v1`  
Bound acquisition plan: `INDEXALERT-KRX-HIST-ACQ-v3`  
Bound execution contract: `INDEXALERT-KRX-HIST-EXEC-v3`  
Status: **PREPARED ONLY — NO WORKER SERVICE / VOLUME / BULK EXECUTION AUTHORIZED**

## Purpose

The full-history KRX acquisition must not run inside `indexalert-runtime`,
`indexalert-backend` or `indexalert-push`. It requires an isolated one-shot
worker with a dedicated private persistent volume.

The worker image is defined by `Dockerfile.krx-historical-worker`.
Its default command is deliberately network-free:

`python research_v1_krx_historical_worker_entrypoint.py`

It does **not** contain `--execute-identity-seed`.

## Required Railway shape before any bulk request

Service name:

`indexalert-krx-historical-worker`

Source:
- repository: `kims34/openpilot-opkr`
- branch: `index-alert-research-v1`
- Dockerfile: `Dockerfile.krx-historical-worker`

The service must have no public domain and no cron. Restart policy must be
one-shot / never restart after successful exit.

A dedicated persistent volume must be attached at:

`/data`

The private raw root must be:

`/data/indexalert/krx-historical-v3`

The volume must not be the production web runtime's shared raw-data boundary.
Before network execution, Railway service config must visibly attest the worker's
own `/data` volume mount.

## Required worker variables

Secret variables:
- `KRX_ID`
- `KRX_PW`
- `KRX_AUTH_KEY`

Non-secret exact values:
- `KRX_PRIVATE_RAW_DIR=/data/indexalert/krx-historical-v3`
- `INDEXALERT_KRX_HIST_WORKER_ROLE=DEDICATED_ONE_SHOT`

Railway's own `RAILWAY_SERVICE_NAME` must resolve to
`indexalert-krx-historical-worker`.

## Bulk execution consent remains absent

The initial preflight deployment must **not** contain:

`KRX_HISTORICAL_ACQUISITION_CONSENT`

The only valid value later is:

`I_AUTHORIZE_INDEXALERT_KRX_HIST_ACQ_v3`

That value may be configured only after explicit user approval for the full
historical acquisition. Tiny-probe consent does not count.

## First executable stage after future approval

Even after bulk execution is explicitly approved, the worker may initially run
only:

`python research_v1_krx_historical_worker_entrypoint.py --execute-identity-seed`

That stage is exactly 27 preregistered identity/status seed requests. Each
request writes immutable private raw bytes, a receipt, manifest and checkpoint.
The private phase state must reach exact `IDENTITY_SEED=COMPLETE` before the
listing-date master phase can initialize.

No per-security investor-flow or status-history phase may be skipped ahead.

## Public-output boundary

No raw KRX rows or raw response bytes may enter GitHub, public Actions artifacts,
service logs or a public web response. Public outputs are limited to counts,
phase status and cryptographic fingerprints.

## Authority

This deployment contract does not authorize:
- creating a Railway service;
- creating or attaching a paid persistent volume;
- setting bulk execution consent;
- starting the historical network job;
- performance research;
- sealed holdout;
- live trading.

Those remain separate actions.
