# IndexAlert KRX Worker Provisioning Consent Contract v1

Updated: 2026-10-02 KST  
Contract: `INDEXALERT-KRX-WORKER-PROVISIONING-v1`  
Status: **FROZEN — USER-AUTHORIZED; PROVISIONING COMPLETED / PREFLIGHT ONLY**

This contract separates Railway infrastructure provisioning from every KRX network-execution consent.

Exact approval phrase:

`I_AUTHORIZE_INDEXALERT_KRX_WORKER_PROVISIONING_v1`

Creating a Railway service and persistent volume may incur Railway usage/storage charges.

## Authorization record

The exact approval phrase was received on 2026-10-02 KST. This authorizes only the provisioning scope below.

Provisioning completed on 2026-10-02 KST:
- service `indexalert-krx-historical-worker` / ID `003812ee-102b-42b6-bda4-36925885b428`;
- dedicated volume `indexalert-krx-historical-data` / ID `61610fae-dc0c-493e-9920-eb3cef4cea86`, mounted at `/data`;
- source `kims34/openpilot-opkr@index-alert-research-v1`;
- build `Dockerfile.krx-historical-worker`;
- start command `python research_v1_krx_historical_worker_entrypoint.py`;
- restart policy `NEVER`, no cron, no public domain;
- direct service variables only: `KRX_PRIVATE_RAW_DIR` and `INDEXALERT_KRX_HIST_WORKER_ROLE`;
- `KRX_HISTORICAL_ACQUISITION_CONSENT`, `KRX_EXPECTED_SCOPE_ATTESTATION_CONSENT`, `KRX_ID`, `KRX_PW`, and `KRX_AUTH_KEY` remained absent.

The corrected preflight deployment `d5365809-f146-41d6-b536-942555a20b1d` completed SUCCESS. Its runtime log reported `mode=PREFLIGHT_ONLY`, `network_request_attempted=false`, `historical_acquisition_network_execution_authorized=false`, `feature_performance_testing_authorized=false`, `sealed_holdout_authorized=false`, and `live_trading_authorized=false`.

An earlier initial deployment built the repository default Dockerfile before the dedicated Dockerfile setting was corrected; it was superseded and removed. No KRX credentials or network-execution consent were present, and no historical KRX network request was attempted.

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
