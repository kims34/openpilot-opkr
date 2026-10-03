# IndexAlert KRX PER_SECURITY_HISTORY interruption evidence

Evidence ID: `INDEXALERT-KRX-PER-SECURITY-HISTORY-INTERRUPTION-2026-10-03-v1`

The original frozen 14,296-task PER_SECURITY_HISTORY run terminated on deployment `bc79d1b5-5fb8-46c7-8067-682e61947014` at source revision `9009c48a00394063c813d29219507ee2190ce09e`.

The public-safe root cause is an internal validator mismatch: the PIT-safe planner admitted official six-character ASCII alphanumeric short codes, but that executor revision accepted decimal digits only. No raw security identifier is published here.

A later network-free aggregate status deployment `92439b24-644a-4d3d-a888-9e0ba568bfac` at source revision `d156f0dc6056924a798679bd9e93e1f2eb0241fc` verified:
- expected tasks: **14,296**
- completed checkpoint: **11,750**
- remaining: **2,546**
- failed: **0**
- phase: **IN_PROGRESS**
- phase_complete: **false**
- frozen fingerprint: `fb5b883c6fe0e9c15e88aea9bdf874ddd7a11ae8a009c2ddf91c4e4249a8ba38`
- status-probe network requests: **0**
- raw rows / security identifiers emitted: **false**

The original one-shot authority is consumed. Both execution consent values are disabled again, the configured worker start command is restored to preflight-only, restart policy remains NEVER, and no later protected stage is authorized.

A resume may only use the exact frozen scope and preserved checkpoint semantics, a CI-validated patched source revision, and a **new explicit user authorization** before any network request resumes. The exact required resume phrase is `I_AUTHORIZE_INDEXALERT_KRX_PER_SECURITY_HISTORY_RESUME_v1`, and runtime additionally requires `KRX_PER_SECURITY_HISTORY_RESUME_CONSENT` to equal that sentinel.
