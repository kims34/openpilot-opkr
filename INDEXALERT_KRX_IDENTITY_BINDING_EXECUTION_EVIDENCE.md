# IndexAlert KRX Identity Standard-Code Binding Execution Evidence

Updated: 2026-10-03 KST  
Evidence ID: `INDEXALERT-KRX-IDENTITY-BINDING-EXEC-2026-10-03-v1`  
Stage: `IDENTITY_STANDARD_CODE_BINDING`  
Status: **COMPLETE — 145/145 / METADATA ONLY**

## Execution

- User stage authorization received: `I_AUTHORIZE_INDEXALERT_KRX_IDENTITY_BINDING_v1`
- Railway service: `indexalert-krx-historical-worker`
- Deployment: `3501cbb8-a6a6-4972-bf82-4fb8e3fb36f6`
- Exact source revision: `6c152d8f29354d843b16c35be27a86a8a8058908`
- Build: `Dockerfile.krx-historical-worker`
- Mode: `EXECUTE_IDENTITY_STANDARD_CODE_BINDING`
- Frozen task count: **145**
- Completed: **145**
- Resumed: **0**
- Network requests attempted: **145**
- Phase status: `COMPLETE`
- Phase complete: **true**

## Integrity metadata

- Frozen task-set SHA-256: `b3e9c845d74b0b479af0fd95d9015de92697fbd82b7bf07f9765378dfafd11d9`
- Private execution batch metadata SHA-256: `d5ca4e7ea45033f6bd6d45e301f1d3041b2e7257836e60d71c442fa73d8013be`
- Private execution batch relpath: `batches/identity-standard-code-binding-v3.json`
- Raw KRX rows, security identifiers, credentials and response bytes were not emitted into GitHub/public evidence.

## Post-run lock

Immediately after completion:
- `KRX_HISTORICAL_ACQUISITION_CONSENT` was disabled again;
- `KRX_IDENTITY_BINDING_CONSENT` was disabled again;
- worker start command was restored to network-free preflight-only;
- no later stage was authorized automatically.

This evidence does **not** authorize `PER_SECURITY_HISTORY`, `STATUS_ECONOMICS`, expected-scope execution, feature-performance testing, sealed holdout, genuine LIVE or real-account ordering.
