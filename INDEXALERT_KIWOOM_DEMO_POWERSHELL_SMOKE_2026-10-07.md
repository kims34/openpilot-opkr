# Kiwoom DEMO PowerShell read-only smoke — 2026-10-07 KST

Evidence class: **user-operated external DEMO connectivity / read-only only**

## Observed redacted result

The user ran the repository's PowerShell fallback against the Kiwoom DEMO host after the preceding DEMO OAuth token check succeeded. The retained result was:

```json
{"STAGE":"DEMO_READ_ONLY_SMOKE","FUNDS_MOVEMENT_AUTHORIZED":false,"GENUINE_LIVE_PROVENANCE_VERIFIED":false,"ORDERING":"DISABLED","ACCOUNT_ENDPOINT_OK":true,"PERMISSION_CHANGE_AUTHORIZED":false,"REAL_ORDERS_AUTHORIZED":false,"TOKEN_OK":true}
```

The script used the fixed DEMO host `https://mockapi.kiwoom.com` and only:
- `POST /oauth2/token`
- reviewed read-only account API `ka00001` at `/api/dostk/acnt`

No order-create, amend, cancel, revoke, funds-transfer, permission-change or REAL-account API was invoked by this smoke.

## Interpretation

This independently supplied user-operated result closes only the narrow DEMO token + reviewed account-endpoint connectivity check for the PowerShell fallback path.

It does **not** establish:
- real-account authentication or settlement evidence;
- genuine LIVE provenance;
- real-market execution/fill evidence;
- Shadow completion;
- source/PIT/status-economics closure;
- successor Alpha admission;
- Early-Live authorization;
- production/live order authority.

Current authority therefore remains fail-closed:
- `REAL_ORDERS_AUTHORIZED=false`
- `FUNDS_MOVEMENT_AUTHORIZED=false`
- `PERMISSION_CHANGE_AUTHORIZED=false`
- `GENUINE_LIVE_PROVENANCE_VERIFIED=false`

A prior REAL-host token attempt with the same locally held credential pair returned Kiwoom provider code 8030 indicating the credential's investment mode did not match REAL. No credential value was retained in project records.
