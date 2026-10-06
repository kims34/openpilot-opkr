# Deferred user-operated validations

User-operated broker checks may be deferred until the owner says they are available. Independent development must continue instead of repeatedly prompting for local PowerShell execution.

Completed:
- `KIWOOM_REAL_ACCOUNT_SCOPE_READONLY_v1` — completed 2026-10-07 with a successful redacted REAL whole-account read-only scope summary. Evidence: `INDEXALERT_KIWOOM_REAL_ACCOUNT_SCOPE_EVIDENCE_2026-10-07.md`.

Current pending items:
- `KIWOOM_REAL_TYPE00_READONLY_v1` — **BLOCKED_EXTERNAL_DEVICE_AUTH**. 2026-10-07 user-operated read-only smoke proved TOKEN_OK=true, ACCOUNT_ENDPOINT_OK=true and WS_CONNECTED=true, then broker LOGIN failed with RETURN_CODE=805004 / embedded DETAIL_CODE=8050 / ERROR_CLASS=DEVICE_AUTH. Evidence: `INDEXALERT_KIWOOM_REAL_TYPE00_EVIDENCE_2026-10-07.md`. Re-run only after the owner resolves Kiwoom designated-device authentication. A live execution event is not required for LOGIN/REG connectivity, and lack of an event must not be mislabeled as failed execution provenance.

Rules:
- Completion of a user validation does not authorize inference of any separate PASS.
- It does not by itself establish durable journal binding, genuine LIVE provenance, settlement admission, Shadow admission, or trading authority.
- Independent code, tests, CI, offline fault replay, contracts and research work continue without repeated prompts.
- Real orders, funds movement and broker permission changes always remain separately authorized actions.
- The tracker itself has no network, credential or execution capability.
