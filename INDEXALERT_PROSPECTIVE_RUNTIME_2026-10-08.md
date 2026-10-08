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
