# Tiny Live A/B/C override — 2026-10-08

## Later 2026-10-08 KST REAL authentication evidence (supersedes DEMO-key as CURRENT blocker)

Verified on the owner's registered-IP Windows machine, with the already available REAL credentials, a fresh user-operated **read-only** smoke:
- `TOKEN_OK=true`, `ACCOUNT_ENDPOINT_OK=true`, `REST_ACCOUNT_ACCEPTED_ISSUED_TOKEN=true` and `WS_CONNECTED=true`;
- `WS_LOGIN_USED_ISSUED_TOKEN=true`, `TOKEN_AGE_SECONDS_AT_WS_LOGIN=0`, token canonical/expiry/type presence all true;
- `STAGE=WS_LOGIN`, `RETURN_CODE=805004`, embedded `DETAIL_CODE=8050`, `ERROR_CLASS=TOKEN_OR_LOGIN_AUTH`;
- `WS_LOGIN_OK=false`, no type00 REG/ACK and no broker execution provenance;
- the local public IP matched the allowed IP in the owner's official REAL API registration screen, which showed a current registration. Neither the actual IP nor credentials are recorded here.
- Owner submitted the updated 8050 WebSocket authentication evidence to Kiwoom support and will supply their reply.

Separately, the isolated Railway REAL-read-only service successfully built/deployed a one-shot smoke image (`6afe4255-cb67-4f4f-93a8-bb03021935d2`), but its **application** returned `STAGE=TOKEN`, `RETURN_CODE=3`, `DETAIL_CODE=8050`, `TOKEN_OK=false`. Railway deployment `SUCCESS` is NOT token/authentication success. Source IP/credential consistency there is not independently established; values are redacted.

The earlier Railway pair of `return_code=2 / detail_code=8030` DEMO-mode results remains HISTORICAL and may not be asserted as the current state after owner variable updates. Do not demand credential re-issuance, repeating the local smoke or Railway upgrades merely from those superseded results. Do not assert IP as the proven cause of the current 8050; support response pending.

Remaining AUTH blocker: independently establish REAL WebSocket LOGIN/type00 registration before progressing. Structural GitHub CI/deployment checks do not make accepted LIVE broker/strategy evidence. `ORDERING=DISABLED`; `REAL_ORDERS_AUTHORIZED=false`; `FUNDS_MOVEMENT_AUTHORIZED=false`; `PERMISSION_CHANGE_AUTHORIZED=false`. The user's registered-IP smoke and all broker credentials are private; no keys/tokens/accounts/public IP values go to GitHub.


This section supersedes the older generic independent-work order below. Use `INDEXALERT_TINY_LIVE_PRIORITY_2026-10-08.md`.

A blockers first: REAL Kiwoom auth/read-only transport; source/PIT/prospective admission; required promotion/Shadow/Fresh Confirmation evidence; genuine execution/settlement evidence; durable order/reconciliation/Kill/capital safety; exact KRW 100,000 maximum Tiny Live ceiling and any eligible frozen risk limits; explicit final activation approval.

B work: exact release pin/rollback, operator diagnostics, failure alerts and recovery drills that reduce Tiny Live launch risk.

C work: non-blocking UI/cosmetics, open-ended hardening without a reproduced launch blocker and exploratory research not required for the current launch path.

Current first external blocker is no longer DEVICE_AUTH. Railway probes show DEMO-mode credentials in the isolated REAL read-only services; REAL OAuth returns 8030 MODE_MISMATCH. Do not request another 8050/device-auth rerun until broker-issued REAL credentials are installed in the isolated REAL read-only service.

---

# Delivery priority override — 2026-10-07 user-directed efficiency

User instruction: “효율적이게 일해 중요한것부터”. This supersedes older next-task pointers that start another open-ended integrity/schema review.

Follow INDEXALERT_DELIVERY_PRIORITIES.md before choosing the next task: original data/source/PIT/economics and valid Alpha evidence, registered future observations, genuine read-only broker/settlement connection, then required module integration and delivery. An external/time-bound path does not prevent an actionable independent required task.

PR309–312 and their successful CI are complete. Additional hypothetical schema-corruption cases are lower priority unless a concrete critical failure blocks the required usage path. Do not create another PR or research sweep merely to keep work active. Stop exploratory coding when only unavailable external evidence/time/owner actions remain, and record the exact blocker.

This changes work order only. No Frozen/model/cost/holdout/promotion/real-order criterion is relaxed. Whole-account REAL read-only baseline stays COMPLETE; type00 DEVICE_AUTH and original signer owner checks remain deferred without repeated requests. Research future-alpha protocol remains a diagnostic, not ACCEPTED successor/formal Shadow/LIVE evidence. All actual ordering/funds/account-permission authority remains false.

---

# Independent-work queue while owner-operated checks are deferred

Status: development planning only. This document grants no research admission, Shadow admission, Early-Live authority, broker permission, order authority, or funds authority.

The owner has explicitly deferred local/owner-operated checks until they later say they are available. Do not repeatedly request PowerShell or device/account actions in the meantime.

## Owner-operated validation status
- `KIWOOM_REAL_ACCOUNT_SCOPE_READONLY_v1`: completed 2026-10-07. The redacted REAL whole-account read-only baseline is recorded in `INDEXALERT_KIWOOM_REAL_ACCOUNT_SCOPE_EVIDENCE_2026-10-07.md`.
- `KIWOOM_REAL_TYPE00_READONLY_v1` is currently pending/deferred. It verifies REAL WebSocket LOGIN + read-only type00 registration only and does not block independent development. No real order is required for LOGIN/REG connectivity.

## Independent work order
Continue work that does not require owner-local credentials or interaction, in this order when actionable evidence/code gaps exist:
1. durable journal/reconciliation fail-closed integrity;
2. Shadow operational diagnostics and restart/Kill/reconnect fault handling;
3. capital ceiling/reservation integrity and conservative cash reuse;
4. read-only broker schema/transport boundary review;
5. canonical Early-Live admission composition and reporting;
6. source/PIT/status-economics work that can be completed from independently available original sources;
7. successor Alpha research only under the frozen research contract and preregistration rules.

Do not manufacture PASS from local flags, synthetic fixtures, hashes, green CI, or self-authored contracts. External evidence stays OPEN until independently observed.

## Frozen blockers that local engineering cannot close by itself
- admitted successor Alpha;
- source/PIT/status-economics PASS;
- exact-policy live-market Shadow completion;
- genuine broker-native execution provenance;
- genuine account/date/scope/settlement reconciliation where external observations are required;
- final Early-Live numeric limits when the governing admission revision is actually eligible to freeze them;
- explicit owner authorization immediately before any real-account ordering.

The consumed invalid v1 sealed holdout remains immutable and must not be rerun, repaired, retuned or used for discovery.

## Authority
Real orders, funds movement and broker/account permission changes remain false and require separate explicit owner authorization. Deferred owner checks are not permission to perform those actions.
