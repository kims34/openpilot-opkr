# IndexAlert KRX Worker Provisioning Readiness Evidence

Updated: 2026-10-02 KST  
Evidence ID: `INDEXALERT-KRX-WORKER-PROVISIONING-READINESS-2026-10-02-v1`  
Status: **READ-ONLY AUDIT — DEDICATED WORKER/VOLUME NOT YET PROVISIONED**

A read-only Railway inspection of project `IndexAlert`, environment `production`, found these existing services:

- `db-query-readonly`
- `verify-deployment-status`
- `indexalert-runtime`
- `indexalert-push`
- `indexalert-backend`

The required service `indexalert-krx-historical-worker` does **not** yet exist.

## Existing /data volume must not be reused

The public `indexalert-runtime` service already has a volume mounted at `/data`.

That volume is **not** eligible for the historical worker. The frozen worker/execution contract requires a dedicated private worker volume and explicitly forbids sharing the raw-data boundary with the public runtime.

The future worker therefore still requires its own persistent volume:
- mount: `/data`
- raw root: `/data/indexalert/krx-historical-v3`

## Worker configuration still missing

The future worker must use:
- repo: `kims34/openpilot-opkr`
- branch: `index-alert-research-v1`
- Dockerfile: `Dockerfile.krx-historical-worker`
- default command: `python research_v1_krx_historical_worker_entrypoint.py`
- no public domain
- no cron
- restart policy `NEVER`

Worker-only required secret names:
- `KRX_ID`
- `KRX_PW`
- `KRX_AUTH_KEY`

Required non-secret values:
- `KRX_PRIVATE_RAW_DIR=/data/indexalert/krx-historical-v3`
- `INDEXALERT_KRX_HIST_WORKER_ROLE=DEDICATED_ONE_SHOT`

The bulk consent variable `KRX_HISTORICAL_ACQUISITION_CONSENT` must remain **absent** during initial preflight-only deployment.

## Current blockers

- dedicated worker service not created;
- dedicated private volume not created/attached;
- worker-only KRX secrets not configured;
- service/volume creation not explicitly authorized.

This evidence authorizes **no Railway mutation and no KRX network request**. It does not authorize sealed holdout or live trading.
