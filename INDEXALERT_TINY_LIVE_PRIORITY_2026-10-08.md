# IndexAlert Tiny Live delivery priority — 2026-10-08

Status: DELIVERY-ORDER OVERRIDE ONLY — NO TRADING AUTHORITY.


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

## Goal
Reach the earliest safe state for explicitly authorized **Tiny Live with total operating capital capped at KRW 100,000**, while preserving every existing Frozen/PIT/Holdout/Net-EV/execution/risk/promotion requirement. This document changes work order only. It does not make any gate easier to pass and does not authorize a real order.

## Authoritative refs
- development: `index-alert-position-regen-fix-v1`
- research: `index-alert-research-v1`
- Android: `index-alert-build`
- actual Early-Live preregistration ref: `index-alert-early-live-v2-prereg`
- `index-alert-early-live` does not currently exist and must not be assumed.

GitHub actual state overrides chat/history. Re-fetch HEAD/open PR/Actions before every continuation.

## A — Tiny Live mandatory blockers
Work these first whenever actionable.

1. **REAL Kiwoom authentication/read-only broker transport**
   - Current Railway REAL read-only services contain credentials that succeed against DEMO but fail REAL OAuth with return_code=2 / detail_code=8030 MODE_MISMATCH.
   - Required external action: owner replaces only `KIWOOM_APP_KEY` and `KIWOOM_APP_SECRET` in the isolated REAL read-only Railway service with broker-issued REAL OpenAPI credentials. Never place credentials in GitHub/chat.
   - After replacement, rerun only the existing one-shot REAL read-only token/account/WebSocket LOGIN/type00 REG smoke. No order is required.

2. **Official source/PIT/prospective evidence admission**
   - Frozen H5 prospective runtime and chronology anchoring infrastructure are implemented.
   - Structural capture/hash/green CI alone are not Fresh Alpha, Shadow, source/model/chronology admission or promotion evidence.
   - Continue genuine forward observation and independent admission under the existing frozen contracts; never backfill decisions.

3. **Strategy/promotion evidence**
   - Consumed invalid v1 holdout remains immutable and cannot be repaired/rerun/reused.
   - Any required independent OOS/prospective/Shadow/Fresh Confirmation evidence remains mandatory; no Tiny Live shortcut.

4. **REAL execution/settlement evidence**
   - Broker-native provenance, partial-fill/failure/retry/reconciliation, fees/taxes/cashflow/settlement and frozen execution-sufficiency requirements remain mandatory where the governing contracts require them.
   - Synthetic/Paper/self-labelled LIVE rows do not close this blocker.

5. **Order safety and risk**
   - Durable duplicate-order prevention, restart/reconnect reconciliation, uncertain-outcome handling, partial/late fills, fail-closed Kill, conservative capital reservation and existing pretrade checks remain mandatory.
   - Tiny Live capital ceiling is **KRW 100,000 maximum**. This is an upper bound, not an activation permission.
   - Any lower loss/drawdown/order-size limits required by the eligible Early-Live contract must be frozen before activation; do not invent them after observing LIVE outcomes.

6. **Explicit activation**
   - Real buy/sell order activation, funds movement, broker/account permission changes and any risk-limit expansion require separate explicit owner approval immediately before the action.
   - Until then: `ORDERING=DISABLED`, `REAL_ORDERS_AUTHORIZED=false`, `FUNDS_MOVEMENT_AUTHORIZED=false`, `PERMISSION_CHANGE_AUTHORIZED=false`.

## B — Tiny Live stabilisation
Do after or in parallel with A only when it directly reduces launch risk:
- operational release pin/rollback and immutable approved model/config bundle;
- operator-facing diagnostics, PnL/position/order/fill journal visibility without secret leakage;
- alerting for Kill/reconciliation/source freshness/runtime failure;
- recovery drills and deployment health for the exact Tiny Live release.

## C — post-Tiny-Live backlog
Preserve, do not delete:
- non-blocking Android/UI enhancements;
- convenience dashboards/cosmetics;
- open-ended schema/refactor hardening without a reproduced launch blocker;
- exploratory successor research that does not affect the current Tiny Live gate;
- performance/ergonomic improvements that can safely wait behind the launch path.

## Work selection rule
Before starting any task ask:
1. Does this directly shorten the safe Tiny Live critical path?
2. Is the blocker actionable now?
3. Is another chat/branch already solving it?
4. Does it preserve all frozen evidence and safety boundaries?
5. Is there a shorter evidence-grounded solution?

Do not create PRs merely to keep work active.

## Current highest-priority external blocker
As of development HEAD `03abee3e4bf1a4237d7a8a73d05dbb36d1e4c831`, PR #351 is merged and its Kiwoom REAL read-only CI passed. The isolated Railway smoke still stops at OAuth TOKEN with return_code=2 / detail_code=8030 / MODE_MISMATCH because the stored credential pair is DEMO-mode. This is the first owner action on the Tiny Live path.

No real trading may start from this document.
