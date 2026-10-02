# IndexAlert KRX Worker Provisioning Consent Contract v1

Updated: 2026-10-02 KST  
Contract: `INDEXALERT-KRX-WORKER-PROVISIONING-v1`  
Status: **FROZEN — USER-AUTHORIZED; PROVISIONING NOT YET COMPLETED**

This contract separates Railway infrastructure provisioning from every KRX network-execution consent.

Exact approval phrase:

`I_AUTHORIZE_INDEXALERT_KRX_WORKER_PROVISIONING_v1`

Creating a Railway service and persistent volume may incur Railway usage/storage charges.

## Authorization record

The exact approval phrase was received on 2026-10-02 KST. This authorizes only the provisioning scope below. The first provisioning attempt did not mutate Railway because the available Railway infrastructure agent returned `Agent usage limit reached`; unsafe fallback deployment paths were not used. The dedicated service and volume therefore remain absent until the authorized provisioning can be executed atomically.

## What this approval would allow

Only:
- create `indexalert-krx-historical-worker`;
- source `kims34/openpilot-opkr@index-alert-research-v1`;
- Dockerfile `Dockerfile.krx-historical-worker`;
- default network-free entrypoint;
- restart policy `NEVER`;
- no public domain;
- no cron;
- dedicated private volume at `/data`;
- `KRX_PRIVATE_RAW_DIR=/data/indexalert/krx-historical-v3`;
- `INDEXALERT_KRX_HIST_WORKER_ROLE=DEDICATED_ONE_SHOT`;
- preflight-only deployment with all acquisition consent variables absent.

## What this approval would NOT allow

It does not authorize:
- `KRX_HISTORICAL_ACQUISITION_CONSENT`;
- `KRX_EXPECTED_SCOPE_ATTESTATION_CONSENT`;
- any historical KRX network request;
- expected-scope sweep;
- any execute-* worker stage;
- reuse of the public runtime volume;
- public domain or cron;
- feature-performance testing;
- sealed holdout;
- live trading.

## Secret boundary

The worker will eventually need secret names `KRX_ID`, `KRX_PW`, and `KRX_AUTH_KEY`.

Their values must not be committed to GitHub or sent in chat. If Railway cannot copy them across services without exposing values to the assistant, the user must enter them directly in the Railway secret UI.

Provisioning approval and secret entry do not authorize any KRX network execution.
