# Tiny Live A/B/C override — 2026-10-08

## Observed KRX nontrading OHLC blocker — 2026-10-08 21:34 KST

Authoritative read-only Railway prospective runtime: service `indexalert-pit-rebuild`, deployment `40df3f6f-5136-485a-adc2-a509438de845`, exact deployment source commit `48548738323bfa7aa938eda7a96b5035813099be`, settled `SUCCESS` (image/health only). A real runtime attempt for target `2026-10-08` reached `FAIL_CLOSED` on earlier source session `2026-09-28` with `COMMON_OHLC_NONPOSITIVE`; no session manifest was committed.

The first real aggregate diagnostic, computed after the approved KRX daily-trade response is joined to same-date security-master common-stock identity, was:
- `common_stock_rows=803`
- `nonpositive_ohlc_rows=27`
- `zero_volume_value_rows=27` (both volume and traded value exactly 0)
- `other_activity_rows=0`
- `all_zero_ohlc_rows=0`

These are **real API-derived counts**, not a synthetic test, but `27/27` zero activity is **not** independent proof that all 27 are officially halted. Some prices were nonpositive while not every OHLC value was zero; the exact missing field combination and matching official security status remain unverified. The complete row identities are not in the public logs or GitHub. Do not infer fills, returns, recovery, untradeability classifications, or status source coverage from the counts.

Required next source evidence before allowing this gap to feed an Alpha input: privately identify the exact 27 rejected securities from the original official daily/master source and compare with legally accessible official same-session halt/tradability/status coverage with PIT availability. If not available, retain `FAIL_CLOSED` and continue only unrelated verified work. Do **not** drop rows, forward-fill price, treat zero volume as a halt attestation, replay future-hindsight data as PIT, use unapproved authenticated Data Marketplace scraping or relax Frozen/OOS/holdout/NetEV gates. No broker order/funds/account permission change.

Separate Kiwoom status still requires official support on REAL WS LOGIN `8050`; passing REST token/account read is not WS type00 PASS. 10만원 Tiny Live remains **not ready**, all order/funds/permission authority false.



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

**Superseded historical note (pre-REAL credential update only):** Older Railway probes returned `8030 MODE_MISMATCH` with then-DEMO-mode credentials. Do not treat this as a current owner action. The later registered-IP Windows read-only REAL token/account probe passed while WebSocket LOGIN returned `805004/8050`; the updated isolated Railway smoke returned TOKEN-stage `8050` rather than `8030`. Kiwoom technical-support reply is pending; REAL key reissuance/upgrade or repeating superseded DEMO probes is not currently requested. Separately, KRX 2026-09-28 27 no-trade OHLC anomaly remains fail-closed pending independent official status evidence.

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


## 2026-10-08 22:41 KST targeted official halt-source route decision (NOT evidence admission)

Current frozen real-data observation: read-only Railway KRX session `2026-09-28`, 803 KOSPI official common-stock rows, **27** with nonpositive OHLC, **27/27** with both official volume and traded value equal to zero, and no fully all-zero OHLC row. The source and current 2026-10-08 prospective target remain `FAIL_CLOSED`; no row is removed, priced or promoted.

**Avoid unnecessary new unapproved routes.** The public official KRX OPEN API service-list page (https://openapi.krx.co.kr/contents/OPP/INFO/service/OPPINFO004.cmd, inspected 2026-10-08) lists KOSPI daily trading and basic-security information but no separate trading-halt/history API service. It is **not** a suitable basis for inventing a new halt endpoint or treating basic-master fields as historical halt proof. The official KRX Data Marketplace **website** presents an issue-statistics trading-halt section (https://data.krx.co.kr/contents/MMC/MAIN/main/index.cmd), which is a distinct product/route from OPEN API.

The research branch already has a *specific authenticated tiny-probe observation* for Data Marketplace trading-halt history `MDCSTAT21301` (MDCSTAT213, individual issue), pinned in `INDEXALERT_KRX_DATA_MARKETPLACE_ROUTE_MAP.md`, read-only probe `research_v1_krx_status_source_probe.py`, and normalized halt intervals in `research_v1_krx_official_status.py`. For each **validated issue episode** request `isuCd=standard_code`, `isuCd2=short_code` and intervals no greater than 730 calendar days; see `INDEXALERT_KRX_HISTORICAL_ACQUISITION_PLAN.md` v3. KRX email v3 (recorded `INDEXALERT_KRX_PERMISSION_REPLY_EVIDENCE.md`) establishes automated personal/non-commercial research **rights**, not data provenance, complete 27-issue identity/coverage, valid publication timestamps or permission for unrelated commercial/redistribution uses.

**Exact high-value next operation (NOT YET EXECUTED OR APPROVED AS A RUN):**
1. First resolve exact **27 stable issue identities** from the original official September 28 daily/master records **inside private research storage**, not from aggregate public logs; a receipt must bind original raw-data hashes and observed availability.
2. Using the already validated `MDCSTAT21301` route, prepare a separately frozen **read-only, date-scoped, 27-episode maximum** status reconciliation request batch for `2026-09-28`, preserving all authorization/preflight/credential controls and explicit run-level consent required by the existing runner. Do not extrapolate a tiny-probe token or historical bulk authorization into this new execution; do not start a request merely from this document.
3. Independently audit the actual observed halt intervals, status effective dates and source retrieval/PIT publication lineage for the exact identifiers; unknown, no official event, or incomplete returned coverage remains `UNKNOWN`, never `TRADABLE` or a fabricated `HALTED`. `27/27` zero volume **is not** proof all 27 are halted; no status is presumed from missing rows.
4. Do not alter the frozen common-stock universe, source-price normalization, OHLC positivity guard, 0..3 NO_TRADE ranking, order capability, sealed holdout, or 10만원 live readiness. A verified status match would be only diagnostic/one source-gate input; price/fill/economic treatment requires its own independently approved rule and fresh evidence.

Because the existing approved status route is already technically probed, the next owner-independent action is privacy-safe local preflight/schema/lineage verification, **not** installing a third-party source or making unsupported automated screen-scrapes. Data Marketplace and KRX OPEN API licences/permissions remain separate; raw issue/price/account materials must not be pushed to this repository or response. The Kiwoom REAL WebSocket `805004/8050` support blocker is entirely separate.
