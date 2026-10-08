# Prospective read-only runtime — 2026-10-08

Status: STRUCTURAL CURRENT-SESSION CAPTURE ONLY — NO SOURCE/MODEL/CHRONOLOGY ADMISSION, NO FRESH ALPHA, NO LIVE ORDER AUTHORITY.

The frozen H5 block16 model is now an immutable runtime bundle and the exact supervised-session calendar prefix from adopted Action 36643183157 is pinned with SHA-256 `852f25e6f43e3c1df6dd201604eab5fea9ec1bd7b7468b9dea30eac3fe334ee3`.

`research_v1_prospective_runtime.py` closes the next execution gap without touching the broker:

- refuses to run before 18:30 KST;
- requires the exact read-only KRX network authority marker and `KRX_AUTH_KEY`;
- fails closed if any real-order, funds-movement or permission-change flag is true or `ORDERING` is not `DISABLED`;
- verifies the immutable 2015-origin long-history source on the Railway PIT volume;
- loads only recent verified prior-session rows as feature warmup;
- fetches official KRX OpenAPI KOSPI daily-trade/security-master data for the small post-freeze gap through the current session;
- extends the pinned supervised-session calendar only with non-empty official market sessions;
- binds the prebuilt block16 model without refitting historical outcomes;
- transactionally stores source, input, producer, model, decision and final session-manifest artifacts under a private PIT-volume directory;
- emits a separate hash-only anchor payload for later independent chronology anchoring.

A market holiday produces `NO_MARKET_SESSION` and no decision. A same-session completed manifest is idempotently reported as already committed. A partial/conflicting same-session state remains fail-closed.

The runtime does not import or call Kiwoom/broker order code. It cannot authorize or place an order. Every committed session keeps independent source/model/chronology admission, Fresh Alpha admission, Shadow S1, Fresh Confirmation S2, promotion and live-order authority false.

The next boundary after this PR is autonomous external chronology anchoring of the hash-only payload; only after that can a fresh observation be considered for independent evidence admission.


## Continuous read-only wrapper

The production image now starts `research_v1_prospective_http_runtime.py`.
It performs startup-only validation of the read-only authority flags, pinned
model, pinned session calendar and immutable PIT source, then remains online
without contacting KRX until the 18:30 KST finality guard has passed.

The wrapper exposes only `GET /health`, `GET /status`, and
`GET /anchor/latest`. Every POST is rejected with 405. The anchor endpoint
contains only the immutable per-session hash payload already written by
`run_once()`; it contains no securities, scores, account data or credentials.

After finality the wrapper retries the existing `run_once()` producer at most
once per 15 minutes. The decision/model/source implementation remains the
same-session-universe-safe implementation from PR #343. No endpoint can grant
source/model/chronology admission, Fresh Alpha, Shadow, promotion, funds,
permissions or live-order authority.

## 2026-10-08 production source-fail telemetry (diagnostic-only)

A live check of the isolated Railway `indexalert-pit-rebuild` read-only prospective HTTP service found repeated `FAIL_CLOSED` attempts on 2026-10-08 after the 18:30 KST finality guard. The exception class was `KRXProspectiveOpenAPISourceError`. No session manifest or chronology anchor was committed; source/model/chronology admission and all trading permissions stayed false. The old public status exposed only the exception class, which was insufficient to distinguish missing KRX fields from incomplete same-session security-master joins or invalid halted-stock OHLC.

The diagnostic change adds `error_reason_code` as a static, allowlisted enum for failure reporting. It never exposes raw KRX bodies, issue names/codes, provider text, secrets, exception strings, or credential-bearing URLs. Unknown source failures map to `KRX_SOURCE_OTHER`; unrelated failures to `OTHER_FAILURE`. The status reader rejects any unrecognized reason code. This does not alter the frozen source/selection policy, skip rejected rows, re-fetch historical data, promote sessions, perform brokerage operations, or relax fail-closed behavior. An actual deployment on the dedicated prospective runtime branch and a new observed failure are required to identify the live cause; synthetic tests alone do not identify it.


## 2026-10-08 21:21+09:00 confirmed older gap-session failure

Actual isolated Railway read-only prospective runtime deployment `1e28a68d-b8ef-432c-a6a6-e754657924fb` reached SUCCESS. One observed runtime attempt emitted `source_failure_session=2026-09-28`, `error_reason_code=COMMON_OHLC_NONPOSITIVE`, `status=FAIL_CLOSED`, `session=2026-10-08`, and a null session-manifest hash. Thus the current target session is blocked by an invalid earlier gap response, not proven to be malformed current-day prices. Trading stays disabled.

The new diagnostics attach only aggregate counts from KOSPI common-stock rows failing strict OHLC >0 validation: total common rows, rejected OHLC rows, rejected rows with both volume and traded value exactly zero, the remaining rejected rows, and rejected rows with all OHLC prices exactly zero. Counts are validated (including conservation/bounds), and no issue identifiers, raw response, actual quotes, keys or provider messages are written to public status. A zero-activity count does **not** prove an official trading halt or justify removing the security. Source/strategy/PIT/holdout/economics/admission and all order/funds/permission gates are unchanged; a new real runtime response must be observed before any cause is inferred.

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
