# Kiwoom REAL 8050 — registered-PC route comparison

**Diagnostic only; no live-trading authority or evidence of a resolved 8050.**

The registered-IP Windows PC previously received a successful REAL OAuth token and REST account response, then WebSocket LOGIN `805004 / 8050`. Kiwoom support reportedly confirmed the account's configuration was normal. Railway's earlier token-stage 8050 is a separate problem.

## What the diagnostic checks

The script `kiwoom_readonly_route_compare.py` is designed **only for the owner's already-registered-IP local PC**. It requires both this script and `kiwoom_real_type00_readonly_smoke.py` together in the same directory. It uses existing local environment credentials, and refuses to run unless `KIWOOM_ENV=REAL`, `KIWOOM_BASE_URL=https://api.kiwoom.com`, and `KIWOOM_ORDERING_ENABLED=false`.

On that PC, once the existing Python dependencies are available, execute from the isolated local directory:

```powershell
python -B kiwoom_readonly_route_compare.py
```

It issues a **single fresh OAuth token and one read-only REST account lookup**, then tries WebSocket LOGIN / Type00 REG on the **system-selected route**. Only when REST succeeded and a WebSocket login/connection blocker occurred does it try **one** additional direct WebSocket connection (`proxy=None`) using the **exact same in-memory token and account identity**, without a second OAuth issuance or account lookup. Thus the two WS paths can be compared without token reissue confounding. No tokens or account identifiers are written to files or displayed. It never sends buy/sell/cancel orders, moves funds, changes account settings, opens holdout, or configures Railway.

Only stages, numeric error/detail codes, boolean proxy configuration indicators and an assessment are emitted. Secret keys, token, account number, IP addresses, proxy URLs, original provider messages and subprocess stderr are never printed. Do not share those secrets separately.

## Interpretation

- `REST_PRECONDITION_NOT_MET`: Token or read-only account lookup failed; no direct comparison attempted.
- `8050_PERSISTS_IN_BOTH_WS_MODES`: Both routes reached WS LOGIN and got the same authentication failure; this does not establish the exact backend cause.
- `ROUTE_DEPENDENT_OUTCOME_POSSIBLE`: The direct route reached WS login success when the system route could not. This suggests a routing difference without proving any particular source IP.
- `WS_LOGIN_ALREADY_OK_NO_ROUTE_COMPARISON`: The system route already logged in successfully; direct mode was not attempted.
- `DIFFERENCE_INCONCLUSIVE`: Compare the two non-sensitive stage/error summaries before concluding.

**Important**: `broker_connected=true` is not proof of profitability, genuine fills or Tiny Live readiness. Type00 REG ACK with no events remains inconclusive. Automated and CI runs mock out the broker; no online test was performed by creating this tool.

Only the final `assessment` and `system/direct.STAGE`, `RETURN_CODE`, and `DETAIL_CODE` are needed for an escalation. Do not retry indefinitely. Keep all ordering disabled. The owner must explicitly authorize real trading separately.

## Downloadable Windows ZIP (no credentials included)

GitHub Actions workflow **Kiwoom REAL Type00 Python Readonly** uploads **five allowlisted source files directly** into artifact `kiwoom-readonly-pc-diagnostic` after offline validation. Download it from the latest **successful** workflow run on Draft PR #415, then unzip **once** on the already registered Windows PC: `RUN_KIWOOM_READONLY_DIAG.cmd` must be visible directly in the extracted folder, alongside the two Python scripts. CI downloads the uploaded artifact again and checks the exact five-file layout and byte-for-byte source integrity. No scripts run automatically on download/unzip.

From an existing terminal session in which your REAL credentials are already securely configured, enter the unzipped folder and run:

```cmd
RUN_KIWOOM_READONLY_DIAG.cmd
```

If Python cannot import dependencies, install the exact pinned versions first (once) using your existing trusted Python environment:

```cmd
py -3 -m pip install -r kiwoom_readonly_pc_requirements.txt
```

The launch script does **not** create or retrieve API keys; if the current shell does not have credentials, it safely exits without broker requests. It does **not** turn on order submission or modify any permissions. Avoid double-clicking unless those same secret-bearing environment variables are already available in that session. Use only one controlled read-only run; repeated retries are not required. Never share full environment output, IPs, provider raw messages, tokens, or credentials.
