# IndexAlert Android Push Physical E2E Audit

Updated: 2026-10-02 KST

## Result

**PHYSICAL_E2E_CONFIRMED** for Android build `4.7-47`.

The original real-handset delivery proof was established against Railway production server revision `d8523810b1c2c092a9ffc8f6245586e3bb719645`. After the execution-ledger provenance hardening rollout, the same persisted real-handset receipt evidence was independently re-read from current production revision `4491bceea722341af62ca2c5bf71fa34cd6d05b4` and again passed the frozen read-only verifier.

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

## Original Railway production rollout and real handset proof

- Service: `indexalert-runtime`
- Original audited deployment: `4cde730b-2aca-49c2-9950-f895897fe642`
- Branch: `index-alert-server`
- Original exact deployed commit: `d8523810b1c2c092a9ffc8f6245586e3bb719645`
- Deployment status: SUCCESS
- Runtime entrypoint remains `production_v32:app`.

v32 Build Contract Smoke Action `36874615527` completed SUCCESS on the original exact production revision.

After the fixed production revision became live, the real Android handset performed the following production requests in order:

1. `POST /register` — HTTP 200
2. `POST /push-self-test` — HTTP 200
3. follow-up `POST /push-self-test` — HTTP 200 while receipt state was being reconciled
4. real handset `POST /push-ack` — HTTP 200

The requests came from the same observed Android handset session/user agent. Provider-send success alone was not used as delivery proof.

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

## Current production revalidation after execution-ledger hardening

The server later advanced to canonical `index-alert-server` revision `4491bceea722341af62ca2c5bf71fa34cd6d05b4` to harden execution-evidence source-label semantics. This server change did not create a new handset ACK and must not be represented as a second physical-delivery event.

The new exact revision was validated independently before being treated as current production:

- Canonical Server Tests Action `36903663517` — SUCCESS on exact SHA `4491bceea722341af62ca2c5bf71fa34cd6d05b4`.
- Railway deployment `8752a2f5-137e-43fe-a5f9-6cf430e6588a` — SUCCESS on exact SHA `4491bceea722341af62ca2c5bf71fa34cd6d05b4`.
- Canonical Server Smoke Action `36903663733` — SUCCESS after production `/status` reported the same exact runtime revision.
- Read-only Physical E2E reverify Action `36904659864` — SUCCESS against current production.
- Reverify artifact: `indexalert-physical-e2e-4.7-47-reverify-4491bcee`, artifact ID `11182369446`, artifact digest `sha256:6489aa88fcbf1b490c0a5c829a8781ba21ba54ee63736d864a3418d655015135`.

The read-only reverify artifact reported:

- `expected_build = "4.7-47"`
- `physical_e2e_confirmed = true`
- `physical_e2e_blocker = "CONFIRMED"`
- `latest_registered_client_build = "4.7-47"`
- `latest_self_test_build = "4.7-47"`
- `registration_device_matches_self_test = true`
- `registration_build_matches_self_test = true`
- `latest_self_test_sent = true`
- `latest_self_test_receipt_confirmed = true`
- `current_build_physical_e2e_confirmed = true`
- `real_receipt_timestamp_present = true`
- `received_delivery_count_positive = true`

Observed privacy-safe state also retained the frozen contract markers `register-client-build-v1`, `android-register-direct-v1`, `registered-device-build-receipt-v1`, and `physical-e2e-blocker-v1`.

This is a **read-only persistence/rebinding verification** of the already-established real-handset receipt evidence under the new production revision. It does not manufacture a new receipt and does not turn provider-send success into handset evidence.

The server requires the exact latest registered device, exact build, sent self-test and real receipt-confirmed ledger state. Same-build evidence from another device, an older-build receipt, or a newer legacy/unknown-build registration fail closed.

Raw FCM tokens and event IDs remain private and are not exposed by `/push-health`.

## Boundary

Physical notification E2E is **DONE** for audited Android build `4.7-47`. The original physical-delivery event was proven on revision `d8523810b1c2c092a9ffc8f6245586e3bb719645`, and the persisted exact-device/exact-build receipt state has now been independently revalidated against current production revision `4491bceea722341af62ca2c5bf71fa34cd6d05b4`.

Still OPEN and independent:
- KRX source gates / approved historical data / PIT and use-rights evidence;
- exact halt/cleanup/delisting execution/recovery economics;
- genuine LIVE execution evidence and separately preregistered empirical sufficiency criteria;
- sealed one-shot holdout;
- Shadow S1 and Fresh Confirmation S2;
- model promotion and live-order authority.
