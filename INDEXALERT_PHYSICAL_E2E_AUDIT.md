# IndexAlert Android Push Physical E2E Audit

Updated: 2026-10-01 KST

## Result

**PHYSICAL_E2E_CONFIRMED** for Android build `4.7-47` against Railway production server revision `d8523810b1c2c092a9ffc8f6245586e3bb719645`.

This audit closes only the Android notification physical-delivery plumbing blocker. It is not Alpha evidence, does not authorize live orders, does not authorize sealed-holdout use, and does not relax any KRX/source/execution/promotion gate.

## Audited Android build

- Branch: `index-alert-build`
- Commit: `5154ef7943353791f615622394523ecd52ef8b0f`
- `versionName=4.7`
- `versionCode=47`
- `client_build=4.7-47`
- APK Action: `36856589300` — SUCCESS
- Debug artifact: `IndexAlert-v4.7-debug`, artifact ID `11158994269`
- Debug SHA256: `0aec298a0d0276f8a5e40dc22429b595e8bb11636f22ceeea75cb018a4a7e411`

The v4.7 client sends `client_build` on `/register`, bootstraps `/push-self-test` on the confirmed registration path, and considers the self-test complete only after the server has observed the real privacy-safe handset `/push-ack` for that event.

## Registration incompatibility found and fixed during physical audit

The first real v4.7 installation reached production market endpoints normally, but repeated `POST /register` requests returned HTTP 400.

Root cause: the base server registration validator requires the `enabled_levels` key set to match `monitor.RULES` exactly. Production has display-only rules with no alert thresholds, including `usdkrw`, while the Android client transmits user-configurable alert rules plus the legacy KOSPI display key. The otherwise valid v4.7 payload therefore failed exact-key validation.

Fix:
- `push_build_registration.py` now fills **only** missing server-side rules whose `levels` are empty.
- alert-bearing rules are never synthesized; missing/unknown alert rules still fail closed in the established validator.
- regression coverage was added in `test_push_build_registration.py`.

Validated server commit:
`d8523810b1c2c092a9ffc8f6245586e3bb719645` (`Test v4.7 registration with display-only server rules`).

Server Tests Action `36874615526` completed SUCCESS.

## Railway production rollout

- Service: `indexalert-runtime`
- Deployment: `4cde730b-2aca-49c2-9950-f895897fe642`
- Branch: `index-alert-server`
- Exact deployed commit: `d8523810b1c2c092a9ffc8f6245586e3bb719645`
- Deployment status: SUCCESS
- Runtime entrypoint remains `production_v32:app`.

v32 Build Contract Smoke Action `36874615527` completed SUCCESS on the exact production revision.

## Real handset evidence

After the fixed production revision became live, the real Android handset performed the following production requests in order:

1. `POST /register` — HTTP 200
2. `POST /push-self-test` — HTTP 200
3. follow-up `POST /push-self-test` — HTTP 200 while receipt state was being reconciled
4. real handset `POST /push-ack` — HTTP 200

The requests came from the same observed Android handset session/user agent. Provider-send success alone was not used as delivery proof.

## Final privacy-safe server attestation

A fresh v32 production smoke after the real handset ACK reported:

- `runtime_revision = "d8523810b1c2c092a9ffc8f6245586e3bb719645"`
- `registration_build_contract = "register-client-build-v1"`
- `self_test_trigger_contract = "android-register-direct-v1"`
- `physical_e2e_binding_contract = "registered-device-build-receipt-v1"`
- `physical_e2e_blocker_contract = "physical-e2e-blocker-v1"`
- `physical_e2e_blocker = "CONFIRMED"`
- `latest_registered_client_build = "4.7-47"`
- `latest_self_test_build = "4.7-47"`
- `registration_device_matches_self_test = true`
- `registration_build_matches_self_test = true`
- `current_build_physical_e2e_confirmed = true`

The server also requires the exact latest registered device, exact build, sent self-test and real receipt-confirmed ledger state. Same-build evidence from another device, an older-build receipt, or a newer legacy/unknown-build registration fail closed.

Raw FCM tokens and event IDs remain private and are not exposed by `/push-health`.

## Boundary

Physical notification E2E is now **DONE** for the audited v4.7-47 build and exact production revision above.

Still OPEN and independent:
- KRX source gates / approved historical data / PIT and use-rights evidence;
- exact halt/cleanup/delisting execution/recovery economics;
- genuine LIVE execution evidence and separately preregistered empirical sufficiency criteria;
- sealed one-shot holdout;
- Shadow S1 and Fresh Confirmation S2;
- model promotion and live-order authority.
