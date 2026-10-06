# Deferred user-operated validations

User-operated broker checks are intentionally deferred until the owner says they are available to run them. Independent development must continue instead of repeatedly prompting for local PowerShell execution.

Current pending item:
- `KIWOOM_REAL_ACCOUNT_SCOPE_READONLY_v1` — run `kiwoom_real_account_scope_readonly_smoke.ps1` when the owner explicitly says local work can resume.

Rules:
- Pending user validation does not authorize inference of a PASS.
- It does not block unrelated code, tests, CI, offline fault replay, contracts or research work.
- Do not repeatedly prompt the owner while local work is deferred.
- Real orders, funds movement and broker permission changes always remain separately authorized actions.
- The tracker itself has no network, credential or execution capability.
