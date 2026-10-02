# IndexAlert KRX Historical Railway Readiness Evidence

Updated: 2026-10-02 21:27 KST  
Evidence ID: `INDEXALERT-KRX-HIST-WORKER-RAILWAY-READINESS-2026-10-02-v1`  
Status: **READ-ONLY AUDIT COMPLETE — DEDICATED WORKER/VOLUME ABSENT**

A read-only Railway inspection of project `IndexAlert` / production found:

- `indexalert-runtime` exists and already owns a volume mounted at `/data`;
- `indexalert-backend`, `indexalert-push`, `db-query-readonly`, and `verify-deployment-status` do not provide the required dedicated historical-worker volume boundary;
- no service named `indexalert-krx-historical-worker` exists;
- no dedicated historical-worker volume is present.

The production runtime's existing `/data` volume must **not** be reused for KRX historical raw storage. The frozen execution/deployment contracts require a new isolated one-shot worker and a separate persistent volume.

Worker-only secret names still required on that new service: `KRX_ID`, `KRX_PW`, `KRX_AUTH_KEY`. Required non-secret values are `KRX_PRIVATE_RAW_DIR=/data/indexalert/krx-historical-v3` and `INDEXALERT_KRX_HIST_WORKER_ROLE=DEDICATED_ONE_SHOT`.

Required future shape:
- service: `indexalert-krx-historical-worker`
- branch: `index-alert-research-v1`
- Dockerfile: `Dockerfile.krx-historical-worker`
- no public domain
- restart policy: NEVER
- dedicated volume mount: `/data`
- private raw root: `/data/indexalert/krx-historical-v3`

Initial provisioning must remain preflight-only: no public domain, no cron, restart policy `NEVER`, and the bulk consent variable must remain absent.

Current verdict:
- infrastructure ready for bulk execution: **false**
- service creation authorized: **false**
- volume creation/attachment authorized: **false**
- worker secret configuration authorized: **false**
- bulk historical network execution authorized: **false**
- expected-scope network execution authorized: **false**

This audit performs no deployment, creates no service/volume, and makes no KRX network request. The next external action is explicit authorization to provision the dedicated worker + volume only; bulk historical execution and expected-scope execution remain separate later consent gates.
