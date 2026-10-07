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
