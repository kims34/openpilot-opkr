# Deferred user-operated validations

User-operated broker checks may be deferred until the owner says they are available. Independent development must continue instead of repeatedly prompting for local PowerShell execution.

Completed:
- `KIWOOM_REAL_ACCOUNT_SCOPE_READONLY_v1` — completed 2026-10-07 with a successful redacted REAL whole-account read-only scope summary. Evidence: `INDEXALERT_KIWOOM_REAL_ACCOUNT_SCOPE_EVIDENCE_2026-10-07.md`.

Current pending items:
- `KIWOOM_REAL_TYPE00_READONLY_v1` — `kiwoom_real_type00_readonly_smoke.ps1`; verifies REAL WebSocket LOGIN + read-only type00 registration. It is intentionally deferred until the owner says local actions can resume. A live execution event is not required for LOGIN/REG connectivity, and lack of an event must not be mislabeled as failed execution provenance.

Rules:
- Completion of a user validation does not authorize inference of any separate PASS.
- It does not by itself establish durable journal binding, genuine LIVE provenance, settlement admission, Shadow admission, or trading authority.
- Independent code, tests, CI, offline fault replay, contracts and research work continue without repeated prompts.
- Real orders, funds movement and broker permission changes always remain separately authorized actions.
- The tracker itself has no network, credential or execution capability.
