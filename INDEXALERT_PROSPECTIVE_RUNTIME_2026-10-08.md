# Private rejected-source capture implementation

The read-only runtime now retains the already-retrieved daily/master bytes when same-session source normalization rejects them. It writes content-addressed raw objects plus an immutable diagnostic receipt outside Git/public directories. The receipt binds the requested source day, exact raw hashes and actual timezone-aware retrieval timestamps; it explicitly does not attest original historical publication, source admission, decisions, Fresh Alpha or orders. A later retry produces a separately dated observation and never reconstructs an earlier failed response. Exact retries are idempotent. Failed persistence creates no usable session/anchor; the source exception still blocks the session. No added KRX request, Data Marketplace collector, strategy/universe/OHLC modification or public raw identifiers.

Offline verification: new raw-byte/receipt/failure/no-extra-fetch/idempotency/retry-timestamp/private-boundary/partial-write tests and existing HTTP privacy tests pass locally. The container lacks pyarrow locally, so the existing parquet warmup test requires repository CI; no local full-suite claim. Actual production use remains separately unverified until the updated read-only image is deployed and a real rejected response is captured. This does not make the 27 issues officially halted or unblock prospective/Alpha/Tiny Live admission.


## Continuation correction — current KRX route authority

This section supersedes the earlier 22:41 KST permission claim. Exact current-head local permission preflight reproduced route-specific Gate F `BLOCKED`; historical v3 remains intact. No new Data Marketplace request or execution approval is implied. Do not request the same missing owner email again.

At continuation, development HEAD `d5d4e27b3fdfb385c4686373b94904aedb0dcf42` includes merged PR363; its merge-push prospective-runtime Action37787094436 is SUCCESS. Railway's existing deployment `40df3f6f-5136-485a-adc2-a509438de845` emitted the same 27/803 OHLC failure at2026-10-08T13:49:27Z, with no session manifest and all admission/order/funds/permission flags false. Deployment health/CI do not resolve the source blocker.

Private-original access is also a distinct dependency: inspection of `run_once()` confirms gap sources are built in memory before the session transaction, and a gap normalization exception exits before its durable session-source persistence. Public aggregate diagnostics therefore cannot reconstruct the original 27 issue identities or bind the original failed response's hashes/timestamps. This is a code-path finding, not an assertion that no copy exists anywhere in private storage. Do not invent those hashes, claim a private-volume read, or silently re-fetch a response as the original. The next concrete engineering task is private diagnostic persistence of already-retrieved rejected OpenAPI raw objects and their real retrieval timestamps, preserving `FAIL_CLOSED`, excluding decision/Alpha admission, and exposing only aggregate/hash diagnostics. Any implementation/redeployment must preserve existing read-only source authority and private-storage contracts.

Frozen universe/OHLC positivity/ranking/PIT/holdout and 100,000-KRW live gates remain unchanged. Kiwoom805004/8050 support response remains pending; no repeated broker smoke or account/security change.

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

The research branch already has a *specific authenticated tiny-probe observation* for Data Marketplace trading-halt history `MDCSTAT21301` (MDCSTAT213, individual issue), pinned in `INDEXALERT_KRX_DATA_MARKETPLACE_ROUTE_MAP.md`, read-only probe `research_v1_krx_status_source_probe.py`, and normalized halt intervals in `research_v1_krx_official_status.py`. For each **validated issue episode** request `isuCd=standard_code`, `isuCd2=short_code` and intervals no greater than 730 calendar days; see `INDEXALERT_KRX_HISTORICAL_ACQUISITION_PLAN.md` v3. Technical reachability does **not** establish current acquisition rights. The unrestricted web-automation claim in historical KRX email v3 is **superseded** by the owner's original email and their confirmation that no matching unrestricted reply exists. `INDEXALERT_KRX_PERMISSION_REPLY_EVIDENCE.md` and `INDEXALERT_KRX_ORIGINAL_MESSAGE_CONFLICT_2026-10-07.md` are authoritative for this correction. The current permission validator returns `SUPERSEDED_UNSUPPORTED_AUTOMATION_CLAIM`, `automated_collection_authorized=false`, `bulk_historical_acquisition_rights_authorized=false` and route-specific Gate F `BLOCKED`. Internal research storage/analysis and separately approved OpenAPI services remain distinct; neither authorizes the `MDCSTAT21301` web-session collector.

**Exact high-value next operation (NOT YET EXECUTED OR APPROVED AS A RUN):**
1. First resolve exact **27 stable issue identities** from the original official September 28 daily/master records **inside private research storage**, not from aggregate public logs; a receipt must bind original raw-data hashes and observed availability.
2. Using the technically probed but currently permission-blocked `MDCSTAT21301` route, prepare only a **network-free draft** of a read-only, date-scoped, 27-episode maximum status reconciliation request batch for `2026-09-28` if independently verified private identities are available. Any future network execution requires independently established applicable route rights **and** the existing preflight/run-level authority; owner run consent alone cannot restore the superseded KRX permission evidence. Do not extrapolate a tiny-probe token or historical bulk authorization into this new execution; do not start a request merely from this document.
3. Independently audit the actual observed halt intervals, status effective dates and source retrieval/PIT publication lineage for the exact identifiers; unknown, no official event, or incomplete returned coverage remains `UNKNOWN`, never `TRADABLE` or a fabricated `HALTED`. `27/27` zero volume **is not** proof all 27 are halted; no status is presumed from missing rows.
4. Do not alter the frozen common-stock universe, source-price normalization, OHLC positivity guard, 0..3 NO_TRADE ranking, order capability, sealed holdout, or 10만원 live readiness. A verified status match would be only diagnostic/one source-gate input; price/fill/economic treatment requires its own independently approved rule and fresh evidence.

Because the existing status route is technically probed but currently permission-blocked, the next owner-independent action is privacy-safe local preflight/schema/lineage verification, **not** installing a third-party source or making unsupported automated screen-scrapes. Data Marketplace and KRX OPEN API licences/permissions remain separate; raw issue/price/account materials must not be pushed to this repository or response. The Kiwoom REAL WebSocket `805004/8050` support blocker is entirely separate.

## 2026-10-10: Audit privately retained rejected KRX source WITHOUT admission

The read-only Railway deployed `c8914baf48ee5d835b7d5c15c67fef8fc1075f35` successfully. On 2026-10-09 target, runtime safely reported `private_rejected_source_receipt_saved=true` for source session 2026-09-28, with 27 of 803 common stocks rejected for OHLC nonpositive and zero volume/value. 22 dated runtime attempts show the same failure; no prospective/Alpha admission. This **proves the private receipt writer returned** on those attempts, not that historical source was available back on Sep 28, and not official halt classification.

The new offline-only audit reads the most recently retrieved private immutable rejected receipt after restart, checks filename SHA, schema, immutable date/route/no-admission metadata and permission mode; verifies content-addressed daily and master raw hashes; replays the existing strict source normalizer **without any network** and emits only allowlisted count aggregates. It never publishes raw KRX bytes, issue IDs, names, OHLC values, receipt hashes, token or original provider exceptions. It never skips/corrects a rejected stock, revises PIT availability, invokes the forbidden Data Marketplace collection path, or changes Frozen model, costs, holdout or order permissions. A failed audit prints a fixed `OFFLINE_AUDIT_FAIL_CLOSED` status, not exception detail; normal prospective fail-closed remains independent. Any confirmed raw-source audit is **not** official halt evidence, source admission, tradability/fill evidence, or a profitability pass. The existing KRX permission block on individual-security halt history remains in force.

## 2026-10-10 observed offline raw verification and identity-shape extension

Railway read-only deployment `948d5ea3-1e44-40a5-9ec5-31b80c3be82f` (`131f1154aaf533547b6d0096173fafb3cddaa30a`) reached `SUCCESS` and logged the **real** startup `REJECTED_SOURCE_RAW_VERIFIED` for the latest of 22 private receipts; latest daily/master raw hashes verified, same source session 2026-09-28 and 27/803 rejected common-stock records reproduced. The 2026-10-10 scheduled attempt remained `FAIL_CLOSED` without Alpha or orders.

Next diagnostic-only extension joins already stored raw daily issue short codes to the already retrieved master standard codes wholly **in private memory**, and reports only counts of structurally unique joined rejected identities plus zero open/high/low/close, negative price and positive close aggregate pattern. It neither publishes issue codes/name/price nor asserts official halt/tradability. A source/identity/count discrepancy fails the offline audit as `OFFLINE_AUDIT_FAIL_CLOSED`; the runtime's original source rejection and all authority flags remain unchanged. No new KRX call, Data Marketplace route, model tuning, trade signal, holdout consumption or broker operation. A later real Railway startup record is required before reporting actual counts.
