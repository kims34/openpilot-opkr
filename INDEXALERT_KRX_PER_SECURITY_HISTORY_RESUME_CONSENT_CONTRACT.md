# IndexAlert KRX PER_SECURITY_HISTORY Resume Consent Contract v1

Contract ID: `INDEXALERT-KRX-PER-SECURITY-HISTORY-RESUME-CONSENT-v1`  
Current state: **FIX VERIFIED — WAITING FOR EXPLICIT USER AUTHORIZATION**

The original one-shot PER_SECURITY_HISTORY authority is consumed. Deployment `bc79d1b5-5fb8-46c7-8067-682e61947014` crashed because its executor incorrectly required decimal-only `isuCd2` values while the frozen PIT-safe planner correctly preserved official six-character ASCII alphanumeric short codes.

A network-free probe verified the private checkpoint at exactly **11,750 / 14,296 complete**, **2,546 remaining**, **0 failed**, phase `IN_PROGRESS`, with frozen task-set SHA-256 `fb5b883c6fe0e9c15e88aea9bdf874ddd7a11ae8a009c2ddf91c4e4249a8ba38`. The frozen task manifest is unchanged.

## Verified fix and preflight binding

The executor/planner short-code domain mismatch is fixed and frozen for resume preparation:
- verified code revision: `585d763542b2fbbdc3f928621f679fb14c8c3bbf`;
- Official KRX Status Integrity Action `37087007640`: **SUCCESS**;
- regression coverage includes official six-character ASCII alphanumeric `isuCd2` values and rejects malformed/non-ASCII forms;
- fresh preflight-only Railway deployment: `c1f875b2-4164-491a-9aaf-e6c5b2a387db`;
- deployment source revision: `585d763542b2fbbdc3f928621f679fb14c8c3bbf`;
- build definition: `Dockerfile.krx-historical-worker`;
- runtime mode: `PREFLIGHT_ONLY`;
- `network_request_attempted=false`;
- explicit execution consent absent and historical network execution unauthorized.

A frozen GitHub source branch `index-alert-krx-per-security-resume-v1` points exactly to the same verified revision (ahead 0 / behind 0). This prevents later development commits from silently changing the future resume code.

No resume execution deployment has been created or authorized. The future execution deployment must be fresh, must resolve to the frozen verified source revision, and must be bound into the machine consent contract only after the exact user authorization below is received.

## Resume authority

Resume requires a new explicit user message:

`I_AUTHORIZE_INDEXALERT_KRX_PER_SECURITY_HISTORY_RESUME_v1`

Until that exact message is received, `resume_network_execution_authorized=false`.

The old bulk/per-security sentinels cannot by themselves authorize resume. A future authorized resume may use them only as technical runtime gates under this new resume authority.

## Mandatory resume binding

Before network resume:
- the alphanumeric short-code fix and regression tests must pass the full Official KRX CI;
- the exact checkpoint must still be 11,750 complete / 2,546 remaining / failed=0;
- frozen task count/fingerprint/private-manifest hash must match;
- a **fresh** deployment must be created from the post-fix source revision;
- that exact source revision and fresh deployment ID must be written into this contract;
- `KRX_PER_SECURITY_HISTORY_RESUME_CONSENT` must equal the exact resume sentinel;
- the existing crashed deployment must not be redeployed/reused.

After exact 14,296/14,296 completion or any failure, all execution consent values must be disabled again and the worker returned to preflight-only.

This contract never authorizes STATUS_ECONOMICS, expected-scope execution, feature-performance testing, sealed holdout, Shadow S1, genuine LIVE, or real-account ordering.


## Frozen execution-source provenance

A future authorized resume deployment is valid only when Railway deployment metadata directly proves both:
- required execution source branch: `index-alert-krx-per-security-resume-v1`;
- required execution commit SHA: `585d763542b2fbbdc3f928621f679fb14c8c3bbf`.

The deployment must be fresh and must not reuse crashed deployment `bc79d1b5-5fb8-46c7-8067-682e61947014`.

Before the contract may transition to `USER_AUTHORIZED_RESUME_READY` or `RESUME_EXECUTION_IN_PROGRESS`, the runtime-gate record must bind:
- the new deployment ID;
- `deployment_branch=index-alert-krx-per-security-resume-v1`;
- `deployment_commit_sha=585d763542b2fbbdc3f928621f679fb14c8c3bbf`;
- `deployment_source_verified=true`.

A preflight or execution deployment from moving branch `index-alert-research-v1`, even if otherwise green, cannot satisfy this execution-source gate. This branch/SHA binding is independent of the resume consent phrase and does not grant network authority by itself.
