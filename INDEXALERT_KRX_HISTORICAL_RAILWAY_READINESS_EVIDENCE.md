# IndexAlert KRX Historical Railway Readiness Evidence

Updated: 2026-10-02 22:47 KST  
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
- `KRX_ID`
- `KRX_PW`
- `KRX_AUTH_KEY`

Still absent:
- `KRX_HISTORICAL_ACQUISITION_CONSENT`
- `KRX_EXPECTED_SCOPE_ATTESTATION_CONSENT`

After the user corrected the password variable name from `KRW_PW` to `KRX_PW`, Railway auto-redeployed once with the repository default image and failed to find the worker entrypoint. No KRX network request was attempted. A manual redeploy under the frozen worker config then produced corrected deployment `02b5697c-b959-45b5-9ef5-600c05efcf32`, which completed SUCCESS using `Dockerfile.krx-historical-worker`.

Runtime preflight evidence from deployment `02b5697c-b959-45b5-9ef5-600c05efcf32` reported:
- `mode=PREFLIGHT_ONLY`
- `krx_id_present=true`
- `krx_pw_present=true`
- `krx_openapi_auth_key_present=true`
- `explicit_execution_consent_present=false`
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
- worker secrets configured: **true**
- infrastructure ready for bulk execution: **false**
- bulk historical network execution authorized: **false**
- expected-scope network execution authorized: **false**
- feature-performance testing authorized: **false**
- sealed holdout authorized: **false**
- live trading authorized: **false**

The worker-secret prerequisite is now satisfied. The next protected step is the separate frozen bulk-execution consent. The 27-request `IDENTITY_SEED` must not run until the exact execution sentinel `I_AUTHORIZE_INDEXALERT_KRX_HIST_ACQ_v3` is explicitly supplied.
