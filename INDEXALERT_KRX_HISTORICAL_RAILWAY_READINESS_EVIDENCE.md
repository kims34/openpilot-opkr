# IndexAlert KRX Historical Railway Readiness Evidence

Updated: 2026-10-02 KST  
Evidence ID: `INDEXALERT-KRX-HIST-WORKER-RAILWAY-READINESS-2026-10-02-v1`  
Status: **READ-ONLY AUDIT COMPLETE — DEDICATED WORKER/VOLUME ABSENT**

A read-only Railway inspection of project `IndexAlert` / production found:

- `indexalert-runtime` exists and already owns a volume mounted at `/data`;
- `indexalert-backend`, `indexalert-push`, `db-query-readonly`, and `verify-deployment-status` do not provide the required dedicated historical-worker volume boundary;
- no service named `indexalert-krx-historical-worker` exists;
- no dedicated historical-worker volume is present.

The production runtime's existing `/data` volume must **not** be reused for KRX historical raw storage. The frozen execution/deployment contracts require a new isolated one-shot worker and a separate persistent volume.

Required future shape:
- service: `indexalert-krx-historical-worker`
- branch: `index-alert-research-v1`
- Dockerfile: `Dockerfile.krx-historical-worker`
- no public domain
- restart policy: NEVER
- dedicated volume mount: `/data`
- private raw root: `/data/indexalert/krx-historical-v3`

Current verdict:
- infrastructure ready for bulk execution: **false**
- service creation authorized: **false**
- volume creation/attachment authorized: **false**
- bulk historical network execution authorized: **false**

This audit performs no deployment, creates no service/volume, and makes no KRX network request.
