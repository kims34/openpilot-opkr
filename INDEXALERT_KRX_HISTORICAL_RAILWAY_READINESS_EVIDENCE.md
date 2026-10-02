# IndexAlert KRX Historical Railway Readiness Evidence

Updated: 2026-10-02 23:08 KST  
Evidence ID: `INDEXALERT-KRX-HIST-WORKER-RAILWAY-READINESS-2026-10-02-v1`  
Status: **IDENTITY BINDING COMPLETE — FURTHER NETWORK EXECUTION NOT AUTHORIZED**

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

Execution-consent state:
- `KRX_HISTORICAL_ACQUISITION_CONSENT` was set to the exact sentinel only for the authorized IDENTITY_SEED run, then immediately replaced with a non-authorizing value after completion;
- `KRX_EXPECTED_SCOPE_ATTESTATION_CONSENT` remains absent.

After the user corrected the password variable name from `KRW_PW` to `KRX_PW`, Railway exposed a builder-selection problem: the generic research-branch `railway.json` pointed at the repository default Dockerfile, and direct Railway `redeploy` could also reuse a Railpack path. Those mismatched attempts were forced back to preflight-only before runtime and made zero KRX network requests. Because `index-alert-research-v1` is used by this dedicated worker only, the branch-root `railway.json` was pinned to `Dockerfile.krx-historical-worker`.

Fresh preflight deployment `83be77ba-ccb1-4dcf-a40d-dd67a49fa9fb` at exact revision `6343f01b493404d59736e06eb6968e9820d0e595` completed SUCCESS using the 12-step worker Dockerfile.

Runtime preflight evidence from deployment `83be77ba-ccb1-4dcf-a40d-dd67a49fa9fb` reported:
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

The authorized IDENTITY_SEED then ran as fresh deployment `d268e5b0-b7c2-46be-b9ae-ca41d27cdb02` on the same exact revision and worker Dockerfile. It completed all **27/27** preregistered tasks with **27** network requests, zero resumes, phase `COMPLETE`, and `raw_rows_emitted=false`. Canonical sanitized evidence is `INDEXALERT_KRX_HISTORICAL_IDENTITY_SEED_EXECUTION_EVIDENCE.md/.json`.

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

The worker-secret prerequisite and IDENTITY_SEED are now complete. The exact bulk-execution sentinel used for the seed has been disabled again. `IDENTITY_STANDARD_CODE_BINDING` is complete and `PER_SECURITY_HISTORY` is prepared network-free. Actual `PER_SECURITY_HISTORY` network execution remains separately unauthorized. Gates C/D/E remain open.


## Identity-binding network-free preparation

On 2026-10-02 KST, fresh worker deployment `6d0081a8-933b-4e2e-bd83-4753d2a75799` at revision `ab09e9a0aabf5bcaba53372b6f48b34796715e5d` ran only `--prepare-identity-standard-code-binding`.

It froze exactly **145 `security_master` tasks** from the completed private seed:
- task-set SHA-256: `b3e9c845d74b0b479af0fd95d9015de92697fbd82b7bf07f9765378dfafd11d9`;
- private manifest metadata SHA-256: `940f446caec81dd1a4a7b3a01053ae3f6a6ef6c79654e23bf2b971dca3622a6c`;
- phase: `PENDING`;
- network requests attempted: **0**;
- raw rows / identifiers emitted publicly: **false**.

The worker start command was restored to preflight-only immediately after preparation. `KRX_IDENTITY_BINDING_CONSENT` remains absent. Actual binding execution is not authorized.


## Identity-binding execution

On 2026-10-03 KST, deployment `3501cbb8-a6a6-4972-bf82-4fb8e3fb36f6` at exact revision `6c152d8f29354d843b16c35be27a86a8a8058908` executed only the frozen `IDENTITY_STANDARD_CODE_BINDING` stage.

- completed: **145/145**
- resumed: **0**
- network requests attempted: **145**
- task-set SHA-256: `b3e9c845d74b0b479af0fd95d9015de92697fbd82b7bf07f9765378dfafd11d9`
- private execution-batch metadata SHA-256: `d5ca4e7ea45033f6bd6d45e301f1d3041b2e7257836e60d71c442fa73d8013be`
- phase: `COMPLETE`
- public raw rows / security identifiers: **none**

The one-shot binding consent and lower-level network consent were disabled again immediately after completion. Worker configuration was restored to preflight-only. The next safe internal step is network-free preparation of `PER_SECURITY_HISTORY`; its actual network execution remains separately unauthorized.


## PER_SECURITY_HISTORY network-free preparation

On 2026-10-03 KST, deployment `f683b1a2-5db6-4e95-81a7-6ec5889a2c59` at exact revision `ffe0e2c05e2a705c4b4cf06922600d07daa464cc` ran only `--prepare-per-security-history`.

It froze:
- total tasks: **14,296**
- `investor_trading_individual_daily`: **9,485**
- `trading_halt`: **4,811**
- task-set SHA-256: `fb5b883c6fe0e9c15e88aea9bdf874ddd7a11ae8a009c2ddf91c4e4249a8ba38`
- private manifest metadata SHA-256: `0d98f45168cedeecc013e95c71abe661ca1fac9df0403ba477d2f5653572c116`
- private manifest: `task_manifests/per-security-history-v3.json`
- phase: `PENDING`
- network requests attempted: **0**
- public raw rows / identifiers: **none**

The exact prepared scope is now code-pinned and execution-contract-pinned. `KRX_PER_SECURITY_HISTORY_CONSENT` remains disabled. Actual execution requires the separate exact approval `I_AUTHORIZE_INDEXALERT_KRX_PER_SECURITY_HISTORY_v1` in addition to the v3 bulk-network sentinel. No later-stage authority was created.
