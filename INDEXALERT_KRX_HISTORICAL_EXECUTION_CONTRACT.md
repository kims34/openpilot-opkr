# IndexAlert KRX Historical Execution Contract v3

Updated: 2026-10-02 KST  
Contract ID: `INDEXALERT-KRX-HIST-EXEC-v3`  
Bound acquisition plan: `INDEXALERT-KRX-HIST-ACQ-v3`  
Status: **IDENTITY_SEED ONE-SHOT COMPLETED — FURTHER NETWORK EXECUTION NOT AUTHORIZED**

## Purpose

This contract governs the future full-history KRX network job. It exists because the repository is public and the KRX permission explicitly prohibits external leakage, sale and third-party distribution.

Rights to acquire history are established, but those rights do not make the network job self-starting. Existing production `/data` volume does not satisfy this isolation requirement by itself; the bulk job must have its own dedicated worker execution identity.

## Isolation

Bulk acquisition must run in a dedicated one-shot worker. The exact worker role must be `INDEXALERT_KRX_HIST_WORKER_ROLE=DEDICATED_ONE_SHOT`. If `RAILWAY_SERVICE_NAME` identifies `indexalert-runtime`, `indexalert-backend` or `indexalert-push`, preflight must fail even when credentials, storage and consent are otherwise valid. The production public web process must never run the bulk job.

Before any network request the worker must pass the exact network-free v3 historical-acquisition preflight bound to execution contract v3, including the exact execution sentinel:

`I_AUTHORIZE_INDEXALERT_KRX_HIST_ACQ_v3`

The prior tiny-probe consent does not satisfy this bulk execution gate.


## Consumed one-shot authorization record

On 2026-10-02 KST, the exact v3 execution sentinel was explicitly supplied for the **27-request `IDENTITY_SEED` stage only**. Deployment `d268e5b0-b7c2-46be-b9ae-ca41d27cdb02` at source revision `6343f01b493404d59736e06eb6968e9820d0e595` completed 27/27 preregistered requests with phase `COMPLETE`, zero resumes and `raw_rows_emitted=false`. Canonical sanitized evidence is `INDEXALERT_KRX_HISTORICAL_IDENTITY_SEED_EXECUTION_EVIDENCE.md/.json`.

That one-shot execution authority was consumed and the exact sentinel was disabled immediately after completion. The worker was restored to its network-free preflight start command. Current machine-contract authority therefore remains `bulk_network_execution_authorized_by_user=false`.


For the next protected stage, `IDENTITY_STANDARD_CODE_BINDING`, the historical-network sentinel is necessary but no longer sufficient. The worker additionally requires the frozen stage-specific sentinel `I_AUTHORIZE_INDEXALERT_KRX_IDENTITY_BINDING_v1` in `KRX_IDENTITY_BINDING_CONSENT`. The exact task set must first be generated network-free and frozen in a private manifest. Canonical authority is `INDEXALERT_KRX_IDENTITY_BINDING_CONSENT_CONTRACT.md/.json`.

This completed seed does **not** authorize `IDENTITY_STANDARD_CODE_BINDING`, expected-scope execution, per-security history, status-economics execution, feature-performance testing, sealed holdout, promotion or live trading. Each protected later network stage requires its own current authorization boundary.


The later historical network stages are also independently gated:
- `PER_SECURITY_HISTORY`: after binding is complete, its exact private task set must first be prepared network-free; execution additionally requires `KRX_PER_SECURITY_HISTORY_CONSENT=I_AUTHORIZE_INDEXALERT_KRX_PER_SECURITY_HISTORY_v1`.
- `STATUS_ECONOMICS`: after per-security history is complete, its exact private cleanup-price task set must first be prepared network-free; execution additionally requires `KRX_STATUS_ECONOMICS_CONSENT=I_AUTHORIZE_INDEXALERT_KRX_STATUS_ECONOMICS_v1`.

Neither stage may reuse an earlier stage-specific approval. Completion of `STATUS_ECONOMICS` still cannot claim exact realized fill/recovery economics.

## Private raw storage

Raw KRX response bytes must be written only to a private persistent volume configured by `KRX_PRIVATE_RAW_DIR`.

Recommended private root:

`/data/indexalert/krx-historical-v3`

Required protections:
- absolute path;
- never inside the Git worktree;
- never under a public/static web directory;
- directories mode 0700;
- files mode 0600;
- content-addressed object naming by SHA-256;
- atomic temp-write + fsync + rename;
- no overwrite/delete of prior raw objects on retry;
- no raw upload to GitHub;
- no raw rows in Actions logs/artifacts.

## Exact raw-object binding

Every successful request must preserve **the raw response bytes before parsing**.

Each request must bind:
- raw response SHA-256;
- raw byte size;
- parsed DataFrame payload SHA-256;
- parsed schema SHA-256;
- canonical request-metadata SHA-256;
- timezone-aware retrieval timestamp;
- transport status;
- acquisition receipt fingerprint;
- metadata-only raw-object manifest.

The raw-object manifest may contain hashes/metadata only. It must never contain KRX credentials, cookies, session tokens, authorization headers or raw rows.

## Source-contract correction

Historical cleanup intervals must come from `MDCSTAT23801` delisted-history fields (`정리매매기간_시작일`, `정리매매기간_종료일`, `폐지일`, `폐지사유`). The authenticated `MDCSTAT23701` route is retained only as a current/ongoing cleanup-trading reconciliation snapshot with `mktId=ALL`.

The executor must **never** invent historical `strtDd/endDd` semantics for `MDCSTAT23701`. Plan v3 superseded plan v2 before any bulk network execution specifically to remove that unsupported assumption.

## Checkpoint/resume

A request is complete only when both exist and verify:
1. immutable content-addressed raw object;
2. matching metadata acquisition receipt.

Resume is allowed only from verified objects/receipts. If the same logical request later returns different bytes, the executor must retain both objects and fail reconciliation rather than overwrite the prior object.

Abort the batch on:
- authentication failure;
- schema drift;
- historical identity/standard-code mapping failure;
- receipt/hash mismatch;
- unsafe storage root.

## Public output

Only metadata may leave the private raw boundary: counts, timestamps, hashes, schema names/fingerprints, batch/receipt IDs, coverage/PIT summaries and sanitized error types.

Security-level numeric raw values or response rows are not public-log material.

## Authority

This contract does not close Gates C/D/E and does not authorize:
- feature-performance testing;
- sealed holdout;
- model promotion;
- live trading.

Those remain false until the completed private acquisition passes receipts/batches, exact historical coverage, PIT lineage and source-data admission.


## Frozen PER_SECURITY_HISTORY prepared scope

Network-free preparation completed on 2026-10-03 KST and is now part of this execution contract:
- exact prepared request count: **14,296**
- investor-flow daily: **9,485**
- trading-halt: **4,811**
- task-set SHA-256: `fb5b883c6fe0e9c15e88aea9bdf874ddd7a11ae8a009c2ddf91c4e4249a8ba38`
- private manifest metadata SHA-256: `0d98f45168cedeecc013e95c71abe661ca1fac9df0403ba477d2f5653572c116`
- private manifest: `task_manifests/per-security-history-v3.json`
- preparation network requests: **0**

`PER_SECURITY_HISTORY` execution must match this exact frozen scope and still requires both the v3 historical-network sentinel and the separate stage-specific approval `I_AUTHORIZE_INDEXALERT_KRX_PER_SECURITY_HISTORY_v1`. No later stage is authorized by this preparation.


## STATUS_ECONOMICS preparation lifecycle

`STATUS_ECONOMICS` remains a separately protected later network stage.

Before `PER_SECURITY_HISTORY` is complete and re-locked, the execution contract must remain in a **preparation shell**:
- `preparation_complete=false`;
- no prepared task count;
- no prepared task-set SHA-256;
- no prepared private-manifest metadata SHA-256;
- no preparation evidence binding;
- `currently_authorized=false`;
- `exact_status_economics_claim_allowed=false`.

Only after canonical `PER_SECURITY_HISTORY` completion evidence proves exact **14,296/14,296**, failed=0, frozen fingerprint match and post-run relock may the worker run the network-free `--prepare-status-economics` command.

A successful preparation may transition this contract only to **prepared scope frozen / execution not authorized**, and must then bind:
- canonical preparation evidence ID `INDEXALERT-KRX-STATUS-ECONOMICS-PREP-v1`;
- predecessor completion evidence ID `INDEXALERT-KRX-PER-SECURITY-HISTORY-EXEC-2026-10-03-v1`;
- positive exact prepared task count;
- exact task-set SHA-256;
- exact private task-manifest metadata SHA-256;
- private manifest `task_manifests/status-economics-v3.json`;
- preparation network requests = **0**.

Even after those values are frozen, execution remains blocked until the user separately supplies `I_AUTHORIZE_INDEXALERT_KRX_STATUS_ECONOMICS_v1`. Preparation cannot authorize exact fill/recovery economics, expected-scope network execution, feature-performance testing, sealed holdout, Shadow S1, genuine LIVE or real-account ordering.
