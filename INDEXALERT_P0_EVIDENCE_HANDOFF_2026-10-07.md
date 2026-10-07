# Owner-assisted broker verification — 2026-10-07 21:39 KST

The owner explicitly rescinded deferral and is available for required actions. Owner-provided screenshots show no application history in the displayed terminal-designation/additional-authentication/overseas-IP-blocking sections. The REST account App Key management screen shows the current PC IP matches a registered IP; this is scoped to that PC/network, not cloud egress or every broker security setting. No security setting, key, permission or IP registration was changed.

The owner reran the pinned read-only smoke script from development24c79cd4582ba71b53693f302caa9a359d090e57 (SHA25671524454eda194d71da895e24262cac7f6c48db11edf9a12a8f2e74de25ed8cd) and supplied the result at21:39KST:
- TOKEN_OK=true; ACCOUNT_ENDPOINT_OK=true; WS_CONNECTED=true.
- STAGE=WS_LOGIN; WS_LOGIN_OK=false; RETURN_CODE=805004; DETAIL_CODE=8050; ERROR_CLASS=DEVICE_AUTH.
- TYPE00_REG_SENT=false; TYPE00_REG_ACK_OK=false; both event counts0.
- ORDERING=DISABLED; real-orders/funds-movement/permission-change authorization=false.
- BROKER_NATIVE_EXECUTION_ID_CAPTURE_TESTED=false; GENUINE_LIVE_PROVENANCE_VERIFIED=false.

Disposition: broker WebSocket device-authentication blocker reproduced after current-PC registered-IP inspection. Do not repeat the same smoke without a relevant new fact/change. Official Kiwoom client classifies8050 as device authentication; the public electronic-fraud-prevention page describes certificate issuance restrictions and does not establish the remediation for this REST WebSocket failure. Exact applicable official error-code remediation remains to be verified before any owner security change. Whole-account baseline remains complete. Raw keys/account identifiers/IPs were not recorded.

Owner inputs still pending: applicable official8050 remediation; original KRX approval sender/date/body to compare with already-recorded HIST_ACQ_v3 scope (no repeat approval request); original Android signing-key backup availability (no private-key/password upload or repeat local search).

---

# Private-store inspection update — 2026-10-07 20:47 KST

Autonomous one-shot read-only inspection of the existing /data and /pit stores is now complete. See INDEXALERT_PRIVATE_INPUT_INVENTORY_2026-10-07.md for scoped counts, exclusions, execution IDs and restored configurations. The earlier statement that private files had not been read described the previous checkpoint and is superseded by this metadata-only inspection. Actual prospective capture and original source/PIT admission remain unverified; no new trust root, model or dataset admission was introduced.

---

# P0 evidence and real-observation handoff — 2026-10-07

Scope: delivery-critical inspection after the user's efficiency instruction. No new strategy experiment, holdout read, broker request/order or speculative hardening.

## Actual inspected state
- Development: d1503d419e2beb52950a3d9bd8f2ec30935f08d8; research: 194da5016ad3aecc2ceb25944666daa74f038083. No open PR observed.
- Production runtime remains pinned to 8a68b01bca5d551d083ccda263df38d86fa54166 / production_v32; Railway inventory has eight services, three existing mounted volumes, no staged changes.
- Existing KRX/PIT stopped one-shot deployments remain their 2026-10-05 audit deployments. No reexecution or mutation was performed.

## Critical finding: registration is not an active observation pipeline
Research protocol IA-FRESH-ALPHA-H5-TOP3-20261007 exists and is frozen. research_v1_fresh_alpha_protocol.py validates metadata and future timestamp eligibility; its module documentation explicitly says it cannot generate signals.
The current research tree contains the protocol, validator, tests and integrity workflow. The current workflow compiles/runs unit tests/validates the protocol only. Exact research-head integrity run37544288237 SUCCESS is not evidence of recorded market decisions.
The inspected deployed runtime tree contains the legacy probability_shadow.py and execution evidence ledger, but no fresh-alpha prospective module. The observed Railway inventory does not identify an active fresh-alpha recording service. No genuine fresh-alpha decision/outcome ledger was independently accessed.

Disposition: ACTUAL_CAPTURE_AND_STORAGE_NOT_VERIFIED. This is a scoped inspection, not a claim that no external producer exists or that the true observation count is zero.
Do not assume automatic accumulation, date a validation clock from registration alone, or estimate completion after126/504 sessions until actual eligible records are confirmed. Do not backfill earlier decisions to fill the gap. The probability shadow ledger and broker execution ledger are separate evidence domains, not substitutes for the exact frozen H5 diagnostic.

## P0 next actionable integration, with its input dependency
Locate the actual frozen H5 decision producer and private append-only observation store, or its original research-approved producer/record specification. Verify the producer implements the registered policy and supplies real decision-time data before connecting it to a recorder.
Needed inputs: exact producer source/model/policy identity; permitted real input dataset with original availability/PIT lineage; actual decision capture/storage location and timestamps. None of these may be inferred from unrelated public probability outputs or caller booleans.
With those inputs available, implement/verify live-time capture and durable storage without orders, then append outcomes only when actually available. This completes a required evidence path; another hypothetical SQLite-corruption patch does not.
No new capture schema/trust-root, model, threshold or source admission has been invented here.

## Source evidence path remains independently open
INDEXALERT_KRX_ORIGIN_BINDING_REVIEW.md already records unresolved original source-contract hash meaning, independent approval/raw/receipt/scope linkage and historical availability evidence.
Scoped Library searches returned no grounded original KRX/source-contract item; broad fuzzy unrelated results were not read. This is a retrieval limitation, not proof that no document exists.
Railway tools exposed inventory/config/logs, not authenticated private volume-file access/SSH. Original artifacts on /data or /pit were not copied, read or altered. Existing storage-integrity PASS cannot replace source/PIT/economics admission.
Do not regenerate source_contract_fingerprint_sha256 from a guessed task-set/batch/Git hash or backdate historical availability.

## Broker path and stopping rule
Whole-account read-only baseline COMPLETE, do not repeat. Real type00 DEVICE_AUTH805004/8050 remains owner-deferred. No repeated phone/PowerShell/key/permission request.
If a required original producer/source artifact becomes available, resume that integration first. If only external evidence/access or owner actions remain for the selected path, record the dependency and stop that path instead of performing cosmetic or speculative edits.
This inspection does not claim all independent engineering is exhausted. It does establish that current high-priority profitability evidence cannot be completed by another generic safety patch or an assumed running126-session observation process.
All Frozen/consumed invalid v1/Champion/admission rules unchanged; real orders, funds movement and account/broker permission authority remain false.
