# IndexAlert KRX Identity Standard-Code Binding Consent Contract v1

Updated: 2026-10-02 KST  
Contract ID: `INDEXALERT-KRX-IDENTITY-BINDING-CONSENT-v1`  
Stage: `IDENTITY_STANDARD_CODE_BINDING`  
Status: **FROZEN — USER-AUTHORIZED ONCE; EXECUTION COMPLETE; AUTHORITY CONSUMED**

## Purpose

This contract isolates the second historical-acquisition network stage from the already-completed 27-request `IDENTITY_SEED`.

The prior approval `I_AUTHORIZE_INDEXALERT_KRX_HIST_ACQ_v3` was consumed for the seed stage and cannot by itself authorize identity binding.

## Frozen prerequisite

Canonical seed evidence:
- evidence ID: `INDEXALERT-KRX-HIST-IDENTITY-SEED-2026-10-02-v1`
- seed phase: `COMPLETE`
- completed requests: **27/27**
- private batch metadata SHA-256: `054a9689adac7f57fa5a797f10ff9a69d3a7abd34a8697b624464588c6f0502f`

The private seed objects remain on the dedicated Railway volume and are not copied into GitHub.


Network-free preparation is also complete and frozen:
- prepared request count: **145**
- request kind: `security_master` = **145**
- prepared task-set SHA-256: `b3e9c845d74b0b479af0fd95d9015de92697fbd82b7bf07f9765378dfafd11d9`
- private task-manifest metadata SHA-256: `940f446caec81dd1a4a7b3a01053ae3f6a6ef6c79654e23bf2b971dca3622a6c`
- canonical public evidence: `INDEXALERT_KRX_IDENTITY_BINDING_PREPARATION_EVIDENCE.md/.json`
- network requests during preparation: **0**

## Authorization record

The user supplied the exact one-shot approval phrase on 2026-10-03 KST:

`I_AUTHORIZE_INDEXALERT_KRX_IDENTITY_BINDING_v1`

That authority was consumed by deployment `3501cbb8-a6a6-4972-bf82-4fb8e3fb36f6`, which completed the frozen 145-task stage. It is no longer active and cannot be reused. Canonical execution evidence is `INDEXALERT_KRX_IDENTITY_BINDING_EXECUTION_EVIDENCE.md/.json`.

## Runtime gate

The binding worker requires **both**:
- `KRX_HISTORICAL_ACQUISITION_CONSENT=I_AUTHORIZE_INDEXALERT_KRX_HIST_ACQ_v3`
- `KRX_IDENTITY_BINDING_CONSENT=I_AUTHORIZE_INDEXALERT_KRX_IDENTITY_BINDING_v1`

The first value is the lower-level historical-network preflight sentinel. The second is the stage-specific authority. Possessing only the first value is insufficient.

Authorized entrypoint for this stage only:

`python research_v1_krx_historical_worker_entrypoint.py --execute-identity-standard-code-binding`

## Allowed scope after explicit approval

Approval authorizes only:
- deriving the frozen identity-binding task set from the completed private seed;
- issuing the exact listing-date security-master requests required by that task set;
- storing raw response bytes only in the existing dedicated private content-addressed volume;
- writing metadata-only phase/batch evidence;
- verified checkpoint/resume for this same frozen phase.

## Explicitly not authorized

This stage does **not** authorize:
- expected-scope execution;
- `PER_SECURITY_HISTORY` execution;
- `STATUS_ECONOMICS` execution;
- investor-flow feature-performance testing;
- Core/Champion promotion;
- sealed holdout;
- Shadow S1;
- genuine LIVE execution;
- real-account order submission.

## Post-run lock

After a successful one-shot binding run:
- both execution consent values must be disabled again;
- worker start command must return to network-free preflight;
- the binding evidence must record counts/hashes only;
- no raw KRX row or credential may enter GitHub or public logs;
- no later stage becomes authorized automatically.


## Completed execution record

- exact source revision: `6c152d8f29354d843b16c35be27a86a8a8058908`
- completed requests: **145/145**
- resumed: **0**
- network requests attempted: **145**
- phase: `COMPLETE`
- execution batch metadata SHA-256: `d5ca4e7ea45033f6bd6d45e301f1d3041b2e7257836e60d71c442fa73d8013be`
- raw rows emitted publicly: **false**

Both execution consent values were disabled again and the worker was restored to preflight-only immediately after completion. No later-stage authority was created.
