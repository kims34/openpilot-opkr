# IndexAlert KRX Historical Railway Readiness Evidence

Updated: 2026-10-02 22:33 KST  
Evidence ID: `INDEXALERT-KRX-HIST-WORKER-RAILWAY-READINESS-2026-10-02-v1`  
Status: **PREFLIGHT PROVISIONING COMPLETE — BULK EXECUTION NOT AUTHORIZED**

Railway production now contains the isolated historical worker required by the frozen deployment contract:

- service: `indexalert-krx-historical-worker`
- service ID: `003812ee-102b-42b6-bda4-36925885b428`
- source: `kims34/openpilot-opkr@index-alert-research-v1`
- Dockerfile: `Dockerfile.krx-historical-worker`
- start command: `python research_v1_krx_historical_worker_entrypoint.py`
- restart policy: `NEVER`
- cron: none
- public domain: none
- dedicated volume: `indexalert-krx-historical-data`
- volume ID: `61610fae-dc0c-493e-9920-eb3cef4cea86`
- volume mount: `/data`
- private raw root: `/data/indexalert/krx-historical-v3`

The production runtime's existing volume `f96f985a-8aba-41ef-88df-f76999c4ff0c` was not reused.

Direct worker variables present:
- `KRX_PRIVATE_RAW_DIR`
- `INDEXALERT_KRX_HIST_WORKER_ROLE`

Still absent:
- `KRX_ID`
- `KRX_PW`
- `KRX_AUTH_KEY`
- `KRX_HISTORICAL_ACQUISITION_CONSENT`
- `KRX_EXPECTED_SCOPE_ATTESTATION_CONSENT`

Corrected preflight deployment `d5365809-f146-41d6-b536-942555a20b1d` completed SUCCESS from branch commit `0d407fa9fc92bcf5b594967a35783e99681fb98d`.

Runtime preflight evidence reported:
- `mode=PREFLIGHT_ONLY`
- `network_request_attempted=false`
- `historical_acquisition_network_execution_authorized=false`
- `feature_performance_testing_authorized=false`
- `sealed_holdout_authorized=false`
- `live_trading_authorized=false`

The initial deployment `4c9958db-d3be-410d-9f5a-792be9cc5cbd` built the repository default Dockerfile before the dedicated Dockerfile setting was corrected. It was superseded and removed. No KRX credential or network-execution consent was present and no historical KRX network request was attempted.

Current verdict:
- dedicated worker service exists: **true**
- dedicated worker volume exists: **true**
- preflight infrastructure ready: **true**
- worker secrets configured: **false**
- infrastructure ready for bulk execution: **false**
- bulk historical network execution authorized: **false**
- expected-scope network execution authorized: **false**
- feature-performance testing authorized: **false**
- sealed holdout authorized: **false**
- live trading authorized: **false**

The next external step is worker-secret configuration. The 27-request `IDENTITY_SEED` may run only after those secrets are present **and** the separate frozen bulk-execution consent is explicitly granted.
