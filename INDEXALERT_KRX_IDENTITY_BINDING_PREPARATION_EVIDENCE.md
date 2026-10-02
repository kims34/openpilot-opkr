# IndexAlert KRX Identity Standard-Code Binding Preparation Evidence

Updated: 2026-10-02 KST  
Evidence ID: `INDEXALERT-KRX-IDENTITY-BINDING-PREP-2026-10-02-v1`  
Stage: `IDENTITY_STANDARD_CODE_BINDING`  
Status: **PREPARED — NETWORK EXECUTION NOT AUTHORIZED**

## Network-free preparation

- Railway service: `indexalert-krx-historical-worker`
- Deployment: `6d0081a8-933b-4e2e-bd83-4753d2a75799`
- Exact source revision: `ab09e9a0aabf5bcaba53372b6f48b34796715e5d`
- Build: `Dockerfile.krx-historical-worker`
- Mode: `PREPARE_IDENTITY_STANDARD_CODE_BINDING`
- Prepared task count: **145**
- Task kind: `security_master` = **145**
- Task-set SHA-256: `b3e9c845d74b0b479af0fd95d9015de92697fbd82b7bf07f9765378dfafd11d9`
- Private manifest metadata SHA-256: `940f446caec81dd1a4a7b3a01053ae3f6a6ef6c79654e23bf2b971dca3622a6c`
- Private manifest relpath: `task_manifests/identity-standard-code-binding-v1.json`
- Phase status: `PENDING`
- Phase complete: **false**
- Network requests attempted: **0**
- Security identifiers emitted publicly: **false**
- Raw rows emitted publicly: **false**

The task list itself remains on the dedicated private Railway volume. This public evidence contains counts and hashes only.

## Authority boundary

Preparation does not authorize execution. The previous 27-request `IDENTITY_SEED` approval is not reusable for this stage.

Actual binding execution requires both frozen runtime sentinels:
- `KRX_HISTORICAL_ACQUISITION_CONSENT=I_AUTHORIZE_INDEXALERT_KRX_HIST_ACQ_v3`
- `KRX_IDENTITY_BINDING_CONSENT=I_AUTHORIZE_INDEXALERT_KRX_IDENTITY_BINDING_v1`

The exact stage-specific user approval phrase remains:

`I_AUTHORIZE_INDEXALERT_KRX_IDENTITY_BINDING_v1`

It has **not** been supplied in this preparation record.

After preparation, the Railway start command was restored to network-free preflight-only. Expected-scope, per-security history, status-economics execution, feature-performance testing, sealed holdout and live trading remain unauthorized.
