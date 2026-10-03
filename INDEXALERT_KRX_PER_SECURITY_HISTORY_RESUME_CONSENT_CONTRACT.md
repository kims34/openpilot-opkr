# IndexAlert KRX PER_SECURITY_HISTORY Resume Consent Contract v1

Contract ID: `INDEXALERT-KRX-PER-SECURITY-HISTORY-RESUME-CONSENT-v1`  
Current state: **WAITING FOR EXPLICIT USER AUTHORIZATION**

The original one-shot PER_SECURITY_HISTORY authority is consumed. Deployment `bc79d1b5-5fb8-46c7-8067-682e61947014` crashed because its executor incorrectly required decimal-only `isuCd2` values while the frozen PIT-safe planner correctly preserved official six-character ASCII alphanumeric short codes.

A network-free probe verified the private checkpoint at exactly **11,750 / 14,296 complete**, **2,546 remaining**, **0 failed**, phase `IN_PROGRESS`, with frozen task-set SHA-256 `fb5b883c6fe0e9c15e88aea9bdf874ddd7a11ae8a009c2ddf91c4e4249a8ba38`. The frozen task manifest is unchanged.

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
