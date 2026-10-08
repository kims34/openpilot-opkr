# Current Tiny Live user-validation override — 2026-10-08

Supersedes the stale DEVICE_AUTH item below.

- `KIWOOM_REAL_TYPE00_READONLY_v1`: **BLOCKED_USER_CREDENTIAL_REPLACEMENT**.
- PR #351 / `INDEXALERT_KIWOOM_RAILWAY_CREDENTIAL_MODE_EVIDENCE_2026-10-08.md` independently probed both isolated Railway read-only services: the stored credentials issue a DEMO token but REAL OAuth returns return_code=2 / detail_code=8030 / MODE_MISMATCH.
- Required user action: replace only `KIWOOM_APP_KEY` and `KIWOOM_APP_SECRET` in the isolated REAL read-only Railway service with broker-issued REAL OpenAPI credentials. Keep `KIWOOM_ENV=REAL`, `KIWOOM_BASE_URL=https://api.kiwoom.com`, `KIWOOM_ORDERING_ENABLED=false`.
- Never paste credentials into chat or GitHub.
- After replacement, rerun the existing one-shot read-only smoke. No order/funds/permission action is authorized.

---

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
