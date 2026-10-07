# Private required-input inventory — 2026-10-07

User-directed continuation: locate the required inputs autonomously, without repeating owner file/authentication requests.

## Observed result

A one-shot read-only command ran on each existing pinned worker and inspected its mounted filesystem. This resolves the earlier limitation that only inventory/config/logs had been checked. It does not authenticate sources or admit any dataset.

| Existing store | Inventory execution | Counted files outside excluded paths | JSON metadata parsed | Relevant candidates |
|---|---|---|---|---|
| KRX worker /data | 362ace0b-3b84-41e7-bd11-a0748d5d733f, SUCCESS; output 2026-10-07T11:47:37Z | 43,496 JSON files | 500 | 0 |
| PIT worker /pit | 75a57387-bc2d-4582-a110-0dd64497c541, SUCCESS; output 2026-10-07T11:47:02Z | 23 Parquet files, 2 JSON files | 2 | 0 |

Candidates were defined by original field names (source/scope-contract fingerprints, decision timestamp, protocol ID, approval/document SHA, available_at/published_at), or filenames containing prospective, fresh_alpha, source_contract, approval, authorization, scope_contract. Only metadata keys/hash/counts would be emitted; no values, security identifiers or raw rows were emitted. There were no candidates under this bounded inspection.

Limits: ordinary JSON contents were capped at 500 files per store; qualifying filenames could bypass that cap. Nested keys were limited to depth six and the first 30 list elements. Files over 2 MiB and symlinks were not read. Traversal excluded holdout-named paths and raw/raw_objects/objects/.git directories; holdout contents, raw-object contents and Parquet contents were never read. The 100,000-file traversal limit was not reached. These results do not prove that no differently named producer/record or external original document exists, and do not establish a true prospective observation count of zero.

Disposition remains ACTUAL_CAPTURE_AND_STORAGE_NOT_VERIFIED / ORIGINAL_SOURCE_BINDING_UNRESOLVED. Existing historical files and metadata are not automatically eligible future observations, historical availability evidence, or an independent source approval. No model was fitted/executed and no historical or future market data acquisition was attempted by the audit command.

## Execution and restoration

The commands used Python -S -B and standard-library filesystem/JSON operations only. No database/file mutation, orders, funds movement, broker permissions, source admission, performance evaluation or holdout evaluation occurred.

Existing source pins were preserved:
- KRX ef95e7857f692fda3855390e918e165487624881
- PIT 26f56e63c3f30a6f8e02695ce9a4eb7b4ac3fe15

The first redeploys, 910a19a6-cd30-4754-a833-c0fb2096536e and 7785480e-fa87-4c45-936b-51530ef770c2, retained their original deployment commands; they did not run the requested inventory. The actual inventory executions above were triggered by committing exactly two staged start-command changes. No unrelated service/config change was staged.

Both service configurations were restored to their original start commands and restartPolicyType=NEVER after the inventory:
- KRX: python -S -B research_v1_krx_readonly_integrity_audit.py
- PIT: python -S -B audit_retired_validation.py

Final describe-service verified unchanged source pins and restored commands. Environment health verified both workers running=0/crashed=0, production runtime running=1/crashed=0, no pending work and no recent deployment failures. The settled one-shot deployment snapshots remain the inventory executions; restored commands apply to future deployments. Production runtime was not redeployed.

## Next required input

An independently verifiable original source/approval and PIT availability path, plus the original frozen-policy producer/record specification, remains necessary before capture integration. Do not create guessed trust roots or treat current probability output as the frozen H5 producer. Do not replay historical data to manufacture prospective records. No repeat inventory or speculative integrity patch is warranted without new evidence or an actionable required integration gap.
