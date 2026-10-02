# IndexAlert KRX Historical Identity Seed Execution Evidence

Updated: 2026-10-02 KST  
Evidence ID: `INDEXALERT-KRX-HIST-IDENTITY-SEED-2026-10-02-v1`  
Plan: `INDEXALERT-KRX-HIST-ACQ-v3`  
Execution contract: `INDEXALERT-KRX-HIST-EXEC-v3`  
Status: **COMPLETE — 27/27 / METADATA ONLY**

## Execution

- User authorization sentinel received: `I_AUTHORIZE_INDEXALERT_KRX_HIST_ACQ_v3`
- Railway service: `indexalert-krx-historical-worker`
- Deployment: `d268e5b0-b7c2-46be-b9ae-ca41d27cdb02`
- Exact source revision: `6343f01b493404d59736e06eb6968e9820d0e595`
- Build: `Dockerfile.krx-historical-worker`
- Worker mode: `EXECUTE_IDENTITY_SEED`
- Task count: **27**
- Completed: **27**
- Resumed: **0**
- Network requests attempted: **27**
- Phase status: `COMPLETE`
- Phase complete: **true**

## Integrity metadata

- Task-set SHA-256: `fb69ed44c2944911417dc26f088f0c5876942530a7c17abdd1fc38ee3f197aa1`
- Private batch metadata SHA-256: `054a9689adac7f57fa5a797f10ff9a69d3a7abd34a8697b624464588c6f0502f`
- Private batch relpath: `batches/identity-seed-v3.json`
- Private raw root remains `/data/indexalert/krx-historical-v3`.

The worker reaches `COMPLETE` only after all preregistered task completions are recorded and each raw content-addressed object is verified by the batch-state path. Raw KRX rows, credentials, cookies and session material are not emitted into this evidence.

## Authority after completion

Immediately after the one-shot stage, the execution consent was disabled again and the service start command was restored to network-free preflight-only.

This evidence does **not** close source Gates C/D/E, does not authorize identity-standard-code binding, expected-scope execution, per-security history, status-economics execution, feature-performance testing, sealed holdout, model promotion, genuine LIVE, or live trading.

The next historical-acquisition stage is the separately controlled `IDENTITY_STANDARD_CODE_BINDING` stage derived from the private identity seed. It must not execute from this evidence alone.

## Safety incident / correction

Two attempted Railway `redeploy` paths were observed to use Railpack rather than the frozen worker Dockerfile. Both were forced to preflight-only before runtime and made **zero KRX network requests**. Root `railway.json` on `index-alert-research-v1` was then pinned to `Dockerfile.krx-historical-worker`. The successful network run was a fresh deployment from exact revision `6343f01b...` and its build logs showed the 12-step worker Dockerfile.
