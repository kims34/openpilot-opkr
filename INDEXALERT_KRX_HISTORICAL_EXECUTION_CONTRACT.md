# IndexAlert KRX Historical Execution Contract v2

Updated: 2026-10-02 KST  
Contract ID: `INDEXALERT-KRX-HIST-EXEC-v2`  
Bound acquisition plan: `INDEXALERT-KRX-HIST-ACQ-v3`  
Status: **IMPLEMENTATION CONTRACT ONLY — BULK NETWORK EXECUTION NOT YET USER-AUTHORIZED**

## Purpose

This contract governs the future full-history KRX network job. It exists because the repository is public and the KRX permission explicitly prohibits external leakage, sale and third-party distribution.

Rights to acquire history are established, but those rights do not make the network job self-starting.

## Isolation

Bulk acquisition must run in a dedicated one-shot worker. The production public web process must not run the bulk job.

Before any network request the worker must pass the exact network-free v3 historical-acquisition preflight bound to execution contract v2, including the exact execution sentinel:

`I_AUTHORIZE_INDEXALERT_KRX_HIST_ACQ_v3`

The prior tiny-probe consent does not satisfy this bulk execution gate.

## Private raw storage

Raw KRX response bytes must be written only to a private persistent volume configured by `KRX_PRIVATE_RAW_DIR`.

Recommended private root:

`/data/indexalert/krx-historical-v2`

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
